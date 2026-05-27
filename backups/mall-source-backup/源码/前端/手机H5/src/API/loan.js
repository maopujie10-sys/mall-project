import request from "@/request";

// 检查是否可申请
export const apiCheckAvailability = (params) => request.get('api/credit!check.action', params)

// 申请前信息 
export const apiApplyLoanConfig = (params) => {
    return request({
        url: "api/credit!config.action",
        method: "get",
        params
    })
};
// 申请贷款
export const apiApplyLoan = (params) => {
    return request({
        url: "api/credit!apply.action",
        method: "get",
        params
    })
};
// 正在计费的贷款(我的贷款)
export const apiLoanMy = (params) => {
    return request({
        url: "api/credit!bill.action",
        method: "get",
        params
    })
};
// 我的贷款记录
export const apiLoanMyRecord = (params) => {
    return request({
        url: "api/credit!histroy.action",
        method: "get",
        params
    })
};
// 还款前
export const apiLoanRepayForward = (params) => {
    return request({
        url: "api/credit!beforepay.action",
        method: "get",
        params
    })
};
// 还款支付
export const apiLoanPay = (params) => {
    return request({
        url: "api/credit!pay.action",
        method: "get",
        params
    })
};
// 重新申请前
export const apiBeforereApply = (params) => {
    return request({
        url: "api/credit!beforereapply.action",
        method: "get",
        params
    })
};
// 获取国家
export const apiListCountry = (params) => {
    return request({
        url: "api/address!listCountry.action",
        method: "post",
        params
    })
};