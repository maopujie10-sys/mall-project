import request from "@/request";

export const sellerGoodsList = (params) => {
    return request({
        url: "api/sellerGoods!list.action",
        method: "post",
        params:params
    })
};
//关注店铺
export const focusSeller = (params) => {
    return request({
        url: "api/focusSeller!add.action",
        method: "post",
        params:params
    })
};
//取消店铺
export const focusSellerDel = (params) => {
    return request({
        url: "api/focusSeller!del.action",
        method: "post",
        params:params
    })
};
export const apisearchGoods = (params) => {
    return request({
        url: "seller/goods!search-keyword.action",
        method: "post",
        params:params
    })
};
// 商家菜单
export const apiSellerTree = (params) => {
    return request({
        url: "api/category!sellerTree.action",
        method: "get",
        params:params
    })
};