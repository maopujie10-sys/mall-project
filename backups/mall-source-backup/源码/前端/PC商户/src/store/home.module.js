import {
  CategoryApi,
  GetHomeBanner,
  RecommendedProductsApi,
  RecommendedProductsNewApi,
  MerchantListApi,
  MerchantProductListApi,
  SellerGoodsListApi,
  getDownloadAppUrl
} from "@/api";

const defaultPageInfo = { pageNum: 1, pageSize: 12 };

export const homeMoule = {
  namespaced: true,
  state: () => ({
    // 分类
    categoryList: [],
    categoryPageInfo: { ...defaultPageInfo },
    // 推荐商品
    recommendList: [],
    recommendPageInfo: { ...defaultPageInfo },
    // 新品
    newList: [],
    newPageInfo: { ...defaultPageInfo },
    // 底部商品
    bottomList: [],
    bottomPageInfo: { ...defaultPageInfo },
    // 商家列表
    merchantList: [],
    // 商家商品列表
    merchantGoodsList: [],
    //全部商品
    sellerGoodsList: [],
    // 首页轮播图
    homeBanner: [],
    searchValue: '',
    downAppUrl: ''
  }),
  mutations: {
    updateCategoryList(state, data) {
      // state.categoryList = [...data]
      state.categoryList = [...data.pageList];
      state.categoryPageInfo = { ...data.pageInfo };
    },
    updateRecommendList(state, data) {
      state.recommendList = [];
      state.recommendList = [...data.pageList];
      state.recommendPageInfo = { ...data.pageInfo };
    },
    updateNewList(state, data) {
      state.newList = [...data.pageList];
      state.newPageInfo = { ...data.pageInfo };
    },
    updateBottomList(state, data) {
      state.bottomList = [...data.pageList];
      state.bottomPageInfo = { ...data.pageInfo };
    },
    updateMerchantList(state, data) {
      state.merchantList = [...data.pageList];
    },
    updateMerchantGoodsList(state, data) {
      state.merchantGoodsList = [...data.pageList];
    },
    updateSellerGoodsList(state, data) {
      state.sellerGoodsList = [...data.pageList];
    },
    updateSearchValue(state, val) {
      state.searchValue = val;
    },
    updateHomeBanner(state, val) {
      state.homeBanner = val;
    },

  },
  actions: {

    async initDownAppUrl({ commit, state }) {
      const res = await getDownloadAppUrl();
      state.downAppUrl = res.data
    },

    async requestCategoryList(
      { commit, state },
      params = { pageNum: 1, pageSize: 20 }
    ) {
      try {
        // if (state.categoryList.length) return Promise.resolve();
        const result = await CategoryApi();
        commit("updateCategoryList", result.data);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },

    async requestHomeBanner(
      { commit, state },
      params = {}
    ) {
      try {
        const { data } = await GetHomeBanner({ ...defaultPageInfo, ...params });
        commit("updateHomeBanner", data.banner);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },

    async requestRecommendLList({ commit }, options = { params: {}, type: 2, pageSize: 10 }) {
      try {
        const result = await RecommendedProductsApi({
          ...defaultPageInfo,
          ...options.params,
        });
        const updateCallbackNames = [
          "updateRecommendList",
          "updateNewList",
          "updateBottomList",
        ];
        commit(updateCallbackNames[options.type], result.data);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestRecommendNewLList({ commit }, options = { type: 1 }) {
      try {
        const result = await RecommendedProductsNewApi({
          ...options,
        });
        const updateCallbackNames = [
          "updateNewList",
          "updateRecommendList"
        ];
        const data = {
          pageList: result.data.result || [],
          pageInfo: {}
        }
        commit(updateCallbackNames[options.type], data);
        return Promise.resolve();
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestMerchantList(
      { commit },
      params = { pageNum: 1, pageSize: 10 }
    ) {
      try {
        const result = await MerchantListApi(params);
        commit("updateMerchantList", result.data);
        return Promise.resolve(result.data);
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    async requestMerchantGoodsList(
      { commit },
      params = { pageNum: 1, pageSize: 10 }
    ) {
      try {
        const result = await MerchantProductListApi(params);
        commit("updateMerchantGoodsList", result.data);
        return Promise.resolve(result.data);
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
    updateMerchantGoodsListHandle(
      { commit },
      data
    ) {
      commit("updateMerchantGoodsList", data);
    },
    async requestSellerGoodsList(
      { commit },
      params = { pageNum: 1, pageSize: 10 }
    ) {
      try {
        const result = await SellerGoodsListApi({
          ...defaultPageInfo,
          ...params,
        });
        commit("updateSellerGoodsList", result.data);
        return Promise.resolve(result.data);
      } catch (error) {
        console.error(error);
        return Promise.reject();
      }
    },
  },
  getters: {
    categoryList: (state) => state.categoryList,
    recommendList: (state) => state.recommendList,
    newList: (state) => state.newList,
    bottomList: (state) => state.bottomList,
    merchantList: (state) => state.merchantList,
    merchantGoodsList: (state) => state.merchantGoodsList,
    sellerGoodsList: (state) => state.sellerGoodsList,
    storeSearchValue: (state) => state.searchValue,
    homeBanner: (state) => state.homeBanner,
    downAppUrl: (state) => state.downAppUrl
  },
};
