#!/usr/bin/env python3
"""
小红书数据采集器 - 使用TikHub API获取用户笔记并存入MongoDB
使用方法：修改 USER_ID 参数，然后运行此脚本
"""

import sys
from pathlib import Path

# 添加 backend 到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

import requests
import time
import random
import os
from dotenv import load_dotenv

# 加载项目根目录的 .env 文件
env_file = project_root / '.env'
if env_file.exists():
    load_dotenv(env_file)
else:
    # 尝试从当前目录加载
    load_dotenv(Path(__file__).parent / '.env')

from database import UserSnapshotRepository, UserProfileRepository
from datetime import datetime

# ============================================
# 配置区域 - 修改这里的参数
# ============================================

USER_ID = '5e6472940000000001008d4e'  # 修改为目标用户ID
TIKHUB_NOTES_API = 'https://api.tikhub.io/api/v1/xiaohongshu/web/get_user_notes_v2'
TIKHUB_USER_INFO_API = 'https://api.tikhub.io/api/v1/xiaohongshu/web_v2/fetch_user_info_app'

# TikHub API Token（从环境变量读取）
TIKHUB_TOKEN = os.getenv('TIKHUB_TOKEN')
if not TIKHUB_TOKEN:
    raise ValueError("TIKHUB_TOKEN environment variable is required. Please copy .env.example to .env and set your token.")

# API请求头
headers = {
    'accept': 'application/json',
    'Authorization': TIKHUB_TOKEN,
}
# ============================================

# ============================================
# 主函数 - 数据采集
# ============================================

def fetch_user_notes(user_id: str) -> dict:
    """
    获取用户的所有笔记
    
    Args:
        user_id: 用户ID
        
    Returns:
        包含user和notes的字典
    """
    all_notes = []
    seen_note_ids = set()
    last_cursor = None
    batch_num = 0
    user_info = None

    print(f"📥 开始获取用户 {user_id} 的笔记...")
    print("=" * 60)

    while True:
        batch_num += 1
        params = {'user_id': user_id}
        if last_cursor:
            params['lastCursor'] = last_cursor
        
        try:
            print(f"  第 {batch_num} 批...", end="")
            
            response = requests.get(
                TIKHUB_NOTES_API, 
                params=params, 
                headers=headers,
                timeout=30  # 添加30秒超时
            )
            response_data = response.json()
            
            # 检查响应
            if response_data.get('code') != 200:
                error_msg = response_data.get('message_zh', response_data.get('message', '未知错误'))
                print(f"\n❌ API错误: {error_msg}")
                # 返回错误信息
                return {
                    'error': error_msg,
                    'success': False,
                    'user': None,
                    'notes': []
                }
                break
            
            data = response_data.get('data', {}).get('data', {})
            current_notes = data.get('notes', [])
            
            if not current_notes:
                print(f"\n✅ 完成！共 {batch_num-1} 批")
                break
            
            # 提取user信息
            if not user_info and current_notes and 'user' in current_notes[0]:
                user_info = current_notes[0]['user']
            
            # 去重添加笔记
            new_count = 0
            for note in current_notes:
                note_id = note.get('id', '')
                if note_id and note_id not in seen_note_ids:
                    all_notes.append(note)
                    seen_note_ids.add(note_id)
                    new_count += 1
            
            print(f" 新增 {new_count} 条")
            
            # 检查是否继续
            if len(current_notes) < 19 or new_count == 0:
                break
            
            # 获取下一页cursor
            last_note = current_notes[-1]
            last_cursor = last_note.get('cursor') or last_note.get('id')
            if not last_cursor:
                break
            
            # 延迟避免限流
            time.sleep(random.uniform(1.5, 3))
            
        except requests.exceptions.Timeout:
            print(f"\n❌ 请求超时")
            return {
                'error': '请求超时，请稍后重试',
                'success': False,
                'user': None,
                'notes': []
            }
        except Exception as e:
            print(f"\n❌ 请求失败: {e}")
            return {
                'error': f'请求失败: {str(e)}',
                'success': False,
                'user': None,
                'notes': []
            }
    
    print(f"\n✅ 总计获取 {len(all_notes)} 条笔记")
    
    return {
        'success': True,
        'user': user_info,
        'notes': all_notes
    }


def fetch_user_info(user_id: str) -> dict:
    """
    获取用户详细信息
    
    Args:
        user_id: 用户ID
        
    Returns:
        包含basic_info, stats, tags的用户信息字典
    """
    print("\n📊 获取用户详细信息...")
    
    params = {'user_id': user_id}
    
    try:
        response = requests.get(
            TIKHUB_USER_INFO_API, 
            params=params, 
            headers=headers,
            timeout=30  # 添加30秒超时
        )
        response_data = response.json()
        
        if response.status_code != 200 or response_data.get('code') != 200:
            print(f"⚠️  用户信息API错误: {response_data.get('message', '未知错误')}")
            return None
        
        data = response_data.get('data', {})
        
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
        
        nickname = user_info['basic_info']['nickname']
        fans = user_info['stats']['fans']
        print(f"✅ {nickname} - 粉丝数: {fans:,}")
        
        return user_info
        
    except requests.exceptions.Timeout:
        print(f"⚠️  获取用户信息超时（30秒）")
        return None
    except Exception as e:
        print(f"⚠️  获取用户信息失败: {e}")
        return None


def save_to_mongodb(user_id: str, data: dict):
    """
    保存数据到MongoDB（包括snapshots和profiles）
    
    Args:
        user_id: 用户ID
        data: 包含notes和user_info的数据
    """
    try:
        snapshot_repo = UserSnapshotRepository()
        profile_repo = UserProfileRepository()
        
        # 1. 保存笔记快照到 user_snapshots
        print("\n💾 保存笔记数据到 user_snapshots...")
        existing_snapshot = snapshot_repo.get_by_user_id(user_id)
        
        snapshot_data = {
            'platform': 'xiaohongshu',
            'user_id': user_id,
            'notes': data['notes'],
            'total_notes': len(data['notes']),
            'created_at': datetime.now()
        }
        
        if existing_snapshot:
            snapshot_repo.update_snapshot(user_id, 'xiaohongshu', data['notes'])
            print(f"✅ 已更新笔记快照: {len(data['notes'])} 条笔记")
        else:
            snapshot_repo.create_snapshot(snapshot_data)
            print(f"✅ 已保存笔记快照: {len(data['notes'])} 条笔记")
        
        # 2. 保存用户详细信息到 user_profiles
        if data.get('user_info'):
            print("💾 保存用户信息到 user_profiles...")
            user_info = data['user_info']
            existing_profile = profile_repo.get_by_user_id(user_id)
            
            if existing_profile:
                # 更新，保留已有的profile_data（AI分析结果）
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
                print(f"✅ 已更新用户profile: {user_info['basic_info']['nickname']}")
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
                print(f"✅ 已创建用户profile: {user_info['basic_info']['nickname']}")
                print(f"   粉丝数: {user_info['stats']['fans']:,}")
        else:
            print("⚠️  未获取到用户详细信息，仅保存笔记数据")
            
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🎯 小红书数据采集工具 (整合版)")
    print("="*60)
    print(f"目标用户: {USER_ID}\n")
    
    # 1. 获取笔记数据
    notes_data = fetch_user_notes(USER_ID)
    
    if not notes_data['notes']:
        print("\n❌ 未能获取笔记数据")
        return
    
    # 2. 获取用户详细信息
    user_info = fetch_user_info(USER_ID)
    
    # 3. 保存到MongoDB
    full_data = {
        'notes': notes_data['notes'],
        'user_info': user_info
    }
    
    save_to_mongodb(USER_ID, full_data)
    
    print("\n" + "="*60)
    print("✨ 数据采集完成！")
    print("="*60)
    print(f"\n📊 数据统计:")
    print(f"  - 笔记数: {len(notes_data['notes'])}")
    if user_info:
        print(f"  - 用户: {user_info['basic_info']['nickname']}")
        print(f"  - 粉丝数: {user_info['stats']['fans']:,}")
    print(f"\n💡 下一步运行: cd backend && python scripts/process_all_snapshots.py")
    print(f"   （使用DeepSeek AI分析内容，生成profile_data）")


if __name__ == "__main__":
    main()

