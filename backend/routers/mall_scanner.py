"""商城结构认知 — 扫描商城结构/接口/数据库/业务流程"""
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
    """扫描商城项目目录结构和路由"""
    await handle_risk("L1", "扫描商城结构")
    results = {
        "time": datetime.now().isoformat(),
        "status": {},
        "routes": [],
    }
    # 检测各接口连通性
    endpoints = [
        ("首页", "/"),
        ("API文档", "/doc.html"),
        ("登录", "/api/login"),
        ("商品列表", "/api/products"),
        ("分类", "/api/categories"),
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
    results["summary"] = f"检测 {total} 个端点，{ok_count} 个正常，{total - ok_count} 个异常"

    # 保存扫描记录
    maps = _get_maps()
    maps.insert(0, results)
    if len(maps) > 20:
        maps[:] = maps[:20]
    state._save()

    return results

@router.get("/history")
async def scan_history(_=Depends(verify_token)):
    """查看扫码历史"""
    await handle_risk("L1", "查看扫描历史")
    return {"maps": _get_maps()}

@router.post("/products")
async def check_products(_=Depends(verify_token)):
    """检测商品系统是否正常"""
    await handle_risk("L1", "检测商品系统")
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
    """检测订单系统是否正常"""
    await handle_risk("L1", "检测订单系统")
    async with httpx.AsyncClient(timeout=10) as c:
        try:
            r = await c.get(f"{MALL_BASE_URL}/api/orders", params={"page": 1, "size": 5})
            if r.status_code == 200:
                data = r.json()
                return {"ok": True, "total": data.get("total", "unknown")}
            return {"ok": False, "code": r.status_code}
        except Exception as e:
            return {"ok": False, "error": str(e)}
