"""
Railway 数据初始化脚本 - 直接在环境中运行
使用方法：python3 init_railway_data.py
"""

import os
import sys
from datetime import datetime

# 确保可以导入 backend 模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from pymongo import MongoClient

# 从环境变量读取配置
MONGO_URI = os.getenv('MONGO_URI')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'tikhub_xhs')

if not MONGO_URI:
    print("❌ 错误：未设置 MONGO_URI 环境变量")
    sys.exit(1)

print("="*60)
print("🚀 Railway 数据初始化")
print("="*60)
print(f"数据库: {DATABASE_NAME}")
print(f"MongoDB URI: {MONGO_URI[:30]}...")

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# 检查现有数据
existing_count = db.user_profiles.count_documents({})
print(f"\n当前数据量: {existing_count}")

if existing_count > 0:
    print("✅ 数据库已有数据，跳过初始化")
    sys.exit(0)

# 创建示例数据
print("\n🌱 创建示例创作者数据...")

sample_creators = [
    {
        "platform": "xiaohongshu",
        "user_id": "5e6472940000000001008d4e",
        "nickname": "硅谷樱花小姐姐🌸",
        "profile_data": {
            "topics": ["科技", "生活", "美食"],
            "content_style": "真诚分享、深度测评",
            "value_points": ["科技产品评测", "美食探店"],
            "engagement": {
                "avg_likes": 1500,
                "avg_comments": 120,
                "engagement_rate": 0.05
            }
        },
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "platform": "xiaohongshu",
        "user_id": "sample_user_002",
        "nickname": "美食探店达人",
        "profile_data": {
            "topics": ["美食", "探店", "生活"],
            "content_style": "轻松活泼、图文并茂",
            "value_points": ["美食推荐", "性价比分析"],
            "engagement": {
                "avg_likes": 2000,
                "avg_comments": 150,
                "engagement_rate": 0.06
            }
        },
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "platform": "xiaohongshu",
        "user_id": "sample_user_003",
        "nickname": "旅行摄影师Lily",
        "profile_data": {
            "topics": ["旅行", "摄影", "攻略"],
            "content_style": "唯美治愈、干货满满",
            "value_points": ["旅行攻略", "摄影技巧"],
            "engagement": {
                "avg_likes": 3000,
                "avg_comments": 200,
                "engagement_rate": 0.08
            }
        },
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
]

result = db.user_profiles.insert_many(sample_creators)
print(f"✅ 成功创建 {len(result.inserted_ids)} 条数据")

# 验证
for creator in sample_creators:
    print(f"  - {creator['nickname']} (ID: {creator['user_id']})")

print("\n" + "="*60)
print("✅ 初始化完成！")
print("="*60)
print("\n测试命令:")
print(f"  curl https://your-backend.railway.app/api/style/creators")
