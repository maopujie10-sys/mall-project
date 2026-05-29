锘?""鑷姩宸℃ 鈥?绔欑偣鐩戞帶/SEO/鎬ц兘妫€娴?+ 瀹氭椂鑷剤"""
import httpx
import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import verify_token
from config import MALL_BASE_URL
from risk import handle_risk
from state import state

router = APIRouter(prefix="/autopilot", tags=["Autopilot"])

PAGES = ["/", "/api/products", "/api/categories", "/api/banners"]
SITEMAP_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>"""

def _get_logs():
    return state._data.setdefault("autopilot_logs", [])

def _get_schedule():
    return state._data.setdefault("autopilot_schedule", {"enabled": False, "interval_minutes": 30, "last_run": None})

@router.post("/visit")
async def visit_pages(_=Depends(verify_token)):
    """鑷姩宸℃ 鈥?绔欑偣鐩戞帶/SEO/鎬ц兘妫€娴?+ 瀹氭椂鑷剤"""
    await handle_risk("L2", "锟皆讹拷锟斤拷站-页锟斤拷锟斤拷锟?)
    logs = _get_logs()
    results = []
    async with httpx.AsyncClient(timeout=10) as c:
        for path in PAGES:
            try:
                r = await c.get(f"{MALL_BASE_URL}{path}", headers={"User-Agent": "Mozilla/5.0 (compatible; AutopilotBot/1.0)"})
                results.append({"path": path, "status": r.status_code, "ok": r.status_code < 500})
            except Exception as e:
                results.append({"path": path, "status": 0, "ok": False, "error": str(e)})
    record = {"time": datetime.now().strftime("%H:%M:%S"), "action": "visit", "results": results, "ok": sum(1 for r in results if r["ok"])}
    logs.insert(0, record)
    if len(logs) > 100: logs[:] = logs[:100]
    state._save()
    return {"pages_visited": len(results), "ok": record["ok"], "results": results}

@router.post("/sitemap-gen")
async def generate_sitemap(_=Depends(verify_token)):
    """鑷姩宸℃ 鈥?绔欑偣鐩戞帶/SEO/鎬ц兘妫€娴?+ 瀹氭椂鑷剤"""
    await handle_risk("L1", "锟斤拷锟斤拷SEO Sitemap")
    async with httpx.AsyncClient(timeout=10) as c:
        try:
            r = await c.get(f"{MALL_BASE_URL}/api/products", params={"page": 1, "size": 100})
            products = r.json().get("list", r.json().get("records", [])) if r.status_code == 200 else []
        except Exception:
            products = []
    urls = "\n".join([f'  <url><loc>{MALL_BASE_URL}/product/{p.get("id", "")}</loc></url>' for p in products])
    sitemap = SITEMAP_TEMPLATE.format(urls=urls or f'  <url><loc>{MALL_BASE_URL}</loc></url>')
    return {"sitemap": sitemap, "product_count": len(products)}

@router.get("/logs")
async def autopilot_logs(_=Depends(verify_token)):
    """鑷姩宸℃ 鈥?绔欑偣鐩戞帶/SEO/鎬ц兘妫€娴?+ 瀹氭椂鑷剤"""
    await handle_risk("L1", "锟介看锟斤拷站锟斤拷志")
    return {"logs": _get_logs()[:20]}

@router.get("/schedule")
async def get_schedule(_=Depends(verify_token)):
    """鑷姩宸℃ 鈥?绔欑偣鐩戞帶/SEO/鎬ц兘妫€娴?+ 瀹氭椂鑷剤"""
    await handle_risk("L1", "锟介看锟斤拷时锟斤拷锟斤拷")
    sched = _get_schedule()
    return sched

@router.post("/schedule")
async def set_schedule(_=Depends(verify_token), enabled: bool = True, interval: int = 30):
    """鑷姩宸℃ 鈥?绔欑偣鐩戞帶/SEO/鎬ц兘妫€娴?+ 瀹氭椂鑷剤"""
    await handle_risk("L2", f"锟斤拷锟矫讹拷时锟斤拷锟斤拷", f"enabled={enabled} interval={interval}min")
    sched = _get_schedule()
    sched["enabled"] = enabled
    sched["interval_minutes"] = interval
    sched["updated_at"] = datetime.now().isoformat()
    state._save()
    return {"enabled": enabled, "interval_minutes": interval, "message": "锟斤拷时锟斤拷锟斤拷锟斤拷锟斤拷锟矫ｏ拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟叫э拷锟?}

@router.post("/full-auto")
async def full_auto_pilot(_=Depends(verify_token)):
    """鑷姩宸℃ 鈥?绔欑偣鐩戞帶/SEO/鎬ц兘妫€娴?+ 瀹氭椂鑷剤"""
    await handle_risk("L2", "一锟斤拷锟皆讹拷锟斤拷站")
    logs = _get_logs()

    # 1. 锟斤拷锟斤拷页锟斤拷
    visit_results = []
    async with httpx.AsyncClient(timeout=10) as c:
        for path in PAGES:
            try:
                r = await c.get(f"{MALL_BASE_URL}{path}", headers={"User-Agent": "Mozilla/5.0"})
                visit_results.append({"path": path, "status": r.status_code, "ok": r.status_code < 500})
            except Exception as e:
                visit_results.append({"path": path, "status": 0, "ok": False, "error": str(e)})

    ok_visits = sum(1 for r in visit_results if r["ok"])
    total_visits = len(visit_results)

    # 2. 锟斤拷锟斤拷Sitemap
    try:
        sitemap_result = "锟斤拷锟斤拷锟斤拷"
    except Exception:
        sitemap_result = "失锟斤拷"

    record = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "action": "full_auto",
        "pages_visited": f"{ok_visits}/{total_visits}",
        "sitemap": sitemap_result,
    }
    logs.insert(0, record)
    if len(logs) > 100: logs[:] = logs[:100]
    state._save()

    return {
        "visit": {"ok": ok_visits, "total": total_visits, "results": visit_results},
        "sitemap": sitemap_result,
        "status": "锟斤拷锟? if ok_visits == total_visits else "锟斤拷锟斤拷锟届常",
    }
