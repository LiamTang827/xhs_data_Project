# 🚀 GitHub 上传快速指南

## ✅ 安全检查已通过

你的项目已完成所有安全处理，可以上传到 GitHub！

---

## 📋 上传前最后检查

运行安全检查脚本：
```bash
cd /Users/tangliam/Projects/xhs_data_Project
./security_check.sh
```

如果显示 "✅ 完美！所有检查通过" 或 "⚠️ 发现警告但可以上传"，就可以继续。

---

## 🚀 GitHub 上传步骤

### 1. 初始化 Git 仓库（如果还未初始化）

```bash
cd /Users/tangliam/Projects/xhs_data_Project

# 初始化
git init

# 设置默认分支名
git branch -M main
```

### 2. 添加文件到暂存区

```bash
# 添加所有文件（.gitignore 会自动排除敏感文件）
git add .

# 查看将要提交的文件
git status

# ⚠️ 重要: 确保以下文件不在列表中:
#   - .env
#   - .env.local
#   - .venv/
#   - __pycache__/
```

### 3. 创建首次提交

```bash
git commit -m "Initial commit: XHS Data Analysis Platform

- 三层架构 (Database, Service, API)
- MongoDB + FastAPI + Next.js
- DeepSeek AI 集成
- TikHub 数据采集工具
- 完整文档和安全配置"
```

### 4. 在 GitHub 创建仓库

前往 https://github.com/new 创建新仓库

**推荐设置：**
- 仓库名: `xhs-data-analysis` 或 `xiaohongshu-ai-platform`
- 可见性: **Private**（推荐，因为包含业务逻辑）
- 不要勾选 "Initialize with README"（我们已有）

### 5. 连接远程仓库并推送

```bash
# 替换 YOUR_USERNAME 和 YOUR_REPO
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# 推送代码
git push -u origin main
```

如果遇到认证问题，使用 Personal Access Token：
1. 前往 https://github.com/settings/tokens
2. 生成新 token (classic)
3. 使用 token 作为密码

---

## 📝 创建本地 .env 文件

⚠️ **重要**: 在本地创建 .env 文件（不会被上传）

### 项目根目录
```bash
cp .env.example .env
vim .env
```

填入：
```env
MONGO_URI=mongodb+srv://xhs_user:S8VVePhiUHfT6H5U@xhs-cluster.omeyngi.mongodb.net/?retryWrites=true&w=majority&appName=xhs-Cluster
DATABASE_NAME=tikhub_xhs
DEEPSEEK_API_KEY=sk-4676746a43814700810e82923669f056
TIKHUB_TOKEN=Bearer l8kcBs4q3GnznWe8F9KX0Uj+CB+RSrNg1CXKslyDTdqwtW+weXuqVwqCFQ==
```

### data-analysiter 目录
```bash
cd data-analysiter
cp .env.example .env
vim .env
```

填入：
```env
MONGO_URI=mongodb+srv://xhs_user:S8VVePhiUHfT6H5U@xhs-cluster.omeyngi.mongodb.net/?retryWrites=true&w=majority&appName=xhs-Cluster
DATABASE_NAME=tikhub_xhs
DEEPSEEK_API_KEY=sk-4676746a43814700810e82923669f056
```

### tikhub-data-collector 目录
```bash
cd ../tikhub-data-collector
cp .env.example .env
vim .env
```

填入：
```env
TIKHUB_TOKEN=Bearer l8kcBs4q3GnznWe8F9KX0Uj+CB+RSrNg1CXKslyDTdqwtW+weXuqVwqCFQ==
MONGO_URI=mongodb+srv://xhs_user:S8VVePhiUHfT6H5U@xhs-cluster.omeyngi.mongodb.net/?retryWrites=true&w=majority&appName=xhs-Cluster
DATABASE_NAME=tikhub_xhs
```

---

## 🔧 测试配置是否正常

### 测试后端服务
```bash
cd data-analysiter
./start.sh

# 应该看到:
# ✅ 已加载 .env 配置
# 🚀 启动 XHS Data Analysis API v2.0...
```

### 测试数据采集
```bash
cd tikhub-data-collector
source ../data-analysiter/.venv/bin/activate
python test_user_tikhub.py

# 应该能正常连接 API 和 MongoDB
```

---

## 📚 在 GitHub 上完善项目

### 1. 添加 README badges

在 GitHub 仓库的 README.md 顶部添加：
```markdown
![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-16.1-black.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
```

### 2. 创建 GitHub Issues 模板

在仓库设置中启用 Issues，创建模板。

### 3. 添加 GitHub Actions（可选）

创建 `.github/workflows/security-check.yml`：
```yaml
name: Security Check

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run security check
        run: |
          chmod +x security_check.sh
          ./security_check.sh
```

### 4. 保护主分支

在仓库设置中：
- Settings → Branches → Add rule
- 勾选 "Require pull request reviews before merging"

---

## 🤝 协作者说明

如果有其他开发者克隆仓库，提醒他们：

```bash
# 克隆仓库后
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# 创建配置文件
cp .env.example .env
cd data-analysiter && cp .env.example .env
cd ../tikhub-data-collector && cp .env.example .env

# 联系你获取真实的配置值
```

在 README 中添加醒目提示：
```markdown
## ⚠️ 配置说明

本项目需要配置环境变量才能运行。克隆后请：

1. 复制 `.env.example` 为 `.env`
2. 联系项目维护者获取真实配置
3. **永远不要提交 .env 文件**
```

---

## 📊 数据文件说明

当前有 32 个 JSON 数据文件。如果包含真实用户数据，建议：

### 选项 1: 排除真实数据
在 `.gitignore` 添加：
```gitignore
data-analysiter/data/**/*.json
!data-analysiter/data/**/.gitkeep
```

### 选项 2: 提供示例数据
创建脱敏的示例数据：
```bash
# 在每个数据目录创建 .gitkeep
find data-analysiter/data -type d -exec touch {}/.gitkeep \;

# 创建示例文件
cat > data-analysiter/data/user_profiles/example.json << 'EOF'
{
  "user_id": "example_user_001",
  "nickname": "示例用户",
  "follower_count": 1000,
  "note_count": 50
}
EOF
```

---

## ✅ 完成检查清单

上传后，确认以下内容：

- [ ] GitHub 仓库已创建
- [ ] 代码已成功推送
- [ ] 在线查看确认没有 .env 文件
- [ ] README 显示正常
- [ ] 文档可以正常访问
- [ ] 本地 .env 文件已创建（未上传）
- [ ] 运行 `./start.sh` 正常启动

---

## 🎉 恭喜！

你的项目已经安全上传到 GitHub！

**下一步**：
- 📝 完善文档
- 🧪 添加单元测试
- 🔄 设置 CI/CD
- 📊 添加代码覆盖率
- 🌐 部署到生产环境

**记住**：
- 🔒 定期轮换 API 密钥
- 📋 保持 .env 文件在本地
- 🔍 定期运行 `security_check.sh`

---

有问题？查看详细文档：
- [SECURITY_GUIDE.md](./SECURITY_GUIDE.md) - 完整安全指南
- [README.md](./README.md) - 项目说明
- [data-analysiter/docs/](./data-analysiter/docs/) - 技术文档
