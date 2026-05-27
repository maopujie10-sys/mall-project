<template>
  <div class="audio-content">
    <audio :src="AudioSounds.chat" ref="AudioChatRef" muted></audio>
    <audio :src="AudioSounds.notify" ref="AudioNotifyRef" muted></audio>
    <audio :src="AudioSounds.chat" ref="AudioServiceRef" muted></audio>
    <audio :src="AudioSounds.order" ref="AudioOrderRef" muted></audio>
    <audio :src="AudioSounds.money" ref="AudioMoneyRef" muted></audio>
  </div>

  <!-- <transition :name="routerTransType">
    <router-view v-slot="{ Component }">
      <keep-alive :include="keepaliveData">
        <component :is="Component" :key="$route.fullPath"/>
      </keep-alive>
    </router-view>
  </transition> -->
  <router-view v-slot="{ Component }">
    <transition :name="routerTransType" mode="out-in">
      <keep-alive :include="keepaliveData">
        <component :is="Component" :key="$route.fullPath" />
      </keep-alive>
    </transition>
  </router-view>

  <fx-footer v-if="route.meta.tarbar" />
</template>

<script setup>
import fxFooter from '@/components/fx-footer/index.vue'
import { useRoute, useRouter } from 'vue-router'
import { usekeepAliveStore } from '@/store/keepAlive.js'
import { computed, onMounted, ref, watch, onBeforeMount } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouterStore } from '@/store/router.js'
import { useOrderStore } from '@/store/order.js'
import { useSystemStore } from '@/store/system.js'
import { useChatStore } from "@/store/chat.js";
import { isPassPage } from '@/utils'
import {  moneylogNotifyCallback } from '@/service/user.api.js'
import { loadJs } from "@/utils"

const route = useRoute()
window.router = useRouter()

const routerStore = useRouterStore()
const orderStore = useOrderStore()
const systemStore = useSystemStore()

const { locale } = useI18n()
systemStore.setIsArLang(locale.value === 'ar')
systemStore.setNotCnLang(!['cn', 'tw'].includes(locale.value))

// 获取系统客服链接
if (!isPassPage()) {
  systemStore.getServeceUrl()
}

const routerTransType = computed(() => {
  return routerStore.routerTransType
})

const usekeepAlive = usekeepAliveStore()
const keepaliveData = computed(() => {
  return usekeepAlive.keepaliveData || []
  // return []
})

const AudioSounds = {
  chat: new URL('@/assets/audio/chat.mp3', import.meta.url),
  notify: new URL('@/assets/audio/notify.mp3', import.meta.url),
  order: new URL('@/assets/audio/order.mp3', import.meta.url),
  money: new URL('@/assets/audio/money.mp3', import.meta.url),
}

// 请求未处理订单数
const orderInterval = ref(null)
const getNotDealOrder = () => {
  if (!orderInterval.value) {
    orderStore.getNoPushNum()
    orderInterval.value = setInterval(() => {
      orderStore.getNoPushNum()
    }, 60000)
  }
}

// 请求到账通知
const moneyInterval = ref(null)
const getMoneyInfoRequst = () => {

}

// 处理到账通知
const moneyLogHandle = async (data) => {
  for (let i = 0; i < data.length; i++) {
    await moneylogNotifyCallback({
      moneyLogId: data[i]
    })
  }
}

const getMoneyInfo = () => {
  if (!moneyInterval.value) {
    getMoneyInfoRequst()
    moneyInterval.value = setInterval(() => {
      getMoneyInfoRequst()
    }, 5000)
  }
}

// 监听到账通知请求触发
document.addEventListener(
  'getMoneyInfoHandle',
  () => {
    getMoneyInfo()
    getNotDealOrder()
  },
  false
)

// 监听退出并停止请求未处理订单数的轮循请求
document.addEventListener(
  'logout',
  () => {
    clearInterval(orderInterval.value)
    orderInterval.value = null
    clearInterval(moneyInterval.value)
    moneyInterval.value = null
  },
  false
)

// 默认触发一次播放
const defaultPlayFlag = ref(false)
const AudioChatRef = ref(null)
const AudioNotifyRef = ref(null)
const AudioServiceRef = ref(null)
const AudioOrderRef = ref(null)
const AudioMoneyRef = ref(null)

const defaultPlay = () => {
  if (!defaultPlayFlag.value && !isPassPage()) {
    AudioChatRef.value.play()
    AudioNotifyRef.value.play()
    AudioServiceRef.value.play()
    AudioOrderRef.value.play()
    AudioMoneyRef.value.play()
    defaultPlayFlag.value = true

    setTimeout(() => {
      AudioChatRef.value.muted = false
      AudioNotifyRef.value.muted = false
      AudioServiceRef.value.muted = false
      AudioMoneyRef.value.muted = false
    }, 1500)

    // 因为订单声音有3秒，在这里开启声音
    setTimeout(() => {
      AudioOrderRef.value.muted = false
    }, 3500)
  }
}

// 系统点击默认触发一次声音播放
document.addEventListener('click', defaultPlay, false)
// 只触发一次默认播放
watch(defaultPlayFlag, (val) => {
  if (val) {
    document.removeEventListener('click', defaultPlay)
  }
})

// 播放
const playAudio = (dom) => {
  if (defaultPlayFlag.value) {
    dom.play()
  }
}

// 监听客服信息
document.addEventListener(
  'servicePlay',
  () => playAudio(AudioServiceRef.value),
  false
)
// 监听系统消息
document.addEventListener(
  'notifyPlay',
  () => playAudio(AudioNotifyRef.value),
  false
)
// 监听聊天消息
document.addEventListener(
  'chatPlay',
  () => playAudio(AudioChatRef.value),
  false
)
// 监听订单消息
document.addEventListener(
  'orderPlay',
  () => playAudio(AudioOrderRef.value),
  false
)

const modeType = import.meta.env.MODE
const mode = modeType === 'mbuy' ? 'argos' : modeType
// console.log('mode', mode)
// console.log('VITE_TITLE', import.meta.env.VITE_APP_TITLE)

const siteTitle = import.meta.env.VITE_APP_TITLE
document.title = siteTitle === 'Mbuy' ? 'Argos' : siteTitle
if (mode !== 'development' && mode !== 'production') {
  // 特殊的mode动态设置ico
  console.log('动态icon', mode)
  const link =
    document.querySelector("link[rel*='icon']") ||
    document.createElement('link')
  link.type = 'image/x-icon'
  link.rel = 'shortcut icon'
  link.href = new URL(`./assets/ico/${mode}.ico`, import.meta.url).href
  document.getElementsByTagName('head')[0].appendChild(link)
}

onBeforeMount( async () => {
  const mode = import.meta.env.MODE
  if (['familyShop'].includes(mode)) {
    await loadJs(`https://lt.xhduh.com/im_create_iframe.js?router=client&id=${Math.random()}`)
    // IM初始化
    const chatStore = useChatStore()
    chatStore.setChatHandle()
  }
})
</script>
<style lang="scss">
@import './assets/css/border.css';

.van-toast {
  word-break: break-word !important;
}

.audio-content {
  width: 0;
  height: 0;
  overflow: hidden;
}

.nationList {
  .van-action-sheet {
    height: 80%;
  }
}

.van-search__content {
  background: #fff !important;
}

.van-dropdown-menu__bar {
  height: 44px !important;
}
</style>
