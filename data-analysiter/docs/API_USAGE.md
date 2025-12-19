# FastAPI 数据分析服务使用指南

## 概述

这个FastAPI服务提供两大核心功能：
1. **视频分析数据** - 视频镜头分解、时间轴、旁白文案
2. **创作者网络数据** - 基于embedding余弦相似度的创作者关系网络

## 快速启动

### 1. 生成数据

```bash
cd data-analysiter
source .venv/bin/activate

# 生成视频分析数据
python transform_shots_to_frontend.py

# 生成创作者网络数据（基于embedding计算余弦相似度）
python generate_creators_data.py
```

### 2. 启动服务

```bash
# 方式1：直接运行
python api_server_fastapi.py

# 方式2：使用run.py
python run.py

# 方式3：使用start.sh
./start.sh
```

服务默认运行在 `http://localhost:5001`

### 3. 启动前端

```bash
cd ../xhs-analyser-frontend
pnpm dev
```

前端默认运行在 `http://localhost:3000`

## API端点

### 健康检查

```bash
GET /api/health
```

返回服务状态、数据文件是否存在、图片数量等信息。

### 创作者网络数据

```bash
GET /api/creators
```

返回创作者节点、关系边、主题聚类数据。

**数据来源：**
- `snapshots/` - 创作者快照数据（粉丝数、互动数）
- `user_profiles/` - 创作者内容主题和风格
- `analyses/*__embedding.json` - 创作者embedding向量

**关系计算：**
- 使用512维embedding向量计算余弦相似度
- 默认阈值：0.7（可在 `generate_creators_data.py` 中调整 `SIMILARITY_THRESHOLD`）
- 相似度越高，创作者内容风格越相近

**响应格式：**
```json
{
  "creators": [
    {
      "id": "xxx",
      "name": "创作者名称",
      "followers": 100000,
      "engagementIndex": 500000,
      "primaryTrack": "主要赛道",
      "recentKeywords": ["关键词1", "关键词2"],
      "avatar": "头像URL",
      "followersDelta": 1000,
      "interactionDelta": 5000,
      "indexSeries": [
        {
          "ts": 1763308800000,
          "value": 1946475
        }
      ],
      "indexSeriesRaw": [
        {
          "time": "2025-11-17T00:00:00",
          "followers": 99000,
          "interaction": 495000,
          "influence": 597000,
          "ts": 1763308800000,
          "value": 597000
        }
      ]
    }
  ],
  "creatorEdges": [
    {
      "source": "创作者A的ID",
      "target": "创作者B的ID",
      "weight": 0.804,
      "types": {
        "style": 0.804
      }
    }
  ],
  "trackClusters": {
    "脑科学与神经科学": ["创作者ID1", "创作者ID2"]
  }
}
```

### 视频分析数据

```bash
GET /api/video-analysis
```

返回视频镜头分解数据、结构段落、时间轴标签。

**响应格式：**
```json
{
  "shots": [
    {
      "id": 1,
      "title": "镜头标题",
      "subtitle": "副标题",
      "image": "/api/images/IMG_8779.JPG",
      "narration": "旁白文案",
      "timeRange": "0:00-0:06",
      "segmentId": 1
    }
  ],
  "structureSegments": [
    {
      "id": 1,
      "label": "开头引言",
      "timeRange": "(0:00-0:30)",
      "color": "blue",
      "width": "25%"
    }
  ],
  "timeLabels": ["0:00", "0:30", "1:00"]
}
```

### 获取图片

```bash
GET /api/images/{filename}
```

获取视频关键帧图片。支持：
- 精确匹配
- URL编码匹配（空格自动转换）
- 大小写不敏感匹配
- 宽松匹配（去除空格）

**示例：**
```bash
curl http://localhost:5001/api/images/IMG_8779.JPG
curl http://localhost:5001/api/images/IMG_8781%202.JPG  # 文件名带空格
```

### 列出所有图片

```bash
GET /api/images
```

返回图片目录中所有可用图片的列表。

## 数据流程

### 创作者网络数据流程

```
snapshots/*.json          → 创作者基础数据（粉丝、互动）
user_profiles/*.json      → 内容主题和风格
analyses/*__embedding.json → 512维embedding向量
         ↓
generate_creators_data.py → 计算余弦相似度
         ↓
creators_data.json        → FastAPI读取
         ↓
GET /api/creators         → 前端获取
```

### 视频分析数据流程

```
shots_merged.json         → 原始镜头数据
         ↓
transform_shots_to_frontend.py → 转换为前端格式
         ↓
shots_frontend.json       → FastAPI读取
         ↓
GET /api/video-analysis   → 前端获取
```

## 创作者指数计算

**计算公式：**
```
影响力指数 = 粉丝数 × 0.6 + 互动数 × 0.4
```

**数据格式：**
- `indexSeries` - 简化格式 `[{ts, value}]`，供前端图表直接使用
- `indexSeriesRaw` - 详细格式，包含粉丝数、互动数等完整信息

**验证数据：**
```bash
python verify_index.py
```

此脚本会展示每个创作者的时间序列数据和计算过程。

## 配置

### 环境变量

前端 `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:5001
```

### 关键配置

`api_server_fastapi.py`:
```python
IMAGES_DIR = Path("/Users/tangliam/Downloads")  # 图片目录
```

`generate_creators_data.py`:
```python
SIMILARITY_THRESHOLD = 0.7  # 余弦相似度阈值
WEIGHT_FOLLOWERS = 0.6      # 粉丝权重（影响力指数计算）
WEIGHT_INTERACTION = 0.4    # 互动权重（影响力指数计算）
```

## 测试

```bash
# 运行测试脚本
python test_fastapi.py

# 手动测试
curl http://localhost:5001/api/health
curl http://localhost:5001/api/creators
curl http://localhost:5001/api/video-analysis
```

## API文档

服务启动后可访问：
- Swagger UI: http://localhost:5001/docs
- ReDoc: http://localhost:5001/redoc

## 故障排除

### 问题：创作者数据为空

**原因：** 快照文件格式不匹配或embedding文件未找到

**解决：**
```bash
# 检查快照文件
ls snapshots/

# 检查embedding文件
ls analyses/*__embedding.json

# 重新生成数据
python generate_creators_data.py
```

### 问题：图片404

**原因：** 图片路径不匹配或文件名编码问题

**解决：**
```bash
# 检查图片目录
ls -la /Users/tangliam/Downloads/*.JPG

# 测试图片访问
curl -I "http://localhost:5001/api/images/IMG_8779.JPG"

# 查看可用图片列表
curl http://localhost:5001/api/images
```

### 问题：前端无法获取数据

**原因：** CORS或API URL配置问题

**解决：**
1. 检查 `.env.local` 中的 `NEXT_PUBLIC_API_URL`
2. 确认FastAPI服务正在运行
3. 检查浏览器控制台的CORS错误

## 更新数据

### 更新创作者数据

当有新的快照或embedding数据时：

```bash
python generate_creators_data.py
```

会自动：
1. 读取所有快照文件（支持多个时间点）
2. 加载embedding向量
3. 计算创作者之间的余弦相似度
4. 生成时间序列和增长delta
5. 输出 `creators_data.json`

### 更新视频分析数据

当有新的视频分析结果时：

```bash
python transform_shots_to_frontend.py
```

## 性能优化

- FastAPI自动启用响应缓存
- 图片使用1天的缓存头
- 开发模式启用热重载（`reload=True`）

## 生产部署

生产环境建议：

1. 关闭热重载
2. 限制CORS域名
3. 添加认证中间件
4. 使用Gunicorn + Uvicorn workers
5. 反向代理（Nginx）

```bash
gunicorn api_server_fastapi:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:5001
```
