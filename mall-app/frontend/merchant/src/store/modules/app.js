import Cookies from 'js-cookie'

const state = {
    isMobile: false,
    sidebar: {
        opened: Cookies.get('sidebarStatus') ? !!+Cookies.get('sidebarStatus') : true,
        withoutAnimation: false,
        setLoading: false,
        loadingSetTimeout: null,
    },
    device: 'desktop',
    showCustomer: false,
    size: Cookies.get('size') || 'medium'
}

const mutations = {
    //修改showCustomer
    SET_SHOW_CUSTOMER: (state, showCustomer) => {
        state.showCustomer = showCustomer
    },
    SET_IS_MOBILE: (state, isMobile) => {
        state.isMobile = isMobile
    },
    TOGGLE_SIDEBAR: state => {
        state.sidebar.opened = !state.sidebar.opened
        state.sidebar.withoutAnimation = false
        if (state.sidebar.opened) {
            Cookies.set('sidebarStatus', 1)
        } else {
            Cookies.set('sidebarStatus', 0)
        }
    },
    CLOSE_SIDEBAR: (state, withoutAnimation) => {
        Cookies.set('sidebarStatus', 0)
        state.sidebar.opened = false
        state.sidebar.withoutAnimation = withoutAnimation
    },
    TOGGLE_DEVICE: (state, device) => {
        state.device = device
    },
    SET_SIZE: (state, size) => {
        state.size = size
        Cookies.set('size', size)
    },
    SET_LOADING: (state, setLoading) => {
        if (setLoading) {
            state.sidebar.loadingSetTimeout && clearTimeout(state.sidebar.loadingSetTimeout)
            state.sidebar.setLoading = setLoading
        } else {
            state.sidebar.loadingSetTimeout = setTimeout(() => {
                state.sidebar.setLoading = setLoading
            }, 300)
        }
    },
    SET_LOADING_TIMEOUT: (state, loadingSetTimeout) => {
        state.sidebar.loadingSetTimeout = loadingSetTimeout
    },
    DELETE_LOADING_TIMEOUT: (state) => {
        state.sidebar.loadingSetTimeout && clearTimeout(state.sidebar.loadingSetTimeout)
    }
}

const actions = {
    toggleSideBar({commit}) {
        commit('TOGGLE_SIDEBAR')
    },
    closeSideBar({commit}, {withoutAnimation}) {
        commit('CLOSE_SIDEBAR', withoutAnimation)
    },
    toggleDevice({commit}, device) {
        commit('TOGGLE_DEVICE', device)
    },
    setSize({commit}, size) {
        commit('SET_SIZE', size)
    },
    setLoading({commit}, setLoading) {
        commit('SET_LOADING', setLoading)
    },
    setLoadingTimeout({commit}, loadingSetTimeout) {
        commit('SET_LOADING_TIMEOUT', loadingSetTimeout)
    },
    deleteLoadingTimeout({commit}) {
        commit('DELETE_LOADING_TIMEOUT')
    }
}

export default {
    namespaced: true,
    state,
    mutations,
    actions
}
