#!/usr/bin/env python3
"""
分析数据库现状 - 看看我们有哪些数据可以用
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
load_dotenv(project_root / '.env')

from database import UserProfileRepository, UserSnapshotRepository
import json

def analyze_database():
    profile_repo = UserProfileRepository()
    snapshot_repo = UserSnapshotRepository()
    
    print("="*60)
    print("📊 数据库现状分析")
    print("="*60)
    
    # 分析snapshots
    snapshots = list(snapshot_repo.collection.find())
    
    print(f"\n🗂️  user_snapshots: {len(snapshots)} 个用户")
    print("-"*60)
    
    for snap in snapshots:
        user_id = snap['user_id']
        notes = snap.get('notes', [])
        
        if not notes:
            print(f"\n❌ {user_id}: 没有笔记")
            continue
        
        # 从第一条笔记提取用户信息
        user_info = notes[0].get('user', {})
        nickname = user_info.get('nickname', 'Unknown')
        fans = user_info.get('fans')
        
        # 计算总互动数
        total_likes = sum(n.get('likes', 0) for n in notes)
        total_collects = sum(n.get('collected_count', 0) for n in notes)
        total_comments = sum(n.get('comments_count', 0) for n in notes)
        total_shares = sum(n.get('share_count', 0) for n in notes)
        
        engagement_index = total_likes + total_collects * 2 + total_comments * 3 + total_shares * 5
        
        print(f"\n✅ {nickname}")
        print(f"   user_id: {user_id}")
        print(f"   粉丝数: {fans if fans else '未知'}")
        print(f"   笔记数: {len(notes)}")
        print(f"   总互动: ❤️{total_likes} 💾{total_collects} 💬{total_comments} 🔗{total_shares}")
        print(f"   互动指数: {engagement_index:,}")
        
        # 提取笔记标题关键词（简单版）
        titles = [n.get('title', '') for n in notes[:5]]
        print(f"   前5个标题:")
        for title in titles:
            print(f"      • {title[:50]}")
    
    print(f"\n{'='*60}")
    print("📋 user_profiles 现状")
    print("="*60)
    
    profiles = profile_repo.get_all_profiles()
    print(f"\n总共: {len(profiles)} 个profile")
    
    for prof in profiles:
        nickname = prof.get('nickname', 'Unknown')
        user_id = prof.get('user_id', 'Unknown')
        profile_data = prof.get('profile_data', {})
        topics = profile_data.get('content_topics', [])
        
        print(f"\n• {nickname} ({user_id})")
        print(f"  topics: {topics}")

if __name__ == '__main__':
    analyze_database()
