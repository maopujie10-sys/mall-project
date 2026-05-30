<template>
  <div>
    <fx-header :fixed="true">
      <template #title>
        {{ $t('退款详情') }}
      </template>
    </fx-header>
    <div style="height: 46px;" />

    <div v-if="detailsInfo" class="list-content" :class="{'is-ar': isArLang}">
      <div class="item">
        <div class="info-item">
          <p>{{ t('申请时间') }}</p>
          <div>{{ detailsInfo.refundTime }}</div>
        </div>
        <div class="info-item">
          <p>{{ t('退款单号') }}</p>
          <div class="copy">
            <p>{{ detailsInfo.id }}</p>
            <svg @click="copyHandle(detailsInfo.id)" width="18" height="18" viewBox="0 0 18 18" fill="none"
                xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" clip-rule="evenodd"
                    d="M8.00416 3.0188C6.90246 3.0188 6.00935 3.91191 6.00935 5.01361V6.00834H5.01337C3.91166 6.00834 3.01855 6.90145 3.01855 8.00315V12.9859C3.01855 14.0876 3.91166 14.9807 5.01337 14.9807H9.99608C11.0978 14.9807 11.9909 14.0876 11.9909 12.9859V11.9911H12.9869C14.0886 11.9911 14.9817 11.098 14.9817 9.99632V5.01361C14.9817 3.91191 14.0886 3.0188 12.9869 3.0188H8.00416ZM11.9909 10.9911H12.9869C13.5363 10.9911 13.9817 10.5457 13.9817 9.99632V5.01361C13.9817 4.46419 13.5363 4.0188 12.9869 4.0188H8.00416C7.45474 4.0188 7.00935 4.46419 7.00935 5.01361V6.00834H9.99608C11.0978 6.00834 11.9909 6.90145 11.9909 8.00315V10.9911ZM4.01855 8.00315C4.01855 7.45373 4.46395 7.00834 5.01337 7.00834H9.99608C10.5455 7.00834 10.9909 7.45373 10.9909 8.00315V12.9859C10.9909 13.5353 10.5455 13.9807 9.99608 13.9807H5.01337C4.46395 13.9807 4.01855 13.5353 4.01855 12.9859V8.00315Z"
                    fill="#333" />
            </svg>
          </div>
        </div>
        <div class="info-item">
          <p>{{ t('退款金额') }}</p>
          <div>${{ numberStrFormat(detailsInfo.returnPrice) }}</div>
        </div>
        <div class="info-item">
          <p>{{ t('退款状态') }}</p>
          <div :style="{'color': detailsInfo.statusColor}">{{ t(detailsInfo.statusTxt) }}</div>
        </div>
        <div class="info-item">
          <p>{{ t('退款理由') }}</p>
          <div>{{ detailsInfo.returnReason }}</div>
        </div>
        <div class="info-item">
          <p>{{ t('退款说明') }}</p>
          <div>{{ detailsInfo.returnDetail || t('无') }}</div>
        </div>
      </div>
    </div>

    <div v-if="detailsInfo && goodsListData.length" class="goods-content" :class="{'is-ar': isArLang}">
      <div v-for="item in goodsListData" :key="item.id" class="item">
        <div class="poster">
          <img :src="item.goodsIcon" alt="" />
        </div>
        <div class="info">
          <p class="name">{{ item.goodsName }}</p>
          <div class="num">
            <p class="price">${{ numberStrFormat(item.goodsReal) }}</p>
            <p>X{{ item.goodsNum }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, nextTick, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Toast } from 'vant'
import { useRoute, useRouter } from 'vue-router'
import useClipboard from 'vue-clipboard3'
import { statusData } from './../config'
import { numberStrFormat } from '@/utils'
import { arLangCheck } from '@/utils/arLangCheck'

import {
  detailsReturns,
  orderListGoods
} from '@/service/goods.api.js'

export default defineComponent({
  name: 'RefundRequestDetails',
  setup() {
    const isArLang = arLangCheck()
    const { t } = useI18n()
    const { toClipboard } = useClipboard()
    const route = useRoute()
    const router = useRouter()
    const { id } = route.query
    const goodsListData = ref([])

    const detailsInfo = ref(null)

    const getDetailsData = () => {
      Toast.loading({
        duration: 0,
        message: t('loading'),
        forbidClick: true
      })
      detailsReturns({ orderId: id }).then(data => {
        const status = Number(data.returnStatus)
        const statusOj = statusData.find(item => item.id === status)
        data.statusTxt = statusOj.txt
        data.statusColor = statusOj.color
        detailsInfo.value = data
      })
    }

    const goodsList = () => {
      orderListGoods({ orderId: id }).then(res => {
        const data = res.pageList
        goodsListData.value = data || []
      })
    }

    const copyHandle = async (txt) => {
      try {
        await toClipboard(txt);
        Toast(t('copySuccess'));
      } catch (e) {
        console.error(e);
      }
    }

    nextTick(() => {
      if (id) {
        getDetailsData()
        goodsList()
      } else {
        Toast(t('参数错误'))
        setTimeout(() => {
          router.back()
        }, 1000)
      }
    })
    return {
      t,
      detailsInfo,
      isArLang,
      copyHandle,
      goodsListData,
      numberStrFormat
    }
  }
})
</script>

<style lang="scss" scoped>
.list-content {
  padding: 15px;
  &.is-ar {
    > .item > .info-item {
      > div {
        padding-left: 0;
        padding-right: 20px;
        text-align: left;
        &.copy {
          > p {
            padding-right: 0;
            padding-left: 5px;
          }
        }
      }
    }
  }
  > .item {
    background-color: #fff;
    border-radius: 4px;
    padding: 5px 15px;
    margin-top: 15px;
    border-bottom: 1px solid #EFF2F6;
    &:first-child {
      margin-top: 0;
    }
    > .info-item {
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 0;
      line-height: 16px;
      font-size: 14px;
      > p {
        color: #999;
      }
      > div {
        text-align: right;
        flex: 1;
        padding-left: 20px;
        word-break: break-all;
        color: #333;
        &.copy {
          display: flex;
          align-items: center;
          > p {
            flex: 1;
            padding-right: 5px;
          }
        }
      }
    }
  }
}

.goods-content {
  padding: 15px;
  padding-top: 0;
  &.is-ar {
    > .item > .info {
      padding-left: 0;
      padding-right: 10px;
    }
  }
  > .item {
    margin-bottom: 15px;
    display: flex;
    background-color: #fff;
    border-radius: 4px;
    padding: 10px;
    > .poster {
      width: 78px;
      height: 78px;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      > img {
        width: 100%;
        height: auto;
      }
    }
    > .info {
      flex: 1;
      padding-left: 10px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      > .name {
        font-size: 14px;
        line-height: 18px;
        color: #333;
      }
      > .num {
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: var(--site-main-color);;
        font-size: 14px;
        > .price {
          font-size: 16px;
        }
      }
    }
  }
}
</style>
