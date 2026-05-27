import variables from '@/styles/element-variables.scss'
import defaultSettings from '@/settings'
import {settingSafeword} from "@/api/user";

const {showSettings, tagsView, fixedHeader, sidebarLogo, projectTitle} = defaultSettings

const state = {
    theme: ['Int Overstock'].includes(projectTitle) ? variables.blackTheme : variables.theme,
    showSettings: showSettings,
    tagsView: tagsView,
    fixedHeader: fixedHeader,
    sidebarLogo: sidebarLogo
}

const mutations = {
    CHANGE_SETTING: (state, {key, value}) => {
        // eslint-disable-next-line no-prototype-builtins
        if (state.hasOwnProperty(key)) {
            state[key] = value
        }
    }
}

const actions = {
    changeSetting({commit}, data) {
        commit('CHANGE_SETTING', data)
    },
    async settingSafeword({commit}, params = {}) {
        try {
            await settingSafeword(params);
            return Promise.resolve();
        } catch (error) {
            console.error(error);
            return Promise.reject();
        }
    },
}

export default {
    namespaced: true,
    state,
    mutations,
    actions
}

