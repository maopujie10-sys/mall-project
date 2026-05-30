<template>
  <div class="record">
    <fx-header fixed>
      <template #title>{{ t('withdrawalRecord') }}</template>
    </fx-header>
    <div class="list-wrap">
      <van-pull-refresh v-model="refreshing" :pulling-text="t('pullingText')" :loosing-text="t('loosingText')" :loading-text="t('loading')" @refresh="onRefresh">
        <van-list v-model:loading="loading" :finished="finished" :loading-text="t('loading')" :finished-text="list.length ? t('product.3') : ''" @load="getListData">
          <ul v-if="list.length">
            <li class="px-2 mt-4 item-list" v-for="(item, idx) in list" :key="idx" :class="{'is-ar': isArLang}" @click="gotoDetails(item)">
              <div class="item">
                <div class="label">{{ $t('rechargeOrderNumber') }}</div>
                <div class="value">
                  <span>{{ item.order_no }}</span>
                  <svg
                    @click.stop="handleCopy(item.order_no)"
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
              <div class="item">
                <div class="label">{{ $t('rechargeOrderTime') }}</div>
                <div class="value">{{ formatZoneDate(item.createTime) }}</div>
              </div>
              <div class="item">
                <div class="label">{{ $t('withdrawOrderAmount') }}</div>
                <div class="value">{{ numberStrFormat(item.volume, ['BTC', 'ETH'].includes(item.coin) ? 6 : 2) }} {{ item.coin_blockchain === 'bank' ? 'USD' : item.coin }}</div>
              </div>
              <div class="item">
                <div class="label">{{ $t('rechargeOrderStatus') }}</div>
                <div class="value" :class="`color-${item.state}`">
                  {{ getStatusName(item.state) }}
                </div>
              </div>
              <div v-if="item.state === 2" class="item">
                <div class="label">{{ $t('失败原因') }}</div>
                <div class="value" :class="`color-${item.state}`">
                  {{ item.failure_msg || '--' }}
                </div>
              </div>
            </li>
          </ul>
          <van-empty v-if="!list.length && !loading" :image="empytImg.href" :description="t('noData')" />
        </van-list>
      </van-pull-refresh>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Toast } from 'vant'
import { exchangeGetWithdrawRecord } from '@/service/exchange.api'
import { useI18n } from 'vue-i18n'
import useClipboard from 'vue-clipboard3'
import { arLangCheck } from '@/utils/arLangCheck'
import { formatZoneDate, numberStrFormat, openPage } from '@/utils'
const { t } = useI18n()

const empytImg = new URL('@/assets/image/public/no_data.png', import.meta.url)

const isArLang = arLangCheck()

// 充值状态 0 初始状态，审核中 1 成功 2 失败
const list = ref([])
const refreshing = ref(false)
const loading = ref(false)
const finished = ref(false)
const { toClipboard } = useClipboard()

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

const page = ref({
  page_no: 1
})

const getListData = () => {
  const params = {
    ...page.value
  }
  exchangeGetWithdrawRecord(params)
    .then((res) => {
      const data = res.elements || []
      list.value = page.value.page_no === 1 ? data : [...list.value, ...data]
      
      loading.value = false
      refreshing.value = false
      finished.value = data.length < res.pageSize
      page.value.page_no++
    })
    .catch(() => {
      finished.value = true
      loading.value = false
      refreshing.value = false
    })
}

const onRefresh = () => {
  loading.value = true
  page.value.page_no = 1
  getListData()
}

const gotoDetails = (data) => {
  const query = {
    order_no: data.order_no
  }
  if (data.state === 2) {
    query.r = data.failure_msg || '--'
  }
  openPage({
    path: '/withdraw/record-details',
    query
  })
}
</script>
<style lang="scss" scoped>

.van-pull-refresh {
  background-color: #EFF2F6;
}

.record {
  padding-top: var(--van-nav-bar-height);
  box-sizing: border-box;

  .item-list {
    &.is-ar {
      .item {
        .value {
          padding-right: 20px;
          padding-left: 0;
          svg {
            margin-right: 4px;
            margin-left: 0 !important;
          }
        }
      }
    }
  }

  .item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: $background-color;
    padding: 10px 15px;
    // border-radius: 4px;
    font-size: 14px;
    &:first-child {
      border-top-left-radius: 4px;
      border-top-right-radius: 4px;
    }
    &:last-child {
      border-bottom-left-radius: 4px;
      border-bottom-right-radius: 4px;
    }

    .label {
      color: $text-color-default;
    }

    .value {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: flex-end;
      color: $text-color-dark;
      word-break: break-all;
      padding-left: 20px;
      svg {
        margin-left: 4px;
        color: $text-color-light;
      }

      &.color-1 {
        color: #0ecb81;
      }

      &.color-2 {
        color: #ff3e3e;
      }

      &.color-0 {
        color: $primary-color;
      }
    }
  }
}
</style>
