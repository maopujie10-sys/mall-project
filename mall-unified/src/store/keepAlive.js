import { defineStore } from 'pinia'
import { useStorage } from '@vueuse/core'

export const usekeepAliveStore = defineStore('keepalive', {
  state: () => useStorage('keepalive', {
    keepaliveData: []
  }),
  actions: {
    setKeepAlive(name) {
      const data = JSON.parse(JSON.stringify(this.keepaliveData))
      if (!data.includes(name)) {
        data.push(name)
      }
      
      this.keepaliveData = data.filter(item => item !== '')
      console.log('this.keepaliveData', this.keepaliveData)
    },
    clearKeepAlive() {
      this.keepaliveData = []
    }
  },
  persist: false // 关闭数据持久化
})
