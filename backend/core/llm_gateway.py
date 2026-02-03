"""
LLM Gateway - 统一的LLM调用网关
实现缓存、压缩、限流等优化
"""

import hashlib
import json
import re
import asyncio
import uuid
import traceback
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from openai import OpenAI

from core.config import settings
from database.connection import get_database


class LLMGateway:
    """LLM网关 - 缓存 + 压缩 + 限流"""
    
    def __init__(self):
        try:
            # 简化初始化，避免版本兼容问题
            self.client = OpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL,
                timeout=30.0  # 添加超时设置
            )
            self.rate_limiter = TokenBucketRateLimiter(
                capacity=100,   # 桶容量
                refill_rate=10  # 每秒补充10个token
            )
            self.db = get_database()
            print("✅ LLM Gateway 初始化完成（缓存 + 限流已启用）")
        except Exception as e:
            print(f"⚠️  LLM Gateway 初始化警告: {e}")
            # 即使初始化失败也创建客户端（用于非AI功能）
            self.client = None
            self.rate_limiter = None
            self.db = get_database()
    
    async def chat(
        self,
        prompt: str,
        model: str = "deepseek-chat",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        use_cache: bool = True
    ) -> str:
        """
        统一的聊天接口
        
        Args:
            prompt: 提示词
            model: 模型名称
            max_tokens: 最大token数
            temperature: 温度参数
            use_cache: 是否启用缓存
            
        Returns:
            生成的文本
        """
        
        # 🔍 调用追踪（诊断异常调用）
        call_id = str(uuid.uuid4())[:8]
        print(f"\n{'='*60}")
        print(f"[LLM #{call_id}] 📞 新的API调用请求")
        print(f"[LLM #{call_id}] 🕐 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[LLM #{call_id}] 🤖 Model: {model}")
        print(f"[LLM #{call_id}] 📝 Prompt长度: {len(prompt)} 字符 (压缩前)")
        print(f"[LLM #{call_id}] ⚙️  Max Tokens: {max_tokens}")
        print(f"[LLM #{call_id}] 🔥 Temperature: {temperature}")
        print(f"[LLM #{call_id}] 💾 Cache: {'启用' if use_cache else '禁用'}")
        
        # 获取调用栈（诊断来源）
        stack = traceback.extract_stack()
        caller_info = None
        for frame in reversed(stack[:-1]):  # 跳过当前函数
            if 'llm_gateway' not in frame.filename:
                caller_info = f"{frame.filename}:{frame.lineno} in {frame.name}"
                break
        if caller_info:
            print(f"[LLM #{call_id}] 📍 调用来源: {caller_info}")
        print(f"{'='*60}\n")
        
        # 1️⃣ Prompt压缩
        compressed_prompt = self._compress_prompt(prompt)
        print(f"[LLM #{call_id}] 🗜️  压缩后长度: {len(compressed_prompt)} 字符 (节省 {len(prompt) - len(compressed_prompt)} 字符)")
        
        # 2️⃣ 生成缓存键
        cache_key = self._generate_cache_key(compressed_prompt, model, temperature)
        
        # 3️⃣ 检查缓存（MongoDB）
        if use_cache:
            cached_response = await self._get_from_cache(cache_key)
            if cached_response:
                print(f"[LLM #{call_id}] 💰 ✅ 缓存命中！节省了API调用")
                print(f"[LLM #{call_id}] 🎯 返回缓存内容长度: {len(cached_response)} 字符\n")
                return cached_response
            else:
                print(f"[LLM #{call_id}] 💰 ❌ 缓存未命中，需要调用API")
        
        # 4️⃣ 频率限制
        print(f"[LLM #{call_id}] ⏱️  等待限流器放行...")
        await self.rate_limiter.acquire()
        print(f"[LLM #{call_id}] ✅ 限流器已放行")
        
        # 5️⃣ 调用API
        try:
            print(f"[LLM #{call_id}] 🚀 正在调用DeepSeek API...")
            api_start_time = datetime.now()
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": compressed_prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            api_duration = (datetime.now() - api_start_time).total_seconds()
            result = response.choices[0].message.content
            
            # 打印详细的API使用统计
            usage = response.usage
            print(f"[LLM #{call_id}] ✅ API调用成功！")
            print(f"[LLM #{call_id}] ⏱️  耗时: {api_duration:.2f}秒")
            print(f"[LLM #{call_id}] 📊 Token统计:")
            print(f"[LLM #{call_id}]    - 输入: {usage.prompt_tokens:,} tokens")
            print(f"[LLM #{call_id}]    - 输出: {usage.completion_tokens:,} tokens")
            print(f"[LLM #{call_id}]    - 总计: {usage.total_tokens:,} tokens")
            print(f"[LLM #{call_id}] 💵 估算成本 (DeepSeek):")
            input_cost = usage.prompt_tokens * 0.27 / 1_000_000
            output_cost = usage.completion_tokens * 1.1 / 1_000_000
            print(f"[LLM #{call_id}]    - 输入: ${input_cost:.6f}")
            print(f"[LLM #{call_id}]    - 输出: ${output_cost:.6f}")
            print(f"[LLM #{call_id}]    - 本次总计: ${input_cost + output_cost:.6f}")
            print(f"[LLM #{call_id}] 📝 返回内容长度: {len(result)} 字符\n")
            
            # 6️⃣ 写入缓存（TTL=24小时）
            if use_cache:
                await self._save_to_cache(cache_key, result)
                print(f"[LLM #{call_id}] 💾 已保存到缓存")
            
            # 7️⃣ 记录统计
            await self._log_usage(model, response.usage, compressed_prompt, result, call_id)
            
            return result
            
        except Exception as e:
            print(f"[LLM #{call_id}] ❌ API调用失败: {e}")
            raise
    
    def _compress_prompt(self, prompt: str) -> str:
        """Prompt压缩优化"""
        # 1. 去除多余空白
        compressed = ' '.join(prompt.split())
        
        # 2. 移除HTML标签（如果存在）
        compressed = re.sub(r'<[^>]+>', '', compressed)
        
        # 3. 截断过长内容（保留重要部分）
        if len(compressed) > 8000:
            # 保留开头2000字符 + 结尾2000字符
            compressed = compressed[:2000] + "\n...(中间省略)...\n" + compressed[-2000:]
        
        return compressed
    
    def _generate_cache_key(self, prompt: str, model: str, temperature: float) -> str:
        """生成缓存键（基于内容哈希）"""
        content = f"{model}:{temperature}:{prompt}"
        return f"llm_cache:{hashlib.sha256(content.encode()).hexdigest()}"
    
    async def _get_from_cache(self, cache_key: str) -> Optional[str]:
        """从MongoDB缓存读取"""
        cache_doc = self.db.llm_cache.find_one({"key": cache_key})
        if cache_doc:
            # 检查是否过期（24小时）
            if datetime.now() - cache_doc['created_at'] < timedelta(hours=24):
                return cache_doc['response']
        return None
    
    async def _save_to_cache(self, cache_key: str, response: str):
        """保存到MongoDB缓存"""
        self.db.llm_cache.update_one(
            {"key": cache_key},
            {
                "$set": {
                    "response": response,
                    "created_at": datetime.now()
                }
            },
            upsert=True
        )
    
    async def _log_usage(self, model: str, usage: Any, prompt: str, response: str, call_id: str = "unknown"):
        """记录使用统计（增强版 - 包含调用追踪）"""
        
        # 获取调用栈信息
        stack = traceback.extract_stack()
        caller_file = "unknown"
        caller_line = 0
        caller_function = "unknown"
        
        for frame in reversed(stack[:-2]):  # 跳过当前和chat函数
            if 'llm_gateway' not in frame.filename:
                caller_file = frame.filename.split('/')[-1]  # 只保留文件名
                caller_line = frame.lineno
                caller_function = frame.name
                break
        
        log_data = {
            "call_id": call_id,
            "model": model,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
            "prompt_length": len(prompt),
            "response_length": len(response),
            "timestamp": datetime.now(),
            "caller_file": caller_file,
            "caller_line": caller_line,
            "caller_function": caller_function
        }
        
        self.db.llm_usage_logs.insert_one(log_data)
        # 已在上面打印详细信息，这里不重复打印


class TokenBucketRateLimiter:
    """令牌桶限流器"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = datetime.now()
        self._lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1):
        """获取令牌（阻塞直到有可用令牌）"""
        async with self._lock:
            while True:
                self._refill()
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return
                await asyncio.sleep(0.1)
    
    def _refill(self):
        """补充令牌"""
        now = datetime.now()
        elapsed = (now - self.last_refill).total_seconds()
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now


# 全局LLM Gateway实例（懒加载）
_llm_gateway = None

def get_llm_gateway() -> LLMGateway:
    """获取LLM Gateway单例"""
    global _llm_gateway
    if _llm_gateway is None:
        _llm_gateway = LLMGateway()
    return _llm_gateway
