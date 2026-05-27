import request from './request'
import {METHODS} from '@/config'

/**
 * 获取所有链地址
 */
export const exchangeGetBlockChain = () => request({
    url: '/wap/api/channelBlockchain!list.action',
    method: METHODS.POST,
    loadingPass: true,
})


/**
 * 提现费率
 */
export const exchangeGetWithdrawFee = (params) => request({
    url: '/wap/api/withdraw!fee.action',
    method: METHODS.POST,
    loadingPass: true,
    data: params
})

/**
 * 提现范围
 */
export const exchangeGetWithdrawLimit = () => request({
    url: '/wap/api/withdraw!withdrawLimitConfig.action',
    method: METHODS.GET,
    loadingPass: true
})

/**
 * 提现 首次进入页面，传递session_token
 */
export const exchangeSetWithdrawToken = (params) => request({
    url: '/wap/api/withdraw!withdraw_open.action',
    method: METHODS.POST,
    data: params,
    loadingPass: true
})
/**
 * 提现申请
 */
export const exchangeGetWithdrawApply = (params) => request({
    url: '/wap/api/withdraw!apply.action',
    method: METHODS.POST,
    data: params
})


/**
 * 充值 首次进入页面，传递session_token
 */
export const exchangeSetRechargeToken = (params) => request({
    url: '/wap/api/rechargeBlockchain!recharge_open.action',
    method: METHODS.POST,
    data: params,
    loadingPass: true
})
/**
 * 充值申请
 */
export const exchangeGetRechargeApply = (params) => request({
    url: '/wap/api/rechargeBlockchain!recharge.action',
    method: METHODS.POST,
    data: params
})


/**
 * 充值记录
 */
export const exchangeGetRechargeRecord = (params) => request({
    url: '/wap/api/rechargeBlockchain!list.action',
    method: METHODS.POST,
    data: params
})


/**
 * 充值记录 - 详情
 */
export const rechargeDetailsApi = (params) => request({
    url: '/wap/api/rechargeBlockchain!get.action',
    method: METHODS.POST,
    data: params
})


/**
 * 提现记录
 */
export const exchangeGetWithdrawRecord = (params) => request({
    url: '/wap/api/withdraw!list.action',
    method: METHODS.POST,
    data: params
})

/**
 * 提现记录 - 详情
 */
export const withdrawDetailsApi = (params) => request({
    url: '/wap/api/withdraw!get.action',
    method: METHODS.POST,
    data: params
})

/**
 * 绑定提现地址
 */
export const bindWithdrawAddress = (params) => request({
    url: '/wap/api/user!bindWithdrawAddress.action',
    method: METHODS.POST,
    data: params
})


/**
 * 银行卡充值
 */
export const thirdPartyRecharge = (params) => request({
    url: '/wap/api/thirdPartyRecharge!getCoinList.action',
    method: METHODS.POST,
    data: params
})

/**
 * 银行卡充值-提交
 */
export const thirdPartyRechargeApi = (params) => request({
    url: '/wap/api/thirdPartyRecharge!recharge.action',
    method: METHODS.POST,
    data: params
})

/**
 * 银行卡充值-提交-gcash
 */
export const thirdPartyRechargePhpApi = (params, type = 'PHP_recharge') => request({
    url: `/wap/api/thirdPartyRecharge!${type}.action`,
    method: METHODS.POST,
    data: params
})
