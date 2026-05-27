import Axios from "@/util/http";
import URL from "../config/index";
/**
 * 上传图片
 */
export const UploadApi = `${URL.BASE_URL}/api/uploadimg!execute.action`;

/**
 * 获取用户信息
 * @param {Object} data {token}
 * @returns void
 */
export const UserInfoApi = (data = {}) =>
  Axios.fetch(`/api/localuser!get.action`, data);

/**
 * 获取未读消息数量
 * @param {} data 
 * @returns 
 */
export const ChatUnReadCount = (data = {}) => Axios.fetch(`/api/public/userOnlineChatController!unread.action`, data)

export const ChatUnReadCountPt = (data = {}) => Axios.fetch(`api/newOnlinechat!unread.action`, data)

// 获取客服地址
export const apiGetCustomerService = (data= {}) => Axios.fetch(`api/syspara!getSyspara.action`, data)
