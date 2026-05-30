"""绔炲搧鐩戞帶澧炲己 -- 浠锋牸鍙樺姩鍛婅+鏂板搧鍙戠幇+淇冮攢杩借釜+瓒嬪娍鍒嗘瀽"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from auth import verify_token
from state import state
from risk import handle_risk

router = APIRouter(prefix="/agent/competitor", tags=["Competitor"])

class TrackRequest(BaseModel):
    product_name: str
    platform: str = "ebay"
    url: str = ""
    target_price: float = 0
    category: str = ""

@router.post("/track")
async def add_track(req: TrackRequest, _=Depends(verify_token)):
    """娣诲姞绔炲搧鐩戞帶"""
    await handle_risk("L1", f"娣诲姞绔炲搧: {req.product_name}")
    tracks = state._data.setdefault("competitor_tracks", [])
    entry = {
        "id": f"ct{len(tracks)+1}",
        "product": req.product_name,
        "platform": req.platform,
        "url": req.url,
        "target_price": req.target_price,
        "category": req.category,
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "price_history": [],
        "alerts": [],
        "promotions": [],
    }
    tracks.append(entry)
    state._save()
    return {"ok": True, "track": entry}

@router.get("/tracks")
async def list_tracks(_=Depends(verify_token)):
    """绔炲搧鐩戞帶鍒楄〃"""
    return {"ok": True, "tracks": state._data.get("competitor_tracks", [])}

@router.delete("/track/{track_id}")
async def remove_track(track_id: str, _=Depends(verify_token)):
    """鍒犻櫎绔炲搧鐩戞帶"""
    tracks = state._data.get("competitor_tracks", [])
    state._data["competitor_tracks"] = [t for t in tracks if t.get("id") != track_id]
    state._save()
    return {"ok": True}

@router.post("/track/{track_id}/price")
async def record_price(track_id: str, price: float = Query(...), currency: str = "USD", _=Depends(verify_token)):
    """璁板綍浠锋牸鍙樺姩"""
    tracks = state._data.get("competitor_tracks", [])
    for t in tracks:
        if t.get("id") == track_id:
            history = t.setdefault("price_history", [])
            prev = history[-1]["price"] if history else None
            entry = {"price": price, "currency": currency, "time": datetime.now().isoformat()}
            if prev and prev != price:
                change = round((price - prev) / prev * 100, 1)
                entry["change_pct"] = change
                alerts = t.setdefault("alerts", [])
                alerts.append({
                    "type": "price_change",
                    "from": prev, "to": price,
                    "change_pct": change,
                    "time": datetime.now().isoformat(),
                    "severity": "P1" if abs(change) > 20 else "P2" if abs(change) > 10 else "P3"
                })
                global_alerts = state._data.setdefault("price_alerts", [])
                global_alerts.append({
                    "product": t["product"], "platform": t["platform"],
                    "from": prev, "to": price, "change_pct": change,
                    "time": datetime.now().isoformat()
                })
            history.append(entry)
            if t.get("target_price") and price <= t["target_price"]:
                alerts = t.setdefault("alerts", [])
                alerts.append({
                    "type": "target_reached",
                    "price": price, "target": t["target_price"],
                    "time": datetime.now().isoformat(),
                    "severity": "P1"
                })
            state._save()
            return {"ok": True, "price": price, "change": change if prev else 0}
    return {"ok": False, "error": "竞品不存在"}

@router.post("/track/{track_id}/promotion")
async def record_promotion(track_id: str, title: str = Query(...), discount: str = Query(""), _=Depends(verify_token)):
    """璁板綍淇冮攢娲诲姩"""
    tracks = state._data.get("competitor_tracks", [])
    for t in tracks:
        if t.get("id") == track_id:
            promos = t.setdefault("promotions", [])
            promos.append({"title": title, "discount": discount, "time": datetime.now().isoformat()})
            state._save()
            return {"ok": True, "promotion": {"title": title, "discount": discount}}
    return {"ok": False, "error": "竞品不存在"}

@router.get("/alerts")
async def price_alerts(days: int = 7, _=Depends(verify_token)):
    """浠锋牸鍙樺姩鍛婅"""
    alerts = state._data.get("price_alerts", [])
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    recent = [a for a in alerts if a.get("time", "") >= cutoff]
    return {"ok": True, "total": len(recent), "alerts": recent[-50:]}

@router.get("/trends")
async def price_trends(_=Depends(verify_token)):
    """绔炲搧浠锋牸瓒嬪娍鍒嗘瀽"""
    tracks = state._data.get("competitor_tracks", [])
    trends = []
    for t in tracks:
        history = t.get("price_history", [])
        if len(history) >= 2:
            first = history[0]["price"]
            last = history[-1]["price"]
            change = round((last - first) / first * 100, 1) if first else 0
            trend = "up" if change > 5 else "down" if change < -5 else "stable"
            trends.append({
                "product": t["product"],
                "platform": t["platform"],
                "first_price": first,
                "last_price": last,
                "change_pct": change,
                "trend": trend,
                "data_points": len(history),
            })
    return {"ok": True, "trends": trends}

@router.get("/promotions")
async def active_promotions(_=Depends(verify_token)):
    """娲昏穬淇冮攢娲诲姩"""
    tracks = state._data.get("competitor_tracks", [])
    promos = []
    for t in tracks:
        for p in t.get("promotions", [])[-5:]:
            promos.append({**p, "product": t["product"], "platform": t["platform"]})
    return {"ok": True, "total": len(promos), "promotions": promos[-20:]}

@router.get("/summary")
async def competitor_summary(_=Depends(verify_token)):
    """绔炲搧鐩戞帶鎬昏"""
    tracks = state._data.get("competitor_tracks", [])
    active = sum(1 for t in tracks if t.get("status") == "active")
    total_alerts = sum(len(t.get("alerts", [])) for t in tracks)
    total_promos = sum(len(t.get("promotions", [])) for t in tracks)
    price_changes = state._data.get("price_alerts", [])
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    recent_changes = sum(1 for a in price_changes if a.get("time", "") >= week_ago)
    
    platforms = {}
    for t in tracks:
        p = t.get("platform", "other")
        platforms[p] = platforms.get(p, 0) + 1
    
    return {
        "ok": True,
        "total_tracks": len(tracks),
        "active_tracks": active,
        "total_alerts": total_alerts,
        "total_promotions": total_promos,
        "price_changes_7d": recent_changes,
        "by_platform": platforms,
    }
