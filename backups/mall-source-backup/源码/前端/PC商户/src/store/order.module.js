import {
  SubmitOrderApi,
  PayOrderApi,
  CancelOrderApi,
  OrderListApi,
  OrderDetailsApi,
  OrderGoodsApi,
  OrderReceiptApi,
  OrderReturnApi,
  OrdeEvaluationApi, 
  SetSafewordApi,
  OrderGetLogistics
} from "@/api";
import { ES_REMIND_ORDER } from '@/common'
const defaultPageInfo = { pageNum: 1, pageSize: 20 };
const remindList = localStorage.getItem(ES_REMIND_ORDER) ? JSON.parse(localStorage.getItem(ES_REMIND_ORDER)) : []

export const orderMoule = {
  namespaced: true,
  state: () => ({
    orderList: [],
    orderDetails: {},
    orderGoods: [],
    logistics: [],
    remindList: remindList
  }),
  mutations: {
    updateOrderList(state, data) {
      state.orderList = [...data.pageList];
    },
    updateOrderDetailsList(state, data) {
      state.orderDetails = { ...data.orderInfo };
    },
    updateOrderGoodsList(state, data) {
      state.orderGoods = [...data.pageList];
    },
    updateRemindList(state, data) {
      state.remindList = [...data]
    },
    updateLogistics(state, data) {
      if (Array.isArray(data)) {
        data.sort((a, b) => a.createTime - b.createTime)
      }
      state.logistics = data
    }
  },
  actions: {
    async requestOrderList({ commit }, params = {}) {
      try {
        const result = await OrderListApi({ ...defaultPageInfo, ...params });
        commit("updateOrderList", result.data);
        return Promise.resolve(result.data);
      } catch (error) {
        console.error(error);
        return Promise.reject(error);
      }
    },
    async requestOrderSubmit({ commit }, params = {}) {
      try {
        const result = await SubmitOrderApi(params);
        return Promise.resolve(result.data);
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestOrderPay({ commit }, params = {}) {
      return await PayOrderApi(params);
    },
    async setSafewordFunc({ commit }, params = {}) {
      try {
        await SetSafewordApi(params);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestOrderCancel({ commit }, params = {}) {
      try {
        await CancelOrderApi(params);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestOrderLogistics({ commit }, params = {}) {
      try {
        const result = await OrderGetLogistics(params);
        commit('updateLogistics', result.data)
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestOrderGoodsList({ commit }, params = {}) {
      try {
        const result = await OrderGoodsApi(params);
        commit("updateOrderGoodsList", result.data);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestOrderReceipt({ commit }, params = {}) {
      try {
        await OrderReceiptApi(params);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestOrderReturn({ commit }, params = {}) {
      try {
        await OrderReturnApi(params);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestOrderDetailsList({ commit }, params = {}) {
      try {
        const result = await OrderDetailsApi(params);
        commit("updateOrderDetailsList", result.data);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestOrderEvaluationList({ commit }, params = {}) {
      try {
        await OrdeEvaluationApi(params);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
  },
  getters: {
    orderList: (state) => state.orderList,
    orderDetails: (state) => state.orderDetails,
    orderGoods: (state) => state.orderGoods,
    remindList: (state) => state.remindList,
    logistics: (state) => state.logistics
  },
};
