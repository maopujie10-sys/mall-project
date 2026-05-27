export const saleData = [
  {
    title: 'totalSales',
    number: 0,
    icon: new URL('@/assets/image/shop/icon_23.png', import.meta.url)
  },
  {
    title: 'totalProfit',
    number: 0,
    icon: new URL('@/assets/image/shop/icon_22.png', import.meta.url)
  }
]

export const visitorsData = [
  {
    title: 'todayVisitors',
    number: 0,
    decimals: 0,
    icon: new URL('@/assets/image/shop/icon_24.png', import.meta.url)
  },
  {
    title: 'visitors7',
    number: 0,
    decimals: 0,
    icon: new URL('@/assets/image/shop/icon_25.png', import.meta.url)
  },
  {
    title: 'visitors30',
    number: 0,
    decimals: 0,
    icon: new URL('@/assets/image/shop/icon_26.png', import.meta.url)
  },
  {
    title: 'ordersSoldToday',
    number: 0,
    decimals: 0,
    icon: new URL('@/assets/image/shop/icon_27.png', import.meta.url)
  },
  {
    title: 'totalSalesToday',
    number: 0,
    decimals: 2,
    icon: new URL('@/assets/image/shop/icon_28.png', import.meta.url)
  },
  {

    title: '预计利润',
    number: 0,
    decimals: 2,
    icon: new URL('@/assets/image/shop/icon_29.png', import.meta.url)
  }
]

export const navData = [
  {
    title: '店铺设置',
    icon: new URL('@/assets/image/shop/icon_15.png', import.meta.url),
    href: '/shop/settings'
  },
  {
    title: 'refunds',
    icon: new URL('@/assets/image/shop/icon_16.png', import.meta.url),
    href: '/refundRequest'
  },
  {
    title: 'throughCar',
    icon: new URL('@/assets/image/shop/icon_04.png', import.meta.url),
    href: '/shop/marketing'
  },
  {
    title: 'shopPromotion',
    icon: new URL('@/assets/image/shop/icon_17.png', import.meta.url),
    href: '/shop/promotion'
  },
  {
    title: 'shopRecharge',
    icon: new URL('@/assets/image/shop/icon_07.png', import.meta.url),
    href: '/recharge'
  },
  {
    title: 'shopWithdraw',
    icon: new URL('@/assets/image/shop/icon_08.png', import.meta.url),
    href: '/withdraw'
  },
  {
    title: '卖家等级',
    icon: new URL('@/assets/image/shop/icon_21.png', import.meta.url),
    href: '/sellerLevel'
  },
  {
    title: '切换至买家',
    icon: new URL('@/assets/image/shop/icon_31.png', import.meta.url),
    href: '/gotoBuyer'
  }
]

export const statItemData = [
  {
    title: '店铺关注',
    icon: new URL('@/assets/image/shop/icon_18.png', import.meta.url),
    number: 0,
    decimals: 0
  },
  {
    title: '店铺评分',
    icon: new URL('@/assets/image/shop/icon_19.png', import.meta.url),
    number: 0,
    decimals: 1,
    prefix: ''
  },
  {
    title: '卖家信用分',
    icon: new URL('@/assets/image/shop/icon_20.png', import.meta.url),
    number: 0,
    decimals: 0
  }
]

export const statBlockData = [
  {
    title: 'totalOrders',
    number: 0,
    color: '#5C9DFF'
  },
  {
    title: 'waitingOrders',
    number: 0,
    color: '#FF8049'
  },
  {
    title: 'successfulOrders',
    number: 0,
    color: '#3FBC8F'
  },
  {
    title: 'orderCancellation',
    number: 0,
    color: '#5D6A7E'
  },
  {
    title: '已退款',
    number: 0,
    color: '#665ebd'
  }
]

export const promotionData = [
  {
    title: 'shopPromotionDownload',
    key: 'download',
    value: ''
  },
  {
    title: 'shopPromotionCode',
    key: 'code',
    value: ''
  }
]

export const teamNav = [
  {
    title: 'shopFirstLevel',
    key: 1
  },
  {
    title: 'shopSecondLevel',
    key: 2
  },
  {
    title: 'shopThirdLevel',
    key: 3
  }
]

export const verifyStepData = [
  {
    name: '店铺设置',
    tipsData: [
      {
        tips: '请您完善店铺信息，以保证顾客能正常访问到您的店铺',
        btnTxt: '立即设置',
        href: '/shop/settings'
      }
    ]
  },
  {
    name: '店铺认证',
    tipsData: [
      {
        tips: '请完善您的身份认证信息，以保证顾客能正常访问到您的店铺',
        btnTxt: '立即认证',
        href: '/name'
      },
      {
        tips: '您的身份认证信息正在审核中，请您耐心等待',
        btnTxt: '查看认证',
        href: '/name'
      },
      {
        tips: '您的身份认证信息审核失败，请您重新认证',
        btnTxt: '再次认证',
        href: '/name'
      }
    ]
  },
  {
    name: '上架商品',
    tipsData: [
      {
        tips: '您店铺中上架商品数量不足，请前往添加',
        btnTxt: '添加商品',
        href: '/product'
      }
    ]
  }
]

export const shopSettingsNavData = [
  {
    title: 'basicInfo',
    icon: new URL('@/assets/image/shop/icon_12.png', import.meta.url),
    href: '/shop/basicInfo'
  },
  {
    title: 'banner',
    icon: new URL('@/assets/image/shop/icon_13.png', import.meta.url),
    href: '/shop/banner'
  },
  {
    title: 'soical',
    icon: new URL('@/assets/image/shop/icon_14.png', import.meta.url),
    href: '/shop/social'
  }
]
