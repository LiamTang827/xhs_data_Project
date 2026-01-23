#!/bin/bash
# XHS Data Analysis API Starter Script

# 确保在正确的目录
cd "$(dirname "$0")"

# 激活虚拟环境
source .venv/bin/activate

# 加载环境变量（如果存在 .env 文件）
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ 已加载 .env 配置"
else
    echo "⚠️  警告: 未找到 .env 文件，请复制 .env.example 并配置"
    echo "   cp .env.example .env"
    exit 1
fi

# 启动服务
echo "🚀 启动 XHS Data Analysis API v2.0..."
python api/server.py
