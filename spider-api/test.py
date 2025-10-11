# 创建文件: test_mongo.py
import asyncio
import os
from dotenv import load_dotenv
import motor.motor_asyncio

async def test_connection():
    load_dotenv()
    MONGO_URI = os.getenv("MONGO_URI")
    COOKIES = os.getenv("COOKIES")
    
    print("=== 环境变量检查 ===")
    print(f"MONGO_URI: {'已设置' if MONGO_URI else '❌ 未设置'}")
    print(f"COOKIES: {'已设置' if COOKIES else '❌ 未设置'}")
    
    if COOKIES:
        print(f"COOKIES 长度: {len(COOKIES)} 字符")
        print(f"COOKIES 预览: {COOKIES[:50]}...")
    
    print("\n=== MongoDB 连接测试 ===")
    if not MONGO_URI:
        print("❌ MONGO_URI 环境变量未设置")
        return
    
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
        await client.admin.command('ping')
        print("✅ MongoDB 连接成功!")
        
        db_list = await client.list_database_names()
        print(f"数据库列表: {db_list}")
        
        db = client["xhs_data"]
        collections = await db.list_collection_names()
        print(f"xhs_data 集合: {collections}")
        
        # 测试创建一个文档
        print("\n=== 测试数据库写入 ===")
        test_collection = db["test_collection"]
        result = await test_collection.insert_one({"test": "data", "timestamp": "2025-10-04"})
        print(f"✅ 测试文档插入成功，ID: {result.inserted_id}")
        
        # 删除测试文档
        await test_collection.delete_one({"_id": result.inserted_id})
        print("✅ 测试文档已清理")
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_connection())