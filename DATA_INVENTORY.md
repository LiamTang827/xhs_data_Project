# 小红书数据分析平台 - 数据清单

> 📊 **数据库**: MongoDB Atlas (`tikhub_xhs`)  
> 🔄 **最后更新**: 2026-01-18  
> 📍 **目的**: 记录项目中所有可用的数据结构、字段定义和访问方法

---

## 📦 一、MongoDB Collections 概览

| Collection 名称 | 文档数 | 主要用途 | 对应模型 |
|---------------|-------|---------|---------|
| `user_profiles` | 10 | 创作者核心档案 | `UserProfile` |
| `user_snapshots` | 9 | 创作者笔记快照 | `UserSnapshot` |
| `user_embeddings` | 10 | 创作者向量表示 | `UserEmbedding` |
| `creator_networks` | 1 | 创作者关系网络 | `CreatorNetwork` |
| `style_prompts` | 1 | 风格生成提示词模板 | `StylePrompt` |
| `platform_configs` | 0 | 平台API配置 | `PlatformConfig` |

---

## 📋 二、数据结构详解

### 1. user_profiles - 创作者档案

**用途**: 存储创作者的核心画像数据，包括内容主题、风格、价值点等AI分析结果

**字段说明**:
```python
{
  "_id": ObjectId,                    # MongoDB唯一标识
  "platform": str,                    # 平台类型 (xiaohongshu)
  "user_id": str,                     # 平台用户ID
  "nickname": str,                    # 用户昵称
  "profile_data": {                   # 核心画像数据
    "topics": [str],                  # 内容主题标签 (例: ["地理科普", "文化传承"])
    "content_style": str,             # 内容风格描述
    "value_points": [str],            # 价值主张列表
    "engagement": {                   # 互动数据
      "likes": int,                   # 总点赞数
      "collects": int,                # 总收藏数
      "comments": int,                # 总评论数
      "shares": int                   # 总分享数
    }
  },
  "created_at": datetime,             # 创建时间
  "updated_at": datetime              # 更新时间
}
```

**Repository 方法**:
- `get_by_user_id(user_id, platform)` - 根据用户ID查询
- `get_all_profiles()` - 获取所有档案
- `create_profile(profile_data)` - 创建新档案
- `update_profile(user_id, platform, update_data)` - 更新档案
- `get_profile_by_nickname(nickname, platform)` - 根据昵称查询

**API 接口**: 
- `GET /api/creators/list` - 获取创作者列表
- `GET /api/creators/{creator_name}` - 获取单个创作者详情

---

### 2. user_snapshots - 笔记快照

**用途**: 存储创作者的历史笔记数据，用于内容分析和趋势追踪

**字段说明**:
```python
{
  "_id": ObjectId,
  "platform": str,                    # 平台类型
  "user_id": str,                     # 用户ID
  "notes": [                          # 笔记列表
    {
      "note_id": str,                 # 笔记ID
      "title": str,                   # 笔记标题
      "desc": str,                    # 笔记描述/内容摘要
      "liked_count": int,             # 点赞数
      "collected_count": int,         # 收藏数
      "comment_count": int,           # 评论数
      "share_count": int,             # 分享数
      "published_time": datetime,     # 发布时间
      "note_url": str                 # 笔记链接
    }
  ],
  "total_notes": int,                 # 笔记总数
  "created_at": datetime              # 快照创建时间
}
```

**Repository 方法**:
- `get_by_user_id(user_id, platform)` - 根据用户ID查询快照
- `get_notes(user_id, platform, limit=5)` - 获取用户笔记列表
- `create_snapshot(snapshot_data)` - 创建新快照
- `update_snapshot(user_id, platform, notes)` - 更新笔记快照

**使用场景**:
- 创作者内容历史分析
- 爆款笔记识别 (按互动数排序)
- 发布频率统计

---

### 3. user_embeddings - 向量表示

**用途**: 使用AI模型生成的创作者语义向量，用于相似度计算和聚类分析

**字段说明**:
```python
{
  "_id": ObjectId,
  "platform": str,                    # 平台类型
  "user_id": str,                     # 用户ID
  "embedding": [float],               # 512维向量 (BAAI/bge-small-zh-v1.5)
  "model": str,                       # 使用的模型名称
  "dimension": int,                   # 向量维度 (默认512)
  "created_at": datetime              # 创建时间
}
```

**Repository 方法**:
- `get_by_user_id(user_id, platform)` - 根据用户ID查询embedding
- `get_all_embeddings(platform)` - 获取所有embeddings
- `create_embedding(embedding_data)` - 创建embedding
- `update_embedding(user_id, platform, embedding)` - 更新embedding

**技术细节**:
- 模型: `BAAI/bge-small-zh-v1.5` (中文小型通用文本表示模型)
- 维度: 512
- 计算方式: 基于创作者的 profile_data (topics + content_style + value_points)

---

### 4. creator_networks - 创作者网络

**用途**: 存储创作者之间的关系图数据，用于网络可视化

**字段说明**:
```python
{
  "_id": ObjectId,
  "platform": str,                    # 平台类型
  "network_data": {                   # 网络图数据
    "creators": [                     # 节点列表
      {
        "id": str,                    # 创作者ID
        "name": str,                  # 创作者名称
        "followers": int,             # 粉丝数
        "engagementIndex": int,       # 互动指数
        "primaryTrack": str,          # 主赛道
        "contentForm": str,           # 内容形式描述
        "recentKeywords": [str],      # 近期关键词
        "position": {                 # 图中坐标
          "x": float,
          "y": float
        },
        "avatar": str,                # 头像URL
        "ipLocation": str,            # IP属地
        "desc": str,                  # 个人简介
        "redId": str,                 # 小红书号
        "topics": [str]               # 话题标签
      }
    ],
    "edges": [                        # 边列表
      {
        "source": str,                # 源节点ID
        "target": str,                # 目标节点ID
        "weight": float,              # 关系权重
        "types": {                    # 关系类型及权重
          "keyword": float,           # 关键词相似度
          "audience": float,          # 受众重叠度
          "style": float,             # 风格相似度
          "campaign": float           # 合作/联动
        },
        "sampleEvents": [             # 示例事件
          {
            "type": str,              # 事件类型
            "title": str,             # 事件标题
            "timestamp": str          # 时间戳
          }
        ]
      }
    ]
  },
  "created_at": datetime              # 创建时间
}
```

**Repository 方法**:
- `get_latest_network(platform)` - 获取最新的网络数据
- `create_network(network_data)` - 创建新网络快照

**API 接口**:
- `GET /api/creators/network` - 获取创作者网络图数据

**前端使用**: 
- 组件: `CreatorNetworkGraph.tsx`
- 可视化: 使用 D3.js / React-Force-Graph
- 交互: 点击节点显示详情面板

---

### 5. style_prompts - 风格提示词模板

**用途**: 存储AI生成内容时使用的提示词模板

**字段说明**:
```python
{
  "_id": ObjectId,
  "platform": str,                    # 平台类型
  "prompt_type": str,                 # 提示词类型 (style_generation / content_analysis)
  "name": str,                        # 模板名称
  "template": str,                    # 提示词模板文本
  "variables": [str],                 # 模板变量列表
  "description": str,                 # 模板描述
  "created_at": datetime,             # 创建时间
  "updated_at": datetime              # 更新时间
}
```

**Repository 方法**:
- `get_by_type(prompt_type, platform)` - 根据类型获取模板
- `get_all_prompts(platform)` - 获取所有模板
- `create_prompt(prompt_data)` - 创建新模板
- `update_prompt(prompt_type, platform, update_data)` - 更新模板

**使用场景**:
- 风格生成器: 根据创作者画像生成文案风格建议
- 内容分析: AI分析创作者内容特征

---

### 6. platform_configs - 平台配置

**用途**: 存储各平台API的配置信息

**字段说明**:
```python
{
  "_id": ObjectId,
  "platform": str,                    # 平台类型
  "api_config": {                     # API配置
    "base_url": str,                  # API基础URL
    "endpoints": {                    # 接口端点映射
      "user_info": str,
      "note_list": str,
      "note_detail": str
    },
    "headers": {                      # 请求头配置
      str: str
    }
  },
  "auth_token": str,                  # 认证令牌
  "enabled": bool,                    # 是否启用
  "created_at": datetime,             # 创建时间
  "updated_at": datetime              # 更新时间
}
```

**Repository 方法**:
- `get_by_platform(platform)` - 根据平台获取配置
- `get_all_configs()` - 获取所有配置
- `create_config(config_data)` - 创建配置
- `update_config(platform, update_data)` - 更新配置

---

## 🎯 三、前端数据模型

### TypeScript 接口定义

**文件位置**: `xhs-analyser-frontend/src/data/creators.ts`

```typescript
// 创作者节点
export interface CreatorNode {
  id: string;                         // 创作者ID
  name: string;                       // 名称
  followers: number;                  // 粉丝数
  engagementIndex: number;            // 互动指数
  primaryTrack: string;               // 主赛道
  contentForm: string;                // 内容形式
  recentKeywords: string[];           // 关键词
  position: { x: number; y: number }; // 图中位置
  avatar?: string;                    // 头像
  ipLocation?: string;                // IP属地
  desc?: string;                      // 简介
  redId?: string;                     // 小红书号
  topics?: string[];                  // 话题标签 (流量密码)
}

// 创作者边 (关系)
export interface CreatorEdge {
  source: string;                     // 源节点ID
  target: string;                     // 目标节点ID
  weight: number;                     // 权重
  types: Partial<Record<CreatorEdgeSignal, number>>; // 关系类型
  sampleEvents?: Array<{
    type: CreatorEdgeSignal;
    title: string;
    timestamp: string;
  }>;
}

export type CreatorEdgeSignal = "keyword" | "audience" | "style" | "campaign";
```

**文件位置**: `xhs-analyser-frontend/src/lib/api.ts`

```typescript
// 用户笔记
export interface UserNote {
  note_url: string;
  note_id?: string;
  title?: string;
}

// 笔记详情
export interface NoteDetail {
  channel_id: string;
  content_id: string;
  content_type: string;
  content_title: string;
  likes: number;
  shares: number;
  views: number;
  published_time: string | Date;
  collected_number: number;
  comments: NoteComment[];
  description: string;
  tags: string[];
  note_url: string;
  last_updated: string | Date;
}

// 用户信息
export interface UserInfo {
  user_id: string;
  user_name: string;
  red_id?: string;
  fans?: string | number;
  note_count?: number;
  is_verified?: boolean;
  avatar?: string;
  description?: string;
}
```

---

## 🔄 四、数据流向

### 1. 添加创作者流程（实际流程）

```
1. 调用TikHub API爬取用户笔记
   ├─ API: GET /api/v1/xiaohongshu/web/get_user_notes_v2
   ├─ 返回：19-20条笔记/次
   └─ 数据：user{nickname, userid, images}, notes[]

2. 保存原始笔记数据到 user_snapshots
   ├─ 字段：user_id, notes[], total_notes
   ├─ 注意：TikHub返回的user.fans可能为None
   └─ 注意：笔记中**没有tag_list字段**

3. [需DeepSeek API] 分析笔记生成profile
   ├─ 输入：notes前20条的title+desc
   ├─ AI提取：content_topics（话题标签）、content_style
   ├─ 生成embedding（使用本地BAAI/bge-small-zh-v1.5模型）
   └─ 保存到：user_profiles, user_embeddings

4. 生成creator_networks（无需API）
   ├─ 从snapshots中读取笔记数据
   ├─ 计算：engagementIndex = likes + collects*2 + comments*3 + shares*5
   ├─ topics：优先用profile，否则从标题简单分词提取
   └─ 基于topics相似度生成关系边
```

### 2. **重点说明：TikHub API限制**

TikHub返回的笔记数据结构：
```json
{
  "user": {
    "nickname": "创作者昵称",
    "userid": "5ff98b9d0000000001008f40",
    "images": "头像URL",
    "fans": null,  // ⚠️ 可能为null
    "desc": null,  // ⚠️ 可能为null
    "ip_location": null  // ⚠️ 可能为null
  },
  "title": "笔记标题",
  "desc": "笔记描述",
  "likes": 63,  // 注意字段名是likes不是liked_count
  "collected_count": 5,
  "comments_count": 12,
  "share_count": 5
  // ⚠️ 没有tag_list字段！
}
```

**数据清洗策略**：
1. **粉丝数**：TikHub返回为None，暂时设为0
2. **话题标签**：从标题+描述中AI提取或简单分词
3. **互动数据**：从每条笔记累加计算

```
前端加载
  ↓
GET /api/creators/network
  ↓
返回 network_data { creators: [], edges: [] }
  ↓
CreatorNetworkGraph 组件渲染 D3 图
  ↓
点击节点
  ↓
CreatorDetailPanel 显示详情:
  - 头像、名称、属地、粉丝数
  - Creator Index 图表
  - 流量密码 (topics)
```

### 3. 风格生成流程

```
用户选择创作者
  ↓
POST /api/style/generate
  {
    creator_names: [str],
    style_aspects: [str]
  }
  ↓
从 user_profiles 提取:
  - topics
  - content_style
  - value_points
  ↓
调用 LLM (OpenAI/DeepSeek)
使用 style_prompts 模板
  ↓
生成风格建议
  ↓
返回前端 StyleChatbot 组件
```

---

## 📊 五、数据访问示例

### 1. 查询所有创作者档案

```python
from database import UserProfileRepository

repo = UserProfileRepository()
profiles = repo.get_all_profiles()

for profile in profiles:
    print(f"{profile['nickname']}: {profile['profile_data']['topics']}")
```

### 2. 获取创作者笔记

```python
from database import UserSnapshotRepository

repo = UserSnapshotRepository()
notes = repo.get_notes(user_id="5ff98b9d0000000001008f40", limit=10)

for note in notes:
    print(f"{note['title']} - ❤️ {note['liked_count']}")
```

### 3. 计算创作者相似度

```python
from database import UserEmbeddingRepository
import numpy as np

repo = UserEmbeddingRepository()
embeddings = repo.get_all_embeddings()

# 计算余弦相似度
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

emb1 = np.array(embeddings[0]['embedding'])
emb2 = np.array(embeddings[1]['embedding'])
similarity = cosine_similarity(emb1, emb2)
print(f"相似度: {similarity:.4f}")
```

### 4. 前端获取网络数据

```typescript
// xhs-analyser-frontend/src/components/CreatorUniverse.tsx

const response = await fetch('/api/creators/network');
const data = await response.json();

const { creators, edges } = data.network_data;
```

---

## 🔧 六、Repository 方法速查

### BaseRepository (通用方法)

所有 Repository 都继承这些方法:

```python
find_one(query: dict) -> Optional[dict]        # 查询单个文档
find_many(query: dict, limit: int) -> list     # 查询多个文档
insert_one(data: dict) -> str                  # 插入文档
update_one(query: dict, update: dict) -> bool  # 更新文档
delete_one(query: dict) -> bool                # 删除文档
count(query: dict) -> int                      # 统计数量
```

### 专用 Repository

| Repository | Collection | 特殊方法 |
|-----------|-----------|---------|
| `UserProfileRepository` | user_profiles | `get_by_user_id`, `get_profile_by_nickname` |
| `UserSnapshotRepository` | user_snapshots | `get_notes`, `update_snapshot` |
| `UserEmbeddingRepository` | user_embeddings | `get_all_embeddings` |
| `CreatorNetworkRepository` | creator_networks | `get_latest_network` |
| `StylePromptRepository` | style_prompts | `get_by_type`, `get_all_prompts` |
| `PlatformConfigRepository` | platform_configs | `get_by_platform` |

---

## 📝 七、API 端点速查

### Creator Router (`/api/creators`)

| 方法 | 路径 | 功能 | 返回数据 |
|-----|------|-----|---------|
| GET | `/network` | 获取创作者网络图 | `{creators: [], edges: []}` |
| GET | `/list` | 获取创作者列表 | `[{user_id, nickname, ...}]` |
| GET | `/{creator_name}` | 获取单个创作者详情 | `{profile, notes, embedding}` |
| POST | `/add` | 添加新创作者 | `{task_id, status}` |
| GET | `/task/{task_id}` | 查询任务状态 | `{status, progress}` |
| POST | `/{user_id}/refresh` | 刷新创作者数据 | `{success, message}` |

### Style Router (`/api/style`)

| 方法 | 路径 | 功能 | 返回数据 |
|-----|------|-----|---------|
| GET | `/creators` | 获取可用创作者列表 | `[{name, topics, style}]` |
| POST | `/generate` | 生成风格建议 | `{style_analysis, recommendations}` |

### Persona Router (`/api/persona`)

| 方法 | 路径 | 功能 | 返回数据 |
|-----|------|-----|---------|
| POST | `/analyze` | 分析用户画像 | `{persona_tags, ai_summary}` |
| GET | `/{user_id}` | 获取用户画像 | `{persona_data}` |
| GET | `/` | 获取画像列表 | `[{user_id, tags, ...}]` |
| DELETE | `/{user_id}` | 删除画像 | `{success}` |

---

## 💡 八、关键数据指标

### 1. 互动指标 (Engagement Metrics)

- **点赞数** (`liked_count`): 笔记被点赞次数
- **收藏数** (`collected_count`): 笔记被收藏次数  
- **评论数** (`comment_count`): 笔记评论数
- **分享数** (`share_count`): 笔记被分享次数
- **互动指数** (`engagementIndex`): 综合互动权重分数

### 2. 创作者指标

- **粉丝数** (`followers`): 关注者数量
- **笔记总数** (`total_notes`): 发布的笔记总量
- **主赛道** (`primaryTrack`): 创作者的主要内容领域
- **内容形式** (`contentForm`): 内容表现形式描述

### 3. 网络关系权重

- **keyword**: 关键词重叠相似度 (0-1)
- **audience**: 受众重叠度 (0-1)
- **style**: 风格相似度 (0-1)
- **campaign**: 合作/联动强度 (0-1)

---

## 🚀 九、数据更新机制

### 自动更新 (CollectorTask)

```python
# backend/tasks/collector_task.py

class CollectorTask:
    """后台数据收集任务"""
    
    async def run(self):
        # 1. 初始化
        self.status = "initializing"
        
        # 2. 获取数据
        self.status = "fetching"
        user_data = await self._fetch_user_data()
        
        # 3. 分析内容
        self.status = "analyzing"
        profile = await self._analyze_profile(user_data)
        
        # 4. 存入数据库
        repo.create_profile(profile)
        repo.create_snapshot(snapshot)
        repo.create_embedding(embedding)
        
        # 5. 更新网络图
        await self._update_network()
        
        self.status = "completed"
```

### 手动刷新

```http
POST /api/creators/{user_id}/refresh
```

触发重新抓取和分析该创作者的最新数据。

---

## 📖 十、使用最佳实践

### 1. 数据查询优化

```python
# ❌ 不推荐: 循环查询
for user_id in user_ids:
    profile = repo.get_by_user_id(user_id)

# ✅ 推荐: 批量查询
profiles = repo.find_many({"user_id": {"$in": user_ids}})
```

### 2. 前端数据缓存

```typescript
// 使用 React Query 缓存网络数据
const { data, isLoading } = useQuery(
  'creator-network',
  () => fetch('/api/creators/network').then(r => r.json()),
  { staleTime: 5 * 60 * 1000 } // 5分钟内不重复请求
);
```

### 3. 数据一致性

- 修改 `user_profiles` 后应同时更新 `user_embeddings`
- 添加/删除创作者后应重新生成 `creator_networks`

---

## 🔐 十一、环境变量配置

```bash
# .env

# MongoDB
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=tikhub_xhs

# LLM API
OPENAI_API_KEY=sk-xxxx
DEEPSEEK_API_KEY=sk-xxxx

# TikHub API (数据采集)
TIKHUB_API_KEY=your_tikhub_key
TIKHUB_BASE_URL=https://api.tikhub.io
```

---

## 📚 十二、相关文档

- [项目结构](PROJECT_STRUCTURE.md)
- [API 文档](backend/api/README.md)
- [前端组件](xhs-analyser-frontend/README.md)
- [数据采集器](collectors/xiaohongshu/README.md)

---

## 🎓 术语表

| 术语 | 说明 |
|-----|-----|
| **User Profile** | 创作者档案，包含AI分析的内容特征 |
| **Snapshot** | 某一时刻的笔记数据快照 |
| **Embedding** | 文本向量化表示，用于相似度计算 |
| **Creator Network** | 创作者之间的关系图谱 |
| **Style Prompt** | AI生成内容的提示词模板 |
| **Repository** | 数据访问层，封装MongoDB操作 |
| **Collection** | MongoDB中的数据表 |

---

**📞 需要帮助?**  
如果发现数据结构不清楚或有遗漏，请检查:
- 后端模型定义: [backend/database/models.py](backend/database/models.py)
- 仓库方法: [backend/database/repositories.py](backend/database/repositories.py)
- API路由: [backend/api/routers/](backend/api/routers/)
