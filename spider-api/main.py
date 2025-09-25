import json
import os
from loguru import logger
from apis.xhs_pc_apis import XHS_Apis
from xhs_utils.common_util import init
from xhs_utils.data_util import handle_note_info, download_note, save_to_xlsx
from fastapi import FastAPI ,HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
# 步骤 1: 导入你的装饰器
from utils.decorator import handle_spider_exceptions


# --- 2. FastAPI 应用和您的爬虫类实例化 ---
app = FastAPI(
    title="小红书爬虫 API",
    version="1.0.0",
    description="一个用于分析小红书用户和笔记的API"
)

logger.info("程序启动：FastAPI app 实例已成功创建。") # <--- 添加这一行

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

    def spider_note(self, note_url: str, cookies_str: str, proxies=None):
        """
        爬取一个笔记的信息
        :param note_url:
        :param cookies_str:
        :return:
        """
        note_info = None
        try:
            success, msg, note_info = self.xhs_apis.get_note_info(note_url, cookies_str, proxies)
            if success:
                note_info = note_info['data']['items'][0]
                note_info['url'] = note_url
                note_info = handle_note_info(note_info)
        except Exception as e:
            success = False
            msg = e
        logger.info(f'爬取笔记信息 {note_url}: {success}, msg: {msg}')
        return success, msg, note_info

    def spider_some_note(self, notes: list, cookies_str: str, base_path: dict, save_choice: str, excel_name: str = '', proxies=None):
        """
        爬取一些笔记的信息
        :param notes:
        :param cookies_str:
        :param base_path:
        :return:
        """
        if (save_choice == 'all' or save_choice == 'excel') and excel_name == '':
            raise ValueError('excel_name 不能为空')
        note_list = []
        for note_url in notes:
            success, msg, note_info = self.spider_note(note_url, cookies_str, proxies)
            if note_info is not None and success:
                note_list.append(note_info)
        for note_info in note_list:
            if save_choice == 'all' or 'media' in save_choice:
                download_note(note_info, base_path['media'], save_choice)
        if save_choice == 'all' or save_choice == 'excel':
            file_path = os.path.abspath(os.path.join(base_path['excel'], f'{excel_name}.xlsx'))
            save_to_xlsx(note_list, file_path)

    @handle_spider_exceptions
    def spider_user_all_note(self, user_url: str, cookies_str: str, base_path: dict, save_choice: str, excel_name: str = '', proxies=None):
        """
        爬取一个用户的所有笔记
        :param user_url:
        :param cookies_str:
        :param base_path:
        :return:
        """
        note_list = []
        try:
            success, msg, all_note_info = self.xhs_apis.get_user_all_notes(user_url, cookies_str, proxies)
            if success:
                logger.info(f'用户 {user_url} 作品数量: {len(all_note_info)}')
                for simple_note_info in all_note_info:
                    note_url = f"https://www.xiaohongshu.com/explore/{simple_note_info['note_id']}?xsec_token={simple_note_info['xsec_token']}"
                    note_list.append(note_url)
            if save_choice == 'all' or save_choice == 'excel':
                excel_name = user_url.split('/')[-1].split('?')[0]
            self.spider_some_note(note_list, cookies_str, base_path, save_choice, excel_name, proxies)
        except Exception as e:
            success = False
            msg = e
        logger.info(f'爬取用户所有视频 {user_url}: {success}, msg: {msg}')
        return note_list, success, msg

    @handle_spider_exceptions
    def spider_some_search_note(self, query: str, require_num: int, cookies_str: str, base_path: dict, save_choice: str, sort_type_choice=0, note_type=0, note_time=0, note_range=0, pos_distance=0, geo: dict = None,  excel_name: str = '', proxies=None):
        """
            指定数量搜索笔记，设置排序方式和笔记类型和笔记数量
            :param query 搜索的关键词
            :param require_num 搜索的数量
            :param cookies_str 你的cookies
            :param base_path 保存路径
            :param sort_type_choice 排序方式 0 综合排序, 1 最新, 2 最多点赞, 3 最多评论, 4 最多收藏
            :param note_type 笔记类型 0 不限, 1 视频笔记, 2 普通笔记
            :param note_time 笔记时间 0 不限, 1 一天内, 2 一周内天, 3 半年内
            :param note_range 笔记范围 0 不限, 1 已看过, 2 未看过, 3 已关注
            :param pos_distance 位置距离 0 不限, 1 同城, 2 附近 指定这个必须要指定 geo
            返回搜索的结果
        """
        note_list = []
        try:
            success, msg, notes = self.xhs_apis.search_some_note(query, require_num, cookies_str, sort_type_choice, note_type, note_time, note_range, pos_distance, geo, proxies)
            if success:
                notes = list(filter(lambda x: x['model_type'] == "note", notes))
                logger.info(f'搜索关键词 {query} 笔记数量: {len(notes)}')
                for note in notes:
                    note_url = f"https://www.xiaohongshu.com/explore/{note['id']}?xsec_token={note['xsec_token']}"
                    note_list.append(note_url)
            if save_choice == 'all' or save_choice == 'excel':
                excel_name = query
            self.spider_some_note(note_list, cookies_str, base_path, save_choice, excel_name, proxies)
        except Exception as e:
            success = False
            msg = e
        logger.info(f'搜索关键词 {query} 笔记: {success}, msg: {msg}')
        return note_list, success, msg

logger.info("程序启动：准备创建 Data_Spider 实例...") # <--- 添加这一行

data_spider = Data_Spider() # 创建您的爬虫实例

logger.info("程序启动：Data_Spider 实例已成功创建。") # <--- 添加这一行

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
# 这是您的 FastAPI 端点函数
@app.post("/api/v1/user/notes", response_model=StandardResponse, summary="获取用户所有笔记")
async def get_user_all_notes_api(request: UserNotesRequest):
    """
    接收用户URL和Cookie，调用爬虫获取该用户的所有笔记链接。
    """
    logger.info(f"开始处理用户笔记请求: {request.user_url}")

    # 1. 调用您改造后的爬虫方法
    note_list, success, msg = data_spider.fetch_user_all_notes(
        user_url=request.user_url,
        cookies_str=request.cookies,
        proxies=request.proxies
    )

    # 2. 处理爬虫返回的结果
    if not success:
        # 如果是爬虫逻辑层面的失败 (例如 Cookie 无效)，返回 400 客户端错误
        logger.warning(f"爬虫执行失败: {msg}")
        raise HTTPException(
            status_code=400,
            detail={"success": False, "message": f"爬取失败: {msg}", "data": None}
        )

    # 3. 成功时，格式化并返回标准的 JSON 响应
    logger.success(f"成功获取 {len(note_list)} 条笔记链接 for user {request.user_url}")
    return {
        "success": True,
        "message": msg,
        "data": note_list  # note_list 是爬虫返回的URL列表
    }

# if __name__ == '__main__':
#     """
#         此文件为爬虫的入口文件，可以直接运行
#         apis/xhs_pc_apis.py 为爬虫的api文件，包含小红书的全部数据接口，可以继续封装
#         apis/xhs_creator_apis.py 为小红书创作者中心的api文件
#         感谢star和follow
#     """
#
#     cookies_str, base_path = init()
#     data_spider = Data_Spider()
#     """
#         save_choice: all: 保存所有的信息, media: 保存视频和图片（media-video只下载视频, media-image只下载图片，media都下载）, excel: 保存到excel
#         save_choice 为 excel 或者 all 时，excel_name 不能为空
#     """
#
#
#     # 1 爬取列表的所有笔记信息 笔记链接 如下所示 注意此url会过期！
#     notes = [
#         r'https://www.xiaohongshu.com/explore?language=zh-CN',
#     ]
#     data_spider.spider_some_note(notes, cookies_str, base_path, 'all', 'test')
#
#     # 2 爬取用户的所有笔记信息 用户链接 如下所示 注意此url会过期！
#     user_url = 'https://www.xiaohongshu.com/user/profile/65a8d89b0000000008015fd9?xsec_token=ABuLIo4RpfTcnzBhe-OV5xWYslmLaeg_akZ3oLCMtYghg%3D&xsec_source=pc_search'
#     data_spider.spider_user_all_note(user_url, cookies_str, base_path, 'all')
#
#     # 3 搜索指定关键词的笔记
#     query = "iPhone17"
#     query_num = 10
#     sort_type_choice = 0  # 0 综合排序, 1 最新, 2 最多点赞, 3 最多评论, 4 最多收藏
#     note_type = 2 # 0 不限, 1 视频笔记, 2 普通笔记
#     note_time = 1  # 0 不限, 1 一天内, 2 一周内天, 3 半年内
#     note_range = 0  # 0 不限, 1 已看过, 2 未看过, 3 已关注
#     pos_distance = 0  # 0 不限, 1 同城, 2 附近 指定这个1或2必须要指定 geo
#     # geo = {
#     #     # 经纬度
#     #     "latitude": 39.9725,
#     #     "longitude": 116.4207
#     # }
#     data_spider.spider_some_search_note(query, query_num, cookies_str, base_path, 'all', sort_type_choice, note_type, note_time, note_range, pos_distance, geo=None)
