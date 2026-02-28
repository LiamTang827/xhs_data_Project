"""
笔记搜索 API Router
提供基于 embedding 的语义搜索接口
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from api.services.note_search_service import (
    search_notes,
    get_note_stats,
    invalidate_cache
)

router = APIRouter(prefix="/api/notes", tags=["笔记搜索"])


class NoteSearchRequest(BaseModel):
    """笔记搜索请求"""
    query: str = Field(..., min_length=1, max_length=500, description="搜索关键词/句子")
    top_k: int = Field(default=10, ge=1, le=50, description="返回结果数量")
    min_engagement: float = Field(default=0.0, ge=0.0, description="最低互动指数过滤")


@router.post("/search")
async def api_search_notes(request: NoteSearchRequest):
    """
    语义搜索笔记
    
    用户输入关键词 → embedding → 与所有笔记计算余弦相似度 → 返回 top-k 结果
    """
    try:
        result = search_notes(
            query=request.query,
            top_k=request.top_k,
            min_engagement=request.min_engagement,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/stats")
async def api_note_stats():
    """获取笔记 embedding 统计信息"""
    try:
        return get_note_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


@router.post("/cache/invalidate")
async def api_invalidate_cache():
    """清除内存缓存（新增笔记 embedding 后调用）"""
    try:
        invalidate_cache()
        return {"success": True, "message": "缓存已清除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清除缓存失败: {str(e)}")
