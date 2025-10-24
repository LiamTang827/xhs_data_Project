from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
import os
from app.service import SpiderService 
router = APIRouter()
def get_service():
    return SpiderService()

@router.get('/note_info', summary="获取笔记详情")
async def get_note_details(
    note_url: str = Query(..., description="小红书笔记的URL"),
    service: SpiderService = Depends(get_service)
):
    cookies = os.getenv("COOKIES")
    try:
        note_info = await service.process_note_data(note_url, cookies)
        return note_info
    except Exception as e:
        logger.error(f"获取笔记详情失败: {e}")
        return {"error": str(e)}