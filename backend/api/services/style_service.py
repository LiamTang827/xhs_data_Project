"""
Style Generation Service
风格生成业务逻辑层 - 从数据库读取数据
"""

from typing import Dict, List, Any, Optional

from core.config import settings
from core.llm_gateway import get_llm_gateway
from database import (
    UserProfileRepository,
    UserSnapshotRepository,
    StylePromptRepository
)


class StyleGenerationService:
    """风格生成服务"""
    
    def __init__(self):
        # 初始化数据仓库
        self.profile_repo = UserProfileRepository()
        self.snapshot_repo = UserSnapshotRepository()
        self.prompt_repo = StylePromptRepository()
        
        # 使用LLM Gateway替代直接调用OpenAI
        self.llm = get_llm_gateway()
        
        print("✅ StyleGenerationService 初始化完成（已启用LLM Gateway）")
    
    def get_available_creators(self, platform: str = "xiaohongshu") -> List[Dict[str, Any]]:
        """
        获取可用的创作者列表（从snapshots提取最新#hashtags）
        
        Args:
            platform: 平台类型
            
        Returns:
            创作者列表 [{"name": "xxx", "user_id": "xxx", "topics": [...], "style": "xxx"}, ...]
        """
        try:
            from database.repositories import UserSnapshotRepository
            from datetime import datetime, timedelta
            import re
            from collections import Counter
            
            profiles = self.profile_repo.get_all_profiles(platform=platform)
            snapshot_repo = UserSnapshotRepository()
            
            creators = []
            for profile in profiles:
                nickname = profile.get("basic_info", {}).get("nickname") or profile.get("nickname", "未知")
                user_id = profile.get("user_id")
                
                if not user_id:
                    continue
                
                # 从snapshot中提取最近30天的#hashtags
                snapshot = snapshot_repo.get_by_user_id(user_id, platform)
                topics = []
                
                if snapshot:
                    notes = snapshot.get('notes', [])
                    # 过滤最近30天
                    cutoff_time = datetime.now() - timedelta(days=30)
                    cutoff_ts = int(cutoff_time.timestamp())
                    recent_notes = [n for n in notes if n.get('create_time', 0) >= cutoff_ts]
                    
                    # 提取hashtags
                    hashtags = []
                    for note in recent_notes[:20]:
                        title = note.get('title', '') or ''
                        desc = note.get('desc') or ''
                        text = title + ' ' + desc
                        tags = re.findall(r'#([\w\u4e00-\u9fa5]+)', text)
                        hashtags.extend(tags)
                    
                    if hashtags:
                        tag_count = Counter(hashtags)
                        topics = [tag for tag, count in tag_count.most_common(8)]
                
                if not topics:
                    topics = ["综合内容"]
                
                creators.append({
                    "name": nickname,
                    "user_id": user_id,
                    "topics": topics,
                    "style": "创作者"
                })
            
            return creators
            
            return creators
            
        except Exception as e:
            print(f"❌ 获取创作者列表失败: {e}")
            import traceback
            traceback.print_exc()
            # 确保返回空列表而不是 None
            return []
    
    def load_creator_profile(self, creator_name: str, platform: str = "xiaohongshu") -> Optional[Dict[str, Any]]:
        """
        加载创作者档案
        
        Args:
            creator_name: 创作者昵称
            platform: 平台类型
            
        Returns:
            档案数据 or None
        """
        try:
            profile = self.profile_repo.get_profile_by_nickname(creator_name, platform)
            if not profile:
                print(f"⚠️  未找到创作者档案: {creator_name}")
                return None
            
            # 返回profile_data部分
            return profile.get("profile_data", {})
            
        except Exception as e:
            print(f"❌ 加载创作者档案失败: {e}")
            return None
    
    def load_creator_notes(self, creator_name: str, platform: str = "xiaohongshu", limit: int = 5) -> List[Dict[str, Any]]:
        """
        加载创作者的笔记样本
        
        Args:
            creator_name: 创作者昵称
            platform: 平台类型
            limit: 返回笔记数量
            
        Returns:
            笔记列表
        """
        try:
            # 先获取user_id
            profile = self.profile_repo.get_profile_by_nickname(creator_name, platform)
            if not profile:
                print(f"⚠️  未找到创作者: {creator_name}")
                return []
            
            user_id = profile.get("user_id", "")
            if not user_id:
                print(f"⚠️  创作者缺少user_id: {creator_name}")
                return []
            
            # 获取笔记
            notes = self.snapshot_repo.get_notes(user_id, platform, limit)
            
            # 🔧 优化：压缩笔记内容以减少token消耗
            # 只保留每篇笔记的前500字，而不是全文
            compressed_notes = []
            for note in notes:
                compressed_note = note.copy()
                desc = note.get('desc', note.get('description', ''))
                if len(desc) > 500:
                    compressed_note['desc'] = desc[:500] + '...'  # 截断并添加省略号
                    print(f"📉 笔记已压缩: {len(desc)} → 500 字符")
                compressed_notes.append(compressed_note)
            
            return compressed_notes
            
        except Exception as e:
            print(f"❌ 加载创作者笔记失败: {e}")
            return []
    
    def build_style_prompt(
        self,
        creator_profile: Dict[str, Any],
        sample_notes: List[Dict[str, Any]],
        user_topic: str,
        creator_name: str
    ) -> str:
        """
        构建风格生成提示词
        
        Args:
            creator_profile: 创作者档案
            sample_notes: 样本笔记
            user_topic: 用户输入的主题
            creator_name: 创作者昵称
            
        Returns:
            完整的提示词
        """
        try:
            from database.repositories import UserSnapshotRepository
            from datetime import datetime, timedelta
            import re
            from collections import Counter
            
            # 从数据库获取提示词模板
            prompt_data = self.prompt_repo.get_by_type("style_generation")
            if not prompt_data:
                print("⚠️  未找到提示词模板，使用默认模板")
                template = self._get_default_template()
            else:
                template = prompt_data.get("template", self._get_default_template())
            
            # 从 snapshot 提取真实的 #hashtags（最近30天）
            profile = self.profile_repo.get_profile_by_nickname(creator_name, "xiaohongshu")
            topics = []
            if profile:
                user_id = profile.get("user_id")
                if user_id:
                    snapshot_repo = UserSnapshotRepository()
                    snapshot = snapshot_repo.get_by_user_id(user_id, "xiaohongshu")
                    if snapshot:
                        notes = snapshot.get('notes', [])
                        # 过滤最近30天
                        cutoff_time = datetime.now() - timedelta(days=30)
                        cutoff_ts = int(cutoff_time.timestamp())
                        recent_notes = [n for n in notes if n.get('create_time', 0) >= cutoff_ts]
                        
                        # 提取hashtags
                        hashtags = []
                        for note in recent_notes[:20]:
                            title = note.get('title', '') or ''
                            desc = note.get('desc') or ''
                            text = title + ' ' + desc
                            tags = re.findall(r'#([\w\u4e00-\u9fa5]+)', text)
                            hashtags.extend(tags)
                        
                        if hashtags:
                            tag_count = Counter(hashtags)
                            topics = [tag for tag, count in tag_count.most_common(8)]
            
            topics_text = ", ".join(topics) if topics else "综合内容"
            
            # 提取档案信息（保留兼容性）
            content_style = creator_profile.get("content_style", "")
            value_points = "\n".join([f"- {vp}" for vp in creator_profile.get("value_points", [])])
            
            # 格式化样本笔记
            sample_notes_text = ""
            for i, note in enumerate(sample_notes, 1):
                title = note.get("title", "")
                desc = note.get("desc", note.get("description", ""))
                sample_notes_text += f"\n【笔记{i}】\n标题：{title}\n内容：{desc}\n"
            
            # 填充模板，并在prompt中明确提示使用这些热点标签
            hot_topics_instruction = ""
            if topics:
                hot_topics_instruction = f"\n\n⚠️ 重要：请在生成的内容中自然融入以下热点话题标签（这些是{creator_name}最近30天爆款笔记中的真实标签）：\n{', '.join(['#' + t for t in topics[:5]])}\n请在合适的地方使用这些标签，增加内容的热度和曝光度。"
            
            # 填充模板
            prompt = template.format(
                nickname=creator_name,
                topics=topics_text,
                content_style=content_style,
                value_points=value_points,
                sample_notes=sample_notes_text,
                user_topic=user_topic
            ) + hot_topics_instruction
            
            return prompt
            
        except Exception as e:
            print(f"❌ 构建提示词失败: {e}")
            return self._get_fallback_prompt(creator_name, user_topic)
    
    async def generate_content(
        self,
        creator_name: str,
        user_topic: str,
        platform: str = "xiaohongshu"
    ) -> Dict[str, Any]:
        """
        生成风格化内容
        
        Args:
            creator_name: 创作者昵称
            user_topic: 用户主题
            platform: 平台类型
            
        Returns:
            生成结果 {"success": bool, "content": str, "error": str}
        """
        try:
            # 1. 加载创作者档案
            print(f"📥 加载创作者档案: {creator_name}")
            creator_profile = self.load_creator_profile(creator_name, platform)
            if not creator_profile:
                return {
                    "success": False,
                    "content": "",
                    "error": f"未找到创作者档案: {creator_name}"
                }
            
            # 2. 加载笔记样本（优化：减少数量以节省token）
            print(f"📥 加载笔记样本...")
            sample_notes = self.load_creator_notes(creator_name, platform, limit=3)
            if not sample_notes:
                print("⚠️  未找到笔记样本，将基于档案信息生成")
            
            # 3. 构建提示词
            print(f"🔨 构建提示词...")
            prompt = self.build_style_prompt(
                creator_profile,
                sample_notes,
                user_topic,
                creator_name
            )
            
            # 4. 使用LLM Gateway调用API（自动缓存+限流）
            print(f"🤖 调用LLM Gateway生成内容（启用缓存）...")
            generated_content = await self.llm.chat(
                prompt=prompt,
                model="deepseek-chat",
                max_tokens=2000,
                temperature=0.7,
                use_cache=True  # 启用缓存
            )
            
            print(f"✅ 内容生成成功")
            
            return {
                "success": True,
                "content": generated_content,
                "error": ""
            }
            
        except Exception as e:
            error_msg = f"生成失败: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "content": "",
                "error": error_msg
            }
    
    def _get_default_template(self) -> str:
        """获取默认提示词模板"""
        return """你是一位经验丰富的小红书内容创作者，擅长模仿不同博主的风格进行创作。

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
"""
    
    def _get_fallback_prompt(self, creator_name: str, user_topic: str) -> str:
        """获取降级提示词"""
        return f"""请以"{creator_name}"的风格，为主题"{user_topic}"创作一篇小红书笔记。

要求：
1. 标题吸引人
2. 内容真实有价值
3. 添加适当的emoji
4. 给出3-5个话题标签

输出格式：
标题：[标题]
正文：[正文]
话题标签：#标签1 #标签2
"""
