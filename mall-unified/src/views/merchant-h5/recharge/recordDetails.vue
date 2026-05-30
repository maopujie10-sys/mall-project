<template>
  <div>
    <fx-header fixed>
      <template #title>{{ t('充值详情') }}</template>
    </fx-header>
    <div style="height: 46px;" />

    <div class="details-content" :class="{'is-ar': isArLang}">
      <div v-if="!pageLoading" class="content">
        <div v-for="item in infoDataRef" :key="item.key" class="item">
          <p>{{ t(item.title) }}：</p>
          <div :class="{'copy': item.copy}">
            <span v-if="item.key === 'state'" :class="`color-${item.info}`">{{ getStatusName(item.info) }}</span>
            <span v-else-if="item.key === 'img'" class="img" @click="imgPreview(item.info)">
              <img :src="item.info" alt="">
            </span>
            <span v-else :class="{'color': item.color, 'color-2': item.redColor}">{{ item.isNum ? numberStrFormat(item.info, ['BTC', 'ETH'].includes(item.unit) ? 6 : 2) : item.info }}</span>
            <span v-if="item.unit" :class="{'color': item.color}" class="unit">{{ item.unit }}</span>
            <svg
              v-if="item.copy && item.info"
              @click="handleCopy(item.info)"
              xmlns="http://www.w3.org/2000/svg"
              width="18"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="feather feather-copy"
            >
              <rect
                x="9"
                y="9"
                width="13"
                height="13"
                rx="2"
                ry="2"
              ></rect>
              <path
                d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"
              ></path>
            </svg>
          </div>
        </div>
      </div>
    </div>
    <div v-if="isBank && !pageLoading && Number(dataInfo.state === 0) && dataInfo.payUrl" class="btn-content">
      <van-button type="primary" @click="openPage(dataInfo.payUrl, true)">{{ t('去支付') }}</van-button>
    </div>
  </div>
</template>

<script setup  name="RechageRecordDetails">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { Toast, ImagePreview } from 'vant';
import useClipboard from 'vue-clipboard3'
import {useI18n} from 'vue-i18n'
import { rechargeDetailsApi } from '@/service/exchange.api'
import { numberStrFormat, openPage } from '@/utils'
import { arLangCheck } from '@/utils/arLangCheck'
import cloneDeep from 'lodash.clonedeep'
import 'vant/es/image-preview/style';

const isArLang = arLangCheck()
const pageLoading = ref(true)
const infoData = [
  {
    title: '订单号',
    info: '',
    copy: true,
    key: 'order_no'
  },
  {
    title: '创建时间',
    info: '',
    key: 'create_time'
  },
  {
    title: '充值数量',
    info: '',
    color: true,
    key: 'volume',
    isNum: true,
    unit: 'USDT'
  },
  {
    title: '实际到账',
    info: '',
    color: true,
    key: 'amount',
    isNum: true,
    unit: 'USDT'
  },
  {
    title: '订单状态',
    info: '',
    color: true,
    key: 'state'
  },
  {
    title: '币种协议',
    info: '',
    key: 'coin_blockchain'
  },
  {
    title: '收款地址',
    info: '',
    copy: true,
    key: 'channel_address'
  },
  {
    title: '支付凭证',
    info: '',
    key: 'img'
  }
]

const infoDataRef = ref([])

const route = useRoute()
const failureMsg = ref('')
const { t } = useI18n()
const { toClipboard } = useClipboard()
const isBank = ref(false)
const dataInfo = ref(null)

const order_no = route.query.order_no
const isThirdParty = route.query.isThirdParty || 0

isBank.value = Boolean(Number(isThirdParty))

if (isBank.value) {
  const dataArr = cloneDeep(infoData)
  for (let i = 0 ; i < dataArr.length; i++) {
    if (['coin_blockchain', 'channel_address', 'img'].includes(dataArr[i].key)) {
      dataArr.splice(i--, 1)
    }
  }
  infoDataRef.value = dataArr
} else {
  infoDataRef.value = infoData
}

if (route.query.r) {
  failureMsg.value = route.query.r
  const index = infoDataRef.value.findIndex(item => item.key === 'state')
  infoDataRef.value.splice(index + 1, 0, {
    title: '失败原因',
    info: '',
    redColor: true,
    key: 'failure_msg'
  })
}


if (order_no) {
  pageLoading.value = true
  Toast.loading({
    duration: 0,
    forbidClick: true
  })
  rechargeDetailsApi({
    order_no
  }).then(res => {
    dataInfo.value = res
    const itemObj = infoDataRef.value.find(item => item.key === 'volume')
    itemObj.unit = res.coin

    infoDataRef.value.forEach(item => {
      item.info = item.key === 'failure_msg' ? failureMsg.value : res[item.key]
    })
  }).finally(() => {
    Toast.clear()
    pageLoading.value = false
  })
} else {
  Toast(t('参数错误'))
}

const getStatusName = (status) => {
  const statusMap = {
    0: t('processing'),
    1: t('successful'),
    2: t('failure')
  }
  return statusMap[status] ?? ''
}

const handleCopy = async (txt) => {
  try {
    await toClipboard(txt);
    Toast(t('copySuccess'));
  } catch (e) {
    console.error(e);
  }
}

const imgPreview = (data) => {
  ImagePreview({
    images: [data],
    showIndex: false,
    loop: false
  })
}
</script>

<style lang="scss" scoped>
  .details-content {
    padding: 15px;
    &.is-ar {
      .content > .item > div {
        padding-left: 0;
        padding-right: 20px;
        &.copy > span {
          text-align: left;
          padding-right: 0;
          padding-left: 10px;
        }
        .unit {
          padding-left: 0;
          padding-right: 5px;
        }
      }
    }
    > .content {
      background-color: #fff;
      border-radius: 4px;
      overflow: hidden;
      
      > .item {
        padding: 15px;
        position: relative;
        display: flex;
        justify-content: space-between;
        min-height: 50px;
        align-items: center;
        > p {
          color: #999;
          font-size: 14px;
        }
        > div {
          color: #333;
          flex: 1;
          padding-left: 20px;
          display: flex;
          justify-content: flex-end;
          align-items: center;
          &.copy {
            > span {
              flex: 1;
              text-align: right;
              padding-right: 10px;
            }
            svg {
              color: $text-color-light;
            }
          }
          > span {
            font-size: 14px;
            word-break: break-all;
            &.unit {
              padding-left: 5px;
            }
            &.img {
              display: flex;
              align-items: center;
              justify-content: center;
              width: 70px;
              height: 70px;
              border-radius: 4px;
              overflow: hidden;
              background-color: #ddd;
              > img {
                width: 100%;
                height: auto;
              }
            }
            &.color-1 {
              color: #0ecb81;
            }

            &.color-2 {
              color: #ff3e3e;
            }

            &.color,
            &.color-0 {
              color: $primary-color;
            }
          }
        }
        &:last-child {
          &::after {
            display: none;
          }
        }
        &::after {
          content: '';
          display: block;
          width: calc(100% - 30px);
          height: 1px;
          background-color: #eee;
          position: absolute;
          left: 15px;
          bottom: 0;
        }
      }
    }
  }
  .btn-content {
    padding: 15px;
    :deep(.van-button) {
      width: 100%;
      background-color: var(--site-main-color);
      border-color: var(--site-main-color);
    }
  }
</style>
