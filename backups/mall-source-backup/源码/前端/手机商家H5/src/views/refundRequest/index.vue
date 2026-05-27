<template>
  <div>
    <fx-header :fixed="true">
      <template #title>
        {{ $t('refundRequest') }}
      </template>
    </fx-header>
    <div style="height: 46px;" />

    <van-pull-refresh v-model="refreshing" :pulling-text="t('pullingText')" :loosing-text="t('loosingText')" :loading-text="t('loading')" @refresh="onRefresh">
      <van-list v-model:loading="loading" :finished="finished" :loading-text="t('loading')" :finished-text="listData.length ? t('product.3') : ''" @load="getListData">
        <div v-if="listData.length" class="list-content">
          <div v-for="item in listData" :key="item.id" class="item" :class="{'is-ar': isArLang}" @click="goToDetails(item)">
            <div class="info-item">
              <p>{{ t('申请时间') }}</p>
              <div>{{ item.refundTime ? formatZoneDate(item.refundTime) : '-' }}</div>
            </div>
            <div class="info-item">
              <p>{{ t('退款单号') }}</p>
              <div class="copy">
                <p :class="{'is-ar': isArLang}">{{ item.id }}</p>
                <svg @click="copyHandle(item.id)" width="18" height="18" viewBox="0 0 18 18" fill="none"
                    xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" clip-rule="evenodd"
                        d="M8.00416 3.0188C6.90246 3.0188 6.00935 3.91191 6.00935 5.01361V6.00834H5.01337C3.91166 6.00834 3.01855 6.90145 3.01855 8.00315V12.9859C3.01855 14.0876 3.91166 14.9807 5.01337 14.9807H9.99608C11.0978 14.9807 11.9909 14.0876 11.9909 12.9859V11.9911H12.9869C14.0886 11.9911 14.9817 11.098 14.9817 9.99632V5.01361C14.9817 3.91191 14.0886 3.0188 12.9869 3.0188H8.00416ZM11.9909 10.9911H12.9869C13.5363 10.9911 13.9817 10.5457 13.9817 9.99632V5.01361C13.9817 4.46419 13.5363 4.0188 12.9869 4.0188H8.00416C7.45474 4.0188 7.00935 4.46419 7.00935 5.01361V6.00834H9.99608C11.0978 6.00834 11.9909 6.90145 11.9909 8.00315V10.9911ZM4.01855 8.00315C4.01855 7.45373 4.46395 7.00834 5.01337 7.00834H9.99608C10.5455 7.00834 10.9909 7.45373 10.9909 8.00315V12.9859C10.9909 13.5353 10.5455 13.9807 9.99608 13.9807H5.01337C4.46395 13.9807 4.01855 13.5353 4.01855 12.9859V8.00315Z"
                        fill="#333" />
                </svg>
              </div>
            </div>
            <div class="info-item">
              <p>{{ t('退款金额') }}</p>
              <div>${{ numberStrFormat(item.returnPrice) }}</div>
            </div>
            <div class="info-item">
              <p>{{ t('退款状态') }}</p>
              <div :style="{'color': item.statusColor}">{{ t(item.statusTxt) }}</div>
            </div>
            <div class="info-item">
              <p>{{ t('退款理由') }}</p>
              <div>{{ item.returnReason || t('无') }}</div>
            </div>
            <div class="info-item">
              <p>{{ t('退款说明') }}</p>
              <div>{{ item.returnDetail || t('无') }}</div>
            </div>
          </div>
        </div>
        <van-empty v-if="!listData.length && !loading" :image="empytImg.href" :description="t('noData')" />
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script>
import { defineComponent, ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Toast } from 'vant'
import useClipboard from 'vue-clipboard3'
import { arLangCheck } from '@/utils/arLangCheck'
import {
  _returnApply
} from '@/service/goods.api.js'
import { statusData, reasonData } from './config'
import { openPage, formatZoneDate, numberStrFormat } from '@/utils'

export default defineComponent({
  name: 'RefundRequest',
  setup() {
    const isArLang = arLangCheck()

    const { toClipboard } = useClipboard()
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

    const getListData = () => {
      const params = {
        ...page.value
      }
      _returnApply(params).then(res => {
        const pageList = res.pageList || []
        pageList.forEach(item => {
          const status = Number(item.returnStatus)
          const reason = Number(item.returnReason)
          const statusOj = statusData.find(_item => _item.id === status)
          item.statusTxt = statusOj.txt
          item.statusColor = statusOj.color
          const reasonObj = reasonData.find(_item => _item.id === reason)
          item.returnReason = reasonObj ? t(reasonObj.txt) : ''
        })
        listData.value = page.value.pageNum === 1 ? pageList : [...listData.value, ...pageList]
        page.value.pageNum++
        loading.value = false
        refreshing.value = false
        
        finished.value = res.pageInfo.lastPage
      }).catch(() => {
        finished.value = true
        loading.value = false
        refreshing.value = false
      })
    }

    const onRefresh = () => {
      loading.value = true
      page.value.pageNum = 1
      getListData()
    }

    const copyHandle = async (txt) => {
      try {
        await toClipboard(txt);
        Toast(t('copySuccess'));
      } catch (e) {
        console.error(e);
      }
    }

    const goToDetails = (data) => {
      openPage({
        path: '/refundRequest/details',
        query: {
          id: data.id
        }
      })
    }

    return {
      t,
      listData,
      refreshing,
      loading,
      finished,
      empytImg,
      formatZoneDate,
      numberStrFormat,
      isArLang,
      getListData,
      onRefresh,
      copyHandle,
      goToDetails
    }
  }
})
</script>

<style lang="scss" scoped>
.list-content {
  padding: 15px;
  > .item {
    background-color: #fff;
    border-radius: 4px;
    padding: 5px 15px;
    margin-top: 15px;
    border-bottom: 1px solid #EFF2F6;
    &.is-ar {
      > .info-item > div {
        padding-right: 20px;
        padding-left: 0 !important;
        text-align: left;
      }
    }
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
            &.is-ar {
              padding-right: 0;
              padding-left: 5px;
            }
          }
        }
      }
    }
  }
}
</style>
