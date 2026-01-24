#!/usr/bin/env python3
"""
数据分析管道 - 从MongoDB读取数据，调用DeepSeek API生成用户画像和embedding
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from FlagEmbedding import FlagModel

# 加载环境变量
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# 添加项目根目录到路径
sys.path.insert(0, str(BASE_DIR))

from database import UserSnapshotRepository, UserProfileRepository, UserEmbeddingRepository
from processors.analyze import analyze_user_profile


def process_user(user_id: str, embedding_model: FlagModel = None):
    """
    处理单个用户的完整流程
    
    Args:
        user_id: 用户ID
        embedding_model: FlagModel实例，用于生成embedding
    """
    print(f"\n{'='*60}")
    print(f"🎯 处理用户: {user_id}")
    print(f"{'='*60}")
    
    # 1. 从MongoDB读取snapshot
    print("\n📥 步骤 1: 从MongoDB读取数据...")
    snapshot_repo = UserSnapshotRepository()
    snapshot = snapshot_repo.get_by_user_id(user_id, platform="xiaohongshu")
    
    if not snapshot:
        print(f"❌ 未找到用户 {user_id} 的数据")
        return False
    
    notes = snapshot.get('notes', [])
    if not notes:
        print(f"❌ 用户 {user_id} 没有笔记数据")
        return False
    
    # 提取用户信息
    user_info = None
    if notes and 'user' in notes[0]:
        user_info = notes[0]['user']
    
    if not user_info:
        print(f"❌ 无法提取用户信息")
        return False
    
    nickname = user_info.get('nickname', user_id)
    print(f"✅ 找到用户: {nickname}")
    print(f"   - 笔记数: {len(notes)}")
    print(f"   - 粉丝数: {user_info.get('fans', 0)}")
    
    # 2. 调用DeepSeek API分析
    print("\n🤖 步骤 2: 调用DeepSeek API分析用户画像...")
    try:
        profile_data = analyze_user_profile(user_info, notes[:20], embedding_model)  # 只用前20条笔记，传入embedding_model
        
        if not profile_data:
            print(f"❌ DeepSeek API分析失败")
            return False
        
        print(f"✅ 分析完成")
        print(f"   - 内容主题: {len(profile_data.get('content_topics', []))} 个")
        print(f"   - 内容风格: {len(profile_data.get('content_style', []))} 个")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. 保存到MongoDB
    print("\n💾 步骤 3: 保存到MongoDB...")
    
    # 保存 user_profile
    profile_repo = UserProfileRepository()
    
    profile_doc = {
        'platform': 'xiaohongshu',
        'user_id': user_id,
        'nickname': nickname,
        'profile_data': profile_data,
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    existing_profile = profile_repo.get_by_user_id(user_id)
    if existing_profile:
        profile_repo.update_profile(user_id, 'xiaohongshu', profile_data)
        print(f"✅ 已更新 user_profiles")
    else:
        profile_repo.create_profile(profile_doc)
        print(f"✅ 已创建 user_profiles")
    
    # 保存 embedding
    if 'user_style_embedding' in profile_data:
        embedding_repo = UserEmbeddingRepository()
        
        embedding_doc = {
            'platform': 'xiaohongshu',
            'user_id': nickname,  # 使用nickname作为ID（因为user_id可能为空）
            'embedding': profile_data['user_style_embedding'],
            'model': 'text-embedding-3-small',
            'dimension': len(profile_data['user_style_embedding']),
            'created_at': datetime.now()
        }
        
        existing_embedding = embedding_repo.get_by_user_id(nickname)
        if existing_embedding:
            embedding_repo.update_embedding(nickname, 'xiaohongshu', profile_data['user_style_embedding'])
            print(f"✅ 已更新 user_embeddings")
        else:
            embedding_repo.create_embedding(embedding_doc)
            print(f"✅ 已创建 user_embeddings")
    
    print(f"\n✨ 用户 {nickname} 处理完成！")
    return True


def process_all_users():
    """处理所有用户"""
    print("\n🚀 开始处理所有用户...")
    
    # 预加载embedding模型（避免重复加载）
    print("\n📦 加载embedding模型...")
    embedding_model = FlagModel(
        "BAAI/bge-small-zh-v1.5",
        query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
        use_fp16=True
    )
    print("✅ 模型加载完成")
    
    snapshot_repo = UserSnapshotRepository()
    snapshots = snapshot_repo.collection.find({'platform': 'xiaohongshu'})
    
    user_ids = [snap['user_id'] for snap in snapshots if snap.get('user_id')]
    
    print(f"📊 找到 {len(user_ids)} 个用户")
    
    success_count = 0
    for i, user_id in enumerate(user_ids, 1):
        print(f"\n[{i}/{len(user_ids)}] ", end="")
        if process_user(user_id, embedding_model):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"✅ 处理完成！成功: {success_count}/{len(user_ids)}")
    print(f"{'='*60}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="数据分析管道")
    parser.add_argument("--user_id", help="只处理指定用户")
    parser.add_argument("--all", action="store_true", help="处理所有用户")
    
    args = parser.parse_args()
    
    if args.user_id:
        # 单个用户处理时也预加载模型
        print("\n📦 加载embedding模型...")
        embedding_model = FlagModel(
            "BAAI/bge-small-zh-v1.5",
            query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
            use_fp16=True
        )
        print("✅ 模型加载完成")
        process_user(args.user_id, embedding_model)
    elif args.all:
        process_all_users()
    else:
        print("请指定参数:")
        print("  --user_id <user_id>  处理单个用户")
        print("  --all                处理所有用户")


if __name__ == "__main__":
    main()
