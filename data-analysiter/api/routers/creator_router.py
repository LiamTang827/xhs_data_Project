"""
Creator Network API Router
创作者网络数据接口
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional

from database import (
    UserProfileRepository,
    CreatorNetworkRepository
)

router = APIRouter(prefix="/api/creators", tags=["creators"])


@router.get("/network")
async def get_creator_network(platform: str = "xiaohongshu") -> Dict[str, Any]:
    """
    获取创作者网络数据
    
    Args:
        platform: 平台类型
        
    Returns:
        网络数据 {creators: [...], edges: [...]}
    """
    try:
        network_repo = CreatorNetworkRepository()
        network = network_repo.get_latest_network(platform)
        
        if not network:
            # 如果数据库中没有，返回空网络
            return {
                "creators": [],
                "edges": []
            }
        
        return network.get("network_data", {"creators": [], "edges": []})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取网络数据失败: {str(e)}")


@router.get("/list")
async def list_all_creators(platform: Optional[str] = None):
    """
    获取所有创作者列表
    
    Args:
        platform: 平台类型，不指定则返回所有平台
        
    Returns:
        创作者列表
    """
    try:
        profile_repo = UserProfileRepository()
        profiles = profile_repo.get_all_profiles(platform)
        
        creators = []
        for profile in profiles:
            creators.append({
                "user_id": profile.get("user_id", ""),
                "nickname": profile.get("nickname", ""),
                "platform": profile.get("platform", ""),
                "topics": profile.get("profile_data", {}).get("topics", []),
                "content_style": profile.get("profile_data", {}).get("content_style", "")
            })
        
        return {"creators": creators, "total": len(creators)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取创作者列表失败: {str(e)}")


@router.get("/{creator_name}")
async def get_creator_detail(creator_name: str, platform: str = "xiaohongshu"):
    """
    获取创作者详细信息
    
    Args:
        creator_name: 创作者昵称
        platform: 平台类型
        
    Returns:
        创作者详细信息
    """
    try:
        profile_repo = UserProfileRepository()
        profile = profile_repo.get_profile_by_nickname(creator_name, platform)
        
        if not profile:
            raise HTTPException(status_code=404, detail=f"未找到创作者: {creator_name}")
        
        return {
            "user_id": profile.get("user_id", ""),
            "nickname": profile.get("nickname", ""),
            "platform": profile.get("platform", ""),
            "profile_data": profile.get("profile_data", {}),
            "created_at": profile.get("created_at"),
            "updated_at": profile.get("updated_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取创作者详情失败: {str(e)}")
