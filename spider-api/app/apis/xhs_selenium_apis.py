# encoding: utf-8
"""
使用 Selenium 模拟真实浏览器行为来绕过小红书的反爬虫机制
返回的数据格式与 xhs_pc_apis.py 保持一致，以便无缝替换
"""

import json
import time
import urllib.parse
from typing import Optional, Tuple, Dict, Any
from loguru import logger

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class XHS_Selenium_Apis:
    """
    使用 Selenium 的小红书 API 客户端
    模拟真实浏览器行为，绕过反爬虫检测
    """
    
    def __init__(self, headless: bool = True, wait_timeout: int = 10):
        """
        初始化 Selenium WebDriver
        
        :param headless: 是否使用无头模式（不显示浏览器窗口）
        :param wait_timeout: 页面加载的最大等待时间（秒）
        """
        self.wait_timeout = wait_timeout
        self.driver = None
        self.headless = headless
        
    def _init_driver(self, cookies_str: str = None):
        """
        初始化并配置 Chrome WebDriver
        
        :param cookies_str: Cookie 字符串，格式与原 API 一致
        """
        if self.driver:
            return  # 如果已经初始化，直接返回
            
        chrome_options = Options()
        
        # 基础配置
        if self.headless:
            chrome_options.add_argument('--headless')  # 无头模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        # 模拟真实用户
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 设置 User-Agent
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # 初始化 driver
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # 隐藏 webdriver 特征
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # 如果提供了 cookies，则注入
        if cookies_str:
            self._inject_cookies(cookies_str)
            
    def _inject_cookies(self, cookies_str: str):
        """
        将 Cookie 字符串注入到浏览器中
        
        :param cookies_str: Cookie 字符串，格式: 'key1=value1; key2=value2'
        """
        try:
            # 先访问小红书主页，建立域
            self.driver.get("https://www.xiaohongshu.com")
            time.sleep(2)
            
            # 解析并注入 cookies
            if '; ' in cookies_str:
                cookie_pairs = cookies_str.split('; ')
            else:
                cookie_pairs = cookies_str.split(';')
                
            for pair in cookie_pairs:
                if '=' in pair:
                    parts = pair.split('=', 1)
                    cookie_dict = {
                        'name': parts[0].strip(),
                        'value': parts[1].strip() if len(parts) > 1 else '',
                        'domain': '.xiaohongshu.com'
                    }
                    self.driver.add_cookie(cookie_dict)
                    
            logger.info("Cookies 注入成功")
            
        except Exception as e:
            logger.error(f"注入 Cookies 失败: {e}")
            
    def _wait_for_api_response(self, url_pattern: str, timeout: int = None) -> Optional[Dict]:
        """
        等待特定的 API 响应
        通过监听浏览器的网络请求来获取 API 返回的 JSON 数据
        
        :param url_pattern: 要监听的 API URL 模式
        :param timeout: 超时时间
        :return: API 返回的 JSON 数据
        """
        timeout = timeout or self.wait_timeout
        
        # 启用 Chrome DevTools Protocol 来捕获网络请求
        self.driver.execute_cdp_cmd('Network.enable', {})
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # 获取所有网络请求
                logs = self.driver.get_log('performance')
                
                for log in logs:
                    message = json.loads(log['message'])['message']
                    
                    # 检查是否是我们要找的 API 响应
                    if message['method'] == 'Network.responseReceived':
                        response_url = message['params']['response']['url']
                        
                        if url_pattern in response_url:
                            request_id = message['params']['requestId']
                            
                            # 获取响应体
                            try:
                                response_body = self.driver.execute_cdp_cmd(
                                    'Network.getResponseBody',
                                    {'requestId': request_id}
                                )
                                
                                if 'body' in response_body:
                                    return json.loads(response_body['body'])
                                    
                            except Exception as e:
                                logger.debug(f"获取响应体失败: {e}")
                                continue
                                
            except Exception as e:
                logger.debug(f"解析网络日志时出错: {e}")
                
            time.sleep(0.5)
            
        logger.warning(f"等待 API 响应超时: {url_pattern}")
        return None
        
    def get_user_info(self, user_id: str, cookies_str: str, proxies: dict = None) -> Tuple[bool, str, Optional[Dict]]:
        """
        获取用户的基本信息
        
        :param user_id: 用户 ID
        :param cookies_str: Cookie 字符串
        :param proxies: 代理配置（Selenium 暂不支持，保留参数以保持接口一致）
        :return: (是否成功, 消息, 响应数据)
        """
        res_json = None
        
        try:
            # 初始化 driver
            if not self.driver:
                self._init_driver(cookies_str)
                
            # 访问用户主页
            user_url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
            logger.info(f"正在访问用户主页: {user_url}")
            self.driver.get(user_url)
            
            # 等待页面加载
            time.sleep(3)
            
            # 方法1: 尝试从页面的 __INITIAL_STATE__ 中提取数据
            try:
                initial_state_script = self.driver.find_element(By.ID, "__INITIAL_STATE__")
                initial_state_json = initial_state_script.get_attribute('textContent')
                initial_state = json.loads(initial_state_json)
                
                # 从 initial state 中提取用户信息
                user_data = initial_state.get('user', {}).get('userDetail', {})
                
                if user_data:
                    # 构造与原 API 一致的返回格式
                    res_json = {
                        "success": True,
                        "msg": "success",
                        "data": {
                            "basic_info": {
                                "user_id": user_data.get('userId') or user_data.get('user_id') or user_id,
                                "nickname": user_data.get('nickname', ''),
                                "avatar": user_data.get('imageb', user_data.get('avatar', '')),
                                "ip_location": user_data.get('ipLocation', ''),
                                "desc": user_data.get('desc', ''),
                                "gender": user_data.get('gender', 0),
                                "follows": user_data.get('follows', 0),
                                "fans": user_data.get('fans', 0),
                                "interaction": user_data.get('interaction', 0),
                                "red_id": user_data.get('redId', '')
                            }
                        }
                    }
                    
                    success = True
                    msg = "success"
                    logger.success(f"成功获取用户 {user_id} 的信息（通过页面数据）")
                    return success, msg, res_json
                    
            except NoSuchElementException:
                logger.debug("未找到 __INITIAL_STATE__ 元素，尝试其他方法")
            except Exception as e:
                logger.debug(f"解析 __INITIAL_STATE__ 失败: {e}")
                
            # 方法2: 通过页面元素提取信息（备用方案）
            try:
                wait = WebDriverWait(self.driver, self.wait_timeout)
                
                # 等待用户信息区域加载
                user_info_section = wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "user-info"))
                )
                
                # 提取昵称
                try:
                    nickname_elem = self.driver.find_element(By.CLASS_NAME, "user-nickname")
                    nickname = nickname_elem.text
                except:
                    nickname = ""
                    
                # 提取头像
                try:
                    avatar_elem = self.driver.find_element(By.CLASS_NAME, "avatar")
                    avatar_url = avatar_elem.get_attribute("src")
                except:
                    avatar_url = ""
                    
                # 提取简介
                try:
                    desc_elem = self.driver.find_element(By.CLASS_NAME, "user-desc")
                    desc = desc_elem.text
                except:
                    desc = ""
                    
                # 构造返回数据
                res_json = {
                    "success": True,
                    "msg": "success",
                    "data": {
                        "basic_info": {
                            "user_id": user_id,
                            "nickname": nickname,
                            "avatar": avatar_url,
                            "desc": desc,
                            "ip_location": "",
                            "gender": 0,
                            "follows": 0,
                            "fans": 0,
                            "interaction": 0,
                            "red_id": ""
                        }
                    }
                }
                
                success = True
                msg = "success"
                logger.success(f"成功获取用户 {user_id} 的信息（通过页面元素）")
                
            except TimeoutException:
                success = False
                msg = "页面加载超时"
                logger.error(f"获取用户信息超时: {user_id}")
                
        except Exception as e:
            success = False
            msg = str(e)
            logger.error(f"获取用户信息时发生错误: {e}")
            
        return success, msg, res_json
        
    def get_user_all_notes(self, user_url: str, cookies_str: str, proxies: dict = None) -> Tuple[bool, str, list]:
        """
        获取用户的所有笔记
        
        :param user_url: 用户主页 URL
        :param cookies_str: Cookie 字符串
        :param proxies: 代理配置（保留参数以保持接口一致）
        :return: (是否成功, 消息, 笔记列表)
        """
        note_list = []
        
        try:
            # 初始化 driver
            if not self.driver:
                self._init_driver(cookies_str)
                
            # 解析 user_id
            urlParse = urllib.parse.urlparse(user_url)
            user_id = urlParse.path.split("/")[-1]
            
            logger.info(f"正在获取用户 {user_id} 的所有笔记")
            self.driver.get(user_url)
            
            # 等待页面加载
            time.sleep(3)
            
            # 尝试从 __INITIAL_STATE__ 获取笔记列表
            try:
                initial_state_script = self.driver.find_element(By.ID, "__INITIAL_STATE__")
                initial_state_json = initial_state_script.get_attribute('textContent')
                initial_state = json.loads(initial_state_json)
                
                # 提取笔记列表
                notes_data = initial_state.get('user', {}).get('notes', [])
                
                if notes_data:
                    for note in notes_data:
                        note_info = {
                            'note_id': note.get('noteId') or note.get('note_id', ''),
                            'xsec_token': note.get('xsecToken', ''),
                            'type': note.get('type', ''),
                            'title': note.get('title', ''),
                            'cover': note.get('cover', {}).get('url', ''),
                        }
                        note_list.append(note_info)
                        
                    logger.success(f"从页面数据中获取到 {len(note_list)} 条笔记")
                    
            except Exception as e:
                logger.debug(f"从 __INITIAL_STATE__ 提取笔记失败: {e}")
                
            # 如果没有从页面数据获取到，则滚动页面加载更多
            if not note_list:
                wait = WebDriverWait(self.driver, self.wait_timeout)
                
                # 持续滚动以加载所有笔记
                last_height = self.driver.execute_script("return document.body.scrollHeight")
                scroll_attempts = 0
                max_scrolls = 20  # 最多滚动 20 次
                
                while scroll_attempts < max_scrolls:
                    # 滚动到底部
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    
                    # 计算新的高度
                    new_height = self.driver.execute_script("return document.body.scrollHeight")
                    
                    # 如果高度没有变化，说明已经到底了
                    if new_height == last_height:
                        break
                        
                    last_height = new_height
                    scroll_attempts += 1
                    
                # 提取所有笔记链接
                try:
                    note_elements = self.driver.find_elements(By.CSS_SELECTOR, "a.cover")
                    
                    for elem in note_elements:
                        note_href = elem.get_attribute("href")
                        if note_href and "/explore/" in note_href:
                            # 解析 note_id
                            parsed = urllib.parse.urlparse(note_href)
                            note_id = parsed.path.split("/")[-1]
                            
                            # 解析 xsec_token
                            query_params = urllib.parse.parse_qs(parsed.query)
                            xsec_token = query_params.get('xsec_token', [''])[0]
                            
                            note_info = {
                                'note_id': note_id,
                                'xsec_token': xsec_token,
                            }
                            note_list.append(note_info)
                            
                    logger.success(f"通过滚动页面获取到 {len(note_elements)} 条笔记链接")
                    
                except Exception as e:
                    logger.error(f"提取笔记链接时出错: {e}")
                    
            success = True
            msg = f"成功获取 {len(note_list)} 条笔记"
            
        except Exception as e:
            success = False
            msg = str(e)
            logger.error(f"获取用户笔记时发生错误: {e}")
            
        return success, msg, note_list
        
    def get_note_info(self, note_url: str, cookies_str: str, proxies: dict = None) -> Tuple[bool, str, Optional[Dict]]:
        """
        获取笔记的详细信息
        
        :param note_url: 笔记 URL
        :param cookies_str: Cookie 字符串
        :param proxies: 代理配置（保留参数以保持接口一致）
        :return: (是否成功, 消息, 响应数据)
        """
        res_json = None
        
        try:
            # 初始化 driver
            if not self.driver:
                self._init_driver(cookies_str)
                
            # 解析 note_id
            urlParse = urllib.parse.urlparse(note_url)
            note_id = urlParse.path.split("/")[-1]
            
            logger.info(f"正在获取笔记 {note_id} 的详细信息")
            self.driver.get(note_url)
            
            # 等待页面加载
            time.sleep(3)
            
            # 从 __INITIAL_STATE__ 中提取笔记数据
            try:
                initial_state_script = self.driver.find_element(By.ID, "__INITIAL_STATE__")
                initial_state_json = initial_state_script.get_attribute('textContent')
                initial_state = json.loads(initial_state_json)
                
                # 提取笔记详情
                note_detail = initial_state.get('note', {}).get('noteDetailMap', {}).get(note_id, {})
                
                if note_detail:
                    # 构造与原 API 一致的返回格式
                    note_card = note_detail.get('note', {})
                    
                    res_json = {
                        "success": True,
                        "msg": "success",
                        "data": {
                            "items": [
                                {
                                    "id": note_id,
                                    "note_card": note_card
                                }
                            ]
                        }
                    }
                    
                    success = True
                    msg = "success"
                    logger.success(f"成功获取笔记 {note_id} 的信息")
                    return success, msg, res_json
                    
            except Exception as e:
                logger.debug(f"从 __INITIAL_STATE__ 提取笔记信息失败: {e}")
                
            # 备用方案：从页面元素提取
            try:
                wait = WebDriverWait(self.driver, self.wait_timeout)
                
                # 等待页面完全加载
                time.sleep(2)
                
                # 提取标题 - 尝试多种选择器
                title = ""
                title_selectors = [
                    "#detail-title",
                    ".title",
                    "[class*='title']",
                    "h1"
                ]
                for selector in title_selectors:
                    try:
                        title_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if title_elem.text.strip():
                            title = title_elem.text.strip()
                            logger.debug(f"通过选择器 {selector} 找到标题: {title}")
                            break
                    except:
                        continue
                    
                # 提取描述 - 尝试多种选择器
                desc = ""
                desc_selectors = [
                    "#detail-desc",
                    ".desc",
                    "[class*='desc']",
                    "[class*='content']"
                ]
                for selector in desc_selectors:
                    try:
                        desc_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if desc_elem.text.strip():
                            desc = desc_elem.text.strip()
                            logger.debug(f"通过选择器 {selector} 找到描述: {desc[:50]}...")
                            break
                    except:
                        continue
                    
                # 提取互动数据 - 改进的策略
                liked_count = "0"
                collected_count = "0"
                comment_count = "0"
                share_count = "0"
                
                # 尝试多种方式提取互动数据
                # 方式1: 查找包含数字的互动按钮
                try:
                    interact_buttons = self.driver.find_elements(By.CSS_SELECTOR, "[class*='interact'], [class*='action'], [class*='engagement']")
                    for button in interact_buttons:
                        button_text = button.text.lower()
                        # 提取按钮中的数字
                        import re
                        numbers = re.findall(r'\d+', button_text)
                        
                        if '赞' in button_text or 'like' in button_text:
                            if numbers:
                                liked_count = numbers[0]
                                logger.debug(f"找到点赞数: {liked_count}")
                        elif '收藏' in button_text or 'collect' in button_text or 'favorite' in button_text:
                            if numbers:
                                collected_count = numbers[0]
                                logger.debug(f"找到收藏数: {collected_count}")
                        elif '评论' in button_text or 'comment' in button_text:
                            if numbers:
                                comment_count = numbers[0]
                                logger.debug(f"找到评论数: {comment_count}")
                        elif '分享' in button_text or 'share' in button_text:
                            if numbers:
                                share_count = numbers[0]
                                logger.debug(f"找到分享数: {share_count}")
                except Exception as e:
                    logger.debug(f"方式1提取互动数据失败: {e}")
                
                # 方式2: 从页面源代码中查找数据
                if liked_count == "0" or collected_count == "0":
                    try:
                        page_source = self.driver.page_source
                        import re
                        
                        # 查找 liked_count
                        liked_match = re.search(r'"liked_count["\s:]+(\d+)', page_source)
                        if liked_match:
                            liked_count = liked_match.group(1)
                            logger.debug(f"从页面源代码找到点赞数: {liked_count}")
                            
                        # 查找 collected_count
                        collected_match = re.search(r'"collected_count["\s:]+(\d+)', page_source)
                        if collected_match:
                            collected_count = collected_match.group(1)
                            logger.debug(f"从页面源代码找到收藏数: {collected_count}")
                            
                        # 查找 comment_count
                        comment_match = re.search(r'"comment_count["\s:]+(\d+)', page_source)
                        if comment_match:
                            comment_count = comment_match.group(1)
                            logger.debug(f"从页面源代码找到评论数: {comment_count}")
                            
                        # 查找 share_count
                        share_match = re.search(r'"share_count["\s:]+(\d+)', page_source)
                        if share_match:
                            share_count = share_match.group(1)
                            logger.debug(f"从页面源代码找到分享数: {share_count}")
                            
                    except Exception as e:
                        logger.debug(f"方式2提取互动数据失败: {e}")
                
                # 方式3: 查找所有包含 window.__INITIAL_STATE__ 的 script 标签
                if liked_count == "0" or collected_count == "0":
                    try:
                        scripts = self.driver.find_elements(By.TAG_NAME, "script")
                        for script in scripts:
                            script_content = script.get_attribute('innerHTML')
                            if script_content and 'liked_count' in script_content:
                                import re
                                # 提取互动数据
                                liked_match = re.search(r'"liked_count"[:\s]*["\']?(\d+)', script_content)
                                if liked_match:
                                    liked_count = liked_match.group(1)
                                    
                                collected_match = re.search(r'"collected_count"[:\s]*["\']?(\d+)', script_content)
                                if collected_match:
                                    collected_count = collected_match.group(1)
                                    
                                comment_match = re.search(r'"comment_count"[:\s]*["\']?(\d+)', script_content)
                                if comment_match:
                                    comment_count = comment_match.group(1)
                                    
                                logger.debug(f"从 script 标签找到互动数据: 赞={liked_count}, 藏={collected_count}, 评={comment_count}")
                                break
                    except Exception as e:
                        logger.debug(f"方式3提取互动数据失败: {e}")
                
                # 构造返回数据
                res_json = {
                    "success": True,
                    "msg": "success",
                    "data": {
                        "items": [
                            {
                                "id": note_id,
                                "note_card": {
                                    "title": title,
                                    "desc": desc,
                                    "type": "normal",
                                    "interact_info": {
                                        "liked_count": liked_count,
                                        "collected_count": collected_count,
                                        "comment_count": comment_count,
                                        "share_count": share_count
                                    },
                                    "tag_list": [],
                                    "time": int(time.time() * 1000),
                                    "user": {}
                                }
                            }
                        ]
                    }
                }
                
                success = True
                msg = "success"
                logger.success(f"成功获取笔记 {note_id} 的信息（通过页面元素）")
                logger.info(f"互动数据: 赞={liked_count}, 藏={collected_count}, 评={comment_count}, 分享={share_count}")
                
            except TimeoutException:
                success = False
                msg = "页面加载超时"
                logger.error(f"获取笔记信息超时: {note_id}")
                
        except Exception as e:
            success = False
            msg = str(e)
            logger.error(f"获取笔记信息时发生错误: {e}")
            
        return success, msg, res_json
        
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("浏览器已关闭")
            
    def __del__(self):
        """析构函数，确保浏览器被关闭"""
        self.close()


# 使用示例
if __name__ == '__main__':
    # 创建实例
    xhs_selenium = XHS_Selenium_Apis(headless=False)  # headless=False 可以看到浏览器操作
    
    cookies_str = 'your_cookies_here'
    
    try:
        # 测试获取用户信息
        user_id = '67a332a2000000000d008358'
        success, msg, user_info = xhs_selenium.get_user_info(user_id, cookies_str)
        logger.info(f'获取用户信息: {success}, {msg}')
        if user_info:
            logger.info(json.dumps(user_info, ensure_ascii=False, indent=2))
            
        # 测试获取用户笔记列表
        user_url = f'https://www.xiaohongshu.com/user/profile/{user_id}'
        success, msg, notes = xhs_selenium.get_user_all_notes(user_url, cookies_str)
        logger.info(f'获取用户笔记: {success}, {msg}, 数量: {len(notes)}')
        
        # 测试获取笔记详情
        if notes:
            note_url = f"https://www.xiaohongshu.com/explore/{notes[0]['note_id']}?xsec_token={notes[0]['xsec_token']}"
            success, msg, note_info = xhs_selenium.get_note_info(note_url, cookies_str)
            logger.info(f'获取笔记详情: {success}, {msg}')
            if note_info:
                logger.info(json.dumps(note_info, ensure_ascii=False, indent=2))
                
    finally:
        # 确保关闭浏览器
        xhs_selenium.close()
