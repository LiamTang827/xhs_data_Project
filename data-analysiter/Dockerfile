# 1. 强制指定使用 Python 3.10 (彻底解决版本不兼容问题)
FROM python:3.10-slim

# 2. 设置工作目录
WORKDIR /app

# 3. 安装系统级依赖 (Numba 和一些科学计算库需要编译环境)
# 这一步是为了防止 Linux 缺少 gcc 导致编译失败
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 4. 先复制依赖文件 (利用 Docker 缓存加速构建)
COPY requirements.txt .

# 5. 安装 Python 依赖
# --no-cache-dir 减小镜像体积
RUN pip install --no-cache-dir -r requirements.txt

# 6. 复制剩下的所有代码
COPY . .

# 7. 启动命令
CMD run.py
