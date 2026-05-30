import { get, post } from './index'

// 首页数据
export const home_index = (params) => get('/api/home', params)
// 分类列表
export const home_category = (params) => get('/api/category/list', params)
// 分类树
export const apiCategoryTree = (params) => get('/api/category/tree', params)
// 获取分类
export const apiGetCategory = (params) => get('/api/seller/category', params)
// 卖家商品列表
export const home_sellerGoods = (params) => get('/api/product/list', params)
// 获取卖家列表
export const getSellerList = (params) => get('/api/seller/list', params)
// 推荐商品 (type: 0 每日新品, 1 推荐, 2 热销)
export const apiGetNewGoods = (params) => get('/api/product/recommend', params)
// Banner 列表
export const apiGetBannerList = (params) => get('/api/banner/list', params)
// 推荐分类
export const apiGetRecommendGoods = (params) => get('/api/category/recommend', params)
// 未读消息
export const apiQueryMessages = (params) => get('/api/chat/unread', params)
// 搜索
export const searchKeyword = (params) => get('/api/product/search', params)
export const searchKeywordGoods = (params) => get('/api/product/search', params)
export const searchSeller = (params) => get('/api/seller/search', params)
