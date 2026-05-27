/*!
 * @author atongmu <zhounianlai@teacher.com.cn>
 * date 11/07/2019
 * description The project global config.
 */
const ENV_DEV = 'shop.fairyyy.com' // dev

const ENV_PRO = window.location.hostname//
let base_url = ''
if (process.env.NODE_ENV === 'development') {
    base_url = 'https://' + ENV_DEV + '/wap'
} else {
    base_url = 'https://' + ENV_PRO + '/wap'
}
export default {
    /**
     * @description Request api base url.
     */
    baseUrl: {
        dev:'https://shop.fairyyy.com/wap/',
        // dev: "http://stu.teacher.com.cn",
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
