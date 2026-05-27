import Vue from 'vue'
import Router from 'vue-router'
import transitionExtend from "@/utils/transition-extend";
Vue.use(Router)
const router =  transitionExtend(new Router({

    routes: [
        {
            path: '/',
            component: () => import('@/page/home.vue'),
            children: [
                {
                    path: '/',
                    name: 'index',
                    redirect: 'home',
                    component: () => import('@/page/index/index.vue'),
                    meta: {
                        keepAlive: false
                    }
                },
                {
                    path: '/home',
                    name: 'home',
                    component: () => import('@/page/index/index.vue'),
                    meta: {
                        keepAlive: false
                    }
                },
                {
                    path: '/me',
                    name: 'me',
                    component: () => import('@/page/me/index.vue'),

                },
                {
                    path: '/commodity',
                    name: 'commodity',
                    component: () => import('@/page/commodity/index.vue'),
                    
                },
                {
                    //购物车
                    path: '/cart',
                    name: 'cart',
                    component: () => import('@/page/cart/index.vue'),
                    meta: {
                        keepAlive: false
                    }
                }
            ],
            meta: {
                keepAlive: false
            }
        },
        {
            path: '*',
            redirect: '/home',
            meta: {
                keepAlive: false
            }
        },
        {   //语言设置
            path: '/language',
            name: 'language',
            component: () => import('@/page/language/index.vue'),
            meta: {
                keepAlive: false
            }
        },
        {   // 选择头像
            path: '/avatar/selection',
            name: 'avatarSelection',
            component: () => import('@/page/avatarSelection/index.vue'),
            meta: {
                keepAlive: false
            }
        },
        {
            path: '/iframe',
            name: 'iframe',
            component: () => import('@/page/me/iframe.vue'),

        },
        {
            path: '/complaint',
            name: 'complaint',
            component: () => import('@/page/complaint/index.vue'),
        },
        {   //贷款申请
            path: '/loan',
            name: 'loan',
            component: () => import('@/page/loan/index.vue'),
            meta: {
                keepAlive: false
            }
        },
        {   //贷款申请表单页
            path: '/loan/apply',
            name: 'loanApply',
            component: () => import('@/page/loanApply/index.vue'),
            meta: {
                keepAlive: false
            }
        },
        {   //贷款申请表单页
            path: '/loan/my',
            name: 'loanMy',
            component: () => import('@/page/loanMy/index.vue'),
            meta: {
                keepAlive: false
            }
        },
        {   //预计还款表单页
            path: '/repayment/expected',
            name: 'loanExpected',
            component: () => import('@/page/loanExpected/index.vue'),
            meta: {
                keepAlive: false
            }
        },
        { //客服
            path: '/customerService',
            name: 'customerService',
            component: () => import('@/page/customerService/index1.vue')
        }, { //客服2
            path: '/customerService2',
            name: 'customerService2',
            component: () => import('@/page/customerService/index.vue')
        }, { //客服 引导
            path: '/customerServiceIndex',
            name: 'customerServiceIndex',
            component: () => import('@/page/customerServiceIndex/index.vue')
        },
        {
            path: '/login',
            name: '/name',
            component: () => import('@/page/login/index.vue')
        },
        {
            path: '/register',
            name: 'register',
            component: () => import('@/page/register/index.vue')
        },
        // {
        //     path: '/forgetPassword',  // 忘记密码
        //     name: 'ForgetPassword',
        //     component: () => import('@/page/ForgetPassword/index.vue')
        // },
        
        { //设置
            path: '/Setting',
            name: 'Setting',
            component: () => import('@/page/Setting/index.vue')
        }, {
            //资金密码设置
            path: '/FundPasswordSettings',
            name: 'FundPasswordSettings',
            component: () => import('@/page/FundPasswordSettings/index.vue')
        }, {
            //资金密码重置
            path: '/FundPasswordReset',
            name: 'FundPasswordReset',
            component: () => import('@/page/FundPasswordReset/index.vue')
        }, {
            //登录密码重置
            path: '/LoginPasswordReset',
            name: 'LoginPasswordReset',
            component: () => import('@/page/LoginPasswordReset/index.vue')
        }, {
            //充值
            path: '/rechargeList',
            name: 'rechargeList',
            component: () => import('@/page/recharge/list/index.vue')
        }, {
            //充值
            path: '/recharge',
            name: 'recharge',
            component: () => import('@/page/recharge/index.vue')
        },
        {
            //充值记录列表
            path: '/rechargeRecord',
            name: 'rechargeRecord',
            component: () => import('@/page/recharge/Record/index.vue')
        },
        {
            //充值记录详情
            path: '/rechargeRecordDetails',
            name: 'rechargeRecordDetails',
            component: () => import('@/page/recharge/RecordDetails/index.vue')
        },
        {
            //提现
            path: '/withdraw',
            name: 'withdraw',
            component: () => import('@/page/withdraw/index.vue')
        },
        {
            //提现记录列表
            path: '/withdrawRecord',
            name: 'withdrawRecord',
            component: () => import('@/page/withdraw/Record/index.vue')
        },
        {
            //提现记录详情
            path: '/withdrawRecordDetails',
            name: 'withdrawRecordDetails',
            component: () => import('@/page/withdraw/RecordDetails/index.vue')
        }, {
            //完成页面
            path: '/SubmitCompleted',
            name: 'SubmitCompleted',
            component: () => import('@/page/SubmitCompleted/index.vue')
        }, {
            //地址列表
            path: '/AddressList',
            name: 'AddressList',
            component: () => import('@/page/AddressList/index.vue')
        }, {
            //地址详情
            path: '/AddressDetails',
            name: 'AddressDetails',
            component: () => import('@/page/AddressDetails/index.vue')
        }, {
            path: '/shop',
            name: 'shop',
            component: () => import('@/page/shop/index.vue'),
            meta: {
                keepAlive: false
            }
        }, {
            //商品详情
            path: '/CommodityDetails',
            name: 'CommodityDetails',
            component: () => import('@/page/CommodityDetails/index.vue'),
        },  
        {
            // 搜索
            path: '/search',
            name: 'Search',
            component: () => import('@/page/Search/index.vue'),
            meta: {
                keepAlive: false
            }
        }, 
        {
            // 店铺搜索
            path: '/store/search',
            name: 'storeSearch',
            component: () => import('@/page/storeSearch/index.vue'),
            meta: {
                keepAlive: false
            }
        }, 
        {
            //评价嗮单  EvaluationSheet
            path: '/EvaluationSheet',
            name: 'EvaluationSheet',
            component: () => import('@/page/EvaluationSheet/index.vue')
        }, {
            //评价  AllReviews
            path: '/AllReviews',
            name: 'AllReviews',
            component: () => import('@/page/AllReviews/index.vue')
        },
        {
            //商品收藏
            path: '/collectGoods',
            name: 'collectGoods',
            component: () => import('@/page/CollectGoods/index.vue')
        },
        {
            //店铺收藏
            path: '/collectShop',
            name: 'collectShop',
            component: () => import('@/page/CollectShop/index.vue')
        },
        {
            //我的订单
            path: '/order',
            name: 'Order',
            component: () => import('@/page/Order/index.vue')
        },
        {
            //订单详情
            path: '/orderDetails',
            name: 'OrderDetails',
            component: () => import('@/page/Order/Details/index.vue')
        },
        {
            //订单物流信息
            path: '/order/logistics',
            name: 'OrderLogistics',
            component: () => import('@/page/Order/Logistics/index.vue')
        },
        {
            //订单评价
            path: '/orderEvaluate',
            name: 'OrderEvaluate',
            component: () => import('@/page/Order/Evaluate/index.vue')
        },
        {
            //退款申请
            path: '/orderRefund',
            name: 'OrderRefund',
            component: () => import('@/page/Order/Refund/index.vue')
        },
        {
            //下单支付成功
            path: '/SuccessfulOperation',
            name: 'SuccessfulOperation',
            component: () => import('@/page/SuccessfulOperation/index.vue')
        },
        {
            //订单确认
            path: '/orderComnfirmation',
            name: 'orderComnfirmation',
            component: () => import('@/page/orderComnfirmation/index.vue')
        },
        {
            //待付款
            path: '/PendingPayment',
            name: 'PendingPayment',
            component: () => import('@/page/PendingPayment/index.vue')
        },
        {
            //分类查询
            path: '/Classification',
            name: 'Classification',
            component: () => import('@/page/Classification/index.vue')
        },
        {
            //商家端下载
            path: '/merchantDown',
            name: 'merchantDown',
            component: () => import('@/page/Merchant/merchantDown.vue')
        },
        {
            //商家入驻
            path: '/merchantSettled',
            name: 'merchantSettled',
            component: () => import('@/page/Merchant/merchantSettled.vue')
        }, {
            // 手机绑定
            path: '/BindPhone',
            name: 'BindPhone',
            component: () => import('@/page/BindPhone/index.vue')
        }, {
            // 手机绑定 - 已绑定
            path: '/BindPhoneBound',
            name: 'BindPhoneBound',
            component: () => import('@/page/BindPhone/Bound/index.vue')
        }, {
            // 邮箱绑定
            path: '/BindEmail',
            name: 'BindEmail',
            component: () => import('@/page/BindEmail/index.vue')
        }, {
            // 邮箱绑定 - 已绑定
            path: '/BindEmailBound',
            name: 'BindEmailBound',
            component: () => import('@/page/BindEmail/Bound/index.vue')
        }, 
        {
            // 消息中心
            path: '/information',
            name: 'Information',
            component: () => import('@/page/Information/index.vue')
        },
        {
            // 消息中心
            path: '/account/cancellation',
            name: 'accountCancellation',
            component: () => import('@/page/accountCancellation/index.vue')
        },
        {
            // 银行卡充值
            path: '/bank-card',
            name: 'bankCard',
            component: () => import('@/page/recharge/bankCard/index.vue')
        },

    ]
}))
router.beforeEach((to, from, next) => {
    sessionStorage.setItem('upperLevel', from.path)
    next()
})
export default router




