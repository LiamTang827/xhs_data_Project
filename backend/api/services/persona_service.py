"""
User Persona Analysis Service
用户画像分析服务
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import Counter

from database.connection import get_database
from database.models import (
    UserPersona,
    PersonaTag,
    ActivityPattern,
    AudienceProfile,
    PlatformType
)
from core.llm_gateway import get_llm_gateway


class PersonaAnalysisService:
    """用户画像分析服务"""
    
    def __init__(self):
        self.db = get_database()
        self.llm = get_llm_gateway()
        print("✅ PersonaAnalysisService 初始化完成")
    
    async def analyze_user_persona(
        self,
        user_id: str,
        platform: PlatformType = PlatformType.XIAOHONGSHU,
        force_refresh: bool = False
    ) -> UserPersona:
        """
        分析用户画像
        
        Args:
            user_id: 用户ID
            platform: 平台类型
            force_refresh: 是否强制刷新
            
        Returns:
            UserPersona对象
        """
        
        # 1️⃣ 检查缓存（如果不是强制刷新）
        if not force_refresh:
            cached_persona = self.db.user_personas.find_one({
                "user_id": user_id,
                "platform": platform.value
            })
            if cached_persona:
                # 检查是否过期（7天）
                if datetime.now() - cached_persona['updated_at'] < timedelta(days=7):
                    print(f"[Persona] 💰 使用缓存的用户画像: {user_id}")
                    return UserPersona(**cached_persona)
        
        print(f"[Persona] 🔍 开始分析用户画像: {user_id}")
        
        # 2️⃣ 获取用户基础数据
        user_profile = self.db.user_profiles.find_one({
            "user_id": user_id,
            "platform": platform.value
        })
        if not user_profile:
            raise ValueError(f"用户档案不存在: {user_id}")
        
        # 3️⃣ 获取用户笔记快照
        user_snapshot = self.db.user_snapshots.find_one({
            "user_id": user_id,
            "platform": platform.value
        })
        if not user_snapshot:
            raise ValueError(f"用户笔记快照不存在: {user_id}")
        
        # 4️⃣ 提取画像特征
        persona_tags = await self._extract_tags(user_profile, user_snapshot)
        content_themes = self._extract_themes(user_snapshot)
        style_keywords = self._extract_keywords(user_profile)
        activity_pattern = self._analyze_activity_pattern(user_snapshot)
        
        # 5️⃣ 使用LLM生成洞察
        ai_summary = await self._generate_ai_summary(
            user_profile,
            user_snapshot,
            persona_tags,
            content_themes
        )
        recommendations = await self._generate_recommendations(
            user_profile,
            activity_pattern
        )
        
        # 6️⃣ 构建UserPersona对象
        persona = UserPersona(
            user_id=user_id,
            platform=platform,
            nickname=user_profile.get('nickname', ''),
            persona_tags=persona_tags,
            content_themes=content_themes,
            style_keywords=style_keywords,
            value_proposition=user_profile.get('profile_data', {}).get('value_points', [''])[0] if user_profile.get('profile_data', {}).get('value_points') else "",
            activity_pattern=activity_pattern,
            content_quality_score=self._calculate_quality_score(user_snapshot),
            engagement_rate=self._calculate_engagement_rate(user_snapshot),
            audience_profile=AudienceProfile(),  # TODO: 需要更多数据
            ai_summary=ai_summary,
            recommendations=recommendations,
            version="1.0.0"
        )
        
        # 7️⃣ 保存到数据库
        self.db.user_personas.update_one(
            {"user_id": user_id, "platform": platform.value},
            {"$set": persona.model_dump()},
            upsert=True
        )
        
        print(f"[Persona] ✅ 用户画像分析完成: {user_id}")
        return persona
    
    async def _extract_tags(
        self,
        user_profile: Dict[str, Any],
        user_snapshot: Dict[str, Any]
    ) -> List[PersonaTag]:
        """提取用户画像标签"""
        tags = []
        
        # 从profile_data提取
        profile_data = user_profile.get('profile_data', {})
        topics = profile_data.get('topics', [])
        
        for topic in topics[:10]:  # 取前10个主题
            tags.append(PersonaTag(
                name=topic,
                weight=0.8,
                category="兴趣"
            ))
        
        # 从内容风格提取
        content_style = profile_data.get('content_style', '')
        if content_style:
            style_tags = content_style.split('、')
            for style in style_tags[:5]:
                tags.append(PersonaTag(
                    name=style.strip(),
                    weight=0.9,
                    category="风格"
                ))
        
        return tags
    
    def _extract_themes(self, user_snapshot: Dict[str, Any]) -> List[str]:
        """提取内容主题"""
        notes = user_snapshot.get('notes', [])
        all_text = ""
        
        for note in notes:
            all_text += note.get('title', '') + " " + note.get('desc', '') + " "
        
        # TODO: 使用NLP提取关键主题（当前简化版本）
        # 这里可以接入关键词提取算法（TF-IDF, TextRank等）
        return ["穿搭", "美妆", "生活方式"]  # 示例数据
    
    def _extract_keywords(self, user_profile: Dict[str, Any]) -> List[str]:
        """提取风格关键词"""
        profile_data = user_profile.get('profile_data', {})
        content_style = profile_data.get('content_style', '')
        
        # 简单分词提取
        keywords = re.findall(r'[\u4e00-\u9fa5]+', content_style)
        return keywords[:15]  # 取前15个
    
    def _analyze_activity_pattern(self, user_snapshot: Dict[str, Any]) -> ActivityPattern:
        """分析活跃时间段"""
        notes = user_snapshot.get('notes', [])
        
        # TODO: 需要笔记的发布时间数据
        # 当前返回默认值
        return ActivityPattern(
            peak_hours=[18, 19, 20, 21],  # 晚上6-9点
            active_weekdays=[1, 2, 3, 4, 5],  # 工作日
            posting_frequency="中"
        )
    
    def _calculate_quality_score(self, user_snapshot: Dict[str, Any]) -> float:
        """计算内容质量评分"""
        notes = user_snapshot.get('notes', [])
        if not notes:
            return 0.0
        
        total_score = 0
        for note in notes:
            likes = note.get('liked_count', 0)
            collects = note.get('collected_count', 0)
            comments = note.get('comment_count', 0)
            
            # 简单评分公式：点赞*1 + 收藏*2 + 评论*3
            score = likes + collects * 2 + comments * 3
            total_score += score
        
        avg_score = total_score / len(notes)
        # 归一化到0-100
        return min(100, avg_score / 10)
    
    def _calculate_engagement_rate(self, user_snapshot: Dict[str, Any]) -> float:
        """计算互动率"""
        notes = user_snapshot.get('notes', [])
        if not notes:
            return 0.0
        
        total_engagement = 0
        for note in notes:
            likes = note.get('liked_count', 0)
            collects = note.get('collected_count', 0)
            comments = note.get('comment_count', 0)
            total_engagement += (likes + collects + comments)
        
        # 简化版：假设平均曝光量为互动量的100倍
        avg_engagement = total_engagement / len(notes)
        return min(100, avg_engagement * 0.1)
    
    async def _generate_ai_summary(
        self,
        user_profile: Dict[str, Any],
        user_snapshot: Dict[str, Any],
        persona_tags: List[PersonaTag],
        content_themes: List[str]
    ) -> str:
        """使用LLM生成用户画像总结"""
        
        # 构建Prompt
        prompt = f"""
请基于以下数据，生成一份简洁的用户画像总结（150字以内）：

用户昵称：{user_profile.get('nickname', '未知')}
内容主题：{', '.join(content_themes)}
画像标签：{', '.join([tag.name for tag in persona_tags[:10]])}
笔记数量：{user_snapshot.get('total_notes', 0)}
内容风格：{user_profile.get('profile_data', {}).get('content_style', '未知')}

请用第三人称描述这位创作者的特点、风格和受众定位。
"""
        
        # 调用LLM
        summary = await self.llm.chat(
            prompt=prompt,
            model="deepseek-chat",
            max_tokens=300,
            temperature=0.7,
            use_cache=True
        )
        
        return summary.strip()
    
    async def _generate_recommendations(
        self,
        user_profile: Dict[str, Any],
        activity_pattern: ActivityPattern
    ) -> List[str]:
        """生成优化建议"""
        
        prompt = f"""
请为以下创作者提供3-5条具体的内容优化建议：

内容风格：{user_profile.get('profile_data', {}).get('content_style', '未知')}
发布频率：{activity_pattern.posting_frequency}
活跃时段：{activity_pattern.peak_hours}

请提供具体的、可执行的建议（每条不超过30字）。
"""
        
        recommendations_text = await self.llm.chat(
            prompt=prompt,
            model="deepseek-chat",
            max_tokens=400,
            temperature=0.8,
            use_cache=True
        )
        
        # 解析成列表
        recommendations = [
            line.strip().lstrip('1234567890.- ')
            for line in recommendations_text.split('\n')
            if line.strip() and len(line.strip()) > 5
        ]
        
        return recommendations[:5]
    
    def get_persona(self, user_id: str, platform: PlatformType = PlatformType.XIAOHONGSHU) -> Optional[UserPersona]:
        """获取用户画像（仅查询，不分析）"""
        persona_doc = self.db.user_personas.find_one({
            "user_id": user_id,
            "platform": platform.value
        })
        
        if persona_doc:
            return UserPersona(**persona_doc)
        return None
    
    def list_personas(self, platform: PlatformType = PlatformType.XIAOHONGSHU, limit: int = 50) -> List[UserPersona]:
        """列出所有用户画像"""
        personas = self.db.user_personas.find({
            "platform": platform.value
        }).limit(limit)
        
        return [UserPersona(**p) for p in personas]


# 全局服务实例（懒加载）
_persona_service = None

def get_persona_service() -> PersonaAnalysisService:
    """获取Persona服务单例"""
    global _persona_service
    if _persona_service is None:
        _persona_service = PersonaAnalysisService()
    return _persona_service
