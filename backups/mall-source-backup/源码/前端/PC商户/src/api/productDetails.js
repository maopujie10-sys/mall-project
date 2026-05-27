import Axios from "@/util/http";

/**
 * 商品详情
 * @param {Object} params 
 * sellerGoodsId	是	string	商品id
    lang	是	string	语言
 * @returns 
 */
export const ProductDetailsApi = (params = {}) =>
  Axios.post("/api/sellerGoods!info.action", params);

/**
 * 商品评价
 * @param {Object} params
 * @returns
 */
export const ProductCommentApi = (params = {}) =>
  Axios.post("/api/evaluation!list.action", params);

/**
 * 商家详情
 * @param {Object} params
 * @returns
 */
export const SellerInfoApi = (params = {}) =>
  Axios.post("/api/seller!info.action", params);


export const SellerClass = (params = {}) =>
  Axios.fetch("/api/category!sellerTree.action", params);


export const getProductEvaluationCategory = (params = {}) =>
  Axios.post("/api/evaluation!countType.action", params);

export const AlsoLike = (params={})=>
Axios.post('api/sellerGoods!recommend_like.action',params)