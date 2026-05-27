/*!
 * @author atongmu <zhounianlai@teacher.com.cn>
 * date 11/07/2019
 * description The project global config.
 */
const ENV_DEV = 'tiktokmall666.com' // dev

const ENV_PRO = window.location.hostname//
let base_url = ''
let host_url = ''
if (process.env.NODE_ENV === 'development') {
    base_url = 'https://' + ENV_DEV + '/wap'
    host_url= 'https://' + ENV_DEV + '/'
} else {
    base_url = 'https://' + ENV_PRO + '/wap'
    host_url= 'https://' + ENV_PRO + '/'
}
export const HOST_URL = host_url
export default {
    /**
     * @description Request api base url.
     */
    baseUrl: {
        dev:'http://localhost:8800/wap/', //测试环境
        pro: "/wap/",
    },

    /**
     * @description Index page name.
     */
    homePage: "myProject",

    /**
     * @description Public image base url.
     */
    imageBaseUrl: "",

    /**
     * @description Cookie's expire date, default 7 days.
     */
    cookieExpires: 7,
  }
