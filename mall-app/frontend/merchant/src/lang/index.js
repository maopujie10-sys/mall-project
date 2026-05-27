import Vue from 'vue'
import VueI18n from 'vue-i18n'
import Cookies from 'js-cookie'
import {getStorage} from '@/utils/utis'
import elementEnLocale from 'element-ui/lib/locale/lang/en' // element-ui lang
import elementTWLocale from 'element-ui/lib/locale/lang/zh-TW' // element-ui lang
import elementCNLocale from 'element-ui/lib/locale/lang/zh-CN' // element-ui lang
import elementDELocale from 'element-ui/lib/locale/lang/de' // element-ui lang
import elementFRLocale from 'element-ui/lib/locale/lang/fr' // element-ui lang
import elementJALocale from 'element-ui/lib/locale/lang/ja' // element-ui lang
import elementKoLocale from 'element-ui/lib/locale/lang/ko' // element-ui lang
import elementTHLocale from 'element-ui/lib/locale/lang/th' // element-ui lang
import elementPTLocale from 'element-ui/lib/locale/lang/pt' // element-ui lang
import elementESLocale from 'element-ui/lib/locale/lang/es' // element-ui lang
import elementRULocale from 'element-ui/lib/locale/lang/ru-RU' // element-ui lang
import elementELLocale from 'element-ui/lib/locale/lang/el' // element-ui lang
import elementITLocale from 'element-ui/lib/locale/lang/it' // element-ui lang
import elementTRLocale from 'element-ui/lib/locale/lang/tr-TR' // element-ui lang
import elementAFLocale from 'element-ui/lib/locale/lang/af-ZA' // element-ui lang
import elementARLocale from 'element-ui/lib/locale/lang/ar' // element-ui lang
import elementVILocale from 'element-ui/lib/locale/lang/vi' // element-ui lang
import elementIDLocale from 'element-ui/lib/locale/lang/id' // element-ui lang
import elementPHLocale from '@/lang/config/ph' // element-ui lang
import elementMSLocale from '@/lang/config/ms' // element-ui lang
import elementHILocale from '@/lang/config/hi' // element-ui lang
import enLocale from './en'
import cnLocale from './zh-CN'
import twLocale from './zh-TW'
import deLocale from './de'
import frLocale from './fr'
import jaLocale from './ja'
import koLocale from './ko'
import msLocale from './ms'
import thLocale from './th'
import ptLocale from './pt'
import esLocale from './es'
import ruLocale from './ru'
import elLocale from './el'
import itLocale from './it'
import trLocale from './tr-TR'
import afLocale from './af-ZA'
import phLocale from './ph'
import arLocale from './ar'
import viLocale from './vi'
import idLocale from './id'
import hiLocale from './hi'

Vue.use(VueI18n)
// 获取当前语言（初始化时localStorage里没有存语言，默认为浏览器当前的语言）

const lang = getStorage('merchant_pc_lang') || 'en'// getBrowserLang()

const messages = {
    en: {
        ...enLocale,
        ...elementEnLocale
    },
    cn: {
        ...cnLocale,
        ...elementCNLocale
    },
    tw: {
        ...twLocale,
        ...elementTWLocale
    },
    de: {
        ...deLocale,
        ...elementDELocale
    },
    fr: {
        ...frLocale,
        ...elementFRLocale
    },
    ja: {
        ...jaLocale,
        ...elementJALocale
    },
    ko: {
        ...koLocale,
        ...elementKoLocale
    },
    ms: {
        ...msLocale,
        ...elementMSLocale
    },
    th: {
        ...thLocale,
        ...elementTHLocale
    },
    pt: {
        ...ptLocale,
        ...elementPTLocale
    },
    es: {
        ...esLocale,
        ...elementESLocale
    },
    ru: {
        ...ruLocale,
        ...elementRULocale
    },
    el: {
        ...elLocale,
        ...elementELLocale
    },
    it: {
        ...itLocale,
        ...elementITLocale
    },
    tr: {
        ...trLocale,
        ...elementTRLocale
    },
    af: {
        ...afLocale,
        ...elementAFLocale
    },
    ph: {
        ...phLocale,
        ...elementPHLocale
    },
    ar: {
        ...arLocale,
        ...elementARLocale
    },
    vi: {
        ...viLocale,
        ...elementVILocale
    },
    id: {
        ...idLocale,
        ...elementIDLocale
    },
    hi: {
        ...hiLocale,
        ...elementHILocale
    }
}

export function getLanguage() {
    const chooseLanguage = Cookies.get('language')
    if (chooseLanguage) return chooseLanguage

    // if has not choose language
    const language = (navigator.language || navigator.browserLanguage).toLowerCase()
    const locales = Object.keys(messages)
    for (const locale of locales) {
        if (language.indexOf(locale) > -1) {
            return locale
        }
    }
    return 'en'
}

// 创建vueI18n实例并输出，在main.js中调用
export const i18n = new VueI18n({
    locale: lang, messages
})

export default {i18n}
