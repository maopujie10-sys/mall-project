import request from "@/request";

export const home_messageNum = (params) => {
    return request({
        url: "api/user/register",
        method: "post",
        params: params
    })
};
export const home_index = (params) => {
    return request({
        url: "api/index!home.action",
        method: "post",
        params: params
    })
};
export const home_category = (params) => {
    return request({
        url: "api/category!list.action",
        method: "post",
        params: params
    })
};
export const home_sellerGoods = (params) => {
    return request({
        url: "api/sellerGoods!list.action",
        method: "post",
        params: params
    })
};
export const getSellerList = (params) => {
    return request({
        url: "api/seller!list.action",
        method: "post",
        params: params
    })
};

//订阅
export const sub = (data) => {
    return request({
        url: '/api/subscribe!add.action',
        method: 'post',
        params: data
    })
}

// 获取客服地址
export const apiGetCustomerService = (data= {}) => {
    return request({
        url: 'api/syspara!getSyspara.action',
        method: 'post',
        params: data
    })
}