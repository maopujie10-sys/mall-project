import router from '@/router/router.js'
import store from '@/store'

router.beforeEach(async (to, from, next) => {
  // userinfo
  const TOKEN = localStorage.getItem('token')
  if (TOKEN && !store.getters.userInfo) {
    await store.dispatch('getUserInfo')
  }

  next()
})
