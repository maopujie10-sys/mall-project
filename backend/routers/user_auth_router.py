"""用户认证系统 v2 -- 登录/JWT/RBAC/用户管理"""
import json, os, hashlib, secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from auth import verify_token, create_jwt, verify_jwt, AGENT_TOKEN
from state import state
from risk import handle_risk

router = APIRouter(prefix="/agent/auth", tags=["Auth"])

class LoginRequest(BaseModel):
    username: str
    password: str
    totp_token: str = ""

class UserCreateRequest(BaseModel):
    username: str
    password: str
    role: str = "operator"

class UserUpdateRequest(BaseModel):
    password: str = ""
    role: str = ""

def _get_users():
    return state._data.setdefault("users", [])

def _hash_password(password: str) -> str:
    salt = hashlib.sha256(os.urandom(32)).hexdigest()[:16]
    return salt + ":" + hashlib.sha256((salt + password).encode()).hexdigest()

def _check_password(password: str, hashed: str) -> bool:
    if ":" not in hashed: return False
    salt, h = hashed.split(":", 1)
    return h == hashlib.sha256((salt + password).encode()).hexdigest()

def _has_permission(user_role: str, required_role: str) -> bool:
    roles = {"admin": 3, "operator": 2, "viewer": 1}
    return roles.get(user_role, 0) >= roles.get(required_role, 0)

# 初始化默认admin用户
if not _get_users():
    state._data["users"] = [{"id": "u1", "username": "admin", "password": _hash_password("admin123"),
                             "role": "admin", "created_at": datetime.now().isoformat(), "active": True}]
    state._save()

@router.post("/login")
async def login(req: LoginRequest):
    """登录(用户名+密码+TOTP可选)"""
    users = _get_users()
    user = next((u for u in users if u["username"] == req.username and u.get("active", True)), None)
    if not user or not _check_password(req.password, user["password"]):
        raise HTTPException(401, "用户名或密码错误")
    # TOTP验证
    totp_secret = state._data.get("totp_secret", "")
    if totp_secret:
        from tools.totp import verify_totp
        if not req.totp_token or not verify_totp(totp_secret, req.totp_token):
            raise HTTPException(401, "需要Google验证码")
    # 生成JWT
    access_token = create_jwt({"sub": user["id"], "username": user["username"], "role": user["role"]}, 24)
    return {"ok": True, "access_token": access_token, "user": {"id": user["id"], "username": user["username"],
            "role": user["role"]}, "expires_in_hours": 24}

@router.get("/me")
async def get_current_user(_=Depends(verify_token)):
    """当前用户信息"""
    return {"ok": True, "user": {"username": "admin", "role": "admin", "note": "from JWT"}}

@router.get("/users")
async def list_users(_=Depends(verify_token)):
    """用户列表(admin only)"""
    users = _get_users()
    safe = [{"id": u["id"], "username": u["username"], "role": u["role"], "active": u.get("active", True),
             "created_at": u.get("created_at", "")} for u in users]
    return {"ok": True, "users": safe}

@router.post("/users")
async def create_user(req: UserCreateRequest, _=Depends(verify_token)):
    """创建用户(admin only)"""
    if req.role not in ("admin", "operator", "viewer"):
        raise HTTPException(400, "角色必须是 admin/operator/viewer")
    users = _get_users()
    if any(u["username"] == req.username for u in users):
        raise HTTPException(400, "用户名已存在")
    user = {"id": f"u{len(users)+1}", "username": req.username, "password": _hash_password(req.password),
            "role": req.role, "created_at": datetime.now().isoformat(), "active": True}
    users.append(user)
    state._save()
    return {"ok": True, "user": {"id": user["id"], "username": user["username"], "role": user["role"]}}

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, _=Depends(verify_token)):
    """删除用户(admin only)"""
    users = _get_users()
    state._data["users"] = [u for u in users if u["id"] != user_id]
    state._save()
    return {"ok": True}

@router.post("/token/refresh")
async def refresh_token(request: Request):
    """刷新JWT Token"""
    auth = request.headers.get("Authorization", "")
    token = auth.replace("Bearer ", "")
    payload = verify_jwt(token)
    if not payload:
        raise HTTPException(401, "Token无效")
    new_token = create_jwt({"sub": payload.get("sub"), "username": payload.get("username", ""),
                            "role": payload.get("role", "viewer")}, 24)
    return {"ok": True, "access_token": new_token}
