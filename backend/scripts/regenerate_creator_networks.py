#!/usr/bin/env python3
"""
重新生成创作者网络数据 - 基于user_snapshots
从笔记数据计算真实的 followers 和 engagementIndex
从 user_profiles 或笔记标题提取 topics（流量密码）
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import re
from collections import Counter

# 添加backend到路径
project_root = Path(__file__).resolve().parent.parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
load_dotenv(project_root / '.env')

from database import (
    UserProfileRepository,
    UserSnapshotRepository,
    CreatorNetworkRepository
)
from database.connection import get_database
import numpy as np


def calculate_creator_index(notes: list, followers: int, days: int = 30) -> dict:
    """
    计算Creator Index - 简单统计最近30天的总互动数
    
    Args:
        notes: 笔记列表
        followers: 粉丝数
        days: 统计最近多少天的笔记，默认30天
        
    Returns:
        {
            "total_engagement": int,  # 总互动数（点赞+收藏+评论+分享）
            "total_likes": int,
            "total_collects": int,
            "total_comments": int,
            "total_shares": int,
            "note_count": int  # 最近30天笔记数
        }
    """
    from datetime import datetime, timedelta
    
    # 过滤最近N天的笔记
    cutoff_time = datetime.now() - timedelta(days=days)
    cutoff_timestamp = int(cutoff_time.timestamp())
    recent_notes = [n for n in notes if n.get('create_time', 0) >= cutoff_timestamp]
    
    if not recent_notes:
        return {
            "total_engagement": 0,
            "total_likes": 0,
            "total_collects": 0,
            "total_comments": 0,
            "total_shares": 0,
            "note_count": 0
        }
    
    # 统计总数
    total_likes = sum(n.get('likes', 0) for n in recent_notes)
    total_collects = sum(n.get('collected_count', 0) for n in recent_notes)
    total_comments = sum(n.get('comments_count', 0) for n in recent_notes)
    total_shares = sum(n.get('share_count', 0) for n in recent_notes)
    total_engagement = total_likes + total_collects + total_comments + total_shares
    
    return {
        "total_engagement": total_engagement,
        "total_likes": total_likes,
        "total_collects": total_collects,
        "total_comments": total_comments,
        "total_shares": total_shares,
        "note_count": len(recent_notes)
    }


def extract_hashtags_from_notes(notes: list, max_tags: int = 8, days: int = 30) -> list:
    """
    从笔记标题和描述中提取#话题标签 - 只分析最近N天的笔记
    
    Args:
        notes: 笔记列表
        max_tags: 最多返回多少个标签
        days: 分析最近多少天的笔记，默认30天
    """
    from datetime import datetime, timedelta
    
    # 过滤最近N天的笔记
    cutoff_time = datetime.now() - timedelta(days=days)
    cutoff_timestamp = int(cutoff_time.timestamp())
    
    recent_notes = [n for n in notes if n.get('create_time', 0) >= cutoff_timestamp]
    
    if not recent_notes:
        # 如果最近30天没有笔记，使用所有笔记
        recent_notes = notes[:20]
    
    hashtags = []
    
    for note in recent_notes[:20]:  # 最多分析20条
        title = note.get('title', '') or ''
        desc = note.get('desc') or ''
        text = title + ' ' + desc
        
        # 提取 #xxx 或 #xxx# 格式的话题
        # 匹配 # 后面跟着的中文、英文、数字
        tags = re.findall(r'#([\w\u4e00-\u9fa5]+)', text)
        hashtags.extend(tags)
    
    # 统计词频，返回高频标签
    if hashtags:
        tag_count = Counter(hashtags)
        result = [tag for tag, count in tag_count.most_common(max_tags)]
        return result
    
    return ["综合内容"]


def regenerate_creator_network():
    """重新生成创作者网络数据"""
    print("="*60)
    print("🔄 重新生成创作者网络数据（基于user_snapshots）")
    print("="*60)
    
    profile_repo = UserProfileRepository()
    snapshot_repo = UserSnapshotRepository()
    network_repo = CreatorNetworkRepository()
    
    # 1. 从snapshots获取所有用户
    print("\n📥 步骤 1: 读取所有用户快照...")
    snapshots = list(snapshot_repo.collection.find({'platform': 'xiaohongshu'}))
    print(f"✅ 找到 {len(snapshots)} 个用户快照")
    
    # 2. 为每个用户生成节点数据
    creators = []
    
    for i, snapshot in enumerate(snapshots, 1):
        user_id = snapshot['user_id']
        notes = snapshot.get('notes', [])
        
        if not notes:
            print(f"\n[{i}/{len(snapshots)}] ⚠️  {user_id}: 没有笔记数据，跳过")
            continue
        
        # 先获取profile（用于获取nickname和topics）
        profile = profile_repo.get_by_user_id(user_id)
        
        # 尝试从多个来源获取昵称和基础信息
        nickname = 'Unknown'
        followers = 0
        avatar = ''
        ip_location = ''
        desc = ''
        fans_growth_7d = None  # 7天粉丝增长
        
        if profile:
            # 从新结构获取
            basic_info = profile.get('basic_info', {})
            stats = profile.get('stats', {})
            stats_history = profile.get('stats_history', [])
            
            nickname = basic_info.get('nickname', profile.get('nickname', 'Unknown'))
            followers = stats.get('fans', 0)  # ✅ 从API获取的真实粉丝数
            avatar = basic_info.get('avatar', '')
            ip_location = basic_info.get('ip_location', '')
            desc = basic_info.get('desc', '')
            
            # 计算7天粉丝增长
            if stats_history:
                from datetime import datetime, timedelta
                seven_days_ago = datetime.now() - timedelta(days=7)
                
                # 找到最接近7天前的历史记录
                closest_record = None
                min_diff = float('inf')
                
                for record in stats_history:
                    record_time = record.get('timestamp')
                    if record_time:
                        time_diff = abs((record_time - seven_days_ago).total_seconds())
                        if time_diff < min_diff:
                            min_diff = time_diff
                            closest_record = record
                
                # 如果找到7天内的历史记录（允许前后2天的误差）
                if closest_record and min_diff < 2 * 24 * 3600:  # 2天的秒数
                    old_fans = closest_record.get('fans', 0)
                    fans_growth_7d = followers - old_fans
        
        print(f"\n[{i}/{len(snapshots)}] 处理: {nickname} (user_id: {user_id[:12]}...)")
        print(f"  📊 粉丝数: {followers:,}")
        if fans_growth_7d is not None:
            growth_pct = (fans_growth_7d / followers * 100) if followers > 0 else 0
            print(f"  📈 7天增长: {fans_growth_7d:+,} ({growth_pct:+.2f}%)")
        
        # 计算最近30天的互动数据
        stats = calculate_creator_index(notes, followers, days=30)
        total_engagement = stats["total_engagement"]
        total_likes = stats["total_likes"]
        total_collects = stats["total_collects"]
        total_comments = stats["total_comments"]
        total_shares = stats["total_shares"]
        note_count = stats["note_count"]
        
        # 从最近30天笔记中提取#话题标签（不使用旧的AI分析数据）
        print(f"  🔍 提取#话题标签...")
        topics = extract_hashtags_from_notes(notes, max_tags=8, days=30)
        
        if not topics:
            topics = ["综合内容"]
        
        primary_track = topics[0] if topics else "综合内容"
        content_form = "创作者"
        
        # 生成Creator Index时间序列（基于最近30天笔记的流量）
        from datetime import datetime, timedelta
        cutoff_time = datetime.now() - timedelta(days=30)
        cutoff_timestamp = int(cutoff_time.timestamp())
        
        # 过滤最近30天的笔记
        recent_notes = [n for n in notes if n.get('create_time', 0) >= cutoff_timestamp]
        sorted_notes = sorted(recent_notes, key=lambda x: x.get('create_time', 0))
        
        index_series = []
        for note in sorted_notes:  # 所有最近30天的笔记
            create_time = note.get('create_time', 0)
            if create_time > 0:
                # 计算单条笔记的互动指数
                likes = note.get('likes', 0)
                collects = note.get('collected_count', 0)
                comments = note.get('comments_count', 0)
                shares = note.get('share_count', 0)
                
                note_engagement = likes + collects + comments + shares
                # 转换为互动率（如果有粉丝数）
                if followers > 0:
                    note_rate = round((note_engagement / followers) * 100, 2)
                else:
                    note_rate = note_engagement
                
                index_series.append({
                    "ts": create_time * 1000,  # 转换为毫秒时间戳
                    "value": note_rate
                })
        
        # 生成节点
        creator_node = {
            "id": user_id,
            "name": nickname,
            "followers": followers,
            "fansGrowth7d": fans_growth_7d,  # 7天粉丝增长
            "totalEngagement": total_engagement,  # 总互动数
            "totalLikes": total_likes,
            "totalCollects": total_collects,
            "totalComments": total_comments,
            "totalShares": total_shares,
            "noteCount": note_count,  # 最近30天笔记数
            "primaryTrack": primary_track,
            "contentForm": content_form,
            "recentKeywords": [],
            "position": {"x": 0, "y": 0},  # 前端会重新计算
            "avatar": avatar,
            "ipLocation": ip_location,
            "desc": desc,
            "redId": "",
            "topics": topics,
            "indexSeries": index_series  # 添加时间序列数据
        }
        
        creators.append(creator_node)
        
        print(f"  ✅ 最近30天: {note_count}篇笔记")
        print(f"  ✅ 总互动: {total_engagement:,} (👍{total_likes:,} 💾{total_collects:,} 💬{total_comments:,} 🔗{total_shares:,})")
        print(f"  ✅ 话题: {', '.join(topics[:3])}")
    
    # 3. 生成边（基于embedding余弦相似度）
    print(f"\n{'='*60}")
    print("🔗 步骤 2: 生成创作者关系（基于embedding语义相似度）...")
    
    # 获取所有用户的embeddings
    db = get_database()
    embeddings_collection = db['user_embeddings']
    
    # 构建user_id到embedding的映射
    user_embeddings = {}
    for creator in creators:
        user_id = creator['id']
        # 尝试通过user_id查找embedding
        embedding_doc = embeddings_collection.find_one({
            'platform': 'xiaohongshu',
            '$or': [
                {'user_id': user_id},
                {'user_id': creator['name']}  # 兼容旧数据（用昵称作为key）
            ]
        })
        
        if embedding_doc and embedding_doc.get('embedding'):
            user_embeddings[user_id] = np.array(embedding_doc['embedding'])
    
    print(f"✅ 找到 {len(user_embeddings)} 个用户的embedding向量")
    
    edges = []
    
    # 如果有embedding，用余弦相似度计算
    if len(user_embeddings) >= 2:
        for i, creator1 in enumerate(creators):
            for j, creator2 in enumerate(creators):
                if i >= j:
                    continue
                
                id1 = creator1['id']
                id2 = creator2['id']
                
                # 如果两个用户都有embedding，用向量相似度
                if id1 in user_embeddings and id2 in user_embeddings:
                    vec1 = user_embeddings[id1]
                    vec2 = user_embeddings[id2]
                    
                    # 余弦相似度
                    similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
                    similarity = float(similarity)  # 转为Python float
                    
                    # 相似度 > 0.5 才连边
                    if similarity > 0.5:
                        edges.append({
                            "source": id1,
                            "target": id2,
                            "weight": similarity,
                            "types": {
                                "keyword": similarity,
                                "audience": 0,
                                "style": 0,
                                "campaign": 0
                            }
                        })
                        print(f"  🔗 {creator1['name']} <-> {creator2['name']}: {similarity:.3f}")
                
                # 否则fallback到topic匹配（兼容）
                elif not user_embeddings:
                    topics1 = set(creator1.get('topics', []))
                    topics2 = set(creator2.get('topics', []))
                    
                    if topics1 and topics2:
                        intersection = len(topics1 & topics2)
                        union = len(topics1 | topics2)
                        similarity = intersection / union if union > 0 else 0
                        
                        # 相似度 > 0.1 才连边
                        if similarity > 0.1:
                            edges.append({
                                "source": id1,
                                "target": id2,
                                "weight": similarity,
                                "types": {
                                    "keyword": similarity,
                                    "audience": 0,
                                    "style": 0,
                                    "campaign": 0
                                }
                            })
    else:
        print("  ⚠️  没有embedding数据，使用topic匹配fallback...")
        for i, creator1 in enumerate(creators):
            for j, creator2 in enumerate(creators):
                if i >= j:
                    continue
                
                topics1 = set(creator1.get('topics', []))
                topics2 = set(creator2.get('topics', []))
                
                if topics1 and topics2:
                    intersection = len(topics1 & topics2)
                    union = len(topics1 | topics2)
                    similarity = intersection / union if union > 0 else 0
                    
                    # 相似度 > 0.1 才连边
                    if similarity > 0.1:
                        edges.append({
                            "source": creator1['id'],
                            "target": creator2['id'],
                            "weight": similarity,
                            "types": {
                                "keyword": similarity,
                                "audience": 0,
                                "style": 0,
                                "campaign": 0
                            }
                        })
    
    print(f"✅ 生成 {len(edges)} 条边")
    
    # 4. 保存到MongoDB
    print(f"\n{'='*60}")
    print("💾 步骤 3: 保存到MongoDB...")
    
    network_data = {
        "platform": "xiaohongshu",
        "network_data": {
            "creators": creators,
            "edges": edges
        },
        "created_at": datetime.now()
    }
    
    # 删除旧数据
    network_repo.collection.delete_many({"platform": "xiaohongshu"})
    network_repo.create_network(network_data)
    
    print(f"✅ 已保存到 creator_networks")
    
    # 5. 统计
    print(f"\n{'='*60}")
    print("📊 数据统计:")
    print(f"{'='*60}")
    print(f"创作者总数: {len(creators)}")
    print(f"关系边数: {len(edges)}")
    
    print(f"\n创作者列表（按总互动数排序）:")
    
    for creator in sorted(creators, key=lambda x: x['totalEngagement'], reverse=True):
        print(f"  • {creator['name']}")
        print(f"    - 粉丝: {creator['followers']:,}")
        print(f"    - 最近30天: {creator['noteCount']}篇笔记")
        print(f"    - 总互动: {creator['totalEngagement']:,} (👍{creator['totalLikes']:,} 💾{creator['totalCollects']:,} 💬{creator['totalComments']:,} 🔗{creator['totalShares']:,})")
        print(f"    - 话题: {', '.join(creator['topics'][:3])}")
    
    print(f"\n{'='*60}")
    print("✨ 创作者网络重新生成完成！")
    print(f"{'='*60}")


if __name__ == "__main__":
    regenerate_creator_network()
