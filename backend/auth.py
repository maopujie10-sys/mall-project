"""认证模块 — JWT Token + 简单Token 双模式
v2: 支持 JWT 过期验证 + 速率限制 + 审计日志"""
import time
import hashlib
import hmac
import os
import json
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from config import AGENT_TOKEN

# ===== JWT 配置 =====
JWT_SECRET = os.getenv("JWT_SECRET", AGENT_TOKEN or "friday-ai-os-secret")
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

# ===== 速率限制 =====
_rate_limits: dict[str, list] = {}  # {token: [timestamps]}
RATE_LIMIT_MAX = int(os.getenv("RATE_LIMIT_MAX", "60"))  # 每分钟最多请求
RATE_LIMIT_WINDOW = 60  # 秒

# ===== 审计日志 =====
_audit_log: list = []
AUDIT_MAX = 1000

def _base64url_encode(data: bytes) -> str:
    import base64
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def _base64url_decode(data: str) -> bytes:
    import base64
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data)

def create_jwt(payload: dict, expire_hours: int = None) -> str:
    """创建 JWT Token"""
    expire_hours = expire_hours or JWT_EXPIRE_HOURS
    header = {"alg": "HS256", "typ": "JWT"}
    payload["exp"] = int((datetime.utcnow() + timedelta(hours=expire_hours)).timestamp())
    payload["iat"] = int(datetime.utcnow().timestamp())

    header_b64 = _base64url_encode(json.dumps(header).encode())
    payload_b64 = _base64url_encode(json.dumps(payload).encode())
    signing_input = f"{header_b64}.{payload_b64}"
    signature = hmac.new(JWT_SECRET.encode(), signing_input.encode(), hashlib.sha256).digest()
    signature_b64 = _base64url_encode(signature)

    return f"{signing_input}.{signature_b64}"

def verify_jwt(token: str) -> dict | None:
    """验证 JWT Token，返回 payload 或 None"""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, signature_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}"
        expected_sig = hmac.new(JWT_SECRET.encode(), signing_input.encode(), hashlib.sha256).digest()
        actual_sig = _base64url_decode(signature_b64)

        if not hmac.compare_digest(expected_sig, actual_sig):
            return None

        payload = json.loads(_base64url_decode(payload_b64))
        if payload.get("exp", 0) < datetime.utcnow().timestamp():
            return None  # 过期

        return payload
    except Exception:
        return None

def check_rate_limit(token: str) -> bool:
    """检查速率限制，返回是否允许"""
    now = time.time()
    if token not in _rate_limits:
        _rate_limits[token] = []
    # 清理过期记录
    _rate_limits[token] = [t for t in _rate_limits[token] if now - t < RATE_LIMIT_WINDOW]
    if len(_rate_limits[token]) >= RATE_LIMIT_MAX:
        return False
    _rate_limits[token].append(now)
    return True

def audit_log(method: str, path: str, token: str, status: int, ip: str = ""):
    """记录审计日志"""
    entry = {
        "time": datetime.now().isoformat(),
        "method": method,
        "path": path,
        "token_prefix": token[:8] + "..." if len(token) > 8 else token,
        "status": status,
        "ip": ip,
    }
    _audit_log.append(entry)
    if len(_audit_log) > AUDIT_MAX:
        _audit_log.pop(0)

def get_audit_logs(limit: int = 100) -> list:
    """获取最近审计日志"""
    return _audit_log[-limit:]

def get_rate_limit_stats() -> dict:
    """速率限制统计"""
    now = time.time()
    active = 0
    blocked = 0
    for token, timestamps in _rate_limits.items():
        recent = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
        if len(recent) >= RATE_LIMIT_MAX:
            blocked += 1
        elif recent:
            active += 1
    return {"active_clients": active, "blocked_clients": blocked, "max_per_minute": RATE_LIMIT_MAX}

async def verify_token(request: Request):
    """Token 验证中间件 — 支持 JWT + 简单 Token"""
    token = request.headers.get("X-Agent-Token", "")
    client_ip = request.client.host if request.client else ""

    # 速率限制
    rate_key = token or client_ip
    if not check_rate_limit(rate_key):
        audit_log(request.method, request.url.path, token, 429, client_ip)
        raise HTTPException(status_code=429, detail="请求过于频繁，请稍后重试")

    # JWT 验证
    if token.startswith("eyJ"):
        payload = verify_jwt(token)
        if payload:
            audit_log(request.method, request.url.path, token, 200, client_ip)
            return payload
        audit_log(request.method, request.url.path, token, 403, client_ip)
        raise HTTPException(status_code=403, detail="JWT 无效或已过期")

    # 简单 Token 验证
    if token == AGENT_TOKEN:
        audit_log(request.method, request.url.path, token, 200, client_ip)
        return {"authenticated": True}

    audit_log(request.method, request.url.path, token, 403, client_ip)
    raise HTTPException(status_code=403, detail="无效的 Agent Token")