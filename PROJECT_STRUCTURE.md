# 项目结构说明

## 📁 核心目录结构

```
xhs_data_Project/
├── backend/                    # 后端API服务
│   ├── api/
│   │   ├── routers/
│   │   │   ├── creator_router.py    # 创作者管理 (添加、查询、刷新)
│   │   │   ├── style_router.py      # AI风格生成
│   │   │   └── persona_router.py    # 用户画像分析
│   │   └── services/
│   │       ├── style_service.py     # 风格生成服务
│   │       └── persona_service.py   # 画像分析服务
│   ├── core/
│   │   ├── config.py           # 配置管理
│   │   ├── llm_gateway.py      # LLM调用网关
│   │   └── storage.py          # 存储层
│   ├── database/
│   │   ├── models.py           # 数据模型
│   │   ├── repositories.py     # 数据访问层
│   │   └── connection.py       # 数据库连接
│   ├── tasks/
│   │   └── collector_task.py   # 异步任务管理
│   └── requirements.txt
│
├── collectors/                 # 数据采集器
│   └── xiaohongshu/
│       ├── collector.py        # 爬虫核心
│       ├── analyzer.py         # 数据分析
│       └── pipeline.py         # 数据处理管道
│
└── xhs-analyser-frontend/      # 前端UI
    ├── app/                    # Next.js App Router
    │   └── [locale]/
    │       ├── page.tsx        # 首页
    │       └── style-generator/
    │           └── page.tsx    # AI生成器页面
    ├── src/
    │   ├── components/
    │   │   ├── HomePage.tsx              # 首页组件
    │   │   ├── CreatorUniverse.tsx       # 创作者网络
    │   │   ├── CreatorNetworkGraph.tsx   # 网络图可视化
    │   │   ├── CreatorDetailPanel.tsx    # 详情面板（含流量密码）
    │   │   ├── StyleChatbot.tsx          # AI风格生成器
    │   │   ├── AddCreatorDialog.tsx      # 添加创作者对话框
    │   │   ├── Header.tsx                # 顶部导航
    │   │   └── LanguageSwitcher.tsx      # 语言切换
    │   └── data/
    │       └── creators.ts               # 创作者数据类型
    └── package.json

```

## 🎯 核心功能模块

### 1. 创作者管理
- **添加创作者**: POST /api/creators/add
- **查询创作者**: GET /api/creators
- **刷新数据**: POST /api/creators/{user_id}/refresh

### 2. AI风格生成
- **获取创作者列表**: GET /api/style/creators
- **生成内容**: POST /api/style/generate

### 3. 用户画像分析
- **获取画像**: GET /api/persona
- **分析笔记**: POST /api/persona/analyze

## 🗑️ 已删除的无用文件

### 前端
- TrendingTopics.tsx (功能已整合到CreatorDetailPanel)
- FollowingAnalysis.tsx (未使用)
- VIDEO_ANALYSIS_API.md (过期文档)

### 后端
- analyze_token_usage.py (调试工具)
- analyze_token_usage2.py (调试工具)
- check_database_structure.py (临时脚本)
- diagnose_api_calls.py (临时脚本)
- check_env.py (临时脚本)

### 文档
- NEW_FEATURES_PLAN.md (已完成)
- RAILWAY_DEBUG.md (调试记录)
- TOKEN_OPTIMIZATION.md (优化记录)

## 🚀 本地开发

### 后端
```bash
cd backend
source ../.venv/bin/activate
uvicorn api.server:app --reload --port 8000
```

### 前端
```bash
cd xhs-analyser-frontend
pnpm install
pnpm run dev
```

### 本地联调
1. 后端启动在 http://localhost:8000
2. 前端启动在 http://localhost:3000
3. 前端通过 NEXT_PUBLIC_API_URL 环境变量连接后端

## 📦 部署环境

- **后端**: Railway (https://xhsdataproject-production.up.railway.app)
- **前端**: Vercel (https://xhs-data-project.vercel.app)
- **数据库**: MongoDB Atlas

## 🔧 环境变量

### 后端 (.env)
```
MONGO_URI=mongodb+srv://...
DATABASE_NAME=tikhub_xhs
DEEPSEEK_API_KEY=sk-...
```

### 前端 (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
# 生产环境使用Railway URL
```

## 📝 开发规范

1. **不要提交到git**: 所有调试都在本地进行
2. **代码精简**: 及时删除无用文件和代码
3. **组件复用**: 避免重复组件
4. **类型安全**: 使用TypeScript严格模式
