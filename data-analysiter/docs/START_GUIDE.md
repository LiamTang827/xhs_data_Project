# 🚀 完整启动指南

## 第一步：转换数据

```bash
cd /Users/tangliam/Projects/xhs_data_Project/data-analysiter
python3 transform_shots_to_frontend.py
```

**预期输出:**
```
✅ 转换完成！
   总镜头数: 12
   视频总时长: 1:12
   输出文件: shots_frontend.json
```

## 第二步：启动FastAPI服务

**方法1: 直接启动**
```bash
cd /Users/tangliam/Projects/xhs_data_Project/data-analysiter
uvicorn api_server_fastapi:app --host 0.0.0.0 --port 5001 --reload
```

**方法2: 使用Python脚本**
```bash
cd /Users/tangliam/Projects/xhs_data_Project/data-analysiter
python3 run.py
```

**预期输出:**
```
🚀 启动FastAPI视频分析服务...
📁 数据文件: /path/to/shots_frontend.json
🖼️  图片目录: /Users/tangliam/Downloads
🌐 服务地址: http://localhost:5001

INFO:     Uvicorn running on http://0.0.0.0:5001
INFO:     Application startup complete.
```

## 第三步：验证服务

**测试1: 健康检查**
```bash
curl http://localhost:5001/api/health
```

**测试2: 列出图片**
```bash
curl http://localhost:5001/api/images
```

**测试3: 获取视频数据**
```bash
curl http://localhost:5001/api/video-analysis
```

或者在浏览器打开:
- http://localhost:5001/docs (API文档)
- http://localhost:5001/api/health

## 第四步：启动前端

前端应该已经在运行了 (localhost:3000)，如果没有：

```bash
cd /Users/tangliam/Projects/xhs_data_Project/xhs-analyser-frontend
pnpm dev
```

## 第五步：查看效果

1. 打开浏览器: http://localhost:3000
2. 滚动到 "成长路径推荐" 部分
3. 你应该能看到12个镜头的视频分析

## ❌ 如果还是报错

### 错误1: "Failed to fetch"

**解决方案:**
```bash
# 1. 检查FastAPI是否运行
curl http://localhost:5001/api/health

# 2. 如果没运行，启动它
cd /Users/tangliam/Projects/xhs_data_Project/data-analysiter
uvicorn api_server_fastapi:app --host 0.0.0.0 --port 5001 --reload

# 3. 重启前端
cd /Users/tangliam/Projects/xhs_data_Project/xhs-analyser-frontend
# 按 Ctrl+C 停止，然后
pnpm dev
```

### 错误2: 图片404

**解决方案:**
```bash
# 列出可用图片
curl http://localhost:5001/api/images

# 检查Downloads目录
ls -la /Users/tangliam/Downloads/*.JPG
```

### 错误3: 数据文件不存在

**解决方案:**
```bash
cd /Users/tangliam/Projects/xhs_data_Project/data-analysiter
python3 transform_shots_to_frontend.py
```

## 📝 完整命令序列

在3个不同的终端窗口运行:

**终端1: FastAPI服务**
```bash
cd /Users/tangliam/Projects/xhs_data_Project/data-analysiter
python3 transform_shots_to_frontend.py
uvicorn api_server_fastapi:app --host 0.0.0.0 --port 5001 --reload
```

**终端2: 前端服务**
```bash
cd /Users/tangliam/Projects/xhs_data_Project/xhs-analyser-frontend
pnpm dev
```

**终端3: 测试**
```bash
cd /Users/tangliam/Projects/xhs_data_Project/data-analysiter
python3 test_fastapi.py
```

## ✅ 成功标志

如果一切正常，你会看到：

1. **FastAPI日志**: `INFO: Application startup complete.`
2. **前端**: 显示12个镜头，可以左右滑动
3. **测试脚本**: 所有测试通过 ✅

## 🔗 重要链接

- 前端: http://localhost:3000
- API文档: http://localhost:5001/docs
- 健康检查: http://localhost:5001/api/health
- 图片列表: http://localhost:5001/api/images
