import request from "@/request";

export const home_messageNum = (params) => {
    return request({
        url: "api/user/register",
        method: "post",
        params
    })
};
export const home_index = (params) => {
    return request({
        url: "api/index!home.action",
        method: "post",
        params
    })
};
export const home_category = (params) => {
    return request({
        url: "api/category!list.action",
        method: "post",
        params
    })
};
export const apiCategoryTree = (params) => {
    return request({
        url: "api/category!tree.action",
        method: "get",
        params
    })
};
export const apiGetCategory = (params) => {
    return request({
        url: "api/seller!getCategory.action",
        method: "post",
        params
    })
};
export const home_sellerGoods = (params) => {
    return request({
        url: "api/sellerGoods!list.action",
        method: "post",
        params
    })
};
export const getSellerList = (params) => {
    return request({
        url: "api/seller!list.action",
        method: "post",
        params
    })
};
///
export const apiGetNewGoods = (params) => {
    return request({
        url: "api/sellerGoods!recommend_new.action",
        method: "post",
        params
    })
};
export const apiGetBannerList = (params) => {
    return request({
        url: "api/banner!bannerList.action",
        method: "post",
        params
    })
};
export const apiGetRecommendGoods = (params) => {
    return request({
        url: "api/category!recommend.action",
        method: "post",
        params
    })
};
