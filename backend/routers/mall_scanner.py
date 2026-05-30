""" -- ///"""
import httpx
from datetime import datetime
from fastapi import APIRouter, Depends
from auth import verify_token
from config import MALL_BASE_URL
from risk import handle_risk
from state import state

router = APIRouter(prefix="/mall/scan", tags=["MallScan"])

def _get_maps():
    return state._data.setdefault("mall_maps", [])

@router.post("/structure")
async def scan_structure(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    results = {
        "time": datetime.now().isoformat(),
        "status": {},
        "routes": [],
    }
    
    endpoints = [
        ('', "/"),
        ("API", "/doc.html"),
        ('', "/api/login"),
        ('', "/api/products"),
        ('', "/api/categories"),
    ]
    async with httpx.AsyncClient(timeout=5) as c:
        for name, path in endpoints:
            try:
                r = await c.get(f"{MALL_BASE_URL}{path}")
                results["status"][name] = {"code": r.status_code, "ok": r.status_code < 500}
            except Exception as e:
                results["status"][name] = {"code": 0, "ok": False, "error": str(e)}

    ok_count = sum(1 for v in results["status"].values() if v["ok"])
    total = len(results["status"])
    results["summary"] = f" {total} ,{ok_count} ,{total - ok_count} "

    
    maps = _get_maps()
    maps.insert(0, results)
    if len(maps) > 20:
        maps[:] = maps[:20]
    state._save()

    return results

@router.get("/history")
async def scan_history(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    return {"maps": _get_maps()}

@router.post("/products")
async def check_products(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    async with httpx.AsyncClient(timeout=10) as c:
        try:
            r = await c.get(f"{MALL_BASE_URL}/api/products", params={"page": 1, "size": 5})
            if r.status_code == 200:
                data = r.json()
                return {"ok": True, "total": data.get("total", "unknown"), "sample": data.get("list", data.get("records", []))[:3]}
            return {"ok": False, "code": r.status_code}
        except Exception as e:
            return {"ok": False, "error": str(e)}

@router.post("/orders")
async def check_orders(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    async with httpx.AsyncClient(timeout=10) as c:
        try:
            r = await c.get(f"{MALL_BASE_URL}/api/orders", params={"page": 1, "size": 5})
            if r.status_code == 200:
                data = r.json()
                return {"ok": True, "total": data.get("total", "unknown")}
            return {"ok": False, "code": r.status_code}
        except Exception as e:
            return {"ok": False, "error": str(e)}
