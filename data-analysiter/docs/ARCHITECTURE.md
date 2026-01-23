# 三层架构设计文档

## 📋 概述

本项目采用三层架构（Three-Tier Architecture）设计，实现了数据层、业务逻辑层和表示层的完全分离，为多平台扩展（小红书、Instagram等）奠定基础。

## 🏗️ 架构设计

```
┌──────────────────────────────────────────────────────────┐
│                    Frontend Layer                         │
│                 (xhs-analyser-frontend)                   │
│  - Next.js 16.1.0 with Turbopack                         │
│  - React Components                                       │
│  - API Client (fetch)                                     │
│  - Port: 3000                                            │
└─────────────────────┬────────────────────────────────────┘
                      │ HTTP/REST API
┌─────────────────────▼────────────────────────────────────┐
│                   Backend Service Layer                   │
│                   (data-analysiter/api)                   │
│  - FastAPI Application                                    │
│  - Routers: style_router, creator_router                 │
│  - Services: StyleGenerationService                       │
│  - AI Integration: DeepSeek API                          │
│  - Port: 5001                                            │
└─────────────────────┬────────────────────────────────────┘
                      │ Repository Pattern
┌─────────────────────▼────────────────────────────────────┐
│                   Database Layer                          │
│                 (data-analysiter/database)                │
│  - MongoDB Atlas Connection                               │
│  - Repository Pattern (CRUD封装)                          │
│  - Data Models (Pydantic)                                │
│  - Collections: 6个核心集合                              │
└──────────────────────────────────────────────────────────┘
```

## 📁 项目结构

### 1. 数据库层 (`data-analysiter/database/`)

负责所有MongoDB数据操作，使用Repository Pattern封装CRUD。

```
database/
├── __init__.py              # 导出所有仓库
├── connection.py            # MongoDB连接管理（单例模式）
├── models.py                # Pydantic数据模型
├── repositories.py          # 数据仓库（6个Repository类）
└── migrate_data.py          # 数据迁移脚本（JSON → MongoDB）
```

#### MongoDB Collections Schema

| Collection | 用途 | 主要字段 |
|-----------|------|----------|
| `user_profiles` | 创作者档案 | platform, user_id, nickname, profile_data |
| `user_snapshots` | 用户笔记快照 | platform, user_id, notes[], total_notes |
| `user_embeddings` | 向量embeddings | user_id, embedding[512], model |
| `creator_networks` | 创作者相似度网络 | platform, network_data{creators, edges} |
| `style_prompts` | 风格生成提示词模板 | platform, prompt_type, template, variables |
| `platform_configs` | 平台配置 | platform, api_config, auth_token |

#### Repository类列表

- `UserProfileRepository` - 创作者档案CRUD
- `UserSnapshotRepository` - 笔记快照CRUD
- `UserEmbeddingRepository` - Embeddings CRUD
- `CreatorNetworkRepository` - 网络数据CRUD
- `StylePromptRepository` - 提示词模板CRUD
- `PlatformConfigRepository` - 平台配置CRUD

### 2. 后端服务层 (`data-analysiter/api/`)

处理业务逻辑，连接数据库层和API层。

```
api/
├── server_new.py            # FastAPI主应用（新版本）
├── routers/                 # API路由
│   ├── __init__.py
│   ├── style_router.py      # 风格生成路由
│   └── creator_router.py    # 创作者数据路由
└── services/                # 业务逻辑服务
    ├── __init__.py
    └── style_service.py     # 风格生成服务
```

#### 核心服务

**StyleGenerationService** (`api/services/style_service.py`)
- 从MongoDB加载创作者档案和笔记
- 从MongoDB加载提示词模板
- 调用DeepSeek API生成内容
- 返回格式化结果

### 3. 前端层 (`xhs-analyser-frontend/`)

用户界面和交互，通过API与后端通信。

```
xhs-analyser-frontend/
├── app/                     # Next.js App Router
│   └── api/                 # Next.js API Routes (代理层)
│       └── creators/
└── src/
    └── components/
        └── StyleChatbot.tsx # AI风格生成界面
```

## 🔄 数据流

### 风格生成流程

```
1. 用户在前端选择创作者 + 输入主题
   └→ POST /api/style/generate {creator_name, user_topic}

2. Backend Service Layer (style_router.py)
   └→ StyleGenerationService.generate_content()

3. Service Layer调用Database Layer
   ├→ UserProfileRepository.get_profile_by_nickname()
   ├→ UserSnapshotRepository.get_notes()
   └→ StylePromptRepository.get_by_type()

4. Service Layer调用AI
   └→ DeepSeek API (OpenAI SDK)

5. 返回生成内容
   └→ {success: true, content: "...", error: ""}
```

## 🚀 部署和使用

### 1. 数据迁移（首次运行）

将本地JSON数据迁移到MongoDB：

```bash
cd data-analysiter
python -m database.migrate_data
```

这将迁移：
- ✅ 用户档案 (user_profiles/*.json → user_profiles)
- ✅ 用户快照 (snapshots/*.json → user_snapshots)
- ✅ Embeddings (analyses/*__embedding.json → user_embeddings)
- ✅ 创作者网络 (creators_data.json → creator_networks)
- ✅ 提示词模板 (默认模板 → style_prompts)

### 2. 启动后端服务

```bash
cd data-analysiter
cp .env.example .env  # 首次配置环境变量
./start.sh
```

服务将在 http://localhost:5001 启动

### 3. 启动前端

```bash
cd xhs-analyser-frontend
npm run dev
```

前端将在 http://localhost:3000 启动

### 4. 测试API

访问 Swagger UI: http://localhost:5001/docs

主要端点：
- `GET /api/creators/network` - 获取创作者网络
- `GET /api/creators/list` - 获取创作者列表
- `GET /api/creators/{name}` - 获取创作者详情
- `POST /api/style/generate` - 生成风格化内容
- `GET /api/style/creators` - 获取可用创作者
- `GET /api/health` - 健康检查

## 🔧 扩展性设计

### 添加新平台（如Instagram）

1. **数据库层**: 无需修改，platform字段已支持
2. **服务层**: 
   ```python
   # 添加Instagram特定逻辑
   service.generate_content(
       creator_name="xxx",
       user_topic="xxx",
       platform="instagram"  # 新平台
   )
   ```
3. **API层**: 路由已支持platform参数

### 添加新功能

1. 在 `database/models.py` 添加新模型
2. 在 `database/repositories.py` 添加新Repository
3. 在 `api/services/` 创建新Service
4. 在 `api/routers/` 创建新Router
5. 在 `api/server_new.py` 注册新Router

## 📊 优势

### 1. 关注点分离
- **数据库层**: 只负责数据CRUD，不包含业务逻辑
- **服务层**: 只负责业务逻辑，不直接访问数据库
- **API层**: 只负责HTTP请求处理，不包含业务逻辑

### 2. 可测试性
每层都可以独立测试：
```python
# 测试数据库层
repo = UserProfileRepository()
profile = repo.get_profile_by_nickname("Ada在美国")

# 测试服务层（Mock Repository）
service = StyleGenerationService()
result = service.generate_content("Ada在美国", "美国生活")

# 测试API层（FastAPI TestClient）
response = client.post("/api/style/generate", json={...})
```

### 3. 可维护性
- 修改数据库结构只需更新Database Layer
- 修改业务逻辑只需更新Service Layer
- 修改API接口只需更新Router

### 4. 可扩展性
- 支持多平台（platform参数）
- 支持多数据源（Repository Pattern）
- 支持微服务拆分（每层独立部署）

## 🔐 配置管理

### 环境变量

```bash
# MongoDB连接
export MONGO_URI="mongodb+srv://..."

# DeepSeek API
export DEEPSEEK_API_KEY="sk-..."
```

### 数据库配置

所有配置存储在MongoDB的`platform_configs`集合中：
```python
{
    "platform": "xiaohongshu",
    "api_config": {
        "base_url": "https://api.tikhub.io",
        "endpoints": {...}
    },
    "auth_token": "Bearer xxx"
}
```

## 📝 迁移说明

### 从旧架构迁移到新架构

| 旧文件 | 新架构位置 | 说明 |
|--------|-----------|------|
| `api/style_generator.py` | `api/services/style_service.py` | 业务逻辑分离 |
| `data/user_profiles/*.json` | MongoDB `user_profiles` | 迁移到数据库 |
| `data/snapshots/*.json` | MongoDB `user_snapshots` | 迁移到数据库 |
| `data/analyses/*__embedding.json` | MongoDB `user_embeddings` | 迁移到数据库 |
| `data/creators_data.json` | MongoDB `creator_networks` | 迁移到数据库 |

### 迁移步骤

1. ✅ 运行数据迁移脚本
2. ✅ 更新API服务器（使用server_new.py）
3. ⚠️ 更新前端API调用（如需要）
4. ⚠️ 测试所有功能
5. ⚠️ 备份旧JSON文件
6. ⚠️ 删除旧的style_generator.py

## 🐛 故障排查

### 数据库连接失败
```bash
python -c "from database.connection import test_connection; test_connection()"
```

### 检查数据迁移状态
```bash
python -c "from database import *; print(UserProfileRepository().count())"
```

### API调试
访问 http://localhost:5001/docs 使用Swagger UI测试

## 📚 技术栈

- **后端**: FastAPI, Python 3.9+, Pydantic, pymongo
- **前端**: Next.js 16.1, React, TypeScript
- **数据库**: MongoDB Atlas
- **AI服务**: DeepSeek API (OpenAI SDK compatible)
- **Embedding**: BAAI/bge-small-zh-v1.5 (512维)

## 🎯 下一步

1. [ ] 前端更新API调用（如果需要）
2. [ ] 添加单元测试
3. [ ] 添加API认证（JWT）
4. [ ] 添加缓存层（Redis）
5. [ ] 添加日志系统
6. [ ] 添加监控和告警
7. [ ] Docker容器化
8. [ ] CI/CD自动化部署
