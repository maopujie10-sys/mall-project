"""API -- ,IP+"""
import time
from collections import defaultdict
from fastapi import Request
from fastapi.responses import JSONResponse

# : {: (, )}
RATE_LIMITS = {
    "/agent/scraper": (10, 60),      # : 10/
    "/agent/archive": (5, 60),       # : 5/
    "/heal/auto-fix": (3, 300),      # : 3/5
    "/report": (10, 60),             # : 10/
    "/agent/logs": (20, 60),         # : 20/
    "/agent/competitor": (30, 60),   # : 30/
    "default": (600, 60),            # : 600/
}

# : {ip: {path: [tokens, last_refill_time]}}
# ,
_buckets = defaultdict(lambda: defaultdict(lambda: [600, time.time()]))

def _get_limit(path: str):
    ''''''
    for prefix, limit in RATE_LIMITS.items():
        if prefix != "default" and path.startswith(prefix):
            return limit
    return RATE_LIMITS["default"]

async def rate_limit_middleware(request: Request, call_next):
    ''"FastAPI''"
    
    if request.url.path in ("/health", "/", "/docs", "/openapi.json", "/agent/health", "/agent/health/simple"):
        return await call_next(request)

    # IP (Nginx)
    client_ip = request.headers.get("X-Forwarded-For", '').split(",")[0].strip()
    if not client_ip:
        client_ip = request.headers.get("X-Real-IP", '')
    if not client_ip:
        client_ip = request.client.host if request.client else "unknown"
    path = request.url.path
    
    max_tokens, window = _get_limit(path)
    now = time.time()
    
    bucket = _buckets[client_ip][path]
    tokens, last_refill = bucket
    
    # : 
    elapsed = now - last_refill
    refill_amount = elapsed * (max_tokens / window)
    tokens = min(max_tokens, tokens + refill_amount)
    
    if tokens < 1:
        return JSONResponse(
            status_code=429,
            content={"detail": f",{int(window)} (: {max_tokens}/{window})"}
        )
    
    tokens -= 1
    _buckets[client_ip][path] = [tokens, now]
    
    response = await call_next(request)
    return response

# (10)
_last_cleanup = time.time()

def _cleanup_buckets():
    global _last_cleanup
    now = time.time()
    if now - _last_cleanup < 600:  # 10
        return
    _last_cleanup = now
    for ip in list(_buckets.keys()):
        for path in list(_buckets[ip].keys()):
            _, last_refill = _buckets[ip][path]
            if now - last_refill > 3600:  # 1
                del _buckets[ip][path]
        if not _buckets[ip]:
            del _buckets[ip]
