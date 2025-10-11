import os
import motor.motor_asyncio
from loguru import logger

MONGO_URI = os.getenv("MONGO_URI")
db_client = None
database = None

async def connect_to_mongo():
    """在应用程式启动时建立数据库连接并检查"""
    global db_client, database
    logger.info("正在连接到 MongoDB Atlas...")
    if not MONGO_URI:
        logger.error("❌ MONGO_URI 环境变量未设置，无法连接到数据库。")
        return
    try:
        db_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
        await db_client.admin.command('ping')
        database = db_client.get_database("xhs_data") # 或者从URI中解析
        logger.success("✅ 成功连接到 MongoDB Atlas！")
    except Exception as e:
        logger.error(f"❌ 连接 MongoDB Atlas 失败: {e}")
        db_client = None
        database = None

async def close_mongo_connection():
    """在应用程式关闭时中断数据库连接"""
    global db_client
    if db_client:
        db_client.close()
        logger.info("MongoDB 连接已关闭。")

def get_database():
    """获取数据库实例"""
    return database