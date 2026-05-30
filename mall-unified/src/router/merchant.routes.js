// 商家后台路由
export default [
  {
    path: '/seller/login',
    name: 'MerchantLogin',
    component: () => import('@/views/merchant/login/index.vue'),
    meta: { layout: 'merchant', title: '商家登录' }
  },
  {
    path: '/seller/register',
    name: 'MerchantRegister',
    component: () => import('@/views/merchant/register/index.vue'),
    meta: { layout: 'merchant', title: '商家注册' }
  },
  {
    path: '/seller/dashboard',
    name: 'MerchantDashboard',
    component: () => import('@/views/merchant/dashboard/index.vue'),
    meta: { layout: 'merchant', title: '商家仪表盘', requiresAuth: true }
  },
  {
    path: '/seller/shop',
    name: 'MerchantShop',
    component: () => import('@/views/merchant/shop/index.vue'),
    meta: { layout: 'merchant', title: '店铺管理', requiresAuth: true }
  },
  {
    path: '/seller/products',
    name: 'MerchantProducts',
    component: () => import('@/views/merchant/products/index.vue'),
    meta: { layout: 'merchant', title: '商品管理', requiresAuth: true }
  },
  {
    path: '/seller/orders',
    name: 'MerchantOrders',
    component: () => import('@/views/merchant/orders/index.vue'),
    meta: { layout: 'merchant', title: '订单管理', requiresAuth: true }
  },
  {
    path: '/seller/finance',
    name: 'MerchantFinance',
    component: () => import('@/views/merchant/finance/index.vue'),
    meta: { layout: 'merchant', title: '财务报表', requiresAuth: true }
  },
  {
    path: '/seller/wallet',
    name: 'MerchantWallet',
    component: () => import('@/views/merchant/wallet/index.vue'),
    meta: { layout: 'merchant', title: '钱包', requiresAuth: true }
  },
  {
    path: '/seller/settings',
    name: 'MerchantSettings',
    component: () => import('@/views/merchant/settings/index.vue'),
    meta: { layout: 'merchant', title: '设置', requiresAuth: true }
  },
  {
    path: '/seller/chat',
    name: 'MerchantChat',
    component: () => import('@/views/merchant/chat/index.vue'),
    meta: { layout: 'merchant', title: '客服聊天', requiresAuth: true }
  },
  {
    path: '/seller/marketing',
    name: 'MerchantMarketing',
    component: () => import('@/views/merchant/marketing/index.vue'),
    meta: { layout: 'merchant', title: '营销', requiresAuth: true }
  }
]
