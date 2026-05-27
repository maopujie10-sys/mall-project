<template>
  <div>
    <fx-header :fixed="true">
      <template #title>
        {{ t('查看物流') }}
      </template>
    </fx-header>
    <div style="height: 46px;" />

    <div class="logistics-container">
      <van-empty v-if="!pageLoading && !logData.length" :description="t('noData')"/>
      <div v-if="!pageLoading && logData.length" class="content" :class="{'single': isSingle}">
        <div v-for="item in logData" :key="item.id" class="item">
          <p class="info">{{ t('订单') }}<span>#{{ item.orderId }}#</span>{{ t(item.tipsTxt) }}</p>
          <p class="time">{{ item.createTimeStr || item.updateTime }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup name="OrderLogistics">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Toast } from 'vant'
import { getOrderLog } from '@/service/order.api.js'

const { t } = useI18n()
const route = useRoute()

const pageLoading = ref(true)
const logData = ref([])
const isSingle = ref(false)

if (route.query.id) {
  Toast.loading({
    forbidClick: true,
    duration: 0
  })
  getOrderLog({ orderId: route.query.id}).then(res => {
    if (res.length) {
      const data = res.map(item => {
        const arr = item.log.split(item.orderId)
        return {
          ...item,
          tipsTxt: arr[1]
        }
      }).reverse()
      logData.value = data
    }
    isSingle.value = res.length === 1
    pageLoading.value = false
    Toast.clear()
  }).catch(() => {
    pageLoading.value = false
    Toast.clear()
  })
} else {
  pageLoading.value = false
}
</script>

<style lang="scss" scoped>
.logistics-container {
  padding: 15px;
  > .content {
    padding: 15px;
    background-color: #fff;
    border-radius: 4px;
    &.single {
      > .item {
        &::before {
          display: none;
        }
      }
    }
    > .item {
      position: relative;
      padding-bottom: 20px;
      padding-left: 20px;
      overflow: hidden;
      &::after {
        content: '';
        display: block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: var(--site-main-color);
        position: absolute;
        top: 7px;
        left: 0;
      }
      &::before {
        content: '';
        display: block;
        width: 2px;
        height: 100%;
        background-color: var(--site-main-color);
        position: absolute;
        top: 0;
        left: 4px;
      }
      &:first-child::before {
        top: 8px;
      }
      &:last-child::before {
        height: 15px;
      }
      > .info {
        font-size: 14px;
        line-height: 21px;
        > span {
          color: rgba(21, 82, 240, 1);
        }
      }
      > .time {
        font-size: 14px;
        color: rgba(51, 51, 51, 1);
        margin-top: 5px;
      }
    }
  }
}
</style>
