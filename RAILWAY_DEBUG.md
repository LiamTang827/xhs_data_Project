# Railway 部署问题诊断和修复指南

## 🔍 问题分析

根据你的截图，前端显示：
- `creators` 返回 **500 Internal Server Error**
- `creators` 也返回 **404 Not Found**

本地测试证明代码完全正常，问题在于Railway部署环境。

## ✅ 解决方案

### 1️⃣ 检查Railway环境变量

前往 Railway Dashboard → 你的项目 → Variables，确保设置了：

```
MONGO_URI=mongodb+srv://xhs_user:你的新密码@xhs-cluster.omeyngi.mongodb.net/?retryWrites=true&w=majority&appName=xhs-Cluster
DATABASE_NAME=tikhub_xhs
DEEPSEEK_API_KEY=你的新API密钥
PORT=8000
```

⚠️ **重要**: 由于密钥泄露，必须使用新的密钥！

### 2️⃣ 检查Railway服务URL

确认你的Railway后端服务URL（应该类似 `https://your-app-xxx.up.railway.app`）

### 3️⃣ 配置前端环境变量

在前端项目根目录创建 `.env.local`：

```bash
# Railway 后端URL（替换为你的实际URL）
NEXT_PUBLIC_API_URL=https://your-backend-xxx.up.railway.app
```

然后重新部署前端（如果前端也在Railway上）。

### 4️⃣ 验证Railway后端部署

打开浏览器访问以下URL（替换为你的实际域名）：

```
https://your-backend-xxx.up.railway.app/api/health
https://your-backend-xxx.up.railway.app/api/style/creators
https://your-backend-xxx.up.railway.app/docs
```

### 5️⃣ 如果数据库是空的

如果Railway上的MongoDB是空的（没有创作者数据），需要运行数据初始化：

进入Railway Dashboard → 你的项目 → 打开Shell，执行：

```bash
python init_railway_data.py
```

或者在本地运行并连接到Railway的MongoDB：

```bash
cd backend
MONGO_URI="你的Railway MongoDB URI" python ../init_railway_data.py
```

## 🐛 调试步骤

### 查看Railway日志

1. Railway Dashboard → 你的项目 → Deployments → 查看最新部署日志
2. 检查是否有启动错误或数据库连接错误

### 测试debug端点

访问：`https://your-backend-xxx.up.railway.app/api/style/debug/db`

这会返回数据库连接状态和集合统计信息。

## 📋 快速检查清单

- [ ] Railway环境变量已设置（MONGO_URI, DEEPSEEK_API_KEY, DATABASE_NAME）
- [ ] Railway部署成功（查看Deployments页面状态）
- [ ] 后端health端点可访问
- [ ] MongoDB有数据（至少user_profiles有记录）
- [ ] 前端环境变量指向正确的Railway后端URL
- [ ] 前端已重新构建和部署

## 🔗 相关文件

- 后端Dockerfile: `backend/Dockerfile` ✅ 已修复PYTHONPATH
- 数据初始化: `init_railway_data.py` ✅ 已创建
- API路由: `backend/api/routers/style_router.py` ✅ 正常
- 前端API调用: `xhs-analyser-frontend/src/components/StyleChatbot.tsx`
