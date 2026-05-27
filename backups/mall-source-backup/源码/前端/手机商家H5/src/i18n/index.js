import { createI18n } from 'vue-i18n'
import enLocale from './en'
import cnLocale from './cn'
import twLocale from './tw'
import spLocale from './es'
import ptLocale from './pt'
import afLocale from './af'
import elLocale from './el'
import itLocale from './it'
import ruLocale from './ru'
import trLocale from './tr'
import deLocale from './de'
import frLocale from './fr'
import jaLocale from './ja'
import koLocale from './ko'
import msLocale from './ms'
import thLocale from './th'
import phLocale from './ph'
import arLocale from './ar'
import viLocale from './vi'
import hiLocale from './hi'
import idLocale from './id'

const messages = {
  'en': {
    ...enLocale
  },
  'cn': {
    ...cnLocale
  },
  'tw': {
    ...twLocale
  },
  'es': {
    ...spLocale
  },
  'pt': {
    ...ptLocale
  },
  'af': {
    ...afLocale
  },
  'el': {
    ...elLocale
  },
  'it': {
    ...itLocale
  },
  'ru': {
    ...ruLocale
  },
  'tr': {
    ...trLocale
  },
  'de': {
    ...deLocale
  },
  'fr': {
    ...frLocale
  },
  'ja': {
    ...jaLocale
  },
  'ko': {
    ...koLocale
  },
  'ms': {
    ...msLocale
  },
  'th': {
    ...thLocale
  },
  'ph': {
    ...phLocale
  },
  'ar': {
    ...arLocale
  },
  'vi': {
    ...viLocale
  },
  'hi': {
    ...hiLocale
  },
  'id': {
    ...idLocale
  }
}

const storeLang = localStorage.getItem('lang')
let lang = 'en'
if (Object.keys(messages).includes(storeLang)) {
  lang = storeLang
  if (lang === 'ar') {
    document.documentElement.setAttribute('dir', 'rtl')
  }
} else {
  localStorage.setItem('lang', lang)
  document.documentElement.setAttribute('dir', 'rtr')
}

const i18n = createI18n({
  legacy: false,
  locale: lang, // 首先从缓存里拿，没有的话就用浏览器语言，
  fallbackLocale: 'en', // 设置备用语言
  messages,
  warnHtmlMessage: false
})

export default i18n