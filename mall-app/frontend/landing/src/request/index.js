import axios from 'axios'
import { Toast, Notify } from 'vant';
import { i18n } from "@/i18n";

axios.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded'
// 配置 环境的接口地址
// const BASE_URL = window.location.protocol + "//" + window.location.host + '/wap/'

// const BASE_URL = process.env.NODE_ENV === 'production' ? 'https://rfbhabkjk.com/wap/' : 'https://rfbhabkjk.com/wap/'
const BASE_URL = process.env.NODE_ENV === 'production' ? '/wap' : 'http://localhost:8800/wap/'
// 创建
const request = axios.create({
    baseURL: BASE_URL,
    timeout: 30000, // 超时时间
    headers: {
        'Content-Type': 'application/json;charset=UTF-8'
    }
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
    if (i18n.locale === 'zh-CN') {
        config.params['lang'] = 'cn'
    } else if (i18n.locale === 'CN') {
        config.params['lang'] = 'tw'
    } else if (i18n.locale === 'ko') {
        config.params['lang'] = 'en'
    } else if (i18n.locale === 'de') {
        config.params['lang'] = 'de'
    } else {
        config.params['lang'] = 'en'
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
 506 "账户异常需要进行C3认证，请联系在线客服。"
 */

// 拦截响应
request.interceptors.response.use(res => {
    // 200开头的
    if (res.config.loading) {
        Toast.clear()
    }
    const { code, data, msg } = res.data
    switch (code / 1) {
        case 0:
            return Promise.resolve(data)
        case 403:
            localStorage.removeItem('token')
            // this.$router.push({path:'/login'})
            // window.location = '/#/login'
            return
        default:
            Notify({
                color: '#FFFFFF',
                background: '#ff0000',
                message: i18n.t(msg)
            });
            Toast.fail(i18n.t(msg))    
            console.log('错误')
            return Promise.reject(res.data)
    }
}, error => {
    if (error && error.response) {
        switch (error.response.status) {
            case 400:
                error.message = i18n.t('请求错误');
                break
            case 401:
                error.message = i18n.t('未授权，请登录');
                break
            case 403:
                error.message = i18n.t('拒绝访问');
                break
            case 404:
                error.message = i18n.t('请求地址不存在:') + error.response.config.url;
                break
            case 408:
                error.message = i18n.t('请求超时');
                break
            case 500:
                error.message = i18n.t('服务器内部错误');
                break
            case 501:
                error.message = i18n.t('服务未实现');
                break
            case 502:
                error.message = i18n.t('网关错误');
                break
            case 503:
                error.message = i18n.t('服务不可用');
                break
            case 504:
                error.message = i18n.t('网关超时');
                break
            case 505:
                error.message = i18n.t('HTTP版本不受支持');
                break
            default:
                error.message = Toast.fail({
                    // icon: 'none',
                    // message: i18n.t(msg)
                    message: i18n.t('网络波动请刷新页面')
                });
                Promise.reject(error.data)
                break
        }
    }
    // eslint-disable-next-line prefer-promise-reject-errors
    return Promise.reject(error)
}
)
export default request
