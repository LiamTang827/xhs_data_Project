#!/usr/bin/env python3
"""
创作者数据采集任务管理
负责执行collector和pipeline流程
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import traceback

# 添加collectors路径
project_root = Path(__file__).resolve().parent.parent.parent
collectors_path = project_root / "collectors" / "xiaohongshu"
sys.path.insert(0, str(collectors_path))
sys.path.insert(0, str(project_root / "backend"))

from database import UserSnapshotRepository, UserProfileRepository
from database.connection import get_database


class CollectorTask:
    """创作者数据采集任务"""
    
    def __init__(self, user_id: str, task_id: str):
        self.user_id = user_id
        self.task_id = task_id
        self.db = get_database()
        self.task_logs = self.db.task_logs
        
    async def run(self) -> Dict[str, Any]:
        """
        执行完整的采集和分析流程
        
        Returns:
            结果字典 {"success": bool, "creator": dict, "error": str}
        """
        try:
            # 1. 初始化任务状态
            await self._update_progress("initializing", 0, "初始化任务...")
            
            # 2. 检查创作者是否已存在
            await self._update_progress("checking", 10, "检查创作者是否存在...")
            profile_repo = UserProfileRepository()
            existing = profile_repo.get_profile_by_user_id(self.user_id, "xiaohongshu")
            
            if existing:
                return {
                    "success": False,
                    "error": f"创作者已存在: {existing.get('nickname', self.user_id)}",
                    "creator": existing
                }
            
            # 3. 调用collector爬取数据
            await self._update_progress("fetching", 20, "正在爬取创作者笔记...")
            fetch_result = await self._fetch_user_notes()
            
            if not fetch_result["success"]:
                return {
                    "success": False,
                    "error": fetch_result["error"]
                }
            
            notes_count = fetch_result["notes_count"]
            await self._update_progress("fetching", 50, f"成功爬取 {notes_count} 篇笔记")
            
            # 4. 调用pipeline分析数据
            await self._update_progress("analyzing", 60, "正在分析创作者画像...")
            analysis_result = await self._analyze_user()
            
            if not analysis_result["success"]:
                return {
                    "success": False,
                    "error": analysis_result["error"]
                }
            
            creator_data = analysis_result["creator"]
            await self._update_progress("analyzing", 90, "分析完成")
            
            # 5. 完成
            await self._update_progress("completed", 100, "创作者添加成功")
            
            return {
                "success": True,
                "creator": creator_data,
                "message": f"成功添加创作者: {creator_data.get('nickname', self.user_id)}"
            }
            
        except Exception as e:
            error_msg = f"任务执行失败: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            
            await self._update_progress("failed", 0, error_msg)
            
            return {
                "success": False,
                "error": error_msg
            }
    
    async def _fetch_user_notes(self) -> Dict[str, Any]:
        """调用collector爬取笔记"""
        try:
            # 导入collector
            from collector import fetch_user_notes, save_to_mongodb
            
            # 在线程池中执行同步代码
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                fetch_user_notes,
                self.user_id
            )
            
            if not result:
                return {"success": False, "error": "无法获取用户数据，请检查用户ID是否正确"}
            
            user_info = result.get("user")
            notes = result.get("notes", [])
            
            if not notes:
                return {"success": False, "error": "该用户没有公开笔记"}
            
            # 保存到MongoDB
            await loop.run_in_executor(
                None,
                save_to_mongodb,
                user_info,
                notes
            )
            
            return {
                "success": True,
                "notes_count": len(notes),
                "user_info": user_info
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"爬取失败: {str(e)}"
            }
    
    async def _analyze_user(self) -> Dict[str, Any]:
        """调用pipeline分析用户"""
        try:
            # 导入pipeline
            from pipeline import process_user
            from FlagEmbedding import FlagModel
            
            # 加载embedding模型
            model_name = "BAAI/bge-small-zh-v1.5"
            print(f"📦 加载embedding模型: {model_name}")
            embedding_model = FlagModel(model_name, use_fp16=True)
            
            # 在线程池中执行同步代码
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                None,
                process_user,
                self.user_id,
                embedding_model
            )
            
            if not success:
                return {"success": False, "error": "分析失败，请查看日志"}
            
            # 获取创建的profile
            profile_repo = UserProfileRepository()
            creator_data = profile_repo.get_profile_by_user_id(self.user_id, "xiaohongshu")
            
            if not creator_data:
                return {"success": False, "error": "分析完成但未找到创建的profile"}
            
            return {
                "success": True,
                "creator": creator_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"分析失败: {str(e)}"
            }
    
    async def _update_progress(self, status: str, percent: int, message: str):
        """更新任务进度"""
        update_data = {
            "status": status,
            "progress": {
                "percent": percent,
                "message": message
            },
            "updated_at": datetime.now()
        }
        
        if status in ["completed", "failed"]:
            update_data["finished_at"] = datetime.now()
        
        self.task_logs.update_one(
            {"task_id": self.task_id},
            {"$set": update_data},
            upsert=True
        )
        
        print(f"[Task {self.task_id}] {status.upper()}: {message} ({percent}%)")


async def create_collector_task(user_id: str) -> Dict[str, Any]:
    """
    创建并初始化采集任务
    
    Args:
        user_id: 小红书用户ID
        
    Returns:
        {"task_id": str, "status": str}
    """
    import uuid
    
    task_id = f"add_creator_{uuid.uuid4().hex[:8]}"
    db = get_database()
    
    # 创建任务记录
    task_doc = {
        "task_id": task_id,
        "task_type": "add_creator",
        "user_id": user_id,
        "status": "pending",
        "progress": {
            "percent": 0,
            "message": "任务已创建，等待执行..."
        },
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    db.task_logs.insert_one(task_doc)
    
    return {
        "task_id": task_id,
        "status": "pending"
    }


async def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """
    获取任务状态
    
    Args:
        task_id: 任务ID
        
    Returns:
        任务状态字典
    """
    db = get_database()
    task = db.task_logs.find_one({"task_id": task_id}, {"_id": 0})
    
    if task:
        # 转换datetime为字符串
        for key in ["created_at", "updated_at", "finished_at"]:
            if key in task and task[key]:
                task[key] = task[key].isoformat()
    
    return task
