import { post, get } from './index'

// ===== 认证 =====
export function loginApi(params) {
  return post('/api/user/login', params)
}
export function loginByPhoneApi(params) {
  return post('/api/user/login/idcode', params)
}
export function registerApi(data) {
  return post('/api/user/register', data)
}
export function registerUsernameApi(params) {
  return post('/api/user/register/username', params)
}
export function registerPhoneApi(params) {
  return get('/api/user/register', params)
}
export function getUserInfoApi() {
  return get('/api/user/info')
}
export function getHomeDataApi() {
  return get('/api/home')
}
export function searchGoodsApi(keyword, page = 1) {
  return get('/api/product/search', { keyword, page })
}
export function sendVerificationCode(phone) {
  return post('/api/idcode/send', { phone })
}
export function verifyCode(phone, code) {
  return post('/api/idcode/verify', { phone, code })
}
