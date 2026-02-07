#!/usr/bin/env python3
"""
批量获取用户详细信息并更新user_profiles
使用TikHub fetch_user_info_app API
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import time
import random

project_root = Path(__file__).resolve().parent.parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
load_dotenv(project_root / '.env')

import requests
from database import UserSnapshotRepository, UserProfileRepository

TIKHUB_API_URL = 'https://api.tikhub.io/api/v1/xiaohongshu/web_v2/fetch_user_info_app'
TIKHUB_TOKEN = os.getenv('TIKHUB_TOKEN')

headers = {
    'accept': 'application/json',
    'Authorization': f'Bearer {TIKHUB_TOKEN}',
}


def fetch_user_info(user_id: str) -> dict:
    """
    调用TikHub API获取用户详细信息
    
    Returns:
        包含basic_info, stats, tags的字典
    """
    params = {'user_id': user_id}
    
    try:
        response = requests.get(TIKHUB_API_URL, params=params, headers=headers)
        response_data = response.json()
        
        if response.status_code != 200 or response_data.get('code') != 200:
            print(f"  ❌ API错误: {response_data.get('message', '未知错误')}")
            return None
        
        data = response_data.get('data', {})
        
        # 提取需要的数据
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
        
        return user_info
        
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
        return None


def update_all_profiles():
    """批量更新所有用户的profile信息"""
    
    print("="*60)
    print("🔄 批量更新用户详细信息")
    print("="*60)
    
    snapshot_repo = UserSnapshotRepository()
    profile_repo = UserProfileRepository()
    
    # 获取所有user_id
    snapshots = list(snapshot_repo.collection.find({'platform': 'xiaohongshu'}))
    print(f"\n📥 找到 {len(snapshots)} 个用户")
    
    success_count = 0
    fail_count = 0
    
    for i, snapshot in enumerate(snapshots, 1):
        user_id = snapshot['user_id']
        
        print(f"\n[{i}/{len(snapshots)}] 处理: {user_id[:16]}...")
        
        # 获取用户信息
        user_info = fetch_user_info(user_id)
        
        if not user_info:
            fail_count += 1
            continue
        
        nickname = user_info['basic_info']['nickname']
        fans = user_info['stats']['fans']
        
        print(f"  ✅ {nickname}")
        print(f"  ✅ 粉丝数: {fans:,}")
        
        # 更新或创建profile
        existing_profile = profile_repo.get_by_user_id(user_id)
        
        if existing_profile:
            # 更新现有profile，并保存历史stats用于计算增长
            old_stats = existing_profile.get('stats', {})
            
            # 添加到历史记录（保留最近30条）
            stats_history = existing_profile.get('stats_history', [])
            if old_stats:
                stats_history.append({
                    'timestamp': datetime.now(),
                    'fans': old_stats.get('fans', 0),
                    'follows': old_stats.get('follows', 0),
                    'total_liked': old_stats.get('total_liked', 0),
                    'total_collected': old_stats.get('total_collected', 0),
                    'note_count': old_stats.get('note_count', 0)
                })
            
            # 只保留最近30条历史记录
            if len(stats_history) > 30:
                stats_history = stats_history[-30:]
            
            profile_repo.collection.update_one(
                {'user_id': user_id, 'platform': 'xiaohongshu'},
                {
                    '$set': {
                        'basic_info': user_info['basic_info'],
                        'stats': user_info['stats'],
                        'stats_history': stats_history,
                        'tags': user_info['tags'],
                        'synced_from_api_at': datetime.now(),
                        'updated_at': datetime.now()
                    }
                }
            )
            print(f"  ✅ 已更新profile（历史记录: {len(stats_history)}条）")
        else:
            # 创建新profile
            profile_repo.collection.insert_one({
                'platform': 'xiaohongshu',
                'user_id': user_id,
                'basic_info': user_info['basic_info'],
                'stats': user_info['stats'],
                'tags': user_info['tags'],
                'profile_data': {},  # 等待AI分析
                'synced_from_api_at': datetime.now(),
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
            print(f"  ✅ 已创建profile")
        
        success_count += 1
        
        # 避免API限流
        if i < len(snapshots):
            delay = random.uniform(1.5, 3)
            time.sleep(delay)
    
    print(f"\n{'='*60}")
    print(f"✅ 完成！成功: {success_count}, 失败: {fail_count}")
    print(f"{'='*60}")
    
    # 显示更新后的统计
    print(f"\n📊 更新后的用户列表:")
    profiles = list(profile_repo.collection.find({'platform': 'xiaohongshu'}))
    for p in sorted(profiles, key=lambda x: x.get('stats', {}).get('fans', 0), reverse=True):
        basic = p.get('basic_info', {})
        stats = p.get('stats', {})
        print(f"  • {basic.get('nickname', 'Unknown')[:30]:30} - 粉丝: {stats.get('fans', 0):,}")


if __name__ == "__main__":
    update_all_profiles()
