#!/usr/bin/env python3
"""
通过笔记内容特征，将user_profiles的昵称匹配到user_snapshots的user_id
"""

import os
import sys
from pathlib import Path

# 添加backend到路径
project_root = Path(__file__).resolve().parent.parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
load_dotenv(project_root / '.env')

from database import UserProfileRepository, UserSnapshotRepository


def match_by_keywords():
    """通过关键词匹配profiles和snapshots"""
    
    profile_repo = UserProfileRepository()
    snapshot_repo = UserSnapshotRepository()
    
    # 定义匹配规则（昵称必须与数据库中完全匹配）
    matching_rules = {
        "星球研究所InstituteforPlanet": ["星球研究所", "风花雪月", "地球", "中国人还能修地球"],
        "无穷小亮的科普日常": ["网络热传生物鉴定", "亮记", "无穷小亮"],
        "小Lin说": ["票房", "经济", "财经", "百亿"],
        "小熊说你超有爱": ["失业", "就业", "实业立国", "蓝海"],
        "Ada在美国": ["美国生活", "西雅图生活", "找对象", "美国吃喝"],
        "硅谷樱花小姐姐🌸": ["CES", "硅谷", "Sphere", "Vegas"],  
        "大圆镜科普": ["绝对零度", "薛定谔", "诺奖", "量子", "芯片上"],
        "所长林超": ["周年啦", "创业", "斯坦福", "合伙人"],
        "图灵星球TuringPlanet": ["AI项目", "产品", "从idea", "图灵", "机器学习"],
    }
    
    profiles = list(profile_repo.collection.find({'user_id': {'$in': ['', None]}}))
    snapshots = list(snapshot_repo.collection.find({'platform': 'xiaohongshu'}))
    
    print("="*60)
    print("🔍 开始匹配profiles和snapshots...")
    print("="*60)
    
    matches = []
    
    for snapshot in snapshots:
        user_id = snapshot['user_id']
        notes = snapshot.get('notes', [])
        
        if not notes:
            continue
        
        # 获取所有笔记标题
        all_titles = ' '.join([n.get('title', '') for n in notes[:10]])
        
        # 尝试匹配每个profile
        matched_nickname = None
        max_keyword_matches = 0
        
        for nickname, keywords in matching_rules.items():
            keyword_matches = sum(1 for kw in keywords if kw in all_titles)
            if keyword_matches > max_keyword_matches:
                max_keyword_matches = keyword_matches
                matched_nickname = nickname
        
        if matched_nickname and max_keyword_matches >= 1:
            matches.append({
                'user_id': user_id,
                'nickname': matched_nickname,
                'keyword_matches': max_keyword_matches,
                'sample_title': notes[0].get('title', '')[:50]
            })
            print(f"\n✅ 匹配成功:")
            print(f"   user_id: {user_id[:16]}...")
            print(f"   昵称: {matched_nickname}")
            print(f"   关键词匹配数: {max_keyword_matches}")
            print(f"   示例标题: {notes[0].get('title', '')[:50]}")
        else:
            print(f"\n❌ 未匹配:")
            print(f"   user_id: {user_id[:16]}...")
            print(f"   示例标题: {notes[0].get('title', '')[:50]}")
    
    # 询问是否更新数据库
    print(f"\n{'='*60}")
    print(f"找到 {len(matches)} 个匹配")
    print(f"{'='*60}")
    
    if matches:
        confirm = input("\n是否更新user_profiles中的user_id？(y/n): ")
        if confirm.lower() == 'y':
            for match in matches:
                profile_repo.collection.update_one(
                    {'nickname': match['nickname']},
                    {'$set': {'user_id': match['user_id']}}
                )
            print(f"\n✅ 已更新 {len(matches)} 个profiles的user_id")
        else:
            print("\n❌ 已取消更新")


if __name__ == "__main__":
    match_by_keywords()
