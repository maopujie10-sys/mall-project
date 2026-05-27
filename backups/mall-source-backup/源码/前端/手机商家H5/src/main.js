const whiteHash = ['login-agreement', 'activity/']

function isPassPage(str) {
    for (let i = 0; i < whiteHash.length; i++) {
        if (str.indexOf(whiteHash[i]) > -1) {
            return true
        }
    }
    return false
}

function iswap() {
    var uA = navigator.userAgent.toLowerCase();
    var ipad = uA.match(/ipad/i) == "ipad";
    var iphone = uA.match(/iphone os/i) == "iphone os";
    var midp = uA.match(/midp/i) == "midp";
    var uc7 = uA.match(/rv:1.2.3.4/i) == "rv:1.2.3.4";
    var uc = uA.match(/ucweb/i) == "ucweb";
    var android = uA.match(/android/i) == "android";
    var windowsce = uA.match(/windows ce/i) == "windows ce";
    var windowsmd = uA.match(/windows mobile/i) == "windows mobile";
    if (!(ipad || iphone || midp || uc7 || uc || android || windowsce || windowsmd)) {
        // PC 端访问了手机端，应导航到PC端后台
        const hash = window.location.hash
        if (window.location.href.indexOf('www') > 0 && !isPassPage(hash)) {
            window.location.href = 'https://' + window.location.host + '/ww'
        }
    }else{

    }
}

iswap()


import {createApp} from 'vue'
import './assets/css/index.css'
import './assets/css/init.css'
import 'vant/lib/index.css'
import fxHeader from '@/components/fx-header'
import 'default-passive-events'
// import './assets/css/init.scss'
// import 'amfe-flexible'
import App from './App.vue'
import i18n from '@/i18n'
import 'vant/es/toast/style';
import router from '@/router'
import pinia from '@/store'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import dayjs from "dayjs";
// import '@vant/touch-emulator';
import VueLuckyCanvas from '@lucky-canvas/vue'

// iconfont
import './assets/iconfont/iconfont.css'

const app = createApp(App)
app.use(fxHeader)
pinia.use(piniaPluginPersistedstate);

app.use(i18n)
app.use(router)
app.use(pinia)
app.use(VueLuckyCanvas)

// 主题色
import { needChangeMode } from '@/config'
const modeType = import.meta.env.MODE

const themeName = needChangeMode.includes(modeType) ? modeType : 'main'
import(`./assets/theme/${themeName}.scss`).then(() => {
    app.mount('#app')
})


import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'


dayjs.extend(utc)
dayjs.extend(timezone)


// 2023-01-01 00:00:00 假设是北京时间
const offset = dayjs().utcOffset() / 60;
console.log('当前时区UTC偏移量',offset);
let hour
if (offset <= 8) {
    hour = 8 - offset
    console.log('转换后的时间',dayjs('2023-01-01 00:00:00').add(hour,'hour').format('YYYY-MM-DD HH:mm:ss'));
}  else {
    hour = 8 - offset;
    console.log('转换后的时间',dayjs('2023-01-01 00:00:00').add(hour,'hour').format('YYYY-MM-DD HH:mm:ss'));
}
