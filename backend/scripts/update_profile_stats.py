#!/usr/bin/env python3
"""
计算并更新用户的互动统计数据到profile中
这样刷新网络时就可以直接使用，不需要每次都从snapshots读取
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加backend到路径
project_root = Path(__file__).resolve().parent.parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
load_dotenv(project_root / '.env')

from database.connection import get_database


def calculate_note_stats(notes: list, days: int = 30) -> dict:
    """
    计算最近N天的笔记互动数据
    """
    if not notes:
        return {
            'total_engagement': 0,
            'total_likes': 0,
            'total_collects': 0,
            'total_comments': 0,
            'total_shares': 0,
            'note_count': 0,
            'index_series': []
        }
    
    cutoff_time = datetime.now() - timedelta(days=days)
    cutoff_timestamp = int(cutoff_time.timestamp())
    recent_notes = [n for n in notes if n.get('create_time', 0) >= cutoff_timestamp]
    
    if not recent_notes:
        return {
            'total_engagement': 0,
            'total_likes': 0,
            'total_collects': 0,
            'total_comments': 0,
            'total_shares': 0,
            'note_count': 0,
            'index_series': []
        }
    
    # 统计总互动数
    total_likes = sum(n.get('likes', 0) for n in recent_notes)
    total_collects = sum(n.get('collected_count', 0) for n in recent_notes)
    total_comments = sum(n.get('comments_count', 0) for n in recent_notes)
    total_shares = sum(n.get('share_count', 0) for n in recent_notes)
    total_engagement = total_likes + total_collects + total_comments + total_shares
    
    # 生成index时间序列
    sorted_notes = sorted(recent_notes, key=lambda x: x.get('create_time', 0))
    index_series = []
    
    for note in sorted_notes:
        create_time = note.get('create_time', 0)
        if create_time > 0:
            note_engagement = (
                note.get('likes', 0) + 
                note.get('collected_count', 0) + 
                note.get('comments_count', 0) + 
                note.get('share_count', 0)
            )
            # 转换为互动指数
            index_value = note_engagement / 1000.0
            index_series.append({
                'ts': create_time * 1000,  # 毫秒时间戳
                'value': round(index_value, 2),
                'note_id': note.get('note_id', ''),
                'title': note.get('title', '')[:30]  # 保存标题用于成长路径功能
            })
    
    return {
        'total_engagement': total_engagement,
        'total_likes': total_likes,
        'total_collects': total_collects,
        'total_comments': total_comments,
        'total_shares': total_shares,
        'note_count': len(recent_notes),
        'index_series': index_series
    }


def update_profile_stats():
    """
    更新所有用户profile中的互动统计数据
    逐个用户处理，避免一次性读取所有snapshots
    """
    print("\n" + "=" * 60)
    print("📊 计算并更新用户互动统计数据")
    print("=" * 60)
    
    db = get_database()
    
    # 获取所有用户profile
    print("\n📥 读取用户profile...")
    profiles = list(db.user_profiles.find({'platform': 'xiaohongshu'}))
    print(f"✅ 找到 {len(profiles)} 个用户")
    
    # 逐个处理用户（避免一次性读取所有snapshots）
    print("\n🔄 逐个计算并更新stats...")
    updated = 0
    skipped = 0
    
    for i, profile in enumerate(profiles, 1):
        user_id = profile['user_id']
        nickname = profile.get('basic_info', {}).get('nickname', user_id[:16])
        
        # 单独读取该用户的snapshot（只投影notes字段，提高性能）
        snapshot = db.user_snapshots.find_one(
            {
                'user_id': user_id,
                'platform': 'xiaohongshu'
            },
            {
                'notes': 1  # 只读取notes字段
            }
        )
        
        if not snapshot:
            print(f"[{i}/{len(profiles)}] ⚠️  {nickname}: 无snapshot数据，跳过")
            skipped += 1
            continue
        
        notes = snapshot.get('notes', [])
        if not notes:
            print(f"[{i}/{len(profiles)}] ⚠️  {nickname}: 无笔记数据，跳过")
            skipped += 1
            continue
        
        # 计算统计数据
        note_stats = calculate_note_stats(notes, days=30)
        
        # 更新profile.stats
        update_result = db.user_profiles.update_one(
            {'user_id': user_id, 'platform': 'xiaohongshu'},
            {'$set': {
                'stats.total_engagement': note_stats['total_engagement'],
                'stats.total_likes': note_stats['total_likes'],
                'stats.total_collects': note_stats['total_collects'],
                'stats.total_comments': note_stats['total_comments'],
                'stats.total_shares': note_stats['total_shares'],
                'stats.note_count': note_stats['note_count'],
                'stats.index_series': note_stats['index_series'],
                'stats.stats_updated_at': datetime.now()
            }}
        )
        
        if update_result.modified_count > 0:
            print(f"[{i}/{len(profiles)}] ✅ {nickname}: 互动={note_stats['total_engagement']:,}, 笔记={note_stats['note_count']}")
            updated += 1
        else:
            print(f"[{i}/{len(profiles)}] ⚠️  {nickname}: 更新失败")
    
    print("\n" + "=" * 60)
    print(f"✨ 完成!")
    print(f"✅ 更新成功: {updated} 个用户")
    print(f"⚠️  跳过: {skipped} 个用户（无笔记数据）")
    print("=" * 60)


if __name__ == "__main__":
    update_profile_stats()
