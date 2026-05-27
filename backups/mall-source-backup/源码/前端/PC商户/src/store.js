import Vue from "vue";
import Vuex from "vuex"; //引入 vuex
import createPersistedState from "vuex-persistedstate";
import { ES_TOKEN, ES_LANG, ES_LANGUAGE_MAP } from "@/common/constant";
import { UserInfoApi } from "@/api";
import { homeMoule } from "@/store/home.module";
import { userMoule } from "@/store/user.module";
import { rechargeMoule } from "@/store/recharge.module";
import { withdrawMoule } from "@/store/withdraw.module";
import { productDetailsMoule } from "@/store/productDetails.module";
import { shopCartMoule } from "@/store/shopCart.module";
import { orderMoule } from "@/store/order.module";
import { showI18nMessage } from '@/common'

Vue.use(Vuex); //使用 vuex

const getDefaultLang = () => localStorage.getItem(ES_LANG) || ES_LANGUAGE_MAP.en
const defaultLang = getDefaultLang()

export default new Vuex.Store({
  modules: {
    home: homeMoule,
    user: userMoule,
    recharge: rechargeMoule,
    withdraw: withdrawMoule,
    productDetails: productDetailsMoule,
    shopCart: shopCartMoule,
    order: orderMoule,
  },
  state: {
    token: localStorage.getItem(ES_TOKEN) ?? '',
    lang: defaultLang,
    userInfo: {},
    historyData: []
  },
  plugins: [
    createPersistedState({
      paths: ["userInfo", "shopCart"],
      storage: window.localStorage
    }),
  ],
  mutations: {
    SETLANG(state, lang) {
      state.lang = lang;
      localStorage.setItem(ES_LANG, lang);
    },
    SETTOKEN(state, val) {
      state.token = val;
      localStorage.setItem(ES_TOKEN, val);
    },
    SETUSERINFO(state, userInfo) {
      state.userInfo = { ...userInfo };
    },
    SET_HISTORYDATA(state, data) {
      state.historyData = data
    }
  },
  actions: {
    asyncToken(context, val) {
      context.commit("SETTOKEN", val);
    },
    async getUserInfo({ commit }) {
      try {
        const userInfo = await UserInfoApi();
        commit("SETUSERINFO", userInfo.data);
        return Promise.resolve();
      } catch (error) {
        console.log('error ->', error);
        return Promise.reject();
      }
    },
    async logout({ commit }) {
      commit("SETUSERINFO", {});
      commit("shopCart/clear", []);
      commit('SETTOKEN', '');
      localStorage.removeItem(ES_TOKEN);
      showI18nMessage('message.home.operationSuccess')
      return Promise.resolve();
    },
  },
  getters: {
    existToken: (state) => {
      const token = localStorage.getItem(ES_TOKEN);
      if (token) {
        return true;
      } else {
        return false;
      }
    },
    userInfo: (state) => state.userInfo,
    isLogin: (state) => !!state.token,
    currentLang: (state) => state.lang,
    historyData: (state) => state.historyData
  },
});
