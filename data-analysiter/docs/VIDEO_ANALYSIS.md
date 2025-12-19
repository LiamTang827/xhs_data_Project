# 视频分析数据集成指南

## 📋 快速开始

### 1. 转换数据格式

将 `shots_merged.json` 转换为前端需要的格式：

```bash
cd data-analysiter
python3 transform_shots_to_frontend.py
```

这会生成 `shots_frontend.json` 文件，包含：
- 12个镜头的数据
- 每个镜头的关键帧图片路径
- 旁白文案
- 视频结构段落划分

### 2. 启动API服务

启动Flask API服务来提供数据和图片：

```bash
cd data-analysiter

# 安装依赖（如果还没装）
pip3 install flask flask-cors

# 启动服务
python3 api_server.py
```

服务会在 `http://localhost:5001` 启动

### 3. 配置前端环境变量

在前端项目根目录创建 `.env.local`：

```bash
cd xhs-analyser-frontend
echo "NEXT_PUBLIC_API_URL=http://localhost:5001" > .env.local
```

### 4. 启动前端

```bash
cd xhs-analyser-frontend
pnpm dev
```

访问 `http://localhost:3000` 即可看到真实的视频分析数据！

## 📁 文件说明

### 后端文件 (data-analysiter/)

- **`shots_merged.json`** - 原始视频分析数据（你的数据）
- **`transform_shots_to_frontend.py`** - 数据转换脚本
- **`shots_frontend.json`** - 转换后的前端格式数据
- **`api_server.py`** - Flask API服务

### 前端文件 (xhs-analyser-frontend/)

- **`src/types/videoAnalysis.ts`** - TypeScript类型定义
- **`src/hooks/useVideoAnalysis.ts`** - React Hook获取数据
- **`src/components/GrowthPath.tsx`** - 视频分析展示组件
- **`src/components/CreatorUniverse.tsx`** - 已集成真实数据

## 🔄 数据流程

```
shots_merged.json (原始数据)
    ↓
transform_shots_to_frontend.py (转换)
    ↓
shots_frontend.json (前端格式)
    ↓
api_server.py (API服务)
    ↓
useVideoAnalysis Hook (获取数据)
    ↓
GrowthPath Component (展示)
```

## 📊 数据结构转换

### 输入格式 (shots_merged.json)
```json
{
  "id": 1,
  "image": "IMG_8779.JPG",
  "path": "/Users/tangliam/Downloads/IMG_8779.JPG",
  "start": 0.0,
  "end": 6.0,
  "text": "奥运赛场上霹雳舞者凌空跃起瞬间定格",
  "segments": [...]
}
```

### 输出格式 (shots_frontend.json)
```json
{
  "shots": [
    {
      "id": 1,
      "title": "奥运赛场上霹雳舞者...",
      "subtitle": "(凌空跃起瞬间定格)",
      "image": "/api/images/IMG_8779.JPG",
      "narration": "奥运赛场上霹雳舞者凌空跃起瞬间定格",
      "timeRange": "0:00-0:06",
      "segmentId": 1
    }
  ],
  "structureSegments": [...],
  "totalDuration": "1:12",
  "timeLabels": ["0:00", "0:14", ...]
}
```

## 🎨 段落划分规则

脚本会自动根据时间点划分视频结构：

- **开头引言** (蓝色) - 0-15%时长
- **核心讲解** (绿色) - 15-60%时长
- **案例分析** (紫色) - 60-90%时长
- **结尾总结** (橙色) - 90-100%时长

## 🖼️ 图片处理

### 选项1: 使用图片URL（推荐）
- API服务会从 `/Users/tangliam/Downloads/` 读取图片
- 前端通过 `/api/images/<filename>` 访问

### 选项2: 使用Base64编码
修改 `transform_shots_to_frontend.py`：
```python
transform_shots_to_frontend(
    INPUT_FILE, 
    OUTPUT_FILE, 
    use_base64=True  # 改为True
)
```

## 🔧 API端点

### GET /api/video-analysis
获取视频分析数据
```bash
curl http://localhost:5001/api/video-analysis
```

### GET /api/images/<filename>
获取镜头关键帧图片
```bash
curl http://localhost:5001/api/images/IMG_8779.JPG
```

### GET /api/health
健康检查
```bash
curl http://localhost:5001/api/health
```

## 🐛 常见问题

### 1. 图片显示不出来
- 检查图片路径是否正确
- 确认 `api_server.py` 中的 `IMAGES_DIR` 设置正确
- 尝试使用base64编码图片

### 2. CORS错误
- 确保 `api_server.py` 已安装 `flask-cors`
- 检查 `.env.local` 中的API_URL配置

### 3. 数据不显示
- 检查浏览器控制台是否有错误
- 确认API服务正在运行
- 验证 `shots_frontend.json` 已生成

## 📝 自定义配置

### 修改标题生成规则
编辑 `transform_shots_to_frontend.py` 的标题生成逻辑：
```python
# 当前逻辑：截取前12个字符
title = text[:12] + "..."

# 可以改为自定义规则
title = "镜头" + str(shot_id)
```

### 调整段落划分
修改 `determine_segment_id` 函数中的百分比：
```python
if percentage < 0.20:  # 改为20%
    return 1
```

## 🚀 生产部署

### 部署后端API
```bash
# 使用gunicorn
pip3 install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 api_server:app
```

### 前端环境变量
```bash
# .env.production
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## 📞 需要帮助？

查看详细文档：`docs/VIDEO_ANALYSIS_API.md`
