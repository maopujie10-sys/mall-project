import { get, post, put, del } from './index'

// 购物车列表
export function getCartList() {
  return get('/api/cart/list')
}
// 加入购物车
export function addToCart(data) {
  return post('/api/cart', data)
}
// 更新购物车
export function updateCartItem(data) {
  return put('/api/cart', data)
}
// 删除购物车商品
export function removeCartItem(cartId) {
  return del('/api/cart/' + cartId)
}
