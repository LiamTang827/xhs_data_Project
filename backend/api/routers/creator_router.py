"""
Creator Network API Router
创作者网络数据接口
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio

from database import (
    UserProfileRepository,
    CreatorNetworkRepository
)
from tasks.collector_task import (
    CollectorTask,
    create_collector_task,
    get_task_status
)

router = APIRouter(prefix="/api/creators", tags=["creators"])


# ============================================
# 请求/响应模型
# ============================================

class AddCreatorRequest(BaseModel):
    """添加创作者请求"""
    user_id: str
    auto_update: bool = True  # 是否加入自动更新


class AddCreatorResponse(BaseModel):
    """添加创作者响应"""
    success: bool
    task_id: str
    message: str


class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    task_id: str
    status: str  # pending, initializing, fetching, analyzing, completed, failed
    progress: Dict[str, Any]
    created_at: Optional[str] = None
    finished_at: Optional[str] = None
    error: Optional[str] = None


@router.get("/network")
async def get_creator_network(platform: str = "xiaohongshu") -> Dict[str, Any]:
    """
    获取创作者网络数据
    
    Args:
        platform: 平台类型
        
    Returns:
        网络数据 {creators: [...], creatorEdges: [...], trackClusters: {}, trendingKeywordGroups: []}
    """
    try:
        network_repo = CreatorNetworkRepository()
        network = network_repo.get_latest_network(platform)
        
        if not network:
            # 如果数据库中没有，返回空网络
            return {
                "creators": [],
                "creatorEdges": [],
                "trackClusters": {},
                "trendingKeywordGroups": []
            }
        
        # 获取network_data，确保字段名称匹配前端期望
        network_data = network.get("network_data", {})
        
        return {
            "creators": network_data.get("creators", []),
            "creatorEdges": network_data.get("creatorEdges", network_data.get("edges", [])),
            "trackClusters": network_data.get("trackClusters", {}),
            "trendingKeywordGroups": network_data.get("trendingKeywordGroups", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取网络数据失败: {str(e)}")


@router.get("/list")
async def list_all_creators(platform: Optional[str] = None):
    """
    获取所有创作者列表
    
    Args:
        platform: 平台类型，不指定则返回所有平台
        
    Returns:
        创作者列表
    """
    try:
        profile_repo = UserProfileRepository()
        profiles = profile_repo.get_all_profiles(platform)
        
        creators = []
        for profile in profiles:
            creators.append({
                "user_id": profile.get("user_id", ""),
                "nickname": profile.get("nickname", ""),
                "platform": profile.get("platform", ""),
                "topics": profile.get("profile_data", {}).get("topics", []),
                "content_style": profile.get("profile_data", {}).get("content_style", "")
            })
        
        return {"creators": creators, "total": len(creators)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取创作者列表失败: {str(e)}")


@router.get("/{creator_name}")
async def get_creator_detail(creator_name: str, platform: str = "xiaohongshu"):
    """
    获取创作者详细信息
    
    Args:
        creator_name: 创作者昵称
        platform: 平台类型
        
    Returns:
        创作者详细信息
    """
    try:
        profile_repo = UserProfileRepository()
        profile = profile_repo.get_profile_by_nickname(creator_name, platform)
        
        if not profile:
            raise HTTPException(status_code=404, detail=f"未找到创作者: {creator_name}")
        
        return {
            "user_id": profile.get("user_id", ""),
            "nickname": profile.get("nickname", ""),
            "platform": profile.get("platform", ""),
            "profile_data": profile.get("profile_data", {}),
            "created_at": profile.get("created_at"),
            "updated_at": profile.get("updated_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取创作者详情失败: {str(e)}")


# ============================================
# 添加创作者功能
# ============================================

@router.post("/add", response_model=AddCreatorResponse)
async def add_creator(request: AddCreatorRequest, background_tasks: BackgroundTasks):
    """
    添加新创作者
    
    流程：
    1. 创建任务记录
    2. 在后台执行：爬取数据 → 分析画像 → 保存数据库
    3. 返回task_id供前端轮询进度
    
    Args:
        request: 包含user_id和auto_update
        background_tasks: FastAPI后台任务
        
    Returns:
        任务ID和初始状态
    """
    try:
        # 验证user_id格式（简单验证）
        if not request.user_id or len(request.user_id) < 10:
            raise HTTPException(status_code=400, detail="无效的用户ID格式")
        
        # 创建任务
        task_info = await create_collector_task(request.user_id)
        task_id = task_info["task_id"]
        
        # 在后台执行任务
        async def run_task():
            task = CollectorTask(request.user_id, task_id)
            result = await task.run()
            
            # 更新最终结果
            from database.connection import get_database
            db = get_database()
            db.task_logs.update_one(
                {"task_id": task_id},
                {"$set": {"result": result}}
            )
        
        # 添加到后台任务队列
        background_tasks.add_task(run_task)
        
        return AddCreatorResponse(
            success=True,
            task_id=task_id,
            message="任务已创建，正在后台执行"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@router.get("/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_progress(task_id: str):
    """
    获取任务进度
    
    前端轮询此接口获取实时进度
    
    Args:
        task_id: 任务ID
        
    Returns:
        任务状态和进度信息
    """
    try:
        task = await get_task_status(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return TaskStatusResponse(
            task_id=task["task_id"],
            status=task["status"],
            progress=task.get("progress", {}),
            created_at=task.get("created_at"),
            finished_at=task.get("finished_at"),
            error=task.get("result", {}).get("error") if task.get("status") == "failed" else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")


@router.post("/{user_id}/refresh")
async def refresh_creator_data(user_id: str, background_tasks: BackgroundTasks):
    """
    手动刷新创作者数据
    
    重新爬取并分析创作者的最新数据
    
    Args:
        user_id: 创作者用户ID
        background_tasks: FastAPI后台任务
        
    Returns:
        任务信息
    """
    try:
        # 检查创作者是否存在
        profile_repo = UserProfileRepository()
        existing = profile_repo.get_profile_by_user_id(user_id, "xiaohongshu")
        
        if not existing:
            raise HTTPException(status_code=404, detail="创作者不存在")
        
        # 创建刷新任务（与添加类似）
        task_info = await create_collector_task(user_id)
        task_id = task_info["task_id"]
        
        # 更新任务类型
        from database.connection import get_database
        db = get_database()
        db.task_logs.update_one(
            {"task_id": task_id},
            {"$set": {"task_type": "refresh_creator"}}
        )
        
        # 在后台执行
        async def run_task():
            task = CollectorTask(user_id, task_id)
            result = await task.run()
            db.task_logs.update_one(
                {"task_id": task_id},
                {"$set": {"result": result}}
            )
        
        background_tasks.add_task(run_task)
        
        return {
            "success": True,
            "task_id": task_id,
            "message": f"正在刷新创作者数据: {existing.get('nickname', user_id)}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刷新失败: {str(e)}")
