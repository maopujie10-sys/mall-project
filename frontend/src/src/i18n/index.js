import { createI18n } from "vue-i18n"
import zh from "./zh.js"
import en from "./en.js"

const messages = { zh, en }

const i18n = createI18n({
  locale: "zh",
  fallbackLocale: "en",
  messages,
})

export default i18n