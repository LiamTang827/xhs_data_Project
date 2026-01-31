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


def get_style_service() -> StyleGenerationService:
    """获取风格生成服务实例"""
    global _style_service
    if _style_service is None:
        _style_service = StyleGenerationService()
    return _style_service


# =====================================================
# Request/Response Models
# =====================================================

class GenerateRequest(BaseModel):
    """生成请求模型"""
    creator_name: str
    user_input: str  # 改为user_input以匹配前端
    platform: str = "xiaohongshu"  # 可选字段，默认小红书


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
    import traceback
    try:
        print(f"📡 [/api/style/creators] 收到请求, platform={platform}")
        
        # 尝试获取服务实例
        try:
            service = get_style_service()
            print("✅ StyleGenerationService 实例获取成功")
        except Exception as service_error:
            error_msg = f"服务初始化失败: {str(service_error)}"
            print(f"❌ {error_msg}")
            print(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail={
                    "error": error_msg,
                    "type": "service_initialization_error",
                    "traceback": traceback.format_exc()
                }
            )
        
        # 如果未指定platform，返回所有平台的创作者
        if platform is None:
            all_creators = []
            for plat in ["xiaohongshu", "instagram"]:
                print(f"🔍 正在查询 {plat} 平台的创作者...")
                creators = service.get_available_creators(plat)
                print(f"✅ {plat} 平台找到 {len(creators)} 个创作者")
                # 为每个创作者添加platform字段
                for creator in creators:
                    creator["platform"] = plat
                all_creators.extend(creators)
            
            print(f"📊 总共返回 {len(all_creators)} 个创作者")
            return {
                "success": True,
                "creators": all_creators
            }
        else:
            print(f"🔍 正在查询 {platform} 平台的创作者...")
            creators = service.get_available_creators(platform)
            print(f"✅ {platform} 平台找到 {len(creators)} 个创作者")
            # 添加platform字段
            for creator in creators:
                creator["platform"] = platform
            
            return {
                "success": True,
                "creators": creators
            }
    except HTTPException:
        # 重新抛出HTTPException
        raise
    except Exception as e:
        error_detail = f"获取创作者列表失败: {str(e)}"
        print(f"❌ {error_detail}")
        print(f"堆栈信息:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": error_detail,
                "type": "unknown_error",
                "traceback": traceback.format_exc()
            }
        )


@router.post("/generate", response_model=GenerateResponse)
async def generate_style_content(request: GenerateRequest):
    """
    生成风格化内容
    
    Args:
        request: 生成请求（创作者名称、主题、平台）
        
    Returns:
        生成结果
    """
    try:
        service = get_style_service()
        result = service.generate_content(
            creator_name=request.creator_name,
            user_topic=request.user_input,  # 使用user_input字段
            platform=request.platform
        )
        return result
    except Exception as e:
        return GenerateResponse(
            success=False,
            content="",
            error=f"生成失败: {str(e)}"
        )


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
