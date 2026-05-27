import {
  WithdrawRecordApi,
  WithdrawGetToken,
  WithdrawApplyApi,
  WithdrawDetailsApi,
  GetRechargeAddressApi,
  WithdrawGetFee,
} from "@/api";
const defaultPageInfo = { pageNum: 1, pageSize: 20 };
export const withdrawMoule = {
  namespaced: true,
  state: () => ({
    httpLoading: false,
    btnLoading: false,
    // session token
    sessionToken: "",
    // 提现手续费
    withdrawFee: '',
    // 提现记录
    withdrawRecordList: [],
    withdrawRecordPageInfo: { ...defaultPageInfo },
    // 提现记录详情
    withdrawRecordDetails: {},
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
    updateWithdrawRcordList(state, data) {
      state.withdrawRecordList = data;
    },
    updateWithdrawRcordDetails(state, data) {
      state.withdrawRecordDetails = { ...data };
    },
    updateWithdrawFee(state, data) {
      state.withdrawFee = data
    }
  },
  actions: {
    async requestSessionToken({ commit }, params = {}) {
      try {
        commit("updateHttpLoading", true);
        const result = await GetRechargeAddressApi(params);
        commit("updateSessionToken", result.data);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      } finally {
        commit("updateHttpLoading", false);
      }
    },
    async requestwithdrawRecordList({ commit }, params = {}) {
      try {
        commit("updateHttpLoading", true);
        const result = await WithdrawRecordApi(params);
        commit("updateWithdrawRcordList", result.data);
        return Promise.resolve(result.data);
      } catch (error) {
        console.error(error);
        return Promise.reject(error);
      } finally {
        commit("updateHttpLoading", false);
      }
    },
    async requestWithdrawFee({ dispatch, commit }, params = {}) {
      try {
        const { data } = await WithdrawGetFee(params);
        commit("updateWithdrawFee", data.withdraw_fee);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      } 
    },
    async requesWithdraw({ dispatch, commit }, params = {}) {
      try {
        commit("updateBtnLoading", true);
        const { data } = await WithdrawGetToken()
        params.session_token = data.session_token
        await WithdrawApplyApi(params);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      } finally {
        commit("updateBtnLoading", false);
      }
    },
    async requestwithdrawRecordDetails({ dispatch }, params = {}) {
      try {
        commit("updateHttpLoading", true);
        const result = await WithdrawDetailsApi(params);
        commit("updateWithdrawRcordDetails", result.data);
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
    withdrawFee: (state) => state.withdrawFee,
    withdrawRecordList: (state) => state.withdrawRecordList,
    withdrawRecordPageInfo: (state) => state.withdrawRecordPageInfo,
    withdrawRecordDetails: (state) => state.withdrawRecordDetails,
  },
};
