"""竞品价格监控 — 定时采集+价格变动预警"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from auth import verify_token
from state import state
from risk import handle_risk

router = APIRouter(prefix="/agent/competitor", tags=["Competitor"])

@router.post("/track")
async def add_track(product_name: str = Query(...), platform: str = "ebay", url: str = "", _=Depends(verify_token)):
    """添加竞品监控"""
    await handle_risk("L1", f"添加竞品: {product_name}")
    tracks = state._data.setdefault("competitor_tracks", [])
    entry = {"id": f"ct{len(tracks)+1}", "product": product_name, "platform": platform, "url": url,
             "created_at": datetime.now().isoformat(), "price_history": []}
    tracks.append(entry)
    state._save()
    return {"ok": True, "track": entry}

@router.get("/tracks")
async def list_tracks(_=Depends(verify_token)):
    """竞品监控列表"""
    return {"ok": True, "tracks": state._data.get("competitor_tracks", [])}

@router.delete("/track/{track_id}")
async def remove_track(track_id: str, _=Depends(verify_token)):
    """删除竞品监控"""
    tracks = state._data.get("competitor_tracks", [])
    state._data["competitor_tracks"] = [t for t in tracks if t.get("id") != track_id]
    state._save()
    return {"ok": True}

@router.get("/alerts")
async def price_alerts(_=Depends(verify_token)):
    """价格变动告警"""
    return {"ok": True, "alerts": state._data.get("price_alerts", [])[-20:]}
