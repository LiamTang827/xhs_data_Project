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
                error_msg = f"创作者已存在: {nickname}"
                await self._update_progress("failed", 0, error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "creator": existing
                }
            
            # 3. 调用collector爬取数据
            await self._update_progress("fetching", 20, "正在爬取创作者笔记...")
            fetch_result = await self._fetch_user_notes()
            
            if not fetch_result["success"]:
                error_msg = fetch_result["error"]
                await self._update_progress("failed", 0, error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
            
            notes_count = fetch_result["notes_count"]
            await self._update_progress("fetching", 50, f"成功爬取 {notes_count} 篇笔记")
            
            # 4. 提取关键词（跳过AI分析，节省API费用）
            await self._update_progress("analyzing", 60, "正在提取内容话题...")
            extract_result = await self._extract_topics()
            
            if not extract_result["success"]:
                error_msg = extract_result["error"]
                await self._update_progress("failed", 0, error_msg)
                return {
                    "success": False,
                    "error": error_msg
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
            
            # 检查API错误
            if notes_result.get('success') == False:
                return {"success": False, "error": notes_result.get('error', '获取笔记失败')}
            
            if not notes_result or not notes_result.get('notes'):
                return {"success": False, "error": "用户ID不存在或没有笔记，请检查用户ID是否正确"}
            
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
        """从笔记中提取#话题标签并生成完整profile（不使用AI）"""
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
            for note in notes[:30]:  # 分析前30条笔记
                title = note.get('title', '') or ''
                desc = note.get('desc') or ''
                text = title + ' ' + desc
                
                # 提取 #xxx 或 #xxx# 格式的话题
                tags = re.findall(r'#([\w\u4e00-\u9fa5]+)', text)
                hashtags.extend(tags)
            
            # 统计词频，取前8个高频标签
            if hashtags:
                tag_count = Counter(hashtags)
                topics = [tag for tag, count in tag_count.most_common(8)]
            else:
                topics = ["综合内容"]
            
            # 计算统计数据
            total_likes = sum(note.get('likes', 0) for note in notes)
            total_collects = sum(note.get('collected_count', 0) for note in notes)
            total_comments = sum(note.get('comments_count', 0) for note in notes)
            total_shares = sum(note.get('share_count', 0) for note in notes)
            
            # 创建或更新完整的profile
            profile_repo = UserProfileRepository()
            existing_profile = profile_repo.get_by_user_id(self.user_id, "xiaohongshu")
            
            # 从snapshot获取user_info（第一个笔记的user字段）
            user_info = notes[0].get('user', {}) if notes else {}
            nickname = user_info.get('nickname', self.user_id)
            
            # 构建profile_data
            profile_data = {
                'content_topics': topics,
                'content_style': f"以{topics[0]}为主的创作者" if topics else "综合内容创作者",
                'value_points': [f"{topic}分享" for topic in topics[:3]],
                'engagement': {
                    'likes': total_likes,
                    'collects': total_collects,
                    'comments': total_comments,
                    'shares': total_shares
                }
            }
            
            # 获取基础信息和统计（从user_info如果有的话）
            basic_info = {
                'nickname': nickname,
                'red_id': user_info.get('red_id', ''),
                'desc': user_info.get('desc', ''),
                'avatar': user_info.get('images', ''),
                'gender': user_info.get('gender', 0),
                'ip_location': user_info.get('ip_location', '')
            }
            
            stats = {
                'fans': user_info.get('fans', 0),
                'follows': user_info.get('follows', 0),
                'total_liked': user_info.get('liked', 0),
                'total_collected': user_info.get('collected', 0),
                'note_count': len(notes)
            }
            
            if existing_profile:
                # 更新现有profile
                profile_repo.collection.update_one(
                    {"user_id": self.user_id, "platform": "xiaohongshu"},
                    {"$set": {
                        "profile_data": profile_data,
                        "basic_info": basic_info,
                        "stats": stats,
                        "updated_at": datetime.now()
                    }}
                )
                print(f"✅ 更新profile: {', '.join(topics)}")
            else:
                # 创建新profile
                profile_doc = {
                    'platform': 'xiaohongshu',
                    'user_id': self.user_id,
                    'nickname': nickname,
                    'basic_info': basic_info,
                    'stats': stats,
                    'profile_data': profile_data,
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }
                profile_repo.create_profile(profile_doc)
                print(f"✅ 创建profile: {nickname} - {', '.join(topics)}")
            
            # 生成embedding（基于话题的简单向量）
            await self._generate_embedding(topics)
            
            # 获取最终的profile
            creator_data = profile_repo.get_by_user_id(self.user_id, "xiaohongshu")
            
            return {
                "success": True,
                "creator": creator_data
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"生成profile失败: {str(e)}"
            }
    
    async def _generate_embedding(self, topics: list):
        """生成embedding向量（基于话题的简单向量）"""
        try:
            from database import UserEmbeddingRepository
            
            embedding_repo = UserEmbeddingRepository()
            
            # 检查是否已存在
            existing = embedding_repo.collection.find_one({
                'platform': 'xiaohongshu',
                'user_id': self.user_id
            })
            
            if existing:
                print(f"  ℹ️  embedding已存在，跳过")
                return
            
            # 生成简单的话题向量（384维，模拟bge-small-zh-v1.5）
            # 使用话题的hash值生成确定性向量
            import hashlib
            import numpy as np
            
            # 将所有话题连接成一个字符串
            topic_text = ' '.join(topics)
            
            # 使用hash生成种子
            seed = int(hashlib.md5(topic_text.encode()).hexdigest()[:8], 16)
            np.random.seed(seed)
            
            # 生成384维的向量
            embedding_vector = np.random.randn(384).astype(np.float32)
            # 归一化
            embedding_vector = embedding_vector / np.linalg.norm(embedding_vector)
            
            # 保存embedding
            embedding_doc = {
                'platform': 'xiaohongshu',
                'user_id': self.user_id,
                'embedding': embedding_vector.tolist(),
                'model': 'topic_hash_v1',
                'dimension': 384,
                'topics': topics,
                'created_at': datetime.now()
            }
            
            embedding_repo.create_embedding(embedding_doc)
            print(f"  ✅ 生成embedding向量 (384维)")
            
        except Exception as e:
            print(f"  ⚠️  生成embedding失败: {e}")
            # embedding失败不影响主流程
    
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
