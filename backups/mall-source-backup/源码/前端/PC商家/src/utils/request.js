import axios from 'axios'
import {MessageBox, Notification} from 'element-ui'
import store from '@/store'
import {getToken} from '@/utils/auth'
import {i18n} from "@/lang";
import moment from "moment-timezone";

const BASE_URL = "https://"+ window.location.hostname +"/wap"

let setTimeout = null
// create an axios instance
const service = axios.create({
    baseURL: BASE_URL, // url = base url + request url
    headers: {
        'Content-Type': 'application/json;',
    },
    // withCredentials: true, // send cookies when cross-domain requests
    timeout: 30000 // request timeout
})

// request interceptor
service.interceptors.request.use(config => {
        // isLoading = true 时 显示loading
        if (config.isLoading) {
            store.dispatch('app/deleteLoadingTimeout')
            store.dispatch('app/setLoading', true)
        }
        if (config.unNeedWap) { // 不需要wap
            config.baseURL = config.baseURL.replace('wap/', '')
        }
        if (!config.params) {
            config.params = {}
        }
        if (getToken()) {
            config.params['token'] = getToken()
        }
        config.params.tz = moment.tz.guess(true)
        config.params.lang = store.getters.lang
        return config
    },
    error => {
        // do something with request error
        console.log(error) // for debug
        return Promise.reject(error)
    }
)

// response interceptor
service.interceptors.response.use(response => {
        if (response.config.isLoading) {
            store.dispatch('app/setLoading', false)
            store.dispatch('app/setLoadingTimeout', setTimeout)
        }
        const res = response.data
        if (res.code == 403) {
            localStorage.removeItem('token')
            store.commit('chat/DELETE_MASSAGE_INTERVAL')
            window.setTimeout(() => {
                MessageBox.confirm(i18n.t("你的账号在其他地方登录,你被迫退出"), i18n.t("确认登出"), {
                    confirmButtonText: i18n.t('重新登录'),
                    // cancelButtonText: i18n.t('取消'),
                    showCancelButton: false,
                    type: 'warning'
                }).then(() => {
                    store.dispatch('user/resetToken').then(() => {
                        location.reload()
                    })
                }).catch(() => {
                    store.dispatch('user/resetToken').then(() => {
                        location.reload()
                    })
                })
            }, 100);
        }
        // if the custom code is not 20000, it is judged as an error.
        if (parseInt(res.code) !== 0) {
            if (response.config.unNeedWap && parseInt(res.code) === 200) {
                return res
            }
            if (parseInt(res.code) === -1) {
                console.log('您没有认证商家，无法操作')
            } else {
                window.setTimeout(() => {
                    Notification({
                        title: i18n.t('错误'),
                        message: i18n.t(res.msg, res.data) || 'Error',
                        type: 'error',
                        duration: 5 * 1000
                    })
                }, 100);
            }


            // 50008: Illegal token; 50012: Other clients logged in; 50014: Token expired;
            if (res.code === 50008 || res.code === 50012 || res.code === 50014) {
                // to re-login
                window.setTimeout(() => {
                    MessageBox.confirm(i18n.t("你的账号在其他地方登录,你被迫退出"), i18n.t("确认登出"), {
                        confirmButtonText: i18n.t('重新登录'),
                        // cancelButtonText: i18n.t('取消'),
                        showCancelButton: false,
                        type: 'warning'
                    }).then(() => {
                        store.dispatch('user/resetToken').then(() => {
                            location.reload()
                        })
                    }).catch(() => {
                        store.dispatch('user/resetToken').then(() => {
                            location.reload()
                        })
                    })
                }, 100);
            }
            return Promise.reject(new Error(res.message || 'Error'))
        } else {
            return res
        }
    },
    error => {
        console.log('err' + error) // for debug
        Notification({
            title: i18n.t('错误'),
            message: i18n.t(error.msg, error.data) || 'Error',
            type: 'error',
            duration: 2 * 1000
        })
        return Promise.reject(error)
    }
)

export default service
