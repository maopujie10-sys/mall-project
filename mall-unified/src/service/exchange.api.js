import request from './request'
import {METHODS} from '@/config'

/**
 * 获取所有链地址
 */
export const exchangeGetBlockChain = () => request({
    url: '/api/channel-blockchain/list',
    method: METHODS.POST,
    loadingPass: true,
})


/**
 * 提现费率
 */
export const exchangeGetWithdrawFee = (params) => request({
    url: '/api/withdraw/fee',
    method: METHODS.POST,
    loadingPass: true,
    data: params
})

/**
 * 提现范围
 */
export const exchangeGetWithdrawLimit = () => request({
    url: '/api/withdraw/limit-config',
    method: METHODS.GET,
    loadingPass: true
})

/**
 * 提现 首次进入页面，传递session_token
 */
export const exchangeSetWithdrawToken = (params) => request({
    url: '/api/withdraw/open',
    method: METHODS.POST,
    data: params,
    loadingPass: true
})
/**
 * 提现申请
 */
export const exchangeGetWithdrawApply = (params) => request({
    url: '/api/withdraw/apply',
    method: METHODS.POST,
    data: params
})


/**
 * 充值 首次进入页面，传递session_token
 */
export const exchangeSetRechargeToken = (params) => request({
    url: '/api/recharge/open',
    method: METHODS.POST,
    data: params,
    loadingPass: true
})
/**
 * 充值申请
 */
export const exchangeGetRechargeApply = (params) => request({
    url: '/api/recharge/apply',
    method: METHODS.POST,
    data: params
})


/**
 * 充值记录
 */
export const exchangeGetRechargeRecord = (params) => request({
    url: '/api/recharge/list',
    method: METHODS.POST,
    data: params
})


/**
 * 充值记录 - 详情
 */
export const rechargeDetailsApi = (params) => request({
    url: '/api/recharge/',
    method: METHODS.POST,
    data: params
})


/**
 * 提现记录
 */
export const exchangeGetWithdrawRecord = (params) => request({
    url: '/api/withdraw/list',
    method: METHODS.POST,
    data: params
})

/**
 * 提现记录 - 详情
 */
export const withdrawDetailsApi = (params) => request({
    url: '/api/withdraw/',
    method: METHODS.POST,
    data: params
})

/**
 * 绑定提现地址
 */
export const bindWithdrawAddress = (params) => request({
    url: '/api/user/bind-withdraw-address',
    method: METHODS.POST,
    data: params
})


/**
 * 银行卡充值
 */
export const thirdPartyRecharge = (params) => request({
    url: '/api/third-party-recharge/coin-list',
    method: METHODS.POST,
    data: params
})

/**
 * 银行卡充值-提交
 */
export const thirdPartyRechargeApi = (params) => request({
    url: '/api/third-party-recharge/recharge',
    method: METHODS.POST,
    data: params
})

/**
 * 银行卡充值-提交-gcash
 */
export const thirdPartyRechargePhpApi = (params, type = 'PHP_recharge') => request({
    url: `/api/third-party-recharge/${type}`,
    method: METHODS.POST,
    data: params
})
