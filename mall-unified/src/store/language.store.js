import { defineStore } from 'pinia'
import { useStorage } from '@vueuse/core'
import { SET_LANGUAGE } from '@/store/types.store'
import { getBrowserLang } from '@/utils/index'

export const useLanguageStore = defineStore('language', {
    // state 持久化
    state: () => useStorage('language', {
        language: localStorage.getItem('lang') || getBrowserLang() // 项目初始化时，默认为浏览器的语言,
    }),
    actions: {
        [SET_LANGUAGE](locale) {
            this.language = locale
            localStorage.setItem('lang', locale)
        }

    },
})
