import { theme } from "tailwindcss/stubs/defaultConfig.stub"

// 请求地址
export const BASE_URL = import.meta.env.VITE_APP_BASE_URL

// 请求方法
export const METHODS = { POST: 'POST', GET: 'GET', PUT: 'PUT', PATCH: 'PATCH', DELETE: 'DELETE' }

// 请求超时时间
export const REQUEST_TIMEOUT = 60000

// 表单类型key
export const CONTENT_TYPE = 'Content-Type'

// 表单类型value
export const CONTENT_TYPES = {
    URL_ENCODED: 'application/x-www-form-urlencoded'
}

// 是否携带凭证
export const WITH_CREDENTIALS = false

// API前缀
export const API_PREFIX = '/wap/api'

// 图片服务器地址
export const IMG_PATH = import.meta.env.VITE_APP_IMG_PATH

// 请求频率
export const REQUEST_TIMER = 2000

// socket 地址
export const WS_URL = 'wss://tiktokmall666.com/data/websocket'

/// 默认日线
export const defaultStage = '1day'

export const defaultSeconds = 1 * 24 * 60 * 60 * 1000

// 主题色
export const themeColor = {
    main: '#1552f0',
    'tiktok-wholesale': '#000000'
}

// 需要自定义主题色盘口
export const needChangeMode = ['tiktok-wholesale']
