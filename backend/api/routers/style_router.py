"""
Style Generation API Router - 使用Service层
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict

from api.services import StyleGenerationService

router = APIRouter(prefix="/api/style", tags=["style"])

# 初始化服务（懒加载）
_style_service = None

# 创作者列表缓存（避免重复查询数据库）
_creators_cache = {
    "data": None,
    "timestamp": None,
    "ttl_seconds": 300  # 5分钟缓存
}


def get_style_service() -> StyleGenerationService:
    """获取风格生成服务实例"""
    global _style_service
    if _style_service is None:
        _style_service = StyleGenerationService()
    return _style_service


def get_cached_creators(platform):
    """获取缓存的创作者列表"""
    from datetime import datetime
    
    cache_key = f"creators_{platform}"
    if _creators_cache.get("data") and _creators_cache.get("platform") == platform:
        if _creators_cache.get("timestamp"):
            age = (datetime.now() - _creators_cache["timestamp"]).total_seconds()
            if age < _creators_cache["ttl_seconds"]:
                print(f"✅ 使用缓存的创作者列表 (age: {age:.1f}s)")
                return _creators_cache["data"]
    
    return None


def set_creators_cache(platform, data):
    """设置创作者列表缓存"""
    from datetime import datetime
    _creators_cache["data"] = data
    _creators_cache["platform"] = platform
    _creators_cache["timestamp"] = datetime.now()
    # data是 {success: bool, creators: []} 格式
    creator_count = len(data.get("creators", [])) if isinstance(data, dict) else 0
    print(f"✅ 已缓存创作者列表 ({creator_count} creators)")


def clear_creators_cache():
    """清除创作者列表缓存"""
    _creators_cache["data"] = None
    _creators_cache["timestamp"] = None
    _creators_cache["platform"] = None
    print("🗑️  已清除创作者列表缓存")


# =====================================================
# Request/Response Models
# =====================================================

class GenerateRequest(BaseModel):
    """生成请求模型"""
    creator_name: str
    user_input: str  # 改为user_input以匹配前端
    platform: str = "xiaohongshu"  # 可选字段，默认小红书
    prompt_type: str = "style_generation"  # 可选字段，默认使用风格生成模板


class GenerateResponse(BaseModel):
    """生成响应模型"""
    success: bool
    content: str
    error: str = ""


class CreatorInfo(BaseModel):
    """创作者信息"""
    id: str
    name: str


# =====================================================
# API Endpoints
# =====================================================

@router.get("/creators")
async def list_creators(platform: str = None):
    """
    获取可用的创作者列表
    
    Args:
        platform: 平台类型（可选，不指定则返回所有平台）
        
    Returns:
        创作者列表，包含success标志
    """
    try:
        service = get_style_service()
        
        # 如果未指定platform，返回所有平台的创作者
        if platform is None:
            # 尝试从缓存获取
            cached_data = get_cached_creators("all")
            if cached_data is not None:
                return cached_data
            
            all_creators = []
            for plat in ["xiaohongshu", "instagram"]:
                creators = service.get_available_creators(plat)
                # 为每个创作者添加platform字段
                for creator in creators:
                    creator["platform"] = plat
                all_creators.extend(creators)
            
            result = {
                "success": True,
                "creators": all_creators
            }
            
            # 缓存结果
            set_creators_cache("all", result)
            return result
        else:
            # 尝试从缓存获取
            cached_data = get_cached_creators(platform)
            if cached_data is not None:
                return cached_data
            
            creators = service.get_available_creators(platform)
            # 添加platform字段
            for creator in creators:
                creator["platform"] = platform
            
            result = {
                "success": True,
                "creators": creators
            }
            
            # 缓存结果
            set_creators_cache(platform, result)
            return result
            
    except Exception as e:
        import traceback
        error_detail = f"获取创作者列表失败: {str(e)}\n堆栈: {traceback.format_exc()}"
        print(f"❌ {error_detail}")
        raise HTTPException(status_code=500, detail=f"获取创作者列表失败: {str(e)}")


@router.post("/creators/clear-cache")
async def clear_cache():
    """清除创作者列表缓存"""
    clear_creators_cache()
    return {"success": True, "message": "缓存已清除"}


@router.post("/generate", response_model=GenerateResponse)
async def generate_style_content(request: GenerateRequest):
    """
    生成风格化内容
    
    Args:
        request: 生成请求（创作者名称、主题、平台、prompt类型）
        
    Returns:
        生成结果
    """
    try:
        service = get_style_service()
        result = await service.generate_content(
            creator_name=request.creator_name,
            user_topic=request.user_input,  # 使用user_input字段
            platform=request.platform,
            prompt_type=request.prompt_type  # 传递prompt_type
        )
        return result
    except Exception as e:
        return GenerateResponse(
            success=False,
            content="",
            error=f"生成失败: {str(e)}"
        )


@router.get("/prompts")
async def list_prompt_templates(platform: str = "xiaohongshu"):
    """
    获取可用的prompt模板列表
    
    Args:
        platform: 平台类型（默认xiaohongshu）
        
    Returns:
        prompt模板列表
    """
    try:
        from database.repositories import StylePromptRepository
        
        repo = StylePromptRepository()
        prompts = repo.get_all_prompts(platform)
        
        # 转换为前端需要的格式
        prompt_list = []
        for idx, prompt in enumerate(prompts):
            prompt_list.append({
                "id": prompt.get("prompt_type", f"prompt_{idx}"),  # 使用prompt_type作为唯一ID
                "prompt_type": prompt.get("prompt_type", ""),
                "name": prompt.get("name", ""),
                "description": prompt.get("description", "")
            })
        
        return {
            "success": True,
            "prompts": prompt_list
        }
    except Exception as e:
        import traceback
        error_detail = f"获取prompt模板失败: {str(e)}\n堆栈: {traceback.format_exc()}"
        print(f"❌ {error_detail}")
        raise HTTPException(status_code=500, detail=f"获取prompt模板失败: {str(e)}")


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "style_generation"}


@router.get("/debug/db")
async def debug_database():
    """调试数据库连接 - 仅用于排查问题"""
    try:
        from database.connection import get_database
        db = get_database()
        
        # 测试连接
        collections = db.list_collection_names()
        user_profiles_count = db.user_profiles.count_documents({})
        
        # 获取一个示例
        sample = db.user_profiles.find_one() if user_profiles_count > 0 else None
        
        return {
            "status": "connected",
            "database_name": db.name,
            "collections": collections,
            "user_profiles_count": user_profiles_count,
            "sample_nickname": sample.get("nickname") if sample else None
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }
