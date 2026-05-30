import request from './request'
import { METHODS } from '@/config'

/**
 * 获取订单详情
 * @param params
 * @returns {*}
 * @private
 */
export const _orderDetail = (data) => {
    return request({
        url: "/wap/api/order/info",
        method: METHODS.POST,
        data
    })
}

/**
 * 获取订单详情列表
 * @param data
 * @returns {*}
 * @private
 */
export const _orderDetailList = (data) => {
    return request({
        url: "/api/order/list-goods",
        loadingPass: true,
        method: METHODS.POST,
        data
    })
}
/**
 * 采购请求
 * @param data
 * @returns {*}
 * @private
 */
export const _buyOrder = (data) => {
    return request({
        url: "/wap/seller/orders/push",
        method: METHODS.POST,
        data
    })
}

/**
 * 采购请求
 * @param data
 * @returns {*}
 * @private
 */
export const noPushNum = (data) => {
    return request({
        url: "/wap/seller/orders/noPushNum",
        method: METHODS.POST,
        loadingPass: true,
        data
    })
}

/**
 * 采购请求
 * @param data
 * @returns {*}
 * @private
 */
export const getOrderLog = (data) => {
    return request({
        url: "/wap/api/orderLog/list",
        method: METHODS.GET,
        params: data
    })
}
