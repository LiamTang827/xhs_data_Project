#!/usr/bin/env python3
"""
为MongoDB集合创建索引
提高查询性能
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import get_database


def create_indexes():
    """创建所有必要的索引"""
    print("=" * 60)
    print("📊 创建MongoDB索引")
    print("=" * 60)
    
    db = get_database()
    
    indexes_to_create = [
        {
            "collection": "user_profiles",
            "indexes": [
                ("user_id", [("user_id", 1)], {"unique": True}),
                ("platform_user", [("platform", 1), ("user_id", 1)], {"unique": True}),
                ("nickname", [("nickname", 1)], {}),
                ("platform_nickname", [("platform", 1), ("nickname", 1)], {}),
            ]
        },
        {
            "collection": "user_snapshots",
            "indexes": [
                ("user_platform", [("user_id", 1), ("platform", 1)], {}),
                ("snapshot_date", [("snapshot_date", -1)], {}),
            ]
        },
        {
            "collection": "creator_networks",
            "indexes": [
                ("platform_version", [("platform", 1), ("version", -1)], {}),
                ("created_at", [("created_at", -1)], {}),
            ]
        },
        {
            "collection": "task_logs",
            "indexes": [
                ("task_id", [("task_id", 1)], {"unique": True}),
                ("status", [("status", 1)], {}),
                ("created_at", [("created_at", -1)], {}),
            ]
        },
        {
            "collection": "style_prompts",
            "indexes": [
                ("prompt_type", [("prompt_type", 1)], {}),
                ("platform_type", [("platform", 1), ("prompt_type", 1)], {}),
                ("template_id", [("template_id", 1)], {}),
            ]
        },
        {
            "collection": "user_embeddings",
            "indexes": [
                ("user_id", [("user_id", 1)], {"unique": True}),
                ("updated_at", [("updated_at", -1)], {}),
            ]
        },
        {
            "collection": "note_embeddings",
            "indexes": [
                ("note_id", [("note_id", 1)], {"unique": True}),
                ("user_id", [("user_id", 1)], {}),
                ("engagement_score", [("engagement_score", -1)], {}),
                ("note_create_time", [("note_create_time", -1)], {}),
            ]
        },
    ]
    
    total_created = 0
    total_existed = 0
    
    for collection_config in indexes_to_create:
        collection_name = collection_config["collection"]
        collection = db[collection_name]
        
        print(f"\n📋 {collection_name}:")
        
        for index_name, keys, options in collection_config["indexes"]:
            try:
                # 尝试创建索引
                result = collection.create_index(keys, name=index_name, **options)
                print(f"  ✅ 创建索引: {index_name}")
                total_created += 1
            except Exception as e:
                if "already exists" in str(e) or "duplicate" in str(e).lower():
                    print(f"  ℹ️  索引已存在: {index_name}")
                    total_existed += 1
                else:
                    print(f"  ❌ 创建失败: {index_name} - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 索引创建完成！")
    print(f"  • 新创建: {total_created} 个")
    print(f"  • 已存在: {total_existed} 个")
    print("=" * 60)
    
    # 显示所有索引
    print("\n" + "=" * 60)
    print("📋 当前所有索引:")
    print("=" * 60)
    
    for collection_config in indexes_to_create:
        collection_name = collection_config["collection"]
        collection = db[collection_name]
        
        print(f"\n{collection_name}:")
        indexes = list(collection.list_indexes())
        for idx in indexes:
            print(f"  • {idx.get('name')}: {dict(idx.get('key'))}")


if __name__ == "__main__":
    try:
        create_indexes()
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
