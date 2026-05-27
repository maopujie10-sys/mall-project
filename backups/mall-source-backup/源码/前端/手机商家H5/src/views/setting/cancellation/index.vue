<template>
  <div>
    <fx-header fixed>
      <template #title>
        {{ t('账号注销') }}
      </template>
    </fx-header>
    <div style="height: 46px"></div>
    <div class="cancellation-content">
      <div class="item">
        <ExInput :label="$t('您的账号')" v-model="accountStr" :disabled="true" :clearBtn="false" typeText="text" />
      </div>
      <div class="item">
        <p>{{ t('为什么要离开？') }}</p>
        <van-field
          v-model="reason"
          rows="4"
          autosize
          type="textarea"
          :placeholder="t('pleaseEnter')"
        />
      </div>
      <div class="btn">
        <van-button type="danger" :loading="submitLoading" block @click="submitHandle">{{$t('注销账号')}}</van-button>
      </div>
    </div>

    <van-action-sheet v-model:show="passwordShow" :title="t('请输入交易密码')">
      <div style="height: 22rem">
        <van-password-input
          :length="6"
          :value="cashPassword"
          :focused="showKeyboard"
          @focus="showKeyboard = true"
        />
        <van-number-keyboard
          v-model="cashPassword"
          :show="showKeyboard"
          @blur="showKeyboard = false"
        />
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Toast, Dialog } from 'vant'
import { useI18n } from 'vue-i18n'
import { useUserStore } from '@/store/user'
import { _getBalance, userLogOff } from '@/service/user.api.js'
import ExInput from '@/components/ex-input/index.vue'

const { t } = useI18n()
const router = useRouter()
const userStore = useUserStore()

// 用户信息
const userInfo = computed(() => {
	let obj = {
    username: '***',
    safeword: 0
  }
  if (!userStore.userInfo.token) {
    router.push('/login')
  } else {
    obj = { ...obj, ...userStore.userInfo}
  }
  return obj
})

// 账号
const accountStr = computed(() => {
  const username = userInfo.value.username
  if (userInfo.value.username.indexOf('@') > -1) {
    return username
  } else {
    if (userInfo.value.phone) {
      const arr = userInfo.value.phone.split(' ')
      return `(+${arr[0]}) ${arr[1]}`
    } else {
      return username
    }
  }
})

const passwordShow = ref(false)
const reason = ref('')
const cashPassword = ref('')
const submitLoading = ref(false)

const submitHandle = async () => {
  if (!reason.value) {
    Toast(t('请输入您要注销账号的原因'))
    return false
  }
  submitLoading.value = true
  const walletInfo = await _getBalance()
  // walletInfo.money = 0
  submitLoading.value = false
  if (walletInfo.money > 0) {
    Toast(t('该账号存在可用余额，不可注销！'))
  } else {
    const hasSafeWord = Boolean(userInfo.value.safeword)
    if (hasSafeWord) {
      passwordShow.value = true
      showKeyboard.value = true
    } else {
      requestHandle()
    }
  }
}

const requestHandle = async () => {
  submitLoading.value = true
  passwordShow.value = false
  showKeyboard.value = false
  Dialog.confirm({
    title: t('您确认要注销吗？'),
    message: t('警告！请谨慎操作注销账户，如果您不再使用该账号，可点击【同意注销】，注销后可能几天内无法注册。'),
    confirmButtonColor: '#ee0a24',
    cancelButtonText: t('cancel'),
    confirmButtonText: t('同意注销')
  }).then(() => {
    requestSub()
  }).catch(() => {
    submitLoading.value = false
  })
}

const requestSub = () => {
  const params = {
    account: userInfo.value.username,
    reason: reason.value,
    cashPassword: cashPassword.value || null
  }
  userLogOff(params).then(() => {
    submitLoading.value = false
    Toast.success(t('注销成功'))
    setTimeout(() => {
      userStore.logout()
    }, 1500)
  }).catch(() => {
    cashPassword.value = ''
    submitLoading.value = false
  })
}

const showKeyboard = ref(false)
// 密码输入到6位发送请求
watch(() => cashPassword.value, (val) => {
  if (val.length === 6) {
    Toast.loading('');
    requestSub()

    passwordShow.value = false;
    cashPassword.value = ''
  }
})
</script>

<style lang="scss" scoped>
.cancellation-content {
  padding: 15px;
  min-height: calc(100vh - 46px);
  background-color: #fff;
  > .item {
    margin-bottom: 20px;
    :deep(textarea::-webkit-input-placeholder) {
      color: #868c9a;
    }
    > p {
      font-size: 14px;
      margin-bottom: 10px;
    }
    :deep(.van-field) {
      border: 1px solid #ddd;
      border-radius: 4px;
    }
    :deep(.inputCom) {
      padding-bottom: 0;
      .label {
        font-size: 14px;
      }
      .iptbox {
        margin-top: 10px;
        padding-left: 16px;
        padding-right: 16px;
        border-radius: 4px;
        input {
          font-size: 14px;
          padding-left: 0;
        }
      }
    }
  }
  > .btn {
    padding-top: 20px;
    :deep(.van-button) {
      border-radius: 4px;
    }
  }
}

.popup-title {
  text-align: center;
  padding-top: 15px;
}
.popup-content {
  padding: 50px 30px 0;
}
</style>
