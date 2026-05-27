import request from "@/request";

// 获取验证码
export const getIdcode = function(params) {
  return request({
    url: "api/idcode!execute.action",
    method: "post",
    params: params
  })
}

// 校验验证码
export const verifyCode = function(params) {
  return request({
    url: "api/localuser!verify_code.action",
    method: "post",
    params: params
  })
}

// 通过电话号码或邮箱修改密码
export const updatePwdByVerify = function(params) {
  return request({
    url: "/api/user!resetpsw.action",
    method: "post",
    params: params
  })
}

// 搜索
export const searchKeyword = function(params) {
  return request({
    url: "api/sellerGoods!search-keyword.action",
    method: "post",
    params
  })
}

// 搜索商品列表
export const searchKeywordGoods = function(params) {
  return request({
    url: "api/sellerGoods!search-goods.action",
    method: "post",
    params
  })
}
