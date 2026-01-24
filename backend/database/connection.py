"""
MongoDB Connection Management
"""

import os
from pathlib import Path
from pymongo import MongoClient
from pymongo.database import Database
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量（从项目根目录或backend目录）
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
project_root = backend_dir.parent

# 尝试从项目根目录或backend目录加载.env
for env_path in [project_root / '.env', backend_dir / '.env']:
    if env_path.exists():
        load_dotenv(env_path)
        break

# MongoDB连接配置
MONGO_URI = os.getenv(
    "MONGO_URI"
)
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is required. Please copy .env.example to .env and set your MongoDB URI.")

DATABASE_NAME = os.getenv("DATABASE_NAME", "tikhub_xhs")

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
        _client = MongoClient(MONGO_URI)
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
