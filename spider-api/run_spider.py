"""
GitHub Actions 定时爬虫执行脚本

这个脚本会：
1. 从环境变量读取配置
2. 爬取指定用户的数据
3. 爬取笔记详情
4. 存储到 MongoDB
5. 生成执行报告
"""

import os
import sys
import asyncio
import datetime
from loguru import logger
from typing import List, Dict
import json

# 配置日志
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# 配置 loguru 输出到文件和控制台
logger.remove()  # 移除默认处理器
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    f"{log_dir}/spider_{{time:YYYY-MM-DD}}.log",
    rotation="500 MB",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG"
)

from apis.xhs_pc_apis import XHS_Apis
from main import Data_Spider, safe_int, get_database
from dotenv import load_dotenv
import motor.motor_asyncio

# 加载环境变量
load_dotenv()

# 默认要爬取的用户URL列表（如果环境变量未设置）
DEFAULT_USER_URLS = [
    # 在这里添加你想要定时爬取的用户URL
    # "https://www.xiaohongshu.com/user/profile/xxx?xsec_token=xxx",
]

class SpiderRunner:
    """爬虫执行器"""
    
    def __init__(self):
        self.data_spider = Data_Spider()
        self.cookies = os.getenv("COOKIES")
        self.mongo_uri = os.getenv("MONGO_URI")
        
        if not self.cookies:
            raise ValueError("❌ COOKIES 环境变量未设置！")
        if not self.mongo_uri:
            raise ValueError("❌ MONGO_URI 环境变量未设置！")
        
        # 初始化 MongoDB 连接
        self.db_client = motor.motor_asyncio.AsyncIOMotorClient(self.mongo_uri)
        self.database = self.db_client["xhs_data"]
        self.user_collection = self.database.get_collection("users")
        self.note_collection = self.database.get_collection("notes")
        
        # 统计信息
        self.stats = {
            "start_time": datetime.datetime.now(datetime.timezone.utc),
            "users_processed": 0,
            "users_failed": 0,
            "notes_processed": 0,
            "notes_failed": 0,
            "errors": []
        }
    
    def get_user_urls(self) -> List[str]:
        """获取要爬取的用户URL列表"""
        # 1. 从环境变量获取（用于手动触发）
        env_urls = os.getenv("USER_URLS", "").strip()
        if env_urls:
            urls = [url.strip() for url in env_urls.split(",") if url.strip()]
            logger.info(f"从环境变量获取到 {len(urls)} 个用户URL")
            return urls
        
        # 2. 从配置文件获取
        config_file = "spider_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    urls = config.get("user_urls", [])
                    logger.info(f"从配置文件获取到 {len(urls)} 个用户URL")
                    return urls
            except Exception as e:
                logger.error(f"读取配置文件失败: {e}")
        
        # 3. 使用默认列表
        if DEFAULT_USER_URLS:
            logger.info(f"使用默认用户URL列表 ({len(DEFAULT_USER_URLS)} 个)")
            return DEFAULT_USER_URLS
        
        logger.warning("⚠️ 未找到任何用户URL，将不执行爬取")
        return []
    
    async def crawl_user(self, user_url: str) -> Dict:
        """爬取单个用户的数据"""
        try:
            logger.info(f"=" * 60)
            logger.info(f"开始爬取用户: {user_url}")
            
            import urllib.parse
            
            # 1. 从URL提取user_id
            urlParse = urllib.parse.urlparse(user_url)
            user_id = urlParse.path.split("/")[-1]
            
            # 2. 获取用户基础信息
            success_info, msg_info, user_info_response = self.data_spider.xhs_apis.get_user_info(user_id, self.cookies)
            user_name = "未知用户"
            if success_info and user_info_response.get('data', {}).get('basic_info'):
                basic_info = user_info_response['data']['basic_info']
                user_name = basic_info.get('nickname', '未知用户')
            
            logger.info(f"用户名: {user_name}")
            
            # 3. 获取用户笔记列表
            user_notes, success, msg = self.data_spider.fetch_user_all_notes(user_url, self.cookies)
            
            if not success:
                logger.error(f"获取用户笔记失败: {msg}")
                self.stats["users_failed"] += 1
                self.stats["errors"].append(f"用户 {user_name}: {msg}")
                return {"success": False, "user_name": user_name, "error": msg}
            
            logger.info(f"获取到 {len(user_notes)} 条笔记")
            
            # 4. 获取用户详细信息（包括粉丝数）
            user_detail, success_detail, msg_detail = self.data_spider.fetch_user_detailed_info(
                user_id, user_name, self.cookies
            )
            
            # 5. 计算总互动数
            kvs = urlParse.query.split('&') if urlParse.query else []
            kvDist = {kv.split('=')[0]: kv.split('=')[1] for kv in kvs if '=' in kv}
            xsec_token = kvDist.get('xsec_token', '')
            xsec_source = kvDist.get('xsec_source', 'pc_search')
            
            total_likes = 0
            total_collects = 0
            total_comments = 0
            
            success_notes, msg_notes, res_json = self.data_spider.xhs_apis.get_user_note_info(
                user_id, '', self.cookies, xsec_token, xsec_source
            )
            
            if success_notes and res_json and res_json.get('data', {}).get('notes'):
                notes = res_json['data']['notes']
                for note in notes:
                    interact_info = note.get('interact_info', {})
                    total_likes += safe_int(interact_info.get('liked_count'))
                    total_collects += safe_int(interact_info.get('collected_count'))
                    total_comments += safe_int(interact_info.get('comment_count'))
            
            fan_count = safe_int(user_detail.get('fans', '0')) if user_detail else 0
            
            # 6. 存储到 MongoDB
            user_snapshot = {
                "last_updated": datetime.datetime.now(datetime.timezone.utc),
                "user_url": user_url,
                "red_id": user_detail.get('red_id', '') if user_detail else '',
                "user_name": user_name,
                "note_count": len(user_notes),
                "note_urls": user_notes,
                "fan_count": fan_count,
                "total_likes": total_likes,
                "total_collects": total_collects,
                "total_comments": total_comments,
            }
            
            await self.user_collection.insert_one(user_snapshot)
            logger.success(f"✅ 用户数据已存储: {user_name} | 粉丝: {fan_count} | 笔记: {len(user_notes)}")
            
            self.stats["users_processed"] += 1
            
            return {
                "success": True,
                "user_name": user_name,
                "note_count": len(user_notes),
                "note_urls": user_notes,
                "fan_count": fan_count
            }
            
        except Exception as e:
            logger.error(f"爬取用户 {user_url} 时发生错误: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.stats["users_failed"] += 1
            self.stats["errors"].append(f"用户 {user_url}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def crawl_note(self, note_url: str) -> Dict:
        """爬取单篇笔记的详情"""
        try:
            content_snapshot, success, msg = self.data_spider.fetch_note_details(note_url, self.cookies)
            
            if not success:
                logger.warning(f"获取笔记失败: {note_url} - {msg}")
                self.stats["notes_failed"] += 1
                return {"success": False, "note_url": note_url, "error": msg}
            
            # 存储到 MongoDB
            await self.note_collection.update_one(
                {'content_id': content_snapshot['content_id']},
                {'$set': content_snapshot},
                upsert=True
            )
            
            logger.info(f"✅ 笔记已存储: {content_snapshot['content_id']} | 点赞: {content_snapshot['likes']}")
            self.stats["notes_processed"] += 1
            
            return {"success": True, "content_id": content_snapshot['content_id']}
            
        except Exception as e:
            logger.error(f"爬取笔记 {note_url} 时发生错误: {e}")
            self.stats["notes_failed"] += 1
            return {"success": False, "note_url": note_url, "error": str(e)}
    
    async def run(self):
        """执行爬虫任务"""
        logger.info("=" * 60)
        logger.info("🚀 开始执行定时爬虫任务")
        logger.info(f"执行时间: {self.stats['start_time']}")
        logger.info("=" * 60)
        
        # 1. 获取要爬取的用户列表
        user_urls = self.get_user_urls()
        
        if not user_urls:
            logger.warning("⚠️ 没有要爬取的用户，任务结束")
            return
        
        logger.info(f"共需爬取 {len(user_urls)} 个用户")
        
        # 2. 爬取用户数据
        user_results = []
        for i, user_url in enumerate(user_urls, 1):
            logger.info(f"\n进度: {i}/{len(user_urls)}")
            result = await self.crawl_user(user_url)
            user_results.append(result)
            
            # 添加延迟，避免被反爬
            if i < len(user_urls):
                await asyncio.sleep(3)
        
        # 3. 是否爬取笔记详情
        crawl_notes = os.getenv("CRAWL_NOTES", "true").lower() == "true"
        
        if crawl_notes:
            logger.info("\n" + "=" * 60)
            logger.info("开始爬取笔记详情")
            logger.info("=" * 60)
            
            # 收集所有笔记URL
            all_note_urls = []
            for result in user_results:
                if result.get("success") and result.get("note_urls"):
                    all_note_urls.extend(result["note_urls"])
            
            logger.info(f"共需爬取 {len(all_note_urls)} 篇笔记")
            
            # 爬取笔记（限制数量，避免超时）
            max_notes = int(os.getenv("MAX_NOTES_PER_RUN", "50"))
            notes_to_crawl = all_note_urls[:max_notes]
            
            if len(all_note_urls) > max_notes:
                logger.warning(f"⚠️ 笔记数量超过限制，本次仅爬取前 {max_notes} 篇")
            
            for i, note_url in enumerate(notes_to_crawl, 1):
                logger.info(f"\n笔记进度: {i}/{len(notes_to_crawl)}")
                await self.crawl_note(note_url)
                
                # 添加延迟
                if i < len(notes_to_crawl):
                    await asyncio.sleep(2)
        
        # 4. 生成执行报告
        self.generate_report()
    
    def generate_report(self):
        """生成执行报告"""
        end_time = datetime.datetime.now(datetime.timezone.utc)
        duration = end_time - self.stats["start_time"]
        
        logger.info("\n" + "=" * 60)
        logger.info("📊 执行报告")
        logger.info("=" * 60)
        logger.info(f"开始时间: {self.stats['start_time']}")
        logger.info(f"结束时间: {end_time}")
        logger.info(f"执行时长: {duration}")
        logger.info(f"")
        logger.info(f"用户统计:")
        logger.info(f"  - 成功: {self.stats['users_processed']}")
        logger.info(f"  - 失败: {self.stats['users_failed']}")
        logger.info(f"")
        logger.info(f"笔记统计:")
        logger.info(f"  - 成功: {self.stats['notes_processed']}")
        logger.info(f"  - 失败: {self.stats['notes_failed']}")
        
        if self.stats["errors"]:
            logger.info(f"")
            logger.warning(f"错误列表 ({len(self.stats['errors'])} 个):")
            for error in self.stats["errors"]:
                logger.warning(f"  - {error}")
        
        logger.info("=" * 60)
        
        # 保存报告到文件
        report = {
            "start_time": self.stats["start_time"].isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration.total_seconds(),
            "users_processed": self.stats["users_processed"],
            "users_failed": self.stats["users_failed"],
            "notes_processed": self.stats["notes_processed"],
            "notes_failed": self.stats["notes_failed"],
            "errors": self.stats["errors"]
        }
        
        report_file = f"{log_dir}/report_{self.stats['start_time'].strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 报告已保存: {report_file}")


async def main():
    """主函数"""
    try:
        runner = SpiderRunner()
        await runner.run()
        
        # 判断是否成功
        if runner.stats["users_failed"] > 0 or runner.stats["notes_failed"] > 0:
            logger.warning("⚠️ 部分任务执行失败")
            sys.exit(1)
        else:
            logger.success("✅ 所有任务执行成功")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"❌ 爬虫执行失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
