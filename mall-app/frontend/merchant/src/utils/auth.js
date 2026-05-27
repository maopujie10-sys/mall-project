import Cookies from 'js-cookie'
import store from "@/store";

const TokenKey = 'Admin-Token'

export function getToken() {
    return Cookies.get(TokenKey)
}

export function setToken(token) {
    store.commit('user/SET_TOKEN', token)
    localStorage.setItem('token', token)
    return Cookies.set(TokenKey, token)
}

export function removeToken() {
    store.commit('user/SET_TOKEN', '')
    localStorage.setItem('token', '')
    return Cookies.remove(TokenKey)
}
