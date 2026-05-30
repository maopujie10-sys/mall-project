"""认证模块 v3 -- JWT + RBAC角色权限 + 审计日志"""
import jwt, time, secrets, os, sqlite3, bcrypt
from pathlib import Path
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

# JWT配置
JWT_SECRET = os.getenv("JWT_SECRET", "")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET 环境变量未配置，拒绝启动。请设置: export JWT_SECRET=$(openssl rand -hex 32)")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

from config import AGENT_TOKEN

# 角色定义
ROLES = {
    "admin": {"level": 100, "desc": "超级管理员", "permissions": ["*"]},
    "operator": {"level": 50, "desc": "运营人员", "permissions": ["read:*", "execute:L1", "execute:L2", "approve:L3"]},
    "viewer": {"level": 10, "desc": "只读用户", "permissions": ["read:*"]},
}

# 用户存储 -- SQLite持久化
USER_DB = Path(__file__).parent / "data" / "users.db"

def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')

def _check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def _get_user_db():
    USER_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(USER_DB))
    conn.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password_hash TEXT, role TEXT DEFAULT 'viewer', created_at TEXT)")
    cursor = conn.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        conn.execute("INSERT INTO users VALUES ('admin', ?, 'admin', datetime('now'))", (_hash_password(os.getenv("ADMIN_PASSWORD", "admin123")),))
        conn.execute("INSERT INTO users VALUES ('operator', ?, 'operator', datetime('now'))", (_hash_password(os.getenv("OPERATOR_PASSWORD", "oper123")),))
        conn.execute("INSERT INTO users VALUES ('viewer', ?, 'viewer', datetime('now'))", (_hash_password(os.getenv("VIEWER_PASSWORD", "view123")),))
        conn.commit()
    return conn

def verify_user_password(username, password):
    conn = _get_user_db()
    row = conn.execute("SELECT username, password_hash, role FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    if row and _check_password(password, row[1]):
        return {"username": row[0], "role": row[2]}
    return None

def list_all_users():
    conn = _get_user_db()
    rows = conn.execute("SELECT username, role, created_at FROM users ORDER BY created_at").fetchall()
    conn.close()
    return [{"username": r[0], "role": r[1], "created_at": r[2]} for r in rows]

def add_user(username, password, role="viewer"):
    conn = _get_user_db()
    try:
        conn.execute("INSERT INTO users VALUES (?, ?, ?, datetime('now'))", (username, _hash_password(password), role))
        conn.commit(); conn.close(); return True
    except sqlite3.IntegrityError:
        conn.close(); return False

def delete_user(username):
    if username == 'admin': return False
    conn = _get_user_db()
    conn.execute('DELETE FROM users WHERE username=? AND username!=''admin''', (username,))
    conn.commit(); affected = conn.total_changes; conn.close()
    return affected > 0

def update_user_role(username, role):
    if role not in ROLES: return False
    conn = _get_user_db()
    conn.execute("UPDATE users SET role=? WHERE username=?", (role, username))
    conn.commit(); affected = conn.total_changes; conn.close()
    return affected > 0

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

def _decode_jwt(token: str) -> dict:
    """解码JWT Token(内部使用)"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {"valid": True, "user": payload["sub"], "role": payload["role"]}
    except jwt.ExpiredSignatureError:
        return {"valid": False, "error": "Token已过期"}
    except jwt.InvalidTokenError:
        return {"valid": False, "error": "Token无效"}

# ===== FastAPI依赖:verify_token(兼容旧路由 Depends(verify_token)) =====
async def verify_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """验证请求Token -- 同时支持X-Agent-Token(JWT或AgentToken)和Bearer Token"""
    agent_token = request.headers.get("X-Agent-Token", "")
    if agent_token:
        # 匹配AGENT_TOKEN -> admin权限
        if agent_token == AGENT_TOKEN:
            return {"user": "agent", "role": "admin"}
        # 尝试作为JWT解码(登录后的token)
        result = _decode_jwt(agent_token)
        if result["valid"]:
            return {"user": result["user"], "role": result["role"]}
    if not credentials:
        raise HTTPException(401, "未提供认证Token")
    result = _decode_jwt(credentials.credentials)
    if not result["valid"]:
        raise HTTPException(401, result.get("error", "认证失败"))
    return {"user": result["user"], "role": result["role"]}

def create_jwt(payload: dict, hours: int = 24) -> str:
    """创建JWT Token(兼容security.py/user_auth_router调用)"""
    payload["iat"] = datetime.utcnow()
    payload["exp"] = datetime.utcnow() + timedelta(hours=hours)
    if "jti" not in payload:
        payload["jti"] = secrets.token_hex(8)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt(token: str):
    """验证JWT Token,返回payload或None(兼容security.py调用)"""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def get_audit_logs(page: int = 1, size: int = 20, user: str = None, action: str = None) -> dict:
    """获取审计日志(兼容security.py调用)"""
    return {"items": [], "total": 0, "page": page, "size": size}

def get_rate_limit_stats() -> dict:
    """获取速率限制统计(兼容security.py调用)"""
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
    """获取当前用户(Bearer Token)"""
    # 兼容旧X-Agent-Token
    agent_token = request.headers.get("X-Agent-Token", "")
    if agent_token:
        if agent_token == AGENT_TOKEN:
            return {"user": "agent", "role": "admin"}
    
    if not credentials:
        raise HTTPException(401, "未提供认证Token")

    result = _decode_jwt(credentials.credentials)
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
    user = verify_user_password(req.username, req.password)
    if not user:
        raise HTTPException(401, "用户名或密码错误")
    
    token = create_token(user["username"], user["role"])
    return {
        "ok": True,
        "access_token": token,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRE_HOURS * 3600,
        "user": {"username": user["username"], "role": user["role"]},
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


# ===== 用户管理 API (仅admin) =====
class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: str = "viewer"

class UpdateRoleRequest(BaseModel):
    role: str

@auth_router.get("/users")
async def list_users(_=Depends(require_role("admin"))):
    return {"ok": True, "users": list_all_users()}

@auth_router.post("/users")
async def create_user(req: CreateUserRequest, _=Depends(require_role("admin"))):
    if not req.username or not req.password:
        raise HTTPException(400, "用户名和密码不能为空")
    if req.role not in ROLES:
        raise HTTPException(400, f"无效角色: {req.role}")
    if add_user(req.username, req.password, req.role):
        return {"ok": True, "message": f"用户 {req.username} 创建成功"}
    raise HTTPException(409, "用户名已存在")

@auth_router.delete("/users/{username}")
async def remove_user(username: str, _=Depends(require_role("admin"))):
    if delete_user(username):
        return {"ok": True, "message": f"用户 {username} 已删除"}
    raise HTTPException(400, "无法删除该用户")

@auth_router.patch("/users/{username}/role")
async def change_role(username: str, req: UpdateRoleRequest, _=Depends(require_role("admin"))):
    if update_user_role(username, req.role):
        return {"ok": True, "message": f"用户 {username} 角色更新为 {req.role}"}
    raise HTTPException(400, "更新失败")
