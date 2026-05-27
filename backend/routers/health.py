"""健康检查接口 — 公开，供Docker healthcheck + 外部监控"""
from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get("/agent/health")
async def health():
    return {"status": "ok", "service": "TikTokMall Agent", "version": "1.0.0"}
