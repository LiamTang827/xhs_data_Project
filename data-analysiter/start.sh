#!/bin/bash

# 完整启动脚本
cd "$(dirname "$0")"

echo "🔄 第1步: 转换数据..."
python3 -m generators.video_analysis

if [ $? -ne 0 ]; then
    echo "❌ 数据转换失败"
    exit 1
fi

echo ""
echo "🚀 第2步: 启动FastAPI服务..."
uvicorn api.server:app --host 0.0.0.0 --port 5001 --reload
