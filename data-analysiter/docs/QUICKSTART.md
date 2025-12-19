# 快速启动指南 - FastAPI版本

## 🚀 一键启动

```bash
cd /Users/tangliam/Projects/xhs_data_Project/data-analysiter

# 第1步: 转换数据
python3 transform_shots_to_frontend.py

# 第2步: 启动API服务
python3 api_server_fastapi.py
```

## 📋 详细步骤

### 1. 确保依赖已安装
```bash
pip3 install fastapi uvicorn python-multipart
```

### 2. 转换数据
```bash
python3 transform_shots_to_frontend.py
```
这会生成 `shots_frontend.json`

### 3. 启动FastAPI服务
```bash
python3 api_server_fastapi.py
```

服务会在 http://localhost:5001 启动

### 4. 测试API
在另一个终端运行:
```bash
python3 test_fastapi.py
```

### 5. 查看API文档
浏览器打开:
- http://localhost:5001/docs (Swagger UI)
- http://localhost:5001/redoc (ReDoc)

## 🔧 图片404问题解决

### 方法1: 检查健康状态
```bash
curl http://localhost:5001/api/health
```

### 方法2: 列出所有图片
```bash
curl http://localhost:5001/api/images
```

### 方法3: 修改图片目录
如果图片不在 `/Users/tangliam/Downloads`，编辑 `api_server_fastapi.py`:

```python
IMAGES_DIR = Path("/your/actual/path")  # 改成实际路径
```

## 🌐 前端配置

前端已经配置好了，只需确保：

1. FastAPI服务在运行 (http://localhost:5001)
2. 前端服务在运行 (http://localhost:3000)

前端会自动从API获取数据并显示！

## ✅ 验证流程

1. **启动FastAPI**: `python3 api_server_fastapi.py`
2. **访问健康检查**: http://localhost:5001/api/health
3. **测试图片**: http://localhost:5001/api/images/IMG_8779.JPG
4. **访问前端**: http://localhost:3000
5. **查看视频分析**: 滚动到"成长路径推荐"部分

## 🐛 常见问题

### Q: 图片404
A: 运行 `curl http://localhost:5001/api/images` 查看可用图片列表

### Q: CORS错误
A: FastAPI已配置CORS，重启服务即可

### Q: 数据不显示
A: 确保 `shots_frontend.json` 存在，运行 `python3 transform_shots_to_frontend.py`

## 📞 需要帮助？

查看详细文档: `FASTAPI_README.md`
