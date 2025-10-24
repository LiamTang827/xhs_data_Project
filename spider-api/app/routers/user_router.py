from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
import os
from app.service import SpiderService 
from app.xhs_utils.schemas import StandardResponse 

router = APIRouter()

def get_service():
    return SpiderService()


@router.get('/note_list', summary="获取用户笔记列表")
async def get_user_notes_list(
    user_url: str = Query(..., description="小红书用户的个人主页URL"),
    service: SpiderService = Depends(get_service)
):
    """
    获得用户的笔记列表的api接口
    """
    logger.info(f"Router： /user/notes : {user_url}")
    cookies = os.getenv("COOKIES")
    try:
        user_notes_list= await service.process_user_note_list(user_url,cookies)
        return user_notes_list
        
    except Exception as e:
        logger.error(f"Router：/note_list 订单“崩溃”: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {e}")
    
@router.get('/detail_info',summary="获取用户信息")
async def get_user_info(
    user_url: str = Query(..., description="小红书用户的个人主页URL"),
    service: SpiderService = Depends(get_service)
):
    """
    获得用户的详细信息的api接口
    """
    logger.info(f"Router： /user/detail_info : {user_url}")
    cookies = os.getenv("COOKIES")
    try:
        user_info = await service.process_user_data(user_url,cookies)
        return user_info
        
    except Exception as e:
        logger.error(f"Router：/detail_info 订单“崩溃”: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {e}" )




@router.get('/second_u', summary="赛博用户")
async def get_cyber_user(
    user_url: str = Query(..., description="小红书用户的个人主页URL"),
    service: SpiderService = Depends(get_service)
):
    """
    获得赛博用户的api接口
    """
    logger.info(f"Router： /user/second_u : {user_url}")
    
    try:
        cyber_user_data, success, msg = await service.process_cyber_user_data(user_url)
        if not success:
            raise HTTPException(status_code=400, detail=msg)
        return StandardResponse(
            success=True,
            message=msg,
            data=cyber_user_data
        )
        
    except Exception as e:
        logger.error(f"Router：/second_u 订单“崩溃”: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {e}")
    