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
        url: "/wap/seller/orders!list-returns.action",
        method: METHODS.POST
    })
}

export const detailsReturns = (data) => {
    return request({
        url: "/wap/seller/orders!details-returns.action",
        method: METHODS.POST,
        data
    })
}

export const orderListGoods = (data) => {
    return request({
        url: "/wap/api/order!listGoods.action",
        method: METHODS.POST,
        params: data
    })
}
