import axios from 'axios'
import router from '@/router/router.js'
import { Toast, Notify } from 'vant';
import i18n from "@/i18n";
import multiItem from '../store/modules/multiItem'
axios.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded'
// 配置 环境的接口地址
//const BASE_URL = process.env.NODE_ENV === 'production' ? '/wap' : process.env.VUE_APP_BASE_URL + 'wap'

const BASE_URL = process.env.VUE_APP_BASE_URL
// 创建
const request = axios.create({
    baseURL: process.env.VUE_APP_IS_APP ? multiItem.state[process.env.VUE_APP_ITEM_NAME].app_url + '/wap' : BASE_URL,
    timeout: 100000, // 超时时间
    //   withCredentials: true,
    headers: {
        'Content-Type': 'application/json;charset=UTF-8'
    },
    //   transformRequest: [function(data) {
    //     return data
    //   }]
})

// 拦截请求
request.interceptors.request.use(config => {
    if (config.loading) {
        Toast.loading({ duration: 0, forbidClick: true })
    }
    if (!config.params) { // 放在哪里
        config.params = {}
    }
    if (localStorage.getItem('token')) {
        config.params['token'] = localStorage.getItem('token')
    }

    if (!config.params.lang) {
        // if (i18n.i18n.locale == 'en') {
        //     config.params['lang'] = 'en'
        // } else if (i18n.i18n.locale == 'cn') {
        //     config.params['lang'] = 'cn'
        // } else if (i18n.i18n.locale == 'tw') {
        //     config.params['lang'] = 'tw'
        // }
        config.params['lang'] = i18n.i18n.locale
    }

    return config
}, error => {
    Promise.reject(error)
})

/**
 * 烤猫, [7/27/2022 9:08 PM]
 * 0 成功
1 直接显示
105 直接提示“当前还需交易“ + 返回的金额值 + ”,才可提币"
401 是需要实名认证，问客户”未实名认证，是否认证？"
403 无登录信息，跳转登录页面
506 "帐户异常需要进行C3认证，请联系在线客服。"
 */

// 拦截响应
request.interceptors.response.use(res => { // 200开头的
    if (res.config.loading) {
        Toast.clear()
    }
    const { code, data, msg } = res.data
    switch (code / 1) {
        case 0:
            return Promise.resolve(data)
        case 403:
            localStorage.removeItem('token')
            if (router.currentRoute.path !== '/me') {
                router.push({ path: '/login' })
            }
            return
        default:
            Notify({ type: 'danger', message: i18n.i18n.t(msg) });
            console.log('错误1', res)
            return Promise.reject(res.data)
    }
}, error => {
    if (error && error.response) {
        switch (error.response.status) {
            case 400: error.message = '请求错误'; break
            case 401: error.message = '未授权，请登录'; break
            case 403: error.message = '拒绝访问'; break
            case 404: error.message = `请求地址不存在: ${error.response.config.url}`; break
            case 408: error.message = '请求超时'; break
            case 500: error.message = '服务器内部错误'; break
            case 501: error.message = '服务未实现'; break
            case 502: error.message = '网关错误'; break
            case 503: error.message = '服务不可用'; break
            case 504: error.message = '网关超时'; break
            case 505: error.message = 'HTTP版本不受支持'; break
            default:
                //     error.message = Toast.fail({
                //     // icon: 'none',
                //     // message: i18n.t(msg)
                //     message: i18n.t('网络波动请刷新页面')
                //   });
                Notify({ type: 'danger', message: i18n.i18n.t('网络波动请刷新页面') });
                // Promise.reject(error)
                break
        }
    }
    // eslint-disable-next-line prefer-promise-reject-errors
    return Promise.reject(error)
}
)
export default request
