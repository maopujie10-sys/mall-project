import Vue from "vue";
import Router from "vue-router";
import Layout from "@/layout";
import settings from "@/settings";

Vue.use(Router);

export const constantRoutes = [
    {
        path: "/redirect",
        component: Layout,
        hidden: true,
        children: [
            {
                path: "/redirect/:path(.*)",
                component: () => import("@/views/redirect/index"),
            },
        ],
    },
    {
        path: "/login",
        component: () => import("@/views/login/login.vue"),
        hidden: true,
    },
    {
        path: "/auth-redirect",
        component: () => import("@/views/login/auth-redirect"),
        hidden: true,
    },
    {
        path: "/404",
        component: () => import("@/views/error-page/404"),
        hidden: true,
    },
    {
        path: "/401",
        component: () => import("@/views/error-page/401"),
        hidden: true,
    },
    {
        path: "/",
        component: Layout,
        redirect: "/dashboard",
        children: [
            {
                path: "dashboard",
                component: () => import("@/views/dashboard/index"),
                name: "Dashboard",
                meta: {title: "仪表盘", icon: "dashboard"},
                activeMenu: '/dashboard'
            },
        ],
    },
    // {
    //   path: "/chat",
    //   component: Layout,
    //   children: [
    //     {
    //       path: "index",
    //       component: () => import("@/views/chat/index"),
    //       name: "Message",
    //       meta: {title: "买家消息", icon: "message", affix: true, showMessagesNumber: true},
    //     },
    //   ],
    // },
    {
        path: "/chat2",
        component: Layout,
        children: [
            {
                path: "index",
                component: () => import("@/views/chat2/index"),
                name: "Dashboard",
                // meta: {title: "客服", icon: "message", affix: true},
            },
        ],
    },
    {
        path: "/documentation",
        component: Layout,
        children: [
            {
                path: "index",
                component: () => import("@/views/documentation/index"),
                name: "Documentation",
                meta: {title: "店铺订单", icon: "el-icon-s-order"},
            },
        ],
    },
    {
        path: "/financial",
        component: Layout,
        children: [
            {
                path: "index",
                component: () => import("@/views/financial/index"),
                name: "financial",
                meta: {title: "财务报表", icon: "el-icon-s-marketing"},
            },
        ],
    },
    {
        path: "/wallet",
        component: Layout,
        redirect: "/wallet/page",
        name: "wallet",
        // meta: {title: '我的钱包'},
        children: [
            {
                path: "index",
                component: () => import("@/views/permission/page"),
                name: "PagePermission",
                meta: {
                    title: "我的钱包",
                    icon: "el-icon-s-finance",
                },
            },
            {
                path: "withdraw",
                component: () => import("@/views/permission/withdraw"),
                name: "withdraw",
                alwaysShow: true,
                hidden: true,
                meta: {
                    title: "提现",
                },
            },
            {
                path: "Recharge",
                component: () => import("@/views/permission/recharge"),
                name: "Recharge",
                alwaysShow: true,
                hidden: true,
                meta: {
                    title: "充值",
                },
            },
        ],
    },
    {
        path: "/money",
        component: Layout,
        children: [
            {
                path: "index",
                component: () => import("@/views/money/index"),
                name: "money",
                meta: {title: "资金记录", icon: "documentation"},
            },
        ],
    },
    {
        path: "/shopList",
        component: Layout,
        name: "shopList",
        meta: {
            title: "商品管理",
            icon: "el-icon-s-cooperation",
        },
        children: [
            {
                path: "merchandise",
                component: () => import("@/views/shop/merchandise"),
                name: "merchandise",
                meta: {title: "店铺商品", icon: "el-icon-goods", noCache: true},
            },
            {
                path: "refund",
                component: () => import("@/views/shop/refund"),
                name: "refund",
                meta: {title: "退款请求", icon: "el-icon-warning"},
            },
            {
                path: "comment",
                component: () => import("@/views/shop/comment"),
                name: "comment",
                meta: {title: "商品评论", icon: "el-icon-chat-dot-square"},
            },
            {
                path: "library",
                component: () => import("@/views/shop/library"),
                name: "library",
                meta: {title: "商品库", icon: "el-icon-s-home", noCache: true},
            },
        ],
    },
    {
        path: "/other",
        component: Layout,
        name: "other",
        meta: {
            title: "其他",
            icon: "el-icon-menu",
        },
        children: [
            {
                path: "shopSetting",
                component: () => import("@/views/other/shopSetting"),
                name: "shopSetting",
                meta: {title: "店铺设置", icon: "el-icon-s-tools"},
            },
            {
                path: "promotion",
                component: () => import("@/views/other/promotion"),
                name: "promotion",
                meta: {title: "创业联盟", icon: "el-icon-s-flag"},
            },
            ///destroyAccount
            {
                path: "destroyAccount",
                component: () => import("@/views/other/destroyAccount"),
                name: "destroyAccount",
                hidden: true,
                meta: {title: "注销账号", icon: "el-icon-s-release"},
            },
        ],
    },
    {
        path: "/marketing",
        component: Layout,
        name: "marketing",
        meta: {
            title: "营销工具",
            icon: "el-icon-s-data",
        },
        children: [
            {
                path: "car",
                component: () => import("@/views/marketing/car"),
                name: "car",
                meta: {title: "店铺直通车", icon: "el-icon-truck"},
            },
            {
                path: "buyHistory",
                component: () => import("@/views/marketing/buyHistory"),
                name: "buyHistory",
                meta: {title: "购买历史", icon: "el-icon-time"},
            },
            {
                path: "sellerLevel",//卖家等级
                component: () => import("@/views/marketing/sellerLevel"),
                name: "sellerLevel",
                meta: {title: "卖家等级", icon: "el-icon-sell", unShow: settings.hideSellerLevel},
            },
        ],
    },
    // {
    //   path: "/categoryProducts",
    //   component: Layout,
    //   name: "categoryProducts",
    //   children: [
    //     {
    //       path: "index",
    //       component: () => import("@/views/categoryProducts/index"),
    //       name: "index",
    //       meta: { title: "分类产品", icon: "edit" },
    //     }
    //   ],
    // },
    // {
    //   path: "/profile",
    //   component: Layout,
    //   redirect: "/profile/index",
    //   hidden: true,
    //   children: [
    //     {
    //       path: "index",
    //       component: () => import("@/views/profile/index"),
    //       name: "Profile",
    //       meta: { title: "Profile", icon: "user", noCache: true },
    //     },
    //   ],
    // },
];

/**
 * asyncRoutes
 * the routes that need to be dynamically loaded based on user roles
 */
export const asyncRoutes = [


    /** when your routing map is too long, you can split it into small modules **/
    // componentsRouter,
    // chartsRouter,
    // nestedRouter,
    // tableRouter,


    // 404 page must be placed at the end !!!
    {path: "*", redirect: "/404", hidden: true},
];

const createRouter = () =>
    new Router({
        // mode: 'history', // require service support
        scrollBehavior: () => ({y: 0}),
        routes: constantRoutes,
    });

const router = createRouter();

// Detail see: https://github.com/vuejs/vue-router/issues/1234#issuecomment-357941465
export function resetRouter() {
    const newRouter = createRouter();
    router.matcher = newRouter.matcher; // reset router
}

export default router;
