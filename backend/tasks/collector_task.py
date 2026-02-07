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
            existing = profile_repo.get_by_user_id(self.user_id, "xiaohongshu")
            
            if existing:
                nickname = existing.get('basic_info', {}).get('nickname') or existing.get('nickname', self.user_id)
                return {
                    "success": False,
                    "error": f"创作者已存在: {nickname}",
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
            
            # 4. 提取关键词（跳过AI分析，节省API费用）
            await self._update_progress("analyzing", 60, "正在提取内容话题...")
            extract_result = await self._extract_topics()
            
            if not extract_result["success"]:
                return {
                    "success": False,
                    "error": extract_result["error"]
                }
            
            creator_data = extract_result["creator"]
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
            from collector import fetch_user_notes, fetch_user_info, save_to_mongodb
            
            # 在线程池中执行同步代码
            loop = asyncio.get_event_loop()
            
            # 1. 获取笔记
            notes_result = await loop.run_in_executor(
                None,
                fetch_user_notes,
                self.user_id
            )
            
            if not notes_result or not notes_result.get('notes'):
                return {"success": False, "error": "无法获取用户笔记，请检查用户ID是否正确"}
            
            notes = notes_result.get('notes', [])
            
            # 2. 获取用户信息
            user_info = await loop.run_in_executor(
                None,
                fetch_user_info,
                self.user_id
            )
            
            if not user_info:
                return {"success": False, "error": "无法获取用户详细信息"}
            
            # 3. 保存到MongoDB（新版collector需要这个格式）
            data = {
                'notes': notes,
                'user_info': user_info
            }
            
            await loop.run_in_executor(
                None,
                save_to_mongodb,
                self.user_id,
                data
            )
            
            return {
                "success": True,
                "notes_count": len(notes),
                "user_info": user_info
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"爬取失败: {str(e)}"
            }
    
    async def _extract_topics(self) -> Dict[str, Any]:
        """从笔记中提取#话题标签（不使用AI分析）"""
        try:
            import re
            from collections import Counter
            
            # 获取snapshot
            snapshot_repo = UserSnapshotRepository()
            snapshot = snapshot_repo.get_by_user_id(self.user_id, "xiaohongshu")
            
            if not snapshot:
                return {"success": False, "error": "未找到笔记数据"}
            
            notes = snapshot.get('notes', [])
            
            # 提取#话题标签
            hashtags = []
            for note in notes[:20]:  # 分析前20条笔记
                title = note.get('title', '') or ''
                desc = note.get('desc') or ''
                text = title + ' ' + desc
                
                # 提取 #xxx 或 #xxx# 格式的话题
                # 匹配 # 后面跟着的中文、英文、数字
                tags = re.findall(r'#([\w\u4e00-\u9fa5]+)', text)
                hashtags.extend(tags)
            
            # 统计词频，取前5个高频标签
            if hashtags:
                tag_count = Counter(hashtags)
                topics = [tag for tag, count in tag_count.most_common(8)]  # 取前8个
            else:
                topics = ["综合内容"]
            
            # 更新profile，添加提取的topics
            profile_repo = UserProfileRepository()
            profile = profile_repo.get_by_user_id(self.user_id, "xiaohongshu")
            
            if profile:
                # 更新profile_data中的content_topics
                profile_data = profile.get('profile_data', {})
                profile_data['content_topics'] = topics
                
                profile_repo.collection.update_one(
                    {"user_id": self.user_id, "platform": "xiaohongshu"},
                    {"$set": {"profile_data": profile_data}}
                )
                
                print(f"✅ 提取话题: {', '.join(topics)}")
            
            # 获取更新后的profile
            creator_data = profile_repo.get_by_user_id(self.user_id, "xiaohongshu")
            
            return {
                "success": True,
                "creator": creator_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"提取话题失败: {str(e)}"
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
