import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

export default new Router({
    routes: [
        {
            path: '/',
            name: 'index',
            // component: () => import('@/page/home.vue'),
            component:() => import('@/page/Merchant/merchantSettled.vue')
        },
        {
            path: '*',
            redirect: '/home'
        },
        {
            path: '/pact',
            name: 'pact',
            component: () => import('@/page/Merchant/pact.vue')
        },
        {   //语言设置
            path: '/language',
            name: 'language',
            component: () => import('@/page/language/index.vue')
        },
        { //客服
            path: '/customerService',
            name: 'customerService',
            component: () => import('@/page/customerService/index.vue')
        },{ //客服2
            path: '/customerService2',
            name: 'customerService2',
            component: () => import('@/page/customerService/index.vue')
        },{ //客服 引导
            path: '/customerServiceIndex',
            name: 'customerServiceIndex',
            component: () => import('@/page/customerServiceIndex/index.vue')
        },
        {
            //商家入驻
            path:'/merchantSettled',
            name:'merchantSettled',
            component:() => import('@/page/Merchant/merchantSettled.vue')
        },{
            // 卖家政策
            path:'/shippingPolicy',
            name:'shippingPolicy',
            component:() =>import('@/page/Merchant/shippingPolicy.vue')
        },{
            // 隐私
            path:'/privacyPolicy',
            name:'privacyPolicy',
            component:() =>import('@/page/Merchant/privacyPolicy.vue')
        },{
            // 送货
            path:'/delivery',
            name:'delivery',
            component:() =>import('@/page/Merchant/Delivery.vue')
        },{
            // 退货
            path:'/returnPolicy',
            name:'returnPolicy',
            component:() =>import('@/page/Merchant/returnPolicy.vue')
        },{
            // 借款协议
            path:'/contract',
            name:'contract',
            component:() =>import('@/page/Merchant/contract.vue')
        },{
            // 关于我们
            path:'/aboutUs',
            name:'aboutUs',
            component:() =>import('@/page/Merchant/aboutUs.vue')
        },{
            // 关于我们 hive
            path:'/Hive-about',
            name:'about',
            component:() =>import('@/page/Merchant/about.vue')
        },{
            // 关于我们 hive
            path:'/TikTok-about',
            name:'about',
            component:() =>import('@/page/Merchant/aboutTikTok.vue')
        },{
            path:'/enterprise-prove',
            name:'enterprise',
            component:() =>import('@/page/Merchant/enterprise.vue')
        },{
            path:'/AShippingPolicy',
            name:'AgrosShippingPolicy',
            component:() =>import('@/page/Merchant/ArgosShippingPolicy.vue')
        },{
            path:'/WShippingPolicy',
            name:'WortenShippingPolicy',
            component:() =>import('@/page/Merchant/wortenShippingPolicy.vue')
        },{
            path:'/WPrivacyPolicy',
            name:'WPrivacyPolicy',
            component:() =>import('@/page/Merchant/WPrivacyPolicy.vue')
        },{
            path:"/supportPolicy",
            name:"supportPolicy",
            component:() =>import('@/page/Merchant/supportPolicy.vue')
        }
    ]
})
