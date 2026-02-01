"""
LLM Gateway - 统一的LLM调用网关
实现缓存、压缩、限流等优化
"""

import hashlib
import json
import re
import asyncio
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
        
        # 1️⃣ Prompt压缩
        compressed_prompt = self._compress_prompt(prompt)
        
        # 2️⃣ 生成缓存键
        cache_key = self._generate_cache_key(compressed_prompt, model, temperature)
        
        # 3️⃣ 检查缓存（MongoDB）
        if use_cache:
            cached_response = await self._get_from_cache(cache_key)
            if cached_response:
                print(f"[LLM Gateway] 💰 缓存命中: {cache_key[:16]}... (节省API调用)")
                return cached_response
        
        # 4️⃣ 频率限制
        await self.rate_limiter.acquire()
        
        # 5️⃣ 调用API
        try:
            print(f"[LLM Gateway] 🚀 调用API: {model} (tokens≤{max_tokens})")
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": compressed_prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            result = response.choices[0].message.content
            
            # 6️⃣ 写入缓存（TTL=24小时）
            if use_cache:
                await self._save_to_cache(cache_key, result)
            
            # 7️⃣ 记录统计
            await self._log_usage(model, response.usage, compressed_prompt, result)
            
            return result
            
        except Exception as e:
            print(f"[LLM Gateway] ❌ API调用失败: {e}")
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
    
    async def _log_usage(self, model: str, usage: Any, prompt: str, response: str):
        """记录使用统计"""
        log_data = {
            "model": model,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
            "prompt_length": len(prompt),
            "response_length": len(response),
            "timestamp": datetime.now()
        }
        
        self.db.llm_usage_logs.insert_one(log_data)
        print(f"[LLM Gateway] 📊 Token消耗: {usage.total_tokens} (提示:{usage.prompt_tokens} + 完成:{usage.completion_tokens})")


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
