"""健康检查接口 — 公开，供 Docker healthcheck + 外部监控"""
from fastapi import APIRouter
from risk import handle_risk

router = APIRouter(tags=["Health"])

@router.get("/agent/health")
async def health():
    await handle_risk("L1", "健康检查", "/agent/health")
    return {"status": "ok", "service": "TikTokMall Agent", "version": "1.0.0"}
