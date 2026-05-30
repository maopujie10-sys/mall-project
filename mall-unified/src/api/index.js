import axios from 'axios'
import { ElMessage } from 'element-plus'

// baseURL 留空，每个 API 自己带 /api 前缀，统一管理
const request = axios.create({
  baseURL: '',
  timeout: 30000,
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
})

// 请求拦截器：自动带 token
request.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：统一错误处理
request.interceptors.response.use(
  res => {
    const data = res.data
    if (data && data.code !== undefined && data.code !== 0 && data.code !== '0') {
      ElMessage.error(data.msg || data.message || '请求失败')
      return Promise.reject(new Error(data.msg))
    }
    return data
  },
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
    } else if (err.response?.status >= 500) {
      ElMessage.error('服务器错误，请稍后重试')
    } else if (err.message && !err.message.includes('Network Error')) {
      // 静默处理网络错误
    }
    return Promise.reject(err)
  }
)

export default request

export function get(url, params) {
  return request({ url, method: 'get', params })
}

export function post(url, data) {
  const params = new URLSearchParams()
  if (data) {
    Object.entries(data).forEach(([k, v]) => {
      if (v !== undefined && v !== null) params.append(k, v)
    })
  }
  return request({ url, method: 'post', data: params })
}

export function put(url, data) {
  const params = new URLSearchParams()
  if (data) {
    Object.entries(data).forEach(([k, v]) => {
      if (v !== undefined && v !== null) params.append(k, v)
    })
  }
  return request({ url, method: 'put', data: params })
}

export function del(url, params) {
  return request({ url, method: 'delete', params })
}

export function postJson(url, data) {
  return request({ url, method: 'post', data, headers: { 'Content-Type': 'application/json' } })
}

export function upload(url, file, extraData = {}) {
  const form = new FormData()
  form.append('file', file)
  Object.entries(extraData).forEach(([k, v]) => form.append(k, v))
  return request({ url, method: 'post', data: form, headers: { 'Content-Type': 'multipart/form-data' } })
}
