# 小红书数据采集器

## 功能
- 使用TikHub API采集小红书用户笔记
- 使用DeepSeek API分析用户画像  
- 使用本地BAAI/bge-small-zh-v1.5模型生成embedding
- 数据存储到MongoDB

## 文件说明
- `collector.py` - TikHub API数据采集器
- `analyzer.py` - DeepSeek分析 + 本地embedding生成
- `pipeline.py` - 完整数据处理流程

## 使用方法

### 1. 安装依赖
```bash
cd collectors/xiaohongshu
pip3 install -r requirements.txt
```

### 2. 配置环境变量
在项目根目录的 `.env` 文件中设置：
```
TIKHUB_TOKEN=your_tikhub_token
DEEPSEEK_API_KEY=your_deepseek_key
MONGO_URI=your_mongodb_uri
```

### 3. 采集数据
```bash
# 修改 collector.py 中的 USER_ID
python3 collector.py
```

### 4. 分析数据
```bash
# 分析单个用户
python3 pipeline.py --user_id <user_id>

# 分析所有用户
python3 pipeline.py --all
```

## 数据流
```
TikHub API
  ↓ (collector.py)
MongoDB: user_snapshots
  ↓ (pipeline.py + analyzer.py)
MongoDB: user_profiles + user_embeddings
```
