#!/usr/bin/env python3
"""
测试TikHub API - 爬取一个用户的数据并查看结构
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

# 测试用户ID（从数据库中选一个）
TEST_USER_ID = '5ff98b9d0000000001008f40'  # 星球研究所

TIKHUB_API_URL = 'https://api.tikhub.io/api/v1/xiaohongshu/web/get_user_notes_v2'
TIKHUB_TOKEN = os.getenv('TIKHUB_TOKEN')

headers = {
    'accept': 'application/json',
    'Authorization': TIKHUB_TOKEN,
}

print("="*60)
print(f"🧪 测试TikHub API - 用户ID: {TEST_USER_ID}")
print("="*60)

# 只获取第一批数据（约20条）
params = {'user_id': TEST_USER_ID}

try:
    print("\n📡 发送API请求...")
    response = requests.get(TIKHUB_API_URL, params=params, headers=headers)
    response_data = response.json()
    
    print(f"✅ 响应状态码: {response.status_code}")
    print(f"✅ API返回code: {response_data.get('code')}")
    
    if response_data.get('code') != 200:
        print(f"❌ API错误: {response_data.get('message_zh', '未知错误')}")
        sys.exit(1)
    
    data = response_data.get('data', {}).get('data', {})
    notes = data.get('notes', [])
    
    print(f"\n📝 获取到 {len(notes)} 条笔记")
    
    if notes:
        print("\n" + "="*60)
        print("第一条笔记的数据结构:")
        print("="*60)
        
        first_note = notes[0]
        
        # 显示user信息
        if 'user' in first_note:
            user = first_note['user']
            print("\n👤 用户信息 (notes[0]['user']):")
            print(f"  nickname: {user.get('nickname')}")
            print(f"  user_id/userid: {user.get('user_id') or user.get('userid')}")
            print(f"  fans: {user.get('fans')}")
            print(f"  avatar: {user.get('images', '')[:50]}...")
            print(f"  desc: {user.get('desc')}")
            print(f"  ip_location: {user.get('ip_location')}")
            print(f"  所有字段: {list(user.keys())}")
        
        # 显示笔记信息
        print(f"\n📄 笔记信息:")
        print(f"  note_id: {first_note.get('note_id') or first_note.get('id')}")
        print(f"  title: {first_note.get('title')}")
        print(f"  desc: {first_note.get('desc', '')[:100]}...")
        print(f"  liked_count: {first_note.get('liked_count')}")
        print(f"  collected_count: {first_note.get('collected_count')}")
        print(f"  comment_count: {first_note.get('comment_count')}")
        print(f"  share_count: {first_note.get('share_count')}")
        
        # 重点：tag_list（话题标签）
        if 'tag_list' in first_note:
            tag_list = first_note['tag_list']
            print(f"\n🏷️  话题标签 (tag_list):")
            print(f"  类型: {type(tag_list)}")
            if isinstance(tag_list, list):
                print(f"  数量: {len(tag_list)}")
                for tag in tag_list[:5]:  # 显示前5个
                    if isinstance(tag, dict):
                        print(f"    - {tag.get('name')} (type: {tag.get('type')})")
                    else:
                        print(f"    - {tag}")
            else:
                print(f"  内容: {tag_list}")
        
        print(f"\n  笔记所有字段: {list(first_note.keys())}")
        
        # 保存完整数据到文件供查看
        output_file = project_root / 'test_tikhub_response.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'user': first_note.get('user'),
                'first_note': first_note,
                'all_notes_sample': notes[:3]  # 保存前3条
            }, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n💾 完整数据已保存到: {output_file}")
        
        # 统计所有笔记的tag
        print("\n" + "="*60)
        print("所有笔记的话题标签统计:")
        print("="*60)
        
        all_tags = {}
        for note in notes:
            tag_list = note.get('tag_list', [])
            if isinstance(tag_list, list):
                for tag in tag_list:
                    if isinstance(tag, dict):
                        tag_name = tag.get('name', '')
                    elif isinstance(tag, str):
                        tag_name = tag
                    else:
                        continue
                    
                    if tag_name:
                        all_tags[tag_name] = all_tags.get(tag_name, 0) + 1
        
        # 按频率排序
        sorted_tags = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)
        print(f"\n发现 {len(sorted_tags)} 个不同的标签")
        print("\n前10个高频标签:")
        for tag, count in sorted_tags[:10]:
            print(f"  {count:2d}次 - {tag}")
    
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ 请求失败: {e}")
    import traceback
    traceback.print_exc()
