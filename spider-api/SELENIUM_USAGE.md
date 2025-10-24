# 使用 Selenium 爬虫的完整指南

## 📋 概述

由于小红书加强了反爬虫机制，原有的 `requests` 请求方式已经无法正常工作。新的 `xhs_selenium_apis.py` 使用 Selenium 模拟真实浏览器行为，可以绕过反爬虫检测。

## 🔧 安装依赖

### 1. 安装 Python 依赖包

```bash
pip install -r requirements.txt
```

新增的依赖包包括：
- `selenium==4.15.2` - Web 自动化测试框架
- `webdriver-manager==4.0.1` - 自动管理浏览器驱动
- `motor==3.3.2` - 异步 MongoDB 驱动

### 2. 安装 Chrome 浏览器

Selenium 需要 Chrome 浏览器才能运行。

**macOS:**
```bash
brew install --cask google-chrome
```

**已安装的话可以跳过此步骤。**

### 3. ChromeDriver 会自动下载

使用 `webdriver-manager` 库会自动下载并管理 ChromeDriver，无需手动安装。

## 🚀 如何使用

### 方法 1: 直接替换（推荐）

在您的 `service.py` 中，只需要修改导入语句：

```python
# 原来的导入
# from app.apis.xhs_pc_apis import XHS_Apis

# 新的导入
from app.apis.xhs_selenium_apis import XHS_Selenium_Apis as XHS_Apis
```

这样您就可以无缝切换到 Selenium 版本，**无需修改任何其他代码**。

### 方法 2: 保留两个版本

如果您想同时保留两个版本，可以这样：

```python
from app.apis.xhs_pc_apis import XHS_Apis as XHS_Requests_Apis
from app.apis.xhs_selenium_apis import XHS_Selenium_Apis

class SpiderService:
    def __init__(self, use_selenium=True):
        if use_selenium:
            self.api = XHS_Selenium_Apis(headless=True)
        else:
            self.api = XHS_Requests_Apis()
```

## 📝 API 方法说明

### 1. `get_user_info(user_id, cookies_str, proxies=None)`

获取用户的基本信息。

**参数:**
- `user_id`: 用户 ID
- `cookies_str`: Cookie 字符串（格式与原 API 一致）
- `proxies`: 代理配置（保留接口一致性，Selenium 暂不支持）

**返回:**
```python
(success: bool, msg: str, res_json: dict)
```

**返回数据格式:**
```json
{
  "success": true,
  "msg": "success",
  "data": {
    "basic_info": {
      "user_id": "...",
      "nickname": "用户昵称",
      "avatar": "头像URL",
      "desc": "个人简介",
      "ip_location": "IP 归属地",
      "gender": 0,
      "follows": 123,
      "fans": 456,
      "interaction": 789,
      "red_id": "小红书号"
    }
  }
}
```

### 2. `get_user_all_notes(user_url, cookies_str, proxies=None)`

获取用户的所有笔记列表。

**参数:**
- `user_url`: 用户主页完整 URL
- `cookies_str`: Cookie 字符串
- `proxies`: 代理配置（保留接口一致性）

**返回:**
```python
(success: bool, msg: str, note_list: list)
```

**返回数据格式:**
```python
[
    {
        'note_id': '笔记ID',
        'xsec_token': 'xsec_token',
        'type': 'normal',  # 或 'video'
        'title': '笔记标题',
        'cover': '封面图URL'
    },
    ...
]
```

### 3. `get_note_info(note_url, cookies_str, proxies=None)`

获取单篇笔记的详细信息。

**参数:**
- `note_url`: 笔记完整 URL
- `cookies_str`: Cookie 字符串
- `proxies`: 代理配置（保留接口一致性）

**返回:**
```python
(success: bool, msg: str, res_json: dict)
```

**返回数据格式:**
```json
{
  "success": true,
  "msg": "success",
  "data": {
    "items": [
      {
        "id": "笔记ID",
        "note_card": {
          "title": "笔记标题",
          "desc": "笔记描述",
          "type": "normal",
          "interact_info": {
            "liked_count": "123",
            "collected_count": "45",
            "comment_count": "67",
            "share_count": "89"
          },
          "tag_list": [...],
          "time": 1234567890000,
          "user": {...}
        }
      }
    ]
  }
}
```

## ⚙️ 配置选项

### 初始化参数

```python
XHS_Selenium_Apis(headless=True, wait_timeout=10)
```

**参数说明:**
- `headless`: 是否使用无头模式（不显示浏览器窗口）
  - `True` (默认): 后台运行，适合生产环境
  - `False`: 显示浏览器，适合调试
- `wait_timeout`: 页面加载最大等待时间（秒），默认 10 秒

### 使用示例

```python
# 开发/调试环境：可以看到浏览器操作
api = XHS_Selenium_Apis(headless=False, wait_timeout=15)

# 生产环境：后台运行
api = XHS_Selenium_Apis(headless=True, wait_timeout=10)
```

## 🔍 工作原理

1. **模拟真实浏览器**: Selenium 启动真正的 Chrome 浏览器，完全模拟人类用户行为
2. **注入 Cookies**: 自动将您提供的 Cookies 注入到浏览器中，保持登录状态
3. **隐藏自动化特征**: 通过多种技术手段隐藏 `webdriver` 特征，避免被检测
4. **提取页面数据**: 
   - 方法1: 从页面的 `__INITIAL_STATE__` 脚本标签中提取 JSON 数据（主要方式）
   - 方法2: 通过 DOM 元素直接提取（备用方案）
5. **滚动加载**: 对于笔记列表，自动滚动页面以加载所有内容

## ⚠️ 注意事项

### 1. 性能考虑

- Selenium 比 `requests` 慢得多（启动浏览器需要时间）
- 建议使用**连接池**或**单例模式**复用浏览器实例
- 不要频繁创建和销毁 `XHS_Selenium_Apis` 实例

### 2. 资源管理

务必在使用完毕后调用 `close()` 方法关闭浏览器：

```python
api = XHS_Selenium_Apis()
try:
    # 使用 api
    pass
finally:
    api.close()  # 确保浏览器被关闭
```

或者使用上下文管理器（推荐）：

```python
# TODO: 可以在类中实现 __enter__ 和 __exit__ 方法
```

### 3. Cookie 获取

您需要从浏览器中手动获取 Cookies：

1. 打开 Chrome 浏览器
2. 登录小红书网站
3. 按 F12 打开开发者工具
4. 切换到 "Application" 标签
5. 左侧选择 "Cookies" -> "https://www.xiaohongshu.com"
6. 复制所有 Cookie 拼接成字符串格式：`key1=value1; key2=value2; ...`

### 4. 反爬虫对抗

虽然 Selenium 能绕过大部分反爬虫，但仍需注意：

- **不要频繁请求**: 建议每个请求间隔 2-5 秒
- **使用代理IP**: 如果需要大量爬取，建议配置代理池
- **更新 Cookies**: Cookies 会过期，需要定期更新

### 5. 无头模式问题

如果在服务器上运行（无图形界面），确保：

```bash
# Ubuntu/Debian
sudo apt-get install -y chromium-browser xvfb

# 或者使用 Docker 镜像
# selenium/standalone-chrome
```

## 🐛 常见问题

### Q1: 报错 "chromedriver executable needs to be in PATH"

**A:** 使用 `webdriver-manager` 会自动解决，或者手动安装：

```bash
pip install webdriver-manager
```

### Q2: 无头模式下报错

**A:** 尝试添加更多 Chrome 参数：

```python
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--start-maximized')
```

### Q3: 获取不到数据 / 返回空

**A:** 可能原因：
1. 页面加载太慢，增加 `wait_timeout`
2. Cookies 过期，需要重新获取
3. 元素选择器变化，小红书更新了页面结构

### Q4: 占用内存过高

**A:** 每次使用后记得关闭浏览器：

```python
api.close()
```

## 📊 性能对比

| 方法 | 速度 | 稳定性 | 反爬虫能力 | 资源占用 |
|------|------|--------|-----------|---------|
| requests (原方法) | ⭐⭐⭐⭐⭐ | ❌ 已失效 | ❌ 被检测 | ⭐ 低 |
| Selenium (新方法) | ⭐⭐ 慢 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ 中等 |

## 🔄 迁移指南

### 从 `xhs_pc_apis` 迁移到 `xhs_selenium_apis`

您的 `service.py` **无需任何修改**，只需更改导入：

```python
# 修改前
from app.apis.xhs_pc_apis import XHS_Apis

# 修改后
from app.apis.xhs_selenium_apis import XHS_Selenium_Apis as XHS_Apis
```

返回的数据格式完全一致，所有业务逻辑保持不变。

## 📚 更多资源

- [Selenium 官方文档](https://www.selenium.dev/documentation/)
- [Selenium Python 文档](https://selenium-python.readthedocs.io/)
- [WebDriver Manager](https://github.com/SergeyPirogov/webdriver_manager)

## 🆘 需要帮助？

如果遇到问题，请检查：

1. Chrome 浏览器是否已安装
2. Python 依赖是否完整安装
3. Cookies 是否有效且格式正确
4. 网络连接是否正常

---

**提示**: 建议在开发环境中先以 `headless=False` 模式运行，观察浏览器行为，确认无误后再切换到 `headless=True` 用于生产环境。
