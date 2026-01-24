# Backend Docker 部署 - 完整配置

## ✅ 已完成的优化

### 1. Dockerfile 改进
- ✅ 添加 `curl` 用于健康检查
- ✅ 设置 `PYTHONUNBUFFERED=1` 确保日志实时输出
- ✅ 添加默认 `PORT=5001` 环境变量
- ✅ 添加 `EXPOSE` 指令声明端口
- ✅ 添加 `HEALTHCHECK` 自动健康检查
- ✅ 简化启动命令，使用环境变量

### 2. 新增文件

#### `.dockerignore`
优化构建速度，排除不必要的文件：
- Python缓存文件
- 虚拟环境
- IDE配置
- 测试文件
- 数据文件

#### `docker-compose.yml`
简化部署流程：
- 自动端口映射 5001:5001
- 环境变量管理
- 健康检查配置
- 自动重启策略
- 网络配置

#### `test_docker.sh`
完整的测试流程：
1. 检查Docker状态
2. 验证必需文件
3. 构建镜像
4. 测试容器启动
5. 健康检查
6. 自动清理

#### `deploy.sh`
一键部署脚本：
- 环境检查
- Docker Compose启动
- 健康检查
- 使用说明

#### `DEPLOYMENT.md`
详细的部署文档：
- Docker部署方法
- 云平台部署指南（Railway、Render、Heroku）
- 环境变量配置
- 故障排查
- 性能优化建议

## 🚀 使用方法

### 方法1: 快速部署（推荐）
```bash
cd backend
./deploy.sh
```

### 方法2: Docker Compose
```bash
cd backend
docker-compose up -d
docker-compose logs -f
```

### 方法3: Docker 命令
```bash
cd backend
docker build -t xhs-backend:latest .
docker run -d \
  --name xhs-backend \
  -p 5001:5001 \
  --env-file .env \
  xhs-backend:latest
```

### 方法4: 完整测试
```bash
cd backend
./test_docker.sh
```

## 📋 必需的环境变量（.env文件）

```bash
# MongoDB连接
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/database

# DeepSeek API密钥
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx

# 端口（可选，默认5001）
PORT=5001
```

## 🎯 部署到云平台

### Railway
1. 连接GitHub仓库
2. 选择 `backend` 目录
3. 添加环境变量：`MONGO_URI`, `DEEPSEEK_API_KEY`
4. Railway自动检测Dockerfile并部署

### Render
1. 连接GitHub仓库
2. 选择 Docker 部署
3. Root Directory: `backend`
4. 添加环境变量

### Heroku
```bash
# 使用Container Registry
cd backend
heroku container:login
heroku container:push web -a your-app-name
heroku container:release web -a your-app-name
```

## ✅ 健康检查端点

访问: `http://localhost:5001/api/health`

预期响应:
```json
{
  "status": "ok",
  "version": "2.0.0",
  "database": {
    "connected": true
  }
}
```

## 📊 监控和日志

```bash
# Docker Compose
docker-compose logs -f

# Docker
docker logs -f xhs-backend

# 进入容器调试
docker exec -it xhs-backend /bin/bash
```

## 🔧 故障排查

### 容器无法启动
```bash
docker logs xhs-backend
```

### 数据库连接失败
- 检查 `MONGO_URI` 格式
- 确认MongoDB Atlas IP白名单包含 `0.0.0.0/0`

### 端口冲突
```bash
# 更改主机端口
docker run -p 8080:5001 ...
```

## 📦 镜像优化

当前镜像大小: ~1.5GB（包含所有依赖）

可选优化:
- 使用 Alpine Linux 基础镜像（减小50%）
- 多阶段构建（分离构建和运行环境）
- 压缩Python依赖

## 🎉 总结

所有配置已优化完成，现在你可以：

1. ✅ **本地测试**: `./test_docker.sh`
2. ✅ **快速部署**: `./deploy.sh`
3. ✅ **云端部署**: 参考 `DEPLOYMENT.md`
4. ✅ **健康检查**: 自动配置，无需手动
5. ✅ **日志管理**: 实时输出，方便调试
