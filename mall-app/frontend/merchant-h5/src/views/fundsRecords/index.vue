<template>
  <div>
    <div :class="{'active': showLevel}" class="money-level-content">
      <div class="content">
        <div class="title">
          {{ t('利润去哪里了？') }}
          <van-icon name="cross" class="close" @click="hideMoneyLevel" />
        </div>
        <div class="level-content">
          <div class="item">
            <div class="name">{{ t('一级返佣') }}</div>
            <div class="txt">{{ levelInfo.levle1 }}</div>
          </div>
          <div class="item">
            <div class="name">{{ t('二级返佣') }}</div>
            <div class="txt">{{ levelInfo.levle2 }}</div>
          </div>
          <div class="item">
            <div class="name">{{ t('三级返佣') }}</div>
            <div class="txt">{{ levelInfo.levle3 }}</div>
          </div>
          <van-button class="w-full" type="custom" @click="hideMoneyLevel">{{ $t('确定') }}</van-button>
        </div>
      </div>
      <div class="bg" @click="hideMoneyLevel"></div>
    </div>

    <fxHeader :fixed="true">
      <template #title>
        <span class="font-16 color-333">{{ t('fundingRecords') }}</span>
      </template>
      <template #right>
        <img @click="showSelect = true" class="w-5 h-5" src="@/assets/image/fundsRecords/Frame1277.png" alt="">
      </template>
    </fxHeader>
    <div style="height: 46px;" />
    <van-pull-refresh v-model="refreshing" :pulling-text="t('pullingText')" :loosing-text="t('loosingText')" :loading-text="t('loading')" @refresh="onRefresh">
      <van-list v-model:loading="loading" :finished="finished" :loading-text="t('loading')" :finished-text="list.length ? t('product.3') : ''" @load="getListData">
        <div v-if="list.length">
          <money-log-list
            v-for="item in list"
            :item="item"
            :key="item.id"
            @show="showMoneyLevel"
          />
        </div>
        <van-empty v-if="!list.length && !loading" :image="empytImg.href" :description="t('noData')" />
      </van-list>
    </van-pull-refresh>

    <van-popup v-model:show="showSelect" position="bottom" :close-on-click-overlay="false">
      <div>
        <div class="select-header flex items-center justify-center font-14">
          <div class="cancel" @click="cancelClick">{{ t('取消') }}</div>
          <div class="font-16">{{ t('筛选信息') }}</div>
          <div class="enter" @click="enterClick">{{ t('确定') }}</div>
        </div>
        <SelectList :list="selectListData" v-model="selectVal"/>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import {ref, computed, reactive} from 'vue'
import { useI18n } from 'vue-i18n'
import MoneyLogList from "@/views/fundsRecords/MoneyLogList.vue";
import SelectList from "@/views/fundsRecords/SelectList.vue";
import {_getMoneyLogList} from '@/service/fundsRecords.api.js'

const { t } = useI18n()
const mode = import.meta.env.MODE

const selectListData = [
  {name: '全部', value: ''},
  {name: '充值订单', value: 'recharge'},
  {name: '提现订单', value: 'withdraw'},
  {name: '推广佣金', value: 'brokerage'},
  {name: '商品退款', value: 'return-order-seller'},
  {name: '商品采购', value: 'push-order'},
  {name: '直通车购买', value: 'combo-order'},
  {name: '冻结余额', value: 'freeze_seller_money'},
  {name: '解冻余额', value: 'unfreeze_seller_money'},
  {name: '订单收入', value: 'order-income'},
  {name: '支付订单', value: 'pay-order'},
  {name: '会员退货', value: 'return-order-user'},
  {name: '活动赠送', value: 'first-recharge-bonus'},
  {name: '升级礼金', value: 'mall_level_upgrade_award'},
  {name: '赠送彩金', value: 'jackpot'},
  {name: '邀请奖励', value: 'invitation-rewards'},
  {name: '等级购买', value: 'pay-level'},
  {name: '注册礼金', value: 'sign-bonus'},
]
if (['tiktok-wholesale'].includes(mode)) {
  const index = selectListData.findIndex(item => item.value === 'jackpot')
  selectListData[index].name = '代充值'
}

const selectVal = ref('全部');

const empytImg = new URL('@/assets/image/public/no_data.png', import.meta.url)
const refreshing = ref(false)
const loading = ref(true)
const finished = ref(false)
const currentType = computed(() => {
  const option = selectListData.find(item => item.name === selectVal.value)
  return option ? option.value : ''
})

// 获取数据
const page = ref({
  page_no: 1
})
const list = ref([])

const getListData = () => {
  const params = {
    ...page.value,
    content_type: currentType.value
  }

  _getMoneyLogList(params).then(res => {
    let data = res || []
    data.forEach(item => {
      const itemObj = selectListData.find(_item => _item.value === item.content_type)
      item.typeStr = itemObj ? t(itemObj.name) : item.content_type
    })
    list.value = page.value.page_no === 1 ? data : [...list.value, ...data]
    loading.value = false
    refreshing.value = false

    finished.value = data.length < 20
    page.value.page_no++
  }).catch(() => {
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

const showSelect = ref(false);
const cancelClick = () => {
  showSelect.value = false
}

const enterClick = () => {
  showSelect.value = false
  list.value = []
  onRefresh()
}

const showLevel = ref(false)
const levelInfo = reactive({
  levle1: '0.00',
  levle2: '0.00',
  levle3: '0.00'
})

const showMoneyLevel = (data) => {
  if (data.detail && data.detail.length) {
    const levle1 = data.detail.find(item => Number(item.level) === 1)
    const levle2 = data.detail.find(item => Number(item.level) === 2)
    const levle3 = data.detail.find(item => Number(item.level) === 3)

    levelInfo.levle1 = levle1 ? Number(levle1.rebate).toFixed(2) : '0.00'
    levelInfo.levle2 = levle2 ? Number(levle2.rebate).toFixed(2) : '0.00'
    levelInfo.levle3 = levle3 ? Number(levle3.rebate).toFixed(2) : '0.00'
  }
  showLevel.value = true
}

const hideMoneyLevel = () => {
  levelInfo.levle1 = '0.00'
  levelInfo.levle2 = '0.00'
  levelInfo.levle3 = '0.00'
  showLevel.value = false
}


</script>

<style lang="scss" scoped>
.select-header {
  position: relative;
  height: 50px;

  .cancel, .enter {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
  }

  .cancel {
    left: 15px;
  }

  .enter {
    right: 15px;
    color: var(--site-main-color);
  }
}

.money-level-content {
  &.active {
    > .content {
      top: 50%;
    }
    > .bg {
      opacity: 1;
      pointer-events: auto;
    }
  }
  > div {
    position: fixed;
    transition: all 0.3s ease;
    &.content {
      width: 90vw;
      left: 5vw;
      top: 150vh;
      transform: translateY(-50%);
      background-color: #fff;
      z-index: 999;
      border-radius: 8px;
      > .title {
        width: 100%;
        text-align: center;
        position: relative;
        font-size: 16px;
        font-weight: bold;
        padding: 20px 0;
        .close {
          position: absolute;
          top: 22px;
          right: 15px;
          font-size: 18px;
        }
      }
      > .level-content {
        padding: 20px 15px;
        padding-top: 0px;
        > .item {
          width: 100%;
          height: 44px;
          display: flex;
          align-items: center;
          border: 1px solid #dcdcdc;
          border-radius: 4px;
          margin-bottom: 15px;
          > .name {
            height: 100%;
            line-height: 44px;
            width: 110px;
            background-color: #f0f0f0;
            border-right: 1px solid #dcdcdc;
            text-align: center;
            font-size: 14px;
            overflow: hidden;
          }
          > .txt {
            padding-right: 15px;
            flex: 1;
            text-align: right;
            height: 100%;
            line-height: 44px;
          }
        }
        .van-button--custom {
          color: #fff;
          background-color: var(--site-main-color);
          border-color: var(--site-main-color);
          border-radius: 4px;
          margin-top: 15px;
        }
      }
    }
    &.bg {
      width: 100vw;
      height: 100vh;
      top: 0;
      left: 0;
      background-color: rgba(0, 0, 0, 0.6);
      z-index: 998;
      opacity: 0;
      pointer-events: none;
    }
  }
}
</style>
