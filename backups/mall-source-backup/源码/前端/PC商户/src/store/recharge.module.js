import {
  GetRechargeSessionApi,
  RechargeApi,
  RechargeRecordApi,
  RechargeRecordDetailsApi,
  GetRechargeAddressApi,
} from "@/api";
const defaultPageInfo = { pageNum: 1, pageSize: 20 };
export const rechargeMoule = {
  namespaced: true,
  state: () => ({
    httpLoading: false,
    btnLoading: false,
    // session token
    sessionToken: "",
    // 充值记录
    rechargeRecordList: {
      pageSize: 10,
      thisPageNumber: 1,
      totalElements: 1,
    },
    rechargeRecordPageInfo: { ...defaultPageInfo },
    // 充值记录详情
    rechargeRecordDetails: {},
    // 充值地址
    rechargeAddress: [],
  }),
  mutations: {
    updateHttpLoading(state, data) {
      state.httpLoading = data;
    },
    updateBtnLoading(state, data) {
      state.btnLoading = data;
    },
    updateSessionToken(state, data) {
      state.sessionToken = data.session_token;
    },
    updateRechargeRcordList(state, data) {
      state.rechargeRecordList = data;
    },
    updateRechargeRcordDetails(state, data) {
      state.rechargeRecordDetails = { ...data };
    },
    updateRechargeAddress(state, data) {
      state.rechargeAddress = [...data];
    },
  },
  actions: {
    async requestSessionToken({ commit }, params = {}) {
      try {
        commit("updateHttpLoading", true);
        const result = await GetRechargeSessionApi(params);
        commit("updateSessionToken", result.data);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      } finally {
        commit("updateHttpLoading", false);
      }
    },
    async requestRechargeRecordList({ commit }, params = {}) {
      try {
        commit("updateHttpLoading", true);
        const result = await RechargeRecordApi({ ...params, pageSize: 8 });
        commit("updateRechargeRcordList", result.data);
        return Promise.resolve(result.data);
      } catch (error) {
        console.error(error);
        return Promise.reject(error);
      } finally {
        commit("updateHttpLoading", false);
      }
    },
    async requesRecharge({ dispatch, commit }, params = {}) {
      try {
        commit("updateBtnLoading", true);
        await RechargeApi(params);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      } finally {
        commit("updateBtnLoading", false);
      }
    },
    async requestRechargeRecordDetails({ dispatch, commit }, params = {}) {
      try {
        commit("updateHttpLoading", true);
        const result = await RechargeRecordDetailsApi(params);
        commit("updateRechargeRcordDetails", result.data);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      } finally {
        commit("updateHttpLoading", false);
      }
    },
    async requestRechargeAddress({ dispatch, commit }, params = {}) {
      try {
        commit("updateHttpLoading", true);
        const result = await GetRechargeAddressApi(params);
        commit("updateRechargeAddress", result.data);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      } finally {
        commit("updateHttpLoading", false);
      }
    },
  },
  getters: {
    httpLoading: (state) => state.httpLoading,
    btnLoading: (state) => state.btnLoading,
    sessionToken: (state) => state.sessionToken,
    rechargeRecordList: (state) => state.rechargeRecordList,
    rechargeRecordPageInfo: (state) => state.rechargeRecordPageInfo,
    rechargeRecordDetails: (state) => state.rechargeRecordDetails,
    rechargeAddress: (state) => state.rechargeAddress,
  },
};
