import { agentApi } from './index'

// ===== FastAPI Agent 商城工具 =====

// 仪表盘
export function getMallStatus() { return agentApi.get('/tools/mall/stats') }

// 用户管理
export function getUserList(params) { return agentApi.get('/tools/mall/users', { params }) }
export function updateUserStatus(data) { return agentApi.post('/tools/mall/user/status', data) }
export function adjustUserBalance(data) { return agentApi.post('/tools/mall/user/balance/adjust', data) }

// 商品管理
export function getProductList(params) { return agentApi.get('/tools/mall/products', { params }) }
export function auditProduct(data) { return agentApi.post('/tools/mall/product/audit', data) }

// 订单管理
export function getOrderList(params) { return agentApi.get('/tools/mall/orders', { params }) }
export function forceRefund(orderId) { return agentApi.post(`/tools/mall/order/refund/${orderId}`) }

// 充值审核
export function getRechargePending(params) { return agentApi.get('/tools/mall/recharge/pending', { params }) }
export function auditRecharge(data) { return agentApi.post('/tools/mall/recharge/audit', data) }

// 提现审核
export function getWithdrawPending(params) { return agentApi.get('/tools/mall/withdraw/pending', { params }) }
export function auditWithdraw(data) { return agentApi.post('/tools/mall/withdraw/audit', data) }

// 商家管理
export function getMerchantList(params) { return agentApi.get('/tools/mall/merchant/list', { params }) }
export function updateMerchantStatus(data) { return agentApi.post('/tools/mall/merchant/status', data) }
export function getMerchantApplyList(params) { return agentApi.get('/tools/mall/merchant/apply/list', { params }) }
export function auditMerchantApply(data) { return agentApi.post('/tools/mall/merchant/apply/audit', data) }

// 轮播管理
export function getBannerList(params) { return agentApi.get('/tools/mall/banners', { params }) }
export function getBanner(uuid) { return agentApi.get(`/tools/mall/banner/${uuid}`) }
export function saveBanner(data) { return agentApi.post('/tools/mall/banner', data) }
export function updateBanner(uuid, data) { return agentApi.put(`/tools/mall/banner/${uuid}`, data) }
export function deleteBanner(uuid) { return agentApi.delete(`/tools/mall/banner/${uuid}`) }

// 分类管理
export function getCategoryList(params) { return agentApi.get('/tools/mall/category/list', { params }) }
export function getCategoryAll() { return agentApi.get('/tools/mall/category/all') }
export function getCategory(uuid) { return agentApi.get(`/tools/mall/category/${uuid}`) }
export function saveCategory(data) { return agentApi.post('/tools/mall/category', data) }
export function updateCategory(uuid, data) { return agentApi.put(`/tools/mall/category/${uuid}`, data) }
export function updateCategoryStatus(uuid, data) { return agentApi.put(`/tools/mall/category/${uuid}/status`, data) }
export function deleteCategory(uuid) { return agentApi.delete(`/tools/mall/category/${uuid}`) }

// 评价管理
export function getEvaluationList(params) { return agentApi.get('/tools/mall/evaluations', { params }) }
export function updateEvaluationStatus(uuid, data) { return agentApi.put(`/tools/mall/evaluation/${uuid}/status`, data) }
export function deleteEvaluation(uuid) { return agentApi.delete(`/tools/mall/evaluation/${uuid}`) }
