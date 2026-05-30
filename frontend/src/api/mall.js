import axios from "axios"
import { agentApi } from './index'

// =====  =====
export function getMallStatus() { return agentApi.get('/tools/mall/stats') }

// =====  =====
export function getProductList(params) { return agentApi.get('/tools/mall/products', { params }) }
export function getProductDetail(uuid) { return agentApi.get(`/tools/mall/product/${uuid}`) }
export function createProduct(data) { return agentApi.post('/tools/mall/product', data) }
export function auditProduct(data) { return agentApi.post('/tools/mall/product/audit', data) }
export function updateProduct(uuid, data) { return agentApi.put(`/tools/mall/product/${uuid}`, data) }
export function deleteProduct(uuid) { return agentApi.delete(`/tools/mall/product/${uuid}`) }

// =====  =====
export function getOrderList(params) { return agentApi.get('/tools/mall/orders', { params }) }
export function getOrderDetail(orderId) { return agentApi.get(`/tools/mall/order/${orderId}`) }
export function forceRefund(orderId, data) { return agentApi.post(`/tools/mall/order/refund/${orderId}`, data) }
export function getOrderLogs(orderId) { return agentApi.get(`/tools/mall/order/${orderId}/logs`) }

// =====  =====
export function getUserList(params) { return agentApi.get('/tools/mall/users', { params }) }
export function getUserDetail(userId) { return agentApi.get(`/tools/mall/user/${userId}`) }
export function updateUserStatus(data) { return agentApi.post('/tools/mall/user/status', data) }
export function adjustUserBalance(data) { return agentApi.post('/tools/mall/user/balance/adjust', data) }

// =====  =====
export function getCategoryList(params) { return agentApi.get('/tools/mall/category/list', { params }) }
export function getCategoryAll() { return agentApi.get('/tools/mall/category/all') }
export function getCategory(uuid) { return agentApi.get(`/tools/mall/category/${uuid}`) }
export function saveCategory(data) { return agentApi.post('/tools/mall/category', data) }
export function updateCategory(uuid, data) { return agentApi.put(`/tools/mall/category/${uuid}`, data) }
export function updateCategoryStatus(uuid, data) { return agentApi.put(`/tools/mall/category/${uuid}/status`, data) }
export function deleteCategory(uuid) { return agentApi.delete(`/tools/mall/category/${uuid}`) }

// =====  =====
export function getWalletLogs(params) { return agentApi.get('/tools/mall/wallet/logs', { params }) }
export function getWalletBalance(userId) { return agentApi.get('/tools/mall/wallet/balance') }

// =====  =====
export function getRechargePending(params) { return agentApi.get('/tools/mall/recharge/pending', { params }) }
export function auditRecharge(data) { return agentApi.post('/tools/mall/recharge/audit', data) }

// =====  =====
export function getWithdrawPending(params) { return agentApi.get('/tools/mall/withdraw/pending', { params }) }
export function auditWithdraw(data) { return agentApi.post('/tools/mall/withdraw/audit', data) }

// =====  =====
export function getLogisticsInfo(orderId) { return agentApi.get(`/tools/mall/logistics/${orderId}`) }
export function getLogisticsTrace(orderId) { return agentApi.get(`/tools/mall/logistics/${orderId}/trace`) }

// ===== KYC =====
export function getKycList(params) { return agentApi.get('/tools/mall/kyc/list', { params }) }
export function auditKyc(kycId, data) { return agentApi.post(`/tools/mall/kyc/audit/${kycId}`, data) }
export function getKycHighLevel() { return agentApi.get('/tools/mall/kyc-high-level') }

// =====  =====
export function getComplaintList(params) { return agentApi.get('/tools/mall/complaints', { params }) }
export function handleComplaint(uuid, data) { return agentApi.post(`/tools/mall/complaint/handle/${uuid}`, data) }

// =====  =====
export function getContractInfo() { return agentApi.get('/tools/mall/contract/info') }
export function getContractList(params) { return agentApi.get('/tools/mall/contract/list', { params }) }

// =====  =====
export function getCreditList(params) { return agentApi.get('/tools/mall/credits', { params }) }

// =====  =====
export function getLoanList(params) { return agentApi.get('/tools/mall/loan/admin/list', { params }) }
export function auditLoan(data) { return agentApi.post('/tools/mall/loan/admin/audit', data) }
export function getLoanConfig() { return agentApi.get('/tools/mall/loan/config') }
export function getLoanConfigs() { return agentApi.get('/tools/mall/loan/admin/configs') }

// =====  =====
export function getCommentList(goodId, params) { return agentApi.get(`/tools/mall/comments/${goodId}`, { params }) }
export function deleteComment(uuid) { return agentApi.delete(`/tools/mall/comment/${uuid}`) }

// =====  =====
export function getEvaluationList(params) { return agentApi.get('/tools/mall/evaluations', { params }) }
export function updateEvaluationStatus(uuid, data) { return agentApi.put(`/tools/mall/evaluation/${uuid}/status`, data) }
export function deleteEvaluation(uuid) { return agentApi.delete(`/tools/mall/evaluation/${uuid}`) }

// =====  =====
export function getAddressList(params) { return agentApi.get('/tools/mall/addresses', { params }) }

// =====  =====
export function getCartList(params) { return agentApi.get('/tools/mall/carts', { params }) }

// =====  =====
export function getKeepGoodsList(params) { return agentApi.get('/tools/mall/keep-goods', { params }) }

// =====  =====
export function getFocusSellerList(params) { return agentApi.get('/tools/mall/focus-sellers', { params }) }

// =====  =====
export function getInviteList(params) { return agentApi.get('/tools/mall/invites', { params }) }
export function getInviteStats() { return agentApi.get('/tools/mall/invite/stats') }

// =====  =====
export function getLotteryCurrent() { return agentApi.get('/tools/mall/lottery/current') }
export function getLotteryDetail(activityId) { return agentApi.get(`/tools/mall/lottery/${activityId}`) }

// =====  =====
export function getRebateList(params) { return agentApi.get('/tools/mall/rebates', { params }) }
export function getRebateStats() { return agentApi.get('/tools/mall/rebate/stats') }

// =====  =====
export function getPromoteList(params) { return agentApi.get('/tools/mall/promotes', { params }) }
export function getPromoteConfig() { return agentApi.get('/tools/mall/promote/config') }

// =====  =====
export function getSubscribeList(params) { return agentApi.get('/tools/mall/subscribes', { params }) }
// =====  =====
export function getMerchantList(params) { return agentApi.get('/tools/mall/merchant/list', { params }) }
export function updateMerchantStatus(data) { return agentApi.post('/tools/mall/merchant/status', data) }
export function getMerchantApplyList(params) { return agentApi.get('/tools/mall/merchant/apply/list', { params }) }
export function auditMerchantApply(data) { return agentApi.post('/tools/mall/merchant/apply/audit', data) }
export function getSellerList(params) { return agentApi.get('/tools/mall/seller/list', { params }) }
export function getSellerPromotional() { return agentApi.get('/tools/mall/seller/promotional') }

// =====  =====
export function getMerchantDashboard() { return agentApi.get('/tools/mall/merchant/dashboard') }

// =====  =====
export function getMerchantFinance(params) { return agentApi.get('/tools/mall/merchant/finance', { params }) }
export function getMerchantFinanceHead() { return agentApi.get('/tools/mall/merchant/finance-report/head') }
export function getMerchantFinanceReport(params) { return agentApi.get('/tools/mall/merchant/finance-report/list', { params }) }

// =====  =====
export function getMerchantGoods(params) { return agentApi.get('/tools/mall/merchant/goods', { params }) }

// =====  =====
export function getMerchantOrders(params) { return agentApi.get('/tools/mall/merchant/orders', { params }) }

// =====  =====
export function getMerchantEvaluations(params) { return agentApi.get('/tools/mall/merchant/evaluations', { params }) }

// =====  =====
export function getBannerList(params) { return agentApi.get('/tools/mall/banners', { params }) }
export function getBanner(uuid) { return agentApi.get(`/tools/mall/banner/${uuid}`) }
export function saveBanner(data) { return agentApi.post('/tools/mall/banner', data) }
export function updateBanner(uuid, data) { return agentApi.put(`/tools/mall/banner/${uuid}`, data) }
export function deleteBanner(uuid) { return agentApi.delete(`/tools/mall/banner/${uuid}`) }

// =====  =====
export function getNewsList(params) { return agentApi.get('/tools/mall/news/list', { params }) }
export function getNewsDetail(newsId) { return agentApi.get(`/tools/mall/news/${newsId}`) }
export function saveNews(data) { return agentApi.post('/tools/mall/news', data) }
export function updateNews(newsId, data) { return agentApi.put(`/tools/mall/news/${newsId}`, data) }
export function deleteNews(newsId) { return agentApi.delete(`/tools/mall/news/${newsId}`) }

// =====  =====
export function getNotificationList(params) { return agentApi.get('/tools/mall/notifications', { params }) }
export function saveNotification(data) { return agentApi.post('/tools/mall/notification', data) }
export function updateNotification(nid, data) { return agentApi.put(`/tools/mall/notification/${nid}`, data) }
export function deleteNotification(nid) { return agentApi.delete(`/tools/mall/notification/${nid}`) }

// =====  =====
export function getSysparaList() { return agentApi.get('/tools/mall/syspara/list') }
export function getSyspara(key) { return agentApi.get(`/tools/mall/syspara/${key}`) }
export function saveSyspara(data) { return agentApi.post('/tools/mall/syspara', data) }
export function updateSyspara(sysId, data) { return agentApi.put(`/tools/mall/syspara/${sysId}`, data) }
export function deleteSyspara(sysId) { return agentApi.delete(`/tools/mall/syspara/${sysId}`) }

// =====  =====
export function getAreaCountries(lang) { return agentApi.get('/tools/mall/area/countries', { params: { lang } }) }
export function getAreaStates(countryId) { return agentApi.get('/tools/mall/area/states', { params: { country_id: countryId } }) }
export function getAreaCities(stateId) { return agentApi.get('/tools/mall/area/cities', { params: { state_id: stateId } }) }
export function getAreaMobilePrefix() { return agentApi.get('/tools/mall/area/mobile-prefix') }
// 区域后台管理CRUD
export function getAreaAdminCountries(params) { return agentApi.get('/tools/mall/area/admin/countries', { params }) }
export function saveAreaCountry(data) { return agentApi.post('/tools/mall/area/admin/country', data) }
export function updateAreaCountry(cid, data) { return agentApi.put(`/tools/mall/area/admin/country/${cid}`, data) }
export function deleteAreaCountry(cid) { return agentApi.delete(`/tools/mall/area/admin/country/${cid}`) }
export function getAreaAdminCities(params) { return agentApi.get('/tools/mall/area/admin/cities', { params }) }
export function saveAreaCity(data) { return agentApi.post('/tools/mall/area/admin/city', data) }
export function updateAreaCity(cid, data) { return agentApi.put(`/tools/mall/area/admin/city/${cid}`, data) }
export function deleteAreaCity(cid) { return agentApi.delete(`/tools/mall/area/admin/city/${cid}`) }

// =====  =====
export function getMallLevelList() { return agentApi.get('/tools/mall/malllevel/list') }
export function getMallLevelDetail(uuid) { return agentApi.get(`/tools/mall/malllevel/${uuid}`) }
export function getMallLevelConfig() { return agentApi.get('/tools/mall/malllevel/config') }

// ===== / =====
export function getChatConversations(params) { return agentApi.get('/tools/mall/chat/conversations', { params }) }
export function getChatMessages(conversationId) { return agentApi.get(`/tools/mall/chat/messages/${conversationId}`) }
export function getChatAdminOnechat(conversationId) { return agentApi.get('/tools/mall/chat/admin/onechat', { params: { conversation_id: conversationId } }) }
export function chatAdminReply(data) { return agentApi.post('/tools/mall/chat/admin/reply', data) }

// =====  =====
export function getRotationDomains() { return agentApi.get('/tools/mall/rotation/domains') }
export function getRotationStats() { return agentApi.get('/tools/mall/rotation/stats') }
export function blockDomain(data) { return agentApi.post('/tools/mall/rotation/block', data) }
export function unblockDomain(data) { return agentApi.post('/tools/mall/rotation/unblock', data) }

// =====  =====
export function getIdcodeList(params) { return agentApi.get('/tools/mall/idcodes', { params }) }

// =====  =====
export function getComboList() { return agentApi.get('/tools/mall/combos') }
export function getComboRecords(params) { return agentApi.get('/tools/mall/combo/records', { params }) }
export function saveCombo(data) { return agentApi.post('/tools/mall/combo', data) }
export function updateCombo(uuid, data) { return agentApi.put(`/tools/mall/combo/${uuid}`, data) }
export function deleteCombo(uuid) { return agentApi.delete(`/tools/mall/combo/${uuid}`) }

// ===== Google =====
export function getGoogleAuthList(params) { return agentApi.get('/tools/mall/google-auth/list', { params }) }

// =====  =====
export function getAdminList(params) { return agentApi.get('/tools/mall/admins', { params }) }
export function saveAdmin(data) { return agentApi.post('/tools/mall/admin', data) }
export function updateAdmin(adminId, data) { return agentApi.put(`/tools/mall/admin/${adminId}`, data) }

// =====  =====
export function batchProductStatus(data) { return agentApi.post('/tools/mall/batch/products/status', data) }
export function batchOrderStatus(data) { return agentApi.post('/tools/mall/batch/orders/status', data) }
export function batchUserStatus(data) { return agentApi.post('/tools/mall/batch/users/status', data) }

// ===== AI (mall_brain_router) =====
export function mallBrainScan() { return agentApi.post('/agent/mall-brain/scan') }
export function mallBrainReport() { return agentApi.get('/agent/mall-brain/report') }
export function mallBrainAuto(dryRun) { return agentApi.post('/agent/mall-brain/auto', { dry_run: dryRun }) }
export function mallBrainGaps() { return agentApi.get('/agent/mall-brain/gaps') }
export function mallBrainSummary() { return agentApi.get('/agent/mall-brain/summary') }

// =====  (mall_scanner) =====
export function scanStructure() { return agentApi.post('/mall/scan/structure') }
export function scanHistory() { return agentApi.get('/mall/scan/history') }
export function checkProducts() { return agentApi.post('/mall/scan/products') }
export function checkOrders() { return agentApi.post('/mall/scan/orders') }

// =====  (Agent customer_panel) =====
export function getCustomerMessages() { return agentApi.get('/agent/customer/messages') }
export function replyCustomerMessage(data) { return agentApi.post('/agent/customer/reply', data) }
export function getCustomerStats() { return agentApi.get('/agent/customer/stats') }
export function getCustomerReport() { return agentApi.get('/agent/customer/report') }

const merchant = axios.create({ baseURL: '/api', timeout: 15000, headers: { 'Content-Type': 'application/json' } });
merchant.interceptors.response.use((r)=>{const d=r.data;if(d&&typeof d==='object'&&'code' in d)return d.data!==undefined?d.data:d;return d;},e=>Promise.reject(e));

// ===== API =====
export function getDashboard() { return agentApi.get('/tools/mall/stats') }

export function getDashboardHead(params) { return merchant.post('/dashboard/head', params || {}) }

export function getDashboardLine(params) { return merchant.post('/dashboard/line', params || {}) }

export function getDashboardGoods(params) { return merchant.post('/dashboard/goods', params || {}) }

export function getAttrCategoryList(params) { return agentApi.get('/tools/mall/attr-categories', { params }) }

export function saveAttrCategory(data) { return agentApi.post('/tools/mall/attr-category', data) }

export function updateAttrCategory(uuid, data) { return agentApi.put(`/tools/mall/attr-category/${uuid}`, data) }

export function deleteAttrCategory(uuid) { return agentApi.delete(`/tools/mall/attr-category/${uuid}`) }

export function getAttrList(params) { return agentApi.get('/tools/mall/attrs', { params }) }

export function saveAttr(data) { return agentApi.post('/tools/mall/attr', data) }

export function updateAttr(uuid, data) { return agentApi.put(`/tools/mall/attr/${uuid}`, data) }

export function deleteAttr(uuid) { return agentApi.delete(`/tools/mall/attr/${uuid}`) }



// =====  () =====
export function getAttrValueList(params) { return agentApi.get('/tools/mall/attr-values', { params }) }
export function getAttrValueDetail(id) { return agentApi.get(`/tools/mall/attr-value/${id}`) }
export function saveAttrValue(data) { return agentApi.post('/tools/mall/attr-value', data) }
export function updateAttrValue(id, data) { return agentApi.put(`/tools/mall/attr-value/${id}`, data) }
export function deleteAttrValue(id) { return agentApi.delete(`/tools/mall/attr-value/${id}`) }

// =====  () =====
export function seedProducts() { return agentApi.post('/tools/mall/seed/products') }
export function seedOrders() { return agentApi.post('/tools/mall/seed/orders') }
export function seedUsers() { return agentApi.post('/tools/mall/seed/users') }
export function seedMerchants() { return agentApi.post('/tools/mall/seed/merchants') }
export function seedComments() { return agentApi.post('/tools/mall/seed/comments') }
export function seedClear() { return agentApi.delete('/tools/mall/seed/clear') }

// =====  () =====
export function submitLocalOrder(data) { return agentApi.post('/tools/mall/order-local/submit', data) }

// =====  () =====
export function sellerVersionClient(data) { return agentApi.post('/tools/mall/seller/version/client', data) }
export function sellerVersionRegister(data) { return agentApi.post('/tools/mall/seller/version/register', data) }
export function sellerVersionRegisterJs(data) { return agentApi.post('/tools/mall/seller/version/register-js', data) }
export function sellerVersionUpdateSign(data) { return agentApi.post('/tools/mall/seller/version/update-sign-pdf', data) }

// =====  () =====
export function getUploadList(params) { return agentApi.get('/tools/mall/upload/files', { params }) }
export function deleteUpload(id) { return agentApi.delete(`/tools/mall/upload/${id}`) }

// ===== Java () =====
export function getJavaRotationDomains() { return agentApi.get('/tools/mall/rotation/domains') }
export function javaBlockDomain(data) { return agentApi.post('/tools/mall/rotation/block', data) }
export function javaUnblockDomain(data) { return agentApi.post('/tools/mall/rotation/unblock', data) }
export function getJavaRotationStats() { return agentApi.get('/tools/mall/rotation/stats') }

// ===== 代理管理 =====
export function getAgentList(params) { return agentApi.get('/tools/mall/agent/list', { params }) }
export function getAgentDetail(sellerId) { return agentApi.get(`/tools/mall/agent/${sellerId}`) }
export function updateAgentStatus(data) { return agentApi.put(`/tools/mall/agent/${data.sellerId}/status`, data) }
export function getAgentTeam(sellerId) { return agentApi.get(`/tools/mall/agent/${sellerId}/team`) }
export function getAgentLevelList() { return agentApi.get('/tools/mall/agent/levels') }
export function saveAgentLevel(data) { return agentApi.post('/tools/mall/agent/level', data) }
export function updateAgentLevel(uuid, data) { return agentApi.put(`/tools/mall/agent/level/${uuid}`, data) }
export function deleteAgentLevel(uuid) { return agentApi.delete(`/tools/mall/agent/level/${uuid}`) }
export function getAgentRebateList(params) { return agentApi.get('/tools/mall/agent/rebates', { params }) }
export function getAgentRebateStats() { return agentApi.get('/tools/mall/agent/rebate/stats') }

// ===== 活动/抽奖管理 =====
export function getActivityList(params) { return agentApi.get('/tools/mall/activity/list', { params }) }
export function getActivityDetail(activityId) { return agentApi.get(`/tools/mall/activity/${activityId}`) }
export function saveActivity(data) { return agentApi.post('/tools/mall/activity', data) }
export function updateActivity(activityId, data) { return agentApi.put(`/tools/mall/activity/${activityId}`, data) }
export function toggleActivityShow(activityId, data) { return agentApi.put(`/tools/mall/activity/${activityId}/toggle`, data) }
export function deleteActivity(activityId) { return agentApi.delete(`/tools/mall/activity/${activityId}`) }
export function getActivityPrizes(activityId) { return agentApi.get(`/tools/mall/activity/${activityId}/prizes`) }
export function saveActivityPrize(data) { return agentApi.post('/tools/mall/activity/prize', data) }
export function updateActivityPrize(prizeId, data) { return agentApi.put(`/tools/mall/activity/prize/${prizeId}`, data) }
export function deleteActivityPrize(prizeId) { return agentApi.delete(`/tools/mall/activity/prize/${prizeId}`) }
export function getActivityRecords(params) { return agentApi.get('/tools/mall/activity/records', { params }) }

// ===== 安全重置审核 =====
export function getSafewordList(params) { return agentApi.get('/tools/mall/safeword/list', { params }) }
export function approveSafeword(applyId) { return agentApi.post(`/tools/mall/safeword/${applyId}/approve`) }
export function rejectSafeword(applyId) { return agentApi.post(`/tools/mall/safeword/${applyId}/reject`) }
