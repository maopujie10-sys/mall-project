import Vue from 'vue'
import store from './store';
import App from './App.vue'
import { i18n, vantLocales } from './i18n'
import '@/assets/remNew.js'
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getMessaging, getToken } from "firebase/messaging";
import router from '@/router/router'
import { Lazyload } from 'vant';
import { Button, Row, Col, NavBar, Search, Step, Steps, Notify, Image as VanImage } from 'vant'
import { formatZoneDate, is_mobile, getUrlVal } from '@/utils/utis'
import $cookie from "./storage/cookie";
import $localStorage from "./storage/localStorage";
import $sessionStorage from "./storage/sessionStorage";
import { Input, Table, TableColumn, Select, Option, Form, FormItem } from 'element-ui';
import '@/assets/css/element-variables.scss';
import '@/styles/index.scss';
import Storage from 'vue-ls';
import dayjs from "dayjs";
import tz from "dayjs/plugin/timezone";
import utc from "dayjs/plugin/utc";
import Big from 'big.js'
import slideVerify from "vue-monoplasty-slide-verify";
import VueClipboard from 'vue-clipboard2'
import VueAwesomeSwiper from 'vue-awesome-swiper'
import INotify from "@wcjiang/notify";

import 'swiper/dist/css/swiper.css'
import './permission'
import '@/assets/css/root.css'
import 'vant/lib/icon/local.css';

document.documentElement.style.setProperty(`--main-color`, process.env.VUE_APP_MAIN_COLOR);
document.documentElement.style.setProperty(`--main-footer-color`, process.env.VUE_APP_FOOTER_COLOR);
if (localStorage.getItem('lang') == 'ar') {
    document.documentElement.setAttribute('dir', 'rtl');
} else {
    document.documentElement.setAttribute('dir', 'ltr');
}

if (!is_mobile() && !process.env.VUE_APP_PUT_ON_SHELVES) {
    const goodsId = getUrlVal('sellerGoodsId')
    const sellerId = getUrlVal('sellerId')
    const lang = localStorage.getItem('lang')
    if (goodsId) {
        location.href = location.origin + '/#/productDetails?id=' + goodsId + '&lang=' + lang
    } else if (sellerId) {
        location.href = location.origin + '/#/store?id=' + sellerId + '&lang=' + lang
    } else {
        location.href = location.origin
    }
}
Vue.prototype.$plus = (num1, num2) => new Big(num1).plus(num2)     // +
Vue.prototype.$minus = (num1, num2) => new Big(num1).minus(num2)   // -
Vue.prototype.$times = (num1, num2) => new Big(num1).times(num2)   // *
Vue.prototype.$div = (num1, num2) => new Big(num1).div(num2)       // /

Vue.prototype.$operation = (num1, num2, rule) => {
    if (Number(num1) && Number(num2)) {
        return new Big(num1)[rule](num2)
    } else {
        return 0
    }
}

Vue.config.productionTip = false

dayjs.extend(utc);
dayjs.extend(tz);

const storageOptions = {
    namespace: '', // key 键的前缀
    name: 'ls', // 变量名称，使用方式：Vue.变量名称 或 this.$变量名称
    storage: 'local', // 存储名称: local, session, memory
};
vantLocales(i18n.locale)//组件国际化

Vue.use(Button).use(Row).use(Col).use(NavBar).use(Search).use(VanImage)

Vue.use(dayjs);
Vue.use(Storage, storageOptions);
Vue.use(Input);
Vue.use(Table);
Vue.use(TableColumn);
Vue.use(Select);
Vue.use(Option);
Vue.use(Step);
Vue.use(Form);
Vue.use(FormItem);
Vue.use(Steps);
Vue.use(VueAwesomeSwiper);
Vue.use(Notify);
Vue.use(Lazyload, {
    lazyComponent: true,
});


Vue.use(slideVerify);

Vue.use(VueClipboard)

Vue.prototype.$formatZoneDate = formatZoneDate
Vue.prototype.$notifyWarn = (message) => Notify({ message });
Vue.prototype.$notify = (message, type) => Notify({ type, message });
Vue.prototype.$cookie = $cookie;
Vue.prototype.dayjs = dayjs;
// Global localStorage method $localStorage
Vue.prototype.$localStorage = $localStorage;
// Global sessionStorage method $sessionStorage
Vue.prototype.$defaultGoodsImage = require('@/assets/image/default_goods.png')
Vue.prototype.$sessionStorage = $sessionStorage;
Vue.prototype.$textOmit = (text = '', num = 30) => {
    if (text == null) return '';
    const str = text.replace(/(?:\uD83C[\uDF00-\uDFFF]|\uD83D[\uDC00-\uDE4F])/g, '').replace(/[^\x00-\xff]/g, ' ');
    const len = str.length
    if (len <= num) return text;
    let index = 0;
    let count = 0;
    while (index < len) {
        const code = str.charCodeAt(index)
        count += code >= 0 && code <= 128 ? 1 : 2
        if (count > num) {
            return text.slice(0, index) + '...'
        } index++
    }
    return text
}

// start

const firebaseConfig = {
    apiKey: "AIzaSyCAfTDznXqUGIw8odfEwVgmCg_2KwWnRps",
    authDomain: "fir-eb636.firebaseapp.com",
    projectId: "fir-eb636",
    storageBucket: "fir-eb636.appspot.com",
    messagingSenderId: "270054984552",
    appId: "1:270054984552:web:cdf4559c94bac0e24d64dd",
    measurementId: "G-T6XQDEYV5R"
};
try {
    const FirebaseApp = initializeApp(firebaseConfig);
    const analytics = getAnalytics(FirebaseApp);
    const messaging = getMessaging(FirebaseApp);
    // 私钥  Xmy2tjgkBmpokpBHmgmNOs6Ez_rP_Fcsi8UQwV5HxF0
    getToken(messaging, { vapidKey: "BOQ1p4ycdvk9bvgwjsBq2XiM1P50hjH5KN-LI13TY6t0wtF1vrxJYAuixdzGS1KjAm3M5SFCNGz7eY5OeNu2J4M" }); 
} catch (error) {
    console.error('初始化失败'+error);
}

// function requestPermission() {
//     console.log('Requesting permission...');

//     Notification.requestPermission().then((permission) => {
//         console.log('permission', permission)
//         if (permission === 'granted') {
//             console.log('已经授权通知，可以进行你的通知啦！');
//             // new Notification("通知标题：", {
//             //     body: '通知内容',
//             //     icon: 'https://pic1.zhuanstatic.com/zhuanzh/50b6ffe4-c7e3-4317-bc59-b2ec4931f325.png',
//             //     vibrate: [300, 100, 300],
//             // })
//             const iNotify = new INotify({
//                 effect: 'flash',
//                 interval: 500,
//             });
//             iNotify.setFavicon('1');
//             iNotify.setTitle('New title');
//             iNotify.setInterval(200);
//             iNotify.notify({ openurl: 'http://localhost:8084/#/admin/home' });
//         } else if (permission === 'default') {
//             console.log('用户还未选择同意/拒绝');
//         } else {
//             console.log('用户曾经拒绝授权,不能显示通知');
//         }
//     })
// }
if(process.env.VUE_APP_ITEM_NAME == 'EShop') {
    requestPermission()
}

// end


const $this = new Vue({
    //  Router:Router,
    store: store,
    i18n,
    router: router,
    render: h => h(App),
}).$mount('#app')

export default $this


/**
 * 2023/10/26  周四
 *  商城项目:
 *     新增多语言
 *     研究Firebase Cloud Messaging（FCM)推送
 *     JustShop更换为SM-wholesaleShop
 *     SM-wholesaleShop差异修改
 */
