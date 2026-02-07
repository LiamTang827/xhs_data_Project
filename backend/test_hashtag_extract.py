#!/usr/bin/env python3
"""
测试从笔记中提取#话题标签
"""

import sys
from pathlib import Path
import re
from collections import Counter

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from database import UserSnapshotRepository

def test_extract_hashtags(user_id: str):
    """测试提取#话题标签"""
    print(f"测试用户: {user_id}")
    
    # 获取snapshot
    snapshot_repo = UserSnapshotRepository()
    snapshot = snapshot_repo.get_by_user_id(user_id, "xiaohongshu")
    
    if not snapshot:
        print("❌ 未找到笔记数据")
        return
    
    notes = snapshot.get('notes', [])
    print(f"✅ 找到 {len(notes)} 条笔记\n")
    
    # 提取#话题标签
    hashtags = []
    for i, note in enumerate(notes[:10]):
        title = note.get('title', '') or ''
        desc = note.get('desc') or ''
        text = title + ' ' + desc
        
        # 提取 #xxx 格式的话题
        tags = re.findall(r'#([\w\u4e00-\u9fa5]+)', text)
        
        if tags:
            print(f"笔记 {i+1}: {title[:30]}")
            print(f"  找到标签: {tags}")
            hashtags.extend(tags)
    
    # 统计词频
    if hashtags:
        print(f"\n📊 标签统计:")
        tag_count = Counter(hashtags)
        for tag, count in tag_count.most_common(10):
            print(f"  #{tag}: {count}次")
        
        result = [tag for tag, count in tag_count.most_common(8)]
        print(f"\n✅ 最终话题: {['#' + tag for tag in result]}")
    else:
        print("\n⚠️  没有找到#话题标签，将使用默认值")


if __name__ == "__main__":
    # 测试几个用户
    test_users = [
        "5e6472940000000001008d4e",  # 图灵星球
        "5ff98b9d0000000001008f40",  # 星球研究所
    ]
    
    for user_id in test_users:
        test_extract_hashtags(user_id)
        print("\n" + "="*60 + "\n")
