#!/usr/bin/env python3
"""
Railway 环境变量检查脚本
用于诊断环境变量配置问题
"""
import os
import sys

def check_env():
    print("=" * 60)
    print("🔍 环境变量检查")
    print("=" * 60)
    
    # 检查关键环境变量
    env_vars = {
        "MONGO_URI": os.getenv("MONGO_URI"),
        "DATABASE_NAME": os.getenv("DATABASE_NAME"),
        "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY"),
        "PORT": os.getenv("PORT"),
    }
    
    all_ok = True
    
    for key, value in env_vars.items():
        if value is None:
            print(f"❌ {key}: 未设置")
            all_ok = False
        else:
            # 隐藏敏感信息
            if "KEY" in key or "URI" in key:
                display_value = value[:20] + "..." if len(value) > 20 else value
            else:
                display_value = value
            
            # 检查是否有换行符或等号（错误格式）
            if "\n" in value or (key in value):
                print(f"⚠️  {key}: {repr(value)} (包含异常字符！)")
                all_ok = False
            else:
                print(f"✅ {key}: {display_value}")
    
    print("=" * 60)
    
    if not all_ok:
        print("\n❌ 环境变量配置有问题！")
        print("\n正确的Railway配置格式：")
        print("  Variable Name: DATABASE_NAME")
        print("  Variable Value: tikhub_xhs")
        print("\n错误格式（不要这样写）：")
        print("  Variable Value: DATABASE_NAME=tikhub_xhs")
        sys.exit(1)
    else:
        print("\n✅ 所有环境变量配置正确！")
        
        # 尝试连接数据库
        print("\n" + "=" * 60)
        print("🔄 测试数据库连接...")
        print("=" * 60)
        
        try:
            from core.config import settings
            from database.connection import get_database
            
            print(f"📍 数据库名称: {settings.DATABASE_NAME}")
            print(f"🔗 MongoDB URI: {settings.MONGO_URI[:30]}...")
            
            db = get_database()
            collections = db.list_collection_names()
            
            print(f"✅ 连接成功！")
            print(f"📊 集合列表: {collections}")
            print(f"📦 user_profiles 数量: {db.user_profiles.count_documents({})}")
            
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    check_env()
