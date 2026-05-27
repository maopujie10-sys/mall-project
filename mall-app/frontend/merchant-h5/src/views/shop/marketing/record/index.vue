<template>
  <div>
    <fx-header :fixed="true">
      <template #title>
        {{ t('shopBuyRecord') }}
      </template>
    </fx-header>
    <div style="height: 46px;" />

    <van-pull-refresh v-model="refreshing" :pulling-text="t('pullingText')" :loosing-text="t('loosingText')" :loading-text="t('loading')" @refresh="onRefresh">
      <van-list v-model:loading="loading" :finished="finished" :loading-text="t('loading')" :finished-text="listData.length ? t('product.3') : ''" @load="getListData">
        <div v-if="listData.length" class="list-content">
          <div v-for="(item, index) in listData" :key="index" class="item">
            <div class="info-item">
              <p>{{ t('shopRecordName') }}</p>
              <div>{{ item.name }}</div>
            </div>
            <div class="info-item">
              <p>{{ t('shopRecordStartTime') }}</p>
              <div>{{ item.startTime }}</div>
            </div>
            <div class="info-item">
              <p>{{ t('shopRecordStopTime') }}</p>
              <div>{{ item.stopTime }}</div>
            </div>
            <div class="info-item">
              <p>{{ t('shopRecordPayType') }}</p>
              <div>{{ t('shopRecordPayName') }}</div>
            </div>
            <div class="info-item">
              <p>{{ t('shopRecordPrice') }}</p>
              <div class="price">{{ '$' + numberStrFormat(item.prize) }}</div>
            </div>
          </div>
        </div>
        <van-empty v-if="!listData.length && !loading" :image="empytImg.href" :description="t('noData')" />
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script>
import { defineComponent, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  numberStrFormat
} from '@/utils'

import {
  sellerPromotionalListBuy
} from '@/service/shop.api.js'

export default defineComponent({
  name: 'ShopMarketingRecord',
  setup() {
    const { t } = useI18n()
    const empytImg = new URL('@/assets/image/public/no_data.png', import.meta.url)

    const listData = ref([])
    const refreshing = ref(false)
    const loading = ref(true)
    const finished = ref(false)
    const page = ref({
      pageNum: 1,
      pageSize: 10
    })

    const getListData = async () => {
      const params = {
        ...page.value
      }
      await sellerPromotionalListBuy(params).then(res => {
        const pageList = res.pageList || []
        
        listData.value = page.value.pageNum === 1 ? pageList : [...listData.value, ...pageList]
        page.value.pageNum++
        loading.value = false
        refreshing.value = false
        
        finished.value = res.pageInfo.lastPage
      }).catch(() => {
        loading.value = false
        finished.value = true
      })
    }

    const onRefresh = () => {
      loading.value = true
      page.value.pageNum = 1
      getListData()
    }

    return {
      empytImg,
      refreshing,
      loading,
      finished,
      listData,
      t,
      getListData,
      onRefresh,
      numberStrFormat
    }
  }
})
</script>

<style lang="scss" scoped>
.list-content {
  padding: 15px;
  > .item {
    width: 100%;
    background-color: #fff;
    border-radius: 4px;
    padding: 5px 15px;
    margin-top: 15px;
    &:first-child {
      margin-top: 0;
    }
    > .info-item {
      padding: 10px 0;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      > p {
        font-size: 14px;
        color: #999;
      }
      > div {
        font-size: 14px;
        color: #333;
        &.price {
          color: var(--site-main-color);;
        }
      }
    }
  }
}
</style>
