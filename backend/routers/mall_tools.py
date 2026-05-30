"""Mall Tools API - mall-app Controller"""
import httpx
from fastapi import APIRouter, Depends
from config import MALL_BASE_URL
from auth import verify_token
from state import state
from risk import handle_risk
from mask import mask_sensitive

router = APIRouter(prefix="/tools/mall", tags=["MallTools"])

async def proxy_to_mall(path: str, method: str = "GET", json_data: dict = None, params: dict = None):
    url = f"{MALL_BASE_URL}{path}"
    try:
        async with httpx.AsyncClient(timeout=15) as cli:
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
                    data = r.json()
                    return mask_sensitive(data, level="user")
                except Exception:
                    return {"raw": r.text[:1000]}
            return {"error": f"mall-app returned {r.status_code}", "detail": r.text[:500]}
    except Exception as e:
        return {"error": str(e)}
# ============================================================

# ============================================================

@router.get("/stats")
async def mall_stats(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/dashboard/stats")


# ============================================================
#  (ProductController)
# ============================================================

@router.get("/products")
async def list_products(_=Depends(verify_token), page: int = 1, size: int = 20, keyword: str = None, category_id: str = None):
    await handle_risk("L1", '')
    params = {"page": page, "size": size}
    if keyword: params["keyword"] = keyword
    if category_id: params["category_id"] = category_id
    return await proxy_to_mall("/api/products", params=params)

@router.get("/product/{uuid}")
async def product_detail(uuid: str, _=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall(f"/api/product/{uuid}")

@router.post("/product/audit")
async def audit_product(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", '')
    return await proxy_to_mall("/api/product/audit", method="POST", json_data=data)

@router.put("/product/{uuid}")
async def update_product(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/api/product/{uuid}", method="PUT", json_data=data)

@router.post("/product")
async def create_product(data: dict, _=Depends(verify_token)):
    """创建商品 (AdminController.productCreate)"""
    await handle_risk("L2", '', f"{data.get('name','')}")
    return await proxy_to_mall("/api/product", method="POST", json_data=data)

@router.delete("/product/{uuid}")
async def delete_product(uuid: str, _=Depends(verify_token)):
    await handle_risk("L3", '')
    return await proxy_to_mall(f"/api/product/{uuid}", method="DELETE")


# ============================================================
#  (OrderController + OrderLogController + OrdersLocalController)
# ============================================================

@router.get("/orders")
async def list_orders(_=Depends(verify_token), page: int = 1, size: int = 20, status: str = None, keyword: str = None):
    await handle_risk("L1", '')
    params = {"page": page, "size": size}
    if status: params["status"] = status
    if keyword: params["keyword"] = keyword
    return await proxy_to_mall("/api/orders", params=params)

@router.get("/order/{order_id}")
async def order_detail(order_id: str, _=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall(f"/api/order/{order_id}")

@router.post("/order/refund/{order_id}")
async def force_refund_order(order_id: str, data: dict = None, _=Depends(verify_token)):
    ''''''
    await handle_risk("L3", '', f"ID: {order_id}")
    return await proxy_to_mall(f"/api/order/refund/{order_id}", method="POST", json_data=data or {})

@router.get("/order/{order_id}/logs")
async def order_logs(order_id: str, _=Depends(verify_token)):
    ''" (OrderLogController)''"
    await handle_risk("L1", '')
    return await proxy_to_mall(f"/api/order-log/{order_id}")


# ============================================================
#  (UserController)
# ============================================================

@router.get("/users")
async def list_users(_=Depends(verify_token), page: int = 1, size: int = 20, keyword: str = None):
    await handle_risk("L1", '')
    params = {"page": page, "size": size}
    if keyword: params["keyword"] = keyword
    return await proxy_to_mall("/api/users", params=params)

@router.get("/user/{user_id}")
async def user_detail(user_id: str, _=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall(f"/api/user/{user_id}")

@router.post("/user/status")
async def update_user_status(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall("/api/user/status", method="POST", json_data=data)

@router.post("/user/balance/adjust")
async def adjust_balance(data: dict, _=Depends(verify_token)):
    risk = await handle_risk("L3", '')
    if not risk.get("allowed", True): return risk
    return await proxy_to_mall("/api/user/balance", method="POST", json_data=data)

# ============================================================
#  (Category CRUD)
# ============================================================

@router.get("/categories")
async def list_categories(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/categories")

@router.get("/category/list")
async def category_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/category/list", params={"page": page, "size": size})

@router.get("/category/all")
async def category_all(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/category/all")

@router.get("/category/{uuid}")
async def category_detail(uuid: str, _=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall(f"/api/category/{uuid}")

@router.post("/category")
async def category_create(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall("/api/category", method="POST", json_data=data)

@router.put("/category/{uuid}")
async def category_update(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/api/category/{uuid}", method="PUT", json_data=data)

@router.put("/category/{uuid}/status")
async def category_status(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/api/category/{uuid}/status", method="PUT", json_data=data)

@router.delete("/category/{uuid}")
async def category_delete(uuid: str, _=Depends(verify_token)):
    await handle_risk("L3", '')
    return await proxy_to_mall(f"/api/category/{uuid}", method="DELETE")


# ============================================================
#  (WalletController)
# ============================================================

@router.get("/wallet/logs")
async def wallet_logs(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/wallet/logs", params={"page": page, "pageSize": size})

@router.get("/wallet/balance")
async def wallet_balance(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/wallet/balance")


# ============================================================
#  (RechargeController)
# ============================================================

@router.get("/recharge/pending")
async def recharge_pending(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/recharge/pending", params={"page": page, "size": size})

@router.post("/recharge/audit")
async def audit_recharge(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", '')
    return await proxy_to_mall("/api/recharge/audit", method="POST", json_data=data)


# ============================================================
#  (WithdrawController)
# ============================================================

@router.get("/withdraw/pending")
async def withdraw_pending(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/withdraw/pending", params={"page": page, "size": size})

@router.post("/withdraw/audit")
async def audit_withdraw(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", '')
    return await proxy_to_mall("/api/withdraw/audit", method="POST", json_data=data)

# ============================================================
#  (LogisticsController)
# ============================================================

@router.get("/logistics/{order_id}")
async def logistics_info(order_id: str, _=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall(f"/api/logistics/{order_id}")

@router.get("/logistics/{order_id}/trace")
async def logistics_trace(order_id: str, _=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall(f"/api/logistics/{order_id}/trace")


# ============================================================
# KYC  (KycController + KycHighLevelController)
# ============================================================

@router.get("/kyc/list")
async def kyc_list(_=Depends(verify_token), page: int = 1, size: int = 20, status: int = None):
    await handle_risk("L1", "KYC")
    params = {"pageNum": page, "pageSize": size}
    if status is not None: params["status"] = status
    return await proxy_to_mall("/admin/kyc/list", params=params)

@router.post("/kyc/audit/{kyc_id}")
async def kyc_audit(kyc_id: int, data: dict, _=Depends(verify_token)):
    await handle_risk("L3", "KYC")
    return await proxy_to_mall(f"/admin/kyc/audit/{kyc_id}", method="POST", json_data=data)

@router.get("/kyc-high-level")
async def kyc_high_level(_=Depends(verify_token)):
    await handle_risk("L1", "KYC")
    return await proxy_to_mall("/api/kyc-high-level")


# ============================================================
#  (ComplaintController)
# ============================================================

@router.get("/complaints")
async def complaint_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/complaint/list", params={"pageNum": page, "pageSize": size})

@router.post("/complaint/handle/{uuid}")
async def complaint_handle(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/api/complaint/handle/{uuid}", method="POST", json_data=data)


# ============================================================
#  (ContractController)
# ============================================================

@router.get("/contract/info")
async def contract_info(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/contract/info")

@router.get("/contract/list")
async def contract_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/contract/list", params={"page": page, "size": size})


# ============================================================
#  (CreditController)
# ============================================================

@router.get("/credits")
async def credit_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/credit/list", params={"page": page, "size": size})

# ============================================================
#  (LoanController)
# ============================================================

@router.get("/loan/admin/list")
async def loan_admin_list(_=Depends(verify_token), page: int = 1, size: int = 20, keyword: str = None, status: int = None):
    await handle_risk("L1", '')
    params = {"page": page, "pageSize": size}
    if keyword: params["keyword"] = keyword
    if status is not None: params["status"] = status
    return await proxy_to_mall("/api/loan/admin/list", params=params)

@router.post("/loan/admin/audit")
async def loan_audit(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", '')
    return await proxy_to_mall("/api/loan/admin/audit", method="POST", json_data=data)

@router.get("/loan/config")
async def loan_config(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/loan/config")

@router.get("/loan/admin/configs")
async def loan_configs(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/loan/admin/configs")


# ============================================================
#  (CommentController)
# ============================================================

@router.get("/comments/{good_id}")
async def comment_list(good_id: str, _=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall(f"/api/comment/list/{good_id}", params={"page": page, "pageSize": size})

@router.delete("/comment/{uuid}")
async def comment_delete(uuid: str, _=Depends(verify_token)):
    await handle_risk("L3", '')
    return await proxy_to_mall(f"/api/comment/{uuid}", method="DELETE")


# ============================================================
#  (EvaluationController)
# ============================================================

@router.get("/evaluations")
async def evaluation_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/evaluations", params={"page": page, "size": size})

@router.put("/evaluation/{uuid}/status")
async def evaluation_status(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/api/evaluation/{uuid}/status", method="PUT", json_data=data)

@router.delete("/evaluation/{uuid}")
async def evaluation_delete(uuid: str, _=Depends(verify_token)):
    await handle_risk("L3", '')
    return await proxy_to_mall(f"/api/evaluation/{uuid}", method="DELETE")


# ============================================================
#  (AddressController)
# ============================================================

@router.get("/addresses")
async def address_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/address/list", params={"page": page, "size": size})


# ============================================================
#  (CartController)
# ============================================================

@router.get("/carts")
async def cart_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/cart/list", params={"page": page, "size": size})

# ============================================================
#  (KeepGoodsController)
# ============================================================

@router.get("/keep-goods")
async def keep_goods_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/keep-goods/list", params={"page": page, "pageSize": size})


# ============================================================
#  (FocusSellerController)
# ============================================================

@router.get("/focus-sellers")
async def focus_seller_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/focus-seller/list", params={"page": page, "pageSize": size})


# ============================================================
#  (InviteController)
# ============================================================

@router.get("/invites")
async def invite_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/invite/list", params={"page": page, "size": size})

@router.get("/invite/stats")
async def invite_stats(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/invite/stats")


# ============================================================
#  (LotteryController)
# ============================================================

@router.get("/lottery/current")
async def lottery_current(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/promote/lottery/current")

@router.get("/lottery/{activity_id}")
async def lottery_detail(activity_id: str, _=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall(f"/api/promote/lottery?activityId={activity_id}")


# ============================================================
#  (RebateController)
# ============================================================

@router.get("/rebates")
async def rebate_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/rebate/list", params={"page": page, "pageSize": size})

@router.get("/rebate/stats")
async def rebate_stats(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/rebate/stats")


# ============================================================
#  (PromoteController)
# ============================================================

@router.get("/promotes")
async def promote_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/promote/list", params={"page": page, "size": size})

@router.get("/promote/config")
async def promote_config(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/promote/config")


# ============================================================
#  (SubscribeController)
# ============================================================

@router.get("/subscribes")
async def subscribe_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/subscribe/list", params={"page": page, "size": size})

# ============================================================
#  (MerchantController + SellerController + SellerPromotionalController + SellerVersionController)
# ============================================================

@router.get("/merchant/list")
async def merchant_list(_=Depends(verify_token), page: int = 1, size: int = 20, keyword: str = None, status: str = None):
    await handle_risk("L1", '')
    params = {"page": page, "size": size}
    if keyword: params["keyword"] = keyword
    if status: params["status"] = status
    return await proxy_to_mall("/api/merchant/list", params=params)

@router.post("/merchant/status")
async def merchant_status(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall("/api/merchant/status", method="POST", json_data=data)

@router.get("/merchant/apply/list")
async def merchant_apply_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/merchant/apply/list", params={"page": page, "size": size})

@router.post("/merchant/apply/audit")
async def audit_merchant(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", '')
    return await proxy_to_mall("/api/merchant/apply/audit", method="POST", json_data=data)

@router.get("/seller/list")
async def seller_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/seller/list", params={"page": page, "size": size})

@router.get("/seller/promotional")
async def seller_promotional(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/seller/promotional")


# ============================================================
#  (MerchantDashboardController)
# ============================================================

@router.get("/merchant/dashboard")
async def merchant_dashboard(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/merchant/instrument-panel/head")


# ============================================================
#  (MerchantFinanceController)
# ============================================================

@router.get("/merchant/finance")
async def merchant_finance(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/merchant/finance/list", params={"page": page, "size": size})

@router.get("/merchant/finance-report/head")
async def merchant_finance_head(_=Depends(verify_token)):
    """财务报表KPI汇总"""
    await handle_risk("L1", '')
    return await proxy_to_mall("/merchant/finance-report/head")

@router.get("/merchant/finance-report/list")
async def merchant_finance_report(_=Depends(verify_token), page: int = 1, size: int = 30):
    """财务报表明细"""
    await handle_risk("L1", '')
    return await proxy_to_mall("/merchant/finance-report/list", params={"page": page, "size": size})


# ============================================================
#  (MerchantGoodsController)
# ============================================================

@router.get("/merchant/goods")
async def merchant_goods(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/merchant/goods/list", params={"page": page, "size": size})


# ============================================================
#  (MerchantOrderController)
# ============================================================

@router.get("/merchant/orders")
async def merchant_orders(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/merchant/order/list", params={"page": page, "size": size})


# ============================================================
#  (MerchantEvaluationController)
# ============================================================

@router.get("/merchant/evaluations")
async def merchant_evaluations(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/merchant/evaluation/list", params={"page": page, "size": size})

# ============================================================
#  (BannerController)
# ============================================================

@router.get("/banners")
async def banner_list(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/banners")

@router.get("/banner/{uuid}")
async def banner_detail(uuid: str, _=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall(f"/api/banner/{uuid}")

@router.post("/banner")
async def banner_create(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall("/api/banner", method="POST", json_data=data)

@router.put("/banner/{uuid}")
async def banner_update(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/api/banner/{uuid}", method="PUT", json_data=data)

@router.delete("/banner/{uuid}")
async def banner_delete(uuid: str, _=Depends(verify_token)):
    await handle_risk("L3", '')
    return await proxy_to_mall(f"/api/banner/{uuid}", method="DELETE")


# ============================================================
#  (NewsController)
# ============================================================

@router.get("/news/list")
async def news_list(_=Depends(verify_token), page: int = 1, size: int = 20, lang: str = None):
    await handle_risk("L1", '')
    params = {"pageNum": page, "pageSize": size}
    if lang: params["lang"] = lang
    return await proxy_to_mall("/api/news/list", params=params)

@router.get("/news/{news_id}")
async def news_detail(news_id: int, _=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall(f"/api/news/{news_id}")

@router.post("/news")
async def news_create(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall("/api/news", method="POST", json_data=data)

@router.put("/news/{news_id}")
async def news_update(news_id: int, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/api/news/{news_id}", method="PUT", json_data=data)

@router.delete("/news/{news_id}")
async def news_delete(news_id: int, _=Depends(verify_token)):
    await handle_risk("L3", '')
    return await proxy_to_mall(f"/api/news/{news_id}", method="DELETE")


# ============================================================
#  (NotificationController)
# ============================================================

@router.get("/notifications")
async def notification_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/notification/list", params={"page": page, "size": size})

@router.post("/notification")
async def notification_create(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall("/api/notification", method="POST", json_data=data)

@router.put("/notification/{nid}")
async def notification_update(nid: str, data: dict, _=Depends(verify_token)):
    """更新通知 (AdminController.notificationUpdate)"""
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/api/notification/{nid}", method="PUT", json_data=data)

@router.delete("/notification/{nid}")
async def notification_delete(nid: str, _=Depends(verify_token)):
    """删除通知 (AdminController.notificationAdminDelete)"""
    await handle_risk("L3", '')
    return await proxy_to_mall(f"/api/notification/{nid}", method="DELETE")

# ============================================================
#  (SysParamController)
# ============================================================

@router.get("/syspara/list")
async def syspara_list(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/admin/syspara/list")

@router.get("/syspara/{key}")
async def syspara_get(key: str, _=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall(f"/api/syspara/{key}")

@router.post("/syspara")
async def syspara_save(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall("/admin/syspara", method="POST", json_data=data)

@router.put("/syspara/{sys_id}")
async def syspara_update(sys_id: int, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/admin/syspara/{sys_id}", method="PUT", json_data=data)

@router.delete("/syspara/{sys_id}")
async def syspara_delete(sys_id: int, _=Depends(verify_token)):
    await handle_risk("L3", '')
    return await proxy_to_mall(f"/admin/syspara/{sys_id}", method="DELETE")


# ============================================================
#  (AreaController)
# ============================================================

@router.get("/area/countries")
async def area_countries(_=Depends(verify_token), lang: str = "zh"):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/area/countries", params={"lang": lang})

@router.get("/area/states")
async def area_states(_=Depends(verify_token), country_id: int = None):
    await handle_risk("L1", "/")
    return await proxy_to_mall("/api/area/states", params={"countryId": country_id})

@router.get("/area/cities")
async def area_cities(_=Depends(verify_token), state_id: int = None):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/area/cities", params={"stateId": state_id})

@router.get("/area/mobile-prefix")
async def area_mobile_prefix(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/area/mobile-prefix")

# 区域后台管理CRUD
@router.get("/area/admin/countries")
async def area_admin_countries(_=Depends(verify_token), page: int = 1, size: int = 50):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/area/admin/countries", params={"page": page, "size": size})

@router.post("/area/admin/country")
async def area_country_create(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '', f"{data.get('name','')}")
    return await proxy_to_mall("/api/area/admin/country", method="POST", json_data=data)

@router.put("/area/admin/country/{cid}")
async def area_country_update(cid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/api/area/admin/country/{cid}", method="PUT", json_data=data)

@router.delete("/area/admin/country/{cid}")
async def area_country_delete(cid: str, _=Depends(verify_token)):
    await handle_risk("L3", '')
    return await proxy_to_mall(f"/api/area/admin/country/{cid}", method="DELETE")

@router.get("/area/admin/cities")
async def area_admin_cities(_=Depends(verify_token), page: int = 1, size: int = 50, country_id: str = None):
    await handle_risk("L1", '')
    params = {"page": page, "size": size}
    if country_id: params["countryId"] = country_id
    return await proxy_to_mall("/api/area/admin/cities", params=params)

@router.post("/area/admin/city")
async def area_city_create(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '', f"{data.get('name','')}")
    return await proxy_to_mall("/api/area/admin/city", method="POST", json_data=data)

@router.put("/area/admin/city/{cid}")
async def area_city_update(cid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/api/area/admin/city/{cid}", method="PUT", json_data=data)

@router.delete("/area/admin/city/{cid}")
async def area_city_delete(cid: str, _=Depends(verify_token)):
    await handle_risk("L3", '')
    return await proxy_to_mall(f"/api/area/admin/city/{cid}", method="DELETE")


# ============================================================
#  (MallLevelController)
# ============================================================

@router.get("/malllevel/list")
async def malllevel_list(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/malllevel/list")

@router.get("/malllevel/{uuid}")
async def malllevel_detail(uuid: str, _=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall(f"/api/malllevel/{uuid}")

@router.get("/malllevel/config")
async def malllevel_config(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/malllevel/config")


# ============================================================
# / (ChatController) -- 
# ============================================================

@router.get("/chat/conversations")
async def chat_conversations(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/chat/admin/conversations", params={"page": page, "pageSize": size})

@router.get("/chat/messages/{conversation_id}")
async def chat_messages(conversation_id: str, _=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall(f"/api/chat/admin/messages/{conversation_id}")

@router.get("/chat/admin/onechat")
async def chat_admin_onechat(_=Depends(verify_token), conversation_id: str = None):
    await handle_risk("L1", '')
    return await proxy_to_mall(f"/api/chat/admin/onechat?conversationId={conversation_id}")

@router.post("/chat/admin/reply")
async def chat_admin_reply(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall("/api/chat/admin/reply", method="POST", json_data=data)

# ============================================================
#  (IdcodeController)
# ============================================================

@router.get("/idcodes")
async def idcode_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/idcode/list", params={"page": page, "size": size})


# ============================================================
#  (ComboController)
# ============================================================

@router.get("/combos")
async def combo_list(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/combo/list")

@router.post("/combo")
async def combo_create(data: dict, _=Depends(verify_token)):
    """创建套餐 (AdminController.comboSave)"""
    await handle_risk("L2", '', f"{data.get('name','')}")
    return await proxy_to_mall("/api/combo", method="POST", json_data=data)

@router.put("/combo/{uuid}")
async def combo_update(uuid: str, data: dict, _=Depends(verify_token)):
    """更新套餐 (AdminController.comboUpdate)"""
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/api/combo/{uuid}", method="PUT", json_data=data)

@router.delete("/combo/{uuid}")
async def combo_delete(uuid: str, _=Depends(verify_token)):
    """删除套餐 (AdminController.comboDelete)"""
    await handle_risk("L3", '')
    return await proxy_to_mall(f"/api/combo/{uuid}", method="DELETE")

@router.get("/combo/records")
async def combo_records(_=Depends(verify_token), page: int = 1, size: int = 20):
    """套餐购买记录"""
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/combo/record/list", params={"page": page, "size": size})


# ============================================================
#  (GeetestController)
# ============================================================

@router.get("/geetest/config")
async def geetest_config(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/geetest/config")


# ============================================================
# Google (GoogleAuthController)
# ============================================================

@router.get("/google-auth/list")
async def google_auth_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "Google")
    return await proxy_to_mall("/api/google-auth/list", params={"page": page, "size": size})


# ============================================================
#  (AdminController)
# ============================================================

@router.get("/admins")
async def admin_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/admin/list", params={"page": page, "size": size})

@router.post("/admin")
async def admin_create(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall("/api/admin", method="POST", json_data=data)

@router.put("/admin/{admin_id}")
async def admin_update(admin_id: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/api/admin/{admin_id}", method="PUT", json_data=data)


# ============================================================

# ============================================================

@router.post("/batch/products/status")
async def batch_product_status(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", '')
    return await proxy_to_mall("/api/product/batch/status", method="POST", json_data=data)

@router.post("/batch/orders/status")
async def batch_order_status(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", '')
    return await proxy_to_mall("/api/order/batch/status", method="POST", json_data=data)

@router.post("/batch/users/status")
async def batch_user_status(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", '')
    return await proxy_to_mall("/api/user/batch/status", method="POST", json_data=data)

# ============================================================
#  (AgentController)
# ============================================================

@router.get("/attr-categories")
async def list_attr_categories(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/agent/attr-category/list")

@router.get("/attr-category/{uuid}")
async def get_attr_category(uuid: str, _=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall(f"/agent/attr-category/{uuid}")

@router.post("/attr-category")
async def create_attr_category(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall("/agent/attr-category", method="POST", json_data=data)

@router.put("/attr-category/{uuid}")
async def update_attr_category(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/agent/attr-category/{uuid}", method="PUT", json_data=data)

@router.delete("/attr-category/{uuid}")
async def delete_attr_category(uuid: str, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/agent/attr-category/{uuid}", method="DELETE")

@router.get("/attrs")
async def list_attrs(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/agent/attr/list")

@router.get("/attr/{uuid}")
async def get_attr(uuid: str, _=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall(f"/agent/attr/{uuid}")

@router.post("/attr")
async def create_attr(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall("/agent/attr", method="POST", json_data=data)

@router.put("/attr/{uuid}")
async def update_attr(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/agent/attr/{uuid}", method="PUT", json_data=data)

@router.delete("/attr/{uuid}")
async def delete_attr(uuid: str, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/agent/attr/{uuid}", method="DELETE")

@router.get("/attr-values")
async def list_attr_values(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/agent/attr-value/list")

@router.get("/attr-value/{id}")
async def get_attr_value(id: int, _=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall(f"/agent/attr-value/{id}")

@router.post("/attr-value")
async def create_attr_value(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall("/agent/attr-value", method="POST", json_data=data)

@router.put("/attr-value/{id}")
async def update_attr_value(id: int, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/agent/attr-value/{id}", method="PUT", json_data=data)

@router.delete("/attr-value/{id}")
async def delete_attr_value(id: int, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/agent/attr-value/{id}", method="DELETE")

# ============================================================
#  (AgentController)
# ============================================================

@router.post("/seed/products")
async def seed_products(_=Depends(verify_token)):
    await handle_risk("L3", '')
    return await proxy_to_mall("/agent/seed/products", method="POST")

@router.post("/seed/orders")
async def seed_orders(_=Depends(verify_token)):
    await handle_risk("L3", '')
    return await proxy_to_mall("/agent/seed/orders", method="POST")

@router.post("/seed/users")
async def seed_users(_=Depends(verify_token)):
    await handle_risk("L3", '')
    return await proxy_to_mall("/agent/seed/users", method="POST")

@router.post("/seed/merchants")
async def seed_merchants(_=Depends(verify_token)):
    await handle_risk("L3", '')
    return await proxy_to_mall("/agent/seed/merchants", method="POST")

@router.post("/seed/comments")
async def seed_comments(_=Depends(verify_token)):
    await handle_risk("L3", '')
    return await proxy_to_mall("/agent/seed/comments", method="POST")

@router.post("/seed/clear")
async def seed_clear(_=Depends(verify_token)):
    await handle_risk("L4", '')
    return await proxy_to_mall("/agent/seed/clear", method="DELETE")

# ============================================================
#  (OrdersLocalController)
# ============================================================

@router.post("/order-local/submit")
async def submit_local_order(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall("/api/order-local/submit", method="POST", json_data=data)

# ============================================================
#  (SellerVersionController)
# ============================================================

@router.post("/seller/version/client")
async def seller_version_client(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall("/seller/version/client", method="POST", json_data=data)

@router.post("/seller/version/register")
async def seller_version_register(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall("/seller/version/register", method="POST", json_data=data)

@router.post("/seller/version/register-js")
async def seller_version_register_js(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "JS")
    return await proxy_to_mall("/seller/version/register-js", method="POST", json_data=data)

@router.post("/seller/version/update-sign-pdf")
async def seller_version_update_sign(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall("/seller/version/update-sign-pdf", method="POST", json_data=data)

# ============================================================
#  (UploadImgController)
# ============================================================

@router.get("/upload/list")
async def list_uploads(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/upload/list")

@router.get("/upload/files")
async def list_upload_files(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/upload/list")

@router.delete("/upload/{id}")
async def delete_upload(id: int, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/api/upload/{id}", method="DELETE")

# ============================================================
# Java (RotationController) -- AI
# ============================================================

@router.get("/rotation/domains")
async def java_rotation_domains(_=Depends(verify_token)):
    await handle_risk("L1", "Java")
    return await proxy_to_mall("/api/rotation/domains")

@router.post("/rotation/block")
async def java_rotation_block(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall("/api/rotation/block", method="POST", json_data=data)

@router.post("/rotation/unblock")
async def java_rotation_unblock(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall("/api/rotation/unblock", method="POST", json_data=data)

@router.get("/rotation/stats")
async def java_rotation_stats(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/api/rotation/stats")

# ============================================================
# 代理管理 (AdminController agent/*)
# ============================================================

@router.get("/agent/list")
async def agent_list(_=Depends(verify_token), page: int = 1, size: int = 20, keyword: str = None):
    await handle_risk("L1", '代理列表')
    params = {"page": page, "size": size}
    if keyword: params["keyword"] = keyword
    return await proxy_to_mall("/admin/agent/list", params=params)

@router.get("/agent/{seller_id}")
async def agent_detail(seller_id: str, _=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall(f"/admin/agent/{seller_id}")

@router.put("/agent/{seller_id}/status")
async def agent_update_status(seller_id: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/admin/agent/{seller_id}/status", method="PUT", json_data=data)

@router.get("/agent/{seller_id}/team")
async def agent_team(seller_id: str, _=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall(f"/admin/agent/{seller_id}/team")

@router.get("/agent/levels")
async def agent_level_list(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/admin/agent/level/list")

@router.post("/agent/level")
async def agent_level_create(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall("/admin/agent/level", method="POST", json_data=data)

@router.put("/agent/level/{uuid}")
async def agent_level_update(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/admin/agent/level/{uuid}", method="PUT", json_data=data)

@router.delete("/agent/level/{uuid}")
async def agent_level_delete(uuid: str, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/admin/agent/level/{uuid}", method="DELETE")

@router.get("/agent/rebates")
async def agent_rebate_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/admin/agent/rebate/list", params={"page": page, "size": size})

@router.get("/agent/rebate/stats")
async def agent_rebate_stats(_=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall("/admin/agent/rebate/stats")

# ============================================================
# 活动/抽奖管理 (AdminController activity/*)
# ============================================================

@router.get("/activity/list")
async def activity_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '')
    return await proxy_to_mall("/admin/activity/list", params={"page": page, "size": size})

@router.get("/activity/{activity_id}")
async def activity_detail(activity_id: str, _=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall(f"/admin/activity/{activity_id}")

@router.post("/activity")
async def activity_create(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '', f"{data.get('title','')}")
    return await proxy_to_mall("/admin/activity", method="POST", json_data=data)

@router.put("/activity/{activity_id}")
async def activity_update(activity_id: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/admin/activity/{activity_id}", method="PUT", json_data=data)

@router.put("/activity/{activity_id}/toggle")
async def activity_toggle(activity_id: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/admin/activity/{activity_id}/show", method="PUT", json_data=data)

@router.delete("/activity/{activity_id}")
async def activity_delete(activity_id: str, _=Depends(verify_token)):
    await handle_risk("L3", '')
    return await proxy_to_mall(f"/admin/activity/{activity_id}", method="DELETE")

@router.get("/activity/{activity_id}/prizes")
async def activity_prize_list(activity_id: str, _=Depends(verify_token)):
    await handle_risk("L1", '')
    return await proxy_to_mall(f"/admin/activity/{activity_id}/prize/list")

@router.post("/activity/prize")
async def activity_prize_create(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall("/admin/activity/prize", method="POST", json_data=data)

@router.put("/activity/prize/{prize_id}")
async def activity_prize_update(prize_id: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/admin/activity/prize/{prize_id}", method="PUT", json_data=data)

@router.delete("/activity/prize/{prize_id}")
async def activity_prize_delete(prize_id: str, _=Depends(verify_token)):
    await handle_risk("L2", '')
    return await proxy_to_mall(f"/admin/activity/prize/{prize_id}", method="DELETE")

@router.get("/activity/records")
async def activity_record_list(_=Depends(verify_token), page: int = 1, size: int = 20, activity_id: str = None):
    await handle_risk("L1", '')
    params = {"page": page, "size": size}
    if activity_id: params["activityId"] = activity_id
    return await proxy_to_mall("/admin/activity/record/list", params=params)

# ============================================================
# 安全重置审核 (AdminController safeword/*)
# ============================================================

@router.get("/safeword/list")
async def safeword_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", '安全重置')
    return await proxy_to_mall("/admin/safeword/list", params={"page": page, "size": size})

@router.post("/safeword/{apply_id}/approve")
async def safeword_approve(apply_id: str, _=Depends(verify_token)):
    await handle_risk("L3", '', f"ID: {apply_id}")
    return await proxy_to_mall(f"/admin/safeword/{apply_id}/approve", method="POST")

@router.post("/safeword/{apply_id}/reject")
async def safeword_reject(apply_id: str, _=Depends(verify_token)):
    await handle_risk("L3", '', f"ID: {apply_id}")
    return await proxy_to_mall(f"/admin/safeword/{apply_id}/reject", method="POST")
