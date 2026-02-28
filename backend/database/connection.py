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
        # 添加超时设置以避免长时间hang
        _client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000,  # 服务器选择超时5秒
            connectTimeoutMS=5000,          # 连接超时5秒
            socketTimeoutMS=5000,           # socket超时5秒
            maxPoolSize=10,                 # 最大连接池大小
            minPoolSize=1,                  # 最小连接池大小
            retryWrites=True,               # 启用重试写入
            retryReads=True                 # 启用重试读取
        )
        _database = _client[DATABASE_NAME]
        print(f"✅ MongoDB连接成功: {DATABASE_NAME}")
    
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
