export default {
    state: {
        qiangdan: {},
        qiangdan_status:false,
        qiangdan_tanchuang:false,
        dizhi:{},
        count: 0
    },
    getters: {
        qiangdan: state => state.qiangdan,
        qiangdan_status: state => state.qiangdan_status,
        qiangdan_tanchuang: state => state.qiangdan_tanchuang,
        dizhi_duqu: state=> state.dizhi
    },
    mutations: {
        setQiangdan: (state, qiangdan) => {
            console.log(1233)
            state.qiangdan = qiangdan
        },
        setCount(state, value) {
            state.count = value
        },
        getCount(state) {
            return state.count
        },
        qiangdan_status_sj: (state, qiangdan_status) => {
            state.qiangdan_status = qiangdan_status
        },
        qiangdan_tanchuang_sj: (state, qiangdan_tanchuang) => {
            state.qiangdan_tanchuang = qiangdan_tanchuang
        },
        dizhi_sj: (state, dizhi) => {
            state.dizhi = dizhi
        },
    }
}

