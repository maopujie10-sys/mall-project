// PC 商城路由 — 统一 /pc 前缀
export default [
  {
    path: '/pc',
    name: 'PcHome',
    component: () => import('@/views/pc/home/index.vue'),
    meta: { layout: 'pc', title: 'PC 商城' }
  },
  {
    path: '/pc/products',
    name: 'PcProducts',
    component: () => import('@/views/pc/products/index.vue'),
    meta: { layout: 'pc', title: '商品列表' }
  },
  {
    path: '/pc/product/:id',
    name: 'PcProductDetail',
    component: () => import('@/views/pc/product-detail/index.vue'),
    meta: { layout: 'pc', title: '商品详情' }
  },
  {
    path: '/pc/categories',
    name: 'PcCategories',
    component: () => import('@/views/pc/categories/index.vue'),
    meta: { layout: 'pc', title: '全部分类' }
  },
  {
    path: '/pc/stores',
    name: 'PcStores',
    component: () => import('@/views/pc/stores/index.vue'),
    meta: { layout: 'pc', title: '品牌店铺' }
  },
  {
    path: '/pc/store/:sellerId',
    name: 'PcStoreDetail',
    component: () => import('@/views/pc/store-detail/index.vue'),
    meta: { layout: 'pc', title: '店铺详情' }
  },
  {
    path: '/pc/search',
    name: 'PcSearch',
    component: () => import('@/views/pc/search/index.vue'),
    meta: { layout: 'pc', title: '搜索' }
  },
  {
    path: '/pc/login',
    name: 'PcLogin',
    component: () => import('@/views/pc/login/index.vue'),
    meta: { layout: 'pc', title: '登录' }
  },
  {
    path: '/pc/register',
    name: 'PcRegister',
    component: () => import('@/views/pc/register/index.vue'),
    meta: { layout: 'pc', title: '注册' }
  },
  {
    path: '/pc/cart',
    name: 'PcCart',
    component: () => import('@/views/pc/cart/index.vue'),
    meta: { layout: 'pc', title: '购物车', requiresAuth: true }
  },
  {
    path: '/pc/user',
    name: 'PcUserCenter',
    component: () => import('@/views/pc/user/index.vue'),
    meta: { layout: 'pc', title: '用户中心', requiresAuth: true }
  },
  {
    path: '/pc/order',
    name: 'PcOrders',
    component: () => import('@/views/pc/order/index.vue'),
    meta: { layout: 'pc', title: '我的订单', requiresAuth: true }
  },
  {
    path: '/pc/checkout',
    name: 'PcCheckout',
    component: () => import('@/views/pc/checkout/index.vue'),
    meta: { layout: 'pc', title: '结算', requiresAuth: true }
  },
  {
    path: '/pc/credit',
    name: 'PcCredit',
    component: () => import('@/views/pc/credit/index.vue'),
    meta: { layout: 'pc', title: '信用中心', requiresAuth: true }
  },
  {
    path: '/pc/merchant-settle',
    name: 'PcMerchantSettle',
    component: () => import('@/views/pc/merchant-settle/index.vue'),
    meta: { layout: 'pc', title: '商家入驻' }
  },
  {
    path: '/pc/discount',
    name: 'PcDiscount',
    component: () => import('@/views/pc/discount/index.vue'),
    meta: { layout: 'pc', title: '折扣专区' }
  }
]
