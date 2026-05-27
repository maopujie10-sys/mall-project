<template>
  <div :style="{'background-image': 'url('+ contentBg.href +')'}" class="login-register-content">
    <Vcode :successText="t('vertifyPass')" :failText="t('vertifuFail')" :sliderText="t('vertifyTips')" :imgs="vcodeImgs" :show="vcodeShow" @success="vcodeSuccess" />

    <div class="header-content">
      <h2>{{ t('register') }}</h2>
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
      <div class="item">
        <div class="title">{{ t('repassword') }}</div>
        <div class="input-content">
          <input-item v-model="formData.password1" type="password" :placeholder="t('surePassword')" clear show-password />
        </div>
      </div>
      <div class="link-content" :class="{'is-ar': isArLang}">
        <p></p>
        <p>{{ t('hasAccount') }} <span class="link" @click="goLogin">{{ t('goLogin') }}</span></p>
      </div>

      <div class="btn">
        <van-button type="custom" :loading="submitLoading" block @click="submitHandle">{{ t('register') }}</van-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from 'vue';
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Toast } from 'vant'
import { logoData } from './../login/config'
import InputItem from '@/components/input-item/index.vue'
import Vcode from 'vue3-puzzle-vcode'

import { GET_USERINFO } from '@/store/types.store'
import { useUserStore } from '@/store/user'
import { arLangCheck } from '@/utils/arLangCheck'

import { _registerUser } from '@/service/login.api'
import { sellerInfo } from '@/service/shop.api.js'

const isArLang = arLangCheck()

const { t, locale } = useI18n()
const userStore = useUserStore()
const router = useRouter()
const mode = import.meta.env.MODE

const contentBg = ref(new URL('@/assets/image/login/bg.png', import.meta.url))
if (mode === 'familyShop') {
  contentBg.value = new URL('@/assets/image/login/bg_familyShop.png', import.meta.url)
}

const appData = computed(() => {
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
  password: '',
  password1: ''
})

const typeChange = (index) => {
  if (index !== activeType.value) {
    activeType.value = index
    formData.username = ''
    formData.password = ''
    formData.password1 = ''
  }
}

const submitHandle = () => {
  const emailReg = /^[A-Za-z0-9\u4e00-\u9fa5]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/
  const nameTips = activeType.value === 0 ? 'entryEmail' : 'entryPhone'
  if (formData.username === '') {
    Toast(t(nameTips))
    return false
  }

  if (activeType.value === 0 && !emailReg.test(formData.username)) {
    Toast(t('请输入正确的邮箱地址'));
    return
  }

  if (activeType.value === 1 && !/^[0-9]+$/.test(formData.username)) {
    Toast(t('请输入正确的手机号码'));
    return
  }

  if (formData.password === '') {
    Toast(t('entryPassword'))
    return false
  }

  const reg = /^[A-Za-z0-9!@#$%^&*_()<>.?\/\\{}[\]|,~+:;']+$/
  if (!reg.test(formData.password) || formData.password.length < 6 || formData.password.length > 20) {
      Toast(t('setPasswordTips'))
      return false
  }

  if (formData.password1 === '') {
    Toast(t('surePassword'))
    return false
  }
  if (formData.password !== formData.password1) {
    Toast(t('noSamePassword'))
    return false
  }
  vcodeShow.value = true
}

const vcodeSuccess = () => {
  vcodeShow.value = false
  submitLoading.value = true

  _registerUser({
    username: activeType.value == 0 ? formData.username : `${codeNum.value} ${formData.username}`,
    password: formData.password,
    confirmPassword: formData.password1,
    re_password: formData.password1,
    type: activeType.value == 0 ? 2 : 1
  }).then(async (res) => {
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
    Toast.success(t('registerSuccess'))
    router.push('/shop')
  }).catch((err) => {
    submitLoading.value = false
    console.log(err)
  })
}

const goLogin = () => {
  router.back()
}
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
  padding-top: 8vh;
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
      > p {
        line-height: 1.5;
        &:last-child {
          flex: 1;
          text-align: right;
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
  background-color: var(--site-main-color);
  border-color: var(--site-main-color);
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
