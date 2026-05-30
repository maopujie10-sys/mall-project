<template>
  <div class="shop-header">
    <div class="shop-header-content">
      <div class="avatar-content">
        <div class="avatar">
          <img v-if="sellerData && sellerData.avatar" :src="sellerData.avatar" alt="">
          <img v-else :src="images.logo.href" alt="">
        </div>
        <!-- <div class="level">
          <img v-if="currentLevel" :src="levleIcon[currentLevel]" alt="">
        </div> -->
      </div>
      
      <!-- <p class="name">{{ sellerData?.name || 'Store Name' }}</p> -->
      <div class="name-content">
        <p>{{ sellerData?.name || 'Store Name' }}</p>
        <img v-if="currentLevel && showLevelIcon" :src="levleIcon[currentLevel]" alt="">
      </div>
      <div class="enter" :class="{'is-ar': isArLang}">
        <img :src="images.service.href" alt="" @click="openService(false)">
        <div v-if="showChat && chatNum" class="count one">{{ chatNum }}</div>
        <div v-if="serviceUnread && !isMc && !showChat" class="count one">{{ serviceUnreadNum }}</div>
        <img :src="images.message.href" alt="" @click="openPage('/message')">
        <div v-if="countNum" class="count">{{ countNum }}</div>
      </div>
    </div>
    <div v-if="setStep" class="step-content">
      <div class="step-content-item">
        <div v-for="(item, index) in verifyStepDataRef" :key="index" :class="{'active': index < setStep - 1}" class="item">
          <div class="icon"></div>
          <p>{{ t(item.name) }}</p>
        </div>
      </div>
      <div class="step-content-info">
        <p>{{ t(currentStepInfo.tips) }}</p>
        <div class="btn-content">
          <div class="btn" @click="openPage(currentStepInfo.href)">{{ t(currentStepInfo.btnTxt) }}</div>
        </div>
      </div>
    </div>
  </div>
  
</template>

<script setup>
  import { ref, toRefs, computed, onMounted, nextTick } from 'vue'
  import { openPage } from '@/utils'
  import { useI18n } from 'vue-i18n'
  import { verifyStepData } from './../config'
  import {
    sellerInfo
  } from '@/service/shop.api.js'
  import { _getIdentify, unreadCount, countUnread } from '@/service/user.api.js'
  import { _getUnreadMsg } from '@/service/im.api.js'
  import { useShopInfoStore } from '@/store/user'
  import { useChatStore } from '@/store/chat'
  import { useRoute } from 'vue-router'
  import { openService } from '@/utils/index.js'
  import { arLangCheck } from '@/utils/arLangCheck'

  const props = defineProps({
    sellerGoodsNum: {
      type: Number,
      default: 0
    }
  })

  const chatStore = useChatStore()
  const showChat = computed(() => chatStore.showChat)
  const chatNum = computed(() => chatStore.chatNum)

  const isArLang = arLangCheck()

  const { t } = useI18n()

  const countNum = ref(0)
  const countNumTotal = ref(0)

  const { sellerGoodsNum } = toRefs(props)
  const setStep = ref(0)
  const sellerData = ref({})
  const sellerLoading = ref(true)
  const verifyStepDataRef = ref([...verifyStepData])

  const levleIcon = {
    level1: new URL('@/assets/image/level/level_1.png', import.meta.url),
    level2: new URL('@/assets/image/level/level_2.png', import.meta.url),
    level3: new URL('@/assets/image/level/level_3.png', import.meta.url),
    level4: new URL('@/assets/image/level/level_4.png', import.meta.url),
    level5: new URL('@/assets/image/level/level_5.png', import.meta.url),
    level6: new URL('@/assets/image/level/level_6.png', import.meta.url),
    level7: new URL('@/assets/image/level/level_7.png', import.meta.url)
  }

  const currentLevel = ref('')

  // 平台客服
  const isMc = computed(() => {
    const data = ['metashop']
    const mode = import.meta.env.MODE
    return data.includes(mode)
  })

  // 等级图片是否显示
  const showLevelIcon = computed(() => {
    const mode = import.meta.env.MODE
    // return mode !== 'argos'
    return mode !== ''
  })

  const images = {
    logo: new URL('@/assets/image/shop/head_default.png', import.meta.url),
    service: new URL('@/assets/image/shop/service.png', import.meta.url),
    message: new URL('@/assets/image/shop/message.png', import.meta.url)
  }

  const currentStepInfo = computed(() => {
    let info = null
    if (setStep.value) {
      const index = setStep.value - 1
      const itemData = verifyStepDataRef.value[index]
      const itemIndex = index === 1 ? sellerData.value.authStatus : 0
      info = itemData.tipsData[itemIndex]
    }
    return info
  })

  const serviceUnread = ref(false)
  const serviceUnreadNum = ref(0)
  const unreadCountTotal = ref(0)
  const unreadSysCountTotal = ref(0)
  const getCount = async (flag) => {
    if (!isMc.value && !showChat.value) { // 跳美洽的就不请求
      _getUnreadMsg().then(res => { // 客服未读消息
        const hasMsg = Number(res)
        if (hasMsg !== serviceUnread.value) {
          serviceUnread.value = hasMsg
          if (hasMsg) {
            serviceUnreadNum.value = Number(res) > 99 ? '99+' : Number(res)
            document.dispatchEvent(new CustomEvent('servicePlay'))
          } else {
            serviceUnreadNum.value = ''
          }
        }
      })
    }
    

    let count = 0
    await unreadCount({
      loginType: 'shop'
    }).then(res => { // 聊天消息未读
      const resNum = res || 0
      count = Number(resNum)
      if (unreadCountTotal.value !== count) {
        unreadCountTotal.value = count
        if (count) {
          document.dispatchEvent(new CustomEvent('chatPlay'))
        }
      }
    })
    
    await countUnread({ // 系统消息未读
      type: 3,
      module: 1
    }).then(res => {
      const resNum = Number(res.count) || 0
      count += resNum
      const countR = count > 99 ? '99+' : count
      if (countNumTotal.value !== count) {
        countNum.value = countR
        countNumTotal.value = count
        if (resNum > unreadSysCountTotal.value) {
          document.dispatchEvent(new CustomEvent('notifyPlay'))
        }
        unreadSysCountTotal.value = resNum
      }
    })
  }

  // 轮巡获取未读消息数量
  const interval = ref(null)
  const getCountInterval = () => {
    if (interval.value || interval.value === 0) {
      clearInterval(interval.value)
    }

    sessionStorage.setItem('msgRequset', true)
    interval.value = setInterval(async () => {
      await getCount()
    }, 5000)
  }

  const clearMsgHandle = () => {
    if (interval.value || interval.value === 0) {
      sessionStorage.removeItem('msgRequset')
      clearInterval(interval.value)
    }
  }

  const getStoreInfo = async (flag = false) => {
    sellerLoading.value = true
    setStep.value = 0

    if (!flag) {
      nextTick(async () => {
        await getCount()
        getCountInterval()
      })
    }

    // 基础信息
    await sellerInfo().then(res => {
      sellerData.value = res || {}
      const level = res.mallLevel
      switch(level) {
        case 'C':
          currentLevel.value = 'level2'
          break
        case 'B':
          currentLevel.value = 'level3'
          break
        case 'A':
          currentLevel.value = 'level4'
          break
        case 'S':
          currentLevel.value = 'level5'
          break
        case 'SS':
          currentLevel.value = 'level6'
          break
        case 'SSS':
          currentLevel.value = 'level7'
          break
        default:
          currentLevel.value = 'level1'
      }
    })
    // 认证信息
    await _getIdentify().then(res => {
      const status = Number(res.status)
      let statusInfo = status
      if (status === 2) {
        statusInfo = 3
      } else if (status === 3) {
        statusInfo = 2
      }
      sellerData.value.authStatus = statusInfo
    })

    // 店铺信息
    const shopInfo = useShopInfoStore()
    shopInfo.setShopInfo(sellerData.value)

    const { avatar, name, authStatus } = sellerData.value

    if (!avatar || !name) { // 基本信息包括 店铺名与logo
      setStep.value = 1
    } else if (authStatus === 0 || authStatus === 1 || authStatus === 2) {
      setStep.value = 2
    } else if (sellerGoodsNum.value === 0) {
      setStep.value = 3
    }

    sellerLoading.value = false
  }

  onMounted(() => {
    document.addEventListener('headerRefresh', () => {
      getStoreInfo(true)
    })
    document.addEventListener('clearMsgRequset', () => {
      clearMsgHandle()
    })
    
  })

  // 子组件传递数据
  defineExpose({
    sellerData,
    getStoreInfo,
    getCount
  })
</script>

<style lang="scss" scoped>
.shop-header {
  width: 100%;
  background-color: var(--site-main-color);
  border-bottom: 42px solid var(--site-main-color);
  padding: 0 15px;
  .shop-header-content {
    height: 90px;
    display: flex;
    align-items: center;
    > .avatar-content {
      width: 44px;
      height: 44px;
      position: relative;
      > .avatar {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        border: 1.5px solid #fff;
        overflow: hidden;
        > img {
          width: 100%;
          height: 100%;
        }
      }
      > .level {
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        position: absolute;
        bottom: 0px;
        right: -2px;
        > img {
          width: 100%;
          height: auto;
        }
      }
    }
    
    > .name {
      flex: 1;
      padding: 0 10px;
      color: #fff;
      font-size: 16px;
      font-weight: bold;
    }

    > .name-content {
      flex: 1;
      padding: 0 10px;
      color: #fff;
      font-size: 16px;
      font-weight: bold;
      display: flex;
      align-items: center;
      min-width: 0;
      > p {
        word-break: break-all;
        padding-right: 5px;
        overflow: hidden;
        line-clamp: 2;
        -webkit-line-clamp: 2;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-box-orient: vertical;
      }
      > img {
        width: 20px;
        height: auto;
      }
    }
    > .enter {
      display: flex;
      align-items: center;
      position: relative;
      &.is-ar {
        > img {
          margin-left: 0 !important;
          margin-right: 15px !important;
          &:first-child {
            margin-right: 0 !important;
          }
        }
      }
      > img {
        width: 24px;
        height: 24px;
        margin-left: 15px;
        &:first-child {
          margin-left: 0;
        }
      }
      > .red-point {
        position: absolute;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #ff3e3e;
        top: -2px;
        left: 12px;
        pointer-events: none;
        opacity: 0;
        &.active {
          animation: fadeIn 0.5s infinite;
        }
      }
      > .count {
        vertical-align: baseline;
        background: #ff3e3e;
        border-radius: 50%;
        line-height: 15px;
        font-size: 12px;
        padding: 1px 5px;
        border-radius: 10px;
        color: #fff;
        position: absolute;
        top: -8px;
        right: -10px;
        &.one {
          right: 30px;
        }
      }
    }
  }
  .step-content {
    > .step-content-item {
      width: 100%;
      display: flex;
      align-items: center;
      > .item {
        width: 33.3333%;
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        &::before,
        &::after {
          content: '';
          display: block;
          width: calc((100% - 32px) / 2);
          height: 2px;
          background-color: rgba(255, 255, 255, .4);
          position: absolute;
          top: 12px;
        }
        &::before {
          left: 0;
          border-top-right-radius: 2px;
          border-bottom-right-radius: 2px;
        }
        &::after {
          right: 0;
          border-top-left-radius: 2px;
          border-bottom-left-radius: 2px;
        }
        &:first-child {
          &::before {
            display: none;
          }
        }
        &:last-child {
          &::after {
            display: none;
          }
        }
        &.active {
          &::after {
            background-color: #fff
          }
          > .icon {
            &::after {
              background-color: #fff
            }
          }
          + .item {
            &::before {
              background-color: #fff
            }
          }
        }
        > .icon {
          width: 26px;
          height: 26px;
          background-color: rgba(255, 255, 255, .2);
          border-radius: 50%;
          position: relative;
          &::after {
            content: '';
            display: block;
            width: 14px;
            height: 14px;
            border-radius: 50%;
            background-color: rgba(255, 255, 255, .5);
            position: absolute;
            top: 6px;
            left: 6px;
          }
        }
        > p {
          width: 100%;
          padding: 0 5px;
          color: #fff;
          font-size: 12px;
          margin-top: 7px;
          text-overflow: ellipsis;
          overflow: hidden;
          white-space: nowrap;
          text-align: center;
        }
      }
    }
    > .step-content-info {
      padding: 10px 25px;
      padding-top: 15px;
      margin: 6px 0;
      border-radius: 4px;
      background-color: #fff;
      > p {
        text-align: center;
        color: #333;
        font-size: 12px;
        line-height: 21px;
      }
      > .btn-content {
        display: flex;
        justify-content: center;
        margin-top: 10px;
        > .btn {
          min-width: 130px;
          padding: 0 10px;
          height: 32px;
          text-align: center;
          line-height: 32px;
          background-color: var(--site-main-color);
          border-radius: 4px;
          margin: 0 auto;
          font-size: 12px;
          color: #fff;
        }
      }
      
    }
  }
}
@-webkit-keyframes fadeIn {
  0% {
    opacity: 0
  }

  to {
    opacity: 1
  }
}

@keyframes fadeIn {
  0% {
    opacity: 0
  }

  to {
    opacity: 1
  }
}

</style>
