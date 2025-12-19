# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

# 基础配置
PLATFORM = "xhs"  # 平台，xhs | dy | ks | bili | wb | tieba | zhihu
KEYWORDS = "大圆镜科普"  # 关键词搜索配置，以英文逗号分隔
LOGIN_TYPE = "qrcode"  # qrcode or phone or cookie
COOKIES = "a1=19933a02683j19f3qydy6m7h8mrp45jnbj14l6xap30000242868; webId=a30219d304de8ae9d36cb73c861122fe; gid=yjjqq08qyyD0yjjqq08JKVKCYqVyjiqAvfvKy0U6WxY6F4q8U42VI1888J4JYKY80jijqSK4; abRequestId=a30219d304de8ae9d36cb73c861122fe; x-user-id-creator.xiaohongshu.com=6105160100000000010038fd; customerClientId=373508853109785; access-token-creator.xiaohongshu.com=customer.creator.AT-68c517564780582133317634uzj5xjr7hdkq65ie; galaxy_creator_session_id=lxThO4ooSRHAKKfaW94pkXKOpRUkFc6UYJMY; galaxy.creator.beaker.session.id=1761312732041046360560; webBuild=4.85.1; xsecappid=xhs-pc-web; websectiga=2845367ec3848418062e761c09db7caf0e8b79d132ccdd1a4f8e64a11d0cac0d; sec_poison_id=f3553b1b-22a1-462e-8e9e-2fbe3753164f; web_session=040069b07155495668ab3ce32d3b4b035c9c69; unread={%22ub%22:%226917159a000000000500103a%22%2C%22ue%22:%2269182f19000000001b021575%22%2C%22uc%22:29}; loadts=1763224416130"  # 登录 Cookie 信息，登录方式为 cookie 时必填
CRAWLER_TYPE = (
    "detail"  # 爬取类型，search(关键词搜索) | detail(帖子详情)| creator(创作者主页数据)
)
# 是否开启 IP 代理
ENABLE_IP_PROXY = False

# 代理IP池数量
IP_PROXY_POOL_COUNT = 2

# 代理IP提供商名称
IP_PROXY_PROVIDER_NAME = "kuaidaili"  # kuaidaili | wandouhttp

# 设置为True不会打开浏览器（无头浏览器）
# 设置False会打开一个浏览器
# 小红书如果一直扫码登录不通过，打开浏览器手动过一下滑动验证码
# 抖音如果一直提示失败，打开浏览器看下是否扫码登录之后出现了手机号验证，如果出现了手动过一下再试。
HEADLESS = False

# 是否保存登录状态
SAVE_LOGIN_STATE = True

# ==================== CDP (Chrome DevTools Protocol) 配置 ====================
# 是否启用CDP模式 - 使用用户现有的Chrome/Edge浏览器进行爬取，提供更好的反检测能力
# 启用后将自动检测并启动用户的Chrome/Edge浏览器，通过CDP协议进行控制
# 这种方式使用真实的浏览器环境，包括用户的扩展、Cookie和设置，大大降低被检测的风险
ENABLE_CDP_MODE = True

# CDP调试端口，用于与浏览器通信
# 如果端口被占用，系统会自动尝试下一个可用端口
CDP_DEBUG_PORT = 9222

# 自定义浏览器路径（可选）
# 如果为空，系统会自动检测Chrome/Edge的安装路径
# Windows示例: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
# macOS示例: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CUSTOM_BROWSER_PATH = ""

# CDP模式下是否启用无头模式
# 注意：即使设置为True，某些反检测功能在无头模式下可能效果不佳
CDP_HEADLESS = False

# 浏览器启动超时时间（秒）
BROWSER_LAUNCH_TIMEOUT = 60

# 是否在程序结束时自动关闭浏览器
# 设置为False可以保持浏览器运行，便于调试
AUTO_CLOSE_BROWSER = True

# 数据保存类型选项配置,支持四种类型：csv、db、json、sqlite, 最好保存到DB，有排重的功能。
SAVE_DATA_OPTION = "mongodb"  # csv or db or json or sqlite

# 用户浏览器缓存的浏览器文件配置
USER_DATA_DIR = "%s_user_data_dir"  # %s will be replaced by platform name

# 爬取开始页数 默认从第一页开始
START_PAGE = 1

# 爬取视频/帖子的数量控制
CRAWLER_MAX_NOTES_COUNT = 5

# 并发爬虫数量控制
MAX_CONCURRENCY_NUM = 1

# 是否开启爬媒体模式（包含图片或视频资源），默认不开启爬媒体
ENABLE_GET_MEIDAS = False

# 是否开启爬评论模式, 默认开启爬评论
ENABLE_GET_COMMENTS = False

# 爬取一级评论的数量控制(单视频/帖子)
CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = 10

# 是否开启爬二级评论模式, 默认不开启爬二级评论
# 老版本项目使用了 db, 则需参考 schema/tables.sql line 287 增加表字段
ENABLE_GET_SUB_COMMENTS = False

# 词云相关
# 是否开启生成评论词云图
ENABLE_GET_WORDCLOUD = False
# 自定义词语及其分组
# 添加规则：xx:yy 其中xx为自定义添加的词组，yy为将xx该词组分到的组名。
CUSTOM_WORDS = {
    "零几": "年份",  # 将“零几”识别为一个整体
    "高频词": "专业术语",  # 示例自定义词
}

# 停用(禁用)词文件路径
STOP_WORDS_FILE = "./docs/hit_stopwords.txt"

# 中文字体文件路径
FONT_PATH = "./docs/STZHONGS.TTF"

# 爬取间隔时间
CRAWLER_MAX_SLEEP_SEC = 2

from .bilibili_config import *
from .xhs_config import *
from .dy_config import *
from .ks_config import *
from .weibo_config import *
from .tieba_config import *
from .zhihu_config import *

# 如果在环境变量中配置了 MONGO_URI（例如在 .env），则默认将数据存储选项切换到 mongodb
import os
import pathlib

# 安全地从本模块同级目录下的 `.env` 加载环境变量（仅当变量未被外部设置时）
# 目的：在直接运行 `python main.py` 时，能发现保存在 `MediaCrawler/.env` 的配置
try:
    if not os.getenv("MONGO_URI"):
        # Look for `.env` at the package root (MediaCrawler/.env), not the config/ folder
        env_path = pathlib.Path(__file__).resolve().parents[1] / ".env"
        if env_path.exists():
            try:
                text = env_path.read_text(encoding="utf-8")
                for line in text.splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    os.environ.setdefault(k, v)
            except Exception:
                # 不要在启动时因为 .env 读取失败而中断程序
                pass
except Exception:
    pass

if os.getenv("MONGO_URI"):
    SAVE_DATA_OPTION = "mongodb"
