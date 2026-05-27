import Axios from "@/util/http";

/**
 * 提交订单
 * @param {Object} params 
    token	是	string	用户token
    orderInfo	是	string	商品ID,商品数量
    addressId	否	string	addressId 收到地址ID
 * @returns 
 */
export const SubmitOrderApi = (params = {}) =>
  Axios.post("/api/order!submit.action", params);

/**
 * 支付
 * @param {Object} params
 * token	是	string	用户token
orderId	是	string	订单ID（多单逗号隔开）
safeword	是	string	资金密码
 * @returns
 */
export const PayOrderApi = (params = {}) =>
  Axios.post("/api/order!pay.action", params);

/**
 * 取消订单
 * @param {Object} params
 * token	是	string	用户token
orderId	是	string	订单ID,
returnReason	是	string	取消理由（1：未收到货2：不喜欢，不想要3：卖家发错货4：假冒品牌5：少发、漏发6：收到商品破损7：存在质量问题8：与商家协商一致退款9：其他原因）
 * @returns
 */
export const CancelOrderApi = (params = {}) =>
  Axios.post("/api/order!cancel.action", params);

/**
 * 订单列表
 * @param {Object} params
 * token	是	string	用户token
status	是	int	状态（-1=已取消）（0=待付款）（1=待发货）（2=已确认）（3=待收货）（4=已收获）（5=已评价）（6=退款)
pageNum	是	int	默认1
pageSize	是	int	默认20
 * @returns
 */
export const OrderListApi = (params = {}) =>
  Axios.post("/api/order!listMain.action", params);

/**
 * 订单详情
 * @param {Object} params
 * token	是	string	用户token
orderId	是	orderId	订单ID
 * @returns
 */
export const OrderDetailsApi = (params = {}) =>
  Axios.post("/api/order!info.action", params);

/**
 * 订单商品
 * @param {Object} params
 * token	是	string	用户token
orderId	是	string	订单ID
 * @returns
 */
export const OrderGoodsApi = (params = {}) =>
  Axios.post("/api/order!listGoods.action", params);

/**
   * 收货
   * @param {Object} params 
   * token	是	string	用户token
orderId	是	string	订单ID
   * @returns 
   */
export const OrderReceiptApi = (params = {}) =>
  Axios.post("/api/order!receipt.action", params);

/**
   * 退货
   * @param {Object} params 
   * token	是	string	用户token
orderId	是	string	订单ID
   * @returns 
   */
export const OrderReturnApi = (params = {}) =>
  Axios.post("/api/order!returns.action", params);

/**
 * 添加评论
 * @param {Object} params
 * sellerGoodsId	是	string	商品id
    evaluationType	是	string	评价类型 1-好评 2-中评 3-差评
    rating	是	int	评分
    content	是	string	评论内容
 * @returns
 */
export const OrdeEvaluationApi = (params = {}) =>
  Axios.post("/api/evaluation!add.action", params);

/**
 * 物流信息（订单商品状态
 * @param {} params 
 * orderId 订单ID
 * @returns 
 */
export const OrderGetLogistics = (params = {}) =>
  Axios.post("/api/orderLog!list.action", params);

export const AddOrderEvaluateList = (params = {}) => Axios.postBody('/api/evaluation!addList.action', params)