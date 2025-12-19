# FastAPI API服务使用说明

## 安装依赖

```bash
pip3 install fastapi uvicorn python-multipart
```

## 启动服务

```bash
cd data-analysiter
python3 api_server_fastapi.py
```

服务会在 `http://localhost:5001` 启动

## API文档

启动后访问：
- **Swagger UI**: http://localhost:5001/docs (交互式API文档)
- **ReDoc**: http://localhost:5001/redoc (美观的文档)

## 可用端点

### 1. GET /api/video-analysis
获取视频分析数据

```bash
curl http://localhost:5001/api/video-analysis
```

### 2. GET /api/images/{filename}
获取镜头图片

```bash
curl http://localhost:5001/api/images/IMG_8779.JPG
```

### 3. GET /api/images
列出所有可用图片

```bash
curl http://localhost:5001/api/images
```

### 4. GET /api/health
健康检查

```bash
curl http://localhost:5001/api/health
```

## 图片路径问题解决

FastAPI服务会自动：
1. 尝试多个可能的文件路径
2. 处理URL编码的空格（`%20`）
3. 如果找不到文件，会列出可用的文件列表
4. 提供详细的错误信息

## 调试步骤

如果图片还是404：

1. **检查健康状态**
```bash
curl http://localhost:5001/api/health
```

2. **列出所有图片**
```bash
curl http://localhost:5001/api/images
```

3. **检查文件名是否完全匹配**（注意空格、大小写）

4. **修改图片目录**（如果需要）
编辑 `api_server_fastapi.py` 的这一行：
```python
IMAGES_DIR = Path("/Users/tangliam/Downloads")  # 改成你的实际路径
```

## 生产部署

```bash
# 安装gunicorn
pip3 install gunicorn

# 使用gunicorn运行
gunicorn api_server_fastapi:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:5001
```
