<template>
  <div>
    <fx-header>
      <template #title>{{ t('支付成功') }}</template>
    </fx-header>

    <div class="center">
      <van-icon name="checked" color="#0ECB81"/>
      <p>{{ t('支付成功') }}</p>
      <div class="phone">{{ $t('如有疑问，请立即') }}<span @click="openService">{{ $t('联系客服') }}</span></div>
    </div>

    <div class="bttn">
      <div class="one" @click="back">{{ $t('回到首页') }}</div>
      <div class="two" @click="look">{{ $t('查看订单') }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, ref } from 'vue'
import { useRoute } from "vue-router";
import {useI18n} from 'vue-i18n'
import { openService } from '@/utils/index.js'
import {
  sellerInfo
} from '@/service/shop.api.js'
const route = useRoute()

const {t} = useI18n()

const look = () => {
  const orderId = route.query.id
  router.push({
    path: '/orderdeails',
    query: {
      id: orderId,
    }
  })
}

const back = () => {
  router.push('/my')
}

const sellerData = ref({})

// 平台客服
const isMc = computed(() => {
  const data = ['metashop']
  const mode = import.meta.env.MODE
  return data.includes(mode)
})

nextTick(() => {
  // 基础信息
  sellerInfo().then(res => {
    sellerData.value = res || {}
  })
})
</script>

<style lang="scss" scoped>
.center {
  text-align: center;
  padding: 30px 0px;

  i {
    font-size: 70px;
  }

  p {
    font-size: 18px;
    height: 50px;
    line-height: 50px;
  }

  .phone {
    font-size: 13px;
    color: #666;
    margin-top: 30px;

    span {
      padding-left: 10px;
      color: #1552F0;
    }
  }
}

.bttn {
  padding: 10px;
  box-sizing: border-box;

  div {
    width: 100%;
    height: 40px;
    line-height: 40px;
    text-align: center;
    margin-bottom: 10px;
    border-radius: 5px;
  }

  div.one {
    background: var(--site-main-color);
    color: #fff;
  }

  div.two {
    border: 1px solid var(--site-main-color);
    color: var(--site-main-color);
  }
}
</style>
