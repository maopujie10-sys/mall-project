<template>
  <div class="goods_list" :class="{'is-ar': isArLang}"  @click="goDetails">
    <p class="title mb-2">{{ props.info.id }}</p>
    <p class="mb-2">
      <van-icon size="20px" name="notes-o"/>
      <span>{{ $t('下单日期') }}：{{ formatZoneDate(props.info.createTime) }}</span>
    </p>
    <p class="mb-2">
      <van-icon size="20px" name="debit-pay"/>
      <span>{{ $t('支付状态') }}：
						<span :style="{'color': props.info.payStatus == 1 ? '#2369f6' : '#dc2626'}">{{props.info.payStatus == 1 ? $t('买家已付款') : $t('等待买家付款')}}</span>
        <!-- <span style="color: #f00">已支付</span> -->
					</span>
    </p>
    <p class="mb-2">
      <van-icon size="20px" name="cart-o"/>
      <span>{{ $t('采购状态') }}：{{ props.info.purchStatus == 1 ? `${$t('已采购')}` : $t('待采购') }}</span>
    </p>
    <p class="mb-2">
      <van-icon size="20px" name="logistics"/>
      <span>{{ $t('物流状态') }}：{{handleLogistics(props.info.status)}}</span>
    </p>
    <div class="bottom-content">
      <div class="money">
        <p>${{ numberStrFormat(props.info.totalCost) }}</p>
        <span>({{ $t('利润') }}${{ numberStrFormat(props.info.profit) }})</span>
      </div>
      <div class="btn-content">
        <!-- <span v-if="props.info.purchStatus / 1 !== 1 && props.info.status / 1 !== -1 && props.info.status / 1 !== 0 && props.info.status / 1 !== 6" class="btn" @click.stop="buy">{{ $t('采购') }}</span> -->
        <span v-if="Number(props.info.purchStatus) !== 1 && ![-1, 0, 6].includes(Number(props.info.status))" class="btn" @click.stop="buy">{{ $t('采购') }}</span>
      </div>
    </div>
    
  </div>
</template>
<script setup>
import { logisticsData } from '../refundRequest/config'
import { useI18n } from 'vue-i18n';
import clonedeep from 'lodash.clonedeep'
import { formatZoneDate, numberStrFormat } from '@/utils'
import { arLangCheck } from '@/utils/arLangCheck'

const mode = import.meta.env.MODE
const { t } = useI18n();
const isArLang = arLangCheck()

// console.log(props.info)
const props = defineProps({
  info: {
    type: Object,
    default: () => {}
  }
})

const logisticsDataC = clonedeep(logisticsData)
if (['argos'].includes(mode)) {
  logisticsDataC.forEach(item => {
    if (item.id === 4) {
      item.txt = '订单已完成'
    }
    if (item.id === 5) {
      item.txt = '买家已签收'
    }
  })
}

const handleLogistics = (status) => {
  const item = logisticsDataC.find(item => item.id === status)
  // console.log('item', item)
  if (!item) {
    return t('全部')
  } else {
    return t(item.txt)
  }
}
const buy = () => {
  router.push({
    // path: '/orderdeails',
    path: '/qr_order',
    query: {
      id: props.info.id,
      title: "采购确定"
    }
  })
}
const goDetails = () => {
  router.push({
    path: '/orderdeails',
    query: {
      id: props.info.id,
      title: "订单详情"
    }
  })
}
</script>
<style lang="scss" scoped>
.goods_list{
  background:#fff;
  padding:10px;
  box-sizing: border-box;
  border-radius:5px;
  position:relative;
  margin-bottom:10px;
  &.is-ar {
    p i {
      padding-right: 0;
      padding-left: 10px;
    }
  }
  .bottom-content {
    width: 100%;
    border-top: 1px solid #f6f6f6;
    padding-top: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    .money{
      font-size:13px;
      color:#666;
      text-align:center;
      p {
        font-size:18px;
        font-weight:bold;
        color:var(--site-main-color);
      }
    }
    .btn-content {
      display: flex;
      align-items: center;
      .btn{
        width: 80px;
        height: 30px;
        line-height:30px;
        text-align: center;
        background:var(--site-main-color);
        color:#fff;
        right:10px;
        bottom:10px;
        font-size:13px;
        border-radius:3px;
        margin-right: 10px;
        &:last-child {
          margin-right: 0;
        }
      }
    }
  }
  
  p{
    height:30px;
    line-height:30px;
    span{
      color:#666;
      font-size:13px;
    }
    i{
      padding-right:10px;
    }
  }
  .title{
    font-weight:bold;
  }
}
</style>
