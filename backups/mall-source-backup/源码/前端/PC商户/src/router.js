/*
 * @Author: your name
 * @Date: 2022-03-03 21:23:53
 * @LastEditTime: 2023-01-17 01:24:45
 * @LastEditors: Please set LastEditors
 * @Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 * @FilePath: \www-pro\src\router.js
 */
import Vue from "vue";
import Router from "vue-router";
import { setLocal } from './lang/i18n'

//组件模块
// import Index from './components/index.vue'
// import market from './components/market.vue'
// import coinDetail from './components/coinDetail.vue'
Vue.use(Router);

// export default new Router({
// 	//base:'/pc/',
// 	routes: [
// 		{path: '/',redirect:'/index'},
// 		{path: '/index',name:'index',component:()=>import("@/page/mainPage")},//首页
// 		{path: '/login',name:'login',component:()=>import("@/page/login")},//登录
// 		{path: '/register',name:'index',component:()=>import("@/page/login/registert")},//注册
// 		{path: '/restPwd',name:'index',component:()=>import("@/page/login/restPwd")},//重置密码
// 		{path: '/coinDetail',name:'coinDetail',component:()=>import("@/page/market/coinDetail")},//币种详情
// 		{path: '/market',name:'market',component:()=>import("@/page/market/market")},//行情
// 		{path: '/trade/:id',name:'trade',component:()=>import("@/page/trade/index.vue")},//交易
// 		{path: '/promote',name:'promote',component:()=>import("@/page/promote/index.vue")},//推广中心
// 		{path: '/my',name:'my',redirect:'/my/dashboard',component:()=>import("@/page/my/index.vue"),
// 		children: [
// 			{ path: '/my/dashboard',name:'dashboard', component:()=>import("@/page/my/dashboard.vue")},//我的资产
// 			{ path: '/my/security',name:'security', component:()=>import('@/page/my/mysecurity.vue')},//帐户安全
// 			{ path: '/my/payment',name:'payment', component:()=>import('@/page/my/payment.vue')},//收款方式
// 			{ path: '/my/universal', name:'universal',component:()=>import('@/page/my/universal.vue')},//通用
// 			{ path:'/my/helpCenter',name:'helpCenter',component:()=>import("@/page/my/helpCenter.vue")}, //帮助中心
// 			{ path:'/my/announcement',name:'Announcement',component:()=>import("@/page/my/announcement.vue")},//公告中心
// 		  ]},
// 		{path: '/recharge',name:'recharge',component:()=>import("@/page/wallet/recharge")},//充值
// 		{path: '/wallet',name:'walletIndex',component:()=>import("@/page/wallet/walletIndex"),
// 		  children:[
// 			{path: '/wallet/walletOverview',name:'walletOverview',component:()=>import("@/page/wallet/walletOverview")},//钱包总览
// 			{path:'/wallet/spot',name:'spot',component:()=>import("@/page/wallet/spot")},//现货账户
// 			{path:'/wallet/contractAccounts',name:'contractAccounts',component:()=>import("@/page/wallet/contractAccounts")},//合约账户
// 			{path:'/wallet/financialAccounts',name:'financialAccounts',component:()=>import("@/page/wallet/financialAccounts")},//理财账户
// 			{path:'/wallet/walletHistory',name:'walletHistory',component:() =>import("@/page/wallet/walletHistory")} //钱包历史记录
// 		  ]
// 	    },
// 		{
// 		  path: '/order',name:'orderIndex',component:()=>import("@/page/order/orderIndex"),
// 		  children:[
// 			{path:'/order/contractHistoryOrder',name:'contractHistoryOrder',component:()=>import("@/page/order/contractHistoryOrder")},//合约历史
// 			{path:'/order/financialHistory',name:'financialHistory',component:()=>import("@/page/order/financialHistory")},//理财历史
// 			{path: '/order/changeRecord',name:'changeRecord',component:()=>import("@/page/order/changeRecord")},//账变记录
// 			{path: '/order/exchangeHistory',name:'exchangeHistory',component:()=>import("@/page/order/exchangeHistory")},//兑换历史
// 		  ]
// 		},
// 		{path: '/withdraw',name:'withdraw',component:()=>import("@/page/wallet/withdraw")},//提现
// 		{path: '/exchange',name:'exchange',component:()=>import("@/page/wallet/exchange")},//兑换
// 		{path: '/addressma',name:'address-management',component:()=>import("@/page/wallet/address-management")},//地址管理
// 		{path: '/fundMa',name:'fundMa',component:()=>import("@/page/wealth/financialManage")},//基金理财
// 		{path: '/fundMakc',name:'FundManageKuangChi',component:()=>import("@/page/wealth/lockMiner")},//矿池锁仓
// 	]
// })

const router = new Router({
    //base:'/pc/',
    routes: [
        { path: "/", redirect: "/index" },
        // 首页
        {
            path: "/index",
            name: "index",
            meta: {
                keepAlive: true,
            }, component: () => import("@/page/mainPage"),
        },
        {
            path: "/classification",
            name: "classification",
            meta: {
                keepAlive: true,
            }, component: () => import("@/page/classificationPage"),
        },
        {
            path: "/commodity",
            name: "commodity",
            meta: {
                keepAlive: true,
            }, component: () => import("@/page/commodityPage"),
        },
        // {
        //     path: "/merchantSettled",
        //     name: "merchantSettled",
        //     meta: {
        //         keepAlive: true,
        //     },
        //     component: () => import("@/page/merchantSettledPage"),
        // },
        {
            path: "/information",
            name: "information",
            meta: {
                keepAlive: true,
            }, component: () => import("@/page/informationPage"),
        },
        {
            path: "/productDetails",
            name: "productDetails",
            meta: {
                keepAlive: false,
            }, component: () => import("@/page/productDetailsPage"),
        },
        {
            path: "/login",
            name: "login",
            meta: {
                keepAlive: true,
            },
            component: () => import("@/page/loginPage"),
        },
        {
            path: "/register",
            name: "register",
            meta: {
                keepAlive: true,
            },
            component: () => import("@/page/registerPage"),
        },
        {
            path: "/store",
            name: "store",
            meta: {
                keepAlive: true,
            }, component: () => import("@/page/storePage"),
        },
        {
            path: "/searchStore",
            name: "SearchStore",
            meta: {
                keepAlive: false,
            }, component: () => import("@/page/searchStorePage"),
        },
        {
            path: "/searchGoods",
            name: "SearchGoods",
            meta: {
                keepAlive: true,
            }, component: () => import("@/page/searchGoodsPage"),
        },
        {
            path: "/userInfo",
            name: "userInfo",
            meta: {
                keepAlive: true,
            }, component: () => import("@/page/userInfo"),
            children: [
                {
                    path: "/",
                    redirect: "/userInfo/dashboard",
                },
                {
                    path: "dashboard",
                    name: "dashboard",
                    meta: {
                        keepAlive: true,
                    }, component: () => import("@/page/userInfo/dashboard"),
                },
                {
                    path: "my-order",
                    name: "my-order",
                    meta: {
                        keepAlive: true,
                    }, component: () => import("@/page/userInfo/my-order"),
                }, {
                    path: "order-detail",
                    name: "order-detail",
                    component: () => import("@/page/userInfo/my-order/orderDetail.vue")
                },
                {
                    path: 'order-return',
                    name: 'order-return',
                    component: () => import("@/page/userInfo/my-order/order-return.vue")
                },
                {
                    path: 'order-evaluation',
                    name: 'order-evaluation',
                    component: () => import("@/page/userInfo/my-order/order-evaluation.vue")
                },
                {
                    path: "download",
                    name: "download",
                    meta: {
                        keepAlive: true,
                    }, component: () => import("@/page/userInfo/download"),
                },
                {
                    path: "collect-goods",
                    name: "CollectGoods",
                    meta: {
                        keepAlive: true,
                    }, component: () => import("@/page/userInfo/collectGoods"),
                },
                {
                    path: "collect-shop",
                    name: "CollectShop",
                    meta: {
                        keepAlive: true,
                    }, component: () => import("@/page/userInfo/collectShop"),
                },
                {

                    path: "money-package",
                    name: "money-package",

                    meta: {
                        keepAlive: true,
                    }, 
                    component: () => import("@/page/userInfo/money-package"),
                },
                {
                    path: "money-package/recharge",
                    name: "money-package-recharge",
                    component: () => import("@/page/userInfo/money-package/recharge.vue"),
                },
                {
                    path: "money-package/withdraw",
                    name: "money-package-withdraw",
                    component: () => import("@/page/userInfo/money-package/withdraw.vue"),
                },
                {
                    path: "setup",
                    name: "setup",
                    meta: {
                        keepAlive: true,
                    }, component: () => import("@/page/userInfo/setup/layout"),
                    children: [
                        {
                            path: "/",
                            name: "setup-index",
                            meta: {
                                keepAlive: true,
                            }, component: () => import("@/page/userInfo/setup"),
                        },
                        {
                            path: "login-password",
                            name: "login-password",
                            meta: {
                                keepAlive: true,
                            }, component: () => import("@/page/userInfo/setup/login-password"),
                        },
                        {
                            path: "transaction-password",
                            name: "transaction-password",
                            meta: {
                                keepAlive: true,
                            }, component: () =>
                                import("@/page/userInfo/setup/transaction-password"),
                        },
                        {
                            path: "shipping-address",
                            name: "shipping-address",
                            meta: {
                                keepAlive: true,
                            }, component: () => import("@/page/userInfo/setup/shipping-address"),
                        },
                        {
                            path: "account-cancellation",
                            name: "account-cancellation",
                            meta: {
                                keepAlive: true,
                            }, component: () => import("@/page/userInfo/setup/log-out"),
                        },
                    ],
                },
            ],
        },
        {
            path: "/settlement",
            name: "settlement",
            meta: {
                keepAlive: false,
            }, component: () => import("@/page/settlementPage"),
        },
        {
            path: "/paySuccess",
            name: "paySuccess",
            meta: {
                keepAlive: false,
            }, component: () => import("@/page/settlementPage/paySuccess"),
        },
        {
            path: "/searchResult",
            name: "searchResult",
            meta: {
                keepAlive: false,
            }, component: () => import("@/page/searchResultPage"),
        },
        {
            path: "/discounted",
            name: "discounted",
            meta: {
                keepAlive: true,
            }, component: () => import("@/page/discounted"),
        },
        {
            path: "/credit",
            name: "credit",
            meta: {
                keepAlive: false,
            },
            component: () => import("@/page/creditPage/index.vue"),
            children: [
                {
                    path: "/",
                    name: "application",
                    meta: {
                        keepAlive: false,
                    }, component: () => import("@/page/creditPage/main.vue"),
                },
                {
                    path: "/credit/application",
                    name: "application",
                    meta: {
                        keepAlive: false,
                    }, component: () => import("@/page/creditPage/application.vue"),
                },
                {
                    path: "/credit/myLoan",
                    name: "myLoan",
                    meta: {
                        keepAlive: false,
                    }, component: () => import("@/page/creditPage/myLoan.vue"),
                },
            ]
        },
    ],
    // scrollBehavior() {
    //     return { x: 0, y: 0 };
    // },
    scrollBehavior(to, from) {
        if (to.fullPath === '/index') {
            return {x: 0, y: parseInt(localStorage.getItem('scroll'))}//读取本地的scroll
        } else {
            return {x: 0, y: 0};
        }
    }
});

const langMap ={
    en:'en',
    cn:"zh-CN",
    tw:"zh-TW",
    ja:"ja",
    de:"de",
    ms:"ms",
    af:"af",
    th:"th",
    el:"el",
    pt:"pt",
    es:"es",
    fr:"fr",
    ru:"ru",
    it:"it",
    tr:"tr",
    ko:"ko",
}

router.beforeEach((to, from, next) => {
    const hasLang = to.query && to.query.lang;
 
    if (hasLang && langMap[hasLang]) {
        setLocal(langMap[hasLang])
    }
    return next();
});

export default router