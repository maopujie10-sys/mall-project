<template>
  <div>
    <fx-header :fixed="true">
      <template #title>
        {{ $t('financialStatement') }}
      </template>
      <template #right>
        <div class="filter-icon" @click="actionShow = true">
          <img :src="filterIcon" alt="" />
        </div>
      </template>
    </fx-header>
    <div style="height: 46px;" />

    <van-action-sheet
      v-model:show="actionShow"
      :actions="reportFilterAction"
      :cancel-text="t('取消')"
      close-on-click-action
      @select="selectHandle"
    />

    <van-pull-refresh v-model="refreshing" :pulling-text="t('pullingText')" :loosing-text="t('loosingText')" :loading-text="t('loading')" @refresh="onRefresh">
      <div class="report-content">
        <div v-for="item in reportDataRef" :key="item.key" class="item" :style="{'background-color': item.color}">
          <img :src="blockBg.href" alt="" />
          <p>{{ t(item.title) }}</p>
          <count-to v-if="Number(item.number) > 0" :prefix="item.prefix" :decimals="item.decimals" :startVal="0" :endVal='item.number' :duration='1500' class="number-count"></count-to>
          <h3 v-else class="number-count">0</h3>
        </div>
      </div>

      <van-list v-model:loading="loading" :finished="finished" :loading-text="t('loading')" :finished-text="listData.length ? t('product.3') : ''" @load="getListData">
        <div v-if="listData.length" class="list-content">
          <div v-for="(item, index) in listData" :key="index" class="item">
            <div class="info-content">
              <div class="item">
                <img :src="imgObj.calendar" alt="" />
                <p>{{ t('日期') }}:</p>
                <p>{{ formatZoneDate(item.dayString, 'YYYY-MM-DD') }}</p>
              </div>
              <div class="item">
                <img :src="imgObj.credit" alt="" />
                <p>{{ t('总订单') }}:</p>
                <p>{{ item.orderNum }}</p>
              </div>
              <div class="item">
                <img :src="imgObj.cancel" alt="" />
                <p>{{ t('取消订单') }}:</p>
                <p class="red">{{ item.orderCancel }}</p>
              </div>
              <div class="item">
                <img :src="imgObj.refund" alt="" />
                <p>{{ t('退款订单') }}:</p>
                <p>{{ item.orderReturns }}</p>
              </div>
            </div>
            <div class="amout">
              <!-- <div v-if="item.totalSales">${{ item.totalSales }}</div> -->
              <!-- <p>({{ t('利润') }} {{ item.totalProfit }})</p> -->
              <div class="profit">{{ t('利润') }} {{ numberStrFormat(item.totalProfit) }}</div>
            </div>
          </div>
        </div>
        <van-empty v-if="!listData.length && !loading" :image="empytImg.href" :description="t('noData')" />
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script>
import { computed, defineComponent, nextTick, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Toast } from 'vant'
import { CountTo } from 'vue3-count-to'
import { reportData, reportFilter } from './config'
import { formatZoneDate, numberStrFormat } from '@/utils'

import {
  sellerReportHead,
  reportList
} from '@/service/shop.api.js'

export default defineComponent({
  name: 'FinacialStatements',
  components: {
    CountTo
  },
  setup() {
    const { t } = useI18n()
    const blockBg = new URL('@/assets/image/shop/bg_01.png', import.meta.url)
    const reportDataRef = ref([...reportData])

    const sellerId = localStorage.getItem('sellerId') || ''

    const actionShow = ref(false)
    const reportFilterAction = computed(() => {
      const data = reportFilter.map(item => {
        return {
          name: t(item.name),
          value: item.value
        }
      })
      return data
    })

    const filterIcon = new URL('@/assets/image/fundsRecords/Frame1277.png', import.meta.url)
    const imgObj = {
      calendar: new URL('@/assets/image/finance/calendar.png', import.meta.url),
      credit: new URL('@/assets/image/finance/credit-card.png', import.meta.url),
      cancel: new URL('@/assets/image/finance/cancel.png', import.meta.url),
      refund: new URL('@/assets/image/finance/ri_refund.png', import.meta.url)
    }

    const currentType = ref(0)
    const empytImg = new URL('@/assets/image/public/no_data.png', import.meta.url)
    const listData = ref([])
    const refreshing = ref(false)
    const loading = ref(true)
    const finished = ref(false)
    const page = ref({
      pageNum: 1,
      pageSize: 10
    })

    const getSellerReport = () => {
      Toast.loading({
        duration: 0,
        message: t('loading'),
        forbidClick: true
      })
      sellerReportHead({
        sellerId,
        content_type: currentType.value
      }).then(res => {
        Toast.clear()
        const data = res.head
        reportDataRef.value.forEach(item => {
          item.number = data[item.key]
        })
      }).catch(() => {
        Toast.clear()
      })
    }

    const getListData = () => {
      const params = {
        ...page.value,
        content_type: currentType.value,
        sellerId
      }
      reportList(params).then(res => {
        const pageList = res.pageList || []
        listData.value = page.value.pageNum === 1 ? pageList : [...listData.value, ...pageList]
        loading.value = false
        refreshing.value = false
        
        finished.value = pageList.length < page.value.pageSize
        page.value.pageNum++
      }).catch(() => {
        finished.value = true
        loading.value = false
        refreshing.value = false
      })
    }


    const onRefresh = () => {
      loading.value = true
      page.value.pageNum = 1
      getSellerReport()
      getListData()
    }

    const selectHandle = (item) => {
      currentType.value = item.value
      listData.value = []
      getSellerReport()
      onRefresh()
    }

    nextTick(() => {
      getSellerReport()
    })

    return {
      t,
      blockBg,
      reportDataRef,
      listData,
      refreshing,
      loading,
      finished,
      empytImg,
      filterIcon,
      imgObj,
      actionShow,
      reportFilterAction,
      formatZoneDate,
      numberStrFormat,
      getListData,
      onRefresh,
      selectHandle
    }
  }
})
</script>

<style lang="scss" scoped>
.report-content {
  overflow: hidden;
  padding: 15px;
  > .item {
    float: left;
    width: calc((100% - 15px) / 2);
    margin-right: 15px;
    margin-top: 15px;
    padding: 10px;
    border-radius: 4px;
    overflow: hidden;
    position: relative;
    &:nth-child(-n + 2) {
      margin-top: 0;
    }
    &::before {
      content: '';
      display: block;
      width: 72px;
      height: 72px;
      border-radius: 50%;
      background-color: rgba(255, 255, 255, .1);
      position: absolute;
      top: -36px;
      right: -36px;
      z-index: 1;
    }
    &:nth-child(2n) {
      margin-right: 0;
    }
    > img {
      width: 100%;
      height: auto;
      position: absolute;
      left: 0;
      bottom: 0;
      z-index: 1;
    }
    > p {
      font-size: 14px;
      color: #fff;
      position: relative;
      z-index: 2;
    }
    .number-count {
      font-size: 20px;
      font-weight: bold;
      color: #fff;
      display: inline-block;
      width: 100%;
      text-align: right;
      margin-top: 20px;
      position: relative;
      z-index: 2;
    }
  }
}

.van-pull-refresh {
  background-color: #EFF2F6;
}

.list-content {
  padding: 0 15px;
  > .item {
    background-color: #fff;
    border-radius: 4px;
    padding: 5px 15px;
    margin-top: 15px;
    display: flex;
    font-size: 14px;
    line-height: 16px;
    &:first-child {
      margin-top: 0;
    }
    > .info-content {
      flex: 1;
      > .item {
        display: flex;
        align-items: center;
        padding: 10px 0;
        > img {
          width: 20px;
          height: auto;
        }
        > p {
          &:nth-child(2) {
            color: #333;
            padding-left: 10px;
            padding-right: 5px;
          }
          &:last-child {
            color: #000;
            &.red {
              color: #D93232;
            }
          }
        }
      }
    }
    > .amout {
      padding: 10px 0;
      text-align: right;
      > div {
        font-size: 20px;
        font-weight: bold;
        color: var(--site-main-color);
        &.profit {
          font-weight: normal;
          font-size: 14px;
        }
      }
      > p {
        font-size: 12px;
        color: #999;
        padding-top: 8px;
      }
    }
  }
}

.filter-icon {
  width: 20px;
}
</style>
