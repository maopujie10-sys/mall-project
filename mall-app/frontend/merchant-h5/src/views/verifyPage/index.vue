<template>
  <div class="verify-content">
    <fx-header :fixed="true">
      <template #title>
        {{ t('身份验证') }}
      </template>
    </fx-header>
    <div style="height: 46px;" />
    <div class="info-content">
      <div class="info-item">
        <h2 class="gap">{{ pageType === 1 ? t('手机验证') : t('邮箱验证') }}</h2>
        <p>{{ t('为了保障您的账号安全，请验证后进行下一步操作') }}</p>
      </div>
      <div class="info-item">
        <p class="gap">{{ pageType === 1 ? t('当前绑定手机号') : t('当前绑定邮箱') }}</p>
        <h2><span v-if="pageType === 1">(+{{ phoneCode }})</span>{{ formeateUser(userShowVer, false) }}</h2>
      </div>
      <div class="code-content" :class="{'is-ar': isArLang}">
        <van-field v-model="codeNum" type="tel" label="" :placeholder="t('entryVerifyCode')" />
        <div class="btn" :class="{'is-ar': isArLang}">
          <van-button type="primary" @click="senCode">{{ t('sendVerifyCode') }}<template v-if="time">({{ time }})s</template></van-button>
        </div>
      </div>
      <div class="change-ver-type">
        <van-icon name="exchange" />
        <p @click="changeVerType">{{ pageType === 1 ? t('切换为邮箱验证') : t('切换为手机验证') }}</p>
      </div>
    </div>
    <div class="submit-content">
      <van-button type="primary" :loading="submitLoading" @click="submitHandle">{{ t('nextStep') }}</van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { Toast } from 'vant';
import { useUserStore } from '@/store/user'
import { arLangCheck } from '@/utils/arLangCheck'
import { formeateUser } from '@/utils'
import { _sendVerifyCode } from '@/service/login.api'
import { beforeBindVer } from '@/service/user.api'
const userStore = useUserStore()
const isArLang = arLangCheck()

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const pageType = ref(1)
const verifyType = ref(1)
const phoneCode = ref('44')
const codeNum = ref('')
const time = ref(0)
const timer = ref(null)
const submitLoading = ref(false)
pageType.value = route.query && route.query.type ? Number(route.query.type) : 1
verifyType.value = route.query && route.query.verType ? Number(route.query.verType) : 1
onMounted(() => {
  clearInterval(timer.value)
  timer.value = null
})


const userShowVer = computed(() => {
  if (!userStore.userInfo.token) {
    router.push('/login')
  } else {
    const { email, phone } = userStore.userInfo
    let showTxt = ''
    if (pageType.value === 1) { // 手机号
      if (phone) {
        const phoneArr = phone.split(' ')
        if (phoneArr.length === 2) {
          phoneCode.value = phoneArr[0]
          showTxt = phoneArr[1]
        } else {
          showTxt = phoneArr[0]
        }
      }
    } else { // 邮箱
      showTxt = email || ''
    }
    return showTxt
  }
})

const senCode = () => {
  if (time.value > 0) {
    return false
  }

  const { email, phone } = userStore.userInfo
  Toast.loading({
    duration: 0,
    forbidClick: true
  })
  _sendVerifyCode({
    target: pageType.value === 1 ? phone : email
  }).then(() => {
    Toast(t('sendSuccess'));
    time.value = 60
    timer.value = setInterval(() => {
      if (time.value > 0) {
        time.value = time.value - 1
      } else {
        time.value = 0
        clearInterval(timer.value)
        timer.value = null
      }
    }, 1000);
  }).catch(() => {
    Toast.clear()
  })
}

const changeVerType = () => {
  const { email, phone } = userStore.userInfo
  const type = pageType.value === 1 ? 2 : 1
  if (type === 2 && !email) {
    Toast(t('暂未绑定邮箱，无法进行邮箱验证'))
    return false
  }
  if (type === 1 && !phone) {
    Toast(t('暂未绑定手机号，无法进行手机验证'))
    return false
  }
  pageType.value = type
}

const submitHandle = () => {
  if (codeNum.value === '') {
    Toast(t('entryVerifyCode'))
    return
  }

  submitLoading.value = true
  const { email, phone } = userStore.userInfo

  const params = {
    target: pageType.value === 1 ? phone : email,
    verifcode: codeNum.value
  }
  if (pageType.value === 1) {
    params.phone = phone
  } else {
    params.email = email
  }

  beforeBindVer(params).then(res => {
    submitLoading.value = false
    router.push(`/bindVerify?type=${verifyType.value}&reset=1&verifyCode=${res.verifyCode}`)
  }).catch(() => {
    submitLoading.value = false
  })
}

</script>

<style lang="scss" scoped>
.verify-content {
  min-height: 100vh;
  background-color: #fff;
}

.info-content {
  padding: 0 20px;
  color: #333;
  > .info-item {
    margin-top: 30px;
    &:last-child {
      margin-top: 20px;
    }
    > .gap {
      margin-bottom: 10px;
    }
    h2 {
      font-size: 20px;
      font-weight: 700;
    }
    p {
      font-size: 14px;
    }
  }
  .code-content {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 35px;
    &.is-ar {
      :deep(.van-field__control) {
        text-align: right;
      }
    }
    .van-cell {
      width: 185px;
      height: 44px;
      border: 1px solid #ddd;
      border-radius: 4px;
      &::after {
        border: none;
      }
    }
    > .btn {
      flex: 1;
      padding-left: 15px;
      &.is-ar {
        padding-right: 15px;
        padding-left: 0;
      }
      .van-button {
        width: 100%;
        height: 44px;
        border-radius: 4px;
        background-color: var(--site-main-color);
        border-color: var(--site-main-color);
      }
    }
  }
  > .change-ver-type {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    color: var(--site-main-color);
    margin-top: 10px;
    > p {
      font-size: 14px;
      padding-left: 5px;
      font-weight: bold;
    }
  }
}

.submit-content {
  width: 100%;
  position: fixed;
  left: 0;
  bottom: 60px;
  padding: 0 20px;
  .van-button {
    width: 100%;
    height: 44px;
    border-radius: 4px;
    background-color: var(--site-main-color);
    border-color: var(--site-main-color);
  }
}
</style>
