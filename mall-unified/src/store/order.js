import { defineStore } from 'pinia'
import { noPushNum } from '@/service/order.api.js'

export const useOrderStore = defineStore('orderStore', {
  state: () => ({ num: 0 }),
  actions: {
    getNoPushNum() {
      noPushNum().then(res => {
        const noPushNum = res.noPushNum || 0
        if (noPushNum > this.num) {
          document.dispatchEvent(new CustomEvent('orderPlay'))
          document.dispatchEvent(new CustomEvent('reloadOrderList'))
        }
        this.num = noPushNum
      })
    },
    decrement() {
      if (this.num > 0) {
        this.num--
      }
    }
  },
  persist: false // 关闭数据持久化
})
