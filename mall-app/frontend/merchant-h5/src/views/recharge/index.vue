<template>
  <div>
    <fx-header fixed>
      <template #title>
        <div>{{ t('recharge') }}</div>
      </template>
      <template #right>
        <div @click="handleRecord">{{ t('rechargeRecord') }}</div>
      </template>
    </fx-header>
    <div style="height: 46px;" />

    <div class="recharge">
      <img :src="Banner" alt="" />

      <div class="tips">
        {{ t('rechargeDescribe') }}
      </div>

      <div class="content">
        <van-cell-group inset>
          <van-cell is-link v-for="item in list" :key="item.id" @click="handleClick(item)">
            <template #title>
              <div class="flex items-center content-item">
                <img :src="item.icon" alt="">
                <div class="color-333" :class="isArLang ? 'mr-2': 'ml-2'">
                  {{ item.text }}
                </div>
              </div>
            </template>
          </van-cell>
        </van-cell-group>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n';
import {useRouter} from 'vue-router';
import {Toast} from 'vant'
import { useUserStore } from '@/store/user'
import {
  exchangeGetBlockChain,
  thirdPartyRecharge
} from '@/service/exchange.api'

import { arLangCheck } from '@/utils/arLangCheck'
import Banner from '@/assets/image/exchange/banner.png'
import USDT from '@/assets/image/exchange/usdt.png'
import USDC from '@/assets/image/exchange/usdc.png'
import ETH from '@/assets/image/exchange/eth.png'
import BTC from '@/assets/image/exchange/btc.png'
import BNB from '@/assets/image/exchange/bnb.png'
import CARD from '@/assets/image/exchange/card.png'
import GCASH from '@/assets/image/exchange/gcash.png'
import MAYA from '@/assets/image/exchange/maya.png'
import WISE from '@/assets/image/exchange/wise.png'

const router = useRouter();
const { t } = useI18n();
const userStore = useUserStore()

const isArLang = arLangCheck()
const mode = import.meta.env.MODE

const iconData = {
  'USDT': USDT,
  'USDC': USDC,
  'ETH': ETH,
  'BTC': BTC,
  'BNB': BNB
}

const list = ref([])

userStore.getUserInfo(true)

Toast.loading({duration: 0, forbidClick: true})
exchangeGetBlockChain().then(async (res) => {
  const storeArr = []
  const data = res || []
  for (let i = 0; i < data.length; i++) {
    const iconName = data[i].coin
    if (!storeArr.includes(iconName)) {
      storeArr.push(iconName)
      list.value.push({
        icon: iconData[iconName],
        text: iconName,
        id: iconName.toLowerCase()
      })
    }
  }

  if (true) {
    list.value.push({
      icon: CARD,
      text: t('银行卡'),
      id: 'card'
    })
  }

  if (['sm'].includes(mode)) {
    list.value.push({
      icon: WISE,
      text: 'Wise',
      id: 'card'
    })
  }

  if (['shop2u'].includes(mode)) {
    await thirdPartyRecharge().then(res => {
      const data = res || []
      if (data.length) {
        for (let i = 0; i < data.length; i++) {
          const productType = data[i].productType.toLowerCase()
          let icon = GCASH
          let text = data[i].productType
          if (productType === 'bank') {
            icon = CARD
            text = t('银行卡')
          }
          if (productType === 'maya') {
            icon = MAYA
          }

          list.value.push({
            icon,
            text,
            id: 'bank'
          })
        }
      }
    })
  }

  Toast.clear()
}).catch(() => {
  Toast.clear()
})

const handleRecord = () => {
  router.push({ name: 'RechargeRecord' })
}

const handleClick = (data) => {
  if (data.id === 'card') {
    router.push({ path: `/customerService` })
  } else {
    const queryObj = {
      'GCash': 1,
      'GCash2.0': 2,
      'GCash3.0': 3,
      'Maya': 4,
      'GCash pay': 5,
    }
    const query = Object.keys(queryObj).includes(data.text) ? { g: queryObj[data.text],key:data.text} : {}
    router.push({
      path: `/recharge/${data.id}`,
      query
    })
  }
}
</script>

<style scoped lang="scss">
.recharge {
  padding: 25px 15px 0;
  min-height: calc(100vh - var(--van-nav-bar-height));
  background-color: $background-color;
  text-align: center;

  img {
    width: 100%;
    margin-bottom: 15px;
    max-width: 1000px;
  }

  .tips {
    background: #eff2f6;
    padding: 10px;
    font-size: 14px;
    line-height: 20px;
    color: $text-color-light;
  }

  .content {
    display: block;
    margin-top: 15px;

    .van-cell-group {
      margin: 0;

      :deep(.van-cell) {
        padding: 15px 10px;

        &::after {
          border-color: transparent;
        }
      }
    }

    &-item {

      img {
        width: 28px;
        height: 28px;
        margin-bottom: 0;
      }
    }
  }
}
</style>
