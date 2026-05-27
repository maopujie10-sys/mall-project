import {getCategory} from "@/api/goods";

const state = {
    category: [],
    test: 'test22'
}

const mutations = {
    SET_CATEGORY: (state, category) => {
        state.category = category
    }
}

const actions = {
    //获取分类列表
    getCategory({commit}) {
        return new Promise((resolve, reject) => {
            getCategory().then(response => {
                const data = response.data
                commit('SET_CATEGORY', data)
                resolve()
            }).catch(error => {
                reject(error)
            })
        })
    },
    async getCategoryName({commit, state}, id) {
        if (state.category.length === 0) {
            await this.getCategory()
        }
        return state.category.find(item => item.id === id).name
    }
}

export default {
    namespaced: true,
    state,
    mutations,
    actions
}
