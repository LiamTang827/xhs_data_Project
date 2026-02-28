"""
Repository Pattern - 数据访问层
统一封装MongoDB的CRUD操作
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pymongo.database import Database
from pymongo.collection import Collection

from .connection import get_database
from .models import (
    PlatformType,
    UserProfile,
    UserSnapshot,
    UserEmbedding,
    NoteEmbedding,
    CreatorNetwork,
    StylePrompt,
    StylePromptType,
    PlatformConfig
)


class BaseRepository:
    """基础仓库类"""
    
    def __init__(self, collection_name: str):
        self.db: Database = get_database()
        self.collection: Collection = self.db[collection_name]
    
    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """查询单个文档"""
        return self.collection.find_one(query)
    
    def find_many(self, query: Dict[str, Any], limit: int = 0) -> List[Dict[str, Any]]:
        """查询多个文档"""
        cursor = self.collection.find(query)
        if limit > 0:
            cursor = cursor.limit(limit)
        return list(cursor)
    
    def insert_one(self, document: Dict[str, Any]) -> str:
        """插入单个文档"""
        result = self.collection.insert_one(document)
        return str(result.inserted_id)
    
    def update_one(self, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """更新单个文档"""
        result = self.collection.update_one(query, {"$set": update})
        return result.modified_count > 0
    
    def delete_one(self, query: Dict[str, Any]) -> bool:
        """删除单个文档"""
        result = self.collection.delete_one(query)
        return result.deleted_count > 0
    
    def count(self, query: Dict[str, Any] = {}) -> int:
        """统计文档数量"""
        return self.collection.count_documents(query)


# =====================================================
# 1. User Profile Repository
# =====================================================

class UserProfileRepository(BaseRepository):
    """用户档案仓库"""
    
    def __init__(self):
        super().__init__("user_profiles")
    
    def get_by_user_id(self, user_id: str, platform: str = "xiaohongshu") -> Optional[Dict[str, Any]]:
        """
        根据user_id获取用户档案
        
        Args:
            user_id: 用户ID
            platform: 平台类型
            
        Returns:
            用户档案数据 or None
        """
        return self.find_one({"user_id": user_id, "platform": platform})
    
    def get_all_profiles(self, platform: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取所有用户档案
        
        Args:
            platform: 平台类型，None表示所有平台
            limit: 最大返回数量，默认100
            
        Returns:
            用户档案列表
        """
        query = {"platform": platform} if platform else {}
        # 只返回必要字段，避免加载大字段如embedding
        projection = {
            "user_id": 1,
            "nickname": 1,
            "platform": 1,
            "basic_info": 1,
            "profile_data": 1,
            "stats": 1,
            "_id": 0
        }
        cursor = self.collection.find(query, projection)
        if limit > 0:
            cursor = cursor.limit(limit)
        return list(cursor)
    
    def create_profile(self, profile_data: Dict[str, Any]) -> str:
        """
        创建用户档案
        
        Args:
            profile_data: 档案数据
            
        Returns:
            插入的文档ID
        """
        profile_data['created_at'] = datetime.now()
        profile_data['updated_at'] = datetime.now()
        return self.insert_one(profile_data)
    
    def update_profile(self, user_id: str, platform: str, update_data: Dict[str, Any]) -> bool:
        """
        更新用户档案
        
        Args:
            user_id: 用户ID
            platform: 平台类型
            update_data: 更新的数据
            
        Returns:
            是否更新成功
        """
        update_data['updated_at'] = datetime.now()
        return self.update_one(
            {"user_id": user_id, "platform": platform},
            update_data
        )
    
    def get_profile_by_nickname(self, nickname: str, platform: str = "xiaohongshu") -> Optional[Dict[str, Any]]:
        """
        根据昵称获取用户档案
        
        Args:
            nickname: 用户昵称
            platform: 平台类型
            
        Returns:
            用户档案数据 or None
        """
        return self.find_one({"nickname": nickname, "platform": platform})


# =====================================================
# 2. User Snapshot Repository
# =====================================================

class UserSnapshotRepository(BaseRepository):
    """用户笔记快照仓库"""
    
    def __init__(self):
        super().__init__("user_snapshots")
    
    def get_by_user_id(self, user_id: str, platform: str = "xiaohongshu") -> Optional[Dict[str, Any]]:
        """
        根据user_id获取笔记快照
        
        Args:
            user_id: 用户ID
            platform: 平台类型
            
        Returns:
            笔记快照数据 or None
        """
        return self.find_one({"user_id": user_id, "platform": platform})
    
    def get_notes(self, user_id: str, platform: str = "xiaohongshu", limit: int = 5) -> List[Dict[str, Any]]:
        """
        获取用户的笔记列表
        
        Args:
            user_id: 用户ID
            platform: 平台类型
            limit: 返回笔记数量
            
        Returns:
            笔记列表
        """
        snapshot = self.get_by_user_id(user_id, platform)
        if snapshot and 'notes' in snapshot:
            return snapshot['notes'][:limit]
        return []
    
    def create_snapshot(self, snapshot_data: Dict[str, Any]) -> str:
        """
        创建笔记快照
        
        Args:
            snapshot_data: 快照数据
            
        Returns:
            插入的文档ID
        """
        snapshot_data['created_at'] = datetime.now()
        return self.insert_one(snapshot_data)
    
    def update_snapshot(self, user_id: str, platform: str, notes: List[Dict[str, Any]]) -> bool:
        """
        更新笔记快照
        
        Args:
            user_id: 用户ID
            platform: 平台类型
            notes: 笔记列表
            
        Returns:
            是否更新成功
        """
        return self.update_one(
            {"user_id": user_id, "platform": platform},
            {"notes": notes, "total_notes": len(notes), "updated_at": datetime.now()}
        )


# =====================================================
# 3. User Embedding Repository
# =====================================================

class UserEmbeddingRepository(BaseRepository):
    """用户向量embedding仓库"""
    
    def __init__(self):
        super().__init__("user_embeddings")
    
    def get_by_user_id(self, user_id: str, platform: str = "xiaohongshu") -> Optional[Dict[str, Any]]:
        """
        根据user_id获取embedding
        
        Args:
            user_id: 用户ID
            platform: 平台类型
            
        Returns:
            embedding数据 or None
        """
        return self.find_one({"user_id": user_id, "platform": platform})
    
    def get_all_embeddings(self, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取所有embeddings
        
        Args:
            platform: 平台类型，None表示所有平台
            
        Returns:
            embedding列表
        """
        query = {"platform": platform} if platform else {}
        return self.find_many(query)
    
    def create_embedding(self, embedding_data: Dict[str, Any]) -> str:
        """
        创建embedding
        
        Args:
            embedding_data: embedding数据
            
        Returns:
            插入的文档ID
        """
        embedding_data['created_at'] = datetime.now()
        return self.insert_one(embedding_data)
    
    def update_embedding(self, user_id: str, platform: str, embedding: List[float]) -> bool:
        """
        更新embedding
        
        Args:
            user_id: 用户ID
            platform: 平台类型
            embedding: 向量数据
            
        Returns:
            是否更新成功
        """
        return self.update_one(
            {"user_id": user_id, "platform": platform},
            {"embedding": embedding, "updated_at": datetime.now()}
        )


# =====================================================
# 4. Creator Network Repository
# =====================================================

class CreatorNetworkRepository(BaseRepository):
    """创作者网络仓库"""
    
    def __init__(self):
        super().__init__("creator_networks")
    
    def get_latest_network(self, platform: str = "xiaohongshu") -> Optional[Dict[str, Any]]:
        """
        获取最新的创作者网络
        
        Args:
            platform: 平台类型
            
        Returns:
            网络数据 or None
        """
        # 优化：只投影需要的字段，避免读取整个大文档
        result = self.collection.find_one(
            {"platform": platform},
            {
                "network_data": 1,
                "created_at": 1,
                "platform": 1
            },
            sort=[("created_at", -1)]
        )
        return result
    
    def create_network(self, network_data: Dict[str, Any]) -> str:
        """
        创建创作者网络
        
        Args:
            network_data: 网络数据
            
        Returns:
            插入的文档ID
        """
        network_data['created_at'] = datetime.now()
        return self.insert_one(network_data)


# =====================================================
# 5. Style Prompt Repository
# =====================================================

class StylePromptRepository(BaseRepository):
    """风格提示词仓库"""
    
    def __init__(self):
        super().__init__("style_prompts")
    
    def get_by_type(self, prompt_type: str, platform: str = "xiaohongshu") -> Optional[Dict[str, Any]]:
        """
        根据类型获取提示词模板
        
        Args:
            prompt_type: 提示词类型
            platform: 平台类型
            
        Returns:
            提示词数据 or None
        """
        return self.find_one({"prompt_type": prompt_type, "platform": platform})
    
    def get_all_prompts(self, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取所有提示词模板
        
        Args:
            platform: 平台类型
            
        Returns:
            提示词列表
        """
        query = {"platform": platform} if platform else {}
        return self.find_many(query)
    
    def create_prompt(self, prompt_data: Dict[str, Any]) -> str:
        """
        创建提示词模板
        
        Args:
            prompt_data: 提示词数据
            
        Returns:
            插入的文档ID
        """
        prompt_data['created_at'] = datetime.now()
        prompt_data['updated_at'] = datetime.now()
        return self.insert_one(prompt_data)
    
    def update_prompt(self, prompt_type: str, platform: str, update_data: Dict[str, Any]) -> bool:
        """
        更新提示词模板
        
        Args:
            prompt_type: 提示词类型
            platform: 平台类型
            update_data: 更新数据
            
        Returns:
            是否更新成功
        """
        update_data['updated_at'] = datetime.now()
        return self.update_one(
            {"prompt_type": prompt_type, "platform": platform},
            update_data
        )


# =====================================================
# 6. Note Embedding Repository
# =====================================================

class NoteEmbeddingRepository(BaseRepository):
    """笔记Embedding仓库 - 用于语义搜索"""

    def __init__(self):
        super().__init__("note_embeddings")

    def get_by_note_id(self, note_id: str) -> Optional[Dict[str, Any]]:
        """根据笔记ID获取embedding"""
        return self.find_one({"note_id": note_id})

    def get_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """获取某用户所有笔记的embedding"""
        return self.find_many({"user_id": user_id})

    def get_all_embeddings(self, limit: int = 0) -> List[Dict[str, Any]]:
        """获取所有笔记embedding（用于搜索时的批量加载）"""
        projection = {
            "note_id": 1, "user_id": 1, "title": 1, "desc": 1,
            "embedding": 1, "likes": 1, "collected_count": 1,
            "comments_count": 1, "share_count": 1, "engagement_score": 1,
            "nickname": 1, "avatar": 1, "note_create_time": 1,
            "_id": 0
        }
        cursor = self.collection.find({}, projection)
        if limit > 0:
            cursor = cursor.limit(limit)
        return list(cursor)

    def get_all_embeddings_only(self) -> List[Dict[str, Any]]:
        """仅获取note_id和embedding向量（轻量查询，用于内存搜索）"""
        projection = {"note_id": 1, "embedding": 1, "_id": 0}
        return list(self.collection.find({}, projection))

    def upsert_note_embedding(self, note_data: Dict[str, Any]) -> bool:
        """插入或更新笔记embedding"""
        note_data["created_at"] = datetime.now()
        result = self.collection.update_one(
            {"note_id": note_data["note_id"]},
            {"$set": note_data},
            upsert=True
        )
        return result.upserted_id is not None or result.modified_count > 0

    def bulk_upsert(self, notes: List[Dict[str, Any]]) -> int:
        """批量插入/更新笔记embedding"""
        from pymongo import UpdateOne
        if not notes:
            return 0
        operations = [
            UpdateOne(
                {"note_id": n["note_id"]},
                {"$set": {**n, "created_at": datetime.now()}},
                upsert=True
            )
            for n in notes
        ]
        result = self.collection.bulk_write(operations)
        return result.upserted_count + result.modified_count

    def get_stats(self) -> Dict[str, Any]:
        """获取笔记embedding统计"""
        total = self.count()
        pipeline = [
            {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
            {"$count": "total_users"}
        ]
        user_count_result = list(self.collection.aggregate(pipeline))
        total_users = user_count_result[0]["total_users"] if user_count_result else 0
        return {
            "total_notes": total,
            "total_creators": total_users
        }


# =====================================================
# 7. Platform Config Repository
# =====================================================

class PlatformConfigRepository(BaseRepository):
    """平台配置仓库"""
    
    def __init__(self):
        super().__init__("platform_configs")
    
    def get_by_platform(self, platform: str) -> Optional[Dict[str, Any]]:
        """
        根据平台获取配置
        
        Args:
            platform: 平台类型
            
        Returns:
            配置数据 or None
        """
        return self.find_one({"platform": platform})
    
    def get_all_configs(self) -> List[Dict[str, Any]]:
        """
        获取所有平台配置
        
        Returns:
            配置列表
        """
        return self.find_many({})
    
    def create_config(self, config_data: Dict[str, Any]) -> str:
        """
        创建平台配置
        
        Args:
            config_data: 配置数据
            
        Returns:
            插入的文档ID
        """
        config_data['created_at'] = datetime.now()
        config_data['updated_at'] = datetime.now()
        return self.insert_one(config_data)
    
    def update_config(self, platform: str, update_data: Dict[str, Any]) -> bool:
        """
        更新平台配置
        
        Args:
            platform: 平台类型
            update_data: 更新数据
            
        Returns:
            是否更新成功
        """
        update_data['updated_at'] = datetime.now()
        return self.update_one(
            {"platform": platform},
            update_data
        )
