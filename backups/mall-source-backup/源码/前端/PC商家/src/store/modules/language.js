import {getStorage, setStorage} from '@/utils/utis'

export default {
    namespaced: true,
    state: {
        lang: 'en',
        currentLanguage: getStorage('merchant_pc_lang') || 'en',// 项目初始化时，默认为浏览器的语言,
        languages: [
            {name: 'English', value: 'en', code: 'en', show: true},// 英语
            {name: 'Deutsch', value: 'de', code: 'de', show: true},// 德语
            {name: 'Français', value: 'fr', code: 'fr', show: true},  // 法语
            {name: 'Русский', value: 'ru', code: 'ru', show: true}, // 俄语
            {name: 'Español', value: 'es', code: 'es', show: true}, // 西班牙语
            {name: 'Português', value: 'pt', code: 'pt', show: true}, // 葡萄牙语
            {name: 'Italiano', value: 'it', code: 'it', show: true},  // 意大利语
            {name: 'Melayu', value: 'ms', code: 'ms', show: true},  // 马来语
            {name: 'Afrikaans', value: 'af-ZA', code: 'af', show: true},  // 南非荷兰语
            {name: 'Ελληνικά', value: 'el', code: 'el', show: true},  // 希腊语
            {name: '繁體中文', value: 'zh-TW', code: 'tw', show: true},// 繁体中文
            {name: '简体中文', value: 'zh-CN', code: 'cn', show: true},// 简体中文
            {name: 'Türkçe', value: 'tr-TR', code: 'tr', show: true}, // 土耳其语
            {name: '日本語', value: 'ja', code: 'ja', show: true}, // 日语
            {name: '한국어', value: 'ko', code: 'ko', show: true}, // 韩语
            {name: 'ภาษาไทย', value: 'th', code: 'th', show: true}, // 泰语
            {name: 'Filipino', value: 'ph', code: 'ph', show: true}, // 菲律宾语
            {name: 'العربية', value: 'ar', code: 'ar', show: true}, // 阿拉伯语
            {name: 'Tiếng Việt', value: 'vi', code: 'vi', show: true}, // 越南语
            {name: 'हिंदी', value: 'hi', code: 'hi', show: true}, // 印地语
            {name: 'Indonesia', value: 'id', code: 'id', show: true}, // 印尼语
        ]
    },
    mutations: {
        setCurrentLanguage(state, language) {
            state.currentLanguage = language
            setStorage('merchant_pc_lang', language)
            let lang = state.languages.find(item => item.value === language).code
            state.lang = lang
        },
    }
}
