锘?""API璇锋眰闄愭祦涓棿浠?鈥?浠ょ墝妗剁畻娉?鍩轰簬IP+璺緞"""
import time
from collections import defaultdict
from fastapi import Request, HTTPException

# 闄愭祦閰嶇疆: {璺緞鍓嶇紑: (浠ょ墝鏁? 鏃堕棿绐楀彛绉?}
RATE_LIMITS = {
    "/agent/scraper": (10, 60),      # 閲囬泦: 10娆?鍒嗛挓
    "/agent/archive": (5, 60),       # 褰掓。: 5娆?鍒嗛挓
    "/heal/auto-fix": (3, 300),      # 鑷剤: 3娆?5鍒嗛挓
    "/report": (10, 60),             # 鎶ュ憡: 10娆?鍒嗛挓
    "/agent/logs": (20, 60),         # 鏃ュ織: 20娆?鍒嗛挓
    "/agent/competitor": (30, 60),   # 绔炲搧: 30娆?鍒嗛挓
    "default": (100, 60),            # 榛樿: 100娆?鍒嗛挓
}

# 浠ょ墝妗跺瓨鍌? {ip: {path: (tokens, last_refill_time)}}
_buckets = defaultdict(lambda: defaultdict(lambda: [0, time.time()]))

def _get_limit(path: str):
    """鏍规嵁璺緞鑾峰彇闄愭祦閰嶇疆"""
    for prefix, limit in RATE_LIMITS.items():
        if prefix != "default" and path.startswith(prefix):
            return limit
    return RATE_LIMITS["default"]

async def rate_limit_middleware(request: Request, call_next):
    """FastAPI闄愭祦涓棿浠?""
    # 璺宠繃鍋ュ悍妫€鏌?
    if request.url.path in ("/health", "/", "/docs", "/openapi.json"):
        return await call_next(request)
    
    client_ip = request.client.host if request.client else "unknown"
    path = request.url.path
    
    max_tokens, window = _get_limit(path)
    now = time.time()
    
    bucket = _buckets[client_ip][path]
    tokens, last_refill = bucket
    
    # 浠ょ墝妗? 鎸夋椂闂磋ˉ鍏?
    elapsed = now - last_refill
    refill_amount = elapsed * (max_tokens / window)
    tokens = min(max_tokens, tokens + refill_amount)
    
    if tokens < 1:
        raise HTTPException(
            status_code=429,
            detail=f"璇锋眰澶绻?璇穥int(window)}绉掑悗閲嶈瘯 (闄愭祦: {max_tokens}娆?{window}绉?"
        )
    
    tokens -= 1
    _buckets[client_ip][path] = [tokens, now]
    
    response = await call_next(request)
    return response

# 瀹氭椂娓呯悊杩囨湡妗?姣?0鍒嗛挓)
_last_cleanup = time.time()

def _cleanup_buckets():
    global _last_cleanup
    now = time.time()
    if now - _last_cleanup < 600:  # 10鍒嗛挓
        return
    _last_cleanup = now
    for ip in list(_buckets.keys()):
        for path in list(_buckets[ip].keys()):
            _, last_refill = _buckets[ip][path]
            if now - last_refill > 3600:  # 1灏忔椂鏈娇鐢ㄥ垯娓呯悊
                del _buckets[ip][path]
        if not _buckets[ip]:
            del _buckets[ip]
