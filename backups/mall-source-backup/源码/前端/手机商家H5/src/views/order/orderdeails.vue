<template>
  <div>
    <fx-header :fixed="true">
      <template #title>
        {{ $t('订单详情') }}
      </template>
    </fx-header>
    <div style="height: 46px;" />

    <div class="section" :class="{'is-ar': isArLang}">
      <div class="list">
        <div>{{ $t('订单号') }}</div>
        <div class="flex">
          {{ orderInfo.id }}
          <img class="w-5 h-5" @click="handleCopy(orderInfo.id)" :src="images.copy" alt="">
        </div>
      </div>
      <div class="info-list">
        <p>{{ $t('下单时间') }}</p>
        <div>{{ formatZoneDate(orderInfo.createTime) }}</div>
      </div>
      <div v-if="orderInfo.pushTime" class="info-list">
        <p>{{ $t('采购时间') }}</p>
        <div>{{ formatZoneDate(orderInfo.pushTime) }}</div>
      </div>
      <div class="info-list">
        <p>{{ $t('付款方式') }}</p>
        <div>{{ $t('钱包') }}</div>
      </div>
      <div class="info-list">
        <p>{{ $t('支付状态') }}</p>
        <div>{{ payStatus(orderInfo.payStatus) }}</div>
      </div>
      <div class="info-list">
        <p>{{ $t('物流状态') }}</p>
        <div>{{ statusToText(orderInfo.status) }}</div>
      </div>
      <div class="info-list">
        <p>{{ $t('采购金额') }}</p>
        <div>${{ numberStrFormat(orderInfo.systemPrice) }}</div>
      </div>
      <div class="info-list">
        <p>{{ $t('销售金额') }}</p>
        <div>${{ numberStrFormat(orderInfo.prizeReal) }}</div>
      </div>
      <div class="info-list">
        <p>{{ $t('姓名') }}</p>
        <div>{{ orderInfo.username }}</div>
      </div>
      <div class="info-list">
        <p>{{ $t('邮箱') }}</p>
        <div>{{ orderInfo.email }}</div>
      </div>
      <div class="info-list">
        <p>{{ $t('手机') }}</p>
        <div>{{ orderInfo.phone }}</div>
      </div>
      <div class="info-list">
        <p>{{ $t('国家') }}</p>
        <div>{{ orderInfo.country }}</div>
      </div>
      <div class="info-list">
        <p>{{ $t('州') }}</p>
        <div>{{ orderInfo.province }}</div>
      </div>
      <div class="info-list">
        <p>{{ $t('城市') }}</p>
        <div>{{ orderInfo.city }}</div>
      </div>
      <div class="info-list">
        <p>{{ $t('邮编') }}</p>
        <div>{{ orderInfo.postcode }}</div>
      </div>
      <div class="info-list">
        <p>{{ $t('收货地址') }}</p>
        <div>{{ orderInfo.address }}</div>
      </div>
    </div>

    <van-list v-model:loading="loading" :finished="finished" :loading-text="t('loading')" @load="getListData">
      <div class="listitem" :class="{'is-ar': isArLang}" v-for="item in shopList">
        <div class="goods-sn">
          <p>{{ t('产品编号') }}</p>
          <div>
            <p>{{ item.goodsId }}</p>
            <img class="w-5 h-5" @click="handleCopy(item.goodsId)" :src="images.copy" alt="">
          </div>
        </div>
        <div class="goods-info">
          <div class="pic">
            <img :src="item.goodsIcon"/>
          </div>
          <div class="name">
            <p class="title">{{ item.goodsName }}</p>
            <div v-if="item.attributes && item.attributes.length" v-for="_item in item.attributes" :key="_item.attrValueId" class="spec">
              <div v-if=" _item.attrName &&  _item.attrValue" class="item">
                <p>{{ _item.attrName }}：</p>
                <p>{{ _item.attrValue }}</p>
              </div>
            </div>
            <p class="col">
              <!-- <span>{{ $t('采购数量') }}</span> -->
              <p class="title money">${{ numberStrFormat(item.systemPrice) }}</p>
              <span>x{{ item.goodsNum }}</span>
            </p>
          </div>
        </div>
      </div>
    </van-list>

    <div class="section bottom" :class="{'is-ar': isArLang}">
      <div class="list">
        {{ $t('小计') }} <span>${{ numberStrFormat(orderInfo.systemPrice) }}</span>
        <!-- {{ $t('小计') }} <span>${{ numberStrFormat(orderInfo.prizeReal) }}</span> -->
      </div>
      <div v-if="orderInfo.sellerDiscountPrice" class="list price-content">
        <span></span>
        <p>{{ t('采购优惠') }}<span>{{ new Decimal(orderInfo.sellerDiscount).mul(100) }}%</span>, {{ t('优惠价') }}<span>${{ numberStrFormat(orderInfo.sellerDiscountPrice) }}</span></p>
      </div>
      <div class="list">
        {{ $t('税') }} <span>${{ numberStrFormat(orderInfo.tax) }}</span>
      </div>
      <div class="list">
        {{ $t('运费') }} <span>${{ numberStrFormat(orderInfo.fees) }}</span>
      </div>
      <!--      <div class="list">-->
      <!--        {{ $t('折扣') }} <span>${{ orderInfo.discount }}</span>-->
      <!--      </div>-->
      <div class="list">
        <!-- {{ $t('合计') }} <span class="total">${{
          numberStrFormat(orderInfo.prizeReal + orderInfo.tax + orderInfo.fees)
        }}</span> -->

        {{ $t('合计') }} <span class="total">${{ totalNum }}</span>
      </div>
    </div>

    <div class="right-fixed-enter" :class="{'active': showIconEnter}" @click="toLogistics">
      <img :src="images.car" alt="">
    </div>
    <div class="right-fixed-enter message" :class="{'active': showIconEnter}" @click="toClient">
      <img :src="images.message" alt="">
    </div>
  </div>
</template>

<script setup>
import {logisticsData} from "@/views/refundRequest/config.js";
import {useClipboard} from "@vueuse/core";
import {onMounted, ref, watch, nextTick, onUnmounted, computed} from "vue";
import {useRoute, useRouter} from "vue-router";
import clonedeep from 'lodash.clonedeep'
import {_orderDetail, _orderDetailList} from "../../service/order.api.js";
import {Toast} from "vant";
import {useI18n} from 'vue-i18n'
import {clipboardText, formatZoneDate, numberStrFormat} from '@/utils'
import { arLangCheck } from '@/utils/arLangCheck'
import Decimal from 'decimal.js'


const mode = import.meta.env.MODE
const isArLang = arLangCheck()
const {text, copy, copied, isSupported} = useClipboard()

const handleId = (id) => {
  return id ? id.slice(0, 8) + '******' + id.slice(-8) : ''
}

const images = {
  copy: new URL('@/assets/image/order/copy.png', import.meta.url),
  message: new URL('@/assets/image/order/Frame.png', import.meta.url),
  car: new URL('@/assets/image/order/Vector.png', import.meta.url),
}


const {t} = useI18n()
const route = useRoute();
const router = useRouter()

const orderId = route.query.id;
let orderInfo = ref({});
const shopList = ref([]);
const loading = ref(false)
const finished = ref(false)
const page = ref({
  pageNum: 1
})
/**
 * 初始化操作
 */
onMounted(() => {
  getOrderDetail()
})

// 合计
const totalNum = computed(() => {
  const { sellerDiscountPrice, systemPrice, fees, tax } = orderInfo.value
  const price = sellerDiscountPrice ? sellerDiscountPrice : systemPrice
  return numberStrFormat(Number(price) + Number(fees) + Number(tax))
})

const toClient = () => {
  router.push({
    path: '/messageCenter',
    query: {
      partyId: orderInfo.value.partyId,
      username: orderInfo.value.email
    }
  })
}

const toLogistics = () => {
  router.push({
    path: '/order-logistics',
    query: {
      id: route.query.id
    }
  })
}

const getListData = () => {
  const params = {
    ...page.value,
    orderId
  }
  _orderDetailList(params)
    .then((res) => {
      const data = res.pageList || []
      shopList.value = page.value.pageNum === 1 ? data : [...shopList.value, ...data]
      
      page.value.pageNum++

      loading.value = false
      finished.value = res.pageInfo.lastPage
      
    })
    .catch(() => {
      finished.value = true
      loading.value = false
    })
}

/**
 * 获取订单详情
 */
const getOrderDetail = () => {
  Toast.loading({duration: 0, forbidClick: true})
  _orderDetail({
    orderId
  }).then((res) => {
    orderInfo.value = res.orderInfo;
  })
}
/**
 * 物流状态
 * @param type
 * @returns {string}
 */

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
const statusToText = (type) => {
  const item = logisticsDataC.find(item => item.id === type / 1)
  if (item) {
    return t(item.txt)
  } else {
    return ''
  }

}
/**
 * 支付状态
 * @param type
 * @returns {string}
 */
const payStatus = (type) => {
  return type === 1 ? t('已支付') : t('未支付')
}
/**
 * 订单拷贝
 * @param order_no
 */

const lastScrollTop = ref(0)
const showIconEnter = ref(true)
const handleScroll = () => {
  const currentScrollTop = window.scrollY
  if (currentScrollTop > lastScrollTop.value) {
      // 向下滚动
      showIconEnter.value = false
  } else if (currentScrollTop < lastScrollTop.value) {
      // 向上滚动
      showIconEnter.value = true
  }

  lastScrollTop.value = currentScrollTop
}

watch(copied, () => {
  Toast(t('copySuccess'))
})
const handleCopy = (order_no) => {
  if (order_no) {
    copy(order_no)
  }
}

onUnmounted(() => {
  window.document.removeEventListener('scroll', handleScroll)
})

nextTick(() => {
  window.document.addEventListener('scroll', handleScroll)
})
</script>

<style lang="scss" scoped>
.van-list {
  min-height: 20px;
}

.section {
  margin: 15px;
  border-radius: 4px;
  overflow: hidden;
  &.is-ar {
    .info-list > div {
      padding-left: 0;
      padding-right: 15px;
      text-align: left;
    }
    .list span {
      text-align: left;
      padding-left: 0;
      padding-right: 15px;
    }
    .list {
      > .flex {
        img {
          margin-left: 0;
          margin-right: 8px;
        }
      }
    }
    .price-content {
      > p {
        > span {
          padding-right: 5px !important;
          padding-left: 0 !important;
        }
      }
    }
  }

  .list {
    background: #fff;
    padding: 7px 14px;
    box-sizing: border-box;
    color: #aaa;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;

    span {
      color: #666;
      flex: 1;
      padding-left: 15px;
      text-align: right;
      &.total {
        font-weight: bold;
        color: var(--site-main-color);
      }
    }

    > .flex {
      align-items: center;
      img {
        margin-left: 8px;
      }
    }
  }

  .info-list {
    background-color: #fff;
    padding: 7px 14px;
    box-sizing: border-box;
    color: #aaa;
    display: flex;
    justify-content: space-between;
    font-size: 14px;
    > div {
      flex: 1;
      padding-left: 15px;
      text-align: right;
      color: #666;
    }
  }

  .over {
    background: #fff;
    padding: 7px 14px;
    box-sizing: border-box;
    color: #aaa;
    display: flex;
    font-size: 14px;

    span:nth-child(1) {
      width: 30%;
    }

    span:nth-child(2) {
      width: 70%;
      text-align: right;
      color: #666;
    }
  }
}

.listitem {
  background: #fff;
  border-radius: 5px;
  padding: 10px;
  box-sizing: border-box;
  position: relative;
  margin: 15px;
  &.is-ar {
    .name {
      padding-left: 0;
      padding-right: 10px;
    }
  }
  > .goods-info {
    display: flex;
    align-items: center;
  }

  > .goods-sn {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 10px;
    margin-bottom: 10px;
    font-size: 14px;
    font-weight: bold;
    border-bottom: 1px solid #eee;
    > div {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: flex-end;
      > p {
        margin: 0 5px;
      }
    }
  }

  .pic {
    width: 80px;
    height: 80px;
    text-align: center;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  .name {
    flex: 1;
    padding-left: 10px;

    .title {
      font-size: 15px;
      font-weight: bold;
      overflow: hidden;
      word-break: break-all;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 2;
    }

    .spec {
      > .item {
        display: flex;
        font-size: 13px;
        color: #aaa;
        > p:last-child {
          color: #333;
          flex: 1;
        }
      }
    }

    .col {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 13px;
      color: #aaa;
      margin-top: 5px;
    }

    .money {
      color: var(--site-main-color);
    }

    span:last-child {
      color: var(--site-main-color);
    }
  }
}

.bottom {
  padding-top: 0px;
  padding-bottom: 15px;
}


.line {
  padding: 10px;
  box-sizing: border-box;
  background: #fff;

  div {
    font-size: 15px;
    font-weight: bold;
    color: #aaa;
    height: 30px;
    line-height: 30px;
    position: relative;

    span {
      position: absolute;
      right: 0px;
      color: #666;
    }
  }
}

.btn {
  position: fixed;
  width: 100%;
  bottom: 0px;
  left: 0px;
  padding: 10px;
  box-sizing: border-box;

  div {
    height: 40px;
    line-height: 40px;
    text-align: center;
    border-radius: 5px;
    background: var(--site-main-color);
    color: #fff;
  }
}

.right-fixed-enter {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: var(--site-main-color);
  box-shadow: 0px 4.5px 6px rgba(21, 82, 240, 0.25);
  position: fixed;
  right: 10px;
  z-index: 9999;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  pointer-events: none;
  transition: all 0.3s ease;
  &.active {
    opacity: 1;
    pointer-events: auto;
  }
  &.message {
    margin-top: 60px;
  }
  > img {
    width: 28px;
    height: auto;
  }
}

.price-content {
  > p {
    font-size: 14px;
    color: #666;
    text-align: right;
    > span {
      color: #1552F0 !important;
      font-weight: bold;
      padding-left: 5px !important;
    }
  }
}
</style>
