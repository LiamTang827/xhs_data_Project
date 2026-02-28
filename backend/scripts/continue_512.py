#!/usr/bin/env python3
"""继续为剩余384维用户生成512维embedding"""

import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root / "backend"))

from database.connection import get_database
from database import UserEmbeddingRepository  
from FlagEmbedding import FlagModel
from datetime import datetime

def main():
    print("\n继续为剩余384维用户生成512维embedding...\n")
    
    # 加载模型
    print("📦 加载bge-small-zh-v1.5模型...")
    model = FlagModel(
        "BAAI/bge-small-zh-v1.5",
        query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
        use_fp16=True
    )
    print("✅ 模型加载完成\n")
    
    db = get_database()
    embedding_repo = UserEmbeddingRepository()
    
    # 获取剩余384维用户
    embs_384 = list(db.user_embeddings.find({'model': 'topic_hash_v1'}))
    print(f"找到 {len(embs_384)} 个384维用户\n")
    
    success = 0
    for i, e in enumerate(embs_384, 1):
        uid = e.get('user_id')
        profile = db.user_profiles.find_one({'user_id': uid})
        
        if not profile:
            print(f"[{i}/{len(embs_384)}] ⚠️  {uid[:16]}: 无profile，跳过")
            continue
        
        nickname = profile.get('nickname', uid[:16])
        pd = profile.get('profile_data', {})
        content_topics = pd.get('content_topics', [])
        
        if not content_topics:
            print(f"[{i}/{len(embs_384)}] ⚠️  {nickname}: 无content_topics，跳过")
            continue
        
        print(f"[{i}/{len(embs_384)}] 🔄 {nickname}")
        
        embedding_text = ' '.join(content_topics[:10])
        print(f"  输入: {embedding_text[:50]}...")
        
        try:
            vec = model.encode([embedding_text])
            embedding = vec.tolist()[0] if hasattr(vec, "tolist") else vec[0].tolist()
            
            # 删除旧384维
            db.user_embeddings.delete_one({
                'platform': 'xiaohongshu',
                'user_id': uid,
                'model': 'topic_hash_v1'
            })
            
            # 保存新512维
            embedding_repo.create_embedding({
                'platform': 'xiaohongshu',
                'user_id': uid,
                'embedding': embedding,
                'model': 'BAAI/bge-small-zh-v1.5',
                'dimension': len(embedding),
                'created_at': datetime.now()
            })
            
            print(f"  ✅ 生成512维embedding (dim={len(embedding)})\n")
            success += 1
        except Exception as ex:
            print(f"  ❌ 失败: {ex}\n")
    
    print(f"\n{'='*60}")
    print(f"完成: 成功{success}/{len(embs_384)}")
    print(f"{'='*60}\n")
    
    # 验证
    dims = {}
    for e in db.user_embeddings.find({'platform':'xiaohongshu'},{'dimension':1}):
        d = e.get('dimension')
        dims[d] = dims.get(d, 0) + 1
    
    print("\n最终统计:")
    for d in sorted(dims):
        print(f"  {d}维: {dims[d]}个")
    
    if len(dims) == 1 and 512 in dims:
        print("\n🎉 所有embedding已统一为512维！")
    else:
        print(f"\n⚠️  还有{dims.get(384, 0)}个384维需要转换")

if __name__ == '__main__':
    main()
