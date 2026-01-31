# 1. 使用 Python 3.10 官方镜像
FROM python:3.10-slim

# 2. 设置工作目录
WORKDIR /app

# 3. 安装系统依赖（curl 用于健康检查，gcc 用于编译 Python 包）
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. 复制依赖文件（利用 Docker 缓存）
COPY requirements.txt .

# 5. 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 6. 复制应用代码
COPY . .

# 7. 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 8. 暴露端口（Railway 会自动分配 PORT 环境变量）
EXPOSE 8000

# 9. 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# 10. 启动命令（直接执行 uvicorn，不依赖脚本）
# Railway 会自动提供 PORT 环境变量，默认使用 8000
CMD ["sh", "-c", "uvicorn api.server:app --host 0.0.0.0 --port ${PORT:-8000}"]