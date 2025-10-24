from loguru import logger
import os
import datetime
import urllib.parse
import json 
from app.repos.user_db import save_user
from app.repos.note_db import save_note
from app.apis.xhs_selenium_apis import XHS_Selenium_Apis as XHS_Apis 
from app.xhs_utils.safe_int import safe_int
from app.xhs_utils.data_util import handle_user_info
from app.xhs_utils.data_util import handle_note_info


class SpiderService: 
    def __init__(self):
        self.api = XHS_Apis()
    async def process_user_note_list(self, user_url: str,cookies_str,proxies=None):
        """处理用户笔记列表的业务逻辑"""
       
        try:
            success, msg, all_note_list = self.api.get_user_all_notes(user_url,cookies_str,proxies)
            if not success:
                logger.warning(f"API调用获取用户笔记失败: {msg}")
                return [], False, msg

            note_list = []
            logger.info(f'用户 {user_url} 作品数量: {len(all_note_list)}')
            for simple_note_info in all_note_list:
                note_url = f"https://www.xiaohongshu.com/explore/{simple_note_info['note_id']}?xsec_token={simple_note_info['xsec_token']}"
                note_list.append(note_url)

            return note_list

        except Exception as e:
            logger.error(f"爬取用户 {user_url} 所有笔记时发生未知错误: {e}")
            return [], False, f"未知错误: {e}"
        

    async def process_user_data(self, user_url: str,cookies_str, proxies=None):
        """处理用户详细信息的业务逻辑"""
        urlParse = urllib.parse.urlparse(user_url)
        user_id = urlParse.path.split("/")[-1]
        try:
            success, msg, res_json = self.api.get_user_info(user_id, cookies_str, proxies)
            if not success:
                logger.warning(f"API调用获取用户详情失败: {msg}")
                return {}, False, msg
            user_info = handle_user_info(res_json.get('data'),user_id)

            # 保存用户数据到数据库
            try:
                await save_user(user_info)
                logger.success(f"服务层：用户 {user_id} 数据已保存到数据库")
            except Exception as db_error:
                logger.error(f"服务层：保存用户 {user_id} 到数据库失败: {db_error}")
                # 即使数据库保存失败，仍然返回数据

            return user_info    
        except Exception as e:
            logger.error(f"爬取用户 {user_url} 详细信息时发生未知错误: {e}")
            return  False, f"未知错误: {e}"

    async def process_note_data(self, note_url: str, cookies_str: str, proxies=None):
        """获得笔记的所有信息"""
        urlParse = urllib.parse.urlparse(note_url)
        note_id = urlParse.path.split("/")[-1]
        try:
            success, msg, res_json = self.api.get_note_info(note_url, cookies_str, proxies)
            if not success:
                logger.warning(f"API调用获取笔记详情失败: {msg}")
                return {}, False, msg
            note_data = res_json.get('data', {}) 

            # (如果 'items' “没有”，返回“空”列表 []）
            items_list = note_data.get('items', [])
            
            if not items_list:
                 # (如果“列表”是“空”的)
                 raise Exception("API 返回成功，但 items 列表为空 (笔记可能被删除)")

            note_info_raw = items_list[0]
            
            # 保存笔记数据到数据库
            try:
                # 准备存储的笔记数据（确保包含 note_id）
                note_to_save = {
                    'note_id': note_id,
                    **note_info_raw  # 合并原始笔记数据
                }
                await save_note(note_to_save)
                logger.success(f"服务层：笔记 {note_id} 数据已保存到数据库")
            except Exception as db_error:
                logger.error(f"服务层：保存笔记 {note_id} 到数据库失败: {db_error}")
                # 即使数据库保存失败，仍然返回数据
            
            return note_data
        except Exception as e:
            logger.error(f"爬取笔记 {note_url} 详细信息时发生未知错误: {e}")
            return {}, False, f"未知错误: {e}"
        
    async def process_second_user(self, note_url: str,cookies_str, proxies=None):
        """获得此用户的所有信息"""
       