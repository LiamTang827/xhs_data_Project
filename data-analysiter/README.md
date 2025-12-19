# 小红书数据分析器 (Data Analysiter)

提供小红书创作者分析和视频内容分析的后端服务。

## 📁 目录结构

```
data-analysiter/
├── README.md              # 本文档
├── run.py                 # 启动入口
├── start.sh              # Shell启动脚本
│
├── api/                  # API服务
│   ├── __init__.py
│   └── server.py         # FastAPI主服务（端口5001）
│
├── generators/           # 数据生成脚本
│   ├── __init__.py
│   ├── creators.py       # 创作者网络数据生成（使用embedding余弦相似度）
│   ├── video_analysis.py # 视频分析数据转换
│   └── shots_merge.py    # 镜头与文本合并
│
├── processors/           # 数据处理模块
│   ├── __init__.py
│   ├── clean_data.py     # MongoDB数据清洗
│   ├── analyze.py        # 快照分析（GPT生成画像）
│   ├── pipeline.py       # 完整处理流水线
│   └── export_graph.py   # 图数据导出
│
├── tests/                # 测试文件
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_embedding.py
│   ├── test_fastapi.py
│   ├── test_pictures.py
│   └── test_whipser.py
│
├── docs/                 # 文档
│   ├── API_USAGE.md      # API使用指南
│   ├── FASTAPI.md        # FastAPI说明
│   ├── QUICKSTART.md     # 快速开始
│   ├── START_GUIDE.md    # 启动指南
│   └── VIDEO_ANALYSIS.md # 视频分析说明
│
├── data/                 # 生成的数据文件
│   ├── snapshots/        # 用户快照数据
│   ├── analyses/         # 分析结果（含embedding）
│   ├── user_profiles/    # 用户画像
│   ├── creators_data.json    # 创作者网络数据
│   ├── shots_frontend.json   # 前端用视频分析数据
│   └── shots_merged.json     # 合并后的镜头数据
│
└── raw/                  # 原始输入数据
    ├── pictures.json         # 视频镜头数据
    ├── whisper_segments.json # Whisper语音识别结果
    └── whisper_text.txt      # 语音识别文本
```

## 🚀 快速开始

### 1. 激活虚拟环境

```bash
cd /Users/tangliam/Projects/xhs_data_Project
source .venv/bin/activate
```

### 2. 启动API服务

```bash
cd data-analysiter

# 方式一：使用Python启动
python run.py

# 方式二：使用Shell脚本
./start.sh

# 方式三：直接启动uvicorn
uvicorn api.server:app --host 0.0.0.0 --port 5001 --reload
```

### 3. 访问API

- **服务地址**: http://localhost:5001
- **Swagger文档**: http://localhost:5001/docs
- **ReDoc文档**: http://localhost:5001/redoc

## 📡 API端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | API根路径 |
| `/api/video-analysis` | GET | 获取视频分析数据 |
| `/api/creators` | GET | 获取创作者网络数据 |
| `/api/images/{filename}` | GET | 获取镜头图片 |
| `/api/images` | GET | 列出所有图片 |
| `/api/health` | GET | 健康检查 |

## 🛠️ 数据生成

### 生成创作者网络数据

```bash
python -m generators.creators
```

使用 `data/analyses/*__embedding.json` 中的512维向量计算余弦相似度，
相似度 ≥ 0.7 的创作者之间会建立连接边。

### 生成视频分析数据

```bash
python -m generators.video_analysis
```

将 `data/shots_merged.json` 转换为前端需要的格式。

### 合并镜头与文本

```bash
python -m generators.shots_merge
```

将视频镜头 (`raw/pictures.json`) 与语音识别结果 (`raw/whisper_segments.json`) 合并。

## 📊 数据处理流水线

完整的数据处理流程：

```bash
python -m processors.pipeline
```

流程包括：
1. 从MongoDB获取用户快照
2. 使用LLM生成用户画像
3. 生成embedding向量
4. 导出图数据

## 🔗 前端集成

前端项目位于 `../xhs-analyser-frontend`，通过环境变量配置API地址：

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:5001
```

## 📝 更多文档

- [API使用指南](docs/API_USAGE.md)
- [快速开始](docs/QUICKSTART.md)
- [视频分析说明](docs/VIDEO_ANALYSIS.md)
