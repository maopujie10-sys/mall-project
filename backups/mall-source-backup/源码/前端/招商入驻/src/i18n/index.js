// 引入必要的库
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import { Locale } from 'vant'
import enUS from 'vant/lib/locale/lang/en-US'
import zhCN from 'vant/lib/locale/lang/zh-CN'
import zhTW from 'vant/lib/locale/lang/zh-TW'
import de from 'vant/lib/locale/lang/de-DE'
import af from 'vant/lib/locale/lang/en-US'
import el from 'vant/lib/locale/lang/en-US'
import es from 'vant/lib/locale/lang/es-ES'
import fr from 'vant/lib/locale/lang/fr-FR'
import it from 'vant/lib/locale/lang/en-US'
import ja from 'vant/lib/locale/lang/ja-JP'
import ko from 'vant/lib/locale/lang/en-US'
import ms from 'vant/lib/locale/lang/en-US'
import pt from 'vant/lib/locale/lang/en-US'
import ru from 'vant/lib/locale/lang/en-US'
import th from 'vant/lib/locale/lang/th-TH'
import tr from 'vant/lib/locale/lang/tr-TR'
import ph from 'vant/lib/locale/lang/en-US'
import ar from 'vant/lib/locale/lang/en-US'
import vi from 'vant/lib/locale/lang/vi-VN'
import id from 'vant/lib/locale/lang/en-US'
import hi from 'vant/lib/locale/lang/en-US'
import locale from "element-ui/lib/locale";
import langEn from 'element-ui/lib/locale/lang/en';
import langZh from 'element-ui/lib/locale/lang/zh-CN'
import langTw from 'element-ui/lib/locale/lang/zh-TW';
import langJa from 'element-ui/lib/locale/lang/ja'
import langde from 'element-ui/lib/locale/lang/de'
import langms from 'element-ui/lib/locale/lang/en'
import langth from 'element-ui/lib/locale/lang/th'
import langel from 'element-ui/lib/locale/lang/el'
import langpt from 'element-ui/lib/locale/lang/pt'
import langes from 'element-ui/lib/locale/lang/es'
import langfr from 'element-ui/lib/locale/lang/fr'
import langru from 'element-ui/lib/locale/lang/ru-RU'
import langit from 'element-ui/lib/locale/lang/it'
import langtr from 'element-ui/lib/locale/lang/tr-TR'
import langko from 'element-ui/lib/locale/lang/ko'
import langVi from 'element-ui/lib/locale/lang/vi'
import langHi from 'element-ui/lib/locale/lang/en'
import langid from 'element-ui/lib/locale/lang/id'
// import langph from 'element-ui/lib/locale/lang/en'
import langar from 'element-ui/lib/locale/lang/ar'
// 引入工具函数
import { getStorage, getBrowserLang } from '@/utils/utis'

// 引入项目中需要用到的中英文文案配置js
import enLocale from './en-US'
import cnLocale from './CN'
import zhCnLocale from './zh-CN'
import deLocale from './de'
import afLocale from './af'
import elLocale from './el'
import esLocale from './es'
import frLocale from './fr'
import itLocale from './it'
import jaLocale from './ja'
import koLocale from './ko'
import msLocale from './ms'
import ptLocale from './pt'
import ruLocale from './ru'
import thLocale from './th'
import trLocale from './tr'
import phLocale from './ph'
import arLocale from './ar'
import viLocale from './vi'
import idLocale from './id'
import hiLocale from './hi'
// 使用vue-i18n库
Vue.use(VueI18n)

// 获取当前语言（初始化时localStorage里没有存语言，默认为浏览器当前的语言）
const lang = getStorage('merchant-landing-page-lang') || getBrowserLang()

// 组合element ui 和 项目自身的文案文件
const messages = {
    'en-US': {
        ...enUS,
        ...enLocale
    },
    'zh-CN': {
        ...zhCN,
        ...zhCnLocale
    },
    'CN': {
        ...zhTW,
        ...cnLocale
    },
    'de': {
        ...de,
        ...deLocale
    },
    'af': {
        ...af,
        ...afLocale
    },
    'el': {
        ...el,
        ...elLocale
    },
    'es': {
        ...es,
        ...esLocale
    },
    'fr': {
        ...fr,
        ...frLocale
    },
    'it': {
        ...it,
        ...itLocale
    },
    'ja': {
        ...ja,
        ...jaLocale
    },
    'ko': {
        ...ko,
        ...koLocale
    },
    'ms': {
        ...ms,
        ...msLocale
    },
    'pt': {
        ...pt,
        ...ptLocale
    },
    'ru': {
        ...ru,
        ...ruLocale
    },
    'th': {
        ...th,
        ...thLocale
    },
    'tr': {
        ...tr,
        ...trLocale
    },
    'ph': {
        ...ph,
        ...phLocale
    },
    'ar': {
        ...ar,
        ...arLocale
    },
    'vi': {
        ...vi,
        ...viLocale
    },
    'id': {
        ...id,
        ...idLocale
    },
    'hi': {
        ...hi,
        ...hiLocale
    },
}
// 创建vueI18n实例并输出，在main.js中调用
export const i18n = new VueI18n({
    locale: lang,
    messages,
    silentTranslationWarn: true,
})
export const elementLocales = (lang) => {
    // Vue.config.lang = 'en'
    if (lang === 'zh-CN') {
      locale.use(langZh);
    } else if (lang === 'zh') {
      locale.use(langTw);
    } else if (lang === "ja") {
      locale.use(langJa);
    }else if (lang === "de") {
      locale.use(langde);}
      else if (lang === "ms") {
     locale.use(langms);}
      else if (lang === "th") {
      locale.use(langth);}
    else if (lang === "el") {
      locale.use(langel);
    }else if (lang === "pt") {
        locale.use(langpt); }
      else if (lang === "es") {
        locale.use(langes);

      }
      else if (lang === "fr") {
        locale.use(langfr);

      }else if (lang === "ru") {
        locale.use(langru);

      }else if (lang === "it") {
        locale.use(langit);

      }else if (lang === "tr") {
        locale.use(langtr);

      }else if (lang === "ko") {
        locale.use(langko);
    }else if(lang === "ph"){
        locale.use(langEn);
      } else if(lang === "ar"){
        locale.use(langar);
      }else if(lang === "vi"){
        locale.use(langVi);
      }else if(lang === "id"){
        locale.use(langid);
      }else if(lang === "hi"){
        locale.use(langHi);
      }
      else{
      locale.use(langEn);
    }
  };
// 更新vant组件库本身的语言变化，支持国际化
export function vantLocales(lang) {
    if (lang === 'en-US') {
        Locale.use(lang, enUS)
    } else if (lang === 'zh-CN') {
        Locale.use(lang, zhCN)
    } else if (lang === 'CN') {
        Locale.use(lang, zhTW)
    } else if (lang === 'de') {
        Locale.use(lang, de)
    } else if (lang === 'af') {
        Locale.use(lang, af)
    } else if (lang === 'el') {
        Locale.use(lang, el)
    } else if (lang === 'es') {
        Locale.use(lang, es)
    } else if (lang === 'fr') {
        Locale.use(lang, fr)
    } else if (lang === 'it') {
        Locale.use(lang, it)
    } else if (lang === 'ja') {
        Locale.use(lang, ja)
    } else if (lang === 'ko') {
        Locale.use(lang, ko)
    } else if (lang === 'ms') {
        Locale.use(lang, ms)
    } else if (lang === 'pt') {
        Locale.use(lang, pt)
    } else if (lang === 'ru') {
        Locale.use(lang, ru)
    } else if (lang === 'th') {
        Locale.use(lang, th)
    } else if (lang === 'tr') {
        Locale.use(lang, tr)
    } else if (lang === 'ph') {
        Locale.use(lang, ph)
    } else if (lang === 'ar') {
        Locale.use(lang, ar)
    } else if (lang === 'vi') {
        Locale.use(lang, vi)
    } else if (lang === 'hi') {
        Locale.use(lang, hi)
    } else if (lang === 'id') {
        Locale.use(lang, id)
    } else {
        Locale.use(lang, enUS)
    }
}
export default { i18n, vantLocales,elementLocales }
