import axios from 'axios'
import { ElMessage } from 'element-plus'

function unwrapResponse(response) {
  const data = response.data
  if (data && typeof data === 'object' && 'code' in data) {
    if (data.code !== 0 && data.code !== 200) {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message || '请求失败'))
    }
    return data.data !== undefined ? data.data : data
  }
  return data
}

function handleError(error) {
  const message = error.response?.data?.message || error.message || '网络错误'
  ElMessage.error(message)
  return Promise.reject(error)
}

// Java 商城后端 (mall-app:8080)
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})
api.interceptors.request.use((c) => c, (e) => Promise.reject(e))
api.interceptors.response.use(unwrapResponse, handleError)

// Agent 后端 (mall-agent:9000)
const agentApi = axios.create({
  baseURL: '/ai/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})
agentApi.interceptors.request.use((c) => c, (e) => Promise.reject(e))
agentApi.interceptors.response.use(unwrapResponse, handleError)

export { api, agentApi }
export default api
