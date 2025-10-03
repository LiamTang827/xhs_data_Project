import json
import os
from loguru import logger
from apis.xhs_pc_apis import XHS_Apis
from xhs_utils.common_util import init
from xhs_utils.data_util import handle_note_info, download_note, save_to_xlsx
from fastapi import FastAPI ,HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from utils.decorator import handle_spider_exceptions
from dotenv import load_dotenv
from xhs_utils.database import connect_to_mongo, close_mongo_connection, get_database


load_dotenv()  # 从 .env 文件加载环境变量
# 创建 FastAPI 应用实例
app = FastAPI(
    title="小红书爬虫 API",
    version="1.0.0",
    description="一个用于分析小红书用户和笔记的API"
)

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

#定义
class Data_Spider():
    def __init__(self):
        self.xhs_apis = XHS_Apis()

    def fetch_user_all_notes(self, user_url: str, cookies_str: str, proxies=None):
        """
        一个只负责抓取数据并返回，不进行任何文件保存的方法。
        """
        try:
            success, msg, all_note_info = self.xhs_apis.get_user_all_notes(user_url, cookies_str, proxies)
            if not success:
                logger.warning(f"API调用获取用户笔记失败: {msg}")
                return [], False, msg

            note_list = []
            logger.info(f'用户 {user_url} 作品数量: {len(all_note_info)}')
            for simple_note_info in all_note_info:
                note_url = f"https://www.xiaohongshu.com/explore/{simple_note_info['note_id']}?xsec_token={simple_note_info['xsec_token']}"
                note_list.append(note_url)

            return note_list, True, f'成功获取 {len(note_list)} 条笔记链接'

        except Exception as e:
            logger.error(f"爬取用户 {user_url} 所有笔记时发生未知错误: {e}")
            return [], False, f"未知错误: {e}"
   
    def fetch_note_details(self, note_url: str, cookies_str: str, proxies=None):
        """
        根据笔记URL获取单篇笔记的聚合信息（包括基础信息和评论）。
        """
        try:
            # 1. 获取笔记的基础信息
            success, msg, note_info_response = self.xhs_apis.get_note_info(note_url, cookies_str, proxies)
            if not success:
                logger.warning(f"获取笔记 {note_url} 详情失败: {msg}")
                return None, False, msg

            # 安全检查数据结构
            if not note_info_response.get('data', {}).get('items'):
                logger.warning(f"笔记 {note_url} 数据格式异常")
                return None, False, "笔记数据格式异常"

            note_data = note_info_response['data']['items'][0]
            note_id = note_data.get("id")
            
            if not note_id:
                logger.warning(f"笔记 {note_url} 缺少note_id")
                return None, False, "笔记ID获取失败"

            # 2. 获取笔记的评论信息（修复：使用note_url而不是note_id）
            comments_success, comments_msg, comments_data = self.xhs_apis.get_note_all_comment(note_url, cookies_str, proxies)
            if not comments_success:
                logger.warning(f"获取笔记 {note_url} 评论失败，但仍返回基础信息: {comments_msg}")
                comments_list = []
            else:
                # 修复：get_note_all_comment 直接返回评论列表，不是包装在data.comments中
                comments_list = comments_data if isinstance(comments_data, list) else []

            # 3. 从基础信息中提取点赞和收藏数（而不是调用get_likesAndcollects）
            interact_info = note_data.get('interact_info', {})
            liked_count = interact_info.get('liked_count', 0)
            collected_count = interact_info.get('collected_count', 0)
            comment_count = interact_info.get('comment_count', 0)
            share_count = interact_info.get('share_count', 0)

            # 4. 将所有信息聚合成一个清晰的字典返回
            aggregated_details = {
                "basic_info": note_data,
                "comments": comments_list,
                "interact_info": {
                    "liked_count": liked_count,
                    "collected_count": collected_count,
                    "comment_count": comment_count,
                    "share_count": share_count
                },
                "note_id": note_id,
                "note_url": note_url
            }
            
            return aggregated_details, True, '成功获取笔记聚合详情'

        except Exception as e:
            logger.error(f"处理笔记 {note_url} 详情时发生未知错误: {e}")
            return None, False, f"处理数据时发生未知错误: {e}"

def extract_user_id_from_url(url: str) -> Optional[str]:
    """从类似 https://www.xiaohongshu.com/user/profile/5f... 的URL中提取用户ID"""
    try:
        return url.strip().split('/')[-1]
    except Exception:
        return None
    
data_spider = Data_Spider() 

# --- 3. 定义 API 的输入/输出模型 (Pydantic) ---
class UserNotesRequest(BaseModel):
    user_url: str = Field(..., description="小红书用户的个人主页URL")
    cookies: str = Field(..., description="用于认证的Cookie字符串")
    proxies: Optional[Dict[str, str]] = None

class StandardResponse(BaseModel):
    success: bool
    message: str
    data: Optional[List] = None
# --- 4. 创建 API 端点 (Endpoint) ---
@app.get('/user/notes', response_model=StandardResponse, summary="获取用户笔记")
async def get_user_notes_api(user_url: str):
    """
    传入用户URL，返回用户笔记链接列表
    """
    cookies = os.getenv("COOKIES")
    user_notes, success, msg = data_spider.fetch_user_all_notes(user_url, cookies)
    if not success:
        raise HTTPException(status_code=400, detail=f"爬取失败: {msg}")
    user_id = extract_user_id_from_url(user_url)
    db = get_database()
    
    # 确保成功提取到 user_id 并且数据库连接正常
    if db and user_id:
        try:
            # 获取名为 "users" 的集合 (collection)
            user_collection = db.get_collection("users")
            
            # 准备要存入/更新的数据文档
            user_document = {
                "user_id": user_id,
                "user_url": user_url,
                "note_urls": note_urls,
                "note_count": len(note_urls),
                "last_updated": datetime.datetime.now(datetime.timezone.utc) # 记录更新时间
            }

            # 使用 update_one + upsert=True 来插入或更新用户信息
            await user_collection.update_one(
                {'user_id': user_id},
                {'$set': user_document},
                upsert=True
            )
            logger.info(f"用户 {user_id} 的信息及笔记列表已成功存储到 MongoDB。")
        except Exception as e:
            # 即使存储失败，我们仍然可以返回数据给用户，只记录错误
            logger.error(f"存储用户 {user_id} 到 MongoDB 时发生错误: {e}")

    return {
        "success": success,
        "message": msg,
        "data": user_notes
    }

@app.get('/note/info', summary="获取笔记详情")
async def get_note_details_api(note_url: str):
    """
    传入笔记url，返回笔记的详细信息
    """
    cookies = os.getenv("COOKIES")
    note_details, success, msg = data_spider.fetch_note_details(note_url, cookies)
    if not success:
        raise HTTPException(status_code=400, detail=f"爬取失败: {msg}")
    db= get_database()
    if db and note_details:
        try:
            # 獲取名為 "notes" 的集合 (collection)
            note_collection = db.get_collection("notes")
            
            # 使用 update_one + upsert=True 來避免插入重複的筆記
            await note_collection.update_one(
                {'note_id': note_details['note_id']},
                {'$set': note_details},
                upsert=True
            )
            logger.info(f"筆記 {note_details['note_id']} 已成功儲存到 MongoDB。")
        except Exception as e:
            # 即使儲存失敗，我們仍然可以回傳資料給使用者，只記錄錯誤
            logger.error(f"儲存筆記 {note_details.get('note_id')} 到 MongoDB 時發生錯誤: {e}")

    return {
        "success": success,
        "message": msg,
        "data": note_details
    }