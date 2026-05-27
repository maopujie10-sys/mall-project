// 引入必要的库
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import { Locale } from 'vant'
import enUS from 'vant/lib/locale/lang/en-US'
import zhCN from 'vant/lib/locale/lang/zh-CN'
import zhTW from 'vant/lib/locale/lang/zh-TW'
/**
 * 中文简体(cn)   中文繁体(tw)   英语(en)   德语(de)   法语(fr)   日语(ja)   韩语(ko)   马来西亚语(ms)   
 * 泰国语(th)   葡萄牙语(pt)   西班牙语(es)   俄语(ru)   希腊语(el)   意大利语(it)   土耳其语(tr)   
 * 南非荷兰语(af) 菲律宾(ph)   越南语(vi)   印度语(hi)   印度尼西亚语(id)
 */
// 引入工具函数
import { getStorage, setStorage, getBrowserLang } from '@/utils/utis'
// 引入项目中需要用到的中英文文案配置js
import enLocale from './en'
import twLocale from './tw'
import cnLocale from './cn'
import jaLocale from './ja'
import koLocale from './ko'
import deLocale from './de'
import frLocale from './fr'
import msLocale from './ms'
import thLocale from './th'
import ptLocale from './pt'
import esLocale from './es'
import ruLocale from './ru'
import elLocale from './el'
import itLocale from './it'
import trLocale from './tr'
import afLocale from './af'
import phLocale from './ph'
import arLocale from './ar'
import viLocale from './vi'
import hiLocale from './hi'
import idLocale from './id'
// 使用vue-i18n库
Vue.use(VueI18n)
getStorage('lang') == null && localStorage.setItem('lang', 'en')
// 获取当前语言（初始化时localStorage里没有存语言，默认为en）
let lang = localStorage.getItem('lang') || 'en'
if (lang == 'en-US' || lang == '"en-US"') {
    lang = 'en'
} else if (lang == 'zh-CN' || lang == "'zh-CN'") {
    lang = 'cn'
} else if (lang == 'zh-TW' || lang == "'zh-TW'") {
    lang = 'tw'
}
localStorage.setItem('lang', lang)
// process.env.VUE_APP_PUT_ON_SHELVES && (lang = 'en')
// 组合element ui 和 项目自身的文案文件
const messages = {
    'en': {
        ...enUS,
        ...enLocale
    },
    'cn': {
        ...zhCN,
        ...cnLocale
    },
    'tw': {
        ...zhTW,
        ...twLocale
    },
    'ja': {
        ...enUS,
        ...jaLocale
    },
    'ko': {
        ...enUS,
        ...koLocale
    },
    'de': {
        ...enUS,
        ...deLocale
    },
    'fr': {
        ...enUS,
        ...frLocale
    },
    'ms': {
        ...enUS,
        ...msLocale
    },
    'th': {
        ...enUS,
        ...thLocale
    },
    'pt': {
        ...enUS,
        ...ptLocale
    },
    'es': {
        ...enUS,
        ...esLocale
    },
    'ru': {
        ...enUS,
        ...ruLocale
    },
    'el': {
        ...enUS,
        ...elLocale
    },
    'it': {
        ...enUS,
        ...itLocale
    },
    'tr': {
        ...enUS,
        ...trLocale
    },
    'af': {
        ...enUS,
        ...afLocale
    },
    'ph': {
        ...enUS,
        ...phLocale
    },
    'ar': {
        ...enUS,
        ...arLocale
    },
    'vi': {
        ...enUS,
        ...viLocale
    },
    'hi': {
        ...enUS,
        ...hiLocale
    },
    'id': {
        ...enUS,
        ...idLocale
    },
}
// 创建vueI18n实例并输出，在main.js中调用
export const i18n = new VueI18n({
    locale: lang || 'en',
    messages
})
// 更新vant组件库本身的语言变化，支持国际化
export function vantLocales(lang) {
    if (lang === 'en') {
        Locale.use(lang, enUS)
    } else if (lang === 'cn') {
        Locale.use(lang, zhCN)
    } else if (lang === 'tw') {
        Locale.use(lang, zhTW)
    } else {
        Locale.use(lang, enUS)
    }
}

export default { i18n, vantLocales }
