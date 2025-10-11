import os
import motor.motor_asyncio
from loguru import logger

MONGO_URI = os.getenv("MONGO_URI")

db_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)

# 获取在连接字符串(MONGO_URI)中指定的那个数据库，例如 xhs_data
database = db_client["xhs_data"]

# 从数据库中获取名为 "notes" 的集合
note_collection = database.get_collection("notes")

# 从数据库中获取名为 "users" 的集合 
user_collection = database.get_collection("users")
# --------------------------------------------------------------------

def get_database():
    """返回数据库实例"""
    return database

async def connect_to_mongo():
    """在应用程式启动时建立数据库连接并检查"""
    logger.info("正在连接到 MongoDB Atlas...")
    try:
        await db_client.admin.command('ping')
        logger.success("✅ 成功连接到 MongoDB Atlas！")
    except Exception as e:
        logger.error(f"❌ 连接 MongoDB Atlas 失败: {e}")

async def close_mongo_connection():
    """在应用程式关闭时中断数据库连接"""
    db_client.close()
    logger.info("MongoDB 连接已关闭。")