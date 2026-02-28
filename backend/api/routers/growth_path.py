"""
成长路径分析 API
根据竞品爆款内容生成创作建议
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging

from api.services.growth_path_service import GrowthPathService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/growth-path/{my_user_id}/{competitor_user_id}")
async def analyze_growth_path(
    my_user_id: str,
    competitor_user_id: str,
    top_n: int = Query(default=5, ge=1, le=20, description="返回前N个建议"),
    min_engagement: float = Query(default=1.0, ge=0.1, description="最小互动指数（1.0 = 1000互动数）"),
    days: Optional[int] = Query(default=None, ge=1, le=365, description="只看最近N天的笔记，不传则不限")
):
    """
    分析成长路径：基于竞品爆款内容生成创作建议
    
    **使用场景：**
    - 发现"竞品做了但我没做"的内容方向
    - 学习爆款内容的成功经验
    - 保持个人风格的同时借鉴优秀案例
    
    **参数：**
    - my_user_id: 我的用户ID
    - competitor_user_id: 竞品/参考创作者的用户ID
    - top_n: 返回几个创作建议（默认5个）
    - min_engagement: 爆款阈值，互动指数≥此值才算爆款（默认1.0，即1000互动数）
    
    **返回：**
    - my_profile: 我的基础信息（昵称、内容方向）
    - competitor_profile: 竞品基础信息
    - overall_similarity: 与竞品的整体相似度（0-1）
    - opportunities: 创作机会列表，每个包含：
      - note_title: 笔记标题
      - engagement_index: 互动指数
      - reason: 为什么这是机会
      - direction: 内容方向建议
      - angles: 可以切入的角度
    - summary: 总体策略建议
    
    **示例：**
    ```
    GET /api/creators/growth-path/user_123/user_456?top_n=5&min_engagement=2.0
    ```
    """
    try:
        service = GrowthPathService()
        
        result = await service.analyze_growth_opportunities(
            my_user_id=my_user_id,
            competitor_user_id=competitor_user_id,
            top_n=top_n,
            min_engagement_index=min_engagement,
            days=days
        )
        
        return {
            'success': True,
            'data': result
        }
        
    except ValueError as e:
        logger.warning(f"参数错误: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"分析成长路径失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/competitors/{user_id}")
async def get_potential_competitors(
    user_id: str,
    limit: int = Query(default=10, ge=1, le=50)
):
    """
    获取潜在竞品列表（基于网络连接）
    
    返回与我相似的其他创作者，可以作为参考对象
    """
    try:
        from database.connection import get_database
        db = get_database()
        
        # 从网络数据中找到与该用户连接的其他创作者
        network = db.creator_networks.find_one({'platform': 'xiaohongshu'})
        if not network:
            return {
                'success': True,
                'data': {
                    'competitors': [],
                    'message': '网络数据不存在，请先生成创作者网络'
                }
            }
        
        network_data = network.get('network_data', {})
        edges = network_data.get('edges', [])
        creators = network_data.get('creators', [])
        
        # 找到所有与该用户连接的边
        connected_user_ids = set()
        for edge in edges:
            if edge['source'] == user_id:
                connected_user_ids.add(edge['target'])
            elif edge['target'] == user_id:
                connected_user_ids.add(edge['source'])
        
        # 获取连接的创作者信息
        competitors = []
        creator_map = {c['id']: c for c in creators}
        
        for uid in connected_user_ids:
            if uid in creator_map:
                c = creator_map[uid]
                competitors.append({
                    'user_id': c['id'],
                    'nickname': c.get('nickname', c.get('name', '')),
                    'followers': c.get('followers', 0),
                    'total_engagement': c.get('totalEngagement', 0),
                    'note_count': c.get('noteCount', 0),
                    'topics': c.get('topics', [])[:3],
                    'avatar': c.get('avatar', '')
                })
        
        # 按互动数排序
        competitors.sort(key=lambda x: x['total_engagement'], reverse=True)
        
        return {
            'success': True,
            'data': {
                'competitors': competitors[:limit],
                'total': len(competitors)
            }
        }
        
    except Exception as e:
        logger.error(f"获取竞品列表失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")
