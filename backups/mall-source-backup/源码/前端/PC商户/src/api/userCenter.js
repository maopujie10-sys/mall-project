import Axios, { getCurrentLang } from "@/util/http";
import axios from "axios";
import { ES_TOKEN } from "@/common/constant";
import URL from "@/config/index";

/**
 * 用户收货地址列表
 * @returns
 */
export const AddressListApi = (params = {}) =>
  Axios.post("/api/address!list.action", params);

/**
 * 添加收货地址
 * use	是	int	受否默认，1：默认；0：普通
    phone	String	手机号
    email	String	评分
    contacts	String	联系人
    postcode	String	邮编
    country	String	国家
    province	String	州/省
    city	String	市
    address	String	地址
 * @param {Object} params
 * @returns
 */
export const AddressAddApi = (params = {}) =>
  Axios.post("/api/address!add.action", params);

/**
 * 修改收货地址
 * use	是	int	受否默认，1：默认；0：普通
    phone	String	手机号
    email	String	评分
    contacts	String	联系人
    postcode	String	邮编
    country	String	国家
    province	String	州/省
    city	String	市
    address	String	地址
 * @param {Object} params
 * @returns
 */
export const AddressEditApi = (params = {}) =>
  Axios.post("/api/address!edit.action", params);

// 收货地址-获取国家
export const apiListCountry = (params = {}) => 
  Axios.post("api/address!listCountry.action", params);

// 收货地址-获取洲/省
export const apiListState = ( params = {}) => 
  Axios.post("api/address!listState.action", params);


// 收货地址-获取城市
export const apiListCity = (params = {}) => 
  Axios.post("api/address!listCity.action", params);
 
/**
 * 删除收货地址
 * id	String	ID
 * @param {Object} params
 * @returns
 */
export const AddressDelApi = (params = {}) =>
  Axios.post("/api/address!del.action", params);

/**
 * 修改登录密码
 * @param {Object} params
 * token	是	string	token
old_password	是	string	用户名
password	是	string	密码
comfirm_password	是	string	确认密码
 * @returns
 */
export const UpdateLoginPasswordApi = (params = {}) =>
  Axios.post("/api/user!updateOldAndNewPsw.action", params);

/**
 * 获取用户余额
 * token	是	string	token
 * @param {Object} params
 * @returns
 */
export const GetUserBalanceApi = (params = {}) =>
  Axios.post("/api/wallet!getUsdt.action", params);

/**
   * 设置资金密码
   * @param {Object} params 
   * token	是	string	token
safeword	是	string	密码
re_safeword	是	string	重复密码
   * @returns 
   */
export const SetSafewordApi = (params = {}) =>
  Axios.post("/api/user!setSafewordReg.action", params);

/**
 * 修改资金密码
 * @param {Object} params
 * token	是	string	token
old_safeword	是	string	旧密码
safeword	是	string	资金密码
re_safeword	是	string	重复资金密码
 * @returns
 */
export const UpdateSafewordApi = (params = {}) =>
  Axios.post("/api/user!updateOldAndNewSafeword.action", params);

/**
 * 收藏商品列表
 * @param {Object} params
token	是	string	用户token
pageNum	是	int	页码
pageSize	是	int	长度
lang	是	string	语言
 * @returns
 */
export const KeepGoodsListApi = (params = {}) => {
  // return  Axios.post("/api/keepGoods!list.action", params);
  const { lang } = getCurrentLang()
  const token = localStorage.getItem(ES_TOKEN);

  return axios({
    url: URL.BASE_URL + "api/keepGoods!list.action" + `?token=${token}&lang=${lang}`,
    method: 'post',
    params: params
  }).then((res) => {
    const response = res.data;
    if (response.code === '0') {
      return response
    }
    return Promise.reject(response)
  });
}
  

/**
 * 收藏商品
 * @param {Object} params
sellerGoodsId	是	string	商品id
token	是	string	用户token
 * @returns
 */
export const KeepGoodsAddApi = (params = {}) =>
  Axios.post("/api/keepGoods!add.action", params);

/**
 * 取消收藏商品
 * @param {Object} params
sellerGoodsId	是	string	商品id
token	是	string	用户token
 * @returns
 */
export const KeepGoodsCancelApi = (params = {}) =>
  Axios.post("/api/keepGoods!del.action", params);

/**
 * 收藏商家列表
 * @param {Object} params
token	是	string	用户token
pageNum	是	int	页码
pageSize	是	int	长度
 * @returns
 */
export const FocusSellerListApi = (params = {}) =>
  Axios.post("/api/focusSeller!list.action", params);

/**
 * 关注店家
 * @param {Object} params
sellerId	是	string	店家id
token	是	string	用户token
 * @returns
 */
export const FocusSellerAddApi = (params = {}) =>
  Axios.post("/api/focusSeller!add.action", params);

/**
 * 关注店家
 * @param {Object} params
focusSellerId	是	string	关注店家id
token	是	string	用户token
 * @returns
 */
export const FocusSellerDelApi = (params = {}) =>
  Axios.post("/api/focusSeller!del.action", params);

/**
   * 消息列表
   * @param {Object} params 
   * token	是	string	token
message_id	否	string	最后读到的消息ID  
   * @returns 
   */
export const OnlinechatApi = (params = {}) =>
  Axios.post("/api/newOnlinechat!list.action", params);

/**
   * 发送消息
   * @param {Object} params 
   * token	是	string	token
type	是	string	消息类型：text、img
content	是	string	内容，如果type为img，则是base64编码的图片
file	是	File	文件，如果type为img，不能为空
   * @returns 
   */
export const OnlinechatSendApi = (params = {}) =>
  Axios.post("/api/newOnlinechat!send.action", params);

/**
 * 未读消息
 * @param {Object} params
 * @returns
 */
export const OnlinechatUnreadApi = (params = {}) =>
  // Axios.post("/api/newOnlinechat!unread.action", params);
  Axios.fetch("/public/userOnlineChatController!unread.action", params);

/**
 * 商品收藏数量
 * @param {Object} params
 * @returns
 */
export const keepGoodsCount = (params = {}) =>
  Axios.post("/api/keepGoods!count.action", params);

/**
 * 关注店铺数量
 * @param {Object} params
 * @returns
 */
export const focusSellerCount = (params = {}) =>
Axios.post("/api/focusSeller!count.action", params);


export const changeUserAvatar = (params = {}) =>
Axios.post("/api/localuser!refreshAvatar.action", params);