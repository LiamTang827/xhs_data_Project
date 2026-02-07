#!/usr/bin/env python3
"""
检查数据库中的数据日期分布
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from database.connection import get_database

def check_data_dates():
    """检查各个collection的数据日期"""
    db = get_database()
    
    print("="*60)
    print("📊 数据库数据日期分布")
    print("="*60)
    
    # 1. user_snapshots
    print("\n1. user_snapshots (笔记快照):")
    snapshots = list(db.user_snapshots.find({'platform': 'xiaohongshu'}))
    print(f"   总数: {len(snapshots)} 个用户")
    
    for snapshot in snapshots:
        user_id = snapshot.get('user_id', 'unknown')
        created_at = snapshot.get('created_at')
        notes = snapshot.get('notes', [])
        
        if notes:
            # 获取笔记的时间范围
            note_times = [n.get('create_time', 0) for n in notes if n.get('create_time')]
            if note_times:
                earliest = datetime.fromtimestamp(min(note_times))
                latest = datetime.fromtimestamp(max(note_times))
                print(f"   - {user_id[:12]}...: {len(notes)} 条笔记")
                print(f"     最早笔记: {earliest.strftime('%Y-%m-%d %H:%M')}")
                print(f"     最新笔记: {latest.strftime('%Y-%m-%d %H:%M')}")
                print(f"     快照创建: {created_at.strftime('%Y-%m-%d %H:%M') if created_at else 'unknown'}")
    
    # 2. user_profiles
    print("\n2. user_profiles (用户档案):")
    profiles = list(db.user_profiles.find({'platform': 'xiaohongshu'}))
    print(f"   总数: {len(profiles)} 个用户")
    
    for profile in profiles:
        nickname = profile.get('basic_info', {}).get('nickname', 'Unknown')
        synced_at = profile.get('synced_from_api_at')
        print(f"   - {nickname}: 最后同步 {synced_at.strftime('%Y-%m-%d %H:%M') if synced_at else 'unknown'}")
    
    # 3. creator_networks
    print("\n3. creator_networks (创作者网络):")
    networks = list(db.creator_networks.find({'platform': 'xiaohongshu'}))
    
    if networks:
        network = networks[0]
        created_at = network.get('created_at')
        creators = network.get('network_data', {}).get('creators', [])
        
        print(f"   网络生成时间: {created_at.strftime('%Y-%m-%d %H:%M') if created_at else 'unknown'}")
        print(f"   创作者数量: {len(creators)}")

if __name__ == "__main__":
    check_data_dates()
