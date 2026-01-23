# 🔐 GitHub 上传安全指南

## ✅ 已完成的安全措施

本项目已完成以下无害化处理，可以安全上传到 GitHub：

### 1. 环境变量管理

#### ✅ 创建的配置文件

```
.env.example          # 项目根目录配置模板
data-analysiter/.env.example     # 后端配置模板
tikhub-data-collector/.env.example  # 数据采集工具配置模板
```

#### ✅ 需要配置的敏感信息

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `MONGO_URI` | MongoDB 连接字符串 | `mongodb+srv://user:pass@cluster.mongodb.net/` |
| `DATABASE_NAME` | 数据库名称 | `tikhub_xhs` |
| `DEEPSEEK_API_KEY` | DeepSeek AI API 密钥 | `sk-your-api-key-here` |
| `TIKHUB_TOKEN` | TikHub API 令牌 | `Bearer your-token-here` |

### 2. .gitignore 配置

#### ✅ 已添加到 .gitignore

```gitignore
# 环境变量（最重要！）
.env
.env.local
.env.*.local

# 虚拟环境
.venv/
venv/

# 数据文件（可能包含用户隐私）
data/raw/*.json
data/analyses/*.json

# IDE 配置
.vscode/
.idea/

# 浏览器数据
browser_data/
```

### 3. 代码修改

#### ✅ 已修改的文件

| 文件 | 修改内容 |
|------|---------|
| `database/connection.py` | 移除默认 MongoDB URI，必须从环境变量读取 |
| `start.sh` | 从 .env 文件加载配置，不再硬编码 API Key |
| `tikhub-data-collector/test_user_tikhub.py` | 移除默认 TikHub Token |
| `processors/pipeline.py` | 移除硬编码的 API Key 和 MongoDB URI |
| `processors/analyze.py` | 移除硬编码的 API Key |
| `processors/clean_data.py` | 移除硬编码的 MongoDB URI |

### 4. 文档更新

#### ✅ 已更新的文档

- `README.md` - 主项目说明
- `data-analysiter/README.md` - 后端说明
- `docs/ARCHITECTURE.md` - 架构文档
- `docs/QUICKSTART_V2.md` - 快速开始指南
- `docs/COMMANDS.md` - 命令参考

所有文档中的敏感信息已替换为占位符或环境变量引用。

---

## 📋 上传前检查清单

### 必须完成（否则会泄露敏感信息）

- [ ] ✅ 确认 `.gitignore` 已创建并包含 `.env`
- [ ] ✅ 确认所有 `.env.example` 文件已创建
- [ ] ✅ 确认代码中没有硬编码的密钥和密码
- [ ] ✅ 删除或添加到 .gitignore：真实的 `.env` 文件

### 推荐完成（保护隐私）

- [ ] 检查 `data/` 目录下的 JSON 文件是否包含个人信息
- [ ] 检查日志文件是否包含敏感信息
- [ ] 检查 `browser_data/` 是否已在 .gitignore 中
- [ ] 确认测试文件中没有真实用户数据

---

## 🚀 上传 GitHub 步骤

### 1. 创建 .env 文件（本地使用，不上传）

```bash
# 在项目根目录
cp .env.example .env
vim .env  # 填入你的真实配置

# 在 data-analysiter 目录
cd data-analysiter
cp .env.example .env
vim .env

# 在 tikhub-data-collector 目录
cd ../tikhub-data-collector
cp .env.example .env
vim .env
```

### 2. 验证 .gitignore 生效

```bash
# 在项目根目录执行
git status

# 确保以下文件不会出现：
# - .env
# - .env.local
# - .venv/
# - __pycache__/
# - data/raw/*.json（如果包含敏感数据）
```

### 3. 初始化 Git 仓库

```bash
cd /Users/tangliam/Projects/xhs_data_Project

# 初始化仓库
git init

# 添加所有文件（.gitignore 会自动排除敏感文件）
git add .

# 查看将要提交的文件
git status

# ⚠️ 再次检查：确保没有 .env 文件！
```

### 4. 提交并推送

```bash
# 首次提交
git commit -m "Initial commit: XHS Data Analysis Platform"

# 在 GitHub 创建仓库后
git remote add origin https://github.com/your-username/your-repo.git
git branch -M main
git push -u origin main
```

---

## ⚠️ 万一泄露了敏感信息怎么办？

### 立即行动

1. **立即轮换所有密钥**
   ```bash
   # MongoDB: 在 MongoDB Atlas 修改密码
   # DeepSeek: 在控制台删除并重新生成 API Key
   # TikHub: 联系客服重置 Token
   ```

2. **从 Git 历史中彻底删除**
   ```bash
   # 使用 git-filter-repo 或 BFG Repo-Cleaner
   # 不要使用简单的 git rm！
   
   # 方法1: 使用 git-filter-repo（推荐）
   pip install git-filter-repo
   git filter-repo --path .env --invert-paths
   
   # 方法2: 使用 BFG
   # 下载 bfg.jar
   java -jar bfg.jar --delete-files .env
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   
   # 强制推送
   git push origin --force --all
   ```

3. **检查 GitHub 是否已缓存**
   - GitHub 可能缓存了之前的 commit
   - 联系 GitHub Support 请求清除缓存

---

## 🔒 最佳实践

### 开发环境

1. **使用环境变量管理工具**
   ```bash
   # 安装 python-dotenv
   pip install python-dotenv
   
   # 在代码中
   from dotenv import load_dotenv
   load_dotenv()  # 自动加载 .env
   ```

2. **永远不要 commit .env 文件**
   ```bash
   # 添加 pre-commit hook
   echo '#!/bin/bash
   if git diff --cached --name-only | grep -q "\.env$"; then
     echo "❌ Error: .env file detected in commit"
     exit 1
   fi' > .git/hooks/pre-commit
   
   chmod +x .git/hooks/pre-commit
   ```

3. **定期轮换密钥**
   - 每 90 天轮换一次 API Key
   - 使用密钥管理工具（如 AWS Secrets Manager）

### 生产环境

1. **使用密钥管理服务**
   - AWS Secrets Manager
   - HashiCorp Vault
   - Azure Key Vault

2. **限制密钥权限**
   - MongoDB: 创建只读用户用于分析
   - API Keys: 设置 IP 白名单

3. **监控异常访问**
   - 设置 MongoDB Atlas 告警
   - 监控 API 使用量

---

## 📊 安全检查脚本

创建一个检查脚本，自动扫描敏感信息：

```bash
# 创建 security_check.sh
cat > security_check.sh << 'EOF'
#!/bin/bash

echo "🔍 安全检查开始..."

# 检查是否有 .env 文件被追踪
if git ls-files | grep -q "\.env$"; then
    echo "❌ 发现 .env 文件在 git 追踪中！"
    exit 1
fi

# 检查代码中的敏感模式
echo "检查硬编码的密钥..."
if grep -r "sk-[a-zA-Z0-9]\{32,\}" --include="*.py" .; then
    echo "❌ 发现可能的 API Key！"
    exit 1
fi

if grep -r "mongodb+srv://[^:]*:[^@]*@" --include="*.py" --include="*.md" .; then
    echo "❌ 发现可能的 MongoDB 凭据！"
    exit 1
fi

echo "✅ 安全检查通过！"
EOF

chmod +x security_check.sh
./security_check.sh
```

---

## 📚 相关资源

- [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [12-Factor App: Config](https://12factor.net/config)
- [OWASP: Sensitive Data Exposure](https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure)

---

## ✅ 总结

你的项目现在已经可以安全上传到 GitHub 了！

### 已完成的安全措施

✅ 所有敏感信息已移到环境变量  
✅ .gitignore 已配置  
✅ .env.example 已创建  
✅ 代码中没有硬编码的密钥  
✅ 文档已更新  

### 下一步

1. 在本地创建 `.env` 文件并配置（**不要上传！**）
2. 运行 `git status` 确认 `.env` 不在追踪列表
3. 提交代码到 GitHub
4. 在 GitHub 仓库的 README 中提醒其他开发者配置 `.env`

**记住**：`.env` 文件只存在于本地，永远不要上传到 GitHub！
