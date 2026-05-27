import {
  AddressListApi,
  AddressAddApi,
  AddressEditApi,
  AddressDelApi,
  UpdateLoginPasswordApi,
  GetUserBalanceApi,
  SetSafewordApi,
  UpdateSafewordApi,
  SearchResultListApi,
  KeepGoodsListApi,
  KeepGoodsAddApi,
  KeepGoodsCancelApi,
  FocusSellerListApi,
  FocusSellerAddApi,
  FocusSellerDelApi,
  OnlinechatApi,
  OnlinechatSendApi,
  OnlinechatUnreadApi
} from "@/api";
const defaultPageInfo = { pageNum: 1, pageSize: 20 };
export const userMoule = {
  namespaced: true,
  state: () => ({
    // 收货地址列表
    addressList: [],
    // 默认地址
    defaultAddress: {},
    // 支付时选择的地址
    currentIndex:0,
    paySelectAddress: {},
    // 用户余额
    userBalance: "0",
    // 搜索结果
    serachResultList: [],
    // 收藏商品列表
    collectGoodsList: [],
    // 收藏商家列表
    collectSellerList: [],
    // 消息列表
    messageList: [],
    // 未读的消息数
    unreadMessage: 0
  }),
  mutations: {
    updateAddressList(state, data) {
      state.addressList = [...data.pageList];
      state.defaultAddress = data.pageList.find((item) => item.use === 1);
    },
    updatePaySelectAddress(state, data) {
      state.paySelectAddress = { ...data };
    },
    updateUserBalance(state, data) {
      state.userBalance = data.money;
      localStorage.setItem("userBalance", data.money)
    },
    updateSerachResultList(state, data) {
      state.serachResultList = [...data.pageList];
    },
    updateCollectGoodsList(state, data) {
      state.collectGoodsList = [...data.pageList];
    },
    updateCollectSellerList(state, data) {
      state.collectSellerList = [...data.pageList];
    },
    updateMessageList(state, data) {
      state.messageList = [...data];
    },
    updateUnreadMessage(state, data) {
      state.unreadMessage= data
    },
  },
  actions: {
    async requestAddressList({ commit }, params = {}) {
      try {
        const result = await AddressListApi(params);
        commit("updateAddressList", result.data);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestAddressEdit({ dispatch }, params = {}) {
      try {
        await AddressEditApi(params);
        dispatch("requestAddressList");
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestAddressAdd({ dispatch }, params = {}) {
      try {
        await AddressAddApi(params);
        dispatch("requestAddressList");
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestAddressDel({ dispatch }, params = {}) {
      try {
        await AddressDelApi(params);
        dispatch("requestAddressList");
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestUpdateLoginPasswordList({ dispatch }, params = {}) {
      try {
        await UpdateLoginPasswordApi(params);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestGetUserBalanceList({ commit }, params = {}) {
      try {
        const result = await GetUserBalanceApi(params);
        commit("updateUserBalance", result.data);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestSetSafePasswordList({ dispatch }, params = {}) {
      try {
        await SetSafewordApi(params);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestUpdateSafePasswordList({ dispatch }, params = {}) {
      try {
        await UpdateSafewordApi(params);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestSearchResultList({ commit }, params = {}) {
      try {
        const result = await SearchResultListApi({
          ...defaultPageInfo,
          ...params,
        });
        console.log('updateSerachResultList', result.data);
        commit("updateSerachResultList", result.data);
        return Promise.resolve(result.data);
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestCollectGoodsList({ commit }, params = {}) {
      try {
        const result = await KeepGoodsListApi(params);
        commit("updateCollectGoodsList", result.data);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestCollectSellerList({ commit }, params = {}) {
      try {
        const result = await FocusSellerListApi(params);
        commit("updateCollectSellerList", result.data);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestCollectSellerAdd({ commit }, params = {}) {
      try {
        await FocusSellerAddApi(params);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestCollectSellerDel({ commit }, params = {}) {
      try {
        await FocusSellerDelApi(params);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestCollectGoods({ commit }, params = {}) {
      try {
        await KeepGoodsAddApi(params);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestCollectGoodsDel({ commit }, params = {}) {
      console.log('params ->', params);

      try {
        await KeepGoodsCancelApi(params);
        return Promise.resolve();
      } catch (error) {
        console.error("err0r", error);
        return Promise.reject();
      }
    },
    async requestMessageList({ commit }, params = {}) {
      try {
        const result = await OnlinechatApi(params);
        commit("updateMessageList", result.data);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestUnreadMessageList({ commit }, params = {}) {
      try {
        const result = await OnlinechatUnreadApi(params);
        
        commit("updateUnreadMessage", result.data || 0);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestSendMessage({ commit }, params = {}) {
      try {
        await OnlinechatSendApi(params);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
  },
  getters: {
    addressList: (state) => state.addressList,
    defaultAddress: (state) => state.defaultAddress,
    userBalance: (state) => state.userBalance,
    serachResultList: (state) => state.serachResultList,
    paySelectAddress: (state) => state.paySelectAddress,
    collectGoodsList: (state) => state.collectGoodsList,
    collectSellerList: (state) => state.collectSellerList,
    messageList: (state) => state.messageList,
    unreadMessage: (state) => state.unreadMessage,
  },
};
