#!/usr/bin/env python3
"""
重新生成创作者网络 - 优化版
基于已有的profiles和embeddings计算相似度连边
从snapshots读取笔记数据计算互动指标
"""

import sys
from pathlib import Path
import argparse
import numpy as np
from datetime import datetime, timedelta

# 添加backend到路径
project_root = Path(__file__).resolve().parent.parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
load_dotenv(project_root / '.env')

from database import CreatorNetworkRepository
from database.connection import get_database


def calculate_note_stats(notes: list, days: int = 30) -> dict:
    """
    计算最近N天的笔记互动数据
    
    Args:
        notes: 笔记列表
        days: 统计最近多少天，默认30天
        
    Returns:
        互动统计数据
    """
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
            # 转换为互动指数（简化：直接用互动数/1000）
            index_value = note_engagement / 1000.0
            index_series.append({
                'ts': create_time * 1000,  # 转为毫秒
                'value': round(index_value, 2),
                'note_id': note.get('note_id', ''),
                'title': note.get('title', '')[:30]  # 保存笔记标题（成长路径功能需要）
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


def regenerate_creator_network(similarity_threshold: float = 0.5):
    """
    重新生成创作者网络 - 基于已有profiles和embeddings
    
    Args:
        similarity_threshold: 相似度阈值 (0-1)
    """
    print("\n" + "=" * 60)
    print("🔄 重新生成创作者网络（基于embeddings）")
    print(f"📊 相似度阈值: {similarity_threshold}")
    print("=" * 60)
    
    db = get_database()
    network_repo = CreatorNetworkRepository()
    
    # 1. 从user_profiles获取所有用户
    print("\n📥 步骤 1: 读取所有用户profile...")
    profiles = list(db.user_profiles.find({'platform': 'xiaohongshu'}))
    print(f"✅ 找到 {len(profiles)} 个用户")
    
    # 2. 从user_embeddings获取所有向量
    print("\n📥 步骤 2: 读取所有用户embedding...")
    embeddings = list(db.user_embeddings.find({'platform': 'xiaohongshu'}))
    
    # 建立user_id -> embedding映射
    user_embeddings = {}
    for emb in embeddings:
        user_id = emb.get('user_id')
        vector = emb.get('embedding')
        if user_id and vector:
            user_embeddings[user_id] = np.array(vector)
    
    print(f"✅ 找到 {len(user_embeddings)} 个embedding向量")
    
    # 3. 构建创作者节点（使用profile中已有的统计数据）
    creators = []
    
    for profile in profiles:
        user_id = profile['user_id']
        
        # 只包含有embedding的用户
        if user_id not in user_embeddings:
            continue
        
        # 从profile获取基本信息
        basic_info = profile.get('basic_info', {})
        stats = profile.get('stats', {})
        profile_data = profile.get('profile_data', {})
        
        nickname = basic_info.get('nickname', profile.get('nickname', 'Unknown'))
        followers = stats.get('fans', 0)
        avatar = basic_info.get('avatar', '')
        ip_location = basic_info.get('ip_location', '')
        desc = basic_info.get('desc', '')
        red_id = basic_info.get('red_id', '')
        
        # 从profile_data获取topics
        content_topics = profile_data.get('content_topics', [])
        if not content_topics:
            # fallback到旧的user_style
            user_style = profile_data.get('user_style', {})
            interests = user_style.get('interests', [])
            content_topics = interests if interests else ['综合内容']
        
        # 使用profile中已有的互动数据（如果有的话）
        # 这些数据应该在添加创作者时就计算好并存储在stats中
        total_engagement = stats.get('total_engagement', 0)
        total_likes = stats.get('total_likes', 0)
        total_collects = stats.get('total_collects', 0)
        total_comments = stats.get('total_comments', 0)
        total_shares = stats.get('total_shares', 0)
        note_count = stats.get('note_count', 0)
        index_series = stats.get('index_series', [])
        
        creators.append({
            'id': user_id,
            'name': nickname,
            'followers': followers,
            'fansGrowth7d': 0,  # TODO: 可以从stats_history计算
            'totalEngagement': total_engagement,
            'totalLikes': total_likes,
            'totalCollects': total_collects,
            'totalComments': total_comments,
            'totalShares': total_shares,
            'noteCount': note_count,
            'primaryTrack': content_topics[0] if content_topics else '综合内容',
            'contentForm': '创作者',
            'recentKeywords': [],
            'position': {'x': 0, 'y': 0},
            'avatar': avatar,
            'ipLocation': ip_location,
            'desc': desc,
            'redId': red_id,
            'topics': content_topics[:8],  # 最多8个话题
            'indexSeries': index_series  # 从profile读取，包含笔记标题用于成长路径功能
        })
    
    print(f"✅ 构建了 {len(creators)} 个创作者节点")
    
    # 4. 计算embedding相似度，生成边
    print("\n🔗 步骤 4: 计算相似度并生成连接...")
    edges = []
    
    if len(creators) < 2:
        print("⚠️  创作者数量不足2个，无法生成连接")
    else:
        for i, creator1 in enumerate(creators):
            for j, creator2 in enumerate(creators):
                if i >= j:
                    continue
                
                id1 = creator1['id']
                id2 = creator2['id']
                
                if id1 not in user_embeddings or id2 not in user_embeddings:
                    continue
                
                vec1 = user_embeddings[id1]
                vec2 = user_embeddings[id2]
                
                # 余弦相似度
                similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
                similarity = float(similarity)
                
                # 相似度 > similarity_threshold 才连边
                if similarity > similarity_threshold:
                    edges.append({
                        'source': id1,
                        'target': id2,
                        'weight': similarity,
                        'types': {
                            'keyword': similarity,
                            'audience': 0,
                            'style': 0,
                            'campaign': 0
                        }
                    })
        
        print(f"✅ 生成了 {len(edges)} 条连接")
        
        # 显示一些连接示例
        if edges:
            id_to_name = {c['id']: c['name'] for c in creators}
            print("\n前5个连接:")
            for edge in edges[:5]:
                src_name = id_to_name.get(edge['source'], edge['source'][:16])
                tgt_name = id_to_name.get(edge['target'], edge['target'][:16])
                print(f"  🔗 {src_name} <-> {tgt_name}: {edge['weight']:.3f}")
    
    # 5. 保存网络数据
    print("\n💾 步骤 5: 保存网络数据...")
    
    network_data = {
        'platform': 'xiaohongshu',
        'network_data': {
            'creators': creators,
            'edges': edges
        },
        'created_at': datetime.now()
    }
    
    # 删除旧数据
    db.creator_networks.delete_many({'platform': 'xiaohongshu'})
    
    # 插入新数据
    result = db.creator_networks.insert_one(network_data)
    
    print(f"✅ 网络数据已保存")
    print("\n" + "=" * 60)
    print("✨ 完成!")
    print(f"📊 创作者数: {len(creators)}")
    print(f"🔗 连接数: {len(edges)}")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='重新生成创作者网络')
    parser.add_argument(
        '--similarity-threshold',
        type=float,
        default=0.5,
        help='相似度阈值 (0-1)，默认0.5'
    )
    args = parser.parse_args()
    
    print(f"📊 使用相似度阈值: {args.similarity_threshold}")
    regenerate_creator_network(similarity_threshold=args.similarity_threshold)
