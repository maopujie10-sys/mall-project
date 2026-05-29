"""鍟嗗煄缁撴瀯璁ょ煡 鈥?鎵弿鍟嗗煄缁撴瀯/鎺ュ彛/鏁版嵁搴?涓氬姟娴佺▼"""
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
    """鎵弿鍟嗗煄椤圭洰鐩綍缁撴瀯鍜岃矾鐢?""
    await handle_risk("L1", "鎵弿鍟嗗煄缁撴瀯")
    results = {
        "time": datetime.now().isoformat(),
        "status": {},
        "routes": [],
    }
    # 妫€娴嬪悇鎺ュ彛杩為€氭€?    endpoints = [
        ("棣栭〉", "/"),
        ("API鏂囨。", "/doc.html"),
        ("鐧诲綍", "/api/login"),
        ("鍟嗗搧鍒楄〃", "/api/products"),
        ("鍒嗙被", "/api/categories"),
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
    results["summary"] = f"妫€娴?{total} 涓鐐癸紝{ok_count} 涓甯革紝{total - ok_count} 涓紓甯?

    # 淇濆瓨鎵弿璁板綍
    maps = _get_maps()
    maps.insert(0, results)
    if len(maps) > 20:
        maps[:] = maps[:20]
    state._save()

    return results

@router.get("/history")
async def scan_history(_=Depends(verify_token)):
    """鏌ョ湅鎵爜鍘嗗彶"""
    await handle_risk("L1", "鏌ョ湅鎵弿鍘嗗彶")
    return {"maps": _get_maps()}

@router.post("/products")
async def check_products(_=Depends(verify_token)):
    """妫€娴嬪晢鍝佺郴缁熸槸鍚︽甯?""
    await handle_risk("L1", "妫€娴嬪晢鍝佺郴缁?)
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
    """妫€娴嬭鍗曠郴缁熸槸鍚︽甯?""
    await handle_risk("L1", "妫€娴嬭鍗曠郴缁?)
    async with httpx.AsyncClient(timeout=10) as c:
        try:
            r = await c.get(f"{MALL_BASE_URL}/api/orders", params={"page": 1, "size": 5})
            if r.status_code == 200:
                data = r.json()
                return {"ok": True, "total": data.get("total", "unknown")}
            return {"ok": False, "code": r.status_code}
        except Exception as e:
            return {"ok": False, "error": str(e)}
