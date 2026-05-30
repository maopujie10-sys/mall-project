import axios from 'axios'
import { ElMessage } from 'element-plus'

//  localStorage  Token
function getToken() {
  return localStorage.getItem('agent_token') || localStorage.getItem('friday_token') || 'kWs4N6GiD4vtjnuHV31r14m6HPpKttBSI35lFnpiI90'
}

function unwrapResponse(response) {
  const data = response.data
  if (data && typeof data === 'object' && 'code' in data) {
    if (data.code !== 0 && data.code !== 200) {
      ElMessage.error(data.message || '')
      return Promise.reject(new Error(data.message || ''))
    }
    return data.data !== undefined ? data.data : data
  }
  return data
}

function handleError(error) {
  const msg = error.response?.data?.detail || error.response?.data?.message || error.message || ''
  if (error.response?.status === 403) {
    ElMessage.error('Token  Agent Token')
  } else {
    ElMessage.error(msg)
  }
  return Promise.reject(error)
}

// Java  (mall-app:8080)
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})
api.interceptors.request.use((c) => c, (e) => Promise.reject(e))
api.interceptors.response.use(unwrapResponse, handleError)

// Agent  (mall-agent:9000)
const agentApi = axios.create({
  baseURL: '/ai/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})
//  X-Agent-Token
agentApi.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers['X-Agent-Token'] = token
  }
  return config
}, (e) => Promise.reject(e))
agentApi.interceptors.response.use(unwrapResponse, handleError)

export { api, agentApi, getToken }
export default api
