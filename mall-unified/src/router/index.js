import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

// ===== 落地页 =====
// ===== PC 商城路由 =====
import pcRoutes from '@/router/pc.routes'
// ===== H5 移动商城路由 =====
import h5Routes from '@/router/h5.routes'
// ===== 商家后台路由 =====
import merchantRoutes from '@/router/merchant.routes'
// ===== 商家移动端路由 =====
import merchantH5Routes from '@/router/merchant-h5.routes'

const routes = [
  // 落地页（安装 PWA 后首次打开就是这里）
  {
    path: '/',
    name: 'Landing',
    component: () => import('@/views/landing/index.vue'),
    meta: { layout: 'blank', title: 'TikTokMall 跨境商城' }
  },
  ...pcRoutes,
  ...h5Routes,
  ...merchantRoutes,
  ...merchantH5Routes,
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    return { top: 0 }
  }
})

// 全局路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  // 商家后台需要登录
  if (to.path.startsWith('/seller/') && !userStore.token && !to.path.includes('/login')) {
    next('/seller/login')
    return
  }

  // 需要登录的页面
  const authRequired = ['/pc/user/', '/pc/order/', '/pc/cart/', '/pc/recharge/']
  const needsAuth = authRequired.some(p => to.path.startsWith(p))
  if (needsAuth && !userStore.token) {
    next('/pc/login')
    return
  }

  next()
})

export default router
