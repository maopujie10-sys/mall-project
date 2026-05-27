import { defineStore } from 'pinia'

export const useRouterStore = defineStore({
  id: 'routerTrans',
  state: () => ({
    routerTransType: ''
  }),
  actions: {
    async routerTransHandle(to, form) {
      const toPath = to.path
      const formPath = form.path
      const toLevel = to.meta.level || ''
      const formLevel = form.meta.level || ''
      if (!formPath || !formLevel || (Number(toLevel) === 1 && Number(formLevel) === 1)) {
        this.routerTransType = 'van-fade'
      } else {
        console.log('formLevel', formLevel)
        console.log('toLevel', toLevel)
        if (Number(formLevel) < Number(toLevel)) {
          this.routerTransType = 'van-slide-left'
        } else {
          this.routerTransType = 'van-slide-right'
        }
      }
    }
  }
})
