#!/usr/bin/env python3
"""手动更新图灵星球的profile"""

import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root / 'backend'))

from dotenv import load_dotenv
load_dotenv(project_root / '.env')

import requests
import os
from datetime import datetime
from database import UserProfileRepository

token = os.getenv('TIKHUB_TOKEN')
url = 'https://api.tikhub.io/api/v1/xiaohongshu/web_v2/fetch_user_info_app'
headers = {
    'accept': 'application/json',
    'Authorization': f'Bearer {token}',
}

# 更新图灵星球
user_id = '5e6472940000000001008d4e'
print(f'🔄 更新图灵星球: {user_id}')

response = requests.get(url, params={'user_id': user_id}, headers=headers)
result = response.json()

if result.get('code') == 200:
    data = result['data']
    
    user_info = {
        'basic_info': {
            'nickname': data.get('nickname', ''),
            'red_id': data.get('red_id', ''),
            'desc': data.get('desc', ''),
            'avatar': data.get('images', ''),
            'gender': data.get('gender', 0),
            'ip_location': data.get('ip_location', '')
        },
        'stats': {
            'fans': data.get('fans', 0),
            'follows': data.get('follows', 0),
            'total_liked': data.get('liked', 0),
            'total_collected': data.get('collected', 0),
            'note_count': data.get('collected_notes_num', 0)
        },
        'tags': [tag.get('name') if isinstance(tag, dict) else str(tag) 
                for tag in data.get('tags', [])]
    }
    
    profile_repo = UserProfileRepository()
    
    # 检查是否已存在
    existing = profile_repo.get_by_user_id(user_id)
    
    if existing:
        # 更新，保留profile_data
        profile_repo.collection.update_one(
            {'user_id': user_id, 'platform': 'xiaohongshu'},
            {
                '$set': {
                    'basic_info': user_info['basic_info'],
                    'stats': user_info['stats'],
                    'tags': user_info['tags'],
                    'synced_from_api_at': datetime.now(),
                    'updated_at': datetime.now()
                }
            }
        )
        print(f'✅ 已更新existing profile')
    else:
        # 创建新的
        profile_repo.collection.update_one(
            {'user_id': user_id, 'platform': 'xiaohongshu'},
            {
                '$set': {
                    'platform': 'xiaohongshu',
                    'user_id': user_id,
                    'basic_info': user_info['basic_info'],
                    'stats': user_info['stats'],
                    'tags': user_info['tags'],
                    'synced_from_api_at': datetime.now(),
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }
            },
            upsert=True
        )
        print(f'✅ 已创建新profile')
    
    print(f'✅ {user_info["basic_info"]["nickname"]}')
    print(f'✅ 粉丝数: {user_info["stats"]["fans"]:,}')
    print(f'✅ IP位置: {user_info["basic_info"]["ip_location"]}')
    
else:
    print(f'❌ API错误: {result.get("message", "未知错误")}')
