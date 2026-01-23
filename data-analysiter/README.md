# XHS Data Analysis Platform - 三层架构版本

## 🎯 项目概述

这是一个基于三层架构设计的小红书（XHS）数据分析和AI内容生成平台，支持多平台扩展（小红书、Instagram等）。

### 核心功能

1. **创作者网络分析** - 基于内容embedding计算创作者相似度
2. **AI风格生成** - 使用DeepSeek API模仿创作者风格生成内容
3. **数据管理** - MongoDB存储，Repository Pattern数据访问
4. **多平台支持** - 可扩展架构，支持添加新平台

## 🏗️ 架构设计

采用经典的三层架构（Three-Tier Architecture）：

```
┌─────────────────────────────────────────┐
│  Frontend (Next.js)                      │  ← 用户界面
├─────────────────────────────────────────┤
│  Backend Service (FastAPI)               │  ← 业务逻辑
├─────────────────────────────────────────┤
│  Database Layer (MongoDB + Repository)   │  ← 数据访问
└─────────────────────────────────────────┘
```

详细架构文档：[ARCHITECTURE.md](./docs/ARCHITECTURE.md)

## 📊 数据库设计

### MongoDB Collections

| Collection | 用途 | 数量 |
|-----------|------|------|
| `user_profiles` | 创作者档案 | 8条 |
| `user_snapshots` | 笔记快照 | 8条 |
| `user_embeddings` | 向量embeddings (512维) | 8条 |
| `creator_networks` | 相似度网络 | 1条 |
| `style_prompts` | AI提示词模板 | 1条 |
| `platform_configs` | 平台配置 | 0条 |

## 🚀 快速开始

### 前置条件

- Python 3.9+
- Node.js 18+
- MongoDB Atlas账号
- DeepSeek API Key
- TikHub API Token（用于数据采集）

### 1. 数据采集（首次使用）

```bash
# 使用 TikHub API 采集小红书用户数据
cd tikhub-data-collector
cp .env.example .env  # 配置环境变量
source ../data-analysiter/.venv/bin/activate  # 使用已有虚拟环境
python test_user_tikhub.py
```

详见：[tikhub-data-collector/README.md](../tikhub-data-collector/README.md)

### 2. 安装依赖

```bash
# 后端
cd data-analysiter
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 前端
cd xhs-analyser-frontend
npm install
```

### 3. 数据迁移（如需从JSON迁移）

```bash
cd data-analysiter
source .venv/bin/activate
python -m database.migrate_data
```

### 4. 启动服务

```bash
# 后端（Terminal 1）
cd data-analysiter
cp .env.example .env  # 首次运行需配置
./start.sh  # 会自动加载 .env

# 前端（Terminal 2）
cd xhs-analyser-frontend
npm run dev
```

### 4. 访问应用

- 前端: http://localhost:3000
- 风格生成器: http://localhost:3000/zh/style-generator
- API文档: http://localhost:5001/docs
- 健康检查: http://localhost:5001/api/health

详细指南：[QUICKSTART_V2.md](./docs/QUICKSTART_V2.md)

## 📁 项目结构

```
data-analysiter/                  # 后端项目
├── database/                     # 数据库层 ⭐
│   ├── connection.py            # MongoDB连接管理
│   ├── models.py                # Pydantic数据模型
│   ├── repositories.py          # Repository Pattern
│   └── migrate_data.py          # 数据迁移脚本
├── api/                          # API层 ⭐
│   ├── server.py                # FastAPI主应用
│   ├── routers/                 # API路由
│   │   ├── style_router.py     # 风格生成路由
│   │   └── creator_router.py   # 创作者数据路由
│   └── services/                # 业务逻辑 ⭐
│       └── style_service.py    # 风格生成服务
├── generators/                   # 数据生成器
│   └── creators.py              # 网络生成
├── processors/                   # 数据处理
│   ├── analyze.py               # 数据分析
│   ├── clean_data.py            # 数据清洗
│   └── pipeline.py              # 处理流程
├── tests/                        # 测试工具
│   ├── test_embedding.py        # Embedding测试
│   └── test_user_tikhub.py      # TikHub数据采集
├── data/                         # 数据文件
│   ├── user_profiles/           # 创作者档案
│   ├── snapshots/               # 笔记快照
│   ├── analyses/                # Embeddings
│   └── creators_data.json       # 网络数据
├── docs/                         # 完整文档 ⭐
│   ├── ARCHITECTURE.md          # 架构设计
│   ├── QUICKSTART_V2.md         # 快速开始
│   ├── MIGRATION_SUMMARY.md     # 迁移总结
│   └── COMMANDS.md              # 常用命令
├── start.sh                      # 统一启动脚本 ⭐
├── requirements.txt              # Python依赖
└── README.md                     # 本文件
```

## 🔌 API端点

### 创作者数据

- `GET /api/creators/network` - 获取创作者相似度网络
- `GET /api/creators/list` - 获取所有创作者列表
- `GET /api/creators/{name}` - 获取创作者详情

### AI风格生成

- `POST /api/style/generate` - 生成风格化内容
  ```json
  {
    "creator_name": "Ada在美国",
    "user_topic": "美国留学经验分享",
    "platform": "xiaohongshu"
  }
  ```
- `GET /api/style/creators` - 获取可用的创作者列表

### 系统

- `GET /api/health` - 健康检查
- `GET /` - API信息

完整API文档：http://localhost:5001/docs

## 🛠️ 技术栈

### 后端
- **FastAPI** - 高性能Web框架
- **Pydantic** - 数据验证
- **pymongo** - MongoDB客户端
- **OpenAI SDK** - DeepSeek API调用
- **FlagModel** - BAAI/bge-small-zh-v1.5 (512维embedding)

### 前端
- **Next.js 16** - React框架
- **TypeScript** - 类型安全
- **Tailwind CSS** - 样式
- **Turbopack** - 快速构建

### 数据库
- **MongoDB Atlas** - 云数据库
- **Collections**: 6个核心集合

### AI服务
- **DeepSeek API** - 内容生成
- **Model**: deepseek-chat

## 📈 数据流示例

### AI风格生成流程

```
用户输入
  ↓
[Frontend] POST /api/style/generate
  ↓
[Router] style_router.py
  ↓
[Service] StyleGenerationService
  ├→ [Database] UserProfileRepository.get_profile_by_nickname()
  ├→ [Database] UserSnapshotRepository.get_notes()
  ├→ [Database] StylePromptRepository.get_by_type()
  ↓
[Service] 构建提示词
  ↓
[AI] DeepSeek API
  ↓
[Service] 格式化结果
  ↓
[Router] 返回JSON
  ↓
[Frontend] 显示生成内容
```

## 🎨 特性

### 1. Repository Pattern
所有数据访问通过Repository层，业务逻辑与数据库解耦。

```python
# 业务层不直接访问数据库
from database import UserProfileRepository

repo = UserProfileRepository()
profile = repo.get_profile_by_nickname("Ada在美国")
```

### 2. 依赖注入
Service层通过构造函数注入Repository依赖。

```python
class StyleGenerationService:
    def __init__(self):
        self.profile_repo = UserProfileRepository()
        self.snapshot_repo = UserSnapshotRepository()
```

### 3. 数据验证
使用Pydantic进行数据模型验证。

```python
class UserProfile(BaseModel):
    platform: PlatformType
    user_id: str
    nickname: str
    profile_data: UserProfileData
```

### 4. 多平台支持
通过`platform`参数支持不同平台。

```python
# 小红书
service.generate_content("Ada在美国", "留学生活", "xiaohongshu")

# Instagram (未来)
service.generate_content("user123", "travel", "instagram")
```

## 🔧 开发

### 运行测试

```bash
# 测试数据库连接
python -c "from database.connection import test_connection; test_connection()"

# 测试数据查询
python -c "from database import UserProfileRepository; repo = UserProfileRepository(); print(repo.count())"
```

### 数据库操作

```python
# 进入Python交互式shell
from database import *

# 查询所有创作者
repo = UserProfileRepository()
profiles = repo.get_all_profiles()

# 查询笔记
snapshot_repo = UserSnapshotRepository()
notes = snapshot_repo.get_notes("586f442550c4b43de8f114b0", limit=5)

# 查询embedding
embedding_repo = UserEmbeddingRepository()
embedding = embedding_repo.get_by_user_id("586f442550c4b43de8f114b0")
```

### 添加新平台

1. 在`database/models.py`中添加平台类型
2. 在`platform_configs`集合中添加配置
3. 业务逻辑自动支持（通过platform参数）

## 📊 当前数据

- **创作者数量**: 8位
- **笔记总数**: ~250+条
- **相似度边**: 9条（阈值≥0.7）
- **Embedding维度**: 512

创作者列表：
1. 星球研究所InstituteforPlanet
2. 硅谷樱花小姐姐🌸
3. 无穷小亮的科普日常
4. 小熊说你超有爱
5. 小Lin说
6. 大圆镜科普
7. Ada在美国
8. 所长林超

## 🚧 待实现功能

- [ ] 前端API调用更新（如需要）
- [ ] 单元测试
- [ ] API认证（JWT）
- [ ] 缓存层（Redis）
- [ ] 日志系统
- [ ] 监控告警
- [ ] Docker容器化
- [ ] CI/CD

## 📝 许可

本项目仅供学习和研究使用。

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 支持

如有问题，请查看：
- [架构文档](./docs/ARCHITECTURE.md)
- [快速开始](./docs/QUICKSTART_V2.md)
- [API文档](http://localhost:5001/docs)

---

**Note**: 这是MVP版本，已实现核心功能，采用三层架构为未来扩展奠定基础。
