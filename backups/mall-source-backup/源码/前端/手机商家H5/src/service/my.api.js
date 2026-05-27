import request from './request'
import { METHODS } from '@/config'


/**
 * 链接测试
 * @returns
 */
export const _test = () => {
    return request({
        url: '/todos/1',
        method: METHODS.GET
    })
}

/**
 * 登陆
 * @param {} user
 * @returns
 */
 export const _login = (user) => {
    return request({
        url: '/user/login',
        method: METHODS.POST,
        data: {
            user
        }
    })
 }

/**
 * 获取用户信息
 * @returns {*}
 * @private
 */
 export const _userInfo = () => {
     return request({
         url: "/wap/api/localuser!get.action",
         method: METHODS.POST,
     })
 }

/**
 * 用户余额
 * @param token
 * @returns {*}
 * @private
 */
export const _userWall = () => {
    return request({
        url: "/wap/api/wallet!getUsdt.action",
        method: METHODS.POST,
    })
}


/**
 * 订单列表
 * @param {} data
 * @returns
 */
 export const orderlist = (data) => {
    return request({
        url: '/wap/seller/orders!list.action',
        method: METHODS.POST,
        data
    })
 }
