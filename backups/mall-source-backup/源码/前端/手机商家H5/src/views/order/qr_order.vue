<template>
  <div>
    <fx-header fixed>
      <template #title>
        {{ $t('采购确认') }}
      </template>
    </fx-header>
    <div style="height: 46px;" />

    <van-list v-model:loading="loading" :finished="finished" :loading-text="t('loading')" @load="getListData">
      <div class="list" :class="{'is-ar': isArLang}">
        <div class="listitem" v-for="item in shopList">
          <div class="pic">
            <img style="object-fit: contain" :src="item.goodsIcon"/>
          </div>
          <div class="name">
            <p class="title">{{ item.goodsName }}</p>
            <p class="col">{{ $t('采购数量') }}</p>
            <p class="title money">${{ numberStrFormat(item.systemPrice) }}</p>
            <span>x{{ item.goodsNum }}</span>
          </div>
        </div>
      </div>
    </van-list>

    <div class="line-content" :class="{'is-ar': isArLang}" v-if="Object.keys(orderInfo).length > 0">
      <div class="line">
        <div class="line-item">
          <p>{{ $t('买家付款') }}</p>
          <p class="count">${{ numberStrFormat(orderInfo.prizeReal) }}</p>
        </div>
        <div class="line-item">
          <p>{{ $t('采购金额') }}</p>
          <p class="count">${{ numberStrFormat(orderInfo.systemPrice) }}</p>
        </div>
        <div v-if="orderInfo.sellerDiscountPrice" class="price-content">
          {{ t('优惠价') }}<span>${{ numberStrFormat(orderInfo.sellerDiscountPrice) }}</span>, {{ t('采购优惠') }}<span>{{ new Decimal(orderInfo.sellerDiscount).mul(100) }}%</span>
        </div>
        <div class="line-item">
          <p>{{ $t('采购数量') }}</p>
          <p class="count">{{ orderInfo.goodsCount }}</p>
        </div>
        <div class="line-item">
          <p>{{ $t('利润') }}</p>
          <p class="count">${{ numberStrFormat(orderInfo.profit) }}</p>
        </div>
        <div class="line-item">
          <p>{{ $t('运费') }}</p>
          <p class="count">${{ numberStrFormat(orderInfo.fees) }}</p>
        </div>
        <div class="line-item">
          <p>{{ $t('税') }}</p>
          <p class="count">${{ numberStrFormat(orderInfo.tax) }}</p>
        </div>
        <div class="line-item">
          <p>{{ $t('合计') }}</p>
          <p class="count">${{ totalNum }}</p>
        </div>
      </div>
    </div>

    <div v-if="!pageLoading && orderInfo.purchStatus / 1 !== 1 && orderInfo.status / 1 !== -1 && orderInfo.status / 1 !== 0 && orderInfo.status / 1 !== 6" class="btn">
      <van-button type="primary" size="large" @click="openInputDialog">
        {{ `${$t('立即支付')} $${totalNum}` }}
      </van-button>
    </div>
      
    <van-action-sheet v-model:show="show" :title="t('请输入交易密码')">
      <div style="height: 22rem">
        <van-password-input
            :length="6"
            :value="value"
            :focused="showKeyboard"
            @focus="showKeyboard = true"
        />
        <van-number-keyboard
            v-model="value"
            :show="showKeyboard"
            @blur="showKeyboard = false"
        />
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup>
import {Toast} from 'vant';
import {useRoute} from "vue-router";
import {ref, onMounted, watch, computed} from "vue";
import {useI18n} from 'vue-i18n';
import {_buyOrder, _orderDetail, _orderDetailList} from "../../service/order.api.js";
import { numberStrFormat } from '@/utils'
import { useOrderStore } from "@/store/order.js";
import { useUserStore } from '@/store/user';
import { arLangCheck } from '@/utils/arLangCheck'
import Decimal from 'decimal.js'
import { unitToPx } from 'vant/lib/utils';

const isArLang = arLangCheck()
const orderStore = useOrderStore()
const userStore = useUserStore()

const {t} = useI18n()
const route = useRoute();
let showKeyboard = ref(true);
// 采购金额
let purchaseAmount = ref(0);
// 采购数量
let purchaseNumber = ref(0);
//利润
let profit = ref(0);
//合计
let count = ref(0);
// 订单列表
const shopList = ref([]);
const loading = ref(false)
const finished = ref(false)
const page = ref({
  pageNum: 1
})
const orderId = route.query.id;

//运费
let fee = ref(0);
//税费
let tax = ref(0);
//密码
const value = ref('');
//show
let show = ref(false)
const orderInfo = ref({})

const pageLoading = ref(true)

// 是否已设置了资金密码
const hasSetSafePass = computed(() => {
  return userStore.userInfo?.safeword
})

// 打开输入密码
const openInputDialog = () => {
  if (hasSetSafePass.value) {
    show.value = true
    showKeyboard.value = true
  } else {
    Toast(t('请设置资金密码'))
    setTimeout(() => {
      router.push({
        path: '/fundsPasswordSettings'
      })
    }, 1500)
  }
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

const getOrderDetail = async () => {
  Toast.loading({
    forbidClick: true,
    duration: 0
  })
  await _orderDetail({
    orderId
  }).then((res) => {
    orderInfo.value = res.orderInfo;
    pageLoading.value = false
    Toast.clear()
  }).catch(() => {
    Toast.clear()
  })
}

onMounted(() => {
  getOrderDetail()
})

/**
 * 确定事件
 */
const submit = () => {
  const orderId = route.query.id;
  const data = {
    orderId,
    safeword: value.value
  }

  _buyOrder(data).then((res) => {
    orderStore.decrement()
    document.dispatchEvent(new CustomEvent('reloadOrderList'))
    setTimeout(() => {
      router.back()
    }, 1000)
  })

}

// 密码输入到6位发送请求
watch(() => value.value, (val) => {
  if (val.length === 6) {
    Toast.loading('');
    submit()

    show.value = false;
    value.value = ''
  }
})

// 合计
const totalNum = computed(() => {
  const { sellerDiscountPrice, systemPrice, fees, tax } = orderInfo.value
  const price = sellerDiscountPrice ? sellerDiscountPrice : systemPrice
  return numberStrFormat(Number(price) + Number(fees) + Number(tax))
})

</script>

<style lang="scss" scoped>
.van-list {
  min-height: 20px;
}

.list {
  padding: 10px 15px 0px 15px;
  box-sizing: border-box;
  &.is-ar {
    .listitem .name {
      padding-left: 0;
      padding-right: 10px;
    }
  }

  .listitem {
    background: #fff;
    margin-bottom: 15px;
    border-radius: 5px;
    display: flex;
    padding: 10px;
    box-sizing: border-box;
    position: relative;

    .pic {
      width: 90px;
      height: 90px;
      text-align: center;

      img {
        height: 90px;
        width: auto;
      }
    }

    .name {
      padding-left: 10px;
      word-break: break-all;
      flex: 1;

      .title {
        font-size: 15px;
        font-weight: bold;
      }

      .col {
        font-size: 13px;
        color: #aaa;
      }

      .money {
        color: var(--site-main-color);
      }

      span {
        position: absolute;
        color: #aaa;
        right: 10px;
        bottom: 35px;
        color: var(--site-main-color);
      }
    }
  }
}

.line-content {
  padding: 0 15px;
  &.is-ar {
    .price-content > span {
      padding-left: 0;
      padding-right: 5px;
    }
  }
}
.line {
  border-radius: 5px;
  padding: 15px;
  box-sizing: border-box;
  background: #fff;
}

.btn {
  width: 100%;
  padding: 0 15px;
  box-sizing: border-box;
  margin-top: 40px;
  padding-bottom: 200px;
  :deep(.van-button--primary) {
    background-color: var(--site-main-color);
    border-color: var(--site-main-color);
    border-radius: 4px;
  }
}

.line-item {
  width: 100%;
  display: flex;
  justify-content: space-between;
  font-size: 15px;
  color: #999;
  p {
    height: 40px;
    line-height: 40px;
    text-align: right;
  }
  .count {
    color: #333;
  }
}
.price-content {
  font-size: 14px;
  line-height: 20px;
  color: #333;
  text-align: right;
  > span {
    color: #1552F0;
    font-weight: bold;
    padding-left: 5px;
  }
}
</style>
