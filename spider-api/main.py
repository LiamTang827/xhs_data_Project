import json
import os
import datetime  
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
import motor.motor_asyncio

# 确保在这里加载环境变量
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
logger.info(f"MONGO_URI 是否已加载: {'是' if MONGO_URI else '否'}")

if not MONGO_URI:
    logger.error("❌ MONGO_URI 环境变量未设置！")
    raise ValueError("MONGO_URI 环境变量未设置")

# 打印连接信息（隐藏密码）
if MONGO_URI:
    safe_uri = MONGO_URI.replace(MONGO_URI.split('://')[1].split('@')[0], '***:***')
    logger.info(f"连接字符串: {safe_uri}")

try:
    db_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    logger.info("MongoDB 客户端创建成功")
except Exception as e:
    logger.error(f"创建 MongoDB 客户端失败: {e}")
    raise

# 获取数据库
database = db_client["xhs_data"]

# 获取集合
note_collection = database.get_collection("notes")
user_collection = database.get_collection("users")

def get_database():
    """返回数据库实例"""
    return database

async def connect_to_mongo():
    """测试数据库连接"""
    logger.info("正在测试 MongoDB Atlas 连接...")
    try:
        await db_client.admin.command('ping', serverSelectionTimeoutMS=5000)
        logger.success("✅ 成功连接到 MongoDB Atlas！")
        
        # 检查数据库和集合
        db_list = await db_client.list_database_names()
        logger.info(f"可用数据库: {db_list}")
        
        if "xhs_data" in db_list:
            logger.info("数据库 'xhs_data' 存在")
            collections = await db_client["xhs_data"].list_collection_names()
            logger.info(f"xhs_data 数据库中的集合: {collections}")
        else:
            logger.warning("数据库 'xhs_data' 不存在")
        
    except Exception as e:
        logger.error(f"连接测试失败: {e}")
        raise

# 创建 FastAPI 应用实例
app = FastAPI(
    title="小红书爬虫 API",
    version="1.0.0",
    description="一个用于分析小红书用户和笔记的API"
)

# 辅助函数：安全地将值转换为整数
def safe_int(value, default=0):
    """
    安全地将值转换为整数，支持中文数字格式（如 "2.7万"）
    :param value: 要转换的值（可能是 int, str, None 等）
    :param default: 转换失败时的默认值
    :return: 整数值
    """
    if value is None:
        return default
    
    try:
        # 如果已经是整数，直接返回
        if isinstance(value, int):
            return value
        
        # 如果是字符串，处理中文数字格式
        if isinstance(value, str):
            value = value.strip()
            
            # 处理空字符串
            if not value:
                return default
            
            # 处理包含"万"的情况（如 "2.7万" = 27000）
            if '万' in value:
                num_str = value.replace('万', '').strip()
                try:
                    # 转换为浮点数再乘以10000
                    return int(float(num_str) * 10000)
                except ValueError:
                    return default
            
            # 处理包含"千"的情况（如果有的话）
            if '千' in value:
                num_str = value.replace('千', '').strip()
                try:
                    return int(float(num_str) * 1000)
                except ValueError:
                    return default
            
            # 普通数字字符串
            return int(float(value))
        
        # 其他类型尝试直接转换
        return int(value)
        
    except (ValueError, TypeError):
        return default

#定义
class Data_Spider():
    def __init__(self):
        self.xhs_apis = XHS_Apis()

    def fetch_user_detailed_info(self, user_id: str, user_name: str, cookies_str: str, proxies=None):
        """
        获取用户的详细信息，包括粉丝数
        通过搜索用户名来获取包含粉丝数的数据
        """
        try:
            # 使用 search_user API 搜索用户名
            success, msg, search_result = self.xhs_apis.search_user(user_name, cookies_str, page=1, proxies=proxies)
            
            if not success or not search_result.get('data', {}).get('users'):
                logger.warning(f"搜索用户 {user_name} 失败: {msg}")
                return None, False, msg
            
            # 在搜索结果中找到匹配的用户
            users = search_result['data']['users']
            target_user = None
            
            for user in users:
                if user.get('id') == user_id or user.get('name') == user_name:
                    target_user = user
                    break
            
            if not target_user and len(users) > 0:
                # 如果没找到精确匹配，使用第一个结果（可能是最相关的）
                target_user = users[0]
                logger.warning(f"未找到精确匹配的用户，使用搜索结果第一个: {target_user.get('name')}")
            
            if not target_user:
                return None, False, "未找到用户信息"
            
            # 提取有用的字段
            user_detail = {
                "user_id": target_user.get('id'),
                "user_name": target_user.get('name'),
                "red_id": target_user.get('red_id'),  # 小红书号
                "fans": target_user.get('fans', '0'),  # 粉丝数（字符串格式，如 "2.7万"）
                "note_count": target_user.get('note_count', 0),  # 笔记数量
                "is_verified": target_user.get('red_official_verified', False),  # 是否认证
                "avatar": target_user.get('image', ''),  # 头像
            }
            
            return user_detail, True, '成功获取用户详细信息'
            
        except Exception as e:
            logger.error(f"获取用户 {user_name} 详细信息时发生错误: {e}")
            return None, False, f"未知错误: {e}"

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
        根据笔记URL获取单篇笔记的详细信息，并格式化为 content_snapshot 结构
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
            note_card = note_data.get('note_card', {})
            
            # 提取基础字段
            note_id = note_data.get("id")
            if not note_id:
                logger.warning(f"笔记 {note_url} 缺少note_id")
                return None, False, "笔记ID获取失败"

            # 提取用户信息
            user = note_card.get('user', {})
            user_id = user.get('user_id', user.get('id', ''))
            user_nickname = user.get('nickname', '')
            
            # 提取笔记类型
            note_type = note_card.get('type', 'normal')  # 'normal' 或 'video'
            content_type = 'video' if note_type == 'video' else 'note'
            
            # 提取标题和描述
            title = note_card.get('title', '')
            description = note_card.get('desc', '')
            
            # 提取发布时间
            published_time = note_card.get('time', 0)
            if published_time:
                published_time = datetime.datetime.fromtimestamp(published_time / 1000, tz=datetime.timezone.utc)
            
            # 提取互动数据（使用 safe_int 转换）
            interact_info = note_card.get('interact_info', {})
            liked_count = safe_int(interact_info.get('liked_count', 0))
            collected_count = safe_int(interact_info.get('collected_count', 0))
            comment_count = safe_int(interact_info.get('comment_count', 0))
            share_count = safe_int(interact_info.get('share_count', 0))
            
            # 提取标签
            tag_list = note_card.get('tag_list', [])
            tags = [tag.get('name', '') for tag in tag_list if tag.get('name')]
            
            # 2. 获取笔记的评论信息
            comments_success, comments_msg, comments_data = self.xhs_apis.get_note_all_comment(note_url, cookies_str, proxies)
            if not comments_success:
                logger.warning(f"获取笔记 {note_url} 评论失败: {comments_msg}")
                comments_list = []
            else:
                comments_list = comments_data if isinstance(comments_data, list) else []

            # 3. 格式化评论数据为 content_snapshot 结构
            formatted_comments = []
            for comment in comments_list:
                formatted_comment = {
                    "commenter_id": comment.get('user_info', {}).get('user_id', ''),
                    "commenter_name": comment.get('user_info', {}).get('nickname', ''),
                    "comment_content": comment.get('content', ''),
                    "published_time": comment.get('create_time', 0),
                    "likes_on_comment": safe_int(comment.get('like_count', 0))
                }
                formatted_comments.append(formatted_comment)

            # 4. 构建最终的 content_snapshot 结构
            content_snapshot = {
                "channel_id": user_id,  # 用户ID作为channel_id
                "content_id": note_id,
                "content_type": content_type,
                "content_title": title,
                "likes": liked_count,
                "shares": share_count,
                "views": 0,  # 小红书API不提供浏览量
                "published_time": published_time,
                "collected_number": collected_count,
                "comments": formatted_comments,
                "description": description,
                "tags": tags,
                "note_url": note_url,
                "last_updated": datetime.datetime.now(datetime.timezone.utc),
                # 保留原始数据以备查
                "_raw_data": {
                    "note_card": note_card,
                    "comment_count": comment_count
                }
            }
            
            logger.info(f"成功解析笔记 {note_id}: likes={liked_count}, collects={collected_count}, comments={len(formatted_comments)}")
            
            return content_snapshot, True, '成功获取笔记详情'

        except Exception as e:
            logger.error(f"处理笔记 {note_url} 详情时发生未知错误: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None, False, f"处理数据时发生未知错误: {e}"

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
    传入用户URL，返回用户笔记链接列表及用户详细信息
    """
    import urllib.parse
    
    cookies = os.getenv("COOKIES")
    
    # 1. 从URL提取user_id
    urlParse = urllib.parse.urlparse(user_url)
    user_id = urlParse.path.split("/")[-1]
    
    # 2. 获取用户基础信息
    success_info, msg_info, user_info_response = data_spider.xhs_apis.get_user_info(user_id, cookies)
    user_name = "未知用户"
    if success_info and user_info_response.get('data', {}).get('basic_info'):
        basic_info = user_info_response['data']['basic_info']
        user_name = basic_info.get('nickname', '未知用户')
    
    # 3. 获取用户笔记列表
    user_notes, success, msg = data_spider.fetch_user_all_notes(user_url, cookies)

    if not success:
        raise HTTPException(status_code=400, detail=f"爬取失败: {msg}")
    
    # 4. 获取用户详细信息（包括粉丝数）
    user_detail, success_detail, msg_detail = data_spider.fetch_user_detailed_info(user_id, user_name, cookies)
    
    # 5. 计算总点赞数（从笔记列表中累加）
    kvs = urlParse.query.split('&')
    kvDist = {kv.split('=')[0]: kv.split('=')[1] for kv in kvs}
    xsec_token = kvDist.get('xsec_token', '')
    xsec_source = kvDist.get('xsec_source', 'pc_search')
    
    total_likes = 0
    total_collects = 0
    total_comments = 0
    
    # 获取笔记详细信息以累加互动数据
    success_notes, msg_notes, res_json = data_spider.xhs_apis.get_user_note_info(
        user_id, '', cookies, xsec_token, xsec_source
    )
    
    if success_notes and res_json and res_json.get('data', {}).get('notes'):
        notes = res_json['data']['notes']
        for note in notes:
            interact_info = note.get('interact_info', {})
            # 使用辅助函数安全地转换并累加
            total_likes += safe_int(interact_info.get('liked_count'))
            total_collects += safe_int(interact_info.get('collected_count'))
            total_comments += safe_int(interact_info.get('comment_count'))
    
    db = get_database()
    fan_count=user_detail.get('fans', '0')
    fan_count=safe_int(fan_count)
    # 直接使用 user_url 作为标识
    if db is not None:
        try:
            # 获取名为 "users" 的集合 (collection)
            user_collection = db.get_collection("users")
            
            # 准备要存入/更新的数据文档
            user_snapshot = {
                "last_updated": datetime.datetime.now(datetime.timezone.utc),
                "user_url": user_url, 
                "red_id": user_detail.get('red_id', ''),  # 小红书号
                "user_name": user_name,
                "note_count": len(user_notes),
                "note_urls": user_notes,
                "fan_count": fan_count,
                "total_likes": total_likes,
            }
            

            await user_collection.insert_one(user_snapshot)
        except Exception as e:
            # 即使存储失败，我们仍然可以返回数据给用户，只记录错误
            logger.error(f"存储用户 {user_url} 到 MongoDB 时发生错误: {e}")

    return {
        "success": success,
        "message": msg,
        "data": user_notes
    }

@app.get('/note/info', summary="获取笔记详情")
async def get_note_details_api(note_url: str):
    """
    传入笔记url，返回笔记的详细信息（content_snapshot 格式）
    """
    cookies = os.getenv("COOKIES")
    content_snapshot, success, msg = data_spider.fetch_note_details(note_url, cookies)
    if not success:
        raise HTTPException(status_code=400, detail=f"爬取失败: {msg}")
    
    db = get_database()
    
    # 修复：使用 is not None 检查
    if db is not None and content_snapshot:
        try:
            # 獲取名為 "notes" 的集合 (collection)
            note_collection = db.get_collection("notes")
            
            # 使用 content_id 作为唯一标识，update_one + upsert=True 來避免插入重複的筆記
            await note_collection.update_one(
                {'content_id': content_snapshot['content_id']},
                {'$set': content_snapshot},
                upsert=True
            )
            logger.info(f"笔记 {content_snapshot['content_id']} 已成功存储到 MongoDB (content_snapshot 格式)")
            logger.info(f"互动数据: likes={content_snapshot['likes']}, collects={content_snapshot['collected_number']}, comments={len(content_snapshot['comments'])}")
        except Exception as e:
            # 即使儲存失敗，我們仍然可以回傳資料給使用者，只記錄錯誤
            logger.error(f"儲存筆記 {content_snapshot.get('content_id')} 到 MongoDB 時發生錯誤: {e}")
            import traceback
            logger.error(traceback.format_exc())

    return {
        "success": success,
        "message": msg,
        "data": content_snapshot
    }
