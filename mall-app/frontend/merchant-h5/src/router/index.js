// index.js
import {createRouter, createWebHashHistory} from 'vue-router'
import App from '@/App.vue'
import {useUserStore} from "@/store/user.js";
import {usekeepAliveStore} from "@/store/keepAlive.js";
import { useRouterStore } from '@/store/router.js'
import { sysParaSign } from '@/service/shop.api.js'

// const userStore = useUserStore()
// 路由规则
const routes = [
  {
    path: '/',
    // component: App,
    children: [
      {path: '', redirect: '/shop'},
      {
        path: '/login',
        name: 'Login',
        meta: {
          level: 1
        },
        component: () => import(/* webpackChunkName: "verify" */ /* webpackPrefetch: true */'@/views/login/index.vue'),
      },
      {
        path: '/register',
        name: 'Register',
        meta: {
          level: 2
        },
        component: () => import(/* webpackChunkName: "verify" */ /* webpackPrefetch: true */'@/views/register/index.vue'),
      },
      {
        path: '/shop',
        name: 'ShopIndex',
        meta: {
          level: 1,
          tarbar: true,
          keepAlive: true
        },
        component: () => import('@/views/shop/index.vue'),
      },
      {
        path: '/product',
        name: 'ProductIndex',
        meta: {
          level: 1,
          tarbar: true,
          keepAlive: true
        },
        component: () => import('@/views/product/index.vue'),
      },
      {
        path: '/shop/basicInfo',
        name: 'ShopBasicInfo',
        meta: {
          level: 3,
          tarbar: false
        },
        component: () => import('@/views/shop/basicInfo/index.vue')
      },
      {
        path: '/shop/banner',
        name: 'ShopBanner',
        meta: {
          level: 3,
          tarbar: false
        },
        component: () => import('@/views/shop/banner/index.vue')
      },
      {
        path: '/shop/social',
        name: 'ShopSocial',
        meta: {
          level: 3,
          tarbar: false
        },
        component: () => import('@/views/shop/social/index.vue')
      },
      {
        path: '/shop/promotion',
        name: 'shopPromotion',
        meta: {
          level: 2,
          tarbar: false
        },
        component: () => import('@/views/shop/promotion/index.vue')
      },
      {
        path: '/shop/marketing',
        name: 'ShopMarketing',
        meta: {
          level: 2,
          keepAlive: true,
          tarbar: false
        },
        component: () => import('@/views/shop/marketing/index.vue')
      },
      {
        path: '/shop/marketing/record',
        name: 'ShopMarketingRecord',
        meta: {
          level: 3,
          tarbar: false
        },
        component: () => import('@/views/shop/marketing/record/index.vue')
      },
      {
        path: '/shop/settings',
        name: 'ShopSettings',
        meta: {
          level: 2,
          tarbar: false
        },
        component: () => import('@/views/shop/settings/index.vue')
      },
      {
        path: '/shop/class',
        name: 'ShopClass',
        meta: {
          level: 2,
          tarbar: false,
          keepAlive: true
        },
        component: () => import('@/views/shop/class/index.vue')
      },
      {
        path: '/shop/contract',
        name: 'ShopContract',
        meta: {
          level: 3,
          tarbar: false
        },
        component: () => import('@/views/shop/contract/index.vue')
      },
      {
        path: '/shop/contractSign',
        name: 'ShopContractSign',
        meta: {
          level: 3,
          tarbar: false
        },
        component: () => import('@/views/shop/contractSign/index.vue')
      },
      {
        path: '/productPage',
        name: 'productPage',
        meta: {
          level: 3
        },
        component: () => import('@/views/Layout.vue'),
        children: [
          {path: 'list', meta: {tarbar: false, level: 3}, component: () => import('@/views/product/list.vue')}, //商品库
          {
            path: 'productEdit',
            meta: {tarbar: false, level: 3},
            component: () => import('@/views/product/components/productEdit.vue')
          }, //商品库
          {path: 'details', meta: {tarbar: false, level: 4}, component: () => import('@/views/product/details.vue')}, //商品详情
          {path: 'comment', meta: {tarbar: false, level: 3}, component: () => import('@/views/product/comment.vue')}, //商品评论

        ], //商品
      },
      {   // 订单
        path: '/order',
        name: 'Order',
        meta: {tarbar: true, keepAlive: true, level: 1},
        component: () => import('@/views/order/index.vue'),
      },
      {
        path: '/withdraw',
        name: 'Withdraw',
        meta: {tarbar: false, level: 2},
        component: () => import('@/views/withdraw/index.vue'),
      },
      {
        path: '/withdraw/record',
        name: 'WithdrawRecord',
        meta: {tarbar: false, level: 3},
        component: () => import('@/views/withdraw/record.vue'),
      },
      {
        path: '/withdraw/record-details',
        name: 'WithdrawRecordDetails',
        meta: {tarbar: false, level: 5},
        component: () => import('@/views/withdraw/recordDetails.vue'),
      },
      {
        path: '/recharge',
        name: 'Recharge',
        meta: {tarbar: false, level: 2},
        component: () => import('@/views/recharge/index.vue'),
      },
      {
        path: '/recharge/:id',
        name: 'RechargeDetail',
        meta: {tarbar: false, level: 3},
        component: () => import('@/views/recharge/detail.vue'),
      },
      {
        path: '/recharge/record',
        name: 'RechargeRecord',
        meta: {tarbar: false, level: 4},
        component: () => import('@/views/recharge/record.vue'),
      },
      {
        path: '/recharge/record-details',
        name: 'RechargeRecordDetails',
        meta: {tarbar: false, level: 5},
        component: () => import('@/views/recharge/recordDetails.vue'),
      },
      {
        path: '/recharge/third-party',
        name: 'thirdPartyRecharge',
        meta: {tarbar: false, level: 6},
        component: () => import('@/views/recharge/thirdPartyRecharge.vue'),
      },
      // {
      //   path: '/chart',
      //   redirect: '/chart/index',
      //   component: () => import('@/views/Layout.vue'),
      //   children: [
      //     { path: 'index/:symbol', meta: { tarbar: true }, component: () => import('@/views/charts/index.vue') },
      //     { path: 'order/:symbol', component: () => import('@/views/charts/order.vue') },
      //     { path: 'result', component: () => import('@/views/charts/result.vue') },
      //
      //   ]
      // },
      // {
      //   path: '/exchange',
      //   name: 'Exchange',
      //   redirect: '/exchange/list',
      //   // meta: { tarbar: true },
      //   component: () => import('@/views/Layout.vue'),
      //   children: [
      //     { path: 'list', meta: { tarbar: true }, component: () => import('@/views/exchange/List.vue') },
      //     { path: 'channel-in', name: 'channelIn', component: () => import('@/views/exchange/Channel.vue') },
      //     { path: 'channel-out', name: 'channelOut', component: () => import('@/views/exchange/Channel.vue') },
      //     { path: 'charge-bank', component: () => import('@/views/exchange/charge-bank.vue') },
      //     { path: 'charge-crypto', component: () => import('@/views/exchange/charge-crypto.vue') },
      //     { path: 'warehouse', component: () => import('@/views/exchange/warehouse.vue') },
      //     { path: 'withdraw-bank', component: () => import('@/views/exchange/withdraw-bank.vue') }, //银行卡提现
      //     { path: 'fund-password-verify', component: () => import('@/views/exchange/FundPasswordVerify.vue') }, //资金密码验证
      //     { path: 'withdraw-usdt', component: () => import('@/views/exchange/withdraw-usdt.vue') }, //usdt提现
      //   ]
      // },
      {   // 采购确认
        path: '/qr_order',
        name: 'qrOrder',
        meta: {level: 2},
        component: () => import('@/views/order/qr_order.vue'),
      },
      {   // 采购确认
        path: '/order_search',
        name: 'order_search',
        meta: {level: 2},
        component: () => import('@/views/order/orderSearch.vue'),
      },
      {   // 支付成功
        path: '/passsuess',
        name: 'passsuess',
        meta: {level: 3},
        component: () => import('@/views/order/passsuess.vue'),
      },
      {   // 订单详情
        path: '/orderdeails',
        name: 'orderdeails',
        meta: {level: 2},
        component: () => import('@/views/order/orderdeails.vue'),
      },
      {   // 查看物流
        path: '/order-logistics',
        name: 'OrderLogistics',
        meta: {level: 3},
        component: () => import('@/views/order/logistics.vue'),
      },
      { // 个人中心
        path: '/my',
        name: 'MyCenter',
        meta: {
          level: 1,
          tarbar: true
        },
        component: () => import('@/views/my/index.vue'),
      },
      { // 邮箱手机验证
        path: '/verifyPage',
        name: 'verifyPage',
        meta: {level: 3},
        component: () => import(/* webpackChunkName: "verifyPage" */ /* webpackPrefetch: true */'@/views/verifyPage/index.vue')
      },
      { // 邮箱手机认证
        path: '/certified',
        name: 'certified',
        meta: {level: 3},
        component: () => import(/* webpackChunkName: "certified" */ /* webpackPrefetch: true */'@/views/certified/index.vue')
      },
      {   //语言设置
        path: '/language',
        name: 'Language',
        meta: {level: 2},
        component: () => import(/* webpackChunkName: "language" */ /* webpackPrefetch: true */'@/views/language/index.vue')
      },
      {   // 邀请活动
        path: '/invitation-activity',
        name: 'InvitationActivity',
        meta: {level: 2},
        component: () => import(/* webpackChunkName: "InvitationActivity" */ /* webpackPrefetch: true */'@/views/invitationActivity/index.vue')
      },
      { //客服
        path: '/customerService',
        name: 'customerService',
        meta: {level: 5},
        props: route => {
          return route.query
        },
        component: () => import(/* webpackChunkName: "customerService" */ /* webpackPrefetch: true */'@/views/customerService/index.vue')
      },
      { //客服-第三方
        path: '/customerServiceOther',
        name: 'customerServiceOther',
        meta: {level: 2},
        props: route => {
          return route.query
        },
        component: () => import(/* webpackChunkName: "customerServiceOther" */ /* webpackPrefetch: true */'@/views/customerServiceOther/index.vue')
      },
      { // 修改头像
        path: '/changeAvatar',
        name: 'changeAvatar',
        meta: {level: 3},
        component: () => import(/* webpackChunkName: "changeAvatar" */ /* webpackPrefetch: true */'@/views/changeAvatar/index.vue')
      },
      {//修改登录密码
        path: '/changePassword',
        name: 'changePassword',
        meta: {level: 3},
        component: () => import(/* webpackChunkName: "changePassword" */ /* webpackPrefetch: true */'@/views/changePassword/index.vue')
      },
      {//设置资金密码
        path: '/fundsPasswordSettings',
        name: 'fundsPasswordSettings',
        meta: {level: 3},
        component: () => import(/* webpackChunkName: "fundsPasswordSettings" */ /* webpackPrefetch: true */'@/views/fundsPasswordSettings/index.vue')
      },
      {//修改资金密码
        path: '/changeFundsPassword',
        name: 'changeFundsPassword',
        meta: {level: 3},
        component: () => import(/* webpackChunkName: "changeFundsPassword" */ /* webpackPrefetch: true */'@/views/changeFundsPassword/index.vue')
      },
      {//绑定验证
        path: '/bindVerify',
        name: 'bindVerify',
        meta: {level: 4},
        component: () => import(/* webpackChunkName: "bindVerify" */ /* webpackPrefetch: true */'@/views/bindVerify/index.vue')
      },
      {//重置绑定
        path: '/resetVerify',
        name: 'resetVerify',
        component: () => import(/* webpackChunkName: "resetVerify" */ /* webpackPrefetch: true */'@/views/resetVerify/index.vue')
      },
      {//安全中心
        path: '/safety',
        name: 'safety',
        component: () => import(/* webpackChunkName: "safety" */ /* webpackPrefetch: true */'@/views/safety/index.vue')
      },
      {//更换绑定
        path: '/changeVerify',
        name: 'changeVerify',
        component: () => import(/* webpackChunkName: "changeVerify" */ /* webpackPrefetch: true */'@/views/safety/changeVerify.vue')
      },
      {
        //服务条款
        path: '/TermsOfService',
        name: 'TermsOfService',
        component: () => import(/* webpackChunkName: "TermsOfService" */ /* webpackPrefetch: true */'@/views/termsOfService/index.vue')
      },
      {//
        path: '/resetSuccess',
        name: 'resetSuccess',
        component: () => import(/* webpackChunkName: "resetSuccess" */ /* webpackPrefetch: true */'@/views/resetVerify/resetSuccess.vue')
      },
      {//忘记密码
        path: '/forget',
        name: 'forget',
        component: () => import(/* webpackChunkName: "forget" */ /* webpackPrefetch: true */'@/views/forget/index.vue')
      },
      {//重置登录密码
        path: '/resetPassword',
        name: 'resetPassword',
        component: () => import(/* webpackChunkName: "resetPassword" */ /* webpackPrefetch: true */'@/views/forget/resetPassword.vue')
      },
      {//忘记密码修改成功
        path: '/passSuccess',
        name: 'passSuccess',
        component: () => import(/* webpackChunkName: "passSuccess" */ /* webpackPrefetch: true */'@/views/forget/passSuccess.vue')
      },
      {//安全验证
        path: '/safeVerify',
        name: 'safeVerify',
        component: () => import(/* webpackChunkName: "safeVerify" */ /* webpackPrefetch: true */'@/views/forget/safeVerify.vue')
      },
      {//重置邮箱/手机号
        path: '/resetPane',
        name: 'resetPane',
        component: () => import(/* webpackChunkName: "resetPane" */ /* webpackPrefetch: true */'@/views/resetPane/index.vue')
      },
      {//设置
        path: '/setting',
        name: 'setting',
        meta: {level: 2},
        component: () => import(/* webpackChunkName: "setting" */ /* webpackPrefetch: true */'@/views/setting/index.vue')
      },
      {
        path: '/setting/cancellation',
        name: 'AccountCancellation',
        meta: {
          tarbar: false,
          level: 3
        },
        component: () => import('@/views/setting/cancellation/index.vue')
      },
      {//个人信息
        path: '/personalInfo',
        name: 'personalInfo',
        meta: {level: 2},
        component: () => import(/* webpackChunkName: "personalInfo" */ /* webpackPrefetch: true */'@/views/personalInfo/index.vue')
      },
      {//登录密码修改成功
        path: '/successChange',
        name: 'successChange',
        meta: {level: 2},
        component: () => import(/* webpackChunkName: "successChange" */ /* webpackPrefetch: true */'@/views/successChange/index.vue')
      },
      {//refundRequest
        path: '/refundRequest',
        name: 'refundRequest',
        meta: {level: 2},
        component: () => import(/* webpackChunkName: "refundRequest" */ /* webpackPrefetch: true */'@/views/refundRequest/index.vue')
      },
      {//refundRequest
        path: '/refundRequest/details',
        name: 'RefundRequestDetails',
        meta: {level: 3},
        component: () => import(/* webpackChunkName: "RefundRequestDetails" */ /* webpackPrefetch: true */'@/views/refundRequest/details/index.vue')
      },
      {//名称
        path: '/name',
        name: 'name',
        meta: {level: 3},
        component: () => import(/* webpackChunkName: "name" */ /* webpackPrefetch: true */'@/views/name/index.vue')
      },
      {//电话
        path: '/number',
        name: 'number',
        component: () => import(/* webpackChunkName: "number" */ /* webpackPrefetch: true */'@/views/number/index.vue')
      },

      {//邮箱
        path: '/email',
        name: 'email',
        component: () => import(/* webpackChunkName: "email" */ /* webpackPrefetch: true */'@/views/email/index.vue')
      },
      {//搜索
        path: '/search',
        name: 'search',
        meta: {level: 3},
        component: () => import(/* webpackChunkName: "search" */ /* webpackPrefetch: true */'@/views/search/index.vue')
      },
      {
        path: '/:pathMatch(.*)*',
        name: '404',
        component: () => import('@/views/404.vue')
      },
      {
        path: '/order',
        name: 'order',
        // meta: { tarbar: true },
        component: () => import('@/views/Layout.vue'),
        children: [
          // { path: 'submit', meta: { tarbar: true }, component: () => import('@/views/order/order-submit.vue') },
          // { path: 'success', component: () => import('@/views/order/success.vue') }, //成功
          // { path: 'apply-success', component: () => import('@/views/order/apply-success.vue') }, //申请成功
        ]
      },
      {
        path: '/Record',
        name: 'Record',
        // meta: { tarbar: true },
        component: () => import('@/views/Layout.vue'),
        children: [
          {
            path: 'DepositAndWithdrawal',
            meta: {tarbar: false},
            component: () => import('@/views/Record/DepositAndWithdrawal.vue')
          },
          {path: 'RecordDetails', meta: {tarbar: false}, component: () => import('@/views/Record/RecordDetails.vue')}
        ], //充值和提现记录
      },
      {
        path: '/payMentMethod',
        name: 'payMentMethod',
        // meta: { tarbar: true },
        component: () => import('@/views/Layout.vue'),
        children: [
          {path: 'list', meta: {tarbar: false}, component: () => import('@/views/payMentMethod/list.vue')},
          {path: 'add', meta: {tarbar: false}, component: () => import('@/views/payMentMethod/add.vue')},
          {path: 'selectPay', meta: {tarbar: false}, component: () => import('@/views/payMentMethod/selectPay.vue')},
        ], //收款方式
      },
      { // 资金记录
        path: '/fundsRecords',
        meta: {level: 2},
        component: () => import('@/views/fundsRecords/index.vue')
      },
      { // 财务管理
        path: '/finance',
        meta: {level: 2},
        component: () => import('@/views/FinancialStatements/index.vue')
      },
      { // 消息列表
        path: '/message',
        name: 'MessageList',
        meta: {level: 2},
        component: () => import('@/views/message/list/index.vue')
      },
      { // 系统消息
        path: '/message/system',
        name: 'MessageSystem',
        meta: {
          keepAlive: true,
          level: 3
        },
        component: () => import('@/views/message/system/index.vue')
      },
      { // 消息详情
        path: '/message/details',
        name: 'MessageDetails',
        meta: {level: 4},
        component: () => import('@/views/message/details/index.vue')
      },
      { // 消息中心
        path: '/messageCenter',
        name: 'MessageCenter',
        meta: {level: 3},
        component: () => import('@/views/messageCenter/index.vue')
      },
      { // 卖家等级
        path: '/sellerLevel',
        name: 'SellerLevel',
        meta: {
          level: 2,
          tarbar: false
        },
        component: () => import('@/views/sellerLevel/index.vue')
      },
      {
        path: '/web-view',
        meta: {level: 4},
        component: () => import('@/components/webView/WebView.vue'),
        props: route => {
          return {query: route.query}
        }
      },
      { // 用户协议
        path: '/login-agreement',
        name: 'LoginAgreement',
        meta: {
          level: 1
        },
        component: () => import('@/views/login-agreement/index.vue')
      },
      { // 营销活动-大转盘
        path: '/activity/turntable',
        name: 'ActivityTurntable',
        meta: {
          level: 1
        },
        component: () => import('@/views/activityCenter/turntable/index.vue')
      },
      { // 修改手机号-不收验证码
        path: '/changePhone',
        name: 'ChangePhone',
        meta: {
          level: 3
        },
        component: () => import('@/views/changePhone/index.vue')
      },
    ]
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return new Promise((resolve, reject) => {
      if (savedPosition) {
        console.log('savedPosition', savedPosition)
        setTimeout(() => {
          resolve(savedPosition);
        }, 400)
      } else {
        resolve({ left: 0, top: 0 });
      }
    })
  }
})

// 路由动画
const routerTransHandle = async (to, from) => {
  const routerStore = useRouterStore()
  await routerStore.routerTransHandle(to, from)
}

// 是否请求过需要签订电子合同
let hasRequsetSign = false
let isSign = false

// 跳过合同签订页
const jumpSignRoutes = ['Login', 'Language', 'Register', 'customerService', 'customerServiceOther', 'ActivityTurntable']
// 登录白名单
const whiteRoutes = ['Language', 'customerService', 'customerServiceOther', 'MessageList', 'ShopContract', 'LoginAgreement', 'Register', 'ActivityTurntable']

router.beforeEach(async (to, from, next) => {
  // 进入登录页合同签订初始化
  if (to.name === 'Login') {
    hasRequsetSign = false
  }
  
  const userStore = useUserStore()
  const token = userStore?.userInfo?.token || '';
  if (to.meta.keepAlive) {
    const keepAliveStore = usekeepAliveStore()
    await keepAliveStore.setKeepAlive(to.name)
  }

  // 如果不是首页清除未读消息请求
  if (to.path !== '/shop' && sessionStorage.getItem('msgRequset')) {
    document.dispatchEvent(new CustomEvent('clearMsgRequset'))
  }

  if (token) {
    if (!jumpSignRoutes.includes(to.name)) {
      await userStore.getUserInfo()
      await routerTransHandle(to, from)
      
      // 如果系统开启了签订合同用户没有签订则强制进入合同签订页面
      const signBackNor = from.name === 'ShopSettings' ? '1' : '0'
      if (!userStore.userInfo.signPdfUrl && to.name !== 'ShopContractSign') {
        if (!hasRequsetSign) {
          await sysParaSign().then(res => {
            hasRequsetSign = true
            isSign = (typeof res.sellerSign) === 'string' ? JSON.parse(res.sellerSign) : res.sellerSign
          })
        }
        if (isSign) {
          next(`/shop/contractSign?back=${signBackNor}`)
        } else {
          next()
        }
      } else {
        next()
      }
    } else {
      await routerTransHandle(to, from)
      next()
    }
  } else {
    if (whiteRoutes.includes(to.name)) {
      await routerTransHandle(to, from)
      next();
    } else {
      if (to.name !== 'Login') {
        await routerTransHandle(to, from)
        const isFrom = to.query.from || ''
        const token = to.query.token || ''
        // 如果是从用户端过来的链接
        if (['ShopIndex'].includes(to.name) && isFrom === 'shop' && token) {
          next();
        } else {
          next('/login')
        }
      } else {
        await routerTransHandle(to, from)
        next();
      }
    }
  }
})


export default router
