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

from database import UserSnapshotRepository
from datetime import datetime

# ============================================
# 配置区域 - 修改这里的参数
# ============================================

USER_ID = '5e6472940000000001008d4e'  # 修改为目标用户ID
TIKHUB_API_URL = 'https://api.tikhub.io/api/v1/xiaohongshu/web/get_user_notes_v2'

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
            
            response = requests.get(TIKHUB_API_URL, params=params, headers=headers)
            response_data = response.json()
            
            # 检查响应
            if response_data.get('code') != 200:
                print(f"\n❌ API错误: {response_data.get('message_zh', '未知错误')}")
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
            
        except Exception as e:
            print(f"\n❌ 请求失败: {e}")
            break
    
    print(f"\n✅ 总计获取 {len(all_notes)} 条笔记")
    
    return {
        'user': user_info,
        'notes': all_notes
    }


def save_to_mongodb(user_id: str, data: dict):
    """
    保存数据到MongoDB
    
    Args:
        user_id: 用户ID
        data: 包含user和notes的数据
    """
    if not data['user']:
        print("❌ 缺少用户信息，无法保存")
        return
    
    try:
        repo = UserSnapshotRepository()
        
        # 检查是否已存在
        existing = repo.get_by_user_id(user_id)
        
        snapshot_data = {
            'platform': 'xiaohongshu',
            'user_id': user_id,
            'notes': data['notes'],
            'total_notes': len(data['notes']),
            'created_at': datetime.now()
        }
        
        if existing:
            repo.update_snapshot(user_id, 'xiaohongshu', data['notes'])
            print(f"✅ 已更新到MongoDB: {data['user'].get('nickname', user_id)}")
        else:
            repo.create_snapshot(snapshot_data)
            print(f"✅ 已保存到MongoDB: {data['user'].get('nickname', user_id)}")
            
    except Exception as e:
        print(f"❌ 保存失败: {e}")


def main():
    """主函数"""
    print("\n🎯 TikHub数据采集工具")
    print(f"目标用户: {USER_ID}\n")
    
    # 获取数据
    data = fetch_user_notes(USER_ID)
    
    # 保存到MongoDB
    if data['user']:
        save_to_mongodb(USER_ID, data)
        print(f"\n💡 下一步运行: cd collectors/xiaohongshu && python3 pipeline.py --user_id {USER_ID}")
    else:
        print("\n❌ 未能获取用户信息")


if __name__ == "__main__":
    main()

