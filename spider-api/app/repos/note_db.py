from app.xhs_utils.database import if_database
from loguru import logger
async def save_note(note_data: dict):
    """保存笔记数据到数据库"""
    try:
        db = if_database()
        if db is None:
            logger.error("仓库(note_db)：无法获取数据库实例！")
            raise ConnectionError("数据库未连接")
            
        note_collection = db.get_collection("notes")
        
        await note_collection.update_one(
            {'note_id': note_data['note_id']}, # 检查字典里的 note_id
            {'$set': note_data},                 # 存入整个字典
            upsert=True                          # 如果没有则插入新文档
        )
        logger.info(f"仓库(note_db)：笔记 {note_data.get('note_id')} 已保存。")
        
    except Exception as e:
        logger.error(f"仓库(note_db)：存储笔记 {note_data.get('note_id')} 失败: {e}")
        raise e
