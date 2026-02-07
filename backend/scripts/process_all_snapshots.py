#!/usr/bin/env python3
"""
重新处理所有user_snapshots中的用户
为每个有笔记快照但没有profile的用户生成完整的profile和embedding
"""

import os
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
load_dotenv(project_root / '.env')

from database import (
    UserProfileRepository,
    UserSnapshotRepository,
    UserEmbeddingRepository
)

# 导入分析器
sys.path.insert(0, str(Path(__file__).parent))
from analyzer import analyze_user_profile
from FlagEmbedding import FlagModel


def process_all_snapshots():
    """处理所有user_snapshots中的用户"""
    
    print("="*60)
    print("🔄 开始处理所有user_snapshots中的用户")
    print("="*60)
    
    # 加载embedding模型
    print("\n📦 加载embedding模型...")
    embedding_model = FlagModel(
        "BAAI/bge-small-zh-v1.5",
        query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
        use_fp16=True
    )
    print("✅ 模型加载完成")
    
    snapshot_repo = UserSnapshotRepository()
    profile_repo = UserProfileRepository()
    embedding_repo = UserEmbeddingRepository()
    
    # 获取所有snapshots
    snapshots = list(snapshot_repo.collection.find({'platform': 'xiaohongshu'}))
    print(f"\n📊 找到 {len(snapshots)} 个用户快照")
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for i, snapshot in enumerate(snapshots, 1):
        user_id = snapshot['user_id']
        notes = snapshot.get('notes', [])
        
        if not notes:
            print(f"\n[{i}/{len(snapshots)}] ⚠️  {user_id}: 没有笔记数据，跳过")
            skip_count += 1
            continue
        
        # 从第一条笔记提取用户信息
        user_info = notes[0].get('user', {})
        nickname = user_info.get('nickname', user_id)
        
        print(f"\n{'='*60}")
        print(f"[{i}/{len(snapshots)}] 处理: {nickname}")
        print(f"  user_id: {user_id}")
        print(f"  笔记数: {len(notes)}")
        
        # 检查是否已有profile
        existing_profile = profile_repo.get_by_user_id(user_id)
        if existing_profile:
            print(f"  ⚠️  已存在profile，跳过")
            skip_count += 1
            continue
        
        try:
            # 调用DeepSeek API分析
            print(f"  🤖 调用DeepSeek API分析...")
            profile_data = analyze_user_profile(user_info, notes[:20], embedding_model)
            
            if not profile_data:
                print(f"  ❌ 分析失败")
                error_count += 1
                continue
            
            # 计算总互动数
            total_likes = sum(note.get('likes', 0) for note in notes)
            total_collects = sum(note.get('collected_count', 0) for note in notes)
            total_comments = sum(note.get('comments_count', 0) for note in notes)
            total_shares = sum(note.get('share_count', 0) for note in notes)
            
            engagement = {
                'likes': total_likes,
                'collects': total_collects,
                'comments': total_comments,
                'shares': total_shares
            }
            
            # 确保profile_data中有engagement字段
            if 'profile_data' not in profile_data or not isinstance(profile_data, dict):
                # profile_data就是我们需要的数据
                pass
            
            # 添加engagement数据
            profile_data['engagement'] = engagement
            
            print(f"  ✅ 分析完成")
            print(f"     话题数: {len(profile_data.get('content_topics', []))}")
            print(f"     话题: {', '.join(profile_data.get('content_topics', [])[:3])}")
            print(f"     总互动: ❤️{total_likes} 💾{total_collects} 💬{total_comments} 🔗{total_shares}")
            
            # 保存profile
            profile_doc = {
                'platform': 'xiaohongshu',
                'user_id': user_id,
                'nickname': nickname,
                'profile_data': profile_data,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            profile_repo.create_profile(profile_doc)
            print(f"  ✅ 已保存 user_profiles")
            
            # 保存embedding
            if 'user_style_embedding' in profile_data:
                embedding_doc = {
                    'platform': 'xiaohongshu',
                    'user_id': user_id,
                    'embedding': profile_data['user_style_embedding'],
                    'model': 'BAAI/bge-small-zh-v1.5',
                    'dimension': len(profile_data['user_style_embedding']),
                    'created_at': datetime.now()
                }
                
                embedding_repo.create_embedding(embedding_doc)
                print(f"  ✅ 已保存 user_embeddings")
            
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            import traceback
            traceback.print_exc()
            error_count += 1
    
    # 总结
    print(f"\n{'='*60}")
    print("📊 处理完成！")
    print(f"{'='*60}")
    print(f"总共: {len(snapshots)} 个用户")
    print(f"成功: {success_count}")
    print(f"跳过: {skip_count}")
    print(f"失败: {error_count}")
    print(f"{'='*60}")


if __name__ == '__main__':
    process_all_snapshots()
