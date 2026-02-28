#!/usr/bin/env python3
"""
为所有缺少embedding的用户生成embedding
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.connection import get_database
import hashlib
import numpy as np
from datetime import datetime

def generate_embedding_from_topics(topics):
    """基于话题生成embedding（与collector_task.py保持一致）"""
    EMBEDDING_DIMENSION = 384
    
    if not topics:
        # 如果没有话题，返回随机向量
        seed = int(hashlib.md5("no_topics".encode()).hexdigest(), 16) % (2**32)
        np.random.seed(seed)
        embedding = np.random.randn(EMBEDDING_DIMENSION)
    else:
        # 基于话题文本生成确定性向量
        topics_text = " ".join(sorted(topics))
        seed = int(hashlib.md5(topics_text.encode()).hexdigest(), 16) % (2**32)
        np.random.seed(seed)
        embedding = np.random.randn(EMBEDDING_DIMENSION)
    
    # 归一化
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
    
    return embedding.tolist()

def main():
    db = get_database()
    
    print("检查缺少embedding的用户...")
    
    # 找出所有user_profiles
    all_users = list(db.user_profiles.find({}))
    print(f"总用户数: {len(all_users)}")
    
    no_embedding_count = 0
    for user in all_users:
        user_id = user.get('user_id')
        nickname = user.get('nickname', user_id[:15])
        
        # 检查是否已有embedding
        existing = db.user_embeddings.find_one({'user_id': user_id})
        if existing:
            continue
        
        no_embedding_count += 1
        print(f"\n[{no_embedding_count}] {nickname}")
        print(f"   user_id: {user_id}")
        
        # 从profile_data提取topics
        profile_data = user.get('profile_data', {})
        topics = profile_data.get('content_topics', [])
        print(f"   topics: {topics[:5] if len(topics) > 5 else topics}")
        
        # 如果没有topics，尝试从其他地方提取
        if not topics:
            # 从用户描述或其他字段提取关键词
            desc = user.get('desc', '')
            if desc:
                # 简单地将描述切分为词
                topics = [word.strip() for word in desc.split() if len(word.strip()) > 2][:10]
                print(f"   从desc提取: {topics[:3]}")
        
        # 生成embedding
        embedding = generate_embedding_from_topics(topics)
        
        # 保存到数据库
        embedding_doc = {
            'user_id': user_id,
            'platform': user.get('platform', 'xiaohongshu'),
            'model': 'topic_hash_v1',
            'dimension': 384,
            'embedding': embedding,
            'topics': topics,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = db.user_embeddings.insert_one(embedding_doc)
        print(f"   ✅ 已生成embedding (id: {result.inserted_id})")
    
    print(f"\n\n✅ 完成! 共生成了 {no_embedding_count} 个embedding")
    
    # 统计
    final_count = db.user_embeddings.count_documents({})
    print(f"   总embedding数: {final_count}")

if __name__ == "__main__":
    main()
