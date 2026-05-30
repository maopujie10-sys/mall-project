// 请求地址 — 统一 REST
export const BASE_URL = ''
export const API_PREFIX = '/api'

// 请求方法
export const METHODS = { POST: 'POST', GET: 'GET', PUT: 'PUT', PATCH: 'PATCH', DELETE: 'DELETE' }
export const REQUEST_TIMEOUT = 60000
export const CONTENT_TYPE = 'Content-Type'
export const CONTENT_TYPES = { URL_ENCODED: 'application/x-www-form-urlencoded' }
export const WITH_CREDENTIALS = false
export const IMG_PATH = import.meta.env.VITE_APP_IMG_PATH
export const REQUEST_TIMER = 2000
export const WS_URL = 'wss://tiktokmall666.com/data/websocket'
export const defaultStage = '1day'
export const defaultSeconds = 1 * 24 * 60 * 60 * 1000

export const themeColor = {
    main: '#1552f0',
    'tiktok-wholesale': '#000000'
}
export const needChangeMode = ['tiktok-wholesale']
