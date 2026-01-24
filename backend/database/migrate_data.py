"""
数据迁移脚本 - JSON to MongoDB
将本地JSON文件数据迁移到MongoDB
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

from database import (
    UserProfileRepository,
    UserSnapshotRepository,
    UserEmbeddingRepository,
    CreatorNetworkRepository,
    StylePromptRepository,
)


class DataMigration:
    """数据迁移管理器"""
    
    def __init__(self, base_dir: str = "/Users/tangliam/Projects/xhs_data_Project/data-analysiter"):
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "data"
        
        # 初始化仓库
        self.profile_repo = UserProfileRepository()
        self.snapshot_repo = UserSnapshotRepository()
        self.embedding_repo = UserEmbeddingRepository()
        self.network_repo = CreatorNetworkRepository()
        self.prompt_repo = StylePromptRepository()
        
        print("✅ 数据迁移器初始化完成")
    
    def migrate_user_profiles(self):
        """迁移用户档案数据"""
        print("\n" + "="*60)
        print("📦 开始迁移用户档案数据...")
        print("="*60)
        
        profiles_dir = self.data_dir / "user_profiles"
        if not profiles_dir.exists():
            print("❌ user_profiles目录不存在")
            return
        
        migrated = 0
        skipped = 0
        
        for json_file in profiles_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
                
                nickname = json_file.stem  # 文件名作为昵称
                
                # 检查是否已存在
                existing = self.profile_repo.get_profile_by_nickname(nickname)
                if existing:
                    print(f"⚠️  {nickname} 已存在，跳过")
                    skipped += 1
                    continue
                
                # 准备数据
                mongo_data = {
                    "platform": "xiaohongshu",
                    "user_id": profile_data.get("user_id", ""),
                    "nickname": nickname,
                    "profile_data": profile_data,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                
                # 插入数据库
                doc_id = self.profile_repo.create_profile(mongo_data)
                print(f"✅ {nickname} 迁移成功 (ID: {doc_id})")
                migrated += 1
                
            except Exception as e:
                print(f"❌ {json_file.name} 迁移失败: {e}")
        
        print(f"\n📊 用户档案迁移完成: 成功 {migrated}, 跳过 {skipped}")
    
    def migrate_user_snapshots(self):
        """迁移用户快照数据"""
        print("\n" + "="*60)
        print("📦 开始迁移用户快照数据...")
        print("="*60)
        
        snapshots_dir = self.data_dir / "snapshots"
        if not snapshots_dir.exists():
            print("❌ snapshots目录不存在")
            return
        
        migrated = 0
        skipped = 0
        
        for json_file in snapshots_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    snapshot_data = json.load(f)
                
                # 新格式：user和notes在顶层
                if 'user' in snapshot_data and 'user_id' in snapshot_data['user']:
                    user_id = snapshot_data['user']['user_id']
                    notes = snapshot_data.get('notes', [])
                # 旧格式：data.user.user_id
                elif 'data' in snapshot_data and 'user' in snapshot_data['data']:
                    user_id = snapshot_data['data']['user'].get('user_id', '')
                    notes = snapshot_data['data'].get('notes', [])
                else:
                    print(f"⚠️  {json_file.name} 格式不正确，跳过")
                    continue
                
                if not user_id:
                    print(f"⚠️  {json_file.name} 缺少user_id，跳过")
                    continue
                
                # 检查是否已存在
                existing = self.snapshot_repo.get_by_user_id(user_id)
                if existing:
                    # 如果新数据有更多笔记，更新
                    existing_notes_count = len(existing.get('notes', []))
                    if len(notes) > existing_notes_count:
                        print(f"⚠️  {user_id} 快照已存在，更新 ({existing_notes_count} -> {len(notes)} 笔记)")
                        self.snapshot_repo.update_snapshot(user_id, "xiaohongshu", notes)
                        migrated += 1
                    else:
                        print(f"⚠️  {user_id} 快照已存在，跳过")
                        skipped += 1
                    continue
                
                # 准备数据
                mongo_data = {
                    "platform": "xiaohongshu",
                    "user_id": user_id,
                    "notes": notes,
                    "total_notes": len(notes),
                    "created_at": datetime.now()
                }
                
                # 插入数据库
                doc_id = self.snapshot_repo.create_snapshot(mongo_data)
                print(f"✅ {user_id} 快照迁移成功 (笔记数: {len(notes)}, ID: {doc_id})")
                migrated += 1
                
            except Exception as e:
                print(f"❌ {json_file.name} 迁移失败: {e}")
        
        print(f"\n📊 快照迁移完成: 成功 {migrated}, 跳过 {skipped}")
    
    def migrate_user_embeddings(self):
        """迁移用户embeddings数据"""
        print("\n" + "="*60)
        print("📦 开始迁移用户embeddings...")
        print("="*60)
        
        analyses_dir = self.data_dir / "analyses"
        if not analyses_dir.exists():
            print("❌ analyses目录不存在")
            return
        
        migrated = 0
        skipped = 0
        
        for json_file in analyses_dir.glob("*__embedding.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    embedding_data = json.load(f)
                
                # 从文件名提取user_id
                user_id = json_file.stem.replace('__embedding', '')
                
                # 检查是否已存在
                existing = self.embedding_repo.get_by_user_id(user_id)
                if existing:
                    print(f"⚠️  {user_id} embedding已存在，跳过")
                    skipped += 1
                    continue
                
                # 准备数据
                mongo_data = {
                    "platform": "xiaohongshu",
                    "user_id": user_id,
                    "embedding": embedding_data.get("embedding", []),
                    "model": "BAAI/bge-small-zh-v1.5",
                    "dimension": 512,
                    "created_at": datetime.now()
                }
                
                # 插入数据库
                doc_id = self.embedding_repo.create_embedding(mongo_data)
                print(f"✅ {user_id} embedding迁移成功 (ID: {doc_id})")
                migrated += 1
                
            except Exception as e:
                print(f"❌ {json_file.name} 迁移失败: {e}")
        
        print(f"\n📊 Embeddings迁移完成: 成功 {migrated}, 跳过 {skipped}")
    
    def migrate_creator_network(self):
        """迁移创作者网络数据"""
        print("\n" + "="*60)
        print("📦 开始迁移创作者网络...")
        print("="*60)
        
        network_file = self.data_dir / "creators_data.json"
        if not network_file.exists():
            print("❌ creators_data.json文件不存在")
            return
        
        try:
            with open(network_file, 'r', encoding='utf-8') as f:
                network_data = json.load(f)
            
            # 检查是否已存在最新网络
            existing = self.network_repo.get_latest_network()
            if existing:
                print("⚠️  已存在网络数据，是否覆盖？(y/n)")
                # 为了自动化，这里默认跳过
                print("⚠️  跳过迁移（已存在）")
                return
            
            # 准备数据
            mongo_data = {
                "platform": "xiaohongshu",
                "network_data": network_data,
                "created_at": datetime.now()
            }
            
            # 插入数据库
            doc_id = self.network_repo.create_network(mongo_data)
            print(f"✅ 创作者网络迁移成功 (ID: {doc_id})")
            print(f"   - 创作者数: {len(network_data.get('creators', []))}")
            print(f"   - 关系数: {len(network_data.get('edges', []))}")
            
        except Exception as e:
            print(f"❌ 创作者网络迁移失败: {e}")
    
    def migrate_style_prompts(self):
        """迁移风格生成提示词模板"""
        print("\n" + "="*60)
        print("📦 开始迁移风格提示词模板...")
        print("="*60)
        
        # 默认的风格生成提示词模板
        default_prompt = {
            "platform": "xiaohongshu",
            "prompt_type": "style_generation",
            "name": "小红书风格文案生成",
            "template": """你是一位经验丰富的小红书内容创作者，擅长模仿不同博主的风格进行创作。

【被模仿者档案】
昵称：{nickname}
内容主题：{topics}
内容风格：{content_style}
价值点：{value_points}

【参考笔记】（以下是该博主的典型笔记）
{sample_notes}

【任务】
请以这位博主的风格，为主题"{user_topic}"创作一篇小红书笔记。

【要求】
1. 文案风格要高度贴近该博主的特点
2. 保持该博主常用的表达方式和语气
3. 体现该博主的价值观和内容侧重点
4. 标题要吸引人，正文要有亮点
5. 适当添加emoji增加活力
6. 最后给出3-5个相关话题标签

【输出格式】
标题：[在这里输出标题]

正文：
[在这里输出正文内容]

话题标签：
#标签1 #标签2 #标签3
""",
            "variables": [
                "nickname",
                "topics",
                "content_style",
                "value_points",
                "sample_notes",
                "user_topic"
            ],
            "description": "用于生成小红书风格文案的提示词模板",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        try:
            # 检查是否已存在
            existing = self.prompt_repo.get_by_type("style_generation")
            if existing:
                print("⚠️  风格生成提示词已存在，跳过")
                return
            
            # 插入数据库
            doc_id = self.prompt_repo.create_prompt(default_prompt)
            print(f"✅ 风格提示词模板迁移成功 (ID: {doc_id})")
            
        except Exception as e:
            print(f"❌ 提示词迁移失败: {e}")
    
    def run_all(self):
        """执行所有迁移任务"""
        print("\n" + "🚀"*30)
        print(" 数据迁移 - JSON to MongoDB")
        print("🚀"*30)
        
        self.migrate_user_profiles()
        self.migrate_user_snapshots()
        self.migrate_user_embeddings()
        self.migrate_creator_network()
        self.migrate_style_prompts()
        
        print("\n" + "="*60)
        print("✅ 所有数据迁移完成！")
        print("="*60)
        
        # 显示统计信息
        self.show_statistics()
    
    def show_statistics(self):
        """显示数据库统计信息"""
        print("\n📊 数据库统计信息：")
        print("-" * 60)
        
        try:
            profile_count = self.profile_repo.count()
            snapshot_count = self.snapshot_repo.count()
            embedding_count = self.embedding_repo.count()
            network_count = self.network_repo.count()
            prompt_count = self.prompt_repo.count()
            
            print(f"  用户档案 (user_profiles): {profile_count} 条")
            print(f"  用户快照 (user_snapshots): {snapshot_count} 条")
            print(f"  用户Embeddings (user_embeddings): {embedding_count} 条")
            print(f"  创作者网络 (creator_networks): {network_count} 条")
            print(f"  提示词模板 (style_prompts): {prompt_count} 条")
            
        except Exception as e:
            print(f"❌ 统计信息获取失败: {e}")


def main():
    """主函数"""
    print("\n🎯 数据迁移脚本")
    print("将本地JSON数据迁移到MongoDB\n")
    
    # 创建迁移器
    migrator = DataMigration()
    
    # 执行迁移
    migrator.run_all()
    
    print("\n💡 提示：数据已迁移到MongoDB，现在可以更新业务逻辑代码使用数据库层了！")


if __name__ == "__main__":
    main()
