#!/usr/bin/env python3
"""
测试关键词提取功能
"""

import sys
from pathlib import Path
import re
from collections import Counter

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from database import UserSnapshotRepository

def test_extract_topics(user_id: str):
    """测试提取话题"""
    print(f"测试用户: {user_id}")
    
    # 获取snapshot
    snapshot_repo = UserSnapshotRepository()
    snapshot = snapshot_repo.get_by_user_id(user_id, "xiaohongshu")
    
    if not snapshot:
        print("❌ 未找到笔记数据")
        return
    
    notes = snapshot.get('notes', [])
    print(f"✅ 找到 {len(notes)} 条笔记")
    
    # 提取关键词
    stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
                 '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
                 '自己', '这', '那', '它', '为', '能', '与', '吗', '啊', '呢', '吧', '哦', '哈',
                 '个', '在', '来', '她', '他', '还', '把', '给', '让', '从', '被', '向', '如何', '怎么',
                 '话题', '小红书', '视频', '笔记', '分享', '点赞', '关注', '收藏', '评论', '转发',
                 '创作', '内容', '推荐', '精选', '热门', '飞吻', '得意', '嘻嘻', '薯薯', '薯'}
    
    keywords = []
    for i, note in enumerate(notes[:5]):  # 只看前5条
        title = note.get('title', '') or ''
        desc = note.get('desc') or ''
        print(f"\n笔记 {i+1}:")
        print(f"  标题: {title[:50]}")
        print(f"  描述: {desc[:50] if desc else '(无)'}")
        
        text = title + ' ' + desc[:100]
        
        # 提取2-6个字的中文词组
        chinese_words = re.findall(r'[\u4e00-\u9fa5]{2,6}', text)
        for word in chinese_words:
            if word not in stopwords and len(word) >= 2:
                keywords.append(word)
    
    # 统计词频
    word_count = Counter(keywords)
    most_common = word_count.most_common(10)
    print(f"\n高频词:")
    for word, count in most_common:
        print(f"  {word}: {count}次")
    
    topics = [word for word, count in most_common if count >= 2][:5]
    
    if not topics:
        topics = ["综合内容"]
    
    print(f"\n✅ 提取的话题: {topics}")
    return topics


if __name__ == "__main__":
    # 测试一个已存在的用户
    test_extract_topics("5e6472940000000001008d4e")  # 图灵星球
