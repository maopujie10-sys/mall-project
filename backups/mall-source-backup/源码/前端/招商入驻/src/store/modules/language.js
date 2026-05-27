import {
    getStorage,
    setStorage,
}
    from '@/utils/utis'

export default {
    state: {
        language: getStorage('merchant-landing-page-lang') || "en-US" // 项目初始化时，默认为浏览器的语言
    },
    getters: {
        language: state => state.language
    },
    mutations: {
        setLanguage: (state, language) => {
            console.log('languageVux->', language)
            // const lang = JSON.parse(language)
            state.language = language
            setStorage('merchant-landing-page-lang', language)
        },
    }
}
