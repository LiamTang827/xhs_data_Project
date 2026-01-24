#!/usr/bin/env python3
"""
Generate creators_data.json from MongoDB for FastAPI
从MongoDB读取用户画像和embedding数据，生成创作者网络数据
"""
import json
import math
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 添加backend到路径
project_root = Path(__file__).resolve().parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

# 加载环境变量
env_file = project_root / '.env'
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv(backend_path / '.env')

from database import UserProfileRepository, UserEmbeddingRepository, UserSnapshotRepository

OUT_JSON = backend_path / 'data' / 'creators_data.json'

WEIGHT_FOLLOWERS = 0.6
WEIGHT_INTERACTION = 0.4
SIMILARITY_THRESHOLD = 0.7  # 余弦相似度阈值，高于此值才建立边

def safe_int(v):
    try:
        return int(v)
    except Exception:
        try:
            return int(float(v))
        except Exception:
            return 0

def calculate_influence(followers, interaction):
    """计算影响力指数"""
    return round(WEIGHT_FOLLOWERS * followers + WEIGHT_INTERACTION * interaction)

def cosine_similarity(vec1, vec2):
    """计算两个向量的余弦相似度"""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = math.sqrt(sum(a * a for a in vec1))
    mag2 = math.sqrt(sum(b * b for b in vec2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)

def main():
    """从MongoDB生成创作者网络数据"""
    print("🚀 从MongoDB生成创作者网络数据...")
    print("=" * 60)
    
    # 初始化repositories
    profile_repo = UserProfileRepository()
    embedding_repo = UserEmbeddingRepository()
    snapshot_repo = UserSnapshotRepository()
    
    # 获取所有用户画像
    profiles = profile_repo.get_all_profiles(platform='xiaohongshu')
    print(f"📊 找到 {len(profiles)} 个用户画像")
    
    if not profiles:
        print("❌ 没有用户画像数据")
        return
    
    # 构建节点数据
    nodes = []
    embeddings_dict = {}  # nickname -> embedding
    
    for profile in profiles:
        nickname = profile.get('nickname')
        if not nickname:
            continue
            
        profile_data = profile.get('profile_data', {})
        user_basic = profile_data.get('user_basic', {})
        
        # ✅ 从user_basic中获取真实的user_id（小红书ID）
        real_user_id = user_basic.get('user_id', '')
        
        # 获取embedding（user_embeddings中用的是nickname作为user_id）
        embedding_doc = embedding_repo.get_by_user_id(nickname, platform='xiaohongshu')
        if embedding_doc:
            # 尝试两个字段：优先user_style_embedding，备选embedding
            embedding = embedding_doc.get('user_style_embedding', [])
            if not embedding or len(embedding) == 0:
                embedding = embedding_doc.get('embedding', [])
            if embedding and len(embedding) > 0:
                embeddings_dict[nickname] = embedding
        
        # ✅ 用真实user_id从user_snapshots获取笔记数据
        snapshot = snapshot_repo.get_by_user_id(real_user_id, platform='xiaohongshu')
        total_notes = 0
        total_likes = 0
        total_comments = 0
        
        print(f"\n📝 {nickname}:")
        print(f"   Real user_id: {real_user_id}")
        
        if snapshot:
            notes = snapshot.get('notes', [])
            total_notes = len(notes)
            print(f"   ✅ Found {total_notes} notes")
            for note in notes:
                # 兼容两种字段名：likes/liked_count, comments_count/comment_count
                total_likes += safe_int(note.get('likes', note.get('liked_count', 0)))
                total_comments += safe_int(note.get('comments_count', note.get('comment_count', 0)))
            print(f"   💖 Likes: {total_likes:,}, 💬 Comments: {total_comments:,}")
        else:
            print(f"   ⚠️  No snapshot found")
        
        followers = safe_int(user_basic.get('fans', 0))
        interaction = total_likes + total_comments
        influence = calculate_influence(followers, interaction)
        
        # 匹配前端期望的creator格式
        node = {
            'id': nickname,
            'name': nickname,
            'followers': followers,
            'engagementIndex': interaction,
            'primaryTrack': profile_data.get('content_topics', ['其他'])[0] if profile_data.get('content_topics') else '其他',
            'contentForm': '创作者',
            'recentKeywords': profile_data.get('content_topics', []),
            'position': {'x': 0, 'y': 0},
            'avatar': user_basic.get('avatar', ''),
            'ipLocation': user_basic.get('ip_location', ''),
            'desc': user_basic.get('desc', ''),
            'redId': user_basic.get('user_id', ''),
            'influence': influence,
            'total_notes': total_notes,
            'topics': profile_data.get('content_topics', []),
            'styles': profile_data.get('content_style', []),
            'created_at': profile.get('created_at', datetime.now()).isoformat() if isinstance(profile.get('created_at'), datetime) else str(profile.get('created_at', ''))
        }
        nodes.append(node)
    
    print(f"✅ 生成了 {len(nodes)} 个节点")
    print(f"   - 有embedding的节点: {len(embeddings_dict)} 个")
    
    # 构建边数据（基于embedding相似度）
    edges = []
    names = list(embeddings_dict.keys())
    
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            name1, name2 = names[i], names[j]
            sim = cosine_similarity(embeddings_dict[name1], embeddings_dict[name2])
            
            if sim >= SIMILARITY_THRESHOLD:
                edges.append({
                    'source': name1,
                    'target': name2,
                    'weight': round(sim, 3),
                    'types': {'keyword': 0, 'audience': 0, 'style': 1}
                })
    
    print(f"✅ 生成了 {len(edges)} 条边（相似度 >= {SIMILARITY_THRESHOLD}）")
    
    # 构建trackClusters（按主题分组）
    trackClusters = {}
    for node in nodes:
        track = node.get('primaryTrack', '其他')
        if track not in trackClusters:
            trackClusters[track] = []
        trackClusters[track].append(node['id'])
    
    # 生成最终数据（匹配前端期望的格式）
    output_data = {
        'creators': nodes,  # 改为creators
        'creatorEdges': edges,  # 改为creatorEdges
        'trackClusters': trackClusters,
        'trendingKeywordGroups': [],  # 空数组
        'metadata': {
            'total_creators': len(nodes),
            'total_connections': len(edges),
            'similarity_threshold': SIMILARITY_THRESHOLD,
            'generated_at': datetime.now().isoformat(),
            'source': 'MongoDB'
        }
    }
    
    # 保存到JSON文件
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已生成: {OUT_JSON}")
    print(f"   - 创作者: {len(nodes)} 个")
    print(f"   - 连接: {len(edges)} 条")
    print("\n💡 数据已更新，FastAPI将自动使用新数据")

if __name__ == "__main__":
    main()
