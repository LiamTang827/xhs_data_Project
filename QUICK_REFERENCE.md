# 🚀 快速参考卡

## 📋 常用命令

### 启动服务
```bash
# 后端
cd data-analysiter
./start.sh                    # 自动加载 .env 并启动
# 访问: http://localhost:5001

# 前端
cd xhs-analyser-frontend
npm run dev                   # 启动开发服务器
# 访问: http://localhost:3000
```

### 数据采集
```bash
cd tikhub-data-collector
source ../data-analysiter/.venv/bin/activate
python test_user_tikhub.py    # 采集用户数据到 MongoDB
```

### 安全检查
```bash
./security_check.sh           # 上传前运行
```

---

## 🔧 配置文件

### 必需的 .env 文件
```bash
# 1. 项目根目录
cp .env.example .env

# 2. data-analysiter
cd data-analysiter
cp .env.example .env

# 3. tikhub-data-collector
cd ../tikhub-data-collector
cp .env.example .env
```

### 关键环境变量
```env
MONGO_URI=mongodb+srv://...         # MongoDB 连接
DEEPSEEK_API_KEY=sk-...             # AI API 密钥
TIKHUB_TOKEN=Bearer ...             # 数据采集令牌
```

---

## 📐 架构速览

```
Frontend (3000) → API (5001) → MongoDB Atlas
                    ↓
                DeepSeek AI
```

**详细架构**: [ARCHITECTURE_DIAGRAM.md](./ARCHITECTURE_DIAGRAM.md)

---

## 📁 关键文件位置

### 数据访问层
```
data-analysiter/database/
├── connection.py           # MongoDB 连接
├── models.py              # 数据模型
└── repositories.py        # CRUD 操作
```

### API 层
```
data-analysiter/api/
├── server.py              # FastAPI 主程序
├── routers/               # 路由定义
└── services/              # 业务逻辑
```

### 数据处理
```
data-analysiter/processors/
├── clean_data.py          # 数据清洗
├── analyze.py             # LLM 分析
└── pipeline.py            # 完整流程
```

---

## 🔍 常见问题

### 启动失败？
```bash
# 检查环境变量
cat .env | grep -v '^#'

# 检查虚拟环境
which python
```

### MongoDB 连接失败？
```bash
# 验证连接字符串
echo $MONGO_URI

# 测试连接
python -c "from pymongo import MongoClient; MongoClient('$MONGO_URI').admin.command('ping')"
```

### API Key 无效？
```bash
# 检查 DeepSeek Key
echo $DEEPSEEK_API_KEY

# 测试 API
curl -X POST "https://api.deepseek.com/v1/chat/completions" \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY"
```

---

## 📚 文档导航

| 文档 | 用途 | 推荐 |
|------|------|------|
| [README.md](./README.md) | 项目总览 | ⭐⭐⭐⭐⭐ |
| [ARCHITECTURE_DIAGRAM.md](./ARCHITECTURE_DIAGRAM.md) | 完整架构图 | ⭐⭐⭐⭐⭐ |
| [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) | 项目总结 | ⭐⭐⭐⭐⭐ |
| [SECURITY_GUIDE.md](./SECURITY_GUIDE.md) | 安全指南 | ⭐⭐⭐⭐⭐ |
| [GITHUB_UPLOAD_GUIDE.md](./GITHUB_UPLOAD_GUIDE.md) | 上传指南 | ⭐⭐⭐⭐ |
| [QUICKSTART_V2.md](./data-analysiter/docs/QUICKSTART_V2.md) | 快速开始 | ⭐⭐⭐⭐ |
| [API_USAGE.md](./data-analysiter/docs/API_USAGE.md) | API 文档 | ⭐⭐⭐ |

---

## 🎯 工作流程

### 开发流程
1. **数据采集** → tikhub-data-collector
2. **数据处理** → processors/pipeline.py
3. **启动后端** → ./start.sh
4. **启动前端** → npm run dev
5. **测试功能** → 浏览器访问

### 上传流程
1. **安全检查** → ./security_check.sh
2. **Git 初始化** → git init
3. **提交代码** → git commit
4. **推送远程** → git push

---

## 🔐 安全清单

- [ ] 已创建所有 .env 文件
- [ ] .env 文件未被 Git 追踪
- [ ] 运行 security_check.sh 通过
- [ ] 代码中无硬编码密钥
- [ ] .gitignore 配置正确

---

## 📊 项目指标

- **文件数**: 117 个
- **代码行**: ~15,000 行
- **文档字数**: 20,000+ 字
- **架构层级**: 3 层
- **数据模型**: 6 个
- **API 端点**: 10+ 个

---

## 🆘 获取帮助

**问题**: 不知道从哪开始？
→ 阅读 [README.md](./README.md)

**问题**: 不理解架构？
→ 查看 [ARCHITECTURE_DIAGRAM.md](./ARCHITECTURE_DIAGRAM.md)

**问题**: 配置出错？
→ 参考 [QUICKSTART_V2.md](./data-analysiter/docs/QUICKSTART_V2.md)

**问题**: 准备上传？
→ 遵循 [GITHUB_UPLOAD_GUIDE.md](./GITHUB_UPLOAD_GUIDE.md)

---

## ✅ 快速验证

```bash
# 1. 检查配置
ls -la .env data-analysiter/.env tikhub-data-collector/.env

# 2. 安全检查
./security_check.sh

# 3. 启动测试
cd data-analysiter && ./start.sh

# 4. 访问 API 文档
open http://localhost:5001/docs
```

---

**最后更新**: 2026-01-23
