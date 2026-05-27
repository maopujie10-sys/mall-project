// i18n.js
import Vue from "vue";
import VueI18n from "vue-i18n";
import messages from "./langs";
import store from '../store.js';
import { ES_LANG, ES_LANGUAGE_MAP } from "@/common/constant";
import locale from "element-ui/lib/locale";
import langEn from 'element-ui/lib/locale/lang/en';
import langZh from 'element-ui/lib/locale/lang/zh-CN'
import langTw from 'element-ui/lib/locale/lang/zh-TW';
import langJa from 'element-ui/lib/locale/lang/ja'
import langde from 'element-ui/lib/locale/lang/de'
import langms from 'element-ui/lib/locale/lang/ms'
import langth from 'element-ui/lib/locale/lang/th'
import langel from 'element-ui/lib/locale/lang/el'
import langpt from 'element-ui/lib/locale/lang/pt'
import langes from 'element-ui/lib/locale/lang/es'
import langfr from 'element-ui/lib/locale/lang/fr'
import langru from 'element-ui/lib/locale/lang/ru-RU'
import langit from 'element-ui/lib/locale/lang/it'
import langtr from 'element-ui/lib/locale/lang/tr-TR'
import langko from 'element-ui/lib/locale/lang/ko'
import langPh from 'element-ui/lib/locale/lang/en'
import langAr from 'element-ui/lib/locale/lang/ar'
import langHi from 'element-ui/lib/locale/lang/en'
import langId from 'element-ui/lib/locale/lang/id'
import langVi from 'element-ui/lib/locale/lang/vi'

Vue.use(VueI18n);

const i18n = new VueI18n({
  locale: store.getters.currentLang,
  messages,
});

// locale.i18n((key, value) => i18n.t(key, value)); // 重点：为了实现element插件的多语言切换

// 更新element组件库本身的语言变化，支持国际化
export const elementLocales = (lang) => {
  // Vue.config.lang = 'en'
  if (lang === ES_LANGUAGE_MAP.zhCN) {
    locale.use(langZh);
  } else if (lang === ES_LANGUAGE_MAP.zhTW) {
    locale.use(langTw);
  } else if (lang === ES_LANGUAGE_MAP.ja) {
    locale.use(langJa);
  }else if (lang === ES_LANGUAGE_MAP.de) {
    locale.use(langde);}
    else if (lang === ES_LANGUAGE_MAP.ms) {
   locale.use(langms);}
    else if (lang === ES_LANGUAGE_MAP.th) {
    locale.use(langth);}
  else if (lang === ES_LANGUAGE_MAP.el) {
    locale.use(langel);
  }else if (lang === ES_LANGUAGE_MAP.pt) {
      locale.use(langpt); }
    else if (lang === ES_LANGUAGE_MAP.es) {
      locale.use(langes);
    
    }
    else if (lang === ES_LANGUAGE_MAP.fr) {
      locale.use(langfr);
    
    }else if (lang === ES_LANGUAGE_MAP.ru) {
      locale.use(langru);
    
    }else if (lang === ES_LANGUAGE_MAP.it) {
      locale.use(langit);
    
    }else if (lang === ES_LANGUAGE_MAP.tr) {
      locale.use(langtr);
    
    }else if (lang === ES_LANGUAGE_MAP.ko) {
      locale.use(langko);
    
    }else if (lang === ES_LANGUAGE_MAP.ph) {
      locale.use(langPh);
    }else if (lang === ES_LANGUAGE_MAP.ar) {
      locale.use(langAr);
    }else if (lang === ES_LANGUAGE_MAP.vi) {
      locale.use(langVi);
    }else if (lang === ES_LANGUAGE_MAP.hi) {
      locale.use(langHi);
    }else if (lang === ES_LANGUAGE_MAP.id) {
      locale.use(langId);
    }else{
    locale.use(langEn);
  }
};

export const setLocal = (locale, callback) => {
  // 更新app语言
  i18n.locale = locale;
  // 更新组件库
  // elementLocales(locale);
  // 存储当前语言
  localStorage.setItem(ES_LANG, locale);
  // 更新store
  store.commit('SETLANG', locale);
  elementLocales(store.getters.currentLang)
  // 回掉函数刷新页面
  callback && callback()

  return i18n;
};

elementLocales(store.getters.currentLang)

export default i18n;
