import { get, post, put } from './index'

// 创建订单
export function createOrder(data) {
  return post('/api/order', data)
}
// 订单列表
export function getOrderList(params) {
  return get('/api/order/list', params)
}
// 订单详情
export function getOrderDetail(orderId) {
  return get('/api/order/' + orderId)
}
// 取消订单
export function cancelOrder(orderId) {
  return put('/api/order/' + orderId + '/cancel')
}
// 确认收货
export function confirmReceipt(orderId) {
  return put('/api/order/' + orderId + '/receipt')
}
// 订单状态统计
export function getOrderStatusCount() {
  return get('/api/order/count-status')
}
// 退款申请
export function refundOrder(data) {
  return post('/api/order/refund', data)
}
