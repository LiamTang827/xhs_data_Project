"""
User Persona API Router
用户画像API路由
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel

from database.models import UserPersona, PlatformType
from api.services.persona_service import get_persona_service


router = APIRouter(prefix="/persona", tags=["User Persona"])


# =====================================================
# Request/Response Models
# =====================================================

class PersonaAnalyzeRequest(BaseModel):
    """画像分析请求"""
    user_id: str
    platform: PlatformType = PlatformType.XIAOHONGSHU
    force_refresh: bool = False


class PersonaAnalyzeResponse(BaseModel):
    """画像分析响应"""
    success: bool
    persona: Optional[UserPersona] = None
    message: str = ""


class PersonaListResponse(BaseModel):
    """画像列表响应"""
    success: bool
    personas: list[UserPersona]
    total: int
    message: str = ""


# =====================================================
# API Endpoints
# =====================================================

@router.post("/analyze", response_model=PersonaAnalyzeResponse)
async def analyze_user_persona(request: PersonaAnalyzeRequest):
    """
    分析用户画像
    
    - 自动分析用户的内容主题、风格标签、活跃时间段等
    - 使用AI生成洞察和优化建议
    - 支持强制刷新（force_refresh=True）
    """
    try:
        service = get_persona_service()
        
        persona = await service.analyze_user_persona(
            user_id=request.user_id,
            platform=request.platform,
            force_refresh=request.force_refresh
        )
        
        return PersonaAnalyzeResponse(
            success=True,
            persona=persona,
            message="用户画像分析成功"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/{user_id}", response_model=PersonaAnalyzeResponse)
async def get_user_persona(
    user_id: str,
    platform: PlatformType = Query(PlatformType.XIAOHONGSHU, description="平台类型")
):
    """
    获取用户画像
    
    - 返回已分析的用户画像数据
    - 不触发新的分析（如需分析请使用 POST /analyze）
    """
    try:
        service = get_persona_service()
        persona = service.get_persona(user_id, platform)
        
        if not persona:
            raise HTTPException(
                status_code=404,
                detail=f"用户画像不存在: {user_id}，请先调用 POST /analyze"
            )
        
        return PersonaAnalyzeResponse(
            success=True,
            persona=persona,
            message="获取成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.get("/", response_model=PersonaListResponse)
async def list_user_personas(
    platform: PlatformType = Query(PlatformType.XIAOHONGSHU, description="平台类型"),
    limit: int = Query(50, ge=1, le=200, description="返回数量限制")
):
    """
    列出所有用户画像
    
    - 返回所有已分析的用户画像
    - 支持分页限制
    """
    try:
        service = get_persona_service()
        personas = service.list_personas(platform, limit)
        
        return PersonaListResponse(
            success=True,
            personas=personas,
            total=len(personas),
            message=f"成功获取 {len(personas)} 个用户画像"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取列表失败: {str(e)}")


@router.delete("/{user_id}")
async def delete_user_persona(
    user_id: str,
    platform: PlatformType = Query(PlatformType.XIAOHONGSHU, description="平台类型")
):
    """
    删除用户画像
    
    - 从数据库中删除指定用户的画像数据
    """
    try:
        service = get_persona_service()
        result = service.db.user_personas.delete_one({
            "user_id": user_id,
            "platform": platform.value
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"用户画像不存在: {user_id}")
        
        return {
            "success": True,
            "message": f"已删除用户画像: {user_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
