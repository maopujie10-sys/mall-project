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