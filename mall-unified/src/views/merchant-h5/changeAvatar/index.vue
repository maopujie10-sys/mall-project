<template>
  <div>
    <fx-header :fixed="true">
      <template #title>
        {{ $t('avatar') }}
      </template>
      <template #right>
        <div @click="saveHandle" class="save-btn">{{ $t('save') }}</div>
      </template>
    </fx-header>
    <div style="height: 46px;" />
    <div class="avatar-content">
      <div v-for="(item, index) in avatarData" :key="index" class="item" @click="choiceHandle(index)">
        <img :src="item" alt="">
        <div v-if="index + 1 === currentAvatar" class="check"><van-icon name="success" /></div>
      </div>
    </div>
  </div>
  
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Toast } from 'vant'
import { useUserStore } from '@/store/user'
import { avatarData } from './config'

import { refreshAvatar } from '@/service/user.api.js'

const router = useRouter()
const userStore = useUserStore()
const currentAvatar = ref(1)

if (!userStore.userInfo.token) {
  router.push('/login')
} else {
  const avatar = Number(userStore.userInfo.avatar)
  if (!isNaN(avatar)) {
    currentAvatar.value = avatar
  }
}

const choiceHandle = (index) => {
  if ((index + 1 )!== currentAvatar.value) {
    currentAvatar.value = index + 1
  }
}

const saveHandle = async () => {
  Toast.loading({
    duration: 0,
    forbidClick: true
  })
  
  await refreshAvatar({ idx: currentAvatar.value })
  await userStore.getUserInfo(true)
  router.back()
}

</script>

<style lang="scss" scoped>
.avatar-content {
  width: 100%;
  min-height: calc(100vh - 46px);
  background-color: #fff;
  overflow: hidden;
  padding-top: 20px;
  > .item {
    width: 25vw;
    height: 25vw;
    float: left;
    padding: 4vw;
    position: relative;
    > img {
      border-radius: 50%;
    }
    > .check {
      width: 22px;
      height: 22px;
      border-radius: 50%;
      background-color: var(--site-main-color);
      display: flex;
      align-items: center;
      justify-content: center;
      position: absolute;
      border: 1px solid #fff;
      right: 4vw;
      bottom: 4vw;
      .van-icon {
        color: #fff;
        font-size: 12px;
      }
    }
  }
}

.save-btn {
  color: var(--site-main-color);
}
</style>
