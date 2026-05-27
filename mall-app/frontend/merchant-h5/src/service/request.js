import axios from 'axios'
import {ref} from 'vue'
// import qs from 'qs'
import { Toast, Notify } from 'vant'
import { BASE_URL, REQUEST_TIMEOUT, CONTENT_TYPE, CONTENT_TYPES, WITH_CREDENTIALS, METHODS } from '@/config'
import i18n from "@/i18n/index.js";
// import store from '@/store'
import { useUserStore } from "@/store/user.js";
import moment from "moment-timezone";

// 个性化返回错误提示信息接口
const diyUrlData = ['/wap/seller/goods!update.action', '/wap/seller/goods!addOrUpdate.action', '/wap/api/cms!get.action']

// 活动接口个性化未登录
const diyLogoutData = ['/wap/api/activity/lottery!getPoints.action', '/wap/api/activity/lottery!draw.action', '/wap/api/activity/lottery!pageListMyPrize.action']

// 是否触发了系统轮询请求
const hasTargetSysRequset = ref(false)

// 获取时区信息
moment.tz.setDefault('Asia/Shanghai')
const timezone = moment.tz.guess(true)

const logout = (flag = false) => {
  let userStore = useUserStore()
  userStore.logout(flag) // 恢复初始化
}


const service = axios.create({
  baseURL: BASE_URL,
  withCredentials: WITH_CREDENTIALS,
  timeout: REQUEST_TIMEOUT, // 请求超时时间
  headers: {
    [CONTENT_TYPE]: CONTENT_TYPES.URL_ENCODED
  }
})

// 请求拦截
service.interceptors.request.use(config => {
  if (!config) {
    config = {}
  }
  if (!config.headers) {
    config.headers = {}
  }
  if (config.method === METHODS.POST) {
    if (config.data) {
      // config.data = qs.stringify(config.data)
    }
  }
  const userStore = useUserStore()
  const TOKEN = userStore?.userInfo?.token

  if (TOKEN) { // 携带token
    // if (!config.headers['Authorization']) {
    //   config.headers['Authorization'] = `bearer ${TOKEN}`
    // }
    if (!config.params) {
      config.params = {}
    }
    config.params['token'] = TOKEN
  }
  if (config.loading) {
    Toast.loading({ forbidClick: true, duration: 0 })
  }

  // lang
  if (!config.params) {
    config.params = {}
  }
  config.params.lang = i18n.global.locale.value || 'en'
  config.params.tz = timezone || 'Asia/Shanghai'
  return config
}, error => {
  return Promise.reject(error)
})

// 响应拦截
service.interceptors.response.use(res => {
  if (!res.config.loadingPass) {
    Toast.clear()
  }

  const { data: { code, data, msg } } = res
  if (res.config['returnType'] === 'origin') { // 原样返回
    return Promise.resolve(res.data)
  }
  switch (Number(code)) {
    case 0: // 正确响应
      if (!hasTargetSysRequset.value && res.config.params.token) {
        hasTargetSysRequset.value = true
        // 到账通知
        document.dispatchEvent(new CustomEvent('getMoneyInfoHandle'))
      }
      return Promise.resolve(data)
    case 200: // 正确响应
      if (!hasTargetSysRequset.value && res.config.params.token) {
        hasTargetSysRequset.value = true
        // 到账通知
        document.dispatchEvent(new CustomEvent('getMoneyInfoHandle'))
      }
      return Promise.resolve(data)
    case 403:   // 登录状态已过期，您可以继续留在该页面，或者重新登录
      if (diyLogoutData.includes(res.config.url)) {
        logout(true)
        // 不进入登录页面
        return Promise.reject('login');
      } else {
        logout()
        break
      }
    default: // 直接弹出消息
      if (msg === '暂无用户') {
        logout()
      } else {
        if (diyUrlData.includes(res.config.url)) {
          return Promise.reject(res.data)
        } else {
          Toast({ message: i18n.global.t(msg), type: 'fail', duration: 2000 })
          return Promise.reject(msg);
        }
      }
  }
},
  error => { // 网络状态监控
    if (error && error.request) {
      const status = error.request['status']
      switch (status) {
        case 424:
          logout()
          break
        case 404:
          Toast({ message: i18n.global.t('接口未找到'), type: 'fail', duration: 2000 })
          break
        case 415:
          Toast({ message: 'HTTP协议不匹配，请确认', type: 'fail', duration: 2000 })
          break
        case 428:
          Toast({ message: '验证码不合法', type: 'fail', duration: 2000 })
          break
        // case 500:
        //   Toast({ message: '服务未启动', type: 'fail', duration: 2000 })
        //   break
        // default:
        //   Toast({ message: '服务错误', type: 'fail', duration: 2000 })
        //   break
        default:
          // console.log(error)
          Toast({ message: error.message || '服务错误', type: 'fail', duration: 2000 })

      }
    } else {
      Toast({ message: error.message || '服务错误', type: 'fail', duration: 2000 })
    }

    return Promise.reject(error)
  }
)

export default service