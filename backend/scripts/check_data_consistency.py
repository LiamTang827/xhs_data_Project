#!/usr/bin/env python3
"""检查数据不一致问题"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
load_dotenv(project_root / '.env')

from database import UserProfileRepository, UserSnapshotRepository

def check_data_consistency():
    profile_repo = UserProfileRepository()
    snapshot_repo = UserSnapshotRepository()
    
    print('='*60)
    print('user_profiles 中的用户')
    print('='*60)
    profiles = profile_repo.get_all_profiles()
    profile_ids = {p['user_id']: p['nickname'] for p in profiles}
    for uid, name in profile_ids.items():
        print(f'  {name}: {uid}')
    
    print('\n' + '='*60)
    print('user_snapshots 中的用户')
    print('='*60)
    snapshots = list(snapshot_repo.collection.find())
    for snap in snapshots:
        uid = snap['user_id']
        # 从第一条笔记提取nickname
        nickname = 'Unknown'
        if 'notes' in snap and snap['notes']:
            user_info = snap['notes'][0].get('user', {})
            nickname = user_info.get('nickname', 'Unknown')
        print(f'  {nickname}: {uid}')
        print(f'    笔记数: {snap.get("total_notes", 0)}')
    
    snapshot_ids = {s['user_id'] for s in snapshots}
    
    print('\n' + '='*60)
    print('只在 profiles 中存在（没有笔记数据的用户）')
    print('='*60)
    only_in_profiles = set(profile_ids.keys()) - snapshot_ids
    for uid in only_in_profiles:
        print(f'  ❌ {profile_ids[uid]}: {uid}')
    
    print('\n' + '='*60)
    print('只在 snapshots 中存在（没有画像的用户）')
    print('='*60)
    only_in_snapshots = snapshot_ids - set(profile_ids.keys())
    for uid in only_in_snapshots:
        # 查找nickname
        snap = next((s for s in snapshots if s['user_id'] == uid), None)
        nickname = 'Unknown'
        if snap and 'notes' in snap and snap['notes']:
            user_info = snap['notes'][0].get('user', {})
            nickname = user_info.get('nickname', 'Unknown')
        print(f'  ❌ {nickname}: {uid}')
    
    print('\n' + '='*60)
    print('数据一致性总结')
    print('='*60)
    print(f'user_profiles 总数: {len(profile_ids)}')
    print(f'user_snapshots 总数: {len(snapshots)}')
    print(f'匹配的用户: {len(set(profile_ids.keys()) & snapshot_ids)}')
    print(f'不匹配的用户: {len(only_in_profiles) + len(only_in_snapshots)}')

if __name__ == '__main__':
    check_data_consistency()
