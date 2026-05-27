import request from './request'
import { METHODS } from '@/config'

// 获取资金记录
const _getMoneyLogList = params => {
  return request({
    url: "/wap/api/moneylog!list.action",
    method: METHODS.POST,
    data: params
  })
}

export {
  _getMoneyLogList,
}