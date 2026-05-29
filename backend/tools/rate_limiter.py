"""API请求限流中间件 — 令牌桶算法,基于IP+路径"""
import time
from collections import defaultdict
from fastapi import Request
from fastapi.responses import JSONResponse

# 限流配置: {路径前缀: (令牌数, 时间窗口秒)}
RATE_LIMITS = {
    "/agent/scraper": (10, 60),      # 采集: 10次/分钟
    "/agent/archive": (5, 60),       # 归档: 5次/分钟
    "/heal/auto-fix": (3, 300),      # 自愈: 3次/5分钟
    "/report": (10, 60),             # 报告: 10次/分钟
    "/agent/logs": (20, 60),         # 日志: 20次/分钟
    "/agent/competitor": (30, 60),   # 竞品: 30次/分钟
    "default": (600, 60),            # 默认: 600次/分钟
}

# 令牌桶存储: {ip: {path: [tokens, last_refill_time]}}
# 初始化为满令牌，避免新路径首次请求被误限
_buckets = defaultdict(lambda: defaultdict(lambda: [600, time.time()]))

def _get_limit(path: str):
    """根据路径获取限流配置"""
    for prefix, limit in RATE_LIMITS.items():
        if prefix != "default" and path.startswith(prefix):
            return limit
    return RATE_LIMITS["default"]

async def rate_limit_middleware(request: Request, call_next):
    """FastAPI限流中间件"""
    # 跳过健康检查和静态资源
    if request.url.path in ("/health", "/", "/docs", "/openapi.json", "/agent/health", "/agent/health/simple"):
        return await call_next(request)

    # 读取真实客户端IP (Nginx反向代理后)
    client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    if not client_ip:
        client_ip = request.headers.get("X-Real-IP", "")
    if not client_ip:
        client_ip = request.client.host if request.client else "unknown"
    path = request.url.path
    
    max_tokens, window = _get_limit(path)
    now = time.time()
    
    bucket = _buckets[client_ip][path]
    tokens, last_refill = bucket
    
    # 令牌桶: 按时间补充
    elapsed = now - last_refill
    refill_amount = elapsed * (max_tokens / window)
    tokens = min(max_tokens, tokens + refill_amount)
    
    if tokens < 1:
        return JSONResponse(
            status_code=429,
            content={"detail": f"请求太频繁,请{int(window)}秒后重试 (限流: {max_tokens}次/{window}秒)"}
        )
    
    tokens -= 1
    _buckets[client_ip][path] = [tokens, now]
    
    response = await call_next(request)
    return response

# 定时清理过期桶(每10分钟)
_last_cleanup = time.time()

def _cleanup_buckets():
    global _last_cleanup
    now = time.time()
    if now - _last_cleanup < 600:  # 10分钟
        return
    _last_cleanup = now
    for ip in list(_buckets.keys()):
        for path in list(_buckets[ip].keys()):
            _, last_refill = _buckets[ip][path]
            if now - last_refill > 3600:  # 1小时未使用则清理
                del _buckets[ip][path]
        if not _buckets[ip]:
            del _buckets[ip]
