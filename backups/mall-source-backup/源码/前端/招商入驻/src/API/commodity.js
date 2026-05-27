import request from "@/request";

//商品详情
export const getSellerGoods = (params) => {
    return request({
        url: "api/sellerGoods!info.action",
        method: "post",
        params: params
    })
};
//商品详情里面的评论
export const getEvaluationList = (params) => {
    return request({
        url: "/seller/evaluation!list.action",
        method: "post",
        params: params
    })
};
//获取商家详情
export const getSellerInfo = (params) => {
    return request({
        url: "api/seller!info.action",
        method: "post",
        params: params
    })
};
//提交订单
export const orderSubmit = (params) => {
    return request({
        url: "api/order!submit.action",
        method: "post",
        params: params
    })
};
//下单
export const orderPay = (params) => {
    return request({
        url: "api/order!pay.action",
        method: "post",
        params: params
    })
};
//订单详情
export const orderInfoPay = (params) => {
    return request({
        url: "api/order!info.action",
        method: "post",
        params: params
    })
};
//商户注册
export const sellerRegister = (params) => {
    return request({
        url: "/seller/version!register.action",
        method: "get",
        params: params
    })
};

export const sellerRegister2 = (params) => {
    return request({
        url: "/seller/version!registerjs.action",
        method: "get",
        params: params
    })
};
//图片上传
export const uploadimg = (params) => {
    return request({
        url: "api/uploadimg!execute.action",
        method: "post",
        data: params,
    })
};
//查询申请进度
export const getStatus = (params) => {
    return request({
        url: "api/kyc!get.action",
        method: "post",
        params: params
    })  
};
//关注商品
export const keepGoods = (params) => {
    return request({
        url: "api/keepGoods!add.action",
        method: "post",
        params: params
    })
};
//取消关注商品
export const keepGoodsDel = (params) => {
    return request({
        url: "api/keepGoods!del.action",
        method: "post",
        params: params
    })
};
//添加评论
export const evaluationAdd = (params) => {
    return request({
        url: "api/evaluation!add.action",
        method: "post",
        params: params
    })
};

export const apiListCountry = (params = {}) => {
    return request({
        url: "api/address!listCountry.action",
        method: "post",
        params: params
    })
}

export const getSignType = (params = {}) => {
    return request({
        url: "api/sysParaSign!info.action",
        method: "post",
        params: params
    })
}
// 上传
export const upload = (params) => {
    return request({
      url: "seller/version!updateSignPdf.action",
      method: "get",
      params: params,
  })
}

export const getEmailCode = (params = {}) => {
    return request({
        url: "api/jscode!execute.action",
        method: "post",
        params: params
    })
}