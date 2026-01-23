# 常用命令参考

## 🚀 快速启动

### 一键启动（推荐）

```bash
# 启动后端
cd /Users/tangliam/Projects/xhs_data_Project/data-analysiter
./start.sh

# 启动前端（新终端）
cd /Users/tangliam/Projects/xhs_data_Project/xhs-analyser-frontend
npm run dev
```

### 访问地址

- 前端: http://localhost:3000
- 风格生成器: http://localhost:3000/zh/style-generator
- API文档: http://localhost:5001/docs
- API健康检查: http://localhost:5001/api/health

## 📦 数据管理

### 数据迁移

```bash
# 首次运行：迁移所有数据
cd /Users/tangliam/Projects/xhs_data_Project/data-analysiter
source .venv/bin/activate
python -m database.migrate_data
```

### 生成创作者网络

```bash
cd /Users/tangliam/Projects/xhs_data_Project/data-analysiter
source .venv/bin/activate
python -m generators.creators
```

### 查看数据库统计

```bash
python -c "
from database import *

print('用户档案:', UserProfileRepository().count())
print('用户快照:', UserSnapshotRepository().count())
print('Embeddings:', UserEmbeddingRepository().count())
print('创作者网络:', CreatorNetworkRepository().count())
print('提示词模板:', StylePromptRepository().count())
"
```

## 🔍 数据库查询

### 查询所有创作者

```bash
python -c "
from database import UserProfileRepository

repo = UserProfileRepository()
profiles = repo.get_all_profiles()

for p in profiles:
    print(f\"- {p['nickname']} ({p['user_id']})\")
"
```

### 查询特定创作者

```bash
python -c "
from database import UserProfileRepository

repo = UserProfileRepository()
profile = repo.get_profile_by_nickname('Ada在美国')

if profile:
    print('昵称:', profile['nickname'])
    print('User ID:', profile['user_id'])
    print('主题:', profile['profile_data']['topics'])
    print('风格:', profile['profile_data']['content_style'])
"
```

### 查询创作者笔记

```bash
python -c "
from database import UserSnapshotRepository

repo = UserSnapshotRepository()
notes = repo.get_notes('586f442550c4b43de8f114b0', limit=3)

for i, note in enumerate(notes, 1):
    print(f\"{i}. {note.get('title', 'No title')}\")
"
```

### 查询Embedding

```bash
python -c "
from database import UserEmbeddingRepository

repo = UserEmbeddingRepository()
embedding = repo.get_by_user_id('586f442550c4b43de8f114b0')

if embedding:
    print('User ID:', embedding['user_id'])
    print('Model:', embedding['model'])
    print('维度:', len(embedding['embedding']))
"
```

## 🧪 API测试

### 健康检查

```bash
curl http://localhost:5001/api/health | jq
```

### 获取创作者列表

```bash
curl http://localhost:5001/api/creators/list | jq
```

### 获取创作者网络

```bash
curl http://localhost:5001/api/creators/network | jq
```

### 获取创作者详情

```bash
curl "http://localhost:5001/api/creators/Ada在美国" | jq
```

### 获取可用创作者（风格生成）

```bash
curl http://localhost:5001/api/style/creators | jq
```

### 生成风格化内容

```bash
curl -X POST http://localhost:5001/api/style/generate \
  -H "Content-Type: application/json" \
  -d '{
    "creator_name": "Ada在美国",
    "user_topic": "美国留学经验分享",
    "platform": "xiaohongshu"
  }' | jq
```

## 🗄️ MongoDB操作

### 连接测试

```bash
python -c "from database.connection import test_connection; test_connection()"
```

### 查询集合

```python
# 进入Python shell
from database.connection import get_database

db = get_database()

# 查看所有集合
print(db.list_collection_names())

# 查询user_profiles
profiles = list(db.user_profiles.find())
print(f"用户档案数: {len(profiles)}")

# 查询user_snapshots
snapshots = list(db.user_snapshots.find())
print(f"快照数: {len(snapshots)}")
```

### 插入数据

```python
from database import UserProfileRepository
from datetime import datetime

repo = UserProfileRepository()

# 创建新档案
profile = {
    "platform": "xiaohongshu",
    "user_id": "new_user_123",
    "nickname": "新创作者",
    "profile_data": {
        "topics": ["测试", "示例"],
        "content_style": "测试风格",
        "value_points": ["测试价值1", "测试价值2"]
    },
    "created_at": datetime.now(),
    "updated_at": datetime.now()
}

doc_id = repo.create_profile(profile)
print(f"创建成功: {doc_id}")
```

### 更新数据

```python
from database import UserProfileRepository

repo = UserProfileRepository()

# 更新档案
success = repo.update_profile(
    user_id="new_user_123",
    platform="xiaohongshu",
    update_data={
        "profile_data": {
            "topics": ["更新后的主题"],
            "content_style": "更新后的风格"
        }
    }
)

print(f"更新{'成功' if success else '失败'}")
```

### 删除数据

```python
from database import UserProfileRepository

repo = UserProfileRepository()

# 删除档案
success = repo.delete_one({
    "user_id": "new_user_123",
    "platform": "xiaohongshu"
})

print(f"删除{'成功' if success else '失败'}")
```

## 🔧 开发工具

### 激活虚拟环境

```bash
cd /Users/tangliam/Projects/xhs_data_Project/data-analysiter
source .venv/bin/activate
```

### 安装依赖

```bash
pip install -r requirements.txt
```

### 查看已安装包

```bash
pip list
```

### 更新requirements.txt

```bash
pip freeze > requirements.txt
```

## 📊 数据分析

### 查看创作者相似度

```bash
python -c "
from database import CreatorNetworkRepository

repo = CreatorNetworkRepository()
network = repo.get_latest_network()

if network:
    edges = network['network_data']['edges']
    print(f'共有 {len(edges)} 条相似关系:')
    for edge in edges:
        print(f\"  {edge['source']} ↔ {edge['target']}: {edge['similarity']:.3f}\")
"
```

### 统计笔记数量

```bash
python -c "
from database import UserSnapshotRepository

repo = UserSnapshotRepository()
snapshots = repo.get_all_embeddings()

total_notes = sum(len(s.get('notes', [])) for s in snapshots)
print(f'总笔记数: {total_notes}')

for s in snapshots:
    user_id = s['user_id']
    notes_count = len(s.get('notes', []))
    print(f\"  {user_id}: {notes_count} 条笔记\")
"
```

## 🐛 故障排查

### 检查MongoDB连接

```bash
python -c "
from database.connection import get_database
try:
    db = get_database()
    db.command('ping')
    print('✅ MongoDB连接正常')
except Exception as e:
    print(f'❌ MongoDB连接失败: {e}')
"
```

### 检查API服务

```bash
# 检查端口是否被占用
lsof -i :5001

# 测试API健康检查
curl http://localhost:5001/api/health
```

### 检查DeepSeek API Key

```bash
echo $DEEPSEEK_API_KEY
```

### 查看后端日志

```bash
# 后台运行并查看日志
python api/server_new.py > api.log 2>&1 &
tail -f api.log
```

## 📝 日志管理

### 查看实时日志

```bash
# 后端日志
tail -f /tmp/api_test.log

# 前端日志（Next.js终端输出）
```

### 清理日志

```bash
rm -f /tmp/api_test.log
```

## 🔒 环境变量

### 设置环境变量

```bash
# 使用 .env 文件（推荐）
cp .env.example .env
vim .env  # 编辑你的配置

# 临时设置（当前会话）
export DEEPSEEK_API_KEY="your-api-key"
export MONGO_URI="mongodb+srv://..."

# 永久设置（添加到~/.zshrc或~/.bash_profile）
echo 'export DEEPSEEK_API_KEY="your-key"' >> ~/.zshrc
source ~/.zshrc
```

### 查看环境变量

```bash
env | grep DEEPSEEK
env | grep MONGO
```

## 🚀 生产部署

### Docker构建（未来）

```bash
# 构建镜像
docker build -t xhs-api:v2 .

# 运行容器
docker run -p 5001:5001 \
  -e DEEPSEEK_API_KEY="sk-..." \
  -e MONGO_URI="mongodb+srv://..." \
  xhs-api:v2
```

### 性能测试

```bash
# 使用ab进行压力测试
ab -n 100 -c 10 http://localhost:5001/api/health

# 使用wrk
wrk -t4 -c100 -d30s http://localhost:5001/api/health
```

## 📚 参考资源

- [架构文档](../docs/ARCHITECTURE.md)
- [快速开始](../docs/QUICKSTART_V2.md)
- [迁移总结](../docs/MIGRATION_SUMMARY.md)
- [API文档](http://localhost:5001/docs)

---

**提示**: 将常用命令添加到shell别名以提高效率：

```bash
# 添加到~/.zshrc
alias xhs-api="cd /path/to/data-analysiter && source .venv/bin/activate && export \$(cat .env | grep -v '^#' | xargs) && python api/server.py"

alias xhs-frontend="cd /Users/tangliam/Projects/xhs_data_Project/xhs-analyser-frontend && npm run dev"
```
