import { setShopCartLocal, getShopCartLocal, clearShopCartLocal } from '@/util/shop'

export const shopCartMoule = {
  namespaced: true,
  state: () => ({
    // 购物车数据
    shopCart: [],
    // 勾选支付
    checkProductPay: [],
  }),
  mutations: {
    updateShopCart(state, data) {
      state.shopCart = [...data];
      console.log('data11 ->', data);
      setShopCartLocal(data)
    },
    updateCheckProductPay(state, data) {
      state.checkProductPay = [...data];
    },
    clear(state,data) {
      state.shopCart = [];
      clearShopCartLocal(data)
    }
  },
  getters: {
    shopCart: (state) => state.shopCart,
    checkProductPay: (state) => state.checkProductPay,
  },
};
