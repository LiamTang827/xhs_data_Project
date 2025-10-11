import os
import motor.motor_asyncio
from loguru import logger

# 初始化为 None，等待 connect_to_mongo 被调用
db_client = None
database = None

async def connect_to_mongo():
    """在应用程式启动时建立数据库连接并检查"""
    global db_client, database
    
    # 在这里读取环境变量，确保 load_dotenv() 已经执行
    MONGO_URI = os.getenv("MONGO_URI")
    
    logger.info("正在连接到 MongoDB Atlas...")
    
    if not MONGO_URI:
        logger.error("❌ MONGO_URI 环境变量未设置，无法连接到数据库。")
        logger.error("请检查 .env 文件是否存在且包含正确的 MONGO_URI 配置。")
        return
    
    # 打印部分连接信息用于调试（隐藏密码）
    try:
        from urllib.parse import urlparse
        parsed = urlparse(MONGO_URI)
        safe_uri = f"{parsed.scheme}://{parsed.username}:****@{parsed.hostname}/..."
        logger.info(f"使用连接字符串: {safe_uri}")
    except Exception:
        logger.warning("无法解析连接字符串用于调试显示")
    
    try:
        db_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
        # 测试连接
        await db_client.admin.command('ping')
        database = db_client.get_database("xhs_data")
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
    if database is None:
        logger.warning("⚠️ 数据库尚未初始化！请确保应用已启动并调用了 connect_to_mongo()")
    return database