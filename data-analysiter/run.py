#!/usr/bin/env python3
"""
一键启动脚本
"""
import subprocess
import sys
import os

def run_command(cmd, description):
    """运行命令"""
    print(f"\n{'='*50}")
    print(f"🔄 {description}")
    print(f"{'='*50}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ 失败: {description}")
        sys.exit(1)
    print(f"✅ 完成: {description}")

if __name__ == "__main__":
    # 切换到脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("🚀 启动视频分析服务")
    
    # 1. 转换数据
    run_command(
        "python3 -m generators.video_analysis",
        "转换数据为前端格式"
    )
    
    # 2. 启动服务
    print("\n" + "="*50)
    print("🌐 启动FastAPI服务")
    print("="*50)
    print("按 Ctrl+C 停止服务\n")
    
    subprocess.run([
        "uvicorn",
        "api.server:app",
        "--host", "0.0.0.0",
        "--port", "5001",
        "--reload"
    ])
