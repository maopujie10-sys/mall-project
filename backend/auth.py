"""认证模块 — Token 验证"""
from fastapi import Request, HTTPException
from config import AGENT_TOKEN

async def verify_token(request: Request):
    token = request.headers.get("X-Agent-Token", "")
    if token != AGENT_TOKEN:
        raise HTTPException(status_code=403, detail="无效的Agent Token")
