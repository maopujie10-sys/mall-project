<template>
  <div class="seller-level-content">
    <fx-header :fixed="true">
      <template #title>
        {{ t('卖家等级') }}
      </template>
    </fx-header>
    <div style="height: 46px" />

    <div
      :style="{ 'background-image': 'url(' + bannerBg + ')' }"
      class="seller-banner"
    >
      <!-- <h2 v-html="$t('升级销量扶持')"></h2>
      <h2 v-html="$t('轻松月入过万')"></h2> -->
    </div>

    <div class="info-content">
      <div class="ads-info">
        <h2 v-html="$t('升级销量扶持')"></h2>
        <h2 v-html="$t('轻松月入过万')"></h2>
      </div>
      <div class="current-num-info">
        <p v-if="currentChildNum">
          {{ t('当前分店人数') }}：<span>{{ currentChildNum }}</span>
        </p>
        <p v-if="currentTeamNum">
          {{ t('当前团队人数') }}：<span>{{ currentTeamNum }}</span>
        </p>
      </div>
      <div
        v-for="(item, index) in introDataRef"
        :key="index"
        class="intro-item"
      >
        <h2>{{ index + 1 }}.{{ $t(item.title) }}</h2>
        <div v-for="intro in item.data" :key="intro">
          <h2 v-if="intro.title">{{ $t(intro.title) }}</h2>
          <p
            v-if="intro.info.indexOf('money') > -1"
            v-html="t(intro.info, { money: limitSellerRechargeAmount })"
          ></p>
          <p
            v-else-if="intro.info.indexOf('totalMoney') > -1"
            v-html="t(intro.info, { totalMoney: limitTeamRechargeAmount })"
          ></p>
          <p v-else>{{ $t(intro.info) }}</p>
        </div>
      </div>

      <div class="level-content">
        <div
          v-for="item in levelDataRef"
          :key="item.name"
          :class="item.name"
          class="level-item"
        >
          <div class="top-content" :class="{ 'is-ar': isArLang }">
            <div class="name-content">
              <div class="title">
                {{ item.name }}-{{ $t('等级卖家') }}
                <span v-if="currentLevel === item.name">{{
                  $t('当前的')
                }}</span>
              </div>
              <p v-if="!hideRechargeAmountCnd">
                {{ $t('运行资金') }}：{{ item.rechargeAmountCnd }}
              </p>
              <p>{{ $t('分店数') }}：{{ item.popularizeUserCountCnd }}</p>
              <p v-if="item.teamNum">
                {{ $t('团队人数') }}：{{ item.teamNum }}
              </p>
            </div>
            <img :src="item.icon" alt="" />
          </div>
          <div class="rights-content" :class="{ 'is-ar': isArLang }">
            <div class="item">
              <div class="title">
                <img :src="iconImg.icon_01" alt="" />
                <p>{{ $t('销售利润比例') }}：</p>
              </div>
              <p>{{ item.awardView }}</p>
            </div>
            <div class="item">
              <div class="title">
                <img :src="iconImg.icon_02" alt="" />
                <p>{{ $t('平台流量扶持量（每日）') }}：</p>
              </div>
              <p>{{ item.promoteViewDaily }}</p>
            </div>
            <div class="item">
              <div class="title">
                <img :src="iconImg.icon_03" alt="" />
                <p>{{ $t('全球到货时间') }}：</p>
              </div>
              <p>{{ item.deliveryDays }} {{ $t('days') }}</p>
            </div>
            <div class="item">
              <div class="title">
                <img :src="iconImg.icon_07" alt="" />
                <p>{{ $t('采购优惠') }}：</p>
              </div>
              <p>{{ item.sellerDiscount }}</p>
            </div>
            <div v-if="!hideUpgradeAward" class="item">
              <div class="title">
                <img :src="iconImg.icon_04" alt="" />
                <p>{{ $t('升级礼金') }}：</p>
              </div>
              <p v-if="item.upgradeCash">
                ${{ numberStrFormat(item.upgradeCash) }}
              </p>
              <img v-else :src="iconImg.icon_close" alt="" />
            </div>
            <div v-if="item.goodsNum" class="item">
              <div class="title">
                <img :src="iconImg.icon_09" alt="" />
                <p>{{ $t('可售商品数量') }}：</p>
              </div>
              <p>{{ item.goodsNum }}</p>
            </div>
            <div class="item">
              <div class="title">
                <img :src="iconImg.icon_05" alt="" />
                <p>{{ $t('专属客服') }}：</p>
              </div>
              <img
                :src="
                  item.hasExclusiveService
                    ? iconImg.icon_check
                    : iconImg.icon_close
                "
                alt=""
              />
            </div>
            <div class="item">
              <div class="title">
                <img :src="iconImg.icon_06" alt="" />
                <p>{{ $t('首页推荐') }}：</p>
              </div>
              <img
                :src="
                  item.recommendAtFirstPage
                    ? iconImg.icon_check
                    : iconImg.icon_close
                "
                alt=""
              />
            </div>
            <div
              v-if="item.name === 'SS' && ['familyShop'].includes(mode)"
              class="item"
            >
              <div class="title">
                <img :src="iconImg.icon_08" alt="" />
                <p>{{ $t('成为供货商') }}：</p>
              </div>
              <img :src="iconImg.icon_check" alt="" />
            </div>
            <div v-if="levelCanBuy && item.showLevelBuy" class="level-sale-content item">
              <p>{{ t('等级售价') }}：${{ item.price }}</p>
              <van-button class="buy-btn" size="small" @click="levelBuyHandle(item)">{{ t('购买等级') }}</van-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <van-action-sheet v-model:show="passwordShow" :title="t('shopSafeTips')">
      <div style="height: 22rem">
        <van-password-input
            :length="6"
            :value="safewordInput"
            :focused="showKeyboard"
            @focus="showKeyboard = true"
        />
        <van-number-keyboard
            v-model="safewordInput"
            :show="showKeyboard"
            @blur="showKeyboard = false"
        />
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup name="SellerLevel">
import { computed, ref, nextTick, watch } from 'vue'
import { Toast, Dialog } from 'vant'
import { useI18n } from 'vue-i18n'
import { introData, levelData } from './config'
import { numberStrFormat, openPage } from '@/utils'
import { arLangCheck } from '@/utils/arLangCheck'
import { useUserStore } from '@/store/user.js'
import clonedeep from 'lodash.clonedeep'
import Decimal from 'decimal.js'

import { malllevelList, mallLevelBuy, sellerInfo } from '@/service/shop.api.js'
import { getSysparaAction } from '@/service/user.api.js'

const { t } = useI18n()
const userStore = useUserStore()

const mode = import.meta.env.MODE
const hideUpgradeAward = computed(() => {
  return ['inchoi'].includes(mode)
})
const hideRechargeAmountCnd = computed(() => {
  return ['shop2u'].includes(mode)
})
const isArLang = arLangCheck()

const currentChildNum = ref(0)
const currentTeamNum = ref(0)

const introDataRef = ref([...clonedeep(introData)])
if (hideUpgradeAward.value) {
  const hideArr = ['升级礼金']
  for (let i = 0; i < introDataRef.value.length; i++) {
    if (introDataRef.value[i].data && introDataRef.value[i].data.length) {
      for (let j = 0; j < introDataRef.value[i].data.length; j++) {
        if (hideArr.includes(introDataRef.value[i].data[j].title)) {
          introDataRef.value[i].data.splice(j--, 1)
        }
      }
    }
  }
}

if (['shop2u'].includes(mode)) {
  for (let i = 0; i < introDataRef.value.length; i++) {
    if (introDataRef.value[i].data && introDataRef.value[i].data.length) {
      for (let j = 0; j < introDataRef.value[i].data.length; j++) {
        if (introDataRef.value[i].data[j].title === '会员升级') {
          introDataRef.value[i].data[j].info =
            '会员升级是通过直属推分店数决会员级别，分店数越高，系统将自动升级。'
        }
      }
    }
  }
}

const currentLevel = ref('')

const levelDataClone = clonedeep(levelData)
if (['greenMall', 'hive', 'iceland', 'inchoi', 'int', 'mbuy', 'simon', 'tiktok-wholesale', 'tiktokMall'].includes(mode)) {
  const index = levelDataClone.findIndex((item) => item.name === 'SS')
  levelDataClone.splice(index, 1)
}
if (['familyShop', 'greenMall', 'hive', 'iceland', 'inchoi', 'int', 'mbuy', 'simon', 'sm', 'tiktok-wholesale', 'tiktokMall'].includes(mode)) {
  const index = levelDataClone.findIndex((item) => item.name === 'SSS')
  levelDataClone.splice(index, 1)
}
const levelDataRef = ref([...levelDataClone])

// 升级礼金固定
const isFixedUpgradeCash = computed(() => {
  return ['shop2u'].includes(mode)
})

const bannerBg = new URL('@/assets/image/level/banner.png', import.meta.url)
const iconImg = {
  icon_01: new URL('@/assets/image/level/icon_01.png', import.meta.url),
  icon_02: new URL('@/assets/image/level/icon_02.png', import.meta.url),
  icon_03: new URL('@/assets/image/level/icon_03.png', import.meta.url),
  icon_04: new URL('@/assets/image/level/icon_04.png', import.meta.url),
  icon_05: new URL('@/assets/image/level/icon_05.png', import.meta.url),
  icon_06: new URL('@/assets/image/level/icon_06.png', import.meta.url),
  icon_06: new URL('@/assets/image/level/icon_06.png', import.meta.url),
  icon_07: new URL('@/assets/image/level/icon_07.png', import.meta.url),
  icon_08: new URL('@/assets/image/level/icon_08.png', import.meta.url),
  icon_09: new URL('@/assets/image/level/icon_09.png', import.meta.url),
  icon_check: new URL('@/assets/image/level/icon_check.png', import.meta.url),
  icon_close: new URL('@/assets/image/level/icon_close.png', import.meta.url)
}

const limitSellerRechargeAmount = ref(100)
const limitTeamRechargeAmount = ref(100)
const levelCanBuy = ref(false)

const pageInit = async () => {
  Toast.loading({
    duration: 0,
    message: t('loading'),
    forbidClick: true
  })
  await sellerInfo().then((res) => {
    currentLevel.value = res.mallLevel
    currentChildNum.value = res.childNum || 0
    currentTeamNum.value = res.teamNum || 0
  })

  await getSysparaAction(
    'valid_recharge_amount_for_team_num,valid_recharge_amount_for_seller_upgrade,level_is_support_purchase'
  ).then((res) => {
    limitSellerRechargeAmount.value = res.valid_recharge_amount_for_seller_upgrade
    limitTeamRechargeAmount.value = res.valid_recharge_amount_for_team_num
    levelCanBuy.value = Number(res.level_is_support_purchase)
  })

  malllevelList()
  .then((res) => {
    const data = res.result || []
    if (data.length) {
      // 等级数组
      const levelArr = data.map(item => item.level)
      const currentLevelIndex = levelArr.findIndex(item => item === currentLevel.value)
      // 升级礼金固定值
      const dataArr = [100, 500, 700, 1000, 1500, 2000]
      levelDataRef.value.forEach((item) => {
        data.forEach((_item, _index) => {
          if (item.name === _item.level) {
            item.level = _item.level
            item.rechargeAmountCnd = _item.rechargeAmountCnd
            item.popularizeUserCountCnd = _item.popularizeUserCountCnd
            item.awardView =
              _item.profitRationMin || _item.profitRationMax
                ? `${new Decimal(_item.profitRationMin).mul(
                    100
                  )}%~${new Decimal(_item.profitRationMax).mul(100)}%`
                : '-'
            item.promoteViewDaily = _item.promoteViewDaily
            item.deliveryDays = _item.deliveryDays
            item.upgradeCash = isFixedUpgradeCash.value
              ? dataArr[_index]
              : Number(_item.upgradeCash)
            item.sellerDiscount = _item.sellerDiscount
              ? `${new Decimal(_item.sellerDiscount).mul(100)}%`
              : 0
            item.hasExclusiveService = Boolean(_item.hasExclusiveService)
            item.recommendAtFirstPage = Boolean(_item.recommendAtFirstPage)
            item.teamNum = _item.teamNum || 0
            item.goodsNum = _item.goodsNum || 0
            item.price = _item.price || 0
            item.showLevelBuy = levelArr.findIndex(item => item === _item.level) > currentLevelIndex
          }
        })
      })
    }
    Toast.clear()
  })
  .catch(() => {
    Toast.clear()
  })
}
const safewordInput = ref('')
const passwordShow = ref(false)
const showKeyboard = ref(true)
const currentBuyLevel = ref(null)

const levelBuyHandle = (data) => {
  const hasSafeword = Boolean(Number(userStore?.userInfo?.safeword))
  if (hasSafeword) {
    passwordShow.value = true
    showKeyboard.value = true
    currentBuyLevel.value = data
  } else {
    Dialog.confirm({
      title: t('dialogTips'),
      message: t('shopSafeWord'),
      cancelButtonText: t('cancel'),
      confirmButtonText: t('gotoSet'),
      confirmButtonColor: '#1552F0',
      cancelButtonColor: '#999'
    }).then(() => {
      openPage('/fundsPasswordSettings')
    }).catch(() => {
      console.log('cancel')
    });
  }
}

const levelBuyRequest = () => {
  Toast.loading({
    duration: 0,
    message: t('loading'),
    forbidClick: true
  })

  const params = {
    level: currentBuyLevel.value.level || currentBuyLevel.value.name,
    safeword: safewordInput.value
  }

  mallLevelBuy(params).then(() => {
    Toast(t('shopBuySuc'))
    setTimeout(() => {
      pageInit()
    }, 1500)
  })
}

watch(passwordShow, (val) => {
  if (!val) {
    safewordInput.value = ''
  }
})

// 密码输入到6位发送请求
watch(() => safewordInput.value, (val) => {
  if (val.length === 6) {
    levelBuyRequest()

    passwordShow.value = false;
    safewordInput.value = ''
  }
})

nextTick(() => {
  pageInit()
})

  
</script>

<style lang="scss" scoped>
.seller-level-content {
  min-height: 100vh;
  background-color: #fff;
}

.seller-banner {
  width: 100%;
  height: 114px;
  background-size: cover;
  background-repeat: no-repeat;
  background-position: center top;
  padding-left: 25px;
  display: flex;
  flex-direction: column;
  justify-content: center;

  > h2 {
    color: #fff;
    font-weight: bold;
    font-size: 28px;
    line-height: 133.69%;

    :deep(span) {
      color: #fdcc2b;
      text-shadow: 1px 1px 0 rgba(0, 0, 0, 0.3);
    }
  }
}

.info-content {
  width: 100%;
  padding: 25px 15px;
  background-color: #fff;
  border-top-right-radius: 20px;
  border-top-left-radius: 20px;
  position: relative;
  top: -10px;

  > .ads-info {
    display: flex;
    align-items: center;

    > h2 {
      font-weight: bold;
      font-size: 18px;
      color: #333;

      :deep(span) {
        color: #1552f0;
      }

      &:first-child {
        margin-right: 20px;
      }
    }
  }

  > .intro-item {
    margin-top: 25px;

    &:first-child {
      margin-top: 0;
    }

    > h2 {
      font-weight: bold;
      font-size: 14px;
      color: var(--site-main-color);
    }

    > div {
      h2 {
        font-size: 12px;
        font-weight: bold;
        color: #333;
        margin-top: 15px;
      }

      p {
        font-size: 12px;
        color: #333;
        margin-top: 5px;
      }

      :deep(span) {
        color: #1552f0;
        padding: 0 2px;
      }
    }
  }
}

.level-content {
  margin-top: 30px;

  .level-item {
    padding: 15px 13px;
    border-radius: 10px;
    margin-top: 15px;

    > .top-content {
      border-bottom: 1.5px solid #fff;
      display: flex;
      justify-content: space-between;
      padding-bottom: 20px;
      align-items: flex-start;

      &.is-ar {
        > .name-content > div > span {
          margin-left: 0;
          margin-right: 10px;
        }
      }

      > .name-content {
        > div {
          font-size: 15px;
          font-weight: bold;
          color: #000;
          margin-bottom: 5px;
          display: flex;
          align-items: center;

          > span {
            display: inline-block;
            background-color: var(--site-main-color);
            font-size: 10px;
            line-height: 1;
            font-weight: normal;
            color: #fff;
            padding: 4px 10px;
            border-radius: 20px;
            margin-left: 10px;
          }
        }

        > p {
          font-size: 12px;
          color: #333;
          line-height: 21px;
        }
      }

      > img {
        width: 75px;
        height: auto;
      }
    }

    > .rights-content {
      &.is-ar {
        > .item > .title > p {
          padding-left: 0;
          padding-right: 5px;
        }
      }

      > .item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 10px;

        > .title {
          display: flex;
          align-items: center;

          > img {
            width: 16px;
            height: auto;
          }

          > p {
            font-size: 12px;
            color: #333;
            padding-left: 5px;
          }
        }

        > p {
          font-size: 12px;
          color: #333;
          font-weight: bold;
        }

        > img {
          width: 13px;
          height: auto;
        }
      }
    }

    &.C {
      background: linear-gradient(180deg, #f2fdff 0%, #e9faff 100%);

      > .top-content {
        border-color: #d6f0f5;
      }
    }

    &.B {
      background: linear-gradient(180deg, #ffeef2 0%, #ffdbd0 100%);

      > .top-content {
        border-color: #f9d2cb;
      }
    }

    &.A {
      background: linear-gradient(180deg, #f9eeff 0%, #f3dfff 100%);

      > .top-content {
        border-color: #ebd0f9;
      }
    }

    &.S {
      background: linear-gradient(180deg, #fff4f0 0%, #ffe5d9 100%);

      > .top-content {
        border-color: #fcded1;
      }
    }

    &.SS {
      background: linear-gradient(
        180deg,
        #fff5f1 0%,
        #ffd6d6 49.48%,
        #ffc5ab 100%
      );

      > .top-content {
        border-color: #fcded1;
      }
    }

    &.SSS {
      background: linear-gradient(
        180deg,
        rgba(250, 225, 255, 1) 0%,
        rgba(250, 215, 255, 1) 49.48%,
        rgba(245, 177, 255, 1) 100%
      );

      > .top-content {
        border-color: rgba(247, 194, 254, 1);
      }
    }
  }
}

.current-num-info {
  display: flex;
  align-items: center;
  margin-top: 10px;
  font-size: 14px;
  > p {
    margin-right: 20px;
    &:last-child {
      margin-right: 0;
    }
    > span {
      font-weight: bold;
      color: #1552f0;
    }
  }
}

.level-sale-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  > p {
    color: var(--site-main-color) !important;
    font-size: 13px;
    font-weight: bold;
  }
  .buy-btn {
    font-size: 13px;
    font-weight: bold;
    color: #fff;
    background-color: var(--site-main-color);
    border-color: var(--site-main-color);
    padding: 1px 20px;
    border-radius: 4px;
  }
}
</style>
