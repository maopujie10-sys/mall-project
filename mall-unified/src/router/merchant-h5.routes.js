// 商家移动端路由 — 从 merchant-h5 迁移，已 Vue 3
// 龙一补全 2026-05-31
export default [
  { path: '/m/seller/', redirect: '/m/seller/shop' },

  // ===== 认证 =====
  { path: '/m/seller/login', name: 'MobileSellerLogin', component: () => import('@/views/merchant-h5/login/index.vue'), meta: { layout: 'mobile', title: '商家登录' } },
  { path: '/m/seller/register', name: 'MobileSellerRegister', component: () => import('@/views/merchant-h5/register/index.vue'), meta: { layout: 'mobile', title: '商家注册' } },
  { path: '/m/seller/forget', name: 'MobileSellerForget', component: () => import('@/views/merchant-h5/forget/index.vue'), meta: { layout: 'mobile', title: '忘记密码' } },
  { path: '/m/seller/reset-password', name: 'MobileSellerResetPassword', component: () => import('@/views/merchant-h5/forget/resetPassword.vue'), meta: { layout: 'mobile', title: '重置密码' } },
  { path: '/m/seller/pass-success', name: 'MobileSellerPassSuccess', component: () => import('@/views/merchant-h5/forget/passSuccess.vue'), meta: { layout: 'mobile', title: '修改成功' } },
  { path: '/m/seller/safe-verify', name: 'MobileSellerSafeVerify', component: () => import('@/views/merchant-h5/forget/safeVerify.vue'), meta: { layout: 'mobile', title: '安全验证' } },
  { path: '/m/seller/verify-page', name: 'MobileSellerVerifyPage', component: () => import('@/views/merchant-h5/verifyPage/index.vue'), meta: { layout: 'mobile', title: '邮箱手机验证' } },
  { path: '/m/seller/certified', name: 'MobileSellerCertified', component: () => import('@/views/merchant-h5/certified/index.vue'), meta: { layout: 'mobile', title: '认证' } },

  // ===== 店铺 =====
  { path: '/m/seller/shop', name: 'MobileSellerShop', component: () => import('@/views/merchant-h5/shop/index.vue'), meta: { layout: 'mobile', title: '店铺', requiresAuth: true } },
  { path: '/m/seller/shop/basic-info', name: 'MobileSellerShopBasic', component: () => import('@/views/merchant-h5/shop/basicInfo/index.vue'), meta: { layout: 'mobile', title: '店铺信息', requiresAuth: true } },
  { path: '/m/seller/shop/banner', name: 'MobileSellerShopBanner', component: () => import('@/views/merchant-h5/shop/banner/index.vue'), meta: { layout: 'mobile', title: '店铺Banner', requiresAuth: true } },
  { path: '/m/seller/shop/social', name: 'MobileSellerShopSocial', component: () => import('@/views/merchant-h5/shop/social/index.vue'), meta: { layout: 'mobile', title: '社交媒体', requiresAuth: true } },
  { path: '/m/seller/shop/promotion', name: 'MobileSellerShopPromotion', component: () => import('@/views/merchant-h5/shop/promotion/index.vue'), meta: { layout: 'mobile', title: '推广', requiresAuth: true } },
  { path: '/m/seller/shop/marketing', name: 'MobileSellerShopMarketing', component: () => import('@/views/merchant-h5/shop/marketing/index.vue'), meta: { layout: 'mobile', title: '营销', requiresAuth: true } },
  { path: '/m/seller/shop/marketing/record', name: 'MobileSellerMarketingRecord', component: () => import('@/views/merchant-h5/shop/marketing/record/index.vue'), meta: { layout: 'mobile', title: '营销记录', requiresAuth: true } },
  { path: '/m/seller/shop/settings', name: 'MobileSellerShopSettings', component: () => import('@/views/merchant-h5/shop/settings/index.vue'), meta: { layout: 'mobile', title: '店铺设置', requiresAuth: true } },
  { path: '/m/seller/shop/class', name: 'MobileSellerShopClass', component: () => import('@/views/merchant-h5/shop/class/index.vue'), meta: { layout: 'mobile', title: '分类', requiresAuth: true } },
  { path: '/m/seller/shop/contract', name: 'MobileSellerContract', component: () => import('@/views/merchant-h5/shop/contract/index.vue'), meta: { layout: 'mobile', title: '合同', requiresAuth: true } },
  { path: '/m/seller/shop/contract-sign', name: 'MobileSellerContractSign', component: () => import('@/views/merchant-h5/shop/contractSign/index.vue'), meta: { layout: 'mobile', title: '签订合同', requiresAuth: true } },

  // ===== 商品 =====
  { path: '/m/seller/product', name: 'MobileSellerProducts', component: () => import('@/views/merchant-h5/product/index.vue'), meta: { layout: 'mobile', title: '商品', requiresAuth: true } },
  { path: '/m/seller/product/list', name: 'MobileSellerProductList', component: () => import('@/views/merchant-h5/product/list.vue'), meta: { layout: 'mobile', title: '商品库', requiresAuth: true } },
  { path: '/m/seller/product/edit', name: 'MobileSellerProductEdit', component: () => import('@/views/merchant-h5/product/components/productEdit.vue'), meta: { layout: 'mobile', title: '编辑商品', requiresAuth: true } },
  { path: '/m/seller/product/:id', name: 'MobileSellerProductDetail', component: () => import('@/views/merchant-h5/product/details.vue'), meta: { layout: 'mobile', title: '商品详情', requiresAuth: true } },
  { path: '/m/seller/product/comment', name: 'MobileSellerProductComment', component: () => import('@/views/merchant-h5/product/comment.vue'), meta: { layout: 'mobile', title: '商品评论', requiresAuth: true } },

  // ===== 订单 =====
  { path: '/m/seller/order', name: 'MobileSellerOrders', component: () => import('@/views/merchant-h5/order/index.vue'), meta: { layout: 'mobile', title: '订单', requiresAuth: true } },
  { path: '/m/seller/order/:id', name: 'MobileSellerOrderDetail', component: () => import('@/views/merchant-h5/order/orderdeails.vue'), meta: { layout: 'mobile', title: '订单详情', requiresAuth: true } },
  { path: '/m/seller/order/qr', name: 'MobileSellerQrOrder', component: () => import('@/views/merchant-h5/order/qr_order.vue'), meta: { layout: 'mobile', title: '采购确认', requiresAuth: true } },
  { path: '/m/seller/order/search', name: 'MobileSellerOrderSearch', component: () => import('@/views/merchant-h5/order/orderSearch.vue'), meta: { layout: 'mobile', title: '订单搜索', requiresAuth: true } },
  { path: '/m/seller/order/success', name: 'MobileSellerOrderSuccess', component: () => import('@/views/merchant-h5/order/passsuess.vue'), meta: { layout: 'mobile', title: '支付成功', requiresAuth: true } },
  { path: '/m/seller/order/logistics', name: 'MobileSellerOrderLogistics', component: () => import('@/views/merchant-h5/order/logistics.vue'), meta: { layout: 'mobile', title: '物流', requiresAuth: true } },

  // ===== 充值 =====
  { path: '/m/seller/recharge', name: 'MobileSellerRecharge', component: () => import('@/views/merchant-h5/recharge/index.vue'), meta: { layout: 'mobile', title: '充值', requiresAuth: true } },
  { path: '/m/seller/recharge/:id', name: 'MobileSellerRechargeDetail', component: () => import('@/views/merchant-h5/recharge/detail.vue'), meta: { layout: 'mobile', title: '充值详情', requiresAuth: true } },
  { path: '/m/seller/recharge/record', name: 'MobileSellerRechargeRecord', component: () => import('@/views/merchant-h5/recharge/record.vue'), meta: { layout: 'mobile', title: '充值记录', requiresAuth: true } },
  { path: '/m/seller/recharge/record/:id', name: 'MobileSellerRechargeRecordDetail', component: () => import('@/views/merchant-h5/recharge/recordDetails.vue'), meta: { layout: 'mobile', title: '记录详情', requiresAuth: true } },
  { path: '/m/seller/recharge/third-party', name: 'MobileSellerThirdPartyRecharge', component: () => import('@/views/merchant-h5/recharge/thirdPartyRecharge.vue'), meta: { layout: 'mobile', title: '第三方充值', requiresAuth: true } },

  // ===== 提现 =====
  { path: '/m/seller/withdraw', name: 'MobileSellerWithdraw', component: () => import('@/views/merchant-h5/withdraw/index.vue'), meta: { layout: 'mobile', title: '提现', requiresAuth: true } },
  { path: '/m/seller/withdraw/record', name: 'MobileSellerWithdrawRecord', component: () => import('@/views/merchant-h5/withdraw/record.vue'), meta: { layout: 'mobile', title: '提现记录', requiresAuth: true } },
  { path: '/m/seller/withdraw/record/:id', name: 'MobileSellerWithdrawRecordDetail', component: () => import('@/views/merchant-h5/withdraw/recordDetails.vue'), meta: { layout: 'mobile', title: '记录详情', requiresAuth: true } },

  // ===== 我的 =====
  { path: '/m/seller/my', name: 'MobileSellerMy', component: () => import('@/views/merchant-h5/my/index.vue'), meta: { layout: 'mobile', title: '我的', requiresAuth: true } },
  { path: '/m/seller/setting', name: 'MobileSellerSetting', component: () => import('@/views/merchant-h5/setting/index.vue'), meta: { layout: 'mobile', title: '设置', requiresAuth: true } },
  { path: '/m/seller/setting/cancellation', name: 'MobileSellerAccountCancel', component: () => import('@/views/merchant-h5/setting/cancellation/index.vue'), meta: { layout: 'mobile', title: '注销账号', requiresAuth: true } },
  { path: '/m/seller/personal-info', name: 'MobileSellerPersonalInfo', component: () => import('@/views/merchant-h5/personalInfo/index.vue'), meta: { layout: 'mobile', title: '个人信息', requiresAuth: true } },
  { path: '/m/seller/change-avatar', name: 'MobileSellerChangeAvatar', component: () => import('@/views/merchant-h5/changeAvatar/index.vue'), meta: { layout: 'mobile', title: '修改头像', requiresAuth: true } },
  { path: '/m/seller/change-password', name: 'MobileSellerChangePassword', component: () => import('@/views/merchant-h5/changePassword/index.vue'), meta: { layout: 'mobile', title: '修改密码', requiresAuth: true } },
  { path: '/m/seller/change-phone', name: 'MobileSellerChangePhone', component: () => import('@/views/merchant-h5/changePhone/index.vue'), meta: { layout: 'mobile', title: '修改手机', requiresAuth: true } },
  { path: '/m/seller/success-change', name: 'MobileSellerSuccessChange', component: () => import('@/views/merchant-h5/successChange/index.vue'), meta: { layout: 'mobile', title: '修改成功', requiresAuth: true } },
  { path: '/m/seller/name', name: 'MobileSellerName', component: () => import('@/views/merchant-h5/name/index.vue'), meta: { layout: 'mobile', title: '名称', requiresAuth: true } },
  { path: '/m/seller/number', name: 'MobileSellerNumber', component: () => import('@/views/merchant-h5/number/index.vue'), meta: { layout: 'mobile', title: '电话', requiresAuth: true } },
  { path: '/m/seller/email', name: 'MobileSellerEmail', component: () => import('@/views/merchant-h5/email/index.vue'), meta: { layout: 'mobile', title: '邮箱', requiresAuth: true } },

  // ===== 安全中心 =====
  { path: '/m/seller/safety', name: 'MobileSellerSafety', component: () => import('@/views/merchant-h5/safety/index.vue'), meta: { layout: 'mobile', title: '安全中心', requiresAuth: true } },
  { path: '/m/seller/safety/change-verify', name: 'MobileSellerChangeVerify', component: () => import('@/views/merchant-h5/safety/changeVerify.vue'), meta: { layout: 'mobile', title: '更换绑定', requiresAuth: true } },
  { path: '/m/seller/funds-password-settings', name: 'MobileSellerFundsPwd', component: () => import('@/views/merchant-h5/fundsPasswordSettings/index.vue'), meta: { layout: 'mobile', title: '资金密码', requiresAuth: true } },
  { path: '/m/seller/change-funds-password', name: 'MobileSellerChangeFundsPwd', component: () => import('@/views/merchant-h5/changeFundsPassword/index.vue'), meta: { layout: 'mobile', title: '修改资金密码', requiresAuth: true } },
  { path: '/m/seller/bind-verify', name: 'MobileSellerBindVerify', component: () => import('@/views/merchant-h5/bindVerify/index.vue'), meta: { layout: 'mobile', title: '绑定验证', requiresAuth: true } },
  { path: '/m/seller/reset-verify', name: 'MobileSellerResetVerify', component: () => import('@/views/merchant-h5/resetVerify/index.vue'), meta: { layout: 'mobile', title: '重置绑定', requiresAuth: true } },
  { path: '/m/seller/reset-success', name: 'MobileSellerResetSuccess', component: () => import('@/views/merchant-h5/resetVerify/resetSuccess.vue'), meta: { layout: 'mobile', title: '重置成功', requiresAuth: true } },
  { path: '/m/seller/reset-pane', name: 'MobileSellerResetPane', component: () => import('@/views/merchant-h5/resetPane/index.vue'), meta: { layout: 'mobile', title: '重置手机/邮箱', requiresAuth: true } },

  // ===== 财务 =====
  { path: '/m/seller/funds-records', name: 'MobileSellerFundsRecords', component: () => import('@/views/merchant-h5/fundsRecords/index.vue'), meta: { layout: 'mobile', title: '资金记录', requiresAuth: true } },
  { path: '/m/seller/finance', name: 'MobileSellerFinance', component: () => import('@/views/merchant-h5/FinancialStatements/index.vue'), meta: { layout: 'mobile', title: '财务管理', requiresAuth: true } },
  { path: '/m/seller/record/deposit-withdraw', name: 'MobileSellerRecordDW', component: () => import('@/views/merchant-h5/Record/DepositAndWithdrawal.vue'), meta: { layout: 'mobile', title: '存取记录', requiresAuth: true } },
  { path: '/m/seller/record/details', name: 'MobileSellerRecordDetail', component: () => import('@/views/merchant-h5/Record/RecordDetails.vue'), meta: { layout: 'mobile', title: '记录详情', requiresAuth: true } },
  { path: '/m/seller/payment-method/list', name: 'MobileSellerPayList', component: () => import('@/views/merchant-h5/payMentMethod/list.vue'), meta: { layout: 'mobile', title: '收款方式', requiresAuth: true } },
  { path: '/m/seller/payment-method/add', name: 'MobileSellerPayAdd', component: () => import('@/views/merchant-h5/payMentMethod/add.vue'), meta: { layout: 'mobile', title: '添加收款', requiresAuth: true } },
  { path: '/m/seller/payment-method/select', name: 'MobileSellerPaySelect', component: () => import('@/views/merchant-h5/payMentMethod/selectPay.vue'), meta: { layout: 'mobile', title: '选择支付', requiresAuth: true } },

  // ===== 客服 =====
  { path: '/m/seller/customer-service', name: 'MobileSellerCS', component: () => import('@/views/merchant-h5/customerService/index.vue'), meta: { layout: 'mobile', title: '客服' } },
  { path: '/m/seller/customer-service-other', name: 'MobileSellerCSOther', component: () => import('@/views/merchant-h5/customerServiceOther/index.vue'), meta: { layout: 'mobile', title: '第三方客服' } },

  // ===== 其他功能 =====
  { path: '/m/seller/language', name: 'MobileSellerLang', component: () => import('@/views/merchant-h5/language/index.vue'), meta: { layout: 'mobile', title: '语言' } },
  { path: '/m/seller/invitation', name: 'MobileSellerInvite', component: () => import('@/views/merchant-h5/invitationActivity/index.vue'), meta: { layout: 'mobile', title: '邀请活动', requiresAuth: true } },
  { path: '/m/seller/terms', name: 'MobileSellerTerms', component: () => import('@/views/merchant-h5/termsOfService/index.vue'), meta: { layout: 'mobile', title: '服务条款' } },
  { path: '/m/seller/login-agreement', name: 'MobileSellerLoginAgree', component: () => import('@/views/merchant-h5/login-agreement/index.vue'), meta: { layout: 'mobile', title: '用户协议' } },
  { path: '/m/seller/search', name: 'MobileSellerSearch', component: () => import('@/views/merchant-h5/search/index.vue'), meta: { layout: 'mobile', title: '搜索', requiresAuth: true } },
  { path: '/m/seller/seller-level', name: 'MobileSellerLevel', component: () => import('@/views/merchant-h5/sellerLevel/index.vue'), meta: { layout: 'mobile', title: '卖家等级', requiresAuth: true } },
  { path: '/m/seller/refund-request', name: 'MobileSellerRefund', component: () => import('@/views/merchant-h5/refundRequest/index.vue'), meta: { layout: 'mobile', title: '退款申请', requiresAuth: true } },
  { path: '/m/seller/refund-request/:id', name: 'MobileSellerRefundDetail', component: () => import('@/views/merchant-h5/refundRequest/details/index.vue'), meta: { layout: 'mobile', title: '退款详情', requiresAuth: true } },

  // ===== 消息 =====
  { path: '/m/seller/message', name: 'MobileSellerMessage', component: () => import('@/views/merchant-h5/message/list/index.vue'), meta: { layout: 'mobile', title: '消息', requiresAuth: true } },
  { path: '/m/seller/message/system', name: 'MobileSellerSysMsg', component: () => import('@/views/merchant-h5/message/system/index.vue'), meta: { layout: 'mobile', title: '系统消息', requiresAuth: true } },
  { path: '/m/seller/message/:id', name: 'MobileSellerMsgDetail', component: () => import('@/views/merchant-h5/message/details/index.vue'), meta: { layout: 'mobile', title: '消息详情', requiresAuth: true } },
  { path: '/m/seller/message-center', name: 'MobileSellerMsgCenter', component: () => import('@/views/merchant-h5/messageCenter/index.vue'), meta: { layout: 'mobile', title: '消息中心', requiresAuth: true } },

  // ===== 活动 =====
  { path: '/m/seller/activity/turntable', name: 'MobileSellerTurntable', component: () => import('@/views/merchant-h5/activityCenter/turntable/index.vue'), meta: { layout: 'mobile', title: '大转盘' } },
  { path: '/m/seller/authentication', name: 'MobileSellerAuth', component: () => import('@/views/merchant-h5/authentication/verified.vue'), meta: { layout: 'mobile', title: '高级认证', requiresAuth: true } },

  // ===== 404 =====
  { path: '/m/seller/:pathMatch(.*)*', name: 'MobileSeller404', component: () => import('@/views/merchant-h5/404.vue'), meta: { layout: 'mobile', title: '404' } }
]
