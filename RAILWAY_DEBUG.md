# Railway 部署配置指南

## ✅ 问题已修复

**修复内容：**
1. ✅ 添加了 Next.js API路由桥接前后端（`/api/creators` 和 `/api/style/creators`）
2. ✅ 修复了后端返回数据格式（`edges` → `creatorEdges`）
3. ✅ 创建了前端环境变量模板（`.env.production`）

## 🚀 部署步骤

### 1️⃣ 后端部署（Railway）

1. **环境变量配置**

进入 Railway Dashboard → 你的后端项目 → Variables：

```bash
MONGO_URI=你的MongoDB连接字符串
DATABASE_NAME=tikhub_xhs
DEEPSEEK_API_KEY=你的DeepSeek API密钥
PORT=8000
```

2. **验证部署**

等待部署完成后，访问：
```
https://你的后端域名.up.railway.app/api/health
https://你的后端域名.up.railway.app/api/creators/network
https://你的后端域名.up.railway.app/api/style/creators
```

应该能看到JSON数据返回。

### 2️⃣ 前端部署

1. **配置环境变量**

在前端项目根目录创建 `.env.production`（或在Vercel/Railway配置）：

```bash
NEXT_PUBLIC_API_URL=https://你的后端域名.up.railway.app
```

⚠️ **注意**：替换为你的实际Railway后端域名！

2. **重新部署前端**

```bash
cd xhs-analyser-frontend
# 如果用Vercel
vercel --prod

# 如果用Railway
git push  # Railway会自动检测并部署
```

## 📊 数据检查

你的数据库已有数据：
- ✅ user_profiles: 10条
- ✅ user_snapshots: 9条  
- ✅ user_embeddings: 10条
- ✅ creator_networks: 1条（包含8个创作者和9条边）
- ✅ style_prompts: 1条

**创作者网络数据正常，包含：**
- 8个创作者节点
- 9条关系边
- 完整的轨道分类和关键词组

## 🎯 验证清单

部署完成后验证：

- [ ] 后端 `/api/health` 返回 `{"status": "ok"}`
- [ ] 后端 `/api/creators/network` 返回创作者网络数据
- [ ] 后端 `/api/style/creators` 返回10个创作者列表
- [ ] 前端环境变量 `NEXT_PUBLIC_API_URL` 已配置
- [ ] 前端页面能显示创作者关系网络图
- [ ] 前端"选择模仿创作者"下拉框有选项

## 🔧 本地测试（已验证）

本地测试全部通过：
```bash
✅ /api/creators/network - 返回8个创作者和9条边
✅ /api/style/creators - 返回10个创作者
✅ 数据格式正确（creatorEdges字段匹配）
```

## 📝 技术说明

**架构变化：**
```
前端 Next.js                后端 FastAPI
    ↓                           ↓
/api/creators        →    /api/creators/network
    ↓                           ↓
获取creatorEdges      ←    返回creatorEdges数据
```

**数据流：**
1. 前端调用 Next.js API路由 `/api/creators`
2. Next.js服务端通过 `NEXT_PUBLIC_API_URL` 调用Railway后端
3. 后端从MongoDB读取 `creator_networks` 集合
4. 返回格式化数据：`{creators, creatorEdges, trackClusters, trendingKeywordGroups}`
5. Next.js API路由转发数据给前端
6. 前端渲染网络图和创作者列表
