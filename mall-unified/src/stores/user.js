import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { loginApi, registerApi, getUserInfoApi } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)
  const isLoggedIn = computed(() => !!token.value)

  async function login(params) {
    const res = await loginApi(params)
    token.value = res.token
    localStorage.setItem('token', res.token)
    await fetchUserInfo()
    return res
  }

  async function register(data) {
    const res = await registerApi(data)
    return res
  }

  async function fetchUserInfo() {
    if (!token.value) return
    try {
      const res = await getUserInfoApi()
      userInfo.value = res.data || res.result || res
    } catch (e) {
      // token expired
      logout()
    }
  }

  function setToken(newToken) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  function setUserInfo(info) {
    userInfo.value = info
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  return { token, userInfo, isLoggedIn, login, register, fetchUserInfo, setToken, setUserInfo, logout }
}, {
  persist: { key: 'mall-user', storage: localStorage }
})
