import { api, agentApi } from './index'
import axios from 'axios'

// ===== 商城 Java (/merchant/ → Java mall-app) =====
const merchant = axios.create({
  baseURL: '/merchant',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})
merchant.interceptors.response.use(
  (res) => {
    const d = res.data
    if (d && typeof d === 'object' && 'code' in d) {
      if (d.code !== 0 && d.code !== 200) return Promise.reject(new Error(d.message || 'error'))
      return d.data !== undefined ? d.data : d
    }
    return d
  },
  (err) => Promise.reject(err)
)

// ===== FastAPI Agent 工具 =====

// 仪表盘
export function getDashboard() { return agentApi.get('/tools/mall/stats') }

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

// ===== Java 商城 /merchant/ (商家仪表盘) =====
export function getDashboardHead(params) { return merchant.post('/dashboard/head', params || {}) }
export function getDashboardLine(params) { return merchant.post('/dashboard/line', params || {}) }
export function getDashboardGoods(params) { return merchant.post('/dashboard/goods', params || {}) }
export function getDashboardStats(params) { return merchant.post('/dashboard/stats', params || {}) }
export function getSellerInfo() { return merchant.get('/info') }

// ===== FastAPI 基础 =====
export function getMallStatus() { return agentApi.get('/tools/mall/stats') }

// ===== 轮播管理 =====
export function getBannerList(params) { return agentApi.get('/tools/mall/banners', { params }) }
export function getBanner(uuid) { return agentApi.get(`/tools/mall/banner/${uuid}`) }
export function saveBanner(data) { return agentApi.post('/tools/mall/banner', data) }
export function updateBanner(uuid, data) { return agentApi.put(`/tools/mall/banner/${uuid}`, data) }
export function deleteBanner(uuid) { return agentApi.delete(`/tools/mall/banner/${uuid}`) }

// ===== 分类管理 =====
export function getCategoryList(params) { return agentApi.get('/tools/mall/category/list', { params }) }
export function getCategoryAll() { return agentApi.get('/tools/mall/category/all') }
export function getCategory(uuid) { return agentApi.get(`/tools/mall/category/${uuid}`) }
export function saveCategory(data) { return agentApi.post('/tools/mall/category', data) }
export function updateCategory(uuid, data) { return agentApi.put(`/tools/mall/category/${uuid}`, data) }
export function updateCategoryStatus(uuid, data) { return agentApi.put(`/tools/mall/category/${uuid}/status`, data) }
export function deleteCategory(uuid) { return agentApi.delete(`/tools/mall/category/${uuid}`) }

// ===== 评价管理 =====
export function getEvaluationList(params) { return agentApi.get('/tools/mall/evaluations', { params }) }
export function updateEvaluationStatus(uuid, data) { return agentApi.put(`/tools/mall/evaluation/${uuid}/status`, data) }
export function deleteEvaluation(uuid) { return agentApi.delete(`/tools/mall/evaluation/${uuid}`) }

// ===== 属性分类管理 =====
export function getAttrCategoryList(params) { return agentApi.get('/tools/mall/attr-categories', { params }) }
export function getAttrCategory(uuid) { return agentApi.get(`/tools/mall/attr-category/${uuid}`) }
export function saveAttrCategory(data) { return agentApi.post('/tools/mall/attr-category', data) }
export function updateAttrCategory(uuid, data) { return agentApi.put(`/tools/mall/attr-category/${uuid}`, data) }
export function deleteAttrCategory(uuid) { return agentApi.delete(`/tools/mall/attr-category/${uuid}`) }

// ===== 属性管理 =====
export function getAttrList(params) { return agentApi.get('/tools/mall/attrs', { params }) }
export function getAttr(uuid) { return agentApi.get(`/tools/mall/attr/${uuid}`) }
export function saveAttr(data) { return agentApi.post('/tools/mall/attr', data) }
export function updateAttr(uuid, data) { return agentApi.put(`/tools/mall/attr/${uuid}`, data) }
export function deleteAttr(uuid) { return agentApi.delete(`/tools/mall/attr/${uuid}`) }

// ===== 属性值管理 =====
export function getAttrValueList(params) { return agentApi.get('/tools/mall/attr-values', { params }) }
export function getAttrValue(id) { return agentApi.get(`/tools/mall/attr-value/${id}`) }
export function saveAttrValue(data) { return agentApi.post('/tools/mall/attr-value', data) }
export function updateAttrValue(id, data) { return agentApi.put(`/tools/mall/attr-value/${id}`, data) }
export function deleteAttrValue(id) { return agentApi.delete(`/tools/mall/attr-value/${id}`) }
