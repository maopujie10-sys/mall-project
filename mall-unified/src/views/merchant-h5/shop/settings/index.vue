<template>
  <div class="page-main-content">
    <fx-header :fixed="true">
      <template #title>
        {{ t('店铺设置') }}
      </template>
    </fx-header>
    <div style="height: 46px;" />
    
    <div class="settings-nav-content">
      <div v-for="(item, index) in navData" :key="index" class="item" @click="hrefHandle(item)">
        <div class="icon">
          <img :src="item.icon.href" alt="" />
        </div>
        <div class="title">{{ t(item.title) }}</div>
        <van-icon name="arrow" />
      </div>
    </div>
  </div>
</template>

<script setup name="ShopSettings">
import { computed, ref, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { Toast } from 'vant'
import { openPage } from '@/utils'
import { useUserStore } from '@/store/user.js'
import { sysParaSign } from '@/service/shop.api.js'
import cloneDeep from 'lodash.clonedeep'

import {
  shopSettingsNavData
} from './../config'

const { t } = useI18n()
const userStore = useUserStore()

const signPdfUrl = computed(() => {
  return userStore.userInfo?.signPdfUrl || ''
})

const navData = ref([])
const data = cloneDeep(shopSettingsNavData)
const mode = import.meta.env.MODE

if (['argos', 'argos2', 'int'].includes(mode)) {
  const index = data.findIndex(item => item.title === 'soical')
  data.splice(index, 1)
}

navData.value = data

const hrefHandle = (data) => {
  if (data.href === '/shop/contract') {
    if (signPdfUrl.value) {
      openPage(data.href)
    } else {
      openPage('/shop/contractSign')
    }
  } else {
    openPage(data.href)
  }
}

nextTick(async () => {
  Toast.loading({
    duration: 0
  })
  await userStore.getUserInfo(true)
  
  await sysParaSign().then(res => {
    const isSign = (typeof res.sellerSign) === 'string' ? JSON.parse(res.sellerSign) : res.sellerSign
    if (isSign) {
      navData.value.push({
        title: '电子合同',
        icon: new URL('@/assets/image/shop/icon_30.png', import.meta.url),
        href: '/shop/contract'
      })
    }
    Toast.clear()
  }).catch(() => {
    Toast.clear()
  })
})
</script>

<style lang="scss" scoped>
.settings-nav-content {
  padding: 7px 15px;
  > .item {
    width: 100%;
    height: 63px;
    display: flex;
    align-items: center;
    background-color: #fff;
    padding: 0 13px;
    margin-bottom: 7px;
    border-radius: 4px;
    > .icon {
      width: 30px;
      height: 30px;
    }
    > .title {
      flex: 1;
      padding: 0 12px;
      font-size: 14px;
      color: #000;
    }
  }
}
</style>
