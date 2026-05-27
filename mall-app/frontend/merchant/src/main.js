import Vue from 'vue'
import Cookies from 'js-cookie'
import 'normalize.css/normalize.css' // a modern alternative to CSS resets
import '@vant/touch-emulator';
import Element from 'element-ui'
import './styles/element-variables.scss'
import '@/styles/index.scss' // global css
import App from './App'
import store from './store'
import router from './router'
import './icons' // icon
import './permission' // permission control
import './utils/error-log' // error log
import * as filters from './filters' // global filters
import './assets/init.scss'
import {i18n} from './lang'
import setBootSteps from "@/components/SetBootSteps"; //test
import moment from "moment-timezone";
import BigDecimal from 'js-big-decimal'

Vue.prototype.$bigDecimal = BigDecimal //全局注册，使用方法为:this.$bigDecimal
// 加 this.$bigDecimal.add(1, 2)
// 减 this.$bigDecimal.subtract(1, 2)
// 乘 this.$bigDecimal.multiply(1, 2)
// 除 this.$bigDecimal.divide(1, 2)
// 比较大小 this.$bigDecimal.compare(1, 2)

Vue.component('SetBootSteps', setBootSteps)

/**
 * If you don't want to use mock-server
 * you want to use MockJs for mock api
 * you can execute: mockXHR()
 *
 * Currently MockJs will be used in the production environment,
 * please remove it before going online ! ! !
 */
if (process.env.NODE_ENV === 'production') {
    const {mockXHR} = require('../mock')
    mockXHR()
}

Vue.use(Element, {
    size: Cookies.get('size') || 'medium', // set element-ui default size
    // locale: enLang // 如果使用中文，无需设置，请删除
    i18n: (key, value) => i18n.t(key, value)
})
const formatZoneDate = (time) => {
    if (!time) return '--'
    //设置服务器默认时区
    moment.tz.setDefault('Asia/Shanghai') //设置中国时区
    time = moment(time)
    //获取当前时区
    let timezone = moment.tz.guess(true)
    //time转成当前时区的时间
    time = moment.tz(time, timezone).format('YYYY-MM-DD HH:mm:ss')
    return time
}
Vue.prototype.$formatZoneDate = formatZoneDate
Vue.filter('formatZoneDate', formatZoneDate)
// register global utility filters
Object.keys(filters).forEach(key => {
    Vue.filter(key, filters[key])
})

Vue.config.productionTip = false
Number.prototype.toFloor = function (num) {
    if (num < 0) {
        return this;
    }
    const nnum = Number.parseFloat(this);
    const str = nnum.toString();
    const arr = str.split(".");
    const strZ = arr[0];// arr[0] 整数部分，arr[1] 小数部分
    let strX = ""; // 小数点与小数部分
    if (arr.length > 1) { // 有小数
        if (num > 0) {
            if (arr[1].length >= num) { // 小数长，保留位短
                strX = arr[1].substr(0, num);
            } else { // 小数短，保留位长
                const zeroArr = [];
                for (let i = 0; i < num - arr[1].length; i++) {
                    zeroArr.push(0);
                }
                strX = arr[1].toString() + zeroArr.join("");
            }
            strX = "." + strX;
        }
    } else { // 无小数
        if (num > 0) {
            const zeroArr = [];
            for (let i = 0; i < num; i++) {
                zeroArr.push(0);
            }
            strX = "." + zeroArr.join("");
        }
    }
    const result = strZ + "" + strX;
    return result;
};

new Vue({
    el: '#app',
    router,
    store,
    i18n,
    render: h => h(App)
});
