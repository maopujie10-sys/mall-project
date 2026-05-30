import { get, post, put, del } from './index'

// ===== 用户 =====
export function getUserInfo() { return get('/api/user/info') }
export function changePassword(data) { return put('/api/user/password', data) }
export function registerNoVerifcode(params) { return post('/api/user/register', params) }
export function justShopRegister(params) { return post('/api/user/register', params) }
export function apiSendCode(params) { return post('/api/idcode/send', params) }

// ===== 地址 =====
export function getAddressList() { return get('/api/address/list') }
export function addAddress(data) { return post('/api/address', data) }
export function updateAddress(data) { return put('/api/address/' + data.id, data) }
export function deleteAddress(data) { return del('/api/address/' + data.addressId || data.id) }
export function setDefaultAddress(addressId) { return put('/api/address/' + addressId + '/default') }

// ===== 钱包 =====
export function getWalletBalance() { return get('/api/user/balance') }
export function getWalletLogs(params) { return get('/api/wallet/logs', params) }
export function recharge(data) { return post('/api/recharge', data) }
export function withdraw(data) { return post('/api/withdraw', data) }

// ===== KYC =====
export function getKycStatus() { return get('/api/kyc/status') }
export function submitKyc(data) { return post('/api/kyc', data) }

// ===== 通知 =====
export function getNotifications(params) { return get('/api/notification/list', params) }
export function getUnreadCount() { return get('/api/notification/unread') }
export function markRead(id) { return put('/api/notification/' + id + '/read') }
export function readAll() { return put('/api/notification/read-all') }

// ===== 订单 =====
export function orderListMain(params) { return get('/api/order/list', params) }
export function orderReceipt(params) { return put('/api/order/' + (params.orderId || params.id) + '/receipt') }
export function orderCancel(params) { return put('/api/order/' + (params.orderId || params.id) + '/cancel') }

// ===== 收藏/关注 =====
export function keepGoodsCount() { return get('/api/keep-goods/count') }
export function focusSellerCount() { return get('/api/focus-seller/count') }
export function apicCuntOrderStatus() { return get('/api/order/count-status') }

// ===== 商品详情 =====
export function goods_info_action_post(params) { return get('/api/product/' + params.id) }

// ===== 物流 =====
export function getLogisticsInfo(orderId) { return get('/api/logistics/' + orderId) }
export function getLogisticsTrace(orderId) { return get('/api/logistics/' + orderId + '/trace') }
