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
        获取可用的创作者列表（从creator_networks获取，避免user_profiles超时）
        
        Args:
            platform: 平台类型
            
        Returns:
            创作者列表 [{"nickname": "xxx", "user_id": "xxx", "topics": [...], "followers": 0, ...}, ...]
        """
        try:
            from database.repositories import CreatorNetworkRepository
            
            # 使用CreatorNetworkRepository获取网络数据（更快，有索引）
            network_repo = CreatorNetworkRepository()
            network = network_repo.get_latest_network(platform)
            
            if not network:
                print(f"⚠️  未找到平台 {platform} 的网络数据")
                return []
            
            # 从network_data中提取creators
            network_data = network.get("network_data", {})
            creators_from_network = network_data.get("creators", [])
            
            if not creators_from_network:
                print(f"⚠️  网络数据中没有创作者")
                return []
            
            # 从 user_snapshots 读取真实的笔记数和互动数（唯一数据源）
            snapshot_data = {}  # uid -> {note_count, total_engagement}
            try:
                from database.connection import get_database
                db = get_database()
                for snap in db.user_snapshots.find({}, {'user_id': 1, 'notes': 1}):
                    uid = snap['user_id']
                    notes = snap.get('notes', [])
                    total = 0
                    for n in notes:
                        total += (n.get('likes', 0) or 0) + (n.get('collected_count', 0) or 0) + \
                                 (n.get('comments_count', 0) or 0) + (n.get('share_count', 0) or 0)
                    snapshot_data[uid] = {'note_count': len(notes), 'total_engagement': total}
            except Exception:
                pass
            
            # 转换格式以匹配前端期望
            creators = []
            for creator in creators_from_network:
                uid = creator.get("id", "")
                snap = snapshot_data.get(uid, {})
                creators.append({
                    "nickname": creator.get("name", "未知"),
                    "name": creator.get("name", "未知"),
                    "user_id": uid,
                    "topics": creator.get("topics", []),
                    "followers": creator.get("followers", 0),
                    "total_engagement": snap.get("total_engagement", 0),
                    "note_count": snap.get("note_count", 0),
                    "avatar": creator.get("avatar", ""),
                    "style": "创作者",
                    "platform": platform
                })
            
            print(f"✅ 从creator_networks成功加载 {len(creators)} 个创作者")
            return creators
            
        except Exception as e:
            print(f"❌ 获取创作者列表失败: {e}")
            import traceback
            traceback.print_exc()
            # 确保返回空列表而不是 None
            return []
    
    def get_available_creators_from_profiles(self, platform: str = "xiaohongshu") -> List[Dict[str, Any]]:
        """
        获取可用的创作者列表（从user_profiles + snapshots，备用方案）
        
        Args:
            platform: 平台类型
            
        Returns:
            创作者列表 [{"nickname": "xxx", "user_id": "xxx", "topics": [...], "followers": 0, ...}, ...]
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
                
                # 从profile的stats中获取粉丝和互动数据（多层fallback）
                # 注意：数据库中的字段名是 'fans' 而不是 'followers'
                stats = profile.get("stats", {})
                followers = stats.get("fans") or stats.get("followers")
                total_engagement = stats.get("total_engagement")
                note_count = stats.get("note_count", 0) or 0
                
                # 如果stats中没有数据，尝试从basic_info中获取
                if not followers:
                    followers = profile.get("basic_info", {}).get("fans") or profile.get("basic_info", {}).get("followers")
                if not total_engagement:
                    total_engagement = profile.get("basic_info", {}).get("total_engagement")
                
                # 如果还是没有，尝试从其他位置（profile_data等）
                if not followers:
                    followers = profile.get("profile_data", {}).get("fans") or profile.get("profile_data", {}).get("followers")
                if not total_engagement:
                    total_engagement = profile.get("profile_data", {}).get("total_engagement")
                
                # 最后转换为整数，确保不是None或0
                followers = int(followers) if followers else 0
                total_engagement = int(total_engagement) if total_engagement else 0
                
                # 如果还是为0，添加日志用于debug
                if followers == 0:
                    print(f"⚠️  Warning: 创作者 {nickname} ({user_id}) 的粉丝数为0")
                
                creators.append({
                    "nickname": nickname,
                    "name": nickname,  # 兼容前缀的name字段
                    "user_id": user_id,
                    "topics": topics,
                    "followers": followers,
                    "total_engagement": total_engagement,
                    "note_count": note_count,
                    "avatar": profile.get("basic_info", {}).get("avatar", ""),
                    "style": "创作者",
                    "platform": platform
                })
            
            print(f"✅ 成功加载 {len(creators)} 个创作者")
            return creators
            
        except Exception as e:
            print(f"❌ 获取创作者列表失败: {e}")
            import traceback
            traceback.print_exc()
            # 确保返回空列表而不是 None
            return []
    
    def load_creator_profile(self, creator_name: str, platform: str = "xiaohongshu") -> Optional[Dict[str, Any]]:
        """
        加载创作者档案（从creator_networks读取，避免user_profiles超时）
        
        Args:
            creator_name: 创作者昵称
            platform: 平台类型
            
        Returns:
            档案数据 or None
        """
        try:
            from database.repositories import CreatorNetworkRepository
            
            # 从creator_networks获取网络数据
            network_repo = CreatorNetworkRepository()
            network = network_repo.get_latest_network(platform)
            
            if not network:
                print(f"⚠️  未找到平台 {platform} 的网络数据")
                return None
            
            # 从network_data中查找指定创作者
            network_data = network.get("network_data", {})
            creators = network_data.get("creators", [])
            
            creator_data = None
            for c in creators:
                if c.get("name") == creator_name:
                    creator_data = c
                    break
            
            if not creator_data:
                print(f"⚠️  未找到创作者档案: {creator_name}")
                return None
            
            # 构造profile_data格式（兼容原有代码）
            profile = {
                "nickname": creator_data.get("name", ""),
                "topics": creator_data.get("topics", []),
                "content_style": creator_data.get("contentForm", "创作者"),
                "primary_track": creator_data.get("primaryTrack", ""),
                "description": creator_data.get("desc", ""),
                "followers": creator_data.get("followers", 0),
                "engagement": creator_data.get("totalEngagement", 0),
                "value_points": f"{creator_data.get('primaryTrack', '')}, {', '.join(creator_data.get('topics', [])[:3])}"
            }
            
            print(f"✅ 从creator_networks加载档案: {creator_name}")
            return profile
            
        except Exception as e:
            print(f"❌ 加载创作者档案失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def load_creator_notes(self, creator_name: str, platform: str = "xiaohongshu", limit: int = 5) -> List[Dict[str, Any]]:
        """
        加载创作者的笔记样本（从creator_networks的indexSeries读取，避免user_snapshots超时）
        
        Args:
            creator_name: 创作者昵称
            platform: 平台类型
            limit: 返回笔记数量
            
        Returns:
            笔记列表
        """
        try:
            from database.repositories import CreatorNetworkRepository
            
            # 从creator_networks获取网络数据
            network_repo = CreatorNetworkRepository()
            network = network_repo.get_latest_network(platform)
            
            if not network:
                print(f"⚠️  未找到平台 {platform} 的网络数据")
                return []
            
            # 从network_data中查找指定创作者
            network_data = network.get("network_data", {})
            creators = network_data.get("creators", [])
            
            creator_data = None
            for c in creators:
                if c.get("name") == creator_name:
                    creator_data = c
                    break
            
            if not creator_data:
                print(f"⚠️  未找到创作者: {creator_name}")
                return []
            
            # 从indexSeries获取笔记样本
            index_series = creator_data.get("indexSeries", [])
            if not index_series:
                print(f"⚠️  创作者没有笔记样本: {creator_name}")
                return []
            
            # 转换格式（只使用标题）
            notes = []
            for item in index_series[:limit]:
                notes.append({
                    "title": item.get("title", ""),
                    "note_id": item.get("note_id", ""),
                    "create_time": item.get("ts", 0),
                    "desc": f"（标题）{item.get('title', '')}"  # 只有标题，没有正文
                })
            
            print(f"✅ 从creator_networks加载 {len(notes)} 个笔记标题")
            return notes
            
        except Exception as e:
            print(f"❌ 加载创作者笔记失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def build_style_prompt(
        self,
        creator_profile: Dict[str, Any],
        sample_notes: List[Dict[str, Any]],
        user_topic: str,
        creator_name: str,
        prompt_type: str = "style_generation"
    ) -> str:
        """
        构建风格生成提示词
        
        Args:
            creator_profile: 创作者档案
            sample_notes: 样本笔记
            user_topic: 用户输入的主题
            creator_name: 创作者昵称
            prompt_type: prompt模板类型
            
        Returns:
            完整的提示词
        """
        try:
            from database.repositories import UserSnapshotRepository
            from datetime import datetime, timedelta
            import re
            from collections import Counter
            
            # 根据prompt_type选择相应的模板方法
            template_method = {
                "style_xiaohongshu": self._get_xiaohongshu_template,
                "style_generic": self._get_generic_template,
                "style_amway": self._get_amway_template,
                "style_tutorial": self._get_tutorial_template,
                "style_story": self._get_story_template,
                "style_trending": self._get_trending_template,
                "style_founder_content": self._get_founder_content_template,
            }.get(prompt_type)
            
            if template_method:
                template = template_method()
            else:
                print(f"⚠️  未找到提示词模板 {prompt_type}，使用默认模板")
                template = self._get_default_template()
            
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
        platform: str = "xiaohongshu",
        prompt_type: str = "style_generation"
    ) -> Dict[str, Any]:
        """
        生成风格化内容
        
        Args:
            creator_name: 创作者昵称
            user_topic: 用户主题
            platform: 平台类型
            prompt_type: prompt模板类型
            
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
            print(f"🔨 构建提示词（使用模板: {prompt_type}）...")
            prompt = self.build_style_prompt(
                creator_profile,
                sample_notes,
                user_topic,
                creator_name,
                prompt_type
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
    
    def _get_founder_content_template(self) -> str:
        """创始人社媒内容专用模板"""
        return """你是一位顶级创始人个人品牌内容顾问，帮助创业者撰写高质量的社媒内容。

【创始人档案】
昵称：{nickname}
内容主题：{topics}
个人风格：{content_style}
核心价值观：{value_points}

【参考内容】（该创始人过往发布的典型内容）
{sample_notes}

【创作要求】

1. 【开头】用具体场景或真实细节切入，不要空话
   - 可以是一个观察、一个问题、或一个现场瞬间
   - 用第一人称，体现创始人的真实语境

2. 【核心内容】提炼1-2个核心洞察
   - 体现创始人的独特判断力
   - 结合行业数据或实际案例支撑观点
   - 避免"我们很兴奋"这类空话
   - 避免堆砌行业黑话

3. 【结尾】有温度的收尾
   - 可以是真诚的感谢、思考，或温度的CTA
   - 例如：欢迎交流、招人公告、寻找合作伙伴

【写作风格】
- 语气专业但自然，像在和行业同行聊天
- 不用夸张词汇，表达克制而有力
- 避免自卖自夸，而是通过具体事实说话
- 长度控制在180-320字
- 不用或极少用emoji（如果在LinkedIn尤其要少用）

【内容主题】{user_topic}

【最终输出】
请生成一条创始人的社媒内容，体现该创始人的专业性、洞察力和温度。
内容应该：
- 有具体的细节或数据支撑
- 能让读者感受到创始人的思考深度
- 自然引导业内专家、投资人、潜在用户或合作伙伴的互动

"""

    def _get_xiaohongshu_template(self) -> str:
        """小红书爆款风格模板 - 强调热点、话题、视觉"""
        return """你是一位小红书顶级内容运营师，擅长打造爆款内容。

【创作者档案】
昵称：{nickname}
内容主题：{topics}
风格特点：{content_style}

【参考笔记】（该博主的爆款作品特征）
{sample_notes}

【创作目标】
为主题"{user_topic}"创作一篇小红书爆款笔记，模仿该博主的风格。

【核心要点】
1. 【标题】必须吸睛 - 前3个字决定用户是否点开
   - 使用数字/问句/惊叹句效果好
   - 包含潜在流量词（如：避坑、必买、建议、干货等）
   - 暗示内容价值或情感触发

2. 【正文】关键是"分层阅读"
   - 第一段：问题/痛点/制造悬念
   - 中间部分：干货/解决方案（3-5个要点，用列表/序号）
   - 最后段：总结/鸡汤/CTA引导点赞

3. 【话题标签】5-8个
   - 必须包含热门话题标签
   - 结合创作者常用的垂直领域标签
   - 避免太冷门的标签

4. 【排版】
   - 大量使用emoji（但不要过度）
   - 关键词用特殊符号突出: ✨💡⚡️
   - 分段清晰，每段2-3行

【禁区】
- 不要显得过于商业化/推广感
- 不要空话/鸡汤过多
- 配图文字要对应（虽然你看不到图片，但要注意逻辑）

【输出格式】
标题：[吸睛的标题，包含流量词]

[正文内容，做好分段排版，多用emoji]

话题标签：#标签1 #标签2 #标签3 #标签4 #标签5
"""

    def _get_generic_template(self) -> str:
        """通用风格模仿 - 保持原汁原味"""
        return """你的任务是以某位内容创作者的风格进行创作，保持其独特的表达方式。

【创作者档案】
昵称：{nickname}
常见主题：{topics}
个人风格：{content_style}
核心价值：{value_points}

【参考笔记】
{sample_notes}

【创作要求】
为题目"{user_topic}"创作内容，严格模仿该创作者的风格。

【风格还原】
1. 表达方式：模仿创作者的用词习惯、句式结构
2. 逻辑思路：采用创作者常用的论证方法
3. 感情基调：保留创作者的态度和立场
4. 细节特征：融入创作者的标志性表达、emoji习惯、排版风格

【内容要求】
- 言之有物：提供实际的信息和角度
- 条理清晰：易于理解和记忆
- 保真度高：让读者能察觉到这是该创作者的风格
- 长度适中：400-600字

【输出】
直接输出笔记内容，包含标题、主文和话题标签：

标题：[标题]

[主文内容]

话题标签：#标签1 #标签2 #标签3
"""

    def _get_amway_template(self) -> str:
        """种草推荐型 - 强调产品价值、对比、理由充分"""
        return """你是一位顶级产品测评博主和种草达人。

【创作者档案】
昵称：{nickname}
频道主题：{topics}
推荐风格：{content_style}

【参考笔记】（该博主的推荐作品）
{sample_notes}

【任务】
用该博主的风格，为"{user_topic}"создать种草笔记。

【种草的黄金法则】
1. 【开篇吸引】
   - 制造需求感：你可能不知道但其实很需要这个
   - 制造对比：用过好和不好的对比
   - 真实推荐感：分享个人使用体验

2. 【产品亮点】（重点）
   - 罗列3-5个核心卖点
   - 每个点都要有"为什么这很重要"的解释
   - 使用具体例子或数据说话

3. 【应用场景】
   - 描述什么样的人适合买
   - 解释在什么情况下最好用
   - 对比替代品为什么更好

4. 【价格/获取】
   - 首先诚实评价价格是否值
   - 提供购买链接或渠道建议
   - 分享是否有优惠信息

5. 【诚实缺点】
   - 说出1-2个缺点来增加可信度
   - 解释为什么这些缺点能接受
   - 强化"总体很值"的结论

【排版必须】
- 使用数字列表强调卖点
- 多用✨⭐️💯等评分emoji
- "👍 推荐指数"这类小元素
- 最后一句是强硬的CTA："已下单/入手可复制这个链接"

【禁区】
- 不能显得太硬广
- 不能夸大其词
- 数字必须真实可信

【输出】
标题：[吸睛的种草标题]

[详细的种草内容，包含产品对比、价格、使用场景等]

话题标签：#种草 #推荐 #产品测评 #[相关标签]
"""

    def _get_tutorial_template(self) -> str:
        """干货教程型 - 知识输出、可实操、有逻辑"""
        return """你是一位干货创作者和知识传播者，专注于输出有价值的教程和指南。

【创作者档案】
昵称：{nickname}
知识领域：{topics}
讲解风格：{content_style}

【参考笔记】（该博主的干货作品）
{sample_notes}

【目标】
以该博主的风格，为"{user_topic}"制作一份详细的干货笔记。

【干货笔记的结构】
1. 【开场】开门见山
   - 明确说明能学到什么
   - 为什么这知识很重要/有用
   - 需要多少时间学会

2. 【核心内容】分步骤讲解
   - 用序号清晰列举步骤或要点（通常3-7个）
   - 每个步骤都要explain"为什么"和"怎么做"
   - 穿插实例或对比，让抽象变具体
   - 关键概念标黑或用emoji标注

3. 【常见误区】增加深度
   - 指出新手常犯的2-3个错误
   - 解释为什么会出错
   - 给出正确做法

4. 【进阶/延伸】提升价值
   - 介绍更深层的应用
   - 或者相关的进阶内容
   - 或者如何举一反三

5. 【总结】可记忆的核心
   - 3句话总结核心要点
   - 鼓励立即行动

【写作要求】
- 逻辑严密：前后呼应
- 循序渐进：从易到难
- 实操性强：读者看完想立即用
- 避免啰嗦：干货不等于长篇大论

【排版】
- 大量用数字列表
- 关键词加粗或***包围***
- 用"💡 Tips："开头给建议
- 用对比表格展示区别

【输出】
标题：[干货标题，体现学习收获：如何/方法/指南等]

[详细的分步骤教程内容]

核心要点总结：
✓ 要点1
✓ 要点2  
✓ 要点3

话题标签：#干货 #教程 #[领域标签] #[相关技能]
"""

    def _get_story_template(self) -> str:
        """情感故事型 - 代入感强、引发共鸣、有转折"""
        return """你是一位情感内容创作者和故事讲述高手。

【创作者档案】
昵称：{nickname}
故事风格：{content_style}
常见主题：{topics}

【参考笔记】（该博主的情感作品）
{sample_notes}

【任务】
用该博主的风格，围绕"{user_topic}"讲述一个打动人心的故事。

【故事框架】
1. 【开篇】制造代入感
   - 从细节入手，让读者"看到"画面
   - 描写当时的心情或环境氛围
   - 第一句要能吸引人继续看下去

2. 【冲突/转折点】故事的核心
   - 描述发生了什么事，为什么引发了改变
   - 表达当时的情绪波动
   - 可以是挫折、惊喜、领悟等

3. 【成长/领悟】给予启发
   - 解释这件事怎样改变了你的想法
   - 分享从中学到的人生道理
   - 避免过度鸡汤，要真诚

4. 【回应】制造共鸣
   - 问出一个能引发读者思考的问题
   - 或者邀请读者分享类似经历
   - 强化情感共鸣

【情感表达】
- 使用具体的感官描写：看到/听到/感受到...
- 真实的内心独白："当时我想..."
- 适时的自嘲或温暖幽默
- 适度的emoji表达情绪（不要过多）

【禁区】
- 过度煽情或夸张
- 过度说教
- 没有具体情节细节，只讲道理

【篇幅】
400-600字最佳，足以展开故事又不显冗长

【输出】
标题：[情感标题，能唤起感受：如"这才是真正的..."、"我终于明白了..."]

[完整的故事内容，包含细节、转折、领悟全过程]

话题标签：#故事 #成长 #感悟 #[情感关键词]
"""

    def _get_trending_template(self) -> str:
        """潮流热点型 - 快速响应、独特视角、容易引发讨论"""
        return """你是一位热点评论家和趋势观察者。

【创作者档案】
昵称：{nickname}
评论风格：{content_style}
关注领域：{topics}

【参考笔记】（该博主的热点评论）
{sample_notes}

【目标】
针对热点话题"{user_topic}"，以该博主的风格进行评论和观察。

【热点内容的黄金法则】
1. 【快速切入】
   - 第一句直接说明"这件事是什么"
   - 用最简洁的方式让不了解的人快速get到
   - 引出你的独特观点

2. 【独特角度】核心竞争力
   - 不能说大众都在说的废话
   - 提出一个新鲜视角或counterargument
   - 用数据/案例/逻辑支撑你的观点

3. 【深度分析】
   - 分析这个热点背后的原因
   - 可能的后续发展或影响
   - 为什么你的观点更有洞见

4. 【态度表达】
   - 清楚表达你的立场：支持/反对/中立深思
   - 通过具体分析而不是情绪化表达
   - 尊重不同观点的同时坚持己见

5. 【引发讨论】
   - 提出1-2个问题邀请读者思考
   - 或者给出建议方向
   - 强调这话题值得更多人讨论

【语气特征】
- 犀利但不刻薄
- 理性分析但有温度
- 敢于说出不同声音
- 不跟风，敢质疑

【排版】
- 观点清晰分段
- 用 💭 / 🤔 / ⚡️ 等icon标注关键观点
- 数据/事实用[]方括号框起来
- 结尾用加粗强调核心结论

【禁区】
- 单纯转发八卦，要有观点
- 极端或不尊重他人的言论
- 没有事实基础的瞎说

【输出】
标题：[热点评论标题，体现你的观点立场]

[详细的热点分析和评论，包含新角度、数据、逻辑推导]

核心观点：[用一句话总结你的核心立场]

话题标签：#热点 #观察 #[热点关键词] #[相关话题]
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
