#!/usr/bin/env python3
"""
检查Railway部署日志和调用来源
添加详细的日志追踪系统
"""

# 添加到 llm_gateway.py 的日志增强
ENHANCED_LOGGING = """
# 在 LLMGateway.chat() 方法开头添加：

import traceback
import uuid

async def chat(self, prompt: str, model: str = "deepseek-chat", ...):
    call_id = str(uuid.uuid4())[:8]
    caller_info = ''.join(traceback.format_stack()[-3:-1])  # 获取调用栈
    
    print(f"[LLM #{call_id}] 📞 调用来源:")
    print(caller_info)
    print(f"[LLM #{call_id}] 📝 Model: {model}")
    print(f"[LLM #{call_id}] 📝 Prompt长度: {len(prompt)} 字符")
    print(f"[LLM #{call_id}] 🕐 时间: {datetime.now()}")
    
    # ... 原有代码 ...
"""

print("=" * 60)
print("🔍 可能的异常调用原因分析")
print("=" * 60)

reasons = [
    {
        "原因": "1. 网站被他人访问",
        "说明": "Vercel部署的网站是公开的，任何人都能访问",
        "可能性": "⭐⭐⭐⭐⭐ 最可能",
        "检查方法": [
            "查看Railway日志：railway logs",
            "查看访问IP地址",
            "添加Google Analytics追踪访问量"
        ],
        "解决方案": [
            "添加密码保护",
            "添加访问频率限制（rate limiting）",
            "只在开发环境使用，生产环境加认证"
        ]
    },
    {
        "原因": "2. 开发测试调用",
        "说明": "你或队友在测试时产生的调用",
        "可能性": "⭐⭐⭐⭐ 很可能",
        "检查方法": [
            "回忆是否多次刷新页面测试",
            "是否有多人在测试",
            "检查浏览器开发者工具Network标签"
        ],
        "解决方案": [
            "使用本地开发环境测试",
            "测试时用mock数据"
        ]
    },
    {
        "原因": "3. 前端重复渲染/调用",
        "说明": "React组件重复渲染导致多次API调用",
        "可能性": "⭐⭐⭐ 可能",
        "检查方法": [
            "查看浏览器Console是否有重复日志",
            "检查useEffect依赖数组是否正确"
        ],
        "解决方案": [
            "添加防抖（debounce）",
            "使用loading状态防止重复提交"
        ]
    },
    {
        "原因": "4. 爬虫/机器人访问",
        "说明": "搜索引擎爬虫或恶意机器人",
        "可能性": "⭐⭐ 较小",
        "检查方法": [
            "查看Railway日志的User-Agent",
            "查看访问模式是否规律"
        ],
        "解决方案": [
            "添加robots.txt",
            "添加CAPTCHA验证",
            "添加rate limiting"
        ]
    },
    {
        "原因": "5. 缓存未生效",
        "说明": "每次请求都调用API而不是用缓存",
        "可能性": "⭐⭐⭐ 可能",
        "检查方法": [
            "查看日志是否有'缓存命中'消息",
            "检查MongoDB缓存集合是否有数据"
        ],
        "解决方案": [
            "验证缓存key生成逻辑",
            "检查MongoDB连接"
        ]
    },
    {
        "原因": "6. 错误重试机制",
        "说明": "API失败后自动重试多次",
        "可能性": "⭐⭐ 较小",
        "检查方法": [
            "查看是否有大量error日志",
            "检查OpenAI client的retry配置"
        ],
        "解决方案": [
            "限制重试次数",
            "添加exponential backoff"
        ]
    }
]

for r in reasons:
    print(f"\n{r['原因']}")
    print(f"说明: {r['说明']}")
    print(f"可能性: {r['可能性']}")
    print(f"检查方法:")
    for method in r['检查方法']:
        print(f"  • {method}")
    print(f"解决方案:")
    for solution in r['解决方案']:
        print(f"  • {solution}")

print("\n" + "=" * 60)
print("🔧 立即行动步骤")
print("=" * 60)

actions = [
    "1. 查看Railway日志（最重要！）",
    "   railway logs --tail 100",
    "   查看每次调用的时间戳、来源IP",
    "",
    "2. 检查MongoDB缓存",
    "   连接MongoDB查看缓存集合是否有数据",
    "   db.llm_cache.countDocuments()",
    "",
    "3. 添加详细日志",
    "   在LLMGateway.chat()开头添加调用追踪",
    "   记录每次调用的来源、时间、参数",
    "",
    "4. 添加访问保护",
    "   添加简单的API密钥验证",
    "   限制每IP每小时最多N次调用",
    "",
    "5. 监控实时调用",
    "   运行 railway logs --follow",
    "   打开网站，观察是否有异常调用"
]

for action in actions:
    print(action)

print("\n" + "=" * 60)
print("💡 推荐：添加调用日志追踪")
print("=" * 60)
print(ENHANCED_LOGGING)
