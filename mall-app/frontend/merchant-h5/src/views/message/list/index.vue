<template>
  <div class="page-main-content">
    <fx-header v-if="!headHide" :fixed="true">
      <template #title>
        {{ $t('消息') }}
      </template>
    </fx-header>
    <div v-if="!headHide" style="height: 46px;" />

    <div class="list-content">
      <div class="item-list" @click="openSystemList">
        <div class="avatar sys">
          <van-icon name="bell" class="icon" />
        </div>
        <div class="flex info-content">
          <h3>{{ t('系统消息') }}</h3>
          <p v-if="sysMsgInfo.count" class="num">{{ sysMsgInfo.count }}</p>
        </div>
        <div class="flex txt-content">
          <p class="txt">{{ sysMsgInfo.content || '-' }}</p>
          <p class="time">{{ formatZoneDate(sysMsgInfo.time, 'YYYY-MM-DD HH:mm') }}</p>
        </div>
      </div>
      <div v-for="item in listData" :key="item.id" class="item-list" @click="goToDetails(item)">
        <div class="avatar">
          <img :src="item.avatarImg || (isShop ? userDefault.href : shopDefault.href)" alt="" />
        </div>
        <div class="flex info-content">
          <h3>{{ item.showName || '-' }}</h3>
          <p v-if="item.count" class="num">{{ item.count }}</p>
        </div>
        <div class="flex txt-content">
          <p class="txt">{{ item.content || '-' }}</p>
          <p class="time">{{ item.showTime }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, nextTick, watch } from 'vue'
import { onBeforeRouteLeave, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Toast } from 'vant'
import { openPage, formatZoneDate, formeateUser } from '@/utils'
import { useUserStore } from "@/store/user.js";
import { msgTypeInfo } from './../config'

import {
  chatUserlist,
  countUnread,
  messagePagelist
} from '@/service/user.api.js'

export default defineComponent({
  name: 'MessageList',
  setup() {
    const { t, locale } = useI18n()
    const route = useRoute()
    
    const shopDefault = new URL('@/assets/image/avatar/avatar_d.png', import.meta.url)
    const userDefault = new URL('@/assets/image/userAvatar/default.png', import.meta.url)
    const listData = ref([])
    const pageLoading = ref(true)
    const interval = ref(0)
    
    const dataFormate = async (data) => {
      const dataArr = []
      for (let i = 0; i < data.length; i++) {
        const obj = {
          ...data[i]
        }

        const nowTime = new Date().getTime()
        const localUpdatetime = formatZoneDate(obj.updatetime, 'YYYY-MM-DD HH:mm')
        const updatetime = new Date(localUpdatetime).getTime()
        const updatetimeStr = localUpdatetime.slice(localUpdatetime.indexOf(' ') + 1)
        const timeNum = (nowTime - updatetime) / 1000
        let showTime = ''

        if (timeNum < 60) {
          showTime = t('刚刚')
        } else if (timeNum < 60 * 60 * 24) {
          showTime = updatetimeStr
        } else {
          showTime = localUpdatetime
        }
        obj.showTime = showTime
        obj.count = obj.unreadmsg > 99 ? 99 : obj.unreadmsg
        if (isShop.value) {
          obj.showName = formeateUser(obj.username, false, true)
          if (data[i].useravatar && !isNaN(Number(data[i].useravatar))) {
            await import(`./../../../assets/image/userAvatar/${data[i].useravatar}.png`).then(res => {
              obj.avatarImg = res.default
              dataArr.push(obj)
            })
          } else {
            obj.avatarImg = ''
            dataArr.push(obj)
          }
        } else {
          obj.showName = obj.username
          obj.avatarImg = data[i].avatar || ''
          dataArr.push(obj)
        }
      }
      return dataArr
    }

    const getListData = () => {
      if (pageLoading.value) {
        Toast.loading({duration: 0})
      }
      chatUserlist({
        loginType: isShop.value ? 'shop' : 'user'
      }).then(async res => {
        const dataArr = res || []
        listData.value = await dataFormate(dataArr)
        nextTick(() => {
          pageLoading.value = false
        })
      }).catch(() => {
        pageLoading.value = false
      })
    }

    const goToDetails = (data) => {
      openPage({
        path: '/messageCenter',
        query: {
          partyId: data.partyid,
          username: data.showName
        }
      })
    }

    const openSystemList = () => {
      document.dispatchEvent(new CustomEvent('systemListRefresh'))
      openPage('/message/system')
    }

    const getValueOf = (data, key) => {
      const dataArr = data.varInfo ? JSON.parse(data.varInfo) : []
      const item = dataArr.find(item => item.code === key)
      return item ? item.value : ''
    }

    const getValueStr = (data, key) => {
      const dataArr = data.varInfo ? JSON.parse(data.varInfo) : []
      const item = dataArr.find(item => item.code === key)
      return item ? item.value : '0'
    }

    const sysMsgInfo = ref({
      content: '',
      count: 0,
      time: ''
    })
    const getSysMessageInfo = () => {
      countUnread({
        type: 3,
        module: 1
      }).then(res => {
        const resNum = res.count || 0
        sysMsgInfo.value.count = resNum > 99 ? '99+' : resNum
      })

      const params = {
        pageSize: 10,
        pageNum: 1,
        totalElements: -1,
        type: 3,
        status: 0,
        module: 1
      }
      messagePagelist(params).then(res => {
        const resData = res.elements || []
        if (resData.length) {
          const data = resData[0]
          const varObj = {}
          const dataArr = data.varInfo ? JSON.parse(data.varInfo) : []
          dataArr.forEach(item => {
            varObj[item.code] = ['complaintReason'].includes(item.code) ? t(item.value) : item.value
          })
          const txtData = msgTypeInfo[data.bizType]
          const item = dataArr.find(item => item.code === txtData.key)
          let resTxt = ''
          if (['inbox_recharge_success', 'inbox_withdraw_success'].includes(data.bizType)) {
            const tMsg = data.bizType === 'inbox_recharge_success' ? 'rechargeSuccessTips' : 'withdrawalSuccessTips'
            resTxt = t(tMsg, {orderAmount: getValueStr(data, 'orderAmount')})
          } else if (['inbox_store_audit_fail', 'inbox_store_audit_success'].includes(data.bizType)) {
            resTxt = data.bizType === 'inbox_store_audit_fail' ? t('storeAuthenticationFailedTips', {shop_name: getValueOf(data, 'shop_name'), reason: getValueOf(data, 'reason')}) : t('storeAuthenticationPassedTips', {shop_name: getValueOf(data, 'shop_name')})
          } else if (['inbox_store_compliant_success', 'inbox_withdrawal_audit_fail', 'inbox_recharge_audit_fail'].includes(data.bizType)) {
            resTxt = t(txtData.txt, varObj)
          } else {
            if (txtData.key) {
              resTxt = t(txtData.txt) + (item ? item.value : '0')
              if (txtData.txt1) {
                resTxt += t(txtData.txt1)
              }
            } else {
              resTxt = t(txtData.txt)
            }
          }
          
          sysMsgInfo.value.content = resTxt
          sysMsgInfo.value.time = data.sendTime
        }
      })
    }

    watch(pageLoading, (val) => {
      if (!val && !interval.value) {
        interval.value = setInterval(() => {
          getListData()
        }, 5000)
      }
    })

    onBeforeRouteLeave(() => {
      if (interval.value) {
        clearInterval(interval.value)
      }
    })

    const headHide = ref(false)
    const isShop = ref(true)
    nextTick(async () => {
      const { token, nohead, lang } = route.query
      const userStore = useUserStore()
      if (lang) {
        locale.value = lang
        localStorage.setItem('lang', lang)
      }
      if (token) {
        headHide.value = Boolean(nohead)
        Toast.loading({duration: 0})
        await userStore.getUserInfo(true, token)
      }
      // isShop.value = Boolean(userStore.userInfo.roletype)
      isShop.value = true
      getListData()
      getSysMessageInfo()
    })

    return {
      t,
      isShop,
      shopDefault,
      userDefault,
      pageLoading,
      listData,
      sysMsgInfo,
      headHide,
      goToDetails,
      formatZoneDate,
      openPage,
      openSystemList
    }
  }
})
</script>

<style lang="scss" scoped>
.list-content {
  .item-list {
    position: relative;
    padding: 15px;
    padding-left: 75px;
    border-bottom: 1px solid #eee;
    background-color: #fff;
    > .avatar {
      width: 45px;
      height: 45px;
      overflow: hidden;
      border-radius: 50%;
      position: absolute;
      left: 15px;
      top: 50%;
      margin-top: -22.5px;
      background-color: #f8f8f8;
      &.sys {
        background-color: var(--site-main-color);
        display: flex;
        align-items: center;
        justify-content: center;
        .icon {
          color: #fff;
          font-size: 24px;
        }
      }
      > img {
        width: 100%;
        height: auto;
      }
    }
    > .flex {
      width: 100%;
      display: flex;
      justify-content: space-between;
      &.info-content {
        align-items: flex-start;
        > h3 {
          font-size: 14px;
          font-weight: normal;
          color: #000 !important;
          flex: 1;
        }
        > .num {
          float: right;
          vertical-align: baseline;
          background: #ff3e3e;
          border-radius: 50%;
          line-height: 15px;
          font-size: 12px;
          padding: 1px 5px;
          border-radius: 10px;
          color: #fff;
          &.red {
            padding: 0;
            width: 8px;
            height: 8px;
            border-radius: 50%;
          }
        }
      }
      &.txt-content {
        align-items: center;
        margin-top: 5px;
        > .txt {
          min-width: 0;
          font-size: 12px;
          text-overflow: ellipsis;
          overflow: hidden;
          white-space: nowrap;
          width: calc(100% - 110px);
        }
        > .time {
          font-size: 10px;
          color: #999;
        }
      }
    }
  }
}
</style>
