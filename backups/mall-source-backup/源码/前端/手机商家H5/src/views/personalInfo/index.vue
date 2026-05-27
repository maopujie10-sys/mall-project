<template>
  <div class="h-full w-full">
    <fx-header>
      <template #title>
        {{ $t('personalInformation') }}
      </template>
    </fx-header>
    <div class="flex items-center justify-between bg-white h-20 img" @click="() => router.push('/changeAvatar')">
      <div style="color: #000">{{$t('avatar')}}</div>
      <div class="avatar-content">
        <div class="avatar">
          <img :src="defaultAvatar.avatar" alt="">
        </div>
        <van-icon name="arrow" />
      </div>
    </div>
    <van-cell-group>
      <van-cell style="min-height: 3.125rem" :title="$t('realName')" is-link :to="'/name'">
        <div class="verify-info-content" :class="{'is-ar': isArLang}">
          <p v-if="userInfo.name && kycStatus === 2">{{ formeateUser(userInfo.name, false) }}</p>
          <div v-if="kycStatusTxt" class="icon-content">
            <img :src="kycStatus === 2 ? defaultAvatar.verifyIcon2: (kycStatus === 1 ? defaultAvatar.verifyIcon3 : defaultAvatar.verifyIcon1)" alt="">
            <p>{{ t(kycStatusTxt) }}</p>
          </div>
        </div>
      </van-cell>
      <!-- <van-cell v-if="!isFM" style="min-height: 3.125rem" :title="notAllowPhoneClick ? $t('phoneNum') : $t('phoneVerify')" :is-link="!notAllowPhoneClick" :to="verifyRoute(1, notAllowPhoneClick)">
        <div class="verify-info-content" :class="{'is-ar': isArLang}">
          <p>{{ userInfo.phone ? formeateUser(userInfo.phone, false) : t('未设置') }}</p>
          <div v-if="userInfo.phone && !notAllowPhoneClick" class="icon-content">
            <img :src="userInfo.phoneverif ? defaultAvatar.verifyIcon2: defaultAvatar.verifyIcon1" alt="">
            <p>{{ userInfo.phoneverif ? t('已认证') : t('未认证') }}</p>
          </div>
          <div v-if="userInfo.phone && notAllowPhoneClick" class="icon-content">
            <img :src="defaultAvatar.verifyIcon2" alt="">
            <p>{{ t('已认证') }}</p>
          </div>
        </div>
      </van-cell>
      <van-cell v-if="!isFM" style="min-height: 3.125rem" :title="notAllowEmailClick ? $t('邮箱') : $t('emailVerify')" :is-link="!notAllowEmailClick" :to="verifyRoute(2, notAllowEmailClick)">
        <div class="verify-info-content" :class="{'is-ar': isArLang}">
          <p>{{ userInfo.email ? formeateUser(userInfo.email, false) : t('未设置') }}</p>
          <div v-if="userInfo.email && !notAllowEmailClick" class="icon-content">
            <img :src="userInfo.emailverif ? defaultAvatar.verifyIcon2: defaultAvatar.verifyIcon1" alt="">
            <p>{{ userInfo.emailverif ? t('已认证') : t('未认证') }}</p>
          </div>
          <div v-if="userInfo.email && notAllowEmailClick" class="icon-content">
            <img :src="defaultAvatar.verifyIcon2" alt="">
            <p>{{ t('已认证') }}</p>
          </div>
        </div>
      </van-cell> -->
      <van-cell v-if="!isFM" style="min-height: 3.125rem" :title="$t('changeFunsPassword')" :value="userInfo.safeword ? '' : t('未设置')" is-link :to="userInfo.safeword ? '/changeFundsPassword' : '/fundsPasswordSettings'"  />
      <van-cell v-if="!isFM" style="min-height: 3.125rem" :title="$t('changeLoginPassword')" is-link to="/changePassword" />
    </van-cell-group>
  </div>
</template>

<script setup>
import {computed, reactive, watch, ref} from "vue";
import { useRouter } from 'vue-router';
import { useUserStore } from '@/store/user';
import { useI18n } from 'vue-i18n';
import { _getIdentify } from '@/service/user.api.js'
import { Toast } from 'vant';
import { formeateUser } from '@/utils'
import { arLangCheck } from '@/utils/arLangCheck'

const isArLang = arLangCheck()
const router = useRouter()
const userStore = useUserStore()
const { t } = useI18n();
const mode = import.meta.env.MODE

const defaultAvatar = reactive({
  avatar: new URL('@/assets/imgs/me/defaultAvatar.png', import.meta.url),
  verifyIcon1: new URL('@/assets/imgs/me/fail1.png', import.meta.url),
  verifyIcon2: new URL('@/assets/imgs/me/success1.png', import.meta.url),
  verifyIcon3: new URL('@/assets/imgs/me/wait1.png', import.meta.url)
})

const isFM = computed(() => {
  return ['familyMart'].includes(mode)
})

const notAllowPhoneClick = computed(() => {
  return [].includes(mode)
})

const notAllowEmailClick = computed(() => {
  return ['sm'].includes(mode)
})

const modifyPhoneNotCode = computed(() => {
  return ['sm', 'familyShop'].includes(mode)
})

// 用户信息
const userInfo = computed(() => {
  let obj = {}
  if (!userStore.userInfo.token) {
    router.push('/login')
  } else {
    obj = { ...userStore.userInfo }
  }
  return obj
})

// 认证方式链接
const verifyRoute = (type, flag) => {
  if (!flag) {
    let typeNum = 1
    let goCertified = false
    if (type === 1) {
      typeNum = userInfo.value.phone ? 1 : 2
      goCertified = !userInfo.value.phoneverif && userInfo.value.phone
      if (modifyPhoneNotCode.value) {
        return 'changePhone'
      }
    }
    if (type === 2) {
      typeNum = userInfo.value.email ? 2 : 1
      goCertified = !userInfo.value.emailverif && userInfo.value.email
    }
    return goCertified ? `certified?type=${type}` : `verifyPage?type=${typeNum}&verType=${type}`
  }
}

// 头像
watch(userInfo, async (val) => {
  if (isNaN(Number(val.avatar))) {
    defaultAvatar.avatar = val.avatar
  } else {
    await import(`./../../assets/image/userAvatar/${userStore.userInfo.avatar}.png`).then((res) => {
      defaultAvatar.avatar = res.default
    })
  }
}, {
  immediate: true,
  deep: true
})

Toast.loading({
  duration: 0,
  message: t('loading'),
  forbidClick: true
})
const kycStatusTxt = ref('')
const kycStatus = ref(0)
_getIdentify().then(res => {
  const status = Number(res.status)
  kycStatus.value = status
  switch (status) {
    case 0:
      kycStatusTxt.value = t('未认证')
      break
    case 1:
      kycStatusTxt.value = t('审核中')
      break
    case 2:
      kycStatusTxt.value = t('已认证')
      break
    case 3:
      kycStatusTxt.value = t('审核失败')
      break
  }
})
</script>

<style lang="scss" scoped>
.img {
  padding: var(--van-cell-group-inset-padding);
}
::v-deep(.van-cell__title) {
  color: #333;
}
.avatar-content {
  display: flex;
  align-items: center;
  > .avatar {
    width: 3.75rem;
    height: 3.75rem;
    border-radius: 50%;
    overflow: hidden;
    > img {
      width: 100%;
      height: auto;
    }
  }
  .van-icon {
    color: #969799;
    margin-left: 2px;
  }
}
.verify-info-content {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: nowrap;
  overflow: hidden;
  &.is-ar {
    > p {
      padding-left: 8px;
      padding-right: 0;
    }
    > .icon-content > img {
      margin-right: 0;
      margin-left: 2px;
    }
  }
  > p {
    flex: 1;
    padding-right: 8px;
    line-height: 16px;
    // text-overflow: ellipsis;
    // overflow: hidden;
    // white-space: nowrap;
  }
  > .icon-content {
    display: flex;
    align-items: center;
    flex-wrap: nowrap;
    min-width: 60px;
    > img {
      width: 16px;
      height: auto;
      margin-right: 2px;
    }
    > p {
      white-space: nowrap;
    }
  }
}
</style>
