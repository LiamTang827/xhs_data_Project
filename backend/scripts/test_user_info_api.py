#!/usr/bin/env python3
"""
测试TikHub fetch_user_info API - 获取用户详细信息
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

import requests
import os
import json
from dotenv import load_dotenv

load_dotenv(project_root / '.env')

from database import UserSnapshotRepository

# 获取数据库中的一个user_id
repo = UserSnapshotRepository()
snapshot = repo.collection.find_one({'platform': 'xiaohongshu'})
TEST_USER_ID = snapshot['user_id'] if snapshot else '5ff98b9d0000000001008f40'

TIKHUB_API_URL = 'https://api.tikhub.io/api/v1/xiaohongshu/web_v2/fetch_user_info_app'
TIKHUB_TOKEN = os.getenv('TIKHUB_TOKEN')

headers = {
    'accept': 'application/json',
    'Authorization': f'Bearer {TIKHUB_TOKEN}',
}

print("="*60)
print(f"🧪 测试TikHub fetch_user_info API")
print(f"📌 用户ID: {TEST_USER_ID}")
print("="*60)

params = {'user_id': TEST_USER_ID}

try:
    print("\n📡 发送API请求...")
    response = requests.get(TIKHUB_API_URL, params=params, headers=headers)
    
    print(f"✅ 响应状态码: {response.status_code}")
    print(f"✅ 响应内容: {response.text[:500]}")
    
    response_data = response.json()
    print(f"✅ API返回code: {response_data.get('code')}")
    
    if response.status_code != 200 or response_data.get('code') != 200:
        print(f"❌ API错误: {response_data.get('message') or response_data.get('message_zh', '未知错误')}")
        print(f"完整响应: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
        sys.exit(1)
    
    data = response_data.get('data', {})
    
    print("\n" + "="*60)
    print("📊 返回的数据结构:")
    print("="*60)
    
    # 显示所有顶层字段
    print(f"\n顶层字段: {list(data.keys())[:30]}...")  # 只显示前30个
    
    # 显示用户基本信息（数据直接在顶层）
    print(f"\n👤 用户基本信息:")
    print(f"  userid: {data.get('userid')}")
    print(f"  nickname: {data.get('nickname')}")
    print(f"  red_id: {data.get('red_id')}")
    print(f"  gender: {data.get('gender')}")
    print(f"  ip_location: {data.get('ip_location')}")
    print(f"  location: {data.get('location')}")
    print(f"  desc: {data.get('desc', '')[:100]}...")
    print(f"  images (头像): {data.get('images', '')[:80]}...")
    
    # 显示互动数据
    print(f"\n📊 互动数据:")
    print(f"  fans (粉丝): {data.get('fans')}")
    print(f"  follows (关注): {data.get('follows')}")
    print(f"  interactions: {data.get('interactions')}")
    print(f"  liked: {data.get('liked')}")
    print(f"  collected: {data.get('collected')}")
    
    # 显示笔记统计
    print(f"\n📝 内容统计:")
    print(f"  collected_notes_num: {data.get('collected_notes_num')}")
    print(f"  atme_notes_num: {data.get('atme_notes_num')}")
    
    # 显示标签信息
    tags = data.get('tags', [])
    print(f"\n🏷️  tags字段:")
    print(f"  类型: {type(tags)}")
    if isinstance(tags, list):
        print(f"  数量: {len(tags)}")
        for tag in tags[:5]:
            if isinstance(tag, dict):
                print(f"    - {tag.get('name')} (type: {tag.get('type')})")
            else:
                print(f"    - {tag}")
    elif isinstance(tags, dict):
        print(f"  字段: {list(tags.keys())}")
    
    # 显示认证信息
    print(f"\n✅ 认证信息:")
    print(f"  red_official_verified: {data.get('red_official_verified')}")
    print(f"  red_official_verify_type: {data.get('red_official_verify_type')}")
    print(f"  red_official_verify_content: {data.get('red_official_verify_content', '')[:100]}...")
    
    # 保存完整数据
    output_file = project_root / 'test_user_info_response.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(response_data, f, ensure_ascii=False, indent=2)
    print(f"\n💾 完整数据已保存到: {output_file}")
    
    # 关键分析：能否和现有数据关联
    print("\n" + "="*60)
    print("🔗 数据关联分析:")
    print("="*60)
    
    user_id_in_response = data.get('userid')
    print(f"\n✅ 关键字段匹配:")
    print(f"  请求的user_id: {TEST_USER_ID}")
    print(f"  返回的userid: {user_id_in_response}")
    print(f"  是否匹配: {'✅ 是' if user_id_in_response == TEST_USER_ID else '❌ 否'}")
    
    print(f"\n📋 可用于存储的关键数据:")
    print(f"  主键:")
    print(f"    - user_id: {TEST_USER_ID} (用于关联)")
    print(f"  用户信息:")
    print(f"    - nickname: {data.get('nickname')}")
    print(f"    - red_id: {data.get('red_id')}")
    print(f"    - gender: {data.get('gender')}")
    print(f"    - ip_location: {data.get('ip_location')}")
    print(f"    - desc: 简介文本")
    print(f"    - images: 头像URL")
    print(f"  互动数据 (✅ 有粉丝数！):")
    print(f"    - fans: {data.get('fans')} (粉丝数)")
    print(f"    - follows: {data.get('follows')} (关注数)")
    print(f"    - interactions: {data.get('interactions')}")
    print(f"    - liked: {data.get('liked')} (获赞数)")
    print(f"    - collected: {data.get('collected')} (收藏数)")
    print(f"  标签:")
    print(f"    - tags: {len(data.get('tags', []))} 个标签")
    
    print(f"\n💡 数据库设计建议:")
    print(f"  1. user_snapshots: 保持当前结构 (存储notes)")
    print(f"  2. user_profiles: 补充从此API获取的信息")
    print(f"     - user_id (主键，关联snapshots)")
    print(f"     - nickname, red_id, desc, images")
    print(f"     - fans, follows, interactions (互动数据)")
    print(f"     - ip_location, gender, tags")
    print(f"     - profile_data (AI分析的内容)")
    print(f"  3. creator_networks: 使用user_id作为节点ID")
    print(f"     - 从user_profiles获取fans等数据")
    
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ 请求失败: {e}")
    import traceback
    traceback.print_exc()
