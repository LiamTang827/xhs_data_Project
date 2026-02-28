#!/usr/bin/env python3
"""
完整流程：为12个384维用户生成profile_data，然后统一为512维embedding
"""

import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root / "backend"))
sys.path.insert(0, str(project_root / "collectors" / "xiaohongshu"))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv(project_root / '.env')

from database.connection import get_database
from database import UserEmbeddingRepository, UserProfileRepository
from FlagEmbedding import FlagModel
import numpy as np
from datetime import datetime
import os

# 导入analyzer
from analyzer import analyze_user_profile

def step1_generate_profiles():
    """步骤1：为12个用户生成profile_data"""
    print("\n" + "="*80)
    print("步骤1：生成Profile_data（调用DeepSeek API）")
    print("="*80 + "\n")
    
    db = get_database()
    
    # 获取384维用户
    embs_384 = list(db.user_embeddings.find({'model': 'topic_hash_v1'}))
    
    success = 0
    failed = 0
    skipped = 0
    
    for i, e in enumerate(embs_384, 1):
        uid = e.get('user_id')
        
        # 检查是否已有profile
        profile = db.user_profiles.find_one({'user_id': uid})
        if not profile:
            print(f"[{i}/{len(embs_384)}] ❌ {uid[:16]}: 无profile记录，跳过")
            skipped += 1
            continue
        
        nickname = profile.get('nickname', uid[:16])
        
        # 检查是否已有user_style
        pd = profile.get('profile_data', {})
        user_style = pd.get('user_style', {})
        
        if user_style and isinstance(user_style, dict) and user_style.get('persona'):
            print(f"[{i}/{len(embs_384)}] ✅ {nickname}: 已有user_style，跳过")
            skipped += 1
            continue
        
        print(f"[{i}/{len(embs_384)}] 🔄 {nickname}: 开始生成profile...")
        
        try:
            # 获取用户的笔记快照
            snapshot = db.user_snapshots.find_one({'user_id': uid, 'platform': 'xiaohongshu'})
            
            if not snapshot:
                print(f"  ⚠️  无笔记快照，跳过")
                skipped += 1
                continue
            
            notes = snapshot.get('notes', [])
            if not notes:
                print(f"  ⚠️  笔记为空，跳过")
                skipped += 1
                continue
            
            # 提取用户信息
            user_info = notes[0].get('user', {})
            if not user_info:
                user_info = {
                    'nickname': nickname,
                    'userid': uid,
                    'fans': 0
                }
            
            print(f"  📝 分析 {len(notes)} 条笔记...")
            
            # 加载embedding模型（用于analyzer）
            model = FlagModel(
                "BAAI/bge-small-zh-v1.5",
                query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
                use_fp16=True
            )
            
            # 调用DeepSeek分析
            profile_data = analyze_user_profile(user_info, notes[:50], model)
            
            if not profile_data:
                print(f"  ❌ 分析失败")
                failed += 1
                continue
            
            # 更新profile_data
            db.user_profiles.update_one(
                {'user_id': uid, 'platform': 'xiaohongshu'},
                {
                    '$set': {
                        'profile_data': profile_data,
                        'updated_at': datetime.now()
                    }
                }
            )
            
            print(f"  ✅ Profile生成成功")
            print(f"     话题: {', '.join(profile_data.get('content_topics', [])[:3])}")
            
            success += 1
            
        except Exception as e:
            print(f"  ❌ 失败: {e}")
            failed += 1
    
    print(f"\n{'='*80}")
    print(f"步骤1完成: 成功{success}, 失败{failed}, 跳过{skipped}")
    print(f"{'='*80}\n")
    
    return success > 0

def step2_regenerate_embeddings():
    """步骤2：使用bge-small-zh-v1.5重新生成512维embedding"""
    print("\n" + "="*80)
    print("步骤2：生成512维Embedding（bge-small-zh-v1.5）")
    print("="*80 + "\n")
    
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
        return False
    
    db = get_database()
    embedding_repo = UserEmbeddingRepository()
    
    # 获取384维用户
    embs_384 = list(db.user_embeddings.find({'model': 'topic_hash_v1'}))
    
    success = 0
    failed = 0
    skipped = 0
    
    for i, e in enumerate(embs_384, 1):
        uid = e.get('user_id')
        
        # 获取profile
        profile = db.user_profiles.find_one({'user_id': uid})
        if not profile:
            print(f"[{i}/{len(embs_384)}] ❌ {uid[:16]}: 无profile，跳过")
            skipped += 1
            continue
        
        nickname = profile.get('nickname', uid[:16])
        pd = profile.get('profile_data', {})
        
        # 检查是否有content_topics或user_style
        content_topics = pd.get('content_topics', [])
        user_style = pd.get('user_style', {})
        
        # 构造embedding输入文本
        embedding_text = ""
        
        if user_style and isinstance(user_style, dict):
            # 旧格式：使用user_style
            persona = user_style.get('persona', '')
            tone = user_style.get('tone', '')
            interests = user_style.get('interests', [])
            
            if isinstance(interests, list):
                interests_text = ' '.join(interests)
            else:
                interests_text = str(interests)
            
            embedding_text = f"{persona} {tone} {interests_text}".strip()
        elif content_topics:
            # 新格式：使用content_topics
            if isinstance(content_topics, list):
                embedding_text = ' '.join(content_topics)
            else:
                embedding_text = str(content_topics)
        
        if not embedding_text:
            print(f"[{i}/{len(embs_384)}] ❌ {nickname}: 无可用数据，跳过")
            skipped += 1
            continue
        
        print(f"[{i}/{len(embs_384)}] 🔄 {nickname}")
        
        try:
            print(f"  输入: {embedding_text[:60]}...")
            
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
    print(f"步骤2完成: 成功{success}, 失败{failed}, 跳过{skipped}")
    print(f"{'='*80}\n")
    
    return success > 0

def step3_verify_embeddings():
    """步骤3：验证所有embedding是否统一为512维"""
    print("\n" + "="*80)
    print("步骤3：验证Embedding维度")
    print("="*80 + "\n")
    
    db = get_database()
    embs = list(db.user_embeddings.find({'platform': 'xiaohongshu'}, {'dimension': 1, 'model': 1}))
    
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

def main():
    print("\n" + "="*80)
    print("🚀 统一Embedding为512维（完整流程）")
    print("="*80)
    
    # 检查环境变量
    if not os.environ.get('DEEPSEEK_API_KEY'):
        print("\n❌ 错误：未设置DEEPSEEK_API_KEY环境变量")
        return
    
    print("\n执行计划:")
    print("  1. 为12个用户生成profile_data（调用DeepSeek API，约¥0.047）")
    print("  2. 使用bge-small-zh-v1.5生成512维embedding（本地模型，无成本）")
    print("  3. 验证所有embedding统一为512维")
    
    confirm = input("\n确认执行？(y/n): ")
    if confirm.lower() != 'y':
        print("已取消")
        return
    
    # 执行步骤1
    if not step1_generate_profiles():
        print("\n⚠️  步骤1未成功生成任何profile，继续执行步骤2...")
    
    # 执行步骤2
    if not step2_regenerate_embeddings():
        print("\n❌ 步骤2失败，请检查错误信息")
        return
    
    # 执行步骤3
    if step3_verify_embeddings():
        print("\n🎉 全部完成！所有embedding已统一为512维")
        print("\n下一步: 可以测试刷新网络功能")
        print("  cd backend && python3 scripts/regenerate_creator_networks.py")
    else:
        print("\n⚠️  仍有部分embedding维度不一致，请检查")

if __name__ == '__main__':
    main()
