"""Route fixes — alias POST endpoints at clean /agent/ paths.

The ASGI middleware only rewrites GET, so POST aliases need direct registration."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import verify_token

router = APIRouter(tags=["RouteFixes"])

class FixTokenRequest(BaseModel):
    subject: str = "agent"
    expire_hours: int = 24

class FixCheckRequest(BaseModel):
    domain: str

@router.post("/agent/security/token")
async def agent_security_token(req: FixTokenRequest = FixTokenRequest(), _=Depends(verify_token)):
    """Generate JWT token (alias for /security/agent/security/token)"""
    from routers.security import generate_token, JWTRequest
    inner = JWTRequest(subject=req.subject, expire_hours=req.expire_hours)
    return await generate_token(inner, _)

@router.post("/rotation/check")
async def rotation_check_short(req: FixCheckRequest, _=Depends(verify_token)):
    """Check domain health (short path alias)"""
    from routers.rotation_panel import check_domain, CheckRequest
    inner = CheckRequest(domain=req.domain)
    return await check_domain(inner, _)

@router.post("/agent/rotation/check")
async def agent_rotation_check(req: FixCheckRequest, _=Depends(verify_token)):
    """Check domain health (alias for /rotation/rotation/check)"""
    from routers.rotation_panel import check_domain, CheckRequest
    inner = CheckRequest(domain=req.domain)
    return await check_domain(inner, _)
