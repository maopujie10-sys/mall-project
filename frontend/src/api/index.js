import axios from 'axios'
import { ElMessage } from 'element-plus'

// Shared response interceptor for code-wrapper APIs
function unwrapResponse(response) {
  const data = response.data
  if (data && typeof data === 'object' && 'code' in data) {
    if (data.code !== 0 && data.code !== 200) {
      ElMessage.error(data.message || '璇锋眰澶辫触')
      return Promise.reject(new Error(data.message || '璇锋眰澶辫触'))
    }
    return data.data !== undefined ? data.data : data
  }
  return data
}

function handleError(error) {
  const message = error.response?.data?.message || error.message || '缃戠粶閿欒'
  ElMessage.error(message)
  return Promise.reject(error)
}

// Java backend (mall-app:8080) 鈥?Nginx routes /api/* 鈫?Java
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})
api.interceptors.request.use((c) => c, (e) => Promise.reject(e))
api.interceptors.response.use(unwrapResponse, handleError)

// Agent backend (mall-agent:9000) 鈥?Nginx routes /ai/api/* 鈫?Agent
const agentApi = axios.create({
  baseURL: '/ai/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})
agentApi.interceptors.request.use((c) => c, (e) => Promise.reject(e))
agentApi.interceptors.response.use(unwrapResponse, handleError)

export { api, agentApi }
export default api
