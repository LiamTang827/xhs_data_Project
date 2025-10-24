from app.xhs_utils.database import if_database
from loguru import logger   
async def save_user(user_data: dict):
    """保存/更新用户数据到数据库"""
    try:
        db = if_database()
        if db is None:
            logger.error("仓库(user_db)：无法获取数据库实例！")
            raise ConnectionError("数据库未连接")
            
        user_collection = db.get_collection("users")
        
        await user_collection.update_one(
            {'user_id': user_data['user_id']}, # 检查字典里的 user_id
            {'$set': user_data},                 # 存入整个字典
            upsert=True                          # 如果没有则插入新文档
        )
        logger.info(f"仓库(user_db)：用户 {user_data.get('user_id')} 已保存。")
        
    except Exception as e:
        logger.error(f"仓库(user_db)：存储用户 {user_data.get('user_id')} 失败: {e}")
        raise e