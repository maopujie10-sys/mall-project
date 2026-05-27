import {
    getStorage,
    setStorage,
    getBrowserLang
}
    from '@/utils/utis'

export default {
    state: {
        language: getStorage('lang') || getBrowserLang() // 项目初始化时，默认为浏览器的语言
    },
    getters: {
        language: state => state.language
    },
    mutations: {
        setLanguage: (state, language) => {
            state.language = language
            localStorage.setItem('lang', language)
        },
    }
}
