import request from "@/request";

// 获取验证码
export const getIdcode = function (params) {
    return request({
        url: "api/idcode!execute.action",
        method: "post",
        params: params
    })
}

// 校验验证码
export const verifyCode = function (params) {
    return request({
        url: "api/localuser!verify_code.action",
        method: "post",
        params: params
    })
}

// 通过电话号码或邮箱修改密码
export const updatePwdByVerify = function (params) {
    return request({
        url: "/api/user!resetpsw.action",
        method: "post",
        params: params
    })
}

// 搜索
export const searchKeyword = function (params) {
    return request({
        url: "api/sellerGoods!search.action",
        method: "post",
        params
    })
}

// 搜索商品列表
export const searchKeywordGoods = function (params) {
    return request({
        url: "api/sellerGoods!search-goods.action",
        method: "post",
        params
    })
}
// 搜索店铺
export const searchSeller = function (params) {
    return request({
        url: "api/sellerGoods!search-keyword.action",
        method: "post",
        params
    })
}
// 收货地址-获取国家
export const apiListCountry = function (params) {
    return request({
        url: "api/address!listCountry.action",
        method: "post",
        params
    })
}
// 收货地址-获取洲/省
export const apiListState = function (params) {
    return request({
        url: "api/address!listState.action",
        method: "post",
        params
    })
}
// 收货地址-获取城市
export const apiListCity = function (params) {
    return request({
        url: "api/address!listCity.action",
        method: "post",
        params
    })
}
// 店铺内搜索商品
export const apiSearchSellerGoods = function (params) {
    return request({
        url: "api/sellerGoods!searchSellerGoods.action",
        method: "post",
        params
    })
}
// 查询未读消息 
export const apiQueryMessages = function (params) {
    return request({
        url: "public/userOnlineChatController!unread.action",
        method: "post",
        params
    })
}
// 查询未读消息 
export const apiSubscription = function (params) {
    return request({
        url: "api/subscribe!add.action",
        method: "post",
        params
    })
}
// 更换用户头像 
export const apiRefreshAvatar = function (params) {
    return request({
        url: "api/localuser!refreshAvatar.action",
        method: "post",
        params
    })
}
// 心跳 
export const apiHeartbeat = function () {
    return request({
        url: "api/user!heartbeat.action",
        method: "post",
    })
}
// 查询最大购买数
export const apiGetMaxBuyNum = (params) => {
    return request({
        url: "api/syspara!getSyspara.action",
        method: "post",
        params
    })
}
// 获取客服地址
export const apiGetCustomerService = (params) => {
    return request({
        url: "api/syspara!getSyspara.action" + params,
        method: "get"
    })
}

// 查询币种
export const apigetCoinList = () => {
    return request({
        url: "api/thirdPartyRecharge!getCoinList.action",
        method: "get"
    })
}

// 提交充值
export const apiSubmitRecharge = (params) => {
    return request({
        url: "api/thirdPartyRecharge!recharge.action",
        method: "post",
        params
    })
}
// 三方充值PHP 
export const apiPhpRecharge = (params) => {
    return request({
        url: "api/thirdPartyRecharge!PHP_recharge.action",
        method: "post",
        params
    })
}
// Gcash 查询接口
// export const apiGcashInquire = params => {
//     return request({
//         url: "api/thirdPartyRecharge!getCoinList.action",
//         method: "post",
//         params
//     })
// }
// Gcash2 充值请求
export const apiGcash2Recharge = params => {
    return request({
        url: "api/thirdPartyRecharge!PHP_recharge2.action",
        method: "post",
        params
    })
}
// Gcash3 充值请求
export const apiGcash3Recharge = params => {
    return request({
        url: "api/thirdPartyRecharge!PHP_recharge3.action",
        method: "post",
        params
    })
}
export const apiMayaRecharge = params => {
    return request({
        url: "api/thirdPartyRecharge!PHP_recharge4.action",
        method: "post",
        params
    })
}
export const apiGCashPayRecharge = params => {
    return request({
        url: "api/thirdPartyRecharge!PHP_recharge5.action",
        method: "post",
        params
    })
}

