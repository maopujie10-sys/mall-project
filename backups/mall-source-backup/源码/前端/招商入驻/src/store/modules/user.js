import {gerenxinxi_post, huoquyue_post} from "@/API/user";

export default {
  state: {
    userInfo: null,
    userMoney: null
  },
  getters: {
    userInfo: (state) => {
      return state.userInfo
    },
    userMoney: (state) => {
      return state.userMoney
    }
  },
  mutations: {
    SET_USERINFO: (state, info) => {
      state.userInfo = info
    },
    SET_USERMONEY: (state, money) => {
      state.userMoney = money
    }
  },
  actions: {
    getUserInfo({ commit }) {
      const TOKEN = localStorage.getItem('token')
      return new Promise((resovle, reject) => {
        if (TOKEN) {
          gerenxinxi_post({}).then(res => {
            commit('SET_USERINFO', res)
            resovle(res)
          }).catch(() => {
            commit('SET_USERINFO', null)
            localStorage.removeItem('token')
            reject('fetch error')
          })
        } else {
          commit('SET_USERINFO', null)
          resovle('clear userinfo')
        }
      })
    },
    getUserMoney({ commit }) {
      const TOKEN = localStorage.getItem('token')
      return new Promise((resovle, reject) => {
        if (TOKEN) {
          huoquyue_post().then(res => {
            commit('SET_USERMONEY', res)
            resovle(res)
          }).catch(() => {
            commit('SET_USERMONEY', null)
            reject('fetch error')
          })
        } else {
          commit('SET_USERMONEY', null)
          resovle('clear userMoney')
        }
      })
    },
    logout({ commit }) {
      commit('SET_USERINFO', null)
      localStorage.removeItem('token')
      localStorage.removeItem('productList')
      localStorage.removeItem('cartList')
    }
  }
}
