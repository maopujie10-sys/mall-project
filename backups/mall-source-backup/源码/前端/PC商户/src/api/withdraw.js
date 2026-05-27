import Axios from "@/util/http";

/**
 * 提现记录
 * token	是	string	用户token
page_no	是	int32	页码  
 * @returns
 */
export const WithdrawRecordApi = (params = {}) =>
  Axios.post("/api/withdraw!list.action", params);

/**
 * 获取token
 * @returns 
 */
export const WithdrawGetToken = (params = {}) =>
  Axios.post("/api/rechargeBlockchain!recharge_open.action")

/**
 * 提现申请
 * @param {Object} params
 * token	是	string	token
session_token	是	string	重复提交参数
safeword	是	string	资金密码
amount	是	Double	提现金额
from	是	string	客户转出地址
channel	否	string	渠道 目前只有USDT .
 * @returns
 */
export const WithdrawApplyApi = (params = {}) =>
  Axios.post("/api/withdraw!apply.action", params);

/**
 * 获取提现费率
 * @param {Objet} params 
 * @returns 
 */
// export const WithdrawGetFee = (params = {}) =>
//   Axios.post("/api/withdraw!fee.action", params);

  export const WithdrawGetFee = (channel)=>{
    return Axios.post('/api/withdraw!fee.action',{channel})
  }
/**
 * 提现记录详情
 * @param {Object} params
 * token	是	string	用户token
order_no	是	string	订单号
 * @returns
 */
export const WithdrawDetailsApi = (params = {}) =>
  Axios.post("/api/withdraw!get.action", params);

export const Widerrufsfrist = (params = {}) =>
  Axios.post("/api/withdraw!withdraw_open.action", params);  

export const BindWithdrawAddress = (params = {}) =>
  Axios.post("/api/user!bindWithdrawAddress.action", params);  