# TikHub 数据采集工具

这个文件夹包含所有从 TikHub API 获取小红书数据的脚本。

## 📁 文件说明

### test_user_tikhub.py
**功能**：从 TikHub API 获取小红书用户的笔记数据并存入 MongoDB

**使用方法**：
```bash
cd tikhub-data-collector
python test_user_tikhub.py
```

**配置**：
- 修改文件中的 `USER_ID` 变量为目标用户ID
- 确保环境变量中设置了 `TIKHUB_TOKEN`，或使用默认值

**输出**：
- 数据存储到 MongoDB (`tikhub_xhs` 数据库的 `user_snapshots` 集合)
- 包含用户信息和所有笔记内容

## 🔧 环境要求

```bash
# 安装依赖
pip install requests pymongo

# 或使用 data-analysiter 的虚拟环境
source ../data-analysiter/.venv/bin/activate
```

## 🌐 TikHub API 配置

- **API URL**: `https://api.tikhub.io/api/v1/xiaohongshu/web/get_user_notes_v2`
- **认证**: Bearer Token (从环境变量 `TIKHUB_TOKEN` 读取)
- **文档**: 查看 TikHub API 官方文档

## 📊 数据流程

```
TikHub API → test_user_tikhub.py → MongoDB (user_snapshots)
                                      ↓
                              data-analysiter 处理
```

## 💡 提示

1. 确保 MongoDB 连接正常（需要访问 `xhs-cluster.omeyngi.mongodb.net`）
2. TikHub API 有速率限制，脚本会自动处理重试和延迟
3. 数据采集后，使用 `data-analysiter` 中的工具进行进一步处理和分析

## 🔗 相关项目

- **data-analysiter**: 数据处理和分析工具
- **MediaCrawler**: 爬虫工具（备用方案）
