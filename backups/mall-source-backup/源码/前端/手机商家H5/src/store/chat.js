import { defineStore } from 'pinia'
import { dateFormat } from "@/utils/index.js";
import { sellerInfo } from '@/service/shop.api.js'
import { useUserStore } from './user.js'
const mode = import.meta.env.MODE

export const useChatStore = defineStore('chatStore', {
  state: () => ({
    chatNum: 0,
    showChat: false
  }),
  actions: {
    async setChatHandle() {
      
      if(['familyShop'].includes(mode)) {
        this.showChat = true
        const userInfo = useUserStore().userInfo
        if (userInfo.token) {
          const sellerInfoData = await sellerInfo()

          im_create_iframe_client.setParams({
            userType: 3,
            lang: 'en',
            userId: userInfo.usercode,
            userName: userInfo.username,
            accountType: sellerInfoData.roleName === 'GUEST' ? "演示店铺" : "正式店铺",
            reference: sellerInfoData.recomUserName || '', // 推荐人
            registerTime: sellerInfoData.createTime ? dateFormat(sellerInfoData.createTime) : dateFormat(new Date()),
            lastLoginTime: userInfo.lastLoginTime || dateFormat(new Date()),
            headImg: sellerInfoData.avatar || '',
          });
          im_create_iframe_client.setIconStatus(false)
          im_create_iframe_client.eventOrder((event) => {
            if (event.eventType == "unReadNumChange") { // 消息未读变化事件
              this.chatNum = event.data || 0
            }
          });
        } else {
          im_create_iframe_client.setParams({
            userType: 1,
            userName: '游客',
            lastLoginTime: dateFormat(new Date()),
            lang: 'en',
          });
          im_create_iframe_client.setIconStatus(false)
        }
      }
    },
    closeChatHandle() {
      if (['familyShop'].includes(mode) && window.im_create_iframe_client) {
        this.showChat = false
        this.chatNum = 0
        im_create_iframe_client.close()
        this.setChatHandle()
      }
    },
  },
  persist: false // 关闭数据持久化
})
