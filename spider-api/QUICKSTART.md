# 🚀 快速开始：GitHub Actions 定时爬虫

## 📝 5 分钟配置指南

### 1️⃣ 创建配置文件

```bash
# 复制示例配置
cp spider_config.json.example spider_config.json

# 编辑配置文件，添加你要爬取的用户URL
# vim spider_config.json
```

**配置示例**：
```json
{
  "user_urls": [
    "https://www.xiaohongshu.com/user/profile/你的用户ID?xsec_token=你的token"
  ],
  "max_notes_per_run": 50
}
```

---

### 2️⃣ 配置 GitHub Secrets

1. 打开你的 GitHub 仓库
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 添加两个 Secrets：

| Name | Value |
|------|-------|
| `MONGO_URI` | `mongodb+srv://user:pass@cluster.mongodb.net/xhs_data` |
| `COOKIES` | 你的小红书 Cookie 字符串 |

#### 如何获取 Cookie？

1. 打开小红书网站：https://www.xiaohongshu.com/
2. 登录你的账号
3. 按 `F12` 打开开发者工具
4. 切换到 **Network** 标签
5. 刷新页面
6. 随便点击一个请求
7. 在 **Request Headers** 中找到 `Cookie`
8. 复制完整的 Cookie 字符串

---

### 3️⃣ 提交代码到 GitHub

```bash
# 添加文件
git add .github/workflows/spider.yml
git add run_spider.py
git add spider_config.json.example
git add .gitignore

# 提交
git commit -m "feat: 添加 GitHub Actions 定时爬虫"

# 推送
git push origin main
```

**⚠️ 重要提示**：
- ✅ 提交 `spider_config.json.example`（示例文件）
- ❌ 不要提交 `spider_config.json`（包含真实数据）
- ❌ 不要提交 `.env`（包含敏感信息）

---

### 4️⃣ 手动测试一次

1. 打开 GitHub 仓库
2. 点击 **Actions** 标签
3. 选择 **小红书数据爬虫定时任务**
4. 点击右上角 **Run workflow**
5. 点击绿色按钮 **Run workflow**
6. 等待执行完成（约 5-15 分钟）

---

### 5️⃣ 查看执行结果

#### 查看日志
在 Actions 页面点击执行记录，查看详细日志。

#### 查看数据库
使用 MongoDB Compass 连接到你的 MongoDB Atlas 数据库，查看 `xhs_data` 数据库中的数据。

---

## ⏰ 定时任务说明

默认配置：
- **每天 16:00**（北京时间）
- **每天 04:00**（北京时间）

修改定时：编辑 `.github/workflows/spider.yml` 中的 `cron` 表达式。

---

## 📊 监控和维护

### 查看执行历史
```
GitHub 仓库 → Actions → 查看所有执行记录
```

### 下载日志
```
Actions → 选择执行记录 → 底部 Artifacts → 下载 spider-logs
```

### 更新 Cookie
Cookie 通常 30-90 天过期，需要定期更新：
```
Settings → Secrets → 编辑 COOKIES
```

---

## ❓ 常见问题

**Q: 为什么没有自动运行？**
- 检查 Settings → Actions → 确保已启用 Actions

**Q: 执行失败了怎么办？**
- 查看 Actions 日志
- 检查 Secrets 是否配置正确
- 确认 Cookie 是否过期

**Q: 如何添加更多用户？**
- 编辑 `spider_config.json`
- 提交并推送到 GitHub

---

## 📚 详细文档

查看完整文档：[GITHUB_ACTIONS_GUIDE.md](./GITHUB_ACTIONS_GUIDE.md)

---

## 🎉 完成！

现在你的爬虫会自动运行，数据会自动存储到 MongoDB！

有问题？查看 [常见问题](./GITHUB_ACTIONS_GUIDE.md#常见问题) 或提交 Issue。
