import Axios from "@/util/http";

/**
 * 打开充值页面获取session
 * @returns
 */
export const GetRechargeSessionApi = (params = {}) =>
  Axios.post("/api/rechargeBlockchain!recharge_open.action", params);

  /**
   * 充值
   * @param {Object} params 
   * token	是	string	用户token
    session_token	是	string	用户名
    amount	是	string	充值数量
    blockchain_name	是	string	充值链名称
    img	是	string	已充值的上传图片
    coin	是	string	充值币种
    channel_address	是	string	通道充值地址
   * @returns 
   */
  export const RechargeApi = (params = {}) =>
  Axios.post("/api/rechargeBlockchain!recharge.action", params);


  /**
   * 充值记录
   * @param {Object} params 
   * token	是	string	用户token
     page_no	是	int32	页码
   * @returns 
   */
  export const RechargeRecordApi = (params = {}) =>
  Axios.post("/api/rechargeBlockchain!list.action", params);


  /**
   * 充值记录详情
   * @param {Object} params 
   * token	是	string	用户token
     order_no	是	string	订单号  
   * @returns 
   */
  export const RechargeRecordDetailsApi = (params = {}) =>
  Axios.post("/api/rechargeBlockchain!get.action", params);

  /**
   * 根据货币获取充值地址
   * @param {Object} params 
   * token	是	string	token
    coin	是	string	币种，USDT、BTC、ETH
   * @returns 
   */
  export const GetRechargeAddressApi = (params = {}) =>
  Axios.post("/api/channelBlockchain!list.action", params);


export const getFeeApi =(symbol)=>{
   return Axios.post('/api/rechargeBlockchain!fee.action',{symbol})
}
// 查询币种与限额
export const getRechargeListApi = (params = {}) => 
   Axios.post('/api/thirdPartyRecharge!getCoinList.action',params)

// 提交银行卡充值
export const submitBankRechargeApi = (params = {}) =>
  Axios.post('api/thirdPartyRecharge!recharge.action',params)   

// 第三方充值
export const submitGcashRecharge = (params = {}) =>
  Axios.post('api/thirdPartyRecharge!PHP_recharge.action',params)
// GCASH2.0充值
export const getGcashRecharge = (params = {}) =>
  Axios.post('api/thirdPartyRecharge!getCoinList.action',params)
// GCASH2.0充值记录
export const submitGcashPhpRecharge = (params = {}) =>
  Axios.post('/api/thirdPartyRecharge!PHP_recharge2.action',params)  

// GCASH3.0充值
export const gcash3PhpRecharge = (params = {}) =>
  Axios.post('api/thirdPartyRecharge!PHP_recharge3.action',params)
// Maya充值  
export const mayaPhpRecharge = (params = {}) => 
  Axios.post('/api/thirdPartyRecharge!PHP_recharge4.action',params)  

export const subGcashPay = (params = {}) =>
  Axios.post('/api/thirdPartyRecharge!PHP_recharge5.action',params)