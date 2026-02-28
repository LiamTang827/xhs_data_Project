#!/bin/bash
# 启动后端API服务器

cd "$(dirname "$0")"
source ../.venv/bin/activate

echo "🚀 启动后端API服务器..."
echo "📍 地址: http://localhost:8000"
echo "📖 文档: http://localhost:8000/docs"
echo ""

# 检查并杀掉占用 8000 端口的进程
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "⚠️  检测到 8000 端口已被占用，正在清理..."
    kill -9 $(lsof -ti:8000) 2>/dev/null || true
    sleep 1
    echo "✅ 已清理端口"
fi

uvicorn api.server:app --reload --port 8000
