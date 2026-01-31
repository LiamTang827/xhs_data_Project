"""
Data Models & Schemas
MongoDB数据模型定义
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class PlatformType(str, Enum):
    """平台类型枚举"""
    XIAOHONGSHU = "xiaohongshu"
    INSTAGRAM = "instagram"


# =====================================================
# 1. User Profile Models
# =====================================================

class UserProfileData(BaseModel):
    """用户档案数据"""
    topics: List[str] = Field(default_factory=list, description="内容主题")
    content_style: str = Field(default="", description="内容风格")
    value_points: List[str] = Field(default_factory=list, description="价值点")
    engagement: Dict[str, Any] = Field(default_factory=dict, description="互动数据")


class UserProfile(BaseModel):
    """用户档案完整模型"""
    platform: PlatformType
    user_id: str
    nickname: str
    profile_data: UserProfileData
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# =====================================================
# 2. User Snapshot Models
# =====================================================

class NoteData(BaseModel):
    """笔记数据"""
    note_id: str = Field(alias="id")
    title: str = Field(default="")
    desc: str = Field(default="")
    liked_count: int = Field(default=0, alias="likes")
    collected_count: int = Field(default=0, alias="collects")
    comment_count: int = Field(default=0, alias="comments")
    share_count: int = Field(default=0, alias="shares")
    
    class Config:
        populate_by_name = True


class UserSnapshot(BaseModel):
    """用户笔记快照"""
    platform: PlatformType
    user_id: str
    notes: List[Dict[str, Any]]  # 原始笔记数据
    total_notes: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.now)


# =====================================================
# 3. User Embedding Models
# =====================================================

class UserEmbedding(BaseModel):
    """用户向量embedding"""
    user_id: str
    platform: PlatformType
    embedding: List[float]  # 512维向量
    model: str = "BAAI/bge-small-zh-v1.5"
    dimension: int = 512
    created_at: datetime = Field(default_factory=datetime.now)


# =====================================================
# 4. Creator Network Models
# =====================================================

class CreatorNode(BaseModel):
    """创作者节点"""
    id: str
    name: str
    platform: PlatformType
    category: str = "creator"


class CreatorEdge(BaseModel):
    """创作者关系边"""
    source: str
    target: str
    similarity: float
    label: str = ""


class CreatorNetwork(BaseModel):
    """创作者网络"""
    platform: PlatformType
    network_data: Dict[str, Any]  # {creators: [...], edges: [...]}
    created_at: datetime = Field(default_factory=datetime.now)


# =====================================================
# 5. Style Prompt Models
# =====================================================

class StylePromptType(str, Enum):
    """提示词类型"""
    STYLE_GENERATION = "style_generation"
    CONTENT_ANALYSIS = "content_analysis"


class StylePrompt(BaseModel):
    """风格生成提示词模板"""
    platform: PlatformType
    prompt_type: StylePromptType
    name: str = Field(description="模板名称")
    template: str = Field(description="提示词模板")
    variables: List[str] = Field(default_factory=list, description="模板变量")
    description: str = Field(default="", description="模板描述")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# =====================================================
# 6. Platform Config Models
# =====================================================

class PlatformAPIConfig(BaseModel):
    """平台API配置"""
    base_url: str
    endpoints: Dict[str, str]
    headers: Dict[str, str] = Field(default_factory=dict)


class PlatformConfig(BaseModel):
    """平台配置"""
    platform: PlatformType
    api_config: PlatformAPIConfig
    auth_token: str = Field(default="", description="认证令牌")
    enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# =====================================================
# 7. User Persona Models（NEW）
# =====================================================

class PersonaTag(BaseModel):
    """用户画像标签"""
    name: str = Field(description="标签名称")
    weight: float = Field(default=1.0, description="标签权重 (0-1)")
    category: str = Field(default="", description="标签分类：兴趣/风格/价值观")


class ActivityPattern(BaseModel):
    """活跃时间段分析"""
    peak_hours: List[int] = Field(default_factory=list, description="活跃小时（0-23）")
    active_weekdays: List[int] = Field(default_factory=list, description="活跃星期（1-7）")
    posting_frequency: str = Field(default="unknown", description="发布频率：高/中/低")


class AudienceProfile(BaseModel):
    """受众画像"""
    age_range: str = Field(default="", description="年龄段：18-24, 25-34等")
    gender_ratio: Dict[str, float] = Field(default_factory=dict, description="性别比例：{male: 0.3, female: 0.7}")
    interests: List[str] = Field(default_factory=list, description="受众兴趣标签")


class UserPersona(BaseModel):
    """用户画像模型（User Persona）"""
    user_id: str = Field(description="用户ID")
    platform: PlatformType = Field(default=PlatformType.XIAOHONGSHU)
    nickname: str = Field(default="")
    
    # 核心画像数据
    persona_tags: List[PersonaTag] = Field(default_factory=list, description="用户画像标签")
    content_themes: List[str] = Field(default_factory=list, description="内容主题列表")
    style_keywords: List[str] = Field(default_factory=list, description="风格关键词")
    value_proposition: str = Field(default="", description="价值主张（一句话概括）")
    
    # 行为分析
    activity_pattern: ActivityPattern = Field(default_factory=ActivityPattern, description="活跃时间段")
    content_quality_score: float = Field(default=0.0, description="内容质量评分 (0-100)")
    engagement_rate: float = Field(default=0.0, description="互动率")
    
    # 受众分析
    audience_profile: AudienceProfile = Field(default_factory=AudienceProfile, description="受众画像")
    
    # AI生成的洞察
    ai_summary: str = Field(default="", description="AI生成的用户画像总结")
    recommendations: List[str] = Field(default_factory=list, description="优化建议")
    
    # 元数据
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: str = Field(default="1.0.0", description="画像版本号")

