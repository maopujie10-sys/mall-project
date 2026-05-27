import request from './request'
import {METHODS} from "../config/index.js";
import qs from 'qs'
//商品库
export const getSystemGoods = (data) => {
    return request({
        url: "/wap/seller/systemGoods!list.action",
        method: METHODS.POST,
        data
    })
}

// //商品库 删除商品
export const sellerGoodsdelete = (data) => {
    return request({
        url: "/wap/seller/goods!delete.action",
        method: METHODS.POST,
        data
    })
}

// //商品库 商家上架商品利润区间
export const sysParaProductInfo = () => {
    return request({
        url: "/wap/api/sysParaProduct!info.action",
        method: METHODS.POST
    })
}

//商家商品
export const merchantGoodsList = (data) => {
    return request({
        url: "/wap/seller/goods!list.action",
        method: METHODS.POST,
        data
    })
}
//商品分类
export const categoryList = (data) => {
    return request({
        url: "/wap/api/category!list.action",
        method: METHODS.POST,
        data
    })
}
// 商品分类-二级
export const categoryListTree = () => {
    return request({
        url: "/wap/api/category!tree.action",
        method: METHODS.GET
    })
}
//评论列表
export const getEvaluation = (data) => {
    return request({
        url: "/wap/seller/evaluation!list.action",
        method: METHODS.POST,
        data
    })
}
//商品库搜索
export const searchKeyword= (data) => {
    return request({
        url: "/wap/seller/systemGoods!search-keyword.action",
        method: METHODS.POST,
        data
    })
}
//商家商品搜索
export const searchSllerKeyword= (data) => {
    return request({
        url: "/wap/api/sellerGoods!search-keyword.action",
        method: METHODS.POST,
        data
    })
}
//修改商品信息
export const goodsUpdate= (data) => {
    return request({
        url: "/wap/seller/goods!update.action",
        method: METHODS.POST,
        data
    })
}
//商品库添加商品
export const goodsaddOrUpdate= (data) => {
    return request({
        loadingPass: true,
        url: "/wap/seller/goods!addOrUpdate.action",
        method: METHODS.POST,
        data
    })
}
//搜索后的商品列表
export const sellerGoodsList= (data) => {
    return request({
        url: "/wap/api/sellerGoods!search-goods.action",
        method: METHODS.POST,
        data
    })
}

export const sellerGoodsList2= (data) => {
    return request({
        url: "/wap/seller/goods!search-goods.action?" + qs.stringify(data),
        method: METHODS.POST,
    })
}

export const sellerGoodsSkuInfo= (data) => {
    return request({
        url: "/wap/seller/goods!sellerGoodsSkuInfo.action",
        method: METHODS.POST,
        data
    })
}
