"""商城管理工具 — 用户/商品/订单/分类 CRUD + 代理转发至 mall-app"""
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from config import MALL_BASE_URL
from auth import verify_token
from state import state
from risk import handle_risk

router = APIRouter(prefix="/tools/mall", tags=["MallTools"])

async def proxy_to_mall(path: str, method: str = "GET", json_data: dict = None, params: dict = None):
    url = f"{MALL_BASE_URL}{path}"
    try:
        async with httpx.AsyncClient(timeout=10) as cli:
            if method == "GET":
                r = await cli.get(url, params=params)
            elif method == "POST":
                r = await cli.post(url, json=json_data, params=params)
            elif method == "PUT":
                r = await cli.put(url, json=json_data, params=params)
            elif method == "DELETE":
                r = await cli.delete(url, params=params)
            else:
                return None
            if r.status_code < 500:
                try:
                    return r.json()
                except Exception:
                    return {"raw": r.text[:1000]}
            return {"error": f"mall-app returned {r.status_code}", "detail": r.text[:500]}
    except Exception as e:
        return {"error": str(e)}

@router.get("/products")
async def list_products(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看商品列表")
    return await proxy_to_mall("/api/products", params={"page": page, "size": size})

@router.get("/orders")
async def list_orders(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看订单列表")
    return await proxy_to_mall("/api/orders", params={"page": page, "size": size})

@router.post("/order/refund/{order_id}")
async def force_refund_order(order_id: str, _=Depends(verify_token)):
    """强制退款"""
    await handle_risk("L3", "强制退款", f"订单ID: {order_id}")
    return await proxy_to_mall(f"/api/order/refund/{order_id}", method="POST")

@router.get("/users")
async def list_users(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看用户列表")
    return await proxy_to_mall("/api/users", params={"page": page, "size": size})

@router.get("/categories")
async def list_categories(_=Depends(verify_token)):
    await handle_risk("L1", "查看分类列表")
    return await proxy_to_mall("/api/categories")

@router.get("/stats")
async def mall_stats(_=Depends(verify_token)):
    """商城统计数据"""
    await handle_risk("L1", "查看商城统计")
    return await proxy_to_mall("/api/dashboard/stats")

@router.post("/user/status")
async def update_user_status(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "更新用户状态")
    return await proxy_to_mall("/api/user/status", method="POST", json_data=data)

@router.post("/user/balance/adjust")
async def adjust_balance(data: dict, _=Depends(verify_token)):
    risk = await handle_risk("L3", "调整用户余额")
    if not risk["allowed"]: return risk
    return await proxy_to_mall("/api/user/balance", method="POST", json_data=data)

@router.post("/product/audit")
async def audit_product(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", "审核商品")
    return await proxy_to_mall("/api/product/audit", method="POST", json_data=data)

@router.get("/recharge/pending")
async def recharge_pending(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看充值审核列表")
    return await proxy_to_mall("/api/recharge/pending", params={"page": page, "size": size})

@router.post("/recharge/audit")
async def audit_recharge(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", "审核充值")
    return await proxy_to_mall("/api/recharge/audit", method="POST", json_data=data)

@router.get("/withdraw/pending")
async def withdraw_pending(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看提现审核列表")
    return await proxy_to_mall("/api/withdraw/pending", params={"page": page, "size": size})

@router.post("/withdraw/audit")
async def audit_withdraw(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", "审核提现")
    return await proxy_to_mall("/api/withdraw/audit", method="POST", json_data=data)

@router.get("/merchant/list")
async def merchant_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看商家列表")
    return await proxy_to_mall("/api/merchant/list", params={"page": page, "size": size})

@router.post("/merchant/status")
async def merchant_status(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "更新商家状态")
    return await proxy_to_mall("/api/merchant/status", method="POST", json_data=data)

@router.get("/merchant/apply/list")
async def merchant_apply_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看商家入驻申请")
    return await proxy_to_mall("/api/merchant/apply/list", params={"page": page, "size": size})

@router.post("/merchant/apply/audit")
async def audit_merchant(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", "审核商家入驻")
    return await proxy_to_mall("/api/merchant/apply/audit", method="POST", json_data=data)

@router.get("/banners")
async def banner_list(_=Depends(verify_token)):
    await handle_risk("L1", "查看轮播列表")
    return await proxy_to_mall("/api/banners")

@router.get("/banner/{uuid}")
async def banner_detail(uuid: str, _=Depends(verify_token)):
    await handle_risk("L1", "查看轮播详情")
    return await proxy_to_mall(f"/api/banner/{uuid}")

@router.post("/banner")
async def banner_create(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "创建轮播")
    return await proxy_to_mall("/api/banner", method="POST", json_data=data)

@router.put("/banner/{uuid}")
async def banner_update(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "更新轮播")
    return await proxy_to_mall(f"/api/banner/{uuid}", method="PUT", json_data=data)

@router.delete("/banner/{uuid}")
async def banner_delete(uuid: str, _=Depends(verify_token)):
    await handle_risk("L3", "删除轮播")
    return await proxy_to_mall(f"/api/banner/{uuid}", method="DELETE")

@router.get("/category/list")
async def category_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看分类列表")
    return await proxy_to_mall("/api/category/list", params={"page": page, "size": size})

@router.get("/category/all")
async def category_all(_=Depends(verify_token)):
    await handle_risk("L1", "查看全部分类")
    return await proxy_to_mall("/api/category/all")

@router.get("/category/{uuid}")
async def category_detail(uuid: str, _=Depends(verify_token)):
    await handle_risk("L1", "查看分类详情")
    return await proxy_to_mall(f"/api/category/{uuid}")

@router.post("/category")
async def category_create(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "创建分类")
    return await proxy_to_mall("/api/category", method="POST", json_data=data)

@router.put("/category/{uuid}")
async def category_update(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "更新分类")
    return await proxy_to_mall(f"/api/category/{uuid}", method="PUT", json_data=data)

@router.put("/category/{uuid}/status")
async def category_status(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "更新分类状态")
    return await proxy_to_mall(f"/api/category/{uuid}/status", method="PUT", json_data=data)

@router.delete("/category/{uuid}")
async def category_delete(uuid: str, _=Depends(verify_token)):
    await handle_risk("L3", "删除分类")
    return await proxy_to_mall(f"/api/category/{uuid}", method="DELETE")

@router.get("/evaluations")
async def evaluation_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看评价列表")
    return await proxy_to_mall("/api/evaluations", params={"page": page, "size": size})

@router.put("/evaluation/{uuid}/status")
async def evaluation_status(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "更新评价状态")
    return await proxy_to_mall(f"/api/evaluation/{uuid}/status", method="PUT", json_data=data)

@router.delete("/evaluation/{uuid}")
async def evaluation_delete(uuid: str, _=Depends(verify_token)):
    await handle_risk("L3", "删除评价")
    return await proxy_to_mall(f"/api/evaluation/{uuid}", method="DELETE")