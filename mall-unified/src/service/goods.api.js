import request from './request'
import {METHODS} from "../config/index.js";

/**
 * 退货列表
 * @param token
 * @returns {Promise<axios.AxiosResponse<any>>}
 * @private
 */
export const _returnApply = () => {
    return request({
        url: "/api/seller/orders/returns",
        method: METHODS.POST
    })
}

export const detailsReturns = (data) => {
    return request({
        url: "/api/seller/orders/return-detail",
        method: METHODS.POST,
        data
    })
}

export const orderListGoods = (data) => {
    return request({
        url: "/api/order/list-goods",
        method: METHODS.POST,
        params: data
    })
}
