import { agentApi } from './index'

// ===== 统计面板 =====
export function getMallStatus() { return agentApi.get('/tools/mall/stats') }

// ===== 商品管理 =====
export function getProductList(params) { return agentApi.get('/tools/mall/products', { params }) }
export function getProductDetail(uuid) { return agentApi.get(`/tools/mall/product/${uuid}`) }
export function auditProduct(data) { return agentApi.post('/tools/mall/product/audit', data) }
export function updateProduct(uuid, data) { return agentApi.put(`/tools/mall/product/${uuid}`, data) }
export function deleteProduct(uuid) { return agentApi.delete(`/tools/mall/product/${uuid}`) }

// ===== 订单管理 =====
export function getOrderList(params) { return agentApi.get('/tools/mall/orders', { params }) }
export function getOrderDetail(orderId) { return agentApi.get(`/tools/mall/order/${orderId}`) }
export function forceRefund(orderId, data) { return agentApi.post(`/tools/mall/order/refund/${orderId}`, data) }
export function getOrderLogs(orderId) { return agentApi.get(`/tools/mall/order/${orderId}/logs`) }

// ===== 用户管理 =====
export function getUserList(params) { return agentApi.get('/tools/mall/users', { params }) }
export function getUserDetail(userId) { return agentApi.get(`/tools/mall/user/${userId}`) }
export function updateUserStatus(data) { return agentApi.post('/tools/mall/user/status', data) }
export function adjustUserBalance(data) { return agentApi.post('/tools/mall/user/balance/adjust', data) }

// ===== 分类管理 =====
export function getCategoryList(params) { return agentApi.get('/tools/mall/category/list', { params }) }
export function getCategoryAll() { return agentApi.get('/tools/mall/category/all') }
export function getCategory(uuid) { return agentApi.get(`/tools/mall/category/${uuid}`) }
export function saveCategory(data) { return agentApi.post('/tools/mall/category', data) }
export function updateCategory(uuid, data) { return agentApi.put(`/tools/mall/category/${uuid}`, data) }
export function updateCategoryStatus(uuid, data) { return agentApi.put(`/tools/mall/category/${uuid}/status`, data) }
export function deleteCategory(uuid) { return agentApi.delete(`/tools/mall/category/${uuid}`) }

// ===== 钱包管理 =====
export function getWalletLogs(params) { return agentApi.get('/tools/mall/wallet/logs', { params }) }
export function getWalletBalance(userId) { return agentApi.get('/tools/mall/wallet/balance') }

// ===== 充值审核 =====
export function getRechargePending(params) { return agentApi.get('/tools/mall/recharge/pending', { params }) }
export function auditRecharge(data) { return agentApi.post('/tools/mall/recharge/audit', data) }

// ===== 提现审核 =====
export function getWithdrawPending(params) { return agentApi.get('/tools/mall/withdraw/pending', { params }) }
export function auditWithdraw(data) { return agentApi.post('/tools/mall/withdraw/audit', data) }

// ===== 物流管理 =====
export function getLogisticsInfo(orderId) { return agentApi.get(`/tools/mall/logistics/${orderId}`) }
export function getLogisticsTrace(orderId) { return agentApi.get(`/tools/mall/logistics/${orderId}/trace`) }

// ===== KYC认证 =====
export function getKycList(params) { return agentApi.get('/tools/mall/kyc/list', { params }) }
export function auditKyc(kycId, data) { return agentApi.post(`/tools/mall/kyc/audit/${kycId}`, data) }
export function getKycHighLevel() { return agentApi.get('/tools/mall/kyc-high-level') }

// ===== 投诉管理 =====
export function getComplaintList(params) { return agentApi.get('/tools/mall/complaints', { params }) }
export function handleComplaint(uuid, data) { return agentApi.post(`/tools/mall/complaint/handle/${uuid}`, data) }

// ===== 合同管理 =====
export function getContractInfo() { return agentApi.get('/tools/mall/contract/info') }
export function getContractList(params) { return agentApi.get('/tools/mall/contract/list', { params }) }

// ===== 信用管理 =====
export function getCreditList(params) { return agentApi.get('/tools/mall/credits', { params }) }

// ===== 借贷管理 =====
export function getLoanList(params) { return agentApi.get('/tools/mall/loan/admin/list', { params }) }
export function auditLoan(data) { return agentApi.post('/tools/mall/loan/admin/audit', data) }
export function getLoanConfig() { return agentApi.get('/tools/mall/loan/config') }
export function getLoanConfigs() { return agentApi.get('/tools/mall/loan/admin/configs') }

// ===== 评论管理 =====
export function getCommentList(goodId, params) { return agentApi.get(`/tools/mall/comments/${goodId}`, { params }) }
export function deleteComment(uuid) { return agentApi.delete(`/tools/mall/comment/${uuid}`) }

// ===== 评价管理 =====
export function getEvaluationList(params) { return agentApi.get('/tools/mall/evaluations', { params }) }
export function updateEvaluationStatus(uuid, data) { return agentApi.put(`/tools/mall/evaluation/${uuid}/status`, data) }
export function deleteEvaluation(uuid) { return agentApi.delete(`/tools/mall/evaluation/${uuid}`) }

// ===== 地址管理 =====
export function getAddressList(params) { return agentApi.get('/tools/mall/addresses', { params }) }

// ===== 购物车管理 =====
export function getCartList(params) { return agentApi.get('/tools/mall/carts', { params }) }

// ===== 收藏管理 =====
export function getKeepGoodsList(params) { return agentApi.get('/tools/mall/keep-goods', { params }) }

// ===== 关注管理 =====
export function getFocusSellerList(params) { return agentApi.get('/tools/mall/focus-sellers', { params }) }

// ===== 邀请管理 =====
export function getInviteList(params) { return agentApi.get('/tools/mall/invites', { params }) }
export function getInviteStats() { return agentApi.get('/tools/mall/invite/stats') }

// ===== 抽奖管理 =====
export function getLotteryCurrent() { return agentApi.get('/tools/mall/lottery/current') }
export function getLotteryDetail(activityId) { return agentApi.get(`/tools/mall/lottery/${activityId}`) }

// ===== 返利管理 =====
export function getRebateList(params) { return agentApi.get('/tools/mall/rebates', { params }) }
export function getRebateStats() { return agentApi.get('/tools/mall/rebate/stats') }

// ===== 促销管理 =====
export function getPromoteList(params) { return agentApi.get('/tools/mall/promotes', { params }) }
export function getPromoteConfig() { return agentApi.get('/tools/mall/promote/config') }

// ===== 订阅管理 =====
export function getSubscribeList(params) { return agentApi.get('/tools/mall/subscribes', { params }) }
// ===== 商家管理 =====
export function getMerchantList(params) { return agentApi.get('/tools/mall/merchant/list', { params }) }
export function updateMerchantStatus(data) { return agentApi.post('/tools/mall/merchant/status', data) }
export function getMerchantApplyList(params) { return agentApi.get('/tools/mall/merchant/apply/list', { params }) }
export function auditMerchantApply(data) { return agentApi.post('/tools/mall/merchant/apply/audit', data) }
export function getSellerList(params) { return agentApi.get('/tools/mall/seller/list', { params }) }
export function getSellerPromotional() { return agentApi.get('/tools/mall/seller/promotional') }

// ===== 商家仪表盘 =====
export function getMerchantDashboard() { return agentApi.get('/tools/mall/merchant/dashboard') }

// ===== 商家财务 =====
export function getMerchantFinance(params) { return agentApi.get('/tools/mall/merchant/finance', { params }) }

// ===== 商家商品 =====
export function getMerchantGoods(params) { return agentApi.get('/tools/mall/merchant/goods', { params }) }

// ===== 商家订单 =====
export function getMerchantOrders(params) { return agentApi.get('/tools/mall/merchant/orders', { params }) }

// ===== 商家评价 =====
export function getMerchantEvaluations(params) { return agentApi.get('/tools/mall/merchant/evaluations', { params }) }

// ===== 轮播图管理 =====
export function getBannerList(params) { return agentApi.get('/tools/mall/banners', { params }) }
export function getBanner(uuid) { return agentApi.get(`/tools/mall/banner/${uuid}`) }
export function saveBanner(data) { return agentApi.post('/tools/mall/banner', data) }
export function updateBanner(uuid, data) { return agentApi.put(`/tools/mall/banner/${uuid}`, data) }
export function deleteBanner(uuid) { return agentApi.delete(`/tools/mall/banner/${uuid}`) }

// ===== 新闻管理 =====
export function getNewsList(params) { return agentApi.get('/tools/mall/news/list', { params }) }
export function getNewsDetail(newsId) { return agentApi.get(`/tools/mall/news/${newsId}`) }
export function saveNews(data) { return agentApi.post('/tools/mall/news', data) }
export function updateNews(newsId, data) { return agentApi.put(`/tools/mall/news/${newsId}`, data) }
export function deleteNews(newsId) { return agentApi.delete(`/tools/mall/news/${newsId}`) }

// ===== 通知管理 =====
export function getNotificationList(params) { return agentApi.get('/tools/mall/notifications', { params }) }
export function saveNotification(data) { return agentApi.post('/tools/mall/notification', data) }

// ===== 系统参数 =====
export function getSysparaList() { return agentApi.get('/tools/mall/syspara/list') }
export function getSyspara(key) { return agentApi.get(`/tools/mall/syspara/${key}`) }
export function saveSyspara(data) { return agentApi.post('/tools/mall/syspara', data) }
export function updateSyspara(sysId, data) { return agentApi.put(`/tools/mall/syspara/${sysId}`, data) }
export function deleteSyspara(sysId) { return agentApi.delete(`/tools/mall/syspara/${sysId}`) }

// ===== 区域管理 =====
export function getAreaCountries(lang) { return agentApi.get('/tools/mall/area/countries', { params: { lang } }) }
export function getAreaStates(countryId) { return agentApi.get('/tools/mall/area/states', { params: { country_id: countryId } }) }
export function getAreaCities(stateId) { return agentApi.get('/tools/mall/area/cities', { params: { state_id: stateId } }) }
export function getAreaMobilePrefix() { return agentApi.get('/tools/mall/area/mobile-prefix') }

// ===== 商城等级 =====
export function getMallLevelList() { return agentApi.get('/tools/mall/malllevel/list') }
export function getMallLevelDetail(uuid) { return agentApi.get(`/tools/mall/malllevel/${uuid}`) }
export function getMallLevelConfig() { return agentApi.get('/tools/mall/malllevel/config') }

// ===== 客服/聊天管理 =====
export function getChatConversations(params) { return agentApi.get('/tools/mall/chat/conversations', { params }) }
export function getChatMessages(conversationId) { return agentApi.get(`/tools/mall/chat/messages/${conversationId}`) }
export function getChatAdminOnechat(conversationId) { return agentApi.get('/tools/mall/chat/admin/onechat', { params: { conversation_id: conversationId } }) }
export function chatAdminReply(data) { return agentApi.post('/tools/mall/chat/admin/reply', data) }

// ===== 域名轮值 =====
export function getRotationDomains() { return agentApi.get('/tools/mall/rotation/domains') }
export function getRotationStats() { return agentApi.get('/tools/mall/rotation/stats') }
export function blockDomain(data) { return agentApi.post('/tools/mall/rotation/block', data) }
export function unblockDomain(data) { return agentApi.post('/tools/mall/rotation/unblock', data) }

// ===== 身份证管理 =====
export function getIdcodeList(params) { return agentApi.get('/tools/mall/idcodes', { params }) }

// ===== 套餐管理 =====
export function getComboList() { return agentApi.get('/tools/mall/combos') }

// ===== Google认证 =====
export function getGoogleAuthList(params) { return agentApi.get('/tools/mall/google-auth/list', { params }) }

// ===== 管理员管理 =====
export function getAdminList(params) { return agentApi.get('/tools/mall/admins', { params }) }
export function saveAdmin(data) { return agentApi.post('/tools/mall/admin', data) }
export function updateAdmin(adminId, data) { return agentApi.put(`/tools/mall/admin/${adminId}`, data) }

// ===== 批量操作 =====
export function batchProductStatus(data) { return agentApi.post('/tools/mall/batch/products/status', data) }
export function batchOrderStatus(data) { return agentApi.post('/tools/mall/batch/orders/status', data) }
export function batchUserStatus(data) { return agentApi.post('/tools/mall/batch/users/status', data) }

// ===== AI大脑接口 (mall_brain_router) =====
export function mallBrainScan() { return agentApi.post('/agent/mall-brain/scan') }
export function mallBrainReport() { return agentApi.get('/agent/mall-brain/report') }
export function mallBrainAuto(dryRun) { return agentApi.post('/agent/mall-brain/auto', { dry_run: dryRun }) }
export function mallBrainGaps() { return agentApi.get('/agent/mall-brain/gaps') }
export function mallBrainSummary() { return agentApi.get('/agent/mall-brain/summary') }

// ===== 商城扫描 (mall_scanner) =====
export function scanStructure() { return agentApi.post('/mall/scan/structure') }
export function scanHistory() { return agentApi.get('/mall/scan/history') }
export function checkProducts() { return agentApi.post('/mall/scan/products') }
export function checkOrders() { return agentApi.post('/mall/scan/orders') }

// ===== 客服系统 (Agent内置 customer_panel) =====
export function getCustomerMessages() { return agentApi.get('/agent/customer/messages') }
export function replyCustomerMessage(data) { return agentApi.post('/agent/customer/reply', data) }
export function getCustomerStats() { return agentApi.get('/agent/customer/stats') }
export function getCustomerReport() { return agentApi.get('/agent/customer/report') }
