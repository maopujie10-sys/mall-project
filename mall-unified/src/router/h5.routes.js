// H5 移动商城路由
export default [
  {
    path: '/m',
    name: 'MobileHome',
    component: () => import('@/views/h5/home/index.vue'),
    meta: { layout: 'mobile', title: '首页' }
  },
  {
    path: '/m/categories',
    name: 'MobileCategories',
    component: () => import('@/views/h5/categories/index.vue'),
    meta: { layout: 'mobile', title: '分类' }
  },
  {
    path: '/m/product/:id',
    name: 'MobileProductDetail',
    component: () => import('@/views/h5/product-detail/index.vue'),
    meta: { layout: 'mobile', title: '商品详情' }
  },
  {
    path: '/m/search',
    name: 'MobileSearch',
    component: () => import('@/views/h5/search/index.vue'),
    meta: { layout: 'mobile', title: '搜索' }
  },
  {
    path: '/m/cart',
    name: 'MobileCart',
    component: () => import('@/views/h5/cart/index.vue'),
    meta: { layout: 'mobile', title: '购物车', requiresAuth: true }
  },
  {
    path: '/m/login',
    name: 'MobileLogin',
    component: () => import('@/views/h5/login/index.vue'),
    meta: { layout: 'mobile', title: '登录' }
  },
  {
    path: '/m/register',
    name: 'MobileRegister',
    component: () => import('@/views/h5/register/index.vue'),
    meta: { layout: 'mobile', title: '注册' }
  },
  {
    path: '/m/me',
    name: 'MobileMe',
    component: () => import('@/views/h5/me/index.vue'),
    meta: { layout: 'mobile', title: '我的', requiresAuth: true }
  },
  {
    path: '/m/order',
    name: 'MobileOrders',
    component: () => import('@/views/h5/order/index.vue'),
    meta: { layout: 'mobile', title: '订单', requiresAuth: true }
  },
  {
    path: '/m/checkout',
    name: 'MobileCheckout',
    component: () => import('@/views/h5/checkout/index.vue'),
    meta: { layout: 'mobile', title: '结算', requiresAuth: true }
  },
  {
    path: '/m/shop/:sellerId',
    name: 'MobileShop',
    component: () => import('@/views/h5/shop/index.vue'),
    meta: { layout: 'mobile', title: '店铺' }
  },
  {
    path: '/m/address',
    name: 'AddressList',
    component: () => import('@/views/h5/address/index.vue'),
    meta: { layout: 'mobile', title: '地址管理', requiresAuth: true }
  },
  {
    path: '/m/settings',
    name: 'Settings',
    component: () => import('@/views/h5/settings/index.vue'),
    meta: { layout: 'mobile', title: '设置', requiresAuth: true }
  },
  {
    path: '/m/invest',
    name: 'Invest',
    component: () => import('@/views/h5/invest/index.vue'),
    meta: { layout: 'mobile', title: '充值' }
  },
  {
    path: '/m/loan',
    name: 'Loan',
    component: () => import('@/views/h5/loan/index.vue'),
    meta: { layout: 'mobile', title: '贷款', requiresAuth: true }
  }
]
