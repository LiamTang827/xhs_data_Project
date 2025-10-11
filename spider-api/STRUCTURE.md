# 🏗️ 项目结构说明

## 📁 完整目录结构

```
spider-api/
├── 📄 main.py                      # FastAPI 主应用
├── 📄 run_spider.py                # GitHub Actions 爬虫执行脚本 ⭐
├── 📄 requirements.txt             # Python 依赖
├── 📄 Dockerfile                   # Docker 配置
├── 📄 package.json                 # Node.js 依赖（如果有）
│
├── 📁 .github/                     # GitHub 配置 ⭐
│   └── workflows/
│       └── spider.yml              # GitHub Actions 工作流配置 ⭐
│
├── 📁 apis/                        # API 封装
│   ├── __init__.py
│   ├── xhs_creator_apis.py         # 创作者中心 API
│   └── xhs_pc_apis.py              # PC 端 API
│
├── 📁 xhs_utils/                   # 工具函数
│   ├── __init__.py
│   ├── common_util.py              # 通用工具
│   ├── cookie_util.py              # Cookie 处理
│   ├── data_util.py                # 数据处理
│   ├── database.py                 # 数据库连接
│   ├── xhs_creator_util.py         # 创作者工具
│   └── xhs_util.py                 # 小红书工具
│
├── 📁 static/                      # 静态资源（JS 加密文件等）
│   ├── xhs_creator_xs.js
│   ├── xhs_xray_pack1.js
│   ├── xhs_xray_pack2.js
│   ├── xhs_xray.js
│   └── xhs_xs_xsc_56.js
│
├── 📁 utils/                       # 辅助工具
│   └── decorator.py                # 装饰器
│
├── 📁 logs/                        # 日志文件 ⭐
│   ├── spider_2025-10-11.log       # 每日日志
│   └── report_20251011_080000.json # 执行报告
│
├── 📄 .env                         # 环境变量（不提交）⚠️
├── 📄 .env.example                 # 环境变量示例
├── 📄 .gitignore                   # Git 忽略文件
│
├── 📄 spider_config.json           # 爬虫配置（不提交）⚠️ ⭐
├── 📄 spider_config.json.example   # 配置示例 ⭐
│
├── 📄 README.md                    # 项目说明
├── 📄 QUICKSTART.md                # 快速开始指南 ⭐
├── 📄 GITHUB_ACTIONS_GUIDE.md      # GitHub Actions 详细指南 ⭐
├── 📄 DEBUG_REPORT.md              # 调试报告
├── 📄 STRUCTURE.md                 # 本文件
│
├── 📄 test.py                      # 测试脚本
└── 📄 test_note_format.py          # 笔记格式测试

⭐ = GitHub Actions 相关文件
⚠️ = 敏感文件，不要提交到 Git
```

---

## 🎯 核心文件说明

### 1. **main.py**
- **作用**：FastAPI 主应用，提供 REST API 接口
- **端点**：
  - `GET /user/notes` - 获取用户笔记列表
  - `GET /note/info` - 获取笔记详情
- **用途**：本地开发和 API 服务

### 2. **run_spider.py** ⭐
- **作用**：GitHub Actions 定时爬虫执行脚本
- **功能**：
  - 读取配置（用户列表）
  - 批量爬取用户数据
  - 批量爬取笔记详情
  - 存储到 MongoDB
  - 生成执行报告
- **用途**：自动化数据采集

### 3. **.github/workflows/spider.yml** ⭐
- **作用**：GitHub Actions 工作流配置
- **定义**：
  - 触发条件（定时 + 手动）
  - 运行环境（Ubuntu + Python）
  - 执行步骤
  - 日志上传
- **用途**：自动化任务调度

### 4. **spider_config.json** ⭐
- **作用**：爬虫配置文件
- **内容**：
  - 要爬取的用户 URL 列表
  - 每次运行的笔记数量限制
  - 爬取间隔时间
- **⚠️ 重要**：包含真实数据，不要提交到 Git

---

## 🔄 工作流程

### 本地开发流程

```
1. 启动 FastAPI 服务
   uvicorn main:app --reload

2. 调用 API 接口
   GET /user/notes?user_url=xxx
   GET /note/info?note_url=xxx

3. 数据存储到 MongoDB
```

### GitHub Actions 自动化流程

```
1. 定时触发（或手动触发）
   ↓
2. GitHub Actions 启动
   ↓
3. 检出代码
   ↓
4. 安装 Python 依赖
   ↓
5. 运行 run_spider.py
   ├── 读取 spider_config.json
   ├── 爬取用户数据
   ├── 爬取笔记详情
   └── 存储到 MongoDB
   ↓
6. 生成日志和报告
   ↓
7. 上传日志到 Artifacts
   ↓
8. 发送通知（可选）
```

---

## 📊 数据流向

```
小红书网站
    ↓
 XHS_Apis (apis/xhs_pc_apis.py)
    ↓
 Data_Spider (main.py)
    ↓
 run_spider.py
    ↓
 MongoDB Atlas (xhs_data 数据库)
    ├── users 集合（用户快照）
    └── notes 集合（笔记快照）
```

---

## 🔐 敏感文件管理

### ❌ 不要提交到 Git

```bash
.env                    # 环境变量（MONGO_URI, COOKIES）
spider_config.json      # 包含真实用户URL
logs/                   # 日志文件
*.log                   # 所有日志
```

### ✅ 可以提交到 Git

```bash
.env.example            # 环境变量示例
spider_config.json.example  # 配置文件示例
.gitignore              # 确保敏感文件不被提交
*.md                    # 所有文档
```

---

## 🛠️ 配置文件优先级

### 环境变量

```
1. GitHub Secrets（最高优先级）
   - 用于 GitHub Actions
   - Settings → Secrets

2. 环境变量
   - export MONGO_URI="xxx"
   - export COOKIES="xxx"

3. .env 文件
   - 本地开发使用
   - 不提交到 Git
```

### 用户列表

```
1. 环境变量 USER_URLS（最高优先级）
   - 手动触发时指定
   - export USER_URLS="url1,url2"

2. spider_config.json
   - 主要配置方式
   - 持久化配置

3. DEFAULT_USER_URLS（最低优先级）
   - run_spider.py 中的默认值
   - 兜底方案
```

---

## 📦 依赖关系

### Python 依赖（requirements.txt）

```
fastapi              # Web 框架
uvicorn              # ASGI 服务器
motor                # MongoDB 异步驱动
pymongo              # MongoDB 同步驱动
loguru               # 日志库
python-dotenv        # 环境变量加载
requests             # HTTP 请求
pydantic             # 数据验证
```

### 外部服务依赖

```
MongoDB Atlas        # 云数据库
GitHub Actions       # CI/CD 平台
小红书 API           # 数据源
```

---

## 🔧 配置检查清单

### 本地开发

- [ ] 创建 `.env` 文件
- [ ] 配置 `MONGO_URI`
- [ ] 配置 `COOKIES`
- [ ] 安装 Python 依赖
- [ ] 测试 MongoDB 连接
- [ ] 启动 FastAPI 服务

### GitHub Actions

- [ ] 创建 `spider_config.json`
- [ ] 配置 GitHub Secrets（`MONGO_URI`, `COOKIES`）
- [ ] 提交代码到 GitHub
- [ ] 手动触发测试
- [ ] 查看执行日志
- [ ] 验证数据库数据
- [ ] 启用定时任务

---

## 📝 开发规范

### 命名规范

```python
# 文件名：小写下划线
run_spider.py
xhs_pc_apis.py

# 类名：大驼峰
class Data_Spider:
class SpiderRunner:

# 函数名：小写下划线
def fetch_user_notes():
def safe_int():

# 变量名：小写下划线
user_url = "xxx"
note_list = []
```

### 日志规范

```python
logger.info("正常信息")
logger.success("成功操作")
logger.warning("警告信息")
logger.error("错误信息")
logger.debug("调试信息")
```

### 错误处理

```python
try:
    # 执行操作
    result = do_something()
except Exception as e:
    logger.error(f"操作失败: {e}")
    import traceback
    logger.error(traceback.format_exc())
    return None, False, str(e)
```

---

## 🎨 代码组织

### main.py（API 服务）

```python
1. 导入和初始化
2. 辅助函数（safe_int）
3. Data_Spider 类
   - fetch_user_detailed_info()
   - fetch_user_all_notes()
   - fetch_note_details()
4. Pydantic 模型
5. API 端点
   - /user/notes
   - /note/info
```

### run_spider.py（定时任务）

```python
1. 日志配置
2. SpiderRunner 类
   - get_user_urls()
   - crawl_user()
   - crawl_note()
   - run()
   - generate_report()
3. main() 函数
```

---

## 🚀 扩展建议

### 添加新功能

1. **添加新的 API 端点**
   - 在 `main.py` 中添加端点
   - 在 `Data_Spider` 中添加方法

2. **添加新的爬虫任务**
   - 在 `run_spider.py` 中添加方法
   - 更新配置文件格式

3. **添加通知功能**
   - 在 `.github/workflows/spider.yml` 中添加步骤
   - 支持 Webhook、邮件等

### 性能优化

```python
# 并发爬取
import asyncio
tasks = [crawl_note(url) for url in urls]
await asyncio.gather(*tasks)

# 数据缓存
from functools import lru_cache
@lru_cache(maxsize=100)
def get_user_info(user_id):
    pass
```

---

## 📚 相关文档

- [快速开始](./QUICKSTART.md) - 5 分钟配置指南
- [详细指南](./GITHUB_ACTIONS_GUIDE.md) - 完整的 GitHub Actions 文档
- [调试报告](./DEBUG_REPORT.md) - 问题排查和解决方案
- [README](./README.md) - 项目概述

---

**更新时间**: 2025-10-11  
**版本**: v1.0
