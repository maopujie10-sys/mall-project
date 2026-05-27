import {ProductDetailsApi, ProductCommentApi, SellerInfoApi} from "@/api";

const defaultPageInfo = {pageNum: 1, pageSize: 20};

export const productDetailsMoule = {
    namespaced: true, state: () => ({
        // 商品详情
        productDetails: {seller: {}}, // 商家信息
        sellerInfo: {}, // 商品评价
        productComment: [], productCommentNum: 0, productCommentPageInfo: {...defaultPageInfo},
    }), mutations: {
        updateProductDetails(state, data) {
            // console.log('---updateProductDetails-----',data)
            state.productDetails = {...data};            
        }, updateSellerInfo(state, data) {
            state.sellerInfo = {...data};
        }, updateProductComment(state, data) {
            state.productComment = [...data.pageList];
            state.productCommentNum = data.evaluationNum;
            state.productCommentPageInfo = {...data.pageInfo};
        },
    }, actions: {
        async requestProductDetails({commit}, params = {}) {
            try {
                const result = await ProductDetailsApi(params);
                commit("updateProductDetails", result.data);
                return Promise.resolve();
            } catch (error) {
                console.error(error);
                return Promise.reject();
            }
        }, async requestSellerInfo({commit}, params = {}) {
            try {
                const result = await SellerInfoApi(params);
                commit("updateSellerInfo", result.data);
                return Promise.resolve();
            } catch (error) {
                console.error(error);
                return Promise.reject();
            }
        }, async requestRecommendLList({commit}, params = {}) {
            try {
                const result = await ProductCommentApi({
                    ...defaultPageInfo, ...params,
                });
                commit("updateProductComment", result.data);
                return Promise.resolve(result.data);
            } catch (error) {
                console.error(error);
                return Promise.reject();
            }
        },
    }, getters: {
        productDetails: (state) => state.productDetails,
        sellerInfo: (state) => state.sellerInfo,
        productComment: (state) => state.productComment,
        productCommentPageInfo: (state) => state.productCommentPageInfo,
        productCommentNum: (state) => state.productCommentNum,
    },
};
