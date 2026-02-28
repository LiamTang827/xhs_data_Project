#!/usr/bin/env python3
"""统一所有embedding为512维（使用bge-small-zh-v1.5模型）"""

import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root / "backend"))

from database.connection import get_database
from database import UserEmbeddingRepository
from FlagEmbedding import FlagModel
import numpy as np
from datetime import datetime

def check_profiles():
    """检查384维用户的profile完整性"""
    db = get_database()
    embs_384 = list(db.user_embeddings.find({'model': 'topic_hash_v1'}))
    
    print(f"\n{'='*80}")
    print(f"检查384维用户的profile_data完整性")
    print(f"{'='*80}\n")
    print(f"384维用户总数: {len(embs_384)}\n")
    
    ready_users = []
    missing_users = []
    
    for e in embs_384:
        uid = e.get('user_id')
        p = db.user_profiles.find_one({'user_id': uid})
        
        if p:
            pd = p.get('profile_data', {})
            user_style = pd.get('user_style', {})
            
            if user_style and isinstance(user_style, dict):
                persona = user_style.get('persona', '')
                tone = user_style.get('tone', '')
                interests = user_style.get('interests', [])
                
                if persona or tone or interests:
                    ready_users.append({
                        'user_id': uid,
                        'nickname': p.get('nickname', uid[:16]),
                        'user_style': user_style
                    })
                    print(f"✅ {p.get('nickname', uid[:16])}")
                else:
                    missing_users.append((uid, p.get('nickname', uid[:16]), 'user_style为空'))
                    print(f"❌ {p.get('nickname', uid[:16])}: user_style字段为空")
            else:
                missing_users.append((uid, p.get('nickname', uid[:16]), '缺少user_style'))
                print(f"❌ {p.get('nickname', uid[:16])}: 缺少user_style")
        else:
            missing_users.append((uid, uid[:16], '无profile记录'))
            print(f"❌ {uid[:16]}: 无profile记录")
    
    print(f"\n{'='*80}")
    print(f"统计结果:")
    print(f"  ✅ 可以生成embedding: {len(ready_users)} / {len(embs_384)}")
    print(f"  ❌ 缺少profile_data: {len(missing_users)} / {len(embs_384)}")
    
    if missing_users:
        print(f"\n⚠️  缺少profile_data的用户:")
        for uid, name, reason in missing_users:
            print(f"  - {name}: {reason}")
    
    return ready_users, missing_users

def regenerate_embeddings(ready_users):
    """为ready_users重新生成512维embedding"""
    if not ready_users:
        print("\n⚠️  没有可以生成embedding的用户")
        return
    
    print(f"\n{'='*80}")
    print(f"开始重新生成512维embedding")
    print(f"{'='*80}\n")
    
    # 加载模型
    print("📦 加载bge-small-zh-v1.5模型...")
    try:
        model = FlagModel(
            "BAAI/bge-small-zh-v1.5",
            query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
            use_fp16=True
        )
        print("✅ 模型加载完成\n")
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return
    
    db = get_database()
    embedding_repo = UserEmbeddingRepository()
    
    success = 0
    failed = 0
    
    for user in ready_users:
        uid = user['user_id']
        nickname = user['nickname']
        user_style = user['user_style']
        
        try:
            # 构造embedding输入文本
            persona = user_style.get('persona', '')
            tone = user_style.get('tone', '')
            interests = user_style.get('interests', [])
            
            if isinstance(interests, list):
                interests_text = ' '.join(interests)
            else:
                interests_text = str(interests)
            
            embedding_text = f"{persona} {tone} {interests_text}".strip()
            
            print(f"处理: {nickname}")
            print(f"  输入: {embedding_text[:80]}...")
            
            # 生成embedding
            vec = model.encode([embedding_text])
            if hasattr(vec, "tolist"):
                embedding = vec.tolist()[0]
            else:
                embedding = np.array(vec).tolist()[0] if isinstance(vec, list) else vec[0].tolist()
            
            # 删除旧的384维embedding
            db.user_embeddings.delete_one({
                'platform': 'xiaohongshu',
                'user_id': uid,
                'model': 'topic_hash_v1'
            })
            print(f"  🗑️  删除旧的384维embedding")
            
            # 保存新的512维embedding
            embedding_doc = {
                'platform': 'xiaohongshu',
                'user_id': uid,
                'embedding': embedding,
                'model': 'BAAI/bge-small-zh-v1.5',
                'dimension': len(embedding),
                'created_at': datetime.now()
            }
            
            embedding_repo.create_embedding(embedding_doc)
            print(f"  ✅ 生成512维embedding (dim={len(embedding)})\n")
            
            success += 1
            
        except Exception as e:
            print(f"  ❌ 失败: {e}\n")
            failed += 1
    
    print(f"{'='*80}")
    print(f"完成统计:")
    print(f"  ✅ 成功: {success}")
    print(f"  ❌ 失败: {failed}")
    print(f"{'='*80}\n")

def verify_embeddings():
    """验证所有embedding是否统一为512维"""
    db = get_database()
    embs = list(db.user_embeddings.find({'platform': 'xiaohongshu'}, {'dimension': 1, 'model': 1}))
    
    print(f"\n{'='*80}")
    print(f"验证Embedding维度")
    print(f"{'='*80}\n")
    
    dims = {}
    for e in embs:
        d = e.get('dimension')
        m = e.get('model', 'unknown')
        if d not in dims:
            dims[d] = {'count': 0, 'models': set()}
        dims[d]['count'] += 1
        dims[d]['models'].add(m)
    
    for dim, info in sorted(dims.items()):
        models_str = ', '.join(info['models'])
        print(f"  {dim}维: {info['count']}个 (模型: {models_str})")
    
    print(f"\n总计: {len(embs)} 个embedding")
    
    if len(dims) == 1 and 512 in dims:
        print("\n✅ 所有embedding已统一为512维！")
        return True
    else:
        print("\n⚠️  仍存在维度不一致")
        return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='统一所有embedding为512维')
    parser.add_argument('--check-only', action='store_true', help='仅检查不生成')
    parser.add_argument('--verify-only', action='store_true', help='仅验证维度')
    args = parser.parse_args()
    
    if args.verify_only:
        verify_embeddings()
    else:
        ready_users, missing_users = check_profiles()
        
        if not args.check_only:
            if ready_users:
                print(f"\n准备重新生成 {len(ready_users)} 个用户的embedding...")
                confirm = input("确认继续？(y/n): ")
                if confirm.lower() == 'y':
                    regenerate_embeddings(ready_users)
                    verify_embeddings()
                else:
                    print("\n已取消")
            else:
                print("\n⚠️  没有可以生成embedding的用户")
