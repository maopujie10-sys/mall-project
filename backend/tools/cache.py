锘?""Redis缂撳瓨灞?鈥?瑁呴グ鍣ㄦā寮?鑷姩搴忓垪鍖?TTL鏀寔"""
import json
import functools
import asyncio
import os
import hashlib
from typing import Optional

# 灏濊瘯杩炴帴Redis,涓嶅彲鐢ㄦ椂鍥為€€鍐呭瓨缂撳瓨
try:
    import redis.asyncio as aioredis
    _redis = aioredis.from_url(
        os.getenv("REDIS_DSN", "redis://localhost:6379/0"),
        decode_responses=True,
    )
    _redis_available = True
except Exception:
    _redis = None
    _redis_available = False

# 鍐呭瓨缂撳瓨(Redis涓嶅彲鐢ㄦ椂鍥為€€)
_memory_cache = {}

def _make_key(prefix: str, args, kwargs) -> str:
    """鐢熸垚缂撳瓨key"""
    raw = f"{prefix}:{json.dumps(args, sort_keys=True, default=str)}:{json.dumps(kwargs, sort_keys=True, default=str)}"
    return f"cache:{prefix}:{hashlib.md5(raw.encode()).hexdigest()[:16]}"

async def cache_get(key: str) -> Optional[str]:
    """璇诲彇缂撳瓨"""
    if _redis_available:
        try:
            return await _redis.get(key)
        except Exception:
            pass
    item = _memory_cache.get(key)
    if item and item["expire"] > asyncio.get_event_loop().time():
        return item["value"]
    return None

async def cache_set(key: str, value: str, ttl: int = 300):
    """鍐欏叆缂撳瓨"""
    if _redis_available:
        try:
            await _redis.set(key, value, ex=ttl)
            return
        except Exception:
            pass
    _memory_cache[key] = {
        "value": value,
        "expire": asyncio.get_event_loop().time() + ttl,
    }

async def cache_delete(prefix: str):
    """鎸夊墠缂€娓呴櫎缂撳瓨"""
    if _redis_available:
        try:
            keys = await _redis.keys(f"cache:{prefix}:*")
            if keys:
                await _redis.delete(*keys)
        except Exception:
            pass
    for key in list(_memory_cache.keys()):
        if key.startswith(f"cache:{prefix}:"):
            del _memory_cache[key]

def cached(prefix: str, ttl: int = 300):
    """缂撳瓨瑁呴グ鍣?""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = _make_key(prefix, args, kwargs)
            cached_val = await cache_get(key)
            if cached_val is not None:
                return json.loads(cached_val)
            result = await func(*args, **kwargs)
            await cache_set(key, json.dumps(result, default=str), ttl)
            return result
        return wrapper
    return decorator

# 瀹氭椂娓呯悊杩囨湡鍐呭瓨缂撳瓨
_last_cleanup = 0

async def cleanup_memory_cache():
    global _last_cleanup
    now = asyncio.get_event_loop().time()
    if now - _last_cleanup < 300:
        return
    _last_cleanup = now
    expired = [k for k, v in _memory_cache.items() if v["expire"] < now]
    for k in expired:
        del _memory_cache[k]
