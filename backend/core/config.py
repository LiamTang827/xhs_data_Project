"""
集中化配置管理 - 使用Pydantic Settings
统一管理所有环境变量和应用配置
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """应用配置类 - 使用Pydantic进行类型验证和环境变量管理"""
    
    # ========================================
    # 数据库配置
    # ========================================
    MONGO_URI: str = Field(
        ...,
        description="MongoDB连接URI（必需）"
    )
    DATABASE_NAME: str = Field(
        default="tikhub_xhs",
        description="MongoDB数据库名称"
    )
    
    # ========================================
    # API Keys配置
    # ========================================
    DEEPSEEK_API_KEY: str = Field(
        ...,
        description="DeepSeek API密钥（必需）"
    )
    DEEPSEEK_BASE_URL: str = Field(
        default="https://api.deepseek.com",
        description="DeepSeek API基础URL"
    )
    
    TIKHUB_TOKEN: Optional[str] = Field(
        default=None,
        description="TikHub API令牌（用于数据采集）"
    )
    TIKHUB_API_URL: str = Field(
        default="https://api.tikhub.io/api/v1/xiaohongshu/web/get_user_notes_v2",
        description="TikHub API端点"
    )
    
    # ========================================
    # 应用配置
    # ========================================
    ENV: str = Field(
        default="development",
        description="运行环境：development, staging, production"
    )
    DEBUG: bool = Field(
        default=True,
        description="调试模式"
    )
    API_VERSION: str = Field(
        default="2.0.0",
        description="API版本号"
    )
    
    # ========================================
    # 服务器配置
    # ========================================
    HOST: str = Field(
        default="0.0.0.0",
        description="服务器监听地址"
    )
    PORT: int = Field(
        default=5001,
        description="服务器端口"
    )
    
    # ========================================
    # CORS配置
    # ========================================
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="CORS允许的源"
    )
    
    # ========================================
    # AI模型配置
    # ========================================
    CHAT_MODEL: str = Field(
        default="deepseek-chat",
        description="聊天模型名称"
    )
    EMBEDDING_MODEL: str = Field(
        default="BAAI/bge-small-zh-v1.5",
        description="向量Embedding模型"
    )
    EMBEDDING_DIMENSION: int = Field(
        default=512,
        description="向量维度"
    )
    
    # ========================================
    # 日志配置
    # ========================================
    LOG_LEVEL: str = Field(
        default="INFO",
        description="日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )
    LOG_FILE: str = Field(
        default="backend_server.log",
        description="日志文件路径"
    )
    
    # ========================================
    # 存储配置（本地/S3）
    # ========================================
    STORAGE_TYPE: str = Field(
        default="local",
        description="存储类型：local, s3"
    )
    STORAGE_DIR: str = Field(
        default="/tmp/xhs_storage",
        description="本地存储目录"
    )
    S3_ENDPOINT: str = Field(
        default="",
        description="S3端点URL"
    )
    S3_ACCESS_KEY: str = Field(
        default="",
        description="S3访问密钥"
    )
    S3_SECRET_KEY: str = Field(
        default="",
        description="S3私钥"
    )
    S3_BUCKET: str = Field(
        default="",
        description="S3存储桶名称"
    )
    
    # ========================================
    # Pydantic Settings配置
    # ========================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # 忽略额外的环境变量
    )
    
    @field_validator("ENV")
    @classmethod
    def validate_environment(cls, v):
        """验证环境配置"""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"ENV must be one of {allowed}")
        return v
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v):
        """验证日志级别"""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v.upper()
    
    @property
    def is_production(self) -> bool:
        """判断是否为生产环境"""
        return self.ENV == "production"
    
    @property
    def is_development(self) -> bool:
        """判断是否为开发环境"""
        return self.ENV == "development"
    
    def get_mongo_db_url(self) -> str:
        """获取MongoDB连接URL（隐藏敏感信息用于日志）"""
        if "@" in self.MONGO_URI:
            parts = self.MONGO_URI.split("@")
            return f"mongodb://***@{parts[1]}"
        return "mongodb://***"


# ========================================
# 全局配置实例（单例模式）
# ========================================
def get_settings() -> Settings:
    """
    获取配置实例（懒加载）
    
    Returns:
        Settings: 配置对象
    """
    return Settings()


# 创建全局配置实例
settings = get_settings()


# ========================================
# 配置验证函数
# ========================================
def validate_config() -> bool:
    """
    验证配置完整性
    
    Returns:
        bool: 配置是否有效
    """
    try:
        # 检查必需的配置项
        required_fields = [
            ("MONGO_URI", settings.MONGO_URI),
            ("DEEPSEEK_API_KEY", settings.DEEPSEEK_API_KEY),
        ]
        
        missing_fields = []
        for field_name, field_value in required_fields:
            if not field_value:
                missing_fields.append(field_name)
        
        if missing_fields:
            print(f"❌ 缺少必需的配置项: {', '.join(missing_fields)}")
            return False
        
        print("✅ 配置验证通过")
        print(f"   - 环境: {settings.ENV}")
        print(f"   - 数据库: {settings.get_mongo_db_url()}")
        print(f"   - API版本: {settings.API_VERSION}")
        return True
        
    except Exception as e:
        print(f"❌ 配置验证失败: {e}")
        return False


if __name__ == "__main__":
    # 用于测试配置加载
    print("=" * 60)
    print("🔧 配置管理系统测试")
    print("=" * 60)
    validate_config()
    print("\n📋 当前配置:")
    print(f"   - DATABASE_NAME: {settings.DATABASE_NAME}")
    print(f"   - PORT: {settings.PORT}")
    print(f"   - DEBUG: {settings.DEBUG}")
    print(f"   - LOG_LEVEL: {settings.LOG_LEVEL}")
    print(f"   - EMBEDDING_MODEL: {settings.EMBEDDING_MODEL}")
