"""
Creator Network API Router
创作者网络数据接口
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime, timedelta

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

# 内存缓存：缓存网络数据，避免频繁查询MongoDB
_network_cache: Dict[str, Any] = {
    'data': None,
    'timestamp': None,
    'ttl_seconds': 300  # 缓存5分钟
}


def get_cached_network(platform: str) -> Optional[Dict[str, Any]]:
    """获取缓存的网络数据"""
    if _network_cache['data'] is None:
        return None
    
    if _network_cache['timestamp'] is None:
        return None
    
    # 检查是否过期
    age = (datetime.now() - _network_cache['timestamp']).total_seconds()
    if age > _network_cache['ttl_seconds']:
        print(f"[Cache] Expired (age: {age:.1f}s > ttl: {_network_cache['ttl_seconds']}s)")
        return None
    
    print(f"[Cache] Hit (age: {age:.1f}s)")
    return _network_cache['data']


def set_network_cache(data: Dict[str, Any]):
    """设置网络数据缓存"""
    _network_cache['data'] = data
    _network_cache['timestamp'] = datetime.now()
    print(f"[Cache] Set (ttl: {_network_cache['ttl_seconds']}s)")


def invalidate_network_cache():
    """清除网络数据缓存"""
    _network_cache['data'] = None
    _network_cache['timestamp'] = None
    print("[Cache] Invalidated")


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
    获取创作者网络数据（直接从MongoDB读取，使用缓存优化）
    
    Args:
        platform: 平台类型
        
    Returns:
        网络数据 {creators: [...], creatorEdges: [...], trackClusters: {}, trendingKeywordGroups: []}
    """
    from pymongo.errors import ServerSelectionTimeoutError, NetworkTimeout, AutoReconnect
    
    # 1. 尝试从缓存获取
    cached_data = get_cached_network(platform)
    if cached_data:
        print(f"[API] Cache hit, returning cached data")
        return cached_data
    
    # 2. 缓存未命中，从数据库查询
    print(f"[API] Cache miss, fetching from MongoDB...")
    import time
    start = time.time()
    
    try:
        network_repo = CreatorNetworkRepository()
        network = network_repo.get_latest_network(platform)
        
        elapsed = time.time() - start
        print(f"[API] MongoDB query took {elapsed:.2f}s")
        
        if not network:
            print(f"[API] No network data found for platform: {platform}")
            raise HTTPException(status_code=404, detail=f"未找到平台 {platform} 的网络数据")
        
        # 获取network_data，确保字段名称匹配前端期望
        network_data = network.get("network_data", {})
        
        result = {
            "creators": network_data.get("creators", []),
            "creatorEdges": network_data.get("creatorEdges", network_data.get("edges", [])),
            "trackClusters": network_data.get("trackClusters", {}),
            "trendingKeywordGroups": network_data.get("trendingKeywordGroups", [])
        }
        
        # 3. 保存到缓存
        set_network_cache(result)
        
        print(f"[API] Returning {len(result['creators'])} creators, {len(result['creatorEdges'])} edges")
        return result
        
    except (ServerSelectionTimeoutError, NetworkTimeout, AutoReconnect) as e:
        elapsed = time.time() - start
        print(f"[API] MongoDB timeout after {elapsed:.2f}s: {e}")
        raise HTTPException(
            status_code=503, 
            detail=f"数据库连接超时，请稍后重试 (耗时: {elapsed:.1f}s)"
        )
    except Exception as e:
        elapsed = time.time() - start
        print(f"[API] MongoDB error after {elapsed:.2f}s: {e}")
        raise HTTPException(status_code=500, detail=f"数据库查询失败: {str(e)}")


@router.post("/network/refresh")
async def refresh_creator_network(
    background_tasks: BackgroundTasks, 
    platform: str = "xiaohongshu",
    similarity_threshold: float = 0.5
):
    """
    重新生成创作者网络数据
    
    这个接口会在后台重新计算所有创作者的关系和统计数据
    
    Args:
        platform: 平台类型
        background_tasks: FastAPI后台任务
        similarity_threshold: 相似度阈值 (0-1)，只有相似度大于此值的创作者才会连边，默认0.5
        
    Returns:
        任务信息
    """
    try:
        # 验证阈值范围
        if not 0 <= similarity_threshold <= 1:
            raise HTTPException(status_code=400, detail=f"相似度阈值必须在0-1之间，当前值: {similarity_threshold}")
        
        import subprocess
        import os
        
        def regenerate_network():
            """后台重新生成网络"""
            try:
                backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                script_path = os.path.join(backend_dir, "scripts", "regenerate_creator_networks.py")
                
                print(f"🔄 开始重新生成创作者网络 (相似度阈值: {similarity_threshold})...")
                result = subprocess.run(
                    ["python3", script_path, "--similarity-threshold", str(similarity_threshold)],
                    cwd=backend_dir,
                    check=True,
                    capture_output=True,
                    text=True
                )
                print(f"✅ 网络数据已更新")
                print(result.stdout)
                
                # 清除缓存，下次请求会重新读取
                invalidate_network_cache()
                
            except subprocess.CalledProcessError as e:
                print(f"❌ 重新生成网络失败: {e}")
                print(e.stdout)
                print(e.stderr)
            except Exception as e:
                print(f"❌ 错误: {e}")
        
        # 添加到后台任务
        background_tasks.add_task(regenerate_network)
        
        return {
            "success": True,
            "message": f"网络数据正在后台重新生成（相似度阈值: {similarity_threshold}），请稍后刷新页面"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新生成网络失败: {str(e)}")


@router.get("/similarities/{user_id}")
async def get_creator_similarities(user_id: str, platform: str = "xiaohongshu"):
    """
    计算指定创作者与所有其他创作者的 embedding cosine similarity
    使用 user_embeddings 集合中的 512 维向量

    Returns:
        {similarities: {other_user_id: score (0~1), ...}}
    """
    try:
        import numpy as np
        from database.connection import get_database

        db = get_database()

        # 1. 取出自己的 embedding
        my_doc = db.user_embeddings.find_one(
            {"user_id": user_id, "platform": platform, "dimension": 512},
            {"embedding": 1}
        )
        if not my_doc:
            raise HTTPException(
                status_code=404,
                detail=f"用户 {user_id} 没有 embedding 向量，请先生成"
            )

        my_vec = np.array(my_doc["embedding"], dtype=np.float32)
        my_norm = np.linalg.norm(my_vec)
        if my_norm == 0:
            raise HTTPException(status_code=400, detail="用户 embedding 全为零")
        my_vec = my_vec / my_norm  # 归一化

        # 2. 取出所有其他创作者的 embedding
        cursor = db.user_embeddings.find(
            {"platform": platform, "dimension": 512, "user_id": {"$ne": user_id}},
            {"user_id": 1, "embedding": 1}
        )

        similarities: dict = {}
        for doc in cursor:
            other_id = doc["user_id"]
            vec = np.array(doc["embedding"], dtype=np.float32)
            norm = np.linalg.norm(vec)
            if norm == 0:
                continue
            score = float(np.dot(my_vec, vec / norm))
            # cosine similarity 范围 -1~1，映射到 0~1 方便前端显示
            similarities[other_id] = round(max(0.0, score), 4)

        return {"success": True, "user_id": user_id, "similarities": similarities}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算相似度失败: {str(e)}")


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


@router.get("/{user_id}/notes")
async def get_creator_notes(
    user_id: str,
    platform: str = "xiaohongshu",
    limit: int = 20,
    days: Optional[int] = None,
    sort: str = "engagement"
):
    """
    获取创作者的笔记列表（从 user_snapshots 直接读取，无需调用 AI）

    Args:
        user_id: 创作者用户 ID
        platform: 平台类型
        limit: 返回条数（默认 20）
        days: 时间范围（天），None 表示全部
        sort: 排序方式 engagement / latest

    Returns:
        {success, notes: [{id, title, desc, likes, collected_count, comments_count,
         share_count, engagement_score, create_time, images_list}], total}
    """
    try:
        from database.connection import get_database
        import time as _time

        db = get_database()

        # 从 user_snapshots 读取
        snapshot = db.user_snapshots.find_one(
            {"user_id": user_id, "platform": platform},
            {"notes": 1, "nickname": 1, "_id": 0}
        )
        if not snapshot or "notes" not in snapshot:
            raise HTTPException(status_code=404, detail=f"未找到用户 {user_id} 的笔记数据")

        raw_notes = snapshot["notes"]
        nickname = snapshot.get("nickname", "")

        # 可选：按时间过滤
        if days is not None:
            cutoff = _time.time() - days * 86400
            raw_notes = [n for n in raw_notes if (n.get("create_time") or 0) >= cutoff]

        # 计算互动分并构造返回结构
        results = []
        for n in raw_notes:
            likes = n.get("likes", 0) or 0
            collected = n.get("collected_count", 0) or 0
            comments = n.get("comments_count", 0) or 0
            shares = n.get("share_count", 0) or 0
            engagement = likes + collected * 2 + comments * 3 + shares * 4

            results.append({
                "id": n.get("id", ""),
                "title": n.get("display_title") or n.get("title") or "",
                "desc": n.get("desc", ""),
                "likes": likes,
                "collected_count": collected,
                "comments_count": comments,
                "share_count": shares,
                "engagement_score": engagement,
                "create_time": n.get("create_time"),
                "type": n.get("type", "normal"),
                "images_list": (n.get("images_list") or [])[:1],  # 只返回第一张图
            })

        # 排序
        if sort == "latest":
            results.sort(key=lambda x: x["create_time"] or 0, reverse=True)
        else:
            results.sort(key=lambda x: x["engagement_score"], reverse=True)

        total = len(results)
        results = results[:limit]

        return {
            "success": True,
            "user_id": user_id,
            "nickname": nickname,
            "notes": results,
            "total": total,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取笔记失败: {str(e)}")


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
        
        # 检查创作者是否已存在
        profile_repo = UserProfileRepository()
        existing = profile_repo.get_by_user_id(request.user_id, "xiaohongshu")
        
        if existing:
            nickname = existing.get('basic_info', {}).get('nickname') or existing.get('nickname', request.user_id)
            raise HTTPException(status_code=400, detail=f"创作者已存在: {nickname}")
        
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
            
            # 如果任务成功，重新生成网络数据
            if result.get("success"):
                try:
                    import subprocess
                    import os
                    
                    # 获取backend目录路径
                    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                    script_path = os.path.join(backend_dir, "scripts", "regenerate_creator_networks.py")
                    
                    # 执行脚本重新生成网络
                    print(f"🔄 重新生成创作者网络...")
                    subprocess.run(
                        ["python3", script_path],
                        cwd=backend_dir,
                        check=True,
                        capture_output=True
                    )
                    print(f"✅ 网络数据已更新")
                except Exception as e:
                    print(f"⚠️  重新生成网络失败（不影响添加结果）: {e}")
        
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
