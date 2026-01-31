"""
MongoDB Connection Management
"""

from pathlib import Path
from pymongo import MongoClient
from pymongo.database import Database
from typing import Optional

# 使用集中化配置管理
from core.config import settings

# MongoDB连接配置（从settings获取）
MONGO_URI = settings.MONGO_URI
DATABASE_NAME = settings.DATABASE_NAME

_client: Optional[MongoClient] = None
_database: Optional[Database] = None


def get_database() -> Database:
    """
    获取MongoDB数据库实例（单例模式）
    
    Returns:
        Database: MongoDB数据库实例
    """
    global _client, _database
    
    if _database is None:
        try:
            print(f"🔄 正在连接 MongoDB...")
            print(f"📍 数据库名称: {DATABASE_NAME}")
            print(f"🔗 URI前缀: {MONGO_URI[:20]}...")
            
            _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            _database = _client[DATABASE_NAME]
            
            # 测试连接
            _client.admin.command('ping')
            print(f"✅ MongoDB连接成功: {DATABASE_NAME}")
        except Exception as e:
            print(f"❌ MongoDB连接失败: {str(e)}")
            raise RuntimeError(f"无法连接到MongoDB: {str(e)}") from e
    
    return _database


def close_connection():
    """关闭MongoDB连接"""
    global _client, _database
    
    if _client is not None:
        _client.close()
        _client = None
        _database = None
        print("✅ MongoDB连接已关闭")


def test_connection() -> bool:
    """
    测试MongoDB连接
    
    Returns:
        bool: 连接是否成功
    """
    try:
        db = get_database()
        # 尝试执行一个简单的命令
        db.command('ping')
        print("✅ MongoDB连接测试成功")
        return True
    except Exception as e:
        print(f"❌ MongoDB连接测试失败: {e}")
        return False
