# GitHub Actions 定时爬虫配置指南

## 📋 概述

这个 GitHub Workflow 可以让您的小红书爬虫定时自动运行，无需手动执行。

## 🔧 配置步骤

### 1. 设置 GitHub Secrets

在 GitHub 仓库中配置敏感信息（不会被公开）：

1. 进入您的 GitHub 仓库页面
2. 点击 `Settings`（设置）
3. 在左侧菜单找到 `Secrets and variables` → `Actions`
4. 点击 `New repository secret` 按钮

需要添加以下两个 Secrets：

#### Secret 1: `XHS_COOKIES`
- **Name**: `XHS_COOKIES`
- **Value**: 您的小红书 Cookies 字符串
- 格式示例：
  ```
  a1=xxx; webId=xxx; xsecappid=xxx; ...
  ```

#### Secret 2: `MONGO_URI`
- **Name**: `MONGO_URI`
- **Value**: 您的 MongoDB 连接字符串
- 格式示例：
  ```
  mongodb+srv://username:password@cluster.mongodb.net/xhs_data?retryWrites=true&w=majority
  ```

### 2. 定时执行配置

Workflow 已配置为每天 UTC 00:00（北京时间 08:00）自动执行。

如需修改执行频率，编辑 `.github/workflows/spider_cron.yml` 中的 cron 表达式：

```yaml
schedule:
  - cron: '0 0 * * *'  # 每天 00:00 UTC
```

**常用 cron 表达式示例：**

| 描述 | Cron 表达式 |
|------|------------|
| 每天一次（UTC 00:00） | `0 0 * * *` |
| 每 12 小时一次 | `0 */12 * * *` |
| 每 6 小时一次 | `0 */6 * * *` |
| 每周一早上 | `0 0 * * 1` |
| 每月 1 号 | `0 0 1 * *` |

**注意：** GitHub Actions 的 cron 使用 UTC 时区，需要转换为北京时间（UTC+8）。

## 🚀 使用方法

### 方法 1：定时自动执行

配置好 Secrets 后，Workflow 会按照设定的时间自动运行，无需手动操作。

### 方法 2：手动触发执行

1. 进入 GitHub 仓库的 `Actions` 标签页
2. 在左侧选择 `定时爬取小红书数据` workflow
3. 点击右上角的 `Run workflow` 按钮
4. 可以输入要爬取的 URL（可选）：
   - **user_urls**: 用户主页 URL，多个用逗号分隔
   - **note_urls**: 笔记 URL，多个用逗号分隔
5. 点击绿色的 `Run workflow` 按钮

**示例输入：**

```
user_urls: 
https://www.xiaohongshu.com/user/profile/xxx?xsec_token=xxx,
https://www.xiaohongshu.com/user/profile/yyy?xsec_token=yyy

note_urls:
https://www.xiaohongshu.com/explore/aaa?xsec_token=xxx,
https://www.xiaohongshu.com/explore/bbb?xsec_token=yyy
```

### 方法 3：配置默认爬取列表

如果您想要 Workflow 自动爬取固定的用户或笔记列表，可以：

**选项 A：修改 Workflow 文件**

编辑 `.github/workflows/spider_cron.yml`，在脚本中添加默认 URL：

```python
if not user_urls_str and not note_urls_str:
    logger.warning("⚠️ 未指定要爬取的 URL，使用默认列表...")
    user_urls_str = "https://www.xiaohongshu.com/user/profile/xxx,https://..."
```

**选项 B：创建配置文件**（推荐）

在 `spider-api` 目录下创建 `spider_targets.json`：

```json
{
  "users": [
    "https://www.xiaohongshu.com/user/profile/xxx?xsec_token=xxx",
    "https://www.xiaohongshu.com/user/profile/yyy?xsec_token=yyy"
  ],
  "notes": [
    "https://www.xiaohongshu.com/explore/aaa?xsec_token=xxx",
    "https://www.xiaohongshu.com/explore/bbb?xsec_token=yyy"
  ]
}
```

然后修改执行脚本读取这个文件。

## 📊 查看执行结果

### 查看执行状态

1. 进入 GitHub 仓库的 `Actions` 标签页
2. 点击对应的 workflow 运行记录
3. 查看每个步骤的执行日志

### 查看日志

- ✅ 成功的任务会显示绿色对勾
- ❌ 失败的任务会显示红色叉号，并上传日志文件供下载

### 监控数据

爬取的数据会自动保存到您配置的 MongoDB 数据库中。

## ⚠️ 注意事项

### 1. Cookies 有效期

小红书的 Cookies 会过期，需要定期更新 `XHS_COOKIES` Secret。

**更新步骤：**
1. 在浏览器中重新登录小红书
2. 获取新的 Cookies
3. 更新 GitHub Secret

### 2. 执行频率限制

- GitHub Actions 对免费账户有使用时长限制
- 不建议设置过于频繁的执行时间
- 建议每天 1-2 次即可

### 3. 反爬虫对策

- Selenium 会模拟真实浏览器，但仍需注意频率
- 不要同时爬取大量数据
- 建议在脚本中添加延迟（sleep）

### 4. 网络环境

GitHub Actions 运行在国外服务器上，访问小红书可能会受到限制。如果遇到问题：

- 可以考虑添加代理配置
- 或使用自己的服务器运行定时任务

## 🔍 故障排查

### 问题 1：Workflow 执行失败

**可能原因：**
- Cookies 过期
- MongoDB 连接失败
- Selenium 启动失败

**解决方法：**
1. 检查 GitHub Secrets 是否正确配置
2. 查看 Actions 日志中的详细错误信息
3. 下载上传的日志文件进行排查

### 问题 2：数据未保存到数据库

**可能原因：**
- MongoDB 连接字符串错误
- 网络连接问题

**解决方法：**
1. 验证 `MONGO_URI` 是否正确
2. 确保 MongoDB 允许 GitHub Actions 的 IP 访问

### 问题 3：Selenium 相关错误

**可能原因：**
- ChromeDriver 版本不匹配
- 页面加载超时

**解决方法：**
- Workflow 会自动安装最新的 Chrome 和 ChromeDriver
- 如果仍有问题，可以在脚本中增加等待时间

## 📝 自定义配置

### 增加邮件通知

可以在 Workflow 最后添加邮件通知步骤，使用 GitHub Actions 的邮件服务。

### 增加数据导出

可以在 Workflow 中添加步骤，将爬取的数据导出为 CSV 或 JSON 文件，并上传为 Artifact。

### 并行执行

如果需要爬取大量数据，可以配置矩阵策略，将任务分成多个并行作业。

## 📚 相关资源

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Cron 表达式生成器](https://crontab.guru/)
- [GitHub Actions 定时任务最佳实践](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule)

## 🆘 需要帮助？

如果遇到问题，请：

1. 查看 Actions 日志中的详细错误信息
2. 检查所有配置是否正确
3. 确保本地环境可以正常运行爬虫

---

**提示：** 第一次运行前，建议先手动触发一次 Workflow，确保所有配置都正确无误。
