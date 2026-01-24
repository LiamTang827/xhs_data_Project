# Backend 部署指南

## 🐳 Docker 部署

### 方法1: 使用 docker-compose (推荐)

```bash
# 1. 确保 .env 文件存在且包含必要的环境变量
cd backend

# 2. 构建并启动
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose down
```

### 方法2: 直接使用 Docker

```bash
cd backend

# 1. 构建镜像
docker build -t xhs-backend:latest .

# 2. 运行容器
docker run -d \
  --name xhs-backend \
  -p 5001:5001 \
  -e MONGO_URI="your_mongo_uri" \
  -e DEEPSEEK_API_KEY="your_api_key" \
  --env-file .env \
  xhs-backend:latest

# 3. 查看日志
docker logs -f xhs-backend

# 4. 停止并删除容器
docker stop xhs-backend
docker rm xhs-backend
```

## 🚀 云平台部署

### Railway 部署

1. 在项目根目录创建 `railway.json`:
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "backend/Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn api.server:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

2. 设置环境变量:
   - `MONGO_URI`
   - `DEEPSEEK_API_KEY`
   - `PORT` (Railway自动提供)

### Render 部署

1. 连接 GitHub 仓库
2. 选择 Docker 部署
3. 设置:
   - Docker Context: `backend`
   - Environment Variables:
     - `MONGO_URI`
     - `DEEPSEEK_API_KEY`

### Heroku 部署

```bash
# 1. 登录 Heroku
heroku login

# 2. 创建应用
heroku create your-app-name

# 3. 设置环境变量
heroku config:set MONGO_URI="your_mongo_uri"
heroku config:set DEEPSEEK_API_KEY="your_api_key"

# 4. 部署
git subtree push --prefix backend heroku main

# 或使用 Heroku Container Registry
heroku container:login
cd backend
heroku container:push web -a your-app-name
heroku container:release web -a your-app-name
```

## 📋 必需的环境变量

```bash
# MongoDB连接
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/database

# DeepSeek API密钥
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx

# 端口（可选，默认5001）
PORT=5001
```

## ✅ 健康检查

部署后访问: `http://your-domain/api/health`

预期响应:
```json
{
  "status": "ok",
  "version": "2.0.0",
  "architecture": "three-tier",
  "database": {
    "connected": true,
    "type": "MongoDB Atlas"
  },
  "services": {
    "style_generation": "active",
    "creator_network": "active"
  }
}
```

## 🔧 故障排查

### 问题1: 容器无法启动
```bash
# 查看日志
docker logs xhs-backend

# 进入容器调试
docker exec -it xhs-backend /bin/bash
```

### 问题2: 数据库连接失败
- 检查 `MONGO_URI` 是否正确
- 确认 MongoDB Atlas IP白名单已添加 `0.0.0.0/0`
- 测试连接: `docker exec xhs-backend curl http://localhost:5001/api/health`

### 问题3: 端口冲突
```bash
# 更改主机端口
docker run -p 8080:5001 ...  # 主机8080映射到容器5001
```

## 📊 性能优化

1. **多阶段构建** (可选优化):
```dockerfile
# 在Dockerfile添加多阶段构建减小镜像体积
FROM python:3.10-slim as builder
...
FROM python:3.10-slim
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
```

2. **使用缓存层**:
```bash
# 利用Docker layer caching
docker build --cache-from xhs-backend:latest -t xhs-backend:latest .
```

3. **限制资源**:
```bash
# 限制内存和CPU
docker run --memory="512m" --cpus="1.0" ...
```
