import { defineStore } from 'pinia'
import { useStorage } from '@vueuse/core'
import { GET_USERINFO, GET_BALANCE } from '@/store/types.store'
import { usekeepAliveStore } from "@/store/keepAlive.js";
import { _info, _getBalance } from "@/service/user.api.js";
import { useChatStore } from "@/store/chat.js";
import router from './../router';

export const useUserStore = defineStore('user', {
    persist: true,
    state: () => ({
        userInfo: {
            token: '',
        }
    }),
    getters: {
    },
    actions: {
        async [GET_USERINFO](userInfoObj) { // 发送请求获取信息
            this.userInfo = userInfoObj
            let data = await _info()
            this.userInfo = { ...this.userInfo, ...data }
            let res = await _getBalance()
            let obj = { ...res }
            this.userInfo = { ...this.userInfo, ...obj }
        },
        async getUserInfo(flag, token) {
            return new Promise(async (resolve, reject) => {
                if (this.userInfo.token && !flag) {
                    if (!this.userInfo.username) {
                        const data = await _info()
                        this.userInfo = { ...this.userInfo, ...data }
                    }
                    resolve(this.userInfo)
                } else {
                    if (token) {
                        this.userInfo.token = token
                    }
                    const TOKEN = JSON.parse(JSON.stringify(this.userInfo.token))
                    let data
                    try {
                        data = await _info()
                    } catch (err) {
                        reject(err)
                    }

                    try {
                        let res = await _getBalance()
                        let obj = { ...res }
                        this.userInfo = { ...data, ...obj }
                        TOKEN && (this.userInfo.token = TOKEN)
                        resolve(this.userInfo)
                    } catch (err) {
                        reject(err)
                    }
                }
            })
        },
        async [GET_BALANCE]() {
            const res = await _getBalance()
            const obj = { ...res }
            this.userInfo = { ...this.userInfo, ...obj }
        },
        async logout(flag = false) {
            const keepAliveStore = usekeepAliveStore()
            keepAliveStore.clearKeepAlive()
            
            document.dispatchEvent(new CustomEvent('logout'))
            this.userInfo = {
                token: ''
            }
            const shopStore = useShopInfoStore()
            shopStore.setShopInfo({})
            const path = router.currentRoute.value.path

            if (sessionStorage.getItem('msgRequset')) {
                document.dispatchEvent(new CustomEvent('clearMsgRequset'))
            }

            await localStorage.removeItem('sellerId')

            useChatStore().closeChatHandle()
            
            if (path !== '/login' && !flag) {
                router.push('/login')
            }
        }
    },
})

export const useShopInfoStore = defineStore('shopInfo', {
    state: () => useStorage('shopInfo', {
        shopInfo: {}
    }),
    actions: {
        setShopInfo(obj) {
            this.shopInfo = obj
        }
    }
})
