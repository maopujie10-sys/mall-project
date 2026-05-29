"""商城管理工具 — 全量代理 mall-app 后端全部 Controller
商品/订单/用户/分类/钱包/物流/KYC/投诉/合同/信用/借贷/评论/评价/地址/购物车/收藏/关注/邀请/抽奖/返利/促销/订阅/商家/轮播/新闻/通知/系统参数/区域/等级/聊天/轮值/身份证/套餐/客服"""
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
# 统计面板
# ============================================================

@router.get("/stats")
async def mall_stats(_=Depends(verify_token)):
    """商城统计数据"""
    await handle_risk("L1", "查看商城统计")
    return await proxy_to_mall("/api/dashboard/stats")


# ============================================================
# 商品管理 (ProductController)
# ============================================================

@router.get("/products")
async def list_products(_=Depends(verify_token), page: int = 1, size: int = 20, keyword: str = None, category_id: str = None):
    await handle_risk("L1", "查看商品列表")
    params = {"page": page, "size": size}
    if keyword: params["keyword"] = keyword
    if category_id: params["category_id"] = category_id
    return await proxy_to_mall("/api/products", params=params)

@router.get("/product/{uuid}")
async def product_detail(uuid: str, _=Depends(verify_token)):
    await handle_risk("L1", "查看商品详情")
    return await proxy_to_mall(f"/api/product/{uuid}")

@router.post("/product/audit")
async def audit_product(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", "审核商品")
    return await proxy_to_mall("/api/product/audit", method="POST", json_data=data)

@router.put("/product/{uuid}")
async def update_product(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "更新商品")
    return await proxy_to_mall(f"/api/product/{uuid}", method="PUT", json_data=data)

@router.delete("/product/{uuid}")
async def delete_product(uuid: str, _=Depends(verify_token)):
    await handle_risk("L3", "删除商品")
    return await proxy_to_mall(f"/api/product/{uuid}", method="DELETE")


# ============================================================
# 订单管理 (OrderController + OrderLogController + OrdersLocalController)
# ============================================================

@router.get("/orders")
async def list_orders(_=Depends(verify_token), page: int = 1, size: int = 20, status: str = None, keyword: str = None):
    await handle_risk("L1", "查看订单列表")
    params = {"page": page, "size": size}
    if status: params["status"] = status
    if keyword: params["keyword"] = keyword
    return await proxy_to_mall("/api/orders", params=params)

@router.get("/order/{order_id}")
async def order_detail(order_id: str, _=Depends(verify_token)):
    await handle_risk("L1", "查看订单详情")
    return await proxy_to_mall(f"/api/order/{order_id}")

@router.post("/order/refund/{order_id}")
async def force_refund_order(order_id: str, data: dict = None, _=Depends(verify_token)):
    """强制退款"""
    await handle_risk("L3", "强制退款", f"订单ID: {order_id}")
    return await proxy_to_mall(f"/api/order/refund/{order_id}", method="POST", json_data=data or {})

@router.get("/order/{order_id}/logs")
async def order_logs(order_id: str, _=Depends(verify_token)):
    """订单日志 (OrderLogController)"""
    await handle_risk("L1", "查看订单日志")
    return await proxy_to_mall(f"/api/order-log/{order_id}")


# ============================================================
# 用户管理 (UserController)
# ============================================================

@router.get("/users")
async def list_users(_=Depends(verify_token), page: int = 1, size: int = 20, keyword: str = None):
    await handle_risk("L1", "查看用户列表")
    params = {"page": page, "size": size}
    if keyword: params["keyword"] = keyword
    return await proxy_to_mall("/api/users", params=params)

@router.get("/user/{user_id}")
async def user_detail(user_id: str, _=Depends(verify_token)):
    await handle_risk("L1", "查看用户详情")
    return await proxy_to_mall(f"/api/user/{user_id}")

@router.post("/user/status")
async def update_user_status(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "更新用户状态")
    return await proxy_to_mall("/api/user/status", method="POST", json_data=data)

@router.post("/user/balance/adjust")
async def adjust_balance(data: dict, _=Depends(verify_token)):
    risk = await handle_risk("L3", "调整用户余额")
    if not risk.get("allowed", True): return risk
    return await proxy_to_mall("/api/user/balance", method="POST", json_data=data)

# ============================================================
# 分类管理 (Category CRUD)
# ============================================================

@router.get("/categories")
async def list_categories(_=Depends(verify_token)):
    await handle_risk("L1", "查看分类列表")
    return await proxy_to_mall("/api/categories")

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


# ============================================================
# 钱包管理 (WalletController)
# ============================================================

@router.get("/wallet/logs")
async def wallet_logs(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看钱包流水")
    return await proxy_to_mall("/api/wallet/logs", params={"page": page, "pageSize": size})

@router.get("/wallet/balance")
async def wallet_balance(_=Depends(verify_token)):
    await handle_risk("L1", "查看钱包余额")
    return await proxy_to_mall("/api/wallet/balance")


# ============================================================
# 充值管理 (RechargeController)
# ============================================================

@router.get("/recharge/pending")
async def recharge_pending(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看充值审核列表")
    return await proxy_to_mall("/api/recharge/pending", params={"page": page, "size": size})

@router.post("/recharge/audit")
async def audit_recharge(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", "审核充值")
    return await proxy_to_mall("/api/recharge/audit", method="POST", json_data=data)


# ============================================================
# 提现管理 (WithdrawController)
# ============================================================

@router.get("/withdraw/pending")
async def withdraw_pending(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看提现审核列表")
    return await proxy_to_mall("/api/withdraw/pending", params={"page": page, "size": size})

@router.post("/withdraw/audit")
async def audit_withdraw(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", "审核提现")
    return await proxy_to_mall("/api/withdraw/audit", method="POST", json_data=data)

# ============================================================
# 物流管理 (LogisticsController)
# ============================================================

@router.get("/logistics/{order_id}")
async def logistics_info(order_id: str, _=Depends(verify_token)):
    await handle_risk("L1", "查看物流信息")
    return await proxy_to_mall(f"/api/logistics/{order_id}")

@router.get("/logistics/{order_id}/trace")
async def logistics_trace(order_id: str, _=Depends(verify_token)):
    await handle_risk("L1", "查看物流轨迹")
    return await proxy_to_mall(f"/api/logistics/{order_id}/trace")


# ============================================================
# KYC 认证管理 (KycController + KycHighLevelController)
# ============================================================

@router.get("/kyc/list")
async def kyc_list(_=Depends(verify_token), page: int = 1, size: int = 20, status: int = None):
    await handle_risk("L1", "查看KYC列表")
    params = {"pageNum": page, "pageSize": size}
    if status is not None: params["status"] = status
    return await proxy_to_mall("/admin/kyc/list", params=params)

@router.post("/kyc/audit/{kyc_id}")
async def kyc_audit(kyc_id: int, data: dict, _=Depends(verify_token)):
    await handle_risk("L3", "审核KYC")
    return await proxy_to_mall(f"/admin/kyc/audit/{kyc_id}", method="POST", json_data=data)

@router.get("/kyc-high-level")
async def kyc_high_level(_=Depends(verify_token)):
    await handle_risk("L1", "查看高级KYC")
    return await proxy_to_mall("/api/kyc-high-level")


# ============================================================
# 投诉管理 (ComplaintController)
# ============================================================

@router.get("/complaints")
async def complaint_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看投诉列表")
    return await proxy_to_mall("/api/complaint/list", params={"pageNum": page, "pageSize": size})

@router.post("/complaint/handle/{uuid}")
async def complaint_handle(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "处理投诉")
    return await proxy_to_mall(f"/api/complaint/handle/{uuid}", method="POST", json_data=data)


# ============================================================
# 合同管理 (ContractController)
# ============================================================

@router.get("/contract/info")
async def contract_info(_=Depends(verify_token)):
    await handle_risk("L1", "查看合同信息")
    return await proxy_to_mall("/api/contract/info")

@router.get("/contract/list")
async def contract_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看合同列表")
    return await proxy_to_mall("/api/contract/list", params={"page": page, "size": size})


# ============================================================
# 信用管理 (CreditController)
# ============================================================

@router.get("/credits")
async def credit_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看信用列表")
    return await proxy_to_mall("/api/credit/list", params={"page": page, "size": size})

# ============================================================
# 借贷管理 (LoanController)
# ============================================================

@router.get("/loan/admin/list")
async def loan_admin_list(_=Depends(verify_token), page: int = 1, size: int = 20, keyword: str = None, status: int = None):
    await handle_risk("L1", "查看借贷列表")
    params = {"page": page, "pageSize": size}
    if keyword: params["keyword"] = keyword
    if status is not None: params["status"] = status
    return await proxy_to_mall("/api/loan/admin/list", params=params)

@router.post("/loan/admin/audit")
async def loan_audit(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", "审核借贷")
    return await proxy_to_mall("/api/loan/admin/audit", method="POST", json_data=data)

@router.get("/loan/config")
async def loan_config(_=Depends(verify_token)):
    await handle_risk("L1", "查看借贷配置")
    return await proxy_to_mall("/api/loan/config")

@router.get("/loan/admin/configs")
async def loan_configs(_=Depends(verify_token)):
    await handle_risk("L1", "查看借贷配置列表")
    return await proxy_to_mall("/api/loan/admin/configs")


# ============================================================
# 评论管理 (CommentController)
# ============================================================

@router.get("/comments/{good_id}")
async def comment_list(good_id: str, _=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看商品评论")
    return await proxy_to_mall(f"/api/comment/list/{good_id}", params={"page": page, "pageSize": size})

@router.delete("/comment/{uuid}")
async def comment_delete(uuid: str, _=Depends(verify_token)):
    await handle_risk("L3", "删除评论")
    return await proxy_to_mall(f"/api/comment/{uuid}", method="DELETE")


# ============================================================
# 评价管理 (EvaluationController)
# ============================================================

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


# ============================================================
# 地址管理 (AddressController)
# ============================================================

@router.get("/addresses")
async def address_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看地址列表")
    return await proxy_to_mall("/api/address/list", params={"page": page, "size": size})


# ============================================================
# 购物车管理 (CartController)
# ============================================================

@router.get("/carts")
async def cart_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看购物车列表")
    return await proxy_to_mall("/api/cart/list", params={"page": page, "size": size})

# ============================================================
# 收藏管理 (KeepGoodsController)
# ============================================================

@router.get("/keep-goods")
async def keep_goods_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看收藏列表")
    return await proxy_to_mall("/api/keep-goods/list", params={"page": page, "pageSize": size})


# ============================================================
# 关注管理 (FocusSellerController)
# ============================================================

@router.get("/focus-sellers")
async def focus_seller_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看关注商家列表")
    return await proxy_to_mall("/api/focus-seller/list", params={"page": page, "pageSize": size})


# ============================================================
# 邀请管理 (InviteController)
# ============================================================

@router.get("/invites")
async def invite_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看邀请列表")
    return await proxy_to_mall("/api/invite/list", params={"page": page, "size": size})

@router.get("/invite/stats")
async def invite_stats(_=Depends(verify_token)):
    await handle_risk("L1", "查看邀请统计")
    return await proxy_to_mall("/api/invite/stats")


# ============================================================
# 抽奖管理 (LotteryController)
# ============================================================

@router.get("/lottery/current")
async def lottery_current(_=Depends(verify_token)):
    await handle_risk("L1", "查看当前抽奖活动")
    return await proxy_to_mall("/api/promote/lottery/current")

@router.get("/lottery/{activity_id}")
async def lottery_detail(activity_id: str, _=Depends(verify_token)):
    await handle_risk("L1", "查看抽奖详情")
    return await proxy_to_mall(f"/api/promote/lottery?activityId={activity_id}")


# ============================================================
# 返利管理 (RebateController)
# ============================================================

@router.get("/rebates")
async def rebate_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看返利列表")
    return await proxy_to_mall("/api/rebate/list", params={"page": page, "pageSize": size})

@router.get("/rebate/stats")
async def rebate_stats(_=Depends(verify_token)):
    await handle_risk("L1", "查看返利统计")
    return await proxy_to_mall("/api/rebate/stats")


# ============================================================
# 促销管理 (PromoteController)
# ============================================================

@router.get("/promotes")
async def promote_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看促销列表")
    return await proxy_to_mall("/api/promote/list", params={"page": page, "size": size})

@router.get("/promote/config")
async def promote_config(_=Depends(verify_token)):
    await handle_risk("L1", "查看促销配置")
    return await proxy_to_mall("/api/promote/config")


# ============================================================
# 订阅管理 (SubscribeController)
# ============================================================

@router.get("/subscribes")
async def subscribe_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看订阅列表")
    return await proxy_to_mall("/api/subscribe/list", params={"page": page, "size": size})

# ============================================================
# 商家管理 (MerchantController + SellerController + SellerPromotionalController + SellerVersionController)
# ============================================================

@router.get("/merchant/list")
async def merchant_list(_=Depends(verify_token), page: int = 1, size: int = 20, keyword: str = None, status: str = None):
    await handle_risk("L1", "查看商家列表")
    params = {"page": page, "size": size}
    if keyword: params["keyword"] = keyword
    if status: params["status"] = status
    return await proxy_to_mall("/api/merchant/list", params=params)

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

@router.get("/seller/list")
async def seller_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看卖家列表")
    return await proxy_to_mall("/api/seller/list", params={"page": page, "size": size})

@router.get("/seller/promotional")
async def seller_promotional(_=Depends(verify_token)):
    await handle_risk("L1", "查看卖家推广")
    return await proxy_to_mall("/api/seller/promotional")


# ============================================================
# 商家仪表盘 (MerchantDashboardController)
# ============================================================

@router.get("/merchant/dashboard")
async def merchant_dashboard(_=Depends(verify_token)):
    await handle_risk("L1", "查看商家仪表盘")
    return await proxy_to_mall("/merchant/instrument-panel/head")


# ============================================================
# 商家财务 (MerchantFinanceController)
# ============================================================

@router.get("/merchant/finance")
async def merchant_finance(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看商家财务")
    return await proxy_to_mall("/merchant/finance/list", params={"page": page, "size": size})


# ============================================================
# 商家商品 (MerchantGoodsController)
# ============================================================

@router.get("/merchant/goods")
async def merchant_goods(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看商家商品")
    return await proxy_to_mall("/merchant/goods/list", params={"page": page, "size": size})


# ============================================================
# 商家订单 (MerchantOrderController)
# ============================================================

@router.get("/merchant/orders")
async def merchant_orders(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看商家订单")
    return await proxy_to_mall("/merchant/order/list", params={"page": page, "size": size})


# ============================================================
# 商家评价 (MerchantEvaluationController)
# ============================================================

@router.get("/merchant/evaluations")
async def merchant_evaluations(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看商家评价")
    return await proxy_to_mall("/merchant/evaluation/list", params={"page": page, "size": size})

# ============================================================
# 轮播图管理 (BannerController)
# ============================================================

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


# ============================================================
# 新闻管理 (NewsController)
# ============================================================

@router.get("/news/list")
async def news_list(_=Depends(verify_token), page: int = 1, size: int = 20, lang: str = None):
    await handle_risk("L1", "查看新闻列表")
    params = {"pageNum": page, "pageSize": size}
    if lang: params["lang"] = lang
    return await proxy_to_mall("/api/news/list", params=params)

@router.get("/news/{news_id}")
async def news_detail(news_id: int, _=Depends(verify_token)):
    await handle_risk("L1", "查看新闻详情")
    return await proxy_to_mall(f"/api/news/{news_id}")

@router.post("/news")
async def news_create(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "创建新闻")
    return await proxy_to_mall("/api/news", method="POST", json_data=data)

@router.put("/news/{news_id}")
async def news_update(news_id: int, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "更新新闻")
    return await proxy_to_mall(f"/api/news/{news_id}", method="PUT", json_data=data)

@router.delete("/news/{news_id}")
async def news_delete(news_id: int, _=Depends(verify_token)):
    await handle_risk("L3", "删除新闻")
    return await proxy_to_mall(f"/api/news/{news_id}", method="DELETE")


# ============================================================
# 通知管理 (NotificationController)
# ============================================================

@router.get("/notifications")
async def notification_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看通知列表")
    return await proxy_to_mall("/api/notification/list", params={"page": page, "size": size})

@router.post("/notification")
async def notification_create(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "创建通知")
    return await proxy_to_mall("/api/notification", method="POST", json_data=data)

# ============================================================
# 系统参数 (SysParamController)
# ============================================================

@router.get("/syspara/list")
async def syspara_list(_=Depends(verify_token)):
    await handle_risk("L1", "查看系统参数")
    return await proxy_to_mall("/admin/syspara/list")

@router.get("/syspara/{key}")
async def syspara_get(key: str, _=Depends(verify_token)):
    await handle_risk("L1", "查看系统参数")
    return await proxy_to_mall(f"/api/syspara/{key}")

@router.post("/syspara")
async def syspara_save(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "保存系统参数")
    return await proxy_to_mall("/admin/syspara", method="POST", json_data=data)

@router.put("/syspara/{sys_id}")
async def syspara_update(sys_id: int, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "更新系统参数")
    return await proxy_to_mall(f"/admin/syspara/{sys_id}", method="PUT", json_data=data)

@router.delete("/syspara/{sys_id}")
async def syspara_delete(sys_id: int, _=Depends(verify_token)):
    await handle_risk("L3", "删除系统参数")
    return await proxy_to_mall(f"/admin/syspara/{sys_id}", method="DELETE")


# ============================================================
# 区域管理 (AreaController)
# ============================================================

@router.get("/area/countries")
async def area_countries(_=Depends(verify_token), lang: str = "zh"):
    await handle_risk("L1", "查看国家列表")
    return await proxy_to_mall("/api/area/countries", params={"lang": lang})

@router.get("/area/states")
async def area_states(_=Depends(verify_token), country_id: int = None):
    await handle_risk("L1", "查看州/省列表")
    return await proxy_to_mall("/api/area/states", params={"countryId": country_id})

@router.get("/area/cities")
async def area_cities(_=Depends(verify_token), state_id: int = None):
    await handle_risk("L1", "查看城市列表")
    return await proxy_to_mall("/api/area/cities", params={"stateId": state_id})

@router.get("/area/mobile-prefix")
async def area_mobile_prefix(_=Depends(verify_token)):
    await handle_risk("L1", "查看手机区号")
    return await proxy_to_mall("/api/area/mobile-prefix")


# ============================================================
# 商城等级 (MallLevelController)
# ============================================================

@router.get("/malllevel/list")
async def malllevel_list(_=Depends(verify_token)):
    await handle_risk("L1", "查看商城等级")
    return await proxy_to_mall("/api/malllevel/list")

@router.get("/malllevel/{uuid}")
async def malllevel_detail(uuid: str, _=Depends(verify_token)):
    await handle_risk("L1", "查看等级详情")
    return await proxy_to_mall(f"/api/malllevel/{uuid}")

@router.get("/malllevel/config")
async def malllevel_config(_=Depends(verify_token)):
    await handle_risk("L1", "查看等级配置")
    return await proxy_to_mall("/api/malllevel/config")


# ============================================================
# 聊天/客服管理 (ChatController) — 商城内置客服
# ============================================================

@router.get("/chat/conversations")
async def chat_conversations(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看聊天会话")
    return await proxy_to_mall("/api/chat/admin/conversations", params={"page": page, "pageSize": size})

@router.get("/chat/messages/{conversation_id}")
async def chat_messages(conversation_id: str, _=Depends(verify_token)):
    await handle_risk("L1", "查看聊天消息")
    return await proxy_to_mall(f"/api/chat/admin/messages/{conversation_id}")

@router.get("/chat/admin/onechat")
async def chat_admin_onechat(_=Depends(verify_token), conversation_id: str = None):
    await handle_risk("L1", "查看指定会话")
    return await proxy_to_mall(f"/api/chat/admin/onechat?conversationId={conversation_id}")

@router.post("/chat/admin/reply")
async def chat_admin_reply(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "管理员回复")
    return await proxy_to_mall("/api/chat/admin/reply", method="POST", json_data=data)

# ============================================================
# 身份证管理 (IdcodeController)
# ============================================================

@router.get("/idcodes")
async def idcode_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看身份证列表")
    return await proxy_to_mall("/api/idcode/list", params={"page": page, "size": size})


# ============================================================
# 套餐管理 (ComboController)
# ============================================================

@router.get("/combos")
async def combo_list(_=Depends(verify_token)):
    await handle_risk("L1", "查看套餐列表")
    return await proxy_to_mall("/api/combo/list")


# ============================================================
# 验证码管理 (GeetestController)
# ============================================================

@router.get("/geetest/config")
async def geetest_config(_=Depends(verify_token)):
    await handle_risk("L1", "查看验证码配置")
    return await proxy_to_mall("/api/geetest/config")


# ============================================================
# Google认证管理 (GoogleAuthController)
# ============================================================

@router.get("/google-auth/list")
async def google_auth_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看Google认证列表")
    return await proxy_to_mall("/api/google-auth/list", params={"page": page, "size": size})


# ============================================================
# 管理员管理 (AdminController)
# ============================================================

@router.get("/admins")
async def admin_list(_=Depends(verify_token), page: int = 1, size: int = 20):
    await handle_risk("L1", "查看管理员列表")
    return await proxy_to_mall("/api/admin/list", params={"page": page, "size": size})

@router.post("/admin")
async def admin_create(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "创建管理员")
    return await proxy_to_mall("/api/admin", method="POST", json_data=data)

@router.put("/admin/{admin_id}")
async def admin_update(admin_id: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "更新管理员")
    return await proxy_to_mall(f"/api/admin/{admin_id}", method="PUT", json_data=data)


# ============================================================
# 批量操作
# ============================================================

@router.post("/batch/products/status")
async def batch_product_status(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", "批量更新商品状态")
    return await proxy_to_mall("/api/product/batch/status", method="POST", json_data=data)

@router.post("/batch/orders/status")
async def batch_order_status(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", "批量更新订单状态")
    return await proxy_to_mall("/api/order/batch/status", method="POST", json_data=data)

@router.post("/batch/users/status")
async def batch_user_status(data: dict, _=Depends(verify_token)):
    await handle_risk("L3", "批量更新用户状态")
    return await proxy_to_mall("/api/user/batch/status", method="POST", json_data=data)

# ============================================================
# 属性管理 (AgentController)
# ============================================================

@router.get("/attr-categories")
async def list_attr_categories(_=Depends(verify_token)):
    await handle_risk("L1", "查看属性分类")
    return await proxy_to_mall("/agent/attr-category/list")

@router.get("/attr-category/{uuid}")
async def get_attr_category(uuid: str, _=Depends(verify_token)):
    await handle_risk("L1", "查看属性分类详情")
    return await proxy_to_mall(f"/agent/attr-category/{uuid}")

@router.post("/attr-category")
async def create_attr_category(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "创建属性分类")
    return await proxy_to_mall("/agent/attr-category", method="POST", json_data=data)

@router.put("/attr-category/{uuid}")
async def update_attr_category(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "更新属性分类")
    return await proxy_to_mall(f"/agent/attr-category/{uuid}", method="PUT", json_data=data)

@router.delete("/attr-category/{uuid}")
async def delete_attr_category(uuid: str, _=Depends(verify_token)):
    await handle_risk("L2", "删除属性分类")
    return await proxy_to_mall(f"/agent/attr-category/{uuid}", method="DELETE")

@router.get("/attrs")
async def list_attrs(_=Depends(verify_token)):
    await handle_risk("L1", "查看属性列表")
    return await proxy_to_mall("/agent/attr/list")

@router.get("/attr/{uuid}")
async def get_attr(uuid: str, _=Depends(verify_token)):
    await handle_risk("L1", "查看属性详情")
    return await proxy_to_mall(f"/agent/attr/{uuid}")

@router.post("/attr")
async def create_attr(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "创建属性")
    return await proxy_to_mall("/agent/attr", method="POST", json_data=data)

@router.put("/attr/{uuid}")
async def update_attr(uuid: str, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "更新属性")
    return await proxy_to_mall(f"/agent/attr/{uuid}", method="PUT", json_data=data)

@router.delete("/attr/{uuid}")
async def delete_attr(uuid: str, _=Depends(verify_token)):
    await handle_risk("L2", "删除属性")
    return await proxy_to_mall(f"/agent/attr/{uuid}", method="DELETE")

@router.get("/attr-values")
async def list_attr_values(_=Depends(verify_token)):
    await handle_risk("L1", "查看属性值列表")
    return await proxy_to_mall("/agent/attr-value/list")

@router.get("/attr-value/{id}")
async def get_attr_value(id: int, _=Depends(verify_token)):
    await handle_risk("L1", "查看属性值详情")
    return await proxy_to_mall(f"/agent/attr-value/{id}")

@router.post("/attr-value")
async def create_attr_value(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "创建属性值")
    return await proxy_to_mall("/agent/attr-value", method="POST", json_data=data)

@router.put("/attr-value/{id}")
async def update_attr_value(id: int, data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "更新属性值")
    return await proxy_to_mall(f"/agent/attr-value/{id}", method="PUT", json_data=data)

@router.delete("/attr-value/{id}")
async def delete_attr_value(id: int, _=Depends(verify_token)):
    await handle_risk("L2", "删除属性值")
    return await proxy_to_mall(f"/agent/attr-value/{id}", method="DELETE")

# ============================================================
# 种子数据 (AgentController)
# ============================================================

@router.post("/seed/products")
async def seed_products(_=Depends(verify_token)):
    await handle_risk("L3", "生成种子商品数据")
    return await proxy_to_mall("/agent/seed/products", method="POST")

@router.post("/seed/orders")
async def seed_orders(_=Depends(verify_token)):
    await handle_risk("L3", "生成种子订单数据")
    return await proxy_to_mall("/agent/seed/orders", method="POST")

@router.post("/seed/users")
async def seed_users(_=Depends(verify_token)):
    await handle_risk("L3", "生成种子用户数据")
    return await proxy_to_mall("/agent/seed/users", method="POST")

@router.post("/seed/merchants")
async def seed_merchants(_=Depends(verify_token)):
    await handle_risk("L3", "生成种子商家数据")
    return await proxy_to_mall("/agent/seed/merchants", method="POST")

@router.post("/seed/comments")
async def seed_comments(_=Depends(verify_token)):
    await handle_risk("L3", "生成种子评论数据")
    return await proxy_to_mall("/agent/seed/comments", method="POST")

@router.post("/seed/clear")
async def seed_clear(_=Depends(verify_token)):
    await handle_risk("L4", "清除所有种子数据")
    return await proxy_to_mall("/agent/seed/clear", method="DELETE")

# ============================================================
# 本地订单 (OrdersLocalController)
# ============================================================

@router.post("/order-local/submit")
async def submit_local_order(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "提交本地订单")
    return await proxy_to_mall("/api/order-local/submit", method="POST", json_data=data)

# ============================================================
# 商家版本管理 (SellerVersionController)
# ============================================================

@router.post("/seller/version/client")
async def seller_version_client(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "商家版本客户端")
    return await proxy_to_mall("/seller/version/client", method="POST", json_data=data)

@router.post("/seller/version/register")
async def seller_version_register(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "商家版本注册")
    return await proxy_to_mall("/seller/version/register", method="POST", json_data=data)

@router.post("/seller/version/register-js")
async def seller_version_register_js(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "商家版本JS注册")
    return await proxy_to_mall("/seller/version/register-js", method="POST", json_data=data)

@router.post("/seller/version/update-sign-pdf")
async def seller_version_update_sign(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "商家版本签名更新")
    return await proxy_to_mall("/seller/version/update-sign-pdf", method="POST", json_data=data)

# ============================================================
# 图片上传管理 (UploadImgController)
# ============================================================

@router.get("/upload/list")
async def list_uploads(_=Depends(verify_token)):
    await handle_risk("L1", "查看上传列表")
    return await proxy_to_mall("/api/upload/list")

@router.get("/upload/files")
async def list_upload_files(_=Depends(verify_token)):
    await handle_risk("L1", "查看上传文件列表")
    return await proxy_to_mall("/api/upload/list")

@router.delete("/upload/{id}")
async def delete_upload(id: int, _=Depends(verify_token)):
    await handle_risk("L2", "删除上传文件")
    return await proxy_to_mall(f"/api/upload/{id}", method="DELETE")

# ============================================================
# Java端轮值系统 (RotationController) — 补充AI端轮值
# ============================================================

@router.get("/rotation/domains")
async def java_rotation_domains(_=Depends(verify_token)):
    await handle_risk("L1", "查看Java轮值域名")
    return await proxy_to_mall("/api/rotation/domains")

@router.post("/rotation/block")
async def java_rotation_block(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "封禁轮值域名")
    return await proxy_to_mall("/api/rotation/block", method="POST", json_data=data)

@router.post("/rotation/unblock")
async def java_rotation_unblock(data: dict, _=Depends(verify_token)):
    await handle_risk("L2", "解禁轮值域名")
    return await proxy_to_mall("/api/rotation/unblock", method="POST", json_data=data)

@router.get("/rotation/stats")
async def java_rotation_stats(_=Depends(verify_token)):
    await handle_risk("L1", "查看轮值统计")
    return await proxy_to_mall("/api/rotation/stats")
