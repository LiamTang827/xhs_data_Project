# XHS Data Project - 小红书数据分析平台

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-16.1-black.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green.svg)

> ⚠️ **配置说明**: 克隆后请先复制 `.env.example` 为 `.env` 并填入你的配置。详见 [快速开始](#-快速开始)

## 🏗️ 架构总览

完整的三层架构设计，职责清晰、易于扩展：

```
Frontend (Next.js) → API Layer (FastAPI) → Database Layer (MongoDB)
```

📐 **查看完整架构图**: [ARCHITECTURE_DIAGRAM.md](./ARCHITECTURE_DIAGRAM.md) ⭐

---

## 📁 项目结构

这个工作区包含三个主要项目：

### 1. 🔌 tikhub-data-collector
**用途**：从 TikHub API 获取小红书用户数据

**主要功能**：
- 使用 TikHub API 采集小红书用户笔记
- 自动存储到 MongoDB
- 支持批量获取和增量更新

**使用场景**：数据采集的第一步

📖 [查看详细文档](./tikhub-data-collector/README.md)

---

### 2. 📊 data-analysiter
**用途**：数据处理、分析和 AI 内容生成

**主要功能**：
- 三层架构（Database → Service → API）
- 创作者网络分析（基于 embedding 相似度）
- AI 风格模仿（DeepSeek API）
- FastAPI 后端服务

**技术栈**：
- Python 3.9+, FastAPI
- MongoDB Atlas (Repository Pattern)
- DeepSeek AI, OpenAI SDK
- BGE Embedding Model (512维)

📖 [查看详细文档](./data-analysiter/README.md)

---

### 3. 🎨 xhs-analyser-frontend
**用途**：用户界面和数据可视化

**主要功能**：
- 创作者网络图展示
- AI 风格生成界面
- 数据统计和分析报表

**技术栈**：
- Next.js 16.1.0, TypeScript
- Turbopack
- React Components

📖 [查看详细文档](./xhs-analyser-frontend/README.md)

---

### 4. 🕷️ MediaCrawler
**用途**：备用爬虫工具（多平台支持）

**支持平台**：
- 小红书 (XHS)
- 抖音 (Douyin)
- 快手 (Kuaishou)
- B站 (Bilibili)
- 微博 (Weibo)

📖 [查看详细文档](./MediaCrawler/README.md)

---

## 🚀 快速开始

### 完整工作流程

```bash
# 步骤 1: 数据采集
cd tikhub-data-collector
source ../data-analysiter/.venv/bin/activate
python test_user_tikhub.py

# 步骤 2: 启动后端服务
cd ../data-analysiter
./start.sh  # 或者手动启动

# 步骤 3: 启动前端服务
cd ../xhs-analyser-frontend
npm run dev
```

### 访问服务

- 🎨 前端界面: http://localhost:3000
- 🔌 API 服务: http://localhost:5001
- 📖 API 文档: http://localhost:5001/docs

## 🔧 配置要求

### 环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件，填入你的真实配置
vim .env
```

配置项说明：
- `MONGO_URI`: MongoDB Atlas 连接字符串
- `DEEPSEEK_API_KEY`: DeepSeek AI API 密钥
- `TIKHUB_TOKEN`: TikHub API 认证令牌

### 软件依赖

- Python 3.9+ (推荐使用虚拟环境)
- Node.js 18+
- MongoDB Atlas 账号
- DeepSeek API Key
- TikHub API Token

## 📊 数据流图

```
┌──────────────────────┐
│  TikHub API          │
│  (小红书数据源)        │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│ tikhub-data-collector│
│  (数据采集)           │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│  MongoDB Atlas       │
│  (数据存储)           │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│  data-analysiter     │
│  (处理 + AI生成)      │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│ xhs-analyser-frontend│
│  (可视化界面)         │
└──────────────────────┘
```

## 🏗️ 架构特点

### 分离关注点
- **数据采集** → 独立工具 (tikhub-data-collector)
- **数据处理** → 后端服务 (data-analysiter)
- **用户交互** → 前端应用 (xhs-analyser-frontend)

### 可扩展性
- 支持多平台数据源（小红书、Instagram等）
- Repository Pattern 便于切换数据库
- 模块化设计，易于添加新功能

### 技术栈
- **后端**: FastAPI + MongoDB + DeepSeek AI
- **前端**: Next.js + TypeScript
- **数据**: Repository Pattern + Embedding (512维)

## 📚 文档导航

### data-analysiter 文档
- [ARCHITECTURE.md](./data-analysiter/docs/ARCHITECTURE.md) - 三层架构设计
- [QUICKSTART_V2.md](./data-analysiter/docs/QUICKSTART_V2.md) - 详细使用指南
- [MIGRATION_SUMMARY.md](./data-analysiter/docs/MIGRATION_SUMMARY.md) - 数据迁移说明
- [CLEANUP_SUMMARY.md](./data-analysiter/docs/CLEANUP_SUMMARY.md) - 代码优化记录
- [API_USAGE.md](./data-analysiter/docs/API_USAGE.md) - API 使用文档

### 其他文档
- [tikhub-data-collector/README.md](./tikhub-data-collector/README.md) - 数据采集工具
- [MediaCrawler/README.md](./MediaCrawler/README.md) - 爬虫工具说明

## 🔄 版本历史

- **v2.1** (2026-01-23) - 完成安全处理，准备 GitHub 上传
- **v2.0** (2026-01-23) - 提取 TikHub 数据采集工具到独立文件夹
- **v1.5** (2026-01-22) - 代码清理和优化（删除 20+ 冗余文件）
- **v1.0** (2026-01-20) - 完成三层架构重构和 MongoDB 迁移
- **v0.5** (2026-01-15) - MVP 版本（JSON 文件存储）

## 🔒 安全说明

### ⚠️ 重要：环境变量配置

本项目使用环境变量管理敏感信息。**克隆后必须配置才能运行**：

```bash
# 1. 复制配置模板
cp .env.example .env
cp data-analysiter/.env.example data-analysiter/.env
cp tikhub-data-collector/.env.example tikhub-data-collector/.env

# 2. 编辑 .env 文件，填入你的真实配置
vim .env

# 3. 运行安全检查
./security_check.sh
```

### 📋 需要的配置

- `MONGO_URI`: MongoDB Atlas 连接字符串
- `DEEPSEEK_API_KEY`: DeepSeek AI API 密钥
- `TIKHUB_TOKEN`: TikHub API 认证令牌

### 🔍 安全检查

上传前运行安全检查脚本：
```bash
./security_check.sh
```

### 📚 详细指南

- [SECURITY_GUIDE.md](./SECURITY_GUIDE.md) - 完整安全指南
- [GITHUB_UPLOAD_GUIDE.md](./GITHUB_UPLOAD_GUIDE.md) - GitHub 上传指南

## 👨‍💻 开发者

- 项目所有者: tangliam
- 最后更新: 2026-01-23

## 📄 许可证

请查看各子项目的 LICENSE 文件。
