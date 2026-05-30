<template>
  <div :style="{'background-image': 'url('+ contentBg.href +')'}" class="login-register-content">
    <number-code-dialog v-model="numberCodeVisible" @done="vcodeSuccess" />
    <agree-dialog v-model="agreeVisible" @done="agreeChecked = true" />
    <Vcode :successText="t('vertifyPass')" :failText="t('vertifuFail')" :sliderText="t('vertifyTips')" :imgs="vcodeImgs" :show="vcodeShow" @success="vcodeSuccess" />

    <div class="header-content">
      <h2>{{ t('login') }}</h2>
      <div class="language" :class="{'is-ar': isArLang}" @click="router.push('/language')">
        <img :src="langIcon.href" alt="">
        <img :src="arrowIcon.href" alt="">
      </div>
    </div>
    <div class="logo-content">
      <img :src="appData.logo.href" alt="">
      <h2>{{ appData.name }}</h2>
    </div>
    <div class="type-tab">
      <div v-for="(item, index) in typeTab" :key="index" :class="{'active': index === activeType}" class="item" @click="typeChange(index)">{{ t(item) }}</div>
    </div>
    <div class="form-content">
      <div v-if="activeType === 0" class="item">
        <div class="title">{{ t('email') }}</div>
        <div class="input-content">
          <input-item v-model="formData.username" type="text" :placeholder="t('entryEmail')" clear />
        </div>
      </div>
      <div v-if="activeType === 1" class="item">
        <div class="title">{{ t('phoneNum') }}</div>
        <div class="input-content">
          <input-item v-model="formData.username" v-model:codeNum="codeNum" type="tel" :placeholder="t('entryPhone')" clear area-code />
        </div>
      </div>
      <div class="item">
        <div class="title">{{ t('password') }}</div>
        <div class="input-content">
          <input-item v-model="formData.password" type="password" :placeholder="t('entryPassword')" clear show-password />
        </div>
      </div>
      <div class="link-content" :class="{'is-ar': isArLang}">
        <p>{{ t('如果您没有账号') }}, <span class="link" @click="goRegister">{{ t('点击注册') }}</span></p>
        <p @click="openService" class="link">{{ t('forgetPassword') }}</p>
      </div>

      <div v-if="showAgree" class="agree-content" :class="{'is-ar': isArLang}">
        <div class="check" @click="agreeChecked = !agreeChecked"><van-icon v-if="agreeChecked" name="success" :size="12" /></div>
        <p><span @click="agreeChecked = !agreeChecked">{{ t('我已阅读并同意') }}</span><span class="link" @click="agreeVisible = true">《{{ t('用户协议') }}》</span></p>
      </div>

      <div class="btn">
        <van-button type="custom" :loading="submitLoading" block @click="submitHandle">{{ t('login') }}</van-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Toast } from 'vant'
import { langData } from '@/views/language/config'
import { logoData } from './config'
import InputItem from '@/components/input-item/index.vue'
import Vcode from 'vue3-puzzle-vcode'
import AgreeDialog from './components/AgreeDialog.vue'

import { GET_USERINFO } from '@/store/types.store'
import { useUserStore } from '@/store/user'
import { useSystemStore } from '@/store/system.js'
import { arLangCheck } from '@/utils/arLangCheck'

import { newLoginUser } from '@/service/login.api'
import { sellerInfo } from '@/service/shop.api.js'
import { openService, trim } from '@/utils/index.js'
import NumberCodeDialog from '@/components/number-code-dialog/index.vue'

import { useChatStore } from "@/store/chat.js";

const isArLang = arLangCheck()

const { t, locale } = useI18n()
const userStore = useUserStore()
const systemStore = useSystemStore()
const router = useRouter()
const mode = import.meta.env.MODE

const contentBg = ref(new URL('@/assets/image/login/bg.png', import.meta.url))
if (mode === 'familyShop') {
  contentBg.value = new URL('@/assets/image/login/bg_familyShop.png', import.meta.url)
}

if (mode === 'sm') {
  contentBg.value = new URL('@/assets/image/login/bg_sm.png', import.meta.url)
}

const showAgree = computed(() => {
  return ['familyMart'].includes(mode)
})

const arrowIcon = new URL('@/assets/image/icon/icon_arrow_down.png', import.meta.url)

const langIcon = computed(() => {
  const key = locale.value || 'en'
  const langObj = langData.find(item => item.key === key)
  return langObj.image
})

const appData = computed(() => {
  // const appObj = logoData.find(item => item.key === mode)
  const appObj = logoData.find(item => {
    const key = item.key === 'mbuy' ? 'argos' : item.key
    return key === mode
  })
  return appObj ? appObj : logoData[0]
})

const img1 = new URL('@/assets/image/verify/01.png', import.meta.url)
const img2 = new URL('@/assets/image/verify/02.png', import.meta.url)
const img3 = new URL('@/assets/image/verify/03.png', import.meta.url)
const img4 = new URL('@/assets/image/verify/04.png', import.meta.url)
const img5 = new URL('@/assets/image/verify/05.png', import.meta.url)
const vcodeImgs = [img1.href, img2.href, img3.href, img4.href, img5.href]
const vcodeShow = ref(false)

const typeTab = ['email', 'phoneNum']
const activeType = ref(0)
const submitLoading = ref(false)
const storeAreaCode = localStorage.getItem('areaCode') ? localStorage.getItem('areaCode') : 44
const codeNum = ref(storeAreaCode)
const formData = reactive({
  username: '',
  password: ''
})

const typeChange = (index) => {
  if (index !== activeType.value) {
    activeType.value = index
    const storeName = activeType.value == 0 ? 'storeUserName' : 'storeMobile'
    const storeUserName = localStorage.getItem(storeName)
    formData.username = storeUserName || ''
    formData.password = ''
  }
}

const numberCodeVisible = ref(false)

const submitHandle = () => {
  const nameTips = activeType.value === 0 ? 'entryEmail' : 'entryPhone'
  formData.username = trim(formData.username)
  if (formData.username === '') {
    Toast(t(nameTips))
    return false
  }
  if (formData.password === '') {
    Toast(t('entryPassword'))
    return false
  }

  if (formData.password.length < 6 || formData.password.length > 20) {
    Toast(t('setPasswordTips'))
    return false
  }

  if (showAgree.value && !agreeChecked.value) {
    Toast(`${t('我已阅读并同意')}《${t('用户协议')}》`)
    return false
  }

  if (['hive', 'argos'].includes(mode)) {
    vcodeSuccess()
  } else {
    if (['tiktok-wholesale'].includes(mode)) {
      numberCodeVisible.value = true
    } else {
      vcodeShow.value = true
    }
  }
}

const vcodeSuccess = () => {
  vcodeShow.value = false
  submitLoading.value = true

  newLoginUser({
    username: activeType.value == 0 ? formData.username : `${codeNum.value} ${formData.username}`,
    password: formData.password
  }).then(async (res) => {
    // 保存用户信息
    localStorage.removeItem('storeUserName')
    localStorage.removeItem('storeMobile')

    const storeName = activeType.value == 0 ? 'storeUserName' : 'storeMobile'
    localStorage.setItem(storeName, formData.username)
    localStorage.setItem('loginType', activeType.value)

    await userStore[GET_USERINFO](res)
    await sellerInfo().then(infores => {
      if (infores.id) {
        localStorage.setItem('sellerId', infores.id)
      } else {
        localStorage.removeItem('sellerId')
      }
    }).catch(() => {
      submitLoading.value = false
    })
    
    submitLoading.value = false
    // 公告弹窗
    systemStore.setShowNotic(true)
    // 全局信息获取
    document.dispatchEvent(new CustomEvent('getMoneyInfoHandle'))

    // IM初始化
    const chatStore = useChatStore()
    chatStore.setChatHandle()

    Toast.success(t('loginSuc'))
    router.push('/shop')
  }).catch((err) => {
    submitLoading.value = false
    console.log(err)
  })
}

const goRegister = () => {
  // router.push('/register')
  const {hostname, origin} = window.location
  const href = hostname === 'localhost' ? 'https://www.catvg.xyz/promote/#/' : `${origin}/promote/#/`
  const hrefUrl = `${href}?lang=${locale.value}`
  
  if (window.plus) {
    window.plus.runtime.openURL(hrefUrl)
  } else if (window.webkit) {
    window.webkit.messageHandlers.openWindow.postMessage({url: hrefUrl})
  } else {
    window.open(hrefUrl)
  }
}

const agreeChecked = ref(false)
const agreeVisible = ref(false)

onMounted(() => {
  userStore.logout()
})

nextTick(() => {
  const loginType = localStorage.getItem('loginType')
  activeType.value = loginType ? Number(loginType) : 0

  const storeName = activeType.value == 0 ? 'storeUserName' : 'storeMobile'
  const storeUserName = localStorage.getItem(storeName)
  formData.username = storeUserName || ''
})
</script>

<style lang="scss" scoped>
.login-register-content {
  width: 100%;
  min-height: 100vh;
  background-position: center top;
  background-repeat: no-repeat;
  background-size: cover;
  background-attachment: fixed;
  padding: 0 15px;
  padding-bottom: 20px;
  padding-top: calc(8vh + 60px);
  box-sizing: border-box;
  background-color: #1e1e1e;
  color: #fff;
  > .header-content {
    width: 100%;
    height: 60px;
    padding: 0 15px;
    position: fixed;
    top: 0;
    left: 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    > h2 {
      font-size: 24px;
      font-weight: bold;
    }
    > .language {
      display: flex;
      align-items: center;
      &.is-ar {
        > img {
          &:last-child {
            margin-left: 0;
          }
          &:first-child {
            margin-left: 6px;
          }
        }
      }
      > img {
        &:first-child {
          width: 24px;
          height: 24px;
        }
        &:last-child {
          width: 10px;
          margin-left: 6px;
        }
      }
    }
  }
  > .logo-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 8vh;
    > img {
      width: 72px;
      height: 72px;
    }
    > h2 {
      font-size: 24px;
      font-weight: bold;
      margin-top: 8px;
    }
  }
  > .type-tab {
    overflow: hidden;
    > .item {
      min-width: 80px;
      height: 34px;
      padding: 0 10px;
      text-align: center;
      line-height: 34px;
      font-size: 12px;
      border-radius: 4px;
      margin-right: 10px;
      background-color: #fff;
      color: #333;
      float: left;
      &:last-child {
        margin-right: 0;
      }
      &.active {
        background-color: var(--site-main-color);
        color: #fff;
      }
    }
  }
  > .form-content {
    margin-top: 24px;
    > .item {
      margin-top: 20px;
      &:first-child {
        margin-top: 0;
      }
      > .title {
        font-size: 12px;
        margin-bottom: 10px;
      }
    }

    > .link-content {
      font-size: 12px;
      margin-top: 10px;
      width: 100%;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      &.is-ar {
        > p {
          &:first-child {
            padding-left: 20px;
            padding-right: 0;
          }
        }
      }
      > p {
        line-height: 1.5;
        &:first-child {
          flex: 1;
          padding-right: 20px;
        }
        &:last-child {
          max-width: 40%;
        }
      }
      .link {
        color: #1D91FF;
      }
    }
    > .btn {
      margin-top: 20px;
    }
  }
}

.van-button--custom {
  color: #fff;
  background: var(--site-main-color) !important;
}

.agree-content {
  position: relative;
  margin-top: 10px;
  &.is-ar {
    > .check {
      left: calc(100% - 16px);
    }
  }
  > .check {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    position: absolute;
    left: 0;
    top: 2px;
  }
  > p {
    font-size: 12px;
    line-height: 21px;
    text-indent: 23px;
    .link {
      color: #1D91FF;
    }
  }
}
</style>
