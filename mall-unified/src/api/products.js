import { get, post } from './index'

export function getProductList(params = {}) {
  return get('/api/product/list', params)
}
export function getProductDetail(id) {
  return get('/api/product/' + id)
}
export function getProductSkus(goodsId) {
  return get('/api/goods/' + goodsId + '/skus')
}
export function getCategories() {
  return get('/api/category/list')
}
export function getCategoryTree() {
  return get('/api/category/tree')
}
export function getSubCategories(parentId) {
  return get('/api/category/' + parentId + '/children')
}
export function getSellerList(params) {
  return get('/api/seller/list', params)
}
export function getSellerDetail(sellerId) {
  return get('/api/seller/' + sellerId)
}
export function getSellerGoods(sellerId, params) {
  return get('/api/seller/' + sellerId + '/goods', params)
}
export function getHomeData() {
  return get('/api/home')
}
export function getBanners() {
  return get('/api/banner/list')
}
export function getRecommendProducts(params) {
  return get('/api/product/recommend', params)
}
export function searchProducts(keyword, params = {}) {
  return get('/api/product/search', { keyword, ...params })
}
