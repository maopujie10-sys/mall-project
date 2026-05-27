/*
 * @Author: your name
 * @Date: 2022-03-03 21:23:53
 * @LastEditTime: 2022-03-25 22:17:44
 * @LastEditors: Please set LastEditors
 * @Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 * @FilePath: \www-pro\src\main.js
 */
import Vue from "vue";
import App from "./App.vue";
import QRCode from "qrcodejs2";
import axios from "axios";
import i18n from "./lang/i18n";
import VueSlider from "vue-slider-component";
import { post, fetch, patch, put } from "./util/http";
import ElementUI from "element-ui";
import echarts from "echarts";
import VueCountryIntl from "vue-country-intl";
import SlideVerify from "vue-monoplasty-slide-verify";
import router from "./router";
import store from "./store";
import * as socketApi from "./api/socket";
import VueAwesomeSwiper from "vue-awesome-swiper";
import HeaderView from "./components/header";
import FooterView from "./components/footer";
import ShopCartView from "./components/shopCart";
import LoadingView from "./components/loading";
import OnlineServiceView from './components/customService'
import Big from 'big.js'
import "./assets/sass/index.scss";
import "vue-country-intl/lib/vue-country-intl.css";
import "vue-slider-component/theme/default.css";
import "../src/assets/css/index.css";
import "../src/assets/css/varCss.css";
import "../src/assets/css/public.css";
import "element-ui/lib/theme-chalk/index.css";
import "./element-#F89900/index.css";
import "element-ui/lib/theme-chalk/index.css";
import "./element-#F89900/index.css";
import "swiper/css/swiper.css";
import './assets/icons'
import './assets/iconfont/iconfont.css'
import vuePhotoZoomPro from 'vue-photo-zoom-pro'
import { gsap } from "gsap";
Vue.prototype.$axios = axios;
Vue.prototype.$post = post;
Vue.prototype.$fetch = fetch;
Vue.prototype.$patch = patch;
Vue.prototype.$put = put;
Vue.prototype.$qrCode = QRCode;
Vue.prototype.$echarts = echarts;
Vue.config.productionTip = false;
Vue.prototype.TITLE = process.env.VUE_APP_TITLE;
Vue.prototype.socketApi = socketApi;
Vue.prototype.$GloExchangeRate = "00000";
Vue.prototype.$big = Big
Vue.prototype.$Gsap = gsap

Vue.use(ElementUI);
Vue.use(SlideVerify);
Vue.use(router);
Vue.use(gsap);
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
// Global registration component
Vue.component("VueSlider", VueSlider);
Vue.component(VueCountryIntl.name, VueCountryIntl);
Vue.component("EsHeaderView", HeaderView);
Vue.component("EsFooterView", FooterView);
Vue.component("EsShopCartView", ShopCartView);
Vue.component("EsLoadingView", LoadingView);
Vue.component("EsOnlineServiceView", OnlineServiceView);
Vue.use(VueAwesomeSwiper);
Vue.use(vuePhotoZoomPro)

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
  'Tongda':{
    name: 'Tongda',
    mail: 'support@tongdasvip.com'
  },
  'Shopee': {
    name: 'Shopee',
    mail: 'support@shopee-asiaus.com'
  },
  'TikTok': {
    name: 'TikTok',
    mail: 'support@tiktokmallit.com'
  },
  'Shop2u': {
      name: 'Shop2u',
      mail: 'support@shop2u.co'
  },
  "Green Mall": {
    name: "Green Mall",
    mail: 'support@greenmallus.com'
  },
  "SM-wholesale shop": {
    name: "SM-wholesale shop",
    mail: 'support@justshopvip.com'
  },
  "ArgosShop": {
    name: "ArgosShop",
    mail: "support@argosshopvip.com"
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
  }
}
Vue.prototype.$multiItem = multiItem
// import titleSmall from './components/titleSmall.vue';//引入组件
// Vue.component('title-small',titleSmall)//注册组件

// import FooterView from './components/footerView.vue';//引入组件
// Vue.component('FooterView',FooterView)//注册组件

// import listCoins from './components/listCoins.vue';//引入组件
// Vue.component('listCoins',listCoins)//注册组件

////import {tools} from './util/tools'
//Vue.use(tools)
const is_mobile = () => {
  var regex_match = /(nokia|iphone|android|motorola|^mot-|softbank|foma|docomo|kddi|up.browser|up.link|htc|dopod|blazer|netfront|helio|hosin|huawei|novarra|CoolPad|webos|techfaith|palmsource|blackberry|alcatel|amoi|ktouch|nexian|samsung|^sam-|s[cg]h|^lge|ericsson|philips|sagem|wellcom|bunjalloo|maui|symbian|smartphone|midp|wap|phone|windows ce|iemobile|^spice|^bird|^zte-|longcos|pantech|gionee|^sie-|portalmmm|jigs browser|hiptop|^benq|haier|^lct|operas*mobi|opera*mini|320x320|240x320|176x220)/i;
  var u = navigator.userAgent;
  if (null == u) {
    return true;
  }
  var result = regex_match.exec(u);
  if (null == result) {
    return false
  } else {
    return true
  }
}
const getUrlVal = (name) => {
  let url = location.href
  let urlStr = url?.split('?')[1]
  // 创建空对象存储参数
  let obj = {};
  // 再通过 & 将每一个参数单独分割出来
  let paramsArr = urlStr?.split('&')
  if (paramsArr) {
    for (let i = 0, len = paramsArr?.length; i < len; i++) {
      // 再通过 = 将每一个参数分割为 key:value 的形式
      let arr = paramsArr[i]?.split('=')
      obj[arr[0]] = arr[1];
    }
  }
  return obj[name]
}

if (is_mobile()) {
  const goodsId = getUrlVal('id')
  const storeId = getUrlVal('storeId')
  const lang = localStorage.getItem('ES_LANG')
  if (goodsId) {
    location.href = location.origin + '/wap/#/CommodityDetails?sellerGoodsId=' + goodsId + '&lang=' + lang
  } else if (storeId) {
    location.href = location.origin + '/wap/#/shop?sellerId=' + storeId + '&lang=' + lang
  } else {
    location.href = location.origin + '/wap'
  }
}

new Vue({
  render: (h) => h(App),
  router,
  i18n,
  store,
}).$mount("#app");

String.prototype.format = function (args) {
  if (arguments.length > 0) {
    var result = this;
    if (arguments.length == 1 && typeof args == "object") {
      for (var key in args) {
        var reg = new RegExp("({" + key + "})", "g");
        result = result.replace(reg, args[key]);
      }
    } else {
      for (var i = 0; i < arguments.length; i++) {
        if (arguments[i] == undefined) {
          return "";
        } else {
          var reg = new RegExp("({[" + i + "]})", "g");
          result = result.replace(reg, arguments[i]);
        }
      }
    }
    return result;
  } else {
    return this;
  }
};
