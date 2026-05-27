import Vue from 'vue'
import Vuex from 'vuex'
import app from './modules/app'
import user from './modules/user'
import language from './modules/language'
import qiangdan from './modules/qiangdan'
import multiItem from './modules/multiItem'
Vue.use(Vuex)
const store = new Vuex.Store({
    modules: {
        user,
        app,
        language,
        qiangdan,
        multiItem
    }
})
export default store;
