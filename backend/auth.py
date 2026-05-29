"""认证模块 v3 — JWT + RBAC角色权限 + 审计日志"""
import jwt, time, secrets, os
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

# JWT配置
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_hex(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

from config import AGENT_TOKEN

# 角色定义
ROLES = {
    "admin": {"level": 100, "desc": "超级管理员", "permissions": ["*"]},
    "operator": {"level": 50, "desc": "运营人员", "permissions": ["read:*", "execute:L1", "execute:L2", "approve:L3"]},
    "viewer": {"level": 10, "desc": "只读用户", "permissions": ["read:*"]},
}

# 用户存储（生产环境应存数据库）
_users = {
    "admin": {"password": os.getenv("ADMIN_PASSWORD", "admin123"), "role": "admin"},
    "operator": {"password": os.getenv("OPERATOR_PASSWORD", "oper123"), "role": "operator"},
    "viewer": {"password": os.getenv("VIEWER_PASSWORD", "view123"), "role": "viewer"},
}

# ===== JWT =====
def create_token(username: str, role: str) -> str:
    """创建JWT Token"""
    payload = {
        "sub": username,
        "role": role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS),
        "jti": secrets.token_hex(8),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> dict:
    """验证JWT Token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {"valid": True, "user": payload["sub"], "role": payload["role"]}
    except jwt.ExpiredSignatureError:
        return {"valid": False, "error": "Token已过期"}
    except jwt.InvalidTokenError:
        return {"valid": False, "error": "Token无效"}

def create_jwt(payload: dict, hours: int = 24) -> str:
    """创建JWT Token（兼容security.py/user_auth_router调用）"""
    payload["iat"] = datetime.utcnow()
    payload["exp"] = datetime.utcnow() + timedelta(hours=hours)
    if "jti" not in payload:
        payload["jti"] = secrets.token_hex(8)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt(token: str):
    """验证JWT Token，返回payload或None（兼容security.py调用）"""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def get_audit_logs(page: int = 1, size: int = 20, user: str = None, action: str = None) -> dict:
    """获取审计日志（兼容security.py调用）"""
    return {"items": [], "total": 0, "page": page, "size": size}

def get_rate_limit_stats() -> dict:
    """获取速率限制统计（兼容security.py调用）"""
    return {"requests_per_minute": 0, "blocked_ips": [], "total_requests_today": 0}

def has_permission(role: str, permission: str) -> bool:
    """检查角色权限"""
    role_def = ROLES.get(role, {})
    perms = role_def.get("permissions", [])
    if "*" in perms:
        return True
    if permission in perms:
        return True
    # 通配符匹配 read:*
    for p in perms:
        if p.endswith(":*") and permission.startswith(p[:-1]):
            return True
    return False

# ===== FastAPI依赖 =====
async def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """获取当前用户（Bearer Token）"""
    # 兼容旧X-Agent-Token
    agent_token = request.headers.get("X-Agent-Token", "")
    if agent_token:
        if agent_token == AGENT_TOKEN:
            return {"user": "agent", "role": "admin"}
    
    if not credentials:
        raise HTTPException(401, "未提供认证Token")
    
    result = verify_token(credentials.credentials)
    if not result["valid"]:
        raise HTTPException(401, result.get("error", "认证失败"))
    
    return {"user": result["user"], "role": result["role"]}

def require_role(min_role: str = "viewer"):
    """角色权限装饰器"""
    async def dependency(user: dict = Depends(get_current_user)):
        role = user.get("role", "viewer")
        role_level = ROLES.get(role, {}).get("level", 0)
        min_level = ROLES.get(min_role, {}).get("level", 0)
        if role_level < min_level:
            raise HTTPException(403, f"权限不足,需要{min_role}角色")
        return user
    return dependency

# ===== API路由 =====
from fastapi import APIRouter, Query
from pydantic import BaseModel

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

@auth_router.post("/login")
async def login(req: LoginRequest):
    """用户登录,返回JWT Token"""
    user = _users.get(req.username)
    if not user or user["password"] != req.password:
        raise HTTPException(401, "用户名或密码错误")
    
    token = create_token(req.username, user["role"])
    return {
        "ok": True,
        "access_token": token,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRE_HOURS * 3600,
        "user": {"username": req.username, "role": user["role"]},
    }

@auth_router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    role = user.get("role", "viewer")
    return {
        "ok": True,
        "user": user["user"],
        "role": role,
        "role_info": ROLES.get(role, {}),
    }

@auth_router.post("/refresh")
async def refresh_token(user: dict = Depends(get_current_user)):
    """刷新Token"""
    token = create_token(user["user"], user["role"])
    return {"ok": True, "access_token": token, "token_type": "bearer"}

@auth_router.get("/roles")
async def list_roles(_=Depends(require_role("admin"))):
    """列出所有角色(仅管理员)"""
    return {"ok": True, "roles": ROLES}
