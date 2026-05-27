import { defineStore } from 'pinia'
import { customerServiceUrl } from '@/service/user.api.js'

export const useSystemStore = defineStore('systemStore', {
  state: () => ({
    customer_service_url: '',
    isArLang: false,
    notCnLang: false,
    showNotic: false
  }),
  actions: {
    getServeceUrl() {
      customerServiceUrl().then(res => {
        this.customer_service_url = res.customer_service_url || ''
      })
      
    },
    setIsArLang(flag) {
      this.isArLang = flag
    },
    setNotCnLang(flag) {
      this.notCnLang = flag
    },
    setShowNotic(flag) {
      this.showNotic = flag
    }
  },
  persist: false // 关闭数据持久化
})
