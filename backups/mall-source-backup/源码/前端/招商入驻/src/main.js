import Vue from 'vue'
import store from './store';
import App from './App.vue'
import { i18n, vantLocales ,elementLocales} from './i18n'
import '@/assets/remNew.js'
import router from '@/router/router'
import { Button, Col, NavBar, Row, Search, Icon,Popup,Image as VanImage } from 'vant'
// console.log('Router',Router)
import $cookie from "./storage/cookie";
import $localStorage from "./storage/localStorage";
import $sessionStorage from "./storage/sessionStorage";
import { Button as ElButton, Dialog, Image, Input, Option, Select, Table, TableColumn, Upload, Tooltip } from 'element-ui';
import '@/assets/css/element-variables.scss';
import '@/styles/index.scss';
import "@/styles/varCss.css";
import Storage from 'vue-ls';
import slideVerify from "vue-monoplasty-slide-verify";
import VueClipboard from 'vue-clipboard2'
import '@vant/touch-emulator';

// permission
import './permission'

Vue.config.productionTip = false
Vue.use(Button).use(Row).use(Col).use(NavBar).use(Search).use(Popup).use(VanImage)
vantLocales(i18n.locale)//组件国际化
elementLocales(i18n.locale)//组件国际化
const storageOptions = {
    namespace: '', // key 键的前缀
    name: 'ls', // 变量名称，使用方式：Vue.变量名称 或 this.$变量名称
    storage: 'local', // 存储名称: local, session, memory
};
import moment from "moment-timezone";
const formatZoneDate = (time) => {
    if (!time) return '--'
    //设置服务器默认时区
    moment.tz.setDefault('Asia/Shanghai')
    time = moment(time)
    //获取当前时区
    let timezone = moment.tz.guess(true)
    //time转成当前时区的时间
    time = moment.tz(time, timezone).format('YYYY-MM-DD HH:mm:ss')
    return time
}
Vue.prototype.$formatZoneDate = formatZoneDate
Vue.filter('formatZoneDate', formatZoneDate)
Vue.use(Storage, storageOptions);
Vue.use(Input);
Vue.use(Table);
Vue.use(TableColumn);
Vue.use(Select);
Vue.use(Option);
Vue.use(Dialog);
Vue.use(Image);
Vue.use(Button);
Vue.use(Icon)
Vue.use(ElButton)
Vue.use(Upload)
Vue.use(Tooltip)
Vue.use(slideVerify);
Vue.use(VueClipboard)


Vue.prototype.$cookie = $cookie;

// Global localStorage method $localStorage
Vue.prototype.$localStorage = $localStorage;

// Global sessionStorage method $sessionStorage
Vue.prototype.$sessionStorage = $sessionStorage;
const multiItem = {
    'EShop': {
        name: 'EShop',
        mail: 'Eshop@Eshop.com',
        bucket: 'ht-shop-test',
    },
    'Argos': {
        name: 'Argos',
        mail: 'support@argos.me',
        bucket: 'argos-shop-online',
    },
    'Mbuy': {
        name: 'Mbuy',
        mail: 'support@mbuy.world',
        bucket: 'ht-shop-test',
    },
    'Inchoi': {
        name: 'Inchoi',
        mail: 'support@inchoius.com',
        bucket: 'ht-shop-test',
    },
    'MetaShop': {
        name: 'MetaShop',
        mail: 'support@e-metashop.com',
        bucket: 'ht-shop-test',
    },
    'Hive': {
    name: 'Hive',
    mail: 'support@hivemalls.com'
    },
    'FamilyMart': {
        name: 'FamilyMart',
        mail: 'support@e-familymart.com'
    },
    'FamilyShop': {
        name: 'FamilyShop',
        mail: 'support@familyshopvip.com'
    },
    'Shopee': {
      name: 'Shopee',
      mail: 'support@familyshopvip.com'
    },
    'Tongda':{
      name: 'Tongda',
      mail: 'support@tongdasvip.com'
    },
    'TikTok': {
      name: 'TikTok',
      mail: 'support@tiktokmallit.com'
    },
    'Shop2u': {
        name: 'Shop2u',
        mail: 'support@shop2u.co'
    },
    "GreenMall": {
      name: "GreenMall",
      mail: 'support@greenmallus.com'
    },
    "SM-wholesale shop": {
      name: "SM-wholesale shop",
      mail: 'support@justshopvip.com'
    },
    "Laz": {
      name: "Laz",
      mail: "support@lazshopvip.com"
    },
    "Iceland": {
      name: "Iceland",
      mail: "support@icelandmartvip.com"
    },
    "INT Overstock": {
      name: "INT Overstock",
      mail: "support@overstock8.me"
    },
    "TikTok-Wholesale":{
      name: "TikTok-Wholesale",
      mail: "support@wholesalesvip.com"
    },
    "AntMall": {
      name: "AntMall",
      mail: "support@antmallus.com"
    },
    "SIMON":{
      name: "SIMON",
      mail: "support@simonshopus.com"
    },
    "Texm": {
      name: "Texm",
      mail: "support@texmuk.com"
    },
    "Alibaba": {
      name: "Alibaba",
      mail: "iruddh22@gmail.com"
    },
    "Azedi": {
      name: "Azedi",
      mail: "support@azedius.com"
    },
    "Argos Shop": {
        name: "Argos Shop",
        mail: "support@wortenus.com"
    },
    "Sam-wholesaleShop": {
      name: "Sam-wholesaleShop",
      mail: "support@sammallus.com"
    } 
}
Vue.prototype.$multiItem = multiItem
new Vue({
    //  Router:Router,
    store: store,
    i18n,
    router: router,
    render: h => h(App),
}).$mount('#app')
