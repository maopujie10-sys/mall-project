import {userOnlineChatController} from "@/api/user";
import {getMessageNumber, getUnprocessedOrder} from "@/api/im.api";


const state = {
    totalUnreadMessages: 0,//聊天消息未读数量
    chatInterval: null,
    messageNumber: 0, //站内信未读数量
    massageInterval: null,
    totalUnprocessedOrder: 0, //未处理的订单总数
}

const mutations = {
    CHANGE_TOTAL_UNREAD_MESSAGES: (state, value) => {
        state.totalUnreadMessages = value
    },
    CHANGE_CHAT_INTERVAL: (state, value) => {
        state.chatInterval = value
    },
    DELETE_CHAT_INTERVAL: (state) => {
        state.chatInterval && clearInterval(state.chatInterval)
        state.chatInterval = null
    },
    CHANGE_MASSAGE_INTERVAL: (state, value) => {
        state.massageInterval = value
    },
    DELETE_MASSAGE_INTERVAL: (state) => {
        state.massageInterval && clearInterval(state.massageInterval)
        state.massageInterval = null
    },
    CHANGE_MESSAGE_NUMBER: (state, value) => {
        state.messageNumber = value
    },
    CHANGE_TOTAL_ORDER_MESSAGES: (state, value) => {
        state.totalUnprocessedOrder = value
    }
}

const actions = {
    async userOnlineChatController({commit}, params = {}) {
        try {
            let res = await userOnlineChatController({...params, loginType: 'shop'});
            commit('CHANGE_TOTAL_UNREAD_MESSAGES', res.data)
            return Promise.resolve();
        } catch (error) {
            console.error(error);
            return Promise.reject();
        }
    },
    async getMessageNumber({commit}, params = {type: 3}) {
        try {
            let res = await getMessageNumber(params);
            commit('CHANGE_MESSAGE_NUMBER', res.data.count)
            return Promise.resolve();
        } catch (error) {
            console.error(error);
            return Promise.reject();
        }
    },
    async startChatInterval({commit, dispatch}, params = {}) {

        dispatch('userOnlineChatController', params)
        let chatInterval = setInterval(() => {
            // 如果token为空则停止轮询
            if (!localStorage.getItem('token')) {
                commit('DELETE_CHAT_INTERVAL')
                return
            }
            dispatch('userOnlineChatController', params)
        }, 10000)
        commit('CHANGE_CHAT_INTERVAL', chatInterval)
    },
    async startMassageInterval({commit, dispatch}, params = {type: 3}) {  //站内信
        dispatch('getMessageNumber', params)
        let massageInterval = setInterval(() => {
            dispatch('getMessageNumber', params)
        }, 30000)
        commit('CHANGE_MASSAGE_INTERVAL', massageInterval)
    },
    async getUnprocessedOrder({commit}, params = {}) {
        try {
            let res = await getUnprocessedOrder(params);
            commit('CHANGE_TOTAL_ORDER_MESSAGES', res.data.noPushNum || 0)
            return Promise.resolve();
        } catch (error) {
            console.error(error);
            return Promise.reject();
        }
    }
}

export default {
    namespaced: true,
    state,
    mutations,
    actions
}
