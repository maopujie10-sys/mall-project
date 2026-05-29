锘?""鍟嗗煄绠＄悊宸ュ叿 鈥?鍏ㄩ噺浠ｇ悊 mall-app 鍚庣鍏ㄩ儴 Controller
鍟嗗搧/璁㈠崟/鐢ㄦ埛/鍒嗙被/閽卞寘/鐗╂祦/KYC/鎶曡瘔/鍚堝悓/淇＄敤/鍊熻捶/璇勮/璇勪环/鍦板潃/璐墿杞?鏀惰棌/鍏虫敞/閭€璇?鎶藉/杩斿埄/淇冮攢/璁㈤槄/鍟嗗/杞挱/鏂伴椈/閫氱煡/绯荤粺鍙傛暟/鍖哄煙/绛夌骇/鑱婂ぉ/杞€?韬唤璇?濂楅/瀹㈡湇"""
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
# 缁熻闈㈡澘
# ============================================================

@router.get("/stats")
async def mall_stats(_=Depends(verify_token)):
    """鍟嗗煄缁熻鏁版嵁"""
    await handle_risk("L1", "鏌ョ湅鍟嗗煄缁熻")
    return await proxy_to_mall("/api/dashboard/stats")


# ============================================================
# 鍟嗗搧绠＄悊 (ProductController)
# ============================================================

@router.get("/products")
async def list_products(_=Depends(verify_token), page: int = 1, size: int = 20, keyword: str = None, category_id: str = None):
    await handle_risk("L1", "鏌ョ湅鍟嗗搧鍒楄〃")
    params = {"page": page, "size": size}
    if keyword: params["keyword"] = keyword
    if category_id: params["category_id"] = category_id
    return await proxy_to_mall("/api/products", params=params)

@router.get("/product/{uuid}")
async def product_detail(uuid: str, _=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅鍟嗗搧璇︽儏")
    return await proxy_to_mall(f"/api/product/{uuid}")

@router.post("/product/audit")
async def audit_product(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", "瀹℃牳鍟嗗搧")
    return await proxy_to_mall("/api/product/audit", method="POST", json_data=data)

@router.put("/product/{uuid}")
async def update_product(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鏇存柊鍟嗗搧")
    return await proxy_to_mall(f"/api/product/{uuid}", method="PUT", json_data=data)

@router.delete("/product/{uuid}")
async def delete_product(uuid: str, _=Depends(verify_token)):
    await handle_risk("L3", "鍒犻櫎鍟嗗搧")
    return await proxy_to_mall(f"/api/product/{uuid}", method="DELETE")


# ============================================================
# 璁㈠崟绠＄悊 (OrderController + OrderLogController + OrdersLocalController)
# ============================================================

@router.get("/orders")
async def list_orders(_=Depends(verify_token), page: int = 1, size: int = 20, status: str = None, keyword: str = None):
    await handle_risk("L1", "鏌ョ湅璁㈠崟鍒楄〃")
    params = {"page": page, "size": size}
    if status: params["status"] = status
    if keyword: params["keyword"] = keyword
    return await proxy_to_mall("/api/orders", params=params)

@router.get("/order/{order_id}")
async def order_detail(order_id: str, _=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅璁㈠崟璇︽儏")
    return await proxy_to_mall(f"/api/order/{order_id}")

@router.post("/order/refund/{order_id}")
async def force_refund_order(order_id: str, data: dict = None, _=Depends(verify_token)):
    """寮哄埗閫€娆?""
    await handle_risk("L3", "寮哄埗閫€娆?, f"璁㈠崟ID: {order_id}")
    return await proxy_to_mall(f"/api/order/refund/{order_id}", method="POST", json_data=data or {})

@router.get("/order/{order_id}/logs")
async def order_logs(order_id: str, _=Depends(verify_token)):
    """璁㈠崟鏃ュ織 (OrderLogController)"""
    await handle_risk("L1", "鏌ョ湅璁㈠崟鏃ュ織")
    return await proxy_to_mall(f"/api/order-log/{order_id}")


# ============================================================
# 鐢ㄦ埛绠＄悊 (UserController)
# ============================================================

@router.get("/users")
async def list_users(_=Depends(verify_token), page: int = 1, size: int = 20, keyword: str = None):
    await handle_risk("L1", "鏌ョ湅鐢ㄦ埛鍒楄〃")
    params = {"page": page, "size": size}
    if keyword: params["keyword"] = keyword
    return await proxy_to_mall("/api/users", params=params)

@router.get("/user/{user_id}")
async def user_detail(user_id: str, _=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅鐢ㄦ埛璇︽儏")
    return await proxy_to_mall(f"/api/user/{user_id}")

@router.post("/user/status")
async def update_user_status(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鏇存柊鐢ㄦ埛鐘舵€?)
    return await proxy_to_mall("/api/user/status", method="POST", json_data=data)

@router.post("/user/balance/adjust")
async def adjust_balance(data: dict, _=Depends(verify_token)):
    risk = await handle_risk("L3", "璋冩暣鐢ㄦ埛浣欓")
    if not risk.get("allowed", True): return risk
    return await proxy_to_mall("/api/user/balance", method="POST", json_data=data)

# ============================================================
# 鍒嗙被绠＄悊 (Category CRUD)
# ============================================================

@router.get("/categories")
async def list_categories(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅鍒嗙被鍒楄〃")
    return await proxy_to_mall("/api/categories")

@router.get("/category/list")
async def category_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅鍒嗙被鍒楄〃")
    return await proxy_to_mall("/api/category/list", params={"page": page, "size": size})

@router.get("/category/all")
async def category_all(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅鍏ㄩ儴鍒嗙被")
    return await proxy_to_mall("/api/category/all")

@router.get("/category/{uuid}")
async def category_detail(uuid: str, _=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅鍒嗙被璇︽儏")
    return await proxy_to_mall(f"/api/category/{uuid}")

@router.post("/category")
async def category_create(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鍒涘缓鍒嗙被")
    return await proxy_to_mall("/api/category", method="POST", json_data=data)

@router.put("/category/{uuid}")
async def category_update(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鏇存柊鍒嗙被")
    return await proxy_to_mall(f"/api/category/{uuid}", method="PUT", json_data=data)

@router.put("/category/{uuid}/status")
async def category_status(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鏇存柊鍒嗙被鐘舵€?)
    return await proxy_to_mall(f"/api/category/{uuid}/status", method="PUT", json_data=data)

@router.delete("/category/{uuid}")
async def category_delete(uuid: str, _=Depends(verify_token)):
    await handle_risk("L3", "鍒犻櫎鍒嗙被")
    return await proxy_to_mall(f"/api/category/{uuid}", method="DELETE")


# ============================================================
# 閽卞寘绠＄悊 (WalletController)
# ============================================================

@router.get("/wallet/logs")
async def wallet_logs(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅閽卞寘娴佹按")
    return await proxy_to_mall("/api/wallet/logs", params={"page": page, "pageSize": size})

@router.get("/wallet/balance")
async def wallet_balance(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅閽卞寘浣欓")
    return await proxy_to_mall("/api/wallet/balance")


# ============================================================
# 鍏呭€肩鐞?(RechargeController)
# ============================================================

@router.get("/recharge/pending")
async def recharge_pending(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅鍏呭€煎鏍稿垪琛?)
    return await proxy_to_mall("/api/recharge/pending", params={"page": page, "size": size})

@router.post("/recharge/audit")
async def audit_recharge(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", "瀹℃牳鍏呭€?)
    return await proxy_to_mall("/api/recharge/audit", method="POST", json_data=data)


# ============================================================
# 鎻愮幇绠＄悊 (WithdrawController)
# ============================================================

@router.get("/withdraw/pending")
async def withdraw_pending(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅鎻愮幇瀹℃牳鍒楄〃")
    return await proxy_to_mall("/api/withdraw/pending", params={"page": page, "size": size})

@router.post("/withdraw/audit")
async def audit_withdraw(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", "瀹℃牳鎻愮幇")
    return await proxy_to_mall("/api/withdraw/audit", method="POST", json_data=data)

# ============================================================
# 鐗╂祦绠＄悊 (LogisticsController)
# ============================================================

@router.get("/logistics/{order_id}")
async def logistics_info(order_id: str, _=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅鐗╂祦淇℃伅")
    return await proxy_to_mall(f"/api/logistics/{order_id}")

@router.get("/logistics/{order_id}/trace")
async def logistics_trace(order_id: str, _=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅鐗╂祦杞ㄨ抗")
    return await proxy_to_mall(f"/api/logistics/{order_id}/trace")


# ============================================================
# KYC 璁よ瘉绠＄悊 (KycController + KycHighLevelController)
# ============================================================

@router.get("/kyc/list")
async def kyc_list(_=Depends(verify_token), page: int = 1, size: int = 20, status: int = None):
    await handle_risk("L1", "鏌ョ湅KYC鍒楄〃")
    params = {"pageNum": page, "pageSize": size}
    if status is not None: params["status"] = status
    return await proxy_to_mall("/admin/kyc/list", params=params)

@router.post("/kyc/audit/{kyc_id}")
async def kyc_audit(kyc_id: int, data: dict, _=Depends(verify_token)):
    await handle_risk("L3", "瀹℃牳KYC")
    return await proxy_to_mall(f"/admin/kyc/audit/{kyc_id}", method="POST", json_data=data)

@router.get("/kyc-high-level")
async def kyc_high_level(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅楂樼骇KYC")
    return await proxy_to_mall("/api/kyc-high-level")


# ============================================================
# 鎶曡瘔绠＄悊 (ComplaintController)
# ============================================================

@router.get("/complaints")
async def complaint_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅鎶曡瘔鍒楄〃")
    return await proxy_to_mall("/api/complaint/list", params={"pageNum": page, "pageSize": size})

@router.post("/complaint/handle/{uuid}")
async def complaint_handle(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "澶勭悊鎶曡瘔")
    return await proxy_to_mall(f"/api/complaint/handle/{uuid}", method="POST", json_data=data)


# ============================================================
# 鍚堝悓绠＄悊 (ContractController)
# ============================================================

@router.get("/contract/info")
async def contract_info(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅鍚堝悓淇℃伅")
    return await proxy_to_mall("/api/contract/info")

@router.get("/contract/list")
async def contract_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅鍚堝悓鍒楄〃")
    return await proxy_to_mall("/api/contract/list", params={"page": page, "size": size})


# ============================================================
# 淇＄敤绠＄悊 (CreditController)
# ============================================================

@router.get("/credits")
async def credit_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅淇＄敤鍒楄〃")
    return await proxy_to_mall("/api/credit/list", params={"page": page, "size": size})

# ============================================================
# 鍊熻捶绠＄悊 (LoanController)
# ============================================================

@router.get("/loan/admin/list")
async def loan_admin_list(_=Depends(verify_token), page: int = 1, size: int = 20, keyword: str = None, status: int = None):
    await handle_risk("L1", "鏌ョ湅鍊熻捶鍒楄〃")
    params = {"page": page, "pageSize": size}
    if keyword: params["keyword"] = keyword
    if status is not None: params["status"] = status
    return await proxy_to_mall("/api/loan/admin/list", params=params)

@router.post("/loan/admin/audit")
async def loan_audit(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", "瀹℃牳鍊熻捶")
    return await proxy_to_mall("/api/loan/admin/audit", method="POST", json_data=data)

@router.get("/loan/config")
async def loan_config(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅鍊熻捶閰嶇疆")
    return await proxy_to_mall("/api/loan/config")

@router.get("/loan/admin/configs")
async def loan_configs(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅鍊熻捶閰嶇疆鍒楄〃")
    return await proxy_to_mall("/api/loan/admin/configs")


# ============================================================
# 璇勮绠＄悊 (CommentController)
# ============================================================

@router.get("/comments/{good_id}")
async def comment_list(good_id: str, _=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅鍟嗗搧璇勮")
    return await proxy_to_mall(f"/api/comment/list/{good_id}", params={"page": page, "pageSize": size})

@router.delete("/comment/{uuid}")
async def comment_delete(uuid: str, _=Depends(verify_token)):
    await handle_risk("L3", "鍒犻櫎璇勮")
    return await proxy_to_mall(f"/api/comment/{uuid}", method="DELETE")


# ============================================================
# 璇勪环绠＄悊 (EvaluationController)
# ============================================================

@router.get("/evaluations")
async def evaluation_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅璇勪环鍒楄〃")
    return await proxy_to_mall("/api/evaluations", params={"page": page, "size": size})

@router.put("/evaluation/{uuid}/status")
async def evaluation_status(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鏇存柊璇勪环鐘舵€?)
    return await proxy_to_mall(f"/api/evaluation/{uuid}/status", method="PUT", json_data=data)

@router.delete("/evaluation/{uuid}")
async def evaluation_delete(uuid: str, _=Depends(verify_token)):
    await handle_risk("L3", "鍒犻櫎璇勪环")
    return await proxy_to_mall(f"/api/evaluation/{uuid}", method="DELETE")


# ============================================================
# 鍦板潃绠＄悊 (AddressController)
# ============================================================

@router.get("/addresses")
async def address_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅鍦板潃鍒楄〃")
    return await proxy_to_mall("/api/address/list", params={"page": page, "size": size})


# ============================================================
# 璐墿杞︾鐞?(CartController)
# ============================================================

@router.get("/carts")
async def cart_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅璐墿杞﹀垪琛?)
    return await proxy_to_mall("/api/cart/list", params={"page": page, "size": size})

# ============================================================
# 鏀惰棌绠＄悊 (KeepGoodsController)
# ============================================================

@router.get("/keep-goods")
async def keep_goods_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅鏀惰棌鍒楄〃")
    return await proxy_to_mall("/api/keep-goods/list", params={"page": page, "pageSize": size})


# ============================================================
# 鍏虫敞绠＄悊 (FocusSellerController)
# ============================================================

@router.get("/focus-sellers")
async def focus_seller_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅鍏虫敞鍟嗗鍒楄〃")
    return await proxy_to_mall("/api/focus-seller/list", params={"page": page, "pageSize": size})


# ============================================================
# 閭€璇风鐞?(InviteController)
# ============================================================

@router.get("/invites")
async def invite_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅閭€璇峰垪琛?)
    return await proxy_to_mall("/api/invite/list", params={"page": page, "size": size})

@router.get("/invite/stats")
async def invite_stats(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅閭€璇风粺璁?)
    return await proxy_to_mall("/api/invite/stats")


# ============================================================
# 鎶藉绠＄悊 (LotteryController)
# ============================================================

@router.get("/lottery/current")
async def lottery_current(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅褰撳墠鎶藉娲诲姩")
    return await proxy_to_mall("/api/promote/lottery/current")

@router.get("/lottery/{activity_id}")
async def lottery_detail(activity_id: str, _=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅鎶藉璇︽儏")
    return await proxy_to_mall(f"/api/promote/lottery?activityId={activity_id}")


# ============================================================
# 杩斿埄绠＄悊 (RebateController)
# ============================================================

@router.get("/rebates")
async def rebate_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅杩斿埄鍒楄〃")
    return await proxy_to_mall("/api/rebate/list", params={"page": page, "pageSize": size})

@router.get("/rebate/stats")
async def rebate_stats(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅杩斿埄缁熻")
    return await proxy_to_mall("/api/rebate/stats")


# ============================================================
# 淇冮攢绠＄悊 (PromoteController)
# ============================================================

@router.get("/promotes")
async def promote_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅淇冮攢鍒楄〃")
    return await proxy_to_mall("/api/promote/list", params={"page": page, "size": size})

@router.get("/promote/config")
async def promote_config(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅淇冮攢閰嶇疆")
    return await proxy_to_mall("/api/promote/config")


# ============================================================
# 璁㈤槄绠＄悊 (SubscribeController)
# ============================================================

@router.get("/subscribes")
async def subscribe_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅璁㈤槄鍒楄〃")
    return await proxy_to_mall("/api/subscribe/list", params={"page": page, "size": size})

# ============================================================
# 鍟嗗绠＄悊 (MerchantController + SellerController + SellerPromotionalController + SellerVersionController)
# ============================================================

@router.get("/merchant/list")
async def merchant_list(_=Depends(verify_token), page: int = 1, size: int = 20, keyword: str = None, status: str = None):
    await handle_risk("L1", "鏌ョ湅鍟嗗鍒楄〃")
    params = {"page": page, "size": size}
    if keyword: params["keyword"] = keyword
    if status: params["status"] = status
    return await proxy_to_mall("/api/merchant/list", params=params)

@router.post("/merchant/status")
async def merchant_status(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鏇存柊鍟嗗鐘舵€?)
    return await proxy_to_mall("/api/merchant/status", method="POST", json_data=data)

@router.get("/merchant/apply/list")
async def merchant_apply_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅鍟嗗鍏ラ┗鐢宠")
    return await proxy_to_mall("/api/merchant/apply/list", params={"page": page, "size": size})

@router.post("/merchant/apply/audit")
async def audit_merchant(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", "瀹℃牳鍟嗗鍏ラ┗")
    return await proxy_to_mall("/api/merchant/apply/audit", method="POST", json_data=data)

@router.get("/seller/list")
async def seller_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅鍗栧鍒楄〃")
    return await proxy_to_mall("/api/seller/list", params={"page": page, "size": size})

@router.get("/seller/promotional")
async def seller_promotional(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅鍗栧鎺ㄥ箍")
    return await proxy_to_mall("/api/seller/promotional")


# ============================================================
# 鍟嗗浠〃鐩?(MerchantDashboardController)
# ============================================================

@router.get("/merchant/dashboard")
async def merchant_dashboard(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅鍟嗗浠〃鐩?)
    return await proxy_to_mall("/merchant/instrument-panel/head")


# ============================================================
# 鍟嗗璐㈠姟 (MerchantFinanceController)
# ============================================================

@router.get("/merchant/finance")
async def merchant_finance(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅鍟嗗璐㈠姟")
    return await proxy_to_mall("/merchant/finance/list", params={"page": page, "size": size})


# ============================================================
# 鍟嗗鍟嗗搧 (MerchantGoodsController)
# ============================================================

@router.get("/merchant/goods")
async def merchant_goods(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅鍟嗗鍟嗗搧")
    return await proxy_to_mall("/merchant/goods/list", params={"page": page, "size": size})


# ============================================================
# 鍟嗗璁㈠崟 (MerchantOrderController)
# ============================================================

@router.get("/merchant/orders")
async def merchant_orders(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅鍟嗗璁㈠崟")
    return await proxy_to_mall("/merchant/order/list", params={"page": page, "size": size})


# ============================================================
# 鍟嗗璇勪环 (MerchantEvaluationController)
# ============================================================

@router.get("/merchant/evaluations")
async def merchant_evaluations(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅鍟嗗璇勪环")
    return await proxy_to_mall("/merchant/evaluation/list", params={"page": page, "size": size})

# ============================================================
# 杞挱鍥剧鐞?(BannerController)
# ============================================================

@router.get("/banners")
async def banner_list(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅杞挱鍒楄〃")
    return await proxy_to_mall("/api/banners")

@router.get("/banner/{uuid}")
async def banner_detail(uuid: str, _=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅杞挱璇︽儏")
    return await proxy_to_mall(f"/api/banner/{uuid}")

@router.post("/banner")
async def banner_create(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鍒涘缓杞挱")
    return await proxy_to_mall("/api/banner", method="POST", json_data=data)

@router.put("/banner/{uuid}")
async def banner_update(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鏇存柊杞挱")
    return await proxy_to_mall(f"/api/banner/{uuid}", method="PUT", json_data=data)

@router.delete("/banner/{uuid}")
async def banner_delete(uuid: str, _=Depends(verify_token)):
    await handle_risk("L3", "鍒犻櫎杞挱")
    return await proxy_to_mall(f"/api/banner/{uuid}", method="DELETE")


# ============================================================
# 鏂伴椈绠＄悊 (NewsController)
# ============================================================

@router.get("/news/list")
async def news_list(_=Depends(verify_token), page: int = 1, size: int = 20, lang: str = None):
    await handle_risk("L1", "鏌ョ湅鏂伴椈鍒楄〃")
    params = {"pageNum": page, "pageSize": size}
    if lang: params["lang"] = lang
    return await proxy_to_mall("/api/news/list", params=params)

@router.get("/news/{news_id}")
async def news_detail(news_id: int, _=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅鏂伴椈璇︽儏")
    return await proxy_to_mall(f"/api/news/{news_id}")

@router.post("/news")
async def news_create(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鍒涘缓鏂伴椈")
    return await proxy_to_mall("/api/news", method="POST", json_data=data)

@router.put("/news/{news_id}")
async def news_update(news_id: int, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鏇存柊鏂伴椈")
    return await proxy_to_mall(f"/api/news/{news_id}", method="PUT", json_data=data)

@router.delete("/news/{news_id}")
async def news_delete(news_id: int, _=Depends(verify_token)):
    await handle_risk("L3", "鍒犻櫎鏂伴椈")
    return await proxy_to_mall(f"/api/news/{news_id}", method="DELETE")


# ============================================================
# 閫氱煡绠＄悊 (NotificationController)
# ============================================================

@router.get("/notifications")
async def notification_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅閫氱煡鍒楄〃")
    return await proxy_to_mall("/api/notification/list", params={"page": page, "size": size})

@router.post("/notification")
async def notification_create(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鍒涘缓閫氱煡")
    return await proxy_to_mall("/api/notification", method="POST", json_data=data)

# ============================================================
# 绯荤粺鍙傛暟 (SysParamController)
# ============================================================

@router.get("/syspara/list")
async def syspara_list(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅绯荤粺鍙傛暟")
    return await proxy_to_mall("/admin/syspara/list")

@router.get("/syspara/{key}")
async def syspara_get(key: str, _=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅绯荤粺鍙傛暟")
    return await proxy_to_mall(f"/api/syspara/{key}")

@router.post("/syspara")
async def syspara_save(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "淇濆瓨绯荤粺鍙傛暟")
    return await proxy_to_mall("/admin/syspara", method="POST", json_data=data)

@router.put("/syspara/{sys_id}")
async def syspara_update(sys_id: int, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鏇存柊绯荤粺鍙傛暟")
    return await proxy_to_mall(f"/admin/syspara/{sys_id}", method="PUT", json_data=data)

@router.delete("/syspara/{sys_id}")
async def syspara_delete(sys_id: int, _=Depends(verify_token)):
    await handle_risk("L3", "鍒犻櫎绯荤粺鍙傛暟")
    return await proxy_to_mall(f"/admin/syspara/{sys_id}", method="DELETE")


# ============================================================
# 鍖哄煙绠＄悊 (AreaController)
# ============================================================

@router.get("/area/countries")
async def area_countries(_=Depends(verify_token), lang: str = "zh"):
    await handle_risk("L1", "鏌ョ湅鍥藉鍒楄〃")
    return await proxy_to_mall("/api/area/countries", params={"lang": lang})

@router.get("/area/states")
async def area_states(_=Depends(verify_token), country_id: int = None):
    await handle_risk("L1", "鏌ョ湅宸?鐪佸垪琛?)
    return await proxy_to_mall("/api/area/states", params={"countryId": country_id})

@router.get("/area/cities")
async def area_cities(_=Depends(verify_token), state_id: int = None):
    await handle_risk("L1", "鏌ョ湅鍩庡競鍒楄〃")
    return await proxy_to_mall("/api/area/cities", params={"stateId": state_id})

@router.get("/area/mobile-prefix")
async def area_mobile_prefix(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅鎵嬫満鍖哄彿")
    return await proxy_to_mall("/api/area/mobile-prefix")


# ============================================================
# 鍟嗗煄绛夌骇 (MallLevelController)
# ============================================================

@router.get("/malllevel/list")
async def malllevel_list(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅鍟嗗煄绛夌骇")
    return await proxy_to_mall("/api/malllevel/list")

@router.get("/malllevel/{uuid}")
async def malllevel_detail(uuid: str, _=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅绛夌骇璇︽儏")
    return await proxy_to_mall(f"/api/malllevel/{uuid}")

@router.get("/malllevel/config")
async def malllevel_config(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅绛夌骇閰嶇疆")
    return await proxy_to_mall("/api/malllevel/config")


# ============================================================
# 鑱婂ぉ/瀹㈡湇绠＄悊 (ChatController) 鈥?鍟嗗煄鍐呯疆瀹㈡湇
# ============================================================

@router.get("/chat/conversations")
async def chat_conversations(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅鑱婂ぉ浼氳瘽")
    return await proxy_to_mall("/api/chat/admin/conversations", params={"page": page, "pageSize": size})

@router.get("/chat/messages/{conversation_id}")
async def chat_messages(conversation_id: str, _=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅鑱婂ぉ娑堟伅")
    return await proxy_to_mall(f"/api/chat/admin/messages/{conversation_id}")

@router.get("/chat/admin/onechat")
async def chat_admin_onechat(_=Depends(verify_token), conversation_id: str = None):
    await handle_risk("L1", "鏌ョ湅鎸囧畾浼氳瘽")
    return await proxy_to_mall(f"/api/chat/admin/onechat?conversationId={conversation_id}")

@router.post("/chat/admin/reply")
async def chat_admin_reply(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "绠＄悊鍛樺洖澶?)
    return await proxy_to_mall("/api/chat/admin/reply", method="POST", json_data=data)

# ============================================================
# 韬唤璇佺鐞?(IdcodeController)
# ============================================================

@router.get("/idcodes")
async def idcode_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅韬唤璇佸垪琛?)
    return await proxy_to_mall("/api/idcode/list", params={"page": page, "size": size})


# ============================================================
# 濂楅绠＄悊 (ComboController)
# ============================================================

@router.get("/combos")
async def combo_list(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅濂楅鍒楄〃")
    return await proxy_to_mall("/api/combo/list")


# ============================================================
# 楠岃瘉鐮佺鐞?(GeetestController)
# ============================================================

@router.get("/geetest/config")
async def geetest_config(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅楠岃瘉鐮侀厤缃?)
    return await proxy_to_mall("/api/geetest/config")


# ============================================================
# Google璁よ瘉绠＄悊 (GoogleAuthController)
# ============================================================

@router.get("/google-auth/list")
async def google_auth_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅Google璁よ瘉鍒楄〃")
    return await proxy_to_mall("/api/google-auth/list", params={"page": page, "size": size})


# ============================================================
# 绠＄悊鍛樼鐞?(AdminController)
# ============================================================

@router.get("/admins")
async def admin_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "鏌ョ湅绠＄悊鍛樺垪琛?)
    return await proxy_to_mall("/api/admin/list", params={"page": page, "size": size})

@router.post("/admin")
async def admin_create(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鍒涘缓绠＄悊鍛?)
    return await proxy_to_mall("/api/admin", method="POST", json_data=data)

@router.put("/admin/{admin_id}")
async def admin_update(admin_id: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鏇存柊绠＄悊鍛?)
    return await proxy_to_mall(f"/api/admin/{admin_id}", method="PUT", json_data=data)


# ============================================================
# 鎵归噺鎿嶄綔
# ============================================================

@router.post("/batch/products/status")
async def batch_product_status(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", "鎵归噺鏇存柊鍟嗗搧鐘舵€?)
    return await proxy_to_mall("/api/product/batch/status", method="POST", json_data=data)

@router.post("/batch/orders/status")
async def batch_order_status(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", "鎵归噺鏇存柊璁㈠崟鐘舵€?)
    return await proxy_to_mall("/api/order/batch/status", method="POST", json_data=data)

@router.post("/batch/users/status")
async def batch_user_status(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", "鎵归噺鏇存柊鐢ㄦ埛鐘舵€?)
    return await proxy_to_mall("/api/user/batch/status", method="POST", json_data=data)

# ============================================================
# 灞炴€х鐞?(AgentController)
# ============================================================

@router.get("/attr-categories")
async def list_attr_categories(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅灞炴€у垎绫?)
    return await proxy_to_mall("/agent/attr-category/list")

@router.get("/attr-category/{uuid}")
async def get_attr_category(uuid: str, _=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅灞炴€у垎绫昏鎯?)
    return await proxy_to_mall(f"/agent/attr-category/{uuid}")

@router.post("/attr-category")
async def create_attr_category(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鍒涘缓灞炴€у垎绫?)
    return await proxy_to_mall("/agent/attr-category", method="POST", json_data=data)

@router.put("/attr-category/{uuid}")
async def update_attr_category(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鏇存柊灞炴€у垎绫?)
    return await proxy_to_mall(f"/agent/attr-category/{uuid}", method="PUT", json_data=data)

@router.delete("/attr-category/{uuid}")
async def delete_attr_category(uuid: str, _=Depends(verify_token)):
    await handle_risk("L2", "鍒犻櫎灞炴€у垎绫?)
    return await proxy_to_mall(f"/agent/attr-category/{uuid}", method="DELETE")

@router.get("/attrs")
async def list_attrs(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅灞炴€у垪琛?)
    return await proxy_to_mall("/agent/attr/list")

@router.get("/attr/{uuid}")
async def get_attr(uuid: str, _=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅灞炴€ц鎯?)
    return await proxy_to_mall(f"/agent/attr/{uuid}")

@router.post("/attr")
async def create_attr(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鍒涘缓灞炴€?)
    return await proxy_to_mall("/agent/attr", method="POST", json_data=data)

@router.put("/attr/{uuid}")
async def update_attr(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鏇存柊灞炴€?)
    return await proxy_to_mall(f"/agent/attr/{uuid}", method="PUT", json_data=data)

@router.delete("/attr/{uuid}")
async def delete_attr(uuid: str, _=Depends(verify_token)):
    await handle_risk("L2", "鍒犻櫎灞炴€?)
    return await proxy_to_mall(f"/agent/attr/{uuid}", method="DELETE")

@router.get("/attr-values")
async def list_attr_values(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅灞炴€у€煎垪琛?)
    return await proxy_to_mall("/agent/attr-value/list")

@router.get("/attr-value/{id}")
async def get_attr_value(id: int, _=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅灞炴€у€艰鎯?)
    return await proxy_to_mall(f"/agent/attr-value/{id}")

@router.post("/attr-value")
async def create_attr_value(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鍒涘缓灞炴€у€?)
    return await proxy_to_mall("/agent/attr-value", method="POST", json_data=data)

@router.put("/attr-value/{id}")
async def update_attr_value(id: int, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鏇存柊灞炴€у€?)
    return await proxy_to_mall(f"/agent/attr-value/{id}", method="PUT", json_data=data)

@router.delete("/attr-value/{id}")
async def delete_attr_value(id: int, _=Depends(verify_token)):
    await handle_risk("L2", "鍒犻櫎灞炴€у€?)
    return await proxy_to_mall(f"/agent/attr-value/{id}", method="DELETE")

# ============================================================
# 绉嶅瓙鏁版嵁 (AgentController)
# ============================================================

@router.post("/seed/products")
async def seed_products(_=Depends(verify_token)):
    await handle_risk("L3", "鐢熸垚绉嶅瓙鍟嗗搧鏁版嵁")
    return await proxy_to_mall("/agent/seed/products", method="POST")

@router.post("/seed/orders")
async def seed_orders(_=Depends(verify_token)):
    await handle_risk("L3", "鐢熸垚绉嶅瓙璁㈠崟鏁版嵁")
    return await proxy_to_mall("/agent/seed/orders", method="POST")

@router.post("/seed/users")
async def seed_users(_=Depends(verify_token)):
    await handle_risk("L3", "鐢熸垚绉嶅瓙鐢ㄦ埛鏁版嵁")
    return await proxy_to_mall("/agent/seed/users", method="POST")

@router.post("/seed/merchants")
async def seed_merchants(_=Depends(verify_token)):
    await handle_risk("L3", "鐢熸垚绉嶅瓙鍟嗗鏁版嵁")
    return await proxy_to_mall("/agent/seed/merchants", method="POST")

@router.post("/seed/comments")
async def seed_comments(_=Depends(verify_token)):
    await handle_risk("L3", "鐢熸垚绉嶅瓙璇勮鏁版嵁")
    return await proxy_to_mall("/agent/seed/comments", method="POST")

@router.post("/seed/clear")
async def seed_clear(_=Depends(verify_token)):
    await handle_risk("L4", "娓呴櫎鎵€鏈夌瀛愭暟鎹?)
    return await proxy_to_mall("/agent/seed/clear", method="DELETE")

# ============================================================
# 鏈湴璁㈠崟 (OrdersLocalController)
# ============================================================

@router.post("/order-local/submit")
async def submit_local_order(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鎻愪氦鏈湴璁㈠崟")
    return await proxy_to_mall("/api/order-local/submit", method="POST", json_data=data)

# ============================================================
# 鍟嗗鐗堟湰绠＄悊 (SellerVersionController)
# ============================================================

@router.post("/seller/version/client")
async def seller_version_client(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鍟嗗鐗堟湰瀹㈡埛绔?)
    return await proxy_to_mall("/seller/version/client", method="POST", json_data=data)

@router.post("/seller/version/register")
async def seller_version_register(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鍟嗗鐗堟湰娉ㄥ唽")
    return await proxy_to_mall("/seller/version/register", method="POST", json_data=data)

@router.post("/seller/version/register-js")
async def seller_version_register_js(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鍟嗗鐗堟湰JS娉ㄥ唽")
    return await proxy_to_mall("/seller/version/register-js", method="POST", json_data=data)

@router.post("/seller/version/update-sign-pdf")
async def seller_version_update_sign(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "鍟嗗鐗堟湰绛惧悕鏇存柊")
    return await proxy_to_mall("/seller/version/update-sign-pdf", method="POST", json_data=data)

# ============================================================
# 鍥剧墖涓婁紶绠＄悊 (UploadImgController)
# ============================================================

@router.get("/upload/list")
async def list_uploads(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅涓婁紶鍒楄〃")
    return await proxy_to_mall("/api/upload/list")

@router.get("/upload/files")
async def list_upload_files(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅涓婁紶鏂囦欢鍒楄〃")
    return await proxy_to_mall("/api/upload/list")

@router.delete("/upload/{id}")
async def delete_upload(id: int, _=Depends(verify_token)):
    await handle_risk("L2", "鍒犻櫎涓婁紶鏂囦欢")
    return await proxy_to_mall(f"/api/upload/{id}", method="DELETE")

# ============================================================
# Java绔疆鍊肩郴缁?(RotationController) 鈥?琛ュ厖AI绔疆鍊?# ============================================================

@router.get("/rotation/domains")
async def java_rotation_domains(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅Java杞€煎煙鍚?)
    return await proxy_to_mall("/api/rotation/domains")

@router.post("/rotation/block")
async def java_rotation_block(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "灏佺杞€煎煙鍚?)
    return await proxy_to_mall("/api/rotation/block", method="POST", json_data=data)

@router.post("/rotation/unblock")
async def java_rotation_unblock(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "瑙ｇ杞€煎煙鍚?)
    return await proxy_to_mall("/api/rotation/unblock", method="POST", json_data=data)

@router.get("/rotation/stats")
async def java_rotation_stats(_=Depends(verify_token)):
    await handle_risk("L1", "鏌ョ湅杞€肩粺璁?)
    return await proxy_to_mall("/api/rotation/stats")
