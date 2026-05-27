<template>
  <div :class="{'active': modelValue}" class="login-dialog">
    <div class="login-content">
      <div class="dialog-title">
        {{ t('卖家登录') }}
      </div>
      <div class="type-tab">
        <div v-for="(item, index) in typeTab" :key="index" :class="{'active': index === activeType}" class="item" @click="typeChange(index)">{{ t(item) }}</div>
      </div>
      <div class="form-content">
        <div v-if="activeType === 0" class="item">
          <input-item v-model="formData.username" type="text" :is-turn="true" :placeholder="t('entryEmail')" clear />
        </div>
        <div v-if="activeType === 1" class="item">
          <input-item v-model="formData.username" v-model:codeNum="codeNum" type="tel" :is-turn="true" :placeholder="t('entryPhone')" clear area-code />
        </div>
        <div class="item">
          <input-item v-model="formData.password" type="password" :is-turn="true" :placeholder="t('entryPassword')" clear show-password />
        </div>
        <div class="link-content" :class="{'is-ar': isArLang}">
          <p>{{ t('如果您没有账号') }}, <span class="link" @click="goRegister">{{ t('点击注册') }}</span></p>
          <p @click="openService(true)" class="link">{{ t('forgetPassword') }}</p>
        </div>

        <div class="btn">
          <van-button type="custom" :loading="submitLoading" block @click="submitHandle">{{ t('login') }}</van-button>
        </div>
      </div>
    </div>
    <div class="login-bg" @click="closeDialog"></div>
  </div>
</template>

<script setup name="LoginDialog">
import { ref, reactive, watch } from 'vue';
import { Toast } from 'vant'
import { useI18n } from 'vue-i18n'
import { useUserStore } from '@/store/user'
import { GET_USERINFO } from '@/store/types.store'
import { arLangCheck } from '@/utils/arLangCheck'
import { openService } from '@/utils/index.js'
import InputItem from '@/components/input-item/index.vue'
import { newLoginUser } from '@/service/login.api'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const { t, locale } = useI18n()
const userStore = useUserStore()
const isArLang = arLangCheck()
const emits = defineEmits(['update:modelValue', 'done'])

const closeDialog = () => {
	emits('update:modelValue', false)
}

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
    formData.username = ''
    formData.password = ''
  }
}

const goRegister = () => {
  const {hostname, origin} = window.location
  const href = hostname === 'localhost' ? 'https://www.catvg.xyz/promote/#/' : `${origin}/promote/#/`
  window.open(`${href}?lang=${locale.value}`)
}

const submitHandle = () => {
  const nameTips = activeType.value === 0 ? 'entryEmail' : 'entryPhone'
  if (formData.username === '') {
    Toast(t(nameTips))
    return false
  }
  if (formData.password === '') {
    Toast(t('entryPassword'))
    return false
  }

  submitLoading.value = true

  newLoginUser({
    username: activeType.value == 0 ? formData.username : `${codeNum.value} ${formData.username}`,
    password: formData.password
  }).then(async (res) => {
    await userStore[GET_USERINFO](res)
    Toast(t('loginSuc'))
    submitLoading.value = false
    setTimeout(() => {
      closeDialog()
      emits('done')
    }, 1500)
  }).catch((err) => {
    submitLoading.value = false
    console.log(err)
  })
}

watch(
  () => props.modelValue,
  (val) => {
    if (!val) {
      activeType.value = 0
      formData.username = ""
      formData.password = ""
    }
  }
)
</script>

<style lang="scss" scoped>
.login-dialog {
  width: 100%;
  height: 100vh;
  pointer-events: none;
  z-index: 98;
  opacity: 0;
  position: fixed;
  top: 0;
  left: 0;
  > .login-content {
    width: 540px;
    position: fixed;
    top: 20%;
    left: 50%;
    margin-left: -270px;
    animation-duration: .75s;
    z-index: 99;
    background-image: url('./../../../../assets/activity/turntable/login-bg.png');
    background-repeat: no-repeat;
    background-size: 100% 100%;
    background-position: center top;
    padding: 0 40px;
    padding-top: 20px;
    padding-bottom: 60px;
    display: flex;
    flex-direction: column;
    align-items: center;
    > .dialog-title {
      width: 204px;
      height: 70px;
      background-image: url('./../../../../assets/activity/turntable/login-title.png');
      background-repeat: no-repeat;
      background-size: 100% 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      padding-top: 10px;
      background-position: center top;
      position: relative;
      color: #FFDE6D;
      font-size: 16px;
      top: -45px;
    }
    > .type-tab {
      width: 100%;
      display: flex;
      align-items: center;
      padding: 0 10px;
      > .item {
        color: #BDAAFF;
        cursor: pointer;
        user-select: none;
        margin-right: 30px;
        &.active {
          color: #fff;
        }
      }
    }
    > .form-content {
      width: 100%;
      margin-top: 30px;
      > .item {
        color: #333;
        margin-bottom: 25px;
      }
      > .link-content {
        font-size: 12px;
        margin-top: 10px;
        width: 100%;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        color: #fff;
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
          color: #FFE59A;
          cursor: pointer;
          &:hover {
            color: #EECB88;
          }
        }
      }
      > .btn {
        margin-top: 40px;
      }
    }
  }
  > .login-bg {
    position: fixed;
    left: 0;
    top: 0;
    width: 100%;
    height: 100vh;
    background-color: rgba(0, 0, 0, .4);
    z-index: 98;
    opacity: 0;
    transition: all 0.3s ease;
  }
  &.active {
    pointer-events: auto;
    opacity: 1;
    > .login-content {
      animation-name: bounceInUp;
    }
    > .login-bg {
      opacity: 1;
    }
  }
}

.van-button--custom {
  color: #8F6618;
  background: #EECB88;
  border-color: #F2DB9C;
  border-radius: 44px;
}

@media (max-width: 1180px) {
  .login-dialog {
    > .login-content {
      width: 80vw;
      margin-left: -40vw;
      padding: 0 20px;
      padding-top: 0;
      padding-bottom: 40px;
      > .dialog-title {
        width: 35vw;
        height: 12vw;
        font-size: 3.2vw;
        padding-top: 1vw;
        top: -5vw;
      }
      > .form-content {
        margin-top: 20px;
        > .item {
          margin-bottom: 20px;
        }
        > .btn {
          margin-top: 20px;
        }
      }
    }
  }
}
</style>
