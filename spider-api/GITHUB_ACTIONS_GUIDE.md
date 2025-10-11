# GitHub Actions 定时爬虫部署指南

## 📋 目录

1. [概述](#概述)
2. [文件说明](#文件说明)
3. [配置步骤](#配置步骤)
4. [使用方法](#使用方法)
5. [监控和调试](#监控和调试)
6. [常见问题](#常见问题)

---

## 概述

本项目使用 GitHub Actions 实现小红书数据的定时爬取，具有以下特点：

- ✅ **定时执行**：每天自动运行 2 次（可自定义）
- ✅ **手动触发**：支持在 GitHub 页面手动启动爬虫
- ✅ **云端运行**：无需本地服务器，完全依赖 GitHub 基础设施
- ✅ **数据持久化**：直接存储到 MongoDB Atlas 云数据库
- ✅ **日志记录**：自动保存执行日志，便于排查问题
- ✅ **错误通知**：任务失败时可以接收通知

---

## 文件说明

### 1. `.github/workflows/spider.yml`
GitHub Actions 工作流配置文件，定义了：
- 触发条件（定时 + 手动）
- 运行环境（Ubuntu + Python 3.10）
- 执行步骤

### 2. `run_spider.py`
爬虫执行脚本，负责：
- 读取配置（用户列表）
- 爬取用户数据和笔记详情
- 存储到 MongoDB
- 生成执行报告

### 3. `spider_config.json`
配置文件，包含：
- 要爬取的用户 URL 列表
- 每次运行的笔记数量限制
- 爬取间隔时间

### 4. `logs/`
日志目录（自动创建），包含：
- 每日执行日志
- JSON 格式的执行报告

---

## 配置步骤

### 步骤 1: 创建配置文件

复制示例配置文件并修改：

```bash
cp spider_config.json.example spider_config.json
```

编辑 `spider_config.json`，添加你要爬取的用户 URL：

```json
{
  "user_urls": [
    "https://www.xiaohongshu.com/user/profile/5c9a77000000000010006e8f?xsec_token=YOUR_TOKEN",
    "https://www.xiaohongshu.com/user/profile/5e1a2b000000000001008f23?xsec_token=YOUR_TOKEN"
  ],
  "max_notes_per_run": 50,
  "crawl_interval_seconds": 3
}
```

**重要提示**：
- ⚠️ 不要将 `spider_config.json` 提交到 Git（已在 .gitignore 中）
- ⚠️ 确保 URL 包含完整的 `xsec_token` 参数

### 步骤 2: 配置 GitHub Secrets

在 GitHub 仓库页面设置敏感信息：

1. **打开仓库设置**
   ```
   你的仓库 → Settings → Secrets and variables → Actions
   ```

2. **点击 "New repository secret"**

3. **添加以下 Secrets**：

   | Name | Value | 说明 |
   |------|-------|------|
   | `MONGO_URI` | `mongodb+srv://user:password@cluster.mongodb.net/xhs_data?retryWrites=true&w=majority` | MongoDB Atlas 连接字符串 |
   | `COOKIES` | `你的小红书 Cookie 字符串` | 用于 API 认证 |

#### 如何获取 Cookie：

1. 打开浏览器（Chrome/Edge）
2. 访问 https://www.xiaohongshu.com/
3. 登录你的账号
4. 按 `F12` 打开开发者工具
5. 切换到 "Network" 标签
6. 刷新页面
7. 找到任意请求，查看 "Request Headers"
8. 复制 `Cookie` 字段的完整内容

**Cookie 示例**：
```
a1=xxxx; webId=yyyy; web_session=zzzz; ...
```

#### 如何获取 MongoDB URI：

1. 登录 [MongoDB Atlas](https://cloud.mongodb.com/)
2. 进入你的 Cluster
3. 点击 "Connect" → "Connect your application"
4. 复制连接字符串
5. 将 `<password>` 替换为你的实际密码

### 步骤 3: 提交代码到 GitHub

```bash
# 添加文件
git add .github/workflows/spider.yml
git add run_spider.py
git add spider_config.json.example

# 提交
git commit -m "feat: 添加 GitHub Actions 定时爬虫"

# 推送到 GitHub
git push origin main
```

**注意**：
- ✅ 提交 `.github/workflows/spider.yml`（工作流配置）
- ✅ 提交 `run_spider.py`（执行脚本）
- ✅ 提交 `spider_config.json.example`（配置示例）
- ❌ **不要提交** `spider_config.json`（包含真实 URL）
- ❌ **不要提交** `.env`（包含敏感信息）

---

## 使用方法

### 方式 1: 自动定时运行

GitHub Actions 会自动在以下时间执行：

| UTC 时间 | 北京时间 | 说明 |
|---------|---------|------|
| 08:00 | 16:00 | 下午场 |
| 20:00 | 次日 04:00 | 凌晨场 |

**修改定时时间**：

编辑 `.github/workflows/spider.yml` 中的 `cron` 表达式：

```yaml
schedule:
  # 每天早上 9 点（北京时间 17 点）
  - cron: '0 9 * * *'
  # 每周一早上 8 点
  - cron: '0 8 * * 1'
```

**Cron 表达式说明**：
```
┌───────────── 分钟 (0 - 59)
│ ┌───────────── 小时 (0 - 23)
│ │ ┌───────────── 日期 (1 - 31)
│ │ │ ┌───────────── 月份 (1 - 12)
│ │ │ │ ┌───────────── 星期 (0 - 6, 0 = 周日)
│ │ │ │ │
* * * * *
```

**示例**：
- `0 */6 * * *` - 每 6 小时运行一次
- `0 9,21 * * *` - 每天 9 点和 21 点运行
- `0 0 * * 0` - 每周日午夜运行

### 方式 2: 手动触发

1. **打开 GitHub Actions 页面**
   ```
   你的仓库 → Actions → 小红书数据爬虫定时任务
   ```

2. **点击 "Run workflow"**

3. **（可选）输入参数**：
   - **user_urls**: 临时指定要爬取的用户（逗号分隔）
   - **crawl_notes**: 是否爬取笔记详情（默认 true）

4. **点击绿色的 "Run workflow" 按钮**

5. **等待执行完成**（通常 5-15 分钟）

### 方式 3: 通过配置文件控制

**动态添加用户**：

1. 修改 `spider_config.json`
2. 提交并推送到 GitHub
3. 等待下次定时执行，或手动触发

**临时禁用某个用户**：

只需从 `user_urls` 数组中删除对应的 URL 即可。

---

## 监控和调试

### 查看执行日志

1. **打开 Actions 页面**
   ```
   你的仓库 → Actions
   ```

2. **选择最近的执行记录**

3. **点击 "spider" job**

4. **展开各个步骤查看详细日志**

**日志示例**：
```
🚀 开始执行定时爬虫任务
共需爬取 2 个用户
进度: 1/2
用户名: 测试用户
获取到 50 条笔记
✅ 用户数据已存储: 测试用户 | 粉丝: 27000 | 笔记: 50
```

### 下载执行日志

1. 在 Actions 执行页面
2. 滚动到底部的 "Artifacts" 区域
3. 下载 `spider-logs` 压缩包
4. 解压查看详细日志和 JSON 报告

### 监控执行状态

**方法 1: GitHub 邮件通知**

GitHub 会在工作流失败时自动发送邮件。

**方法 2: 添加自定义通知**

在 `.github/workflows/spider.yml` 中添加通知步骤：

```yaml
- name: 发送成功通知
  if: success()
  run: |
    curl -X POST "你的 Webhook URL" \
      -H "Content-Type: application/json" \
      -d '{"text": "✅ 爬虫任务执行成功"}'

- name: 发送失败通知
  if: failure()
  run: |
    curl -X POST "你的 Webhook URL" \
      -H "Content-Type: application/json" \
      -d '{"text": "❌ 爬虫任务执行失败"}'
```

**支持的通知方式**：
- Slack Webhook
- Discord Webhook
- 企业微信机器人
- 钉钉机器人
- Telegram Bot

### 查看 MongoDB 数据

使用 MongoDB Compass 连接数据库：

1. 打开 MongoDB Compass
2. 输入连接字符串（MONGO_URI）
3. 查看 `xhs_data` 数据库
4. 检查 `users` 和 `notes` 集合

**验证数据**：
```javascript
// 查看最新的用户数据
db.users.find().sort({last_updated: -1}).limit(1)

// 查看最新的笔记数据
db.notes.find().sort({last_updated: -1}).limit(10)

// 统计数据量
db.users.countDocuments()
db.notes.countDocuments()
```

---

## 常见问题

### Q1: GitHub Actions 没有自动运行？

**可能原因**：
1. **仓库未激活 Actions**
   - 解决：Settings → Actions → General → 勾选 "Allow all actions"

2. **Cron 时间配置错误**
   - 解决：检查 `.github/workflows/spider.yml` 中的 cron 表达式

3. **仓库长期无活动**
   - 解决：GitHub 会禁用 60 天无活动的仓库的定时任务，需要手动重新启用

### Q2: 执行失败，显示 "COOKIES 环境变量未设置"

**解决方法**：
1. 确认在 GitHub Secrets 中添加了 `COOKIES`
2. 名称必须完全一致（区分大小写）
3. 重新运行工作流

### Q3: Cookie 过期了怎么办？

**表现**：
- 日志显示 "认证失败"
- 返回 401 或 403 错误

**解决方法**：
1. 重新登录小红书网站
2. 获取新的 Cookie
3. 更新 GitHub Secrets 中的 `COOKIES`

### Q4: 爬取速度太慢或超时

**优化方法**：

1. **减少每次爬取的笔记数量**
   ```json
   {
     "max_notes_per_run": 20  // 从 50 减到 20
   }
   ```

2. **增加爬取间隔**
   ```json
   {
     "crawl_interval_seconds": 5  // 从 3 秒增加到 5 秒
   }
   ```

3. **分批爬取**
   - 不要一次爬取所有用户
   - 将用户分成多个配置文件
   - 创建多个定时任务

### Q5: 如何避免被反爬？

**最佳实践**：

1. **控制频率**
   - 不要设置过于频繁的定时任务（建议至少间隔 6 小时）
   - 增加请求间隔（3-5 秒）

2. **使用真实 Cookie**
   - 使用正常登录的账号
   - 定期更新 Cookie

3. **限制数量**
   - 每次爬取不超过 50 篇笔记
   - 不要同时爬取过多用户

4. **错误处理**
   - 遇到错误自动跳过
   - 不要无限重试

### Q6: MongoDB 连接失败

**检查项**：

1. **连接字符串格式**
   ```
   mongodb+srv://username:password@cluster.mongodb.net/xhs_data?retryWrites=true&w=majority
   ```

2. **网络访问白名单**
   - MongoDB Atlas → Network Access
   - 添加 `0.0.0.0/0`（允许所有 IP）

3. **数据库用户权限**
   - 确保用户有读写权限

### Q7: 如何测试配置是否正确？

**本地测试**：

```bash
# 1. 确保 .env 文件包含所需变量
cat .env
# MONGO_URI=mongodb+srv://...
# COOKIES=a1=xxx...

# 2. 运行爬虫脚本
python run_spider.py

# 3. 检查日志输出
```

**GitHub 测试**：

1. 先手动触发一次工作流
2. 查看执行日志
3. 确认无错误后再启用定时任务

---

## 进阶配置

### 多环境支持

创建不同的工作流文件：

```yaml
# .github/workflows/spider-dev.yml (开发环境)
name: 开发环境爬虫
on:
  workflow_dispatch:
env:
  MONGO_URI: ${{ secrets.MONGO_URI_DEV }}

# .github/workflows/spider-prod.yml (生产环境)
name: 生产环境爬虫
on:
  schedule:
    - cron: '0 8 * * *'
env:
  MONGO_URI: ${{ secrets.MONGO_URI_PROD }}
```

### 并发控制

避免多个任务同时运行：

```yaml
concurrency:
  group: spider-task
  cancel-in-progress: true
```

### 条件执行

只在特定条件下运行：

```yaml
jobs:
  spider:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'  # 仅在 main 分支运行
```

---

## 成本说明

**GitHub Actions 免费额度**：
- 公开仓库：无限制
- 私有仓库：每月 2000 分钟

**单次执行时间**：约 10-20 分钟

**每月消耗**：
- 每天 2 次 × 30 天 × 15 分钟 = 900 分钟
- 在免费额度内 ✅

**MongoDB Atlas 免费额度**：
- 存储：512 MB
- 完全免费 ✅

---

## 总结

✅ **已完成**：
- GitHub Actions 工作流配置
- 爬虫执行脚本
- 配置文件模板
- 完整文档

🎯 **下一步**：
1. 配置 GitHub Secrets
2. 创建 `spider_config.json`
3. 提交代码到 GitHub
4. 手动触发测试
5. 启用定时任务

📚 **相关资源**：
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [MongoDB Atlas 文档](https://docs.atlas.mongodb.com/)
- [小红书 API 分析](https://github.com/topics/xiaohongshu)

---

**更新时间**: 2025-10-11  
**文档版本**: v1.0  
**维护者**: 你的名字
