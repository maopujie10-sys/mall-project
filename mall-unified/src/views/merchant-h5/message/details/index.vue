<template>
  <div class="message-details">
    <fx-header :fixed="true">
      <template #title>
        {{ $t('消息详情') }}
      </template>
    </fx-header>
    <div style="height: 46px;" />

    <div v-if="detailInfo.title" class="details-content">
      <div class="title">{{ detailInfo.titleStr }}</div>
      <p class="time">{{ detailInfo.timeStr }}</p>
      <div class="content" v-html="detailInfo.contentStr"></div>
    </div>
  </div>
</template>

<script>
import { defineComponent, nextTick, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Toast } from 'vant'
import { useI18n } from 'vue-i18n'
import { dataTime } from '@/utils'
import { msgTypeInfo } from './../config'

import {
  messageDetail
} from '@/service/user.api.js'

export default defineComponent({
  name: 'MessageDetails',
  setup() {
    const { t } = useI18n()
    const route = useRoute()
    const router = useRouter()
    const { id } = route.query
    const detailInfo = ref({})

    const getDetailsData = () => {
      Toast.loading({
        duration: 0,
        message: t('loading'),
        forbidClick: true
      })

      messageDetail({ id }).then(res => {
        const data = res
        const varObj = {}
        const dataArr = data.varInfo ? JSON.parse(data.varInfo) : []
        dataArr.forEach(item => {
          varObj[item.code] = ['complaintReason'].includes(item.code) ? t(item.value) : item.value
        })
        const txtData = msgTypeInfo[data.bizType]
        const item = dataArr.find(item => item.code === txtData.key)
        let resTxt = ''
        if (txtData.key) {
          if (txtData.key === 'creditScore') {
            resTxt = t('systemMsgScore', {creditScore: (item ? item.value : '0')})
          } else if (txtData.key === 'inbox_recharge_success') {
            resTxt = t('rechargeSuccessTips', {orderAmount: getValueStr(data, 'orderAmount')})
          } else if (txtData.key === 'inbox_withdraw_success') {
            resTxt = t('withdrawalSuccessTips', {orderAmount: getValueStr(data, 'orderAmount')})
          } else if (txtData.key === 'inbox_store_audit_fail') {
            resTxt = t('storeAuthenticationFailedTips', {shop_name: getValueOf(data, 'shop_name'), reason: getValueOf(data, 'reason')})
          } else if (txtData.key === 'inbox_store_audit_success') {
            resTxt = t('storeAuthenticationPassedTips', {shop_name: getValueOf(data, 'shop_name')})
          } else {
            resTxt = t(txtData.txt) + (item ? item.value : '0')
            if (txtData.txt1) {
              resTxt += t(txtData.txt1)
            }
          }
        } else {
          resTxt = t(txtData.txt, varObj)
        }
        data.titleStr = t(txtData.title)
        data.contentStr = resTxt
        data.timeStr = dataTime(res.sendTime, true)

        detailInfo.value = data
      })
    }

    const getValueStr = (data, key) => {
      const dataArr = data.varInfo ? JSON.parse(data.varInfo) : []
      const item = dataArr.find(item => item.code === key)
      return item ? item.value : '0'
    }

    const getValueOf = (data, key) => {
      const dataArr = data.varInfo ? JSON.parse(data.varInfo) : []
      const item = dataArr.find(item => item.code === key)
      return item ? item.value : ''
    }


    nextTick(() => {
      if (id) {
        getDetailsData()
      } else {
        Toast(t('参数错误'))
        setTimeout(() => {
          router.back()
        }, 1000)
      }
    })
    return {
      t,
      detailInfo
    }
  }
})
</script>

<style lang="scss" scoped>
.message-details {
  min-height: 100vh;
  background-color: #fff;
  padding: 15px;
  > .details-content {
    > .title {
      font-size: 16px;
      font-weight: bold;
    }
    > .time {
      font-size: 12px;
      color: #999;
      padding-top: 5px;
      padding-bottom: 10px;
    }
    > .content {
      padding-top: 15px;
      border-top: 1px solid #eee;
      font-size: 14px;
    }
  }
}
</style>
