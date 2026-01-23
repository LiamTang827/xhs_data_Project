# 快速开始 - 三层架构版本

本指南帮助你快速部署和使用三层架构版本的XHS Data Analysis平台。

## 🎯 前置条件

- Python 3.9+
- Node.js 18+
- MongoDB Atlas账号（已有）
- DeepSeek API Key（已有）

## 📦 第一步：安装依赖

### 后端依赖

```bash
cd data-analysiter
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

需要添加以下依赖到 `requirements.txt`:
```
pymongo
pydantic
openai
```

### 前端依赖

```bash
cd xhs-analyser-frontend
npm install
```

## 🗄️ 第二步：数据迁移

将本地JSON数据迁移到MongoDB：

```bash
cd data-analysiter
source .venv/bin/activate
python -m database.migrate_data
```

预期输出：
```
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀 数据迁移 - JSON to MongoDB 🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀

============================================================
📦 开始迁移用户档案数据...
============================================================
✅ Ada在美国 迁移成功 (ID: ...)
✅ 硅谷樱花小姐姐🌸 迁移成功 (ID: ...)
...

📊 用户档案迁移完成: 成功 7, 跳过 0

============================================================
📦 开始迁移用户快照数据...
============================================================
...

✅ 所有数据迁移完成！

📊 数据库统计信息：
------------------------------------------------------------
  用户档案 (user_profiles): 7 条
  用户快照 (user_snapshots): 12 条
  用户Embeddings (user_embeddings): 7 条
  创作者网络 (creator_networks): 1 条
  提示词模板 (style_prompts): 1 条
```

## 🚀 第三步：启动后端服务

```bash
cd data-analysiter

# 方法1: 使用启动脚本（推荐）
cp .env.example .env  # 首次运行
./start.sh

# 方法2: 手动启动
source .venv/bin/activate
export $(cat .env | grep -v '^#' | xargs)
python api/server.py
```

预期输出：
```
============================================================
🚀 XHS Data Analysis API v2.0 - 三层架构
============================================================

📋 架构层次:
  ├─ 数据库层 (Database Layer): MongoDB + Repository Pattern
  ├─ 服务层 (Service Layer): 业务逻辑处理
  └─ API层 (API Layer): FastAPI RESTful接口

🌐 服务地址: http://localhost:5001

📚 API文档:
  - Swagger UI: http://localhost:5001/docs
  - ReDoc: http://localhost:5001/redoc

🔗 主要端点:
  - GET  /api/creators/network - 创作者网络数据
  - GET  /api/creators/list - 所有创作者列表
  - GET  /api/creators/{name} - 创作者详情
  - POST /api/style/generate - AI风格生成
  - GET  /api/style/creators - 可用创作者
  - GET  /api/health - 健康检查
============================================================
```

### 验证后端服务

在浏览器访问：
- http://localhost:5001 - 查看API信息
- http://localhost:5001/docs - Swagger UI
- http://localhost:5001/api/health - 健康检查

## 🎨 第四步：启动前端

在新终端窗口：

```bash
cd xhs-analyser-frontend
npm run dev
```

访问 http://localhost:3000

## ✅ 第五步：测试功能

### 1. 测试创作者网络API

```bash
curl http://localhost:5001/api/creators/network
```

应返回创作者网络数据（JSON）。

### 2. 测试创作者列表

```bash
curl http://localhost:5001/api/creators/list
```

应返回所有创作者列表。

### 3. 测试风格生成

```bash
curl -X POST http://localhost:5001/api/style/generate \
  -H "Content-Type: application/json" \
  -d '{
    "creator_name": "Ada在美国",
    "user_topic": "美国留学生活",
    "platform": "xiaohongshu"
  }'
```

应返回AI生成的内容。

### 4. 测试前端界面

1. 访问 http://localhost:3000/zh/style-generator
2. 选择创作者（如"Ada在美国"）
3. 输入主题（如"美国留学经验分享"）
4. 点击"生成内容"
5. 等待AI生成结果

## 🔧 常见问题

### Q1: 数据迁移时提示"已存在"

A: 这是正常的，脚本会跳过已存在的数据。如果需要重新迁移，请先在MongoDB中删除相应collection。

### Q2: 后端启动失败 - ModuleNotFoundError

A: 确保：
1. 已激活虚拟环境 `source .venv/bin/activate`
2. 已安装所有依赖 `pip install -r requirements.txt`
3. 在data-analysiter目录下运行

### Q3: API返回401错误

A: 检查DEEPSEEK_API_KEY是否正确设置：
```bash
echo $DEEPSEEK_API_KEY
```

### Q4: 风格生成返回"未找到创作者"

A: 检查：
1. 数据是否已迁移到MongoDB
2. 创作者名称是否正确（区分大小写）
3. 使用以下命令检查数据库：
```bash
python -c "from database import UserProfileRepository; repo = UserProfileRepository(); print([p['nickname'] for p in repo.get_all_profiles()])"
```

### Q5: 前端无法连接后端

A: 检查：
1. 后端服务是否在5001端口运行
2. CORS是否正确配置（已在server_new.py中配置）
3. 前端API调用地址是否为 localhost:5001

## 📝 开发模式

### 后端开发

后端使用uvicorn的`--reload`模式，修改代码后自动重启：

```bash
cd data-analysiter
python api/server_new.py  # 已内置reload
```

### 前端开发

Next.js使用Turbopack，支持快速热更新：

```bash
cd xhs-analyser-frontend
npm run dev
```

### 数据库操作

使用Python交互式shell：

```python
from database import UserProfileRepository

repo = UserProfileRepository()

# 查询所有创作者
profiles = repo.get_all_profiles()
for p in profiles:
    print(p['nickname'])

# 查询特定创作者
profile = repo.get_profile_by_nickname("Ada在美国")
print(profile)

# 统计数量
count = repo.count()
print(f"总共 {count} 个创作者")
```

## 🎯 下一步

- [ ] 阅读 [ARCHITECTURE.md](./ARCHITECTURE.md) 了解架构设计
- [ ] 查看Swagger UI文档了解所有API
- [ ] 尝试添加新的创作者数据
- [ ] 尝试自定义提示词模板
- [ ] 部署到生产环境

## 📞 获取帮助

如有问题，请查看：
1. [架构文档](./ARCHITECTURE.md)
2. [API文档](http://localhost:5001/docs)
3. 检查后端日志输出
4. 检查MongoDB数据完整性
