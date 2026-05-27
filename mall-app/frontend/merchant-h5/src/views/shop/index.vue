<template>
  <div :class="{'not-scroll': showNoticPop}" class="page-main-content">
    <van-pull-refresh
      v-model="refreshing"
      :pulling-text="t('pullingText')"
      :loosing-text="t('loosingText')"
      :loading-text="t('loading')"
      :disabled="showNoticPop"
      @refresh="onRefresh"
    >
      <!-- 公告弹窗 -->
      <notic-pop v-model="showNoticPop" :info-data="showNoticInfo"></notic-pop>

      <!-- 新人注册礼金弹窗 -->
      <sign-bonus-pop ref="SignBonusPopRef" />

      <!-- 活动弹窗 -->
      <!-- <div :class="{'active': currentActivityId}" class="activity-pop-content">
        <div class="content">
          <img :src="getImg('activity/turntable/choujiangclose.svg')" class="close" @click="currentActivityId = null" alt="">
          <img :src="getImg('activity/turntable/choujiang.png')" alt="" @click="openActivity">
          <div class="name" @click="openActivity">{{ t('幸运抽奖') }}</div>
        </div>
      </div> -->

      <shop-header ref="shopHeaderRef" :seller-goods-num="sellerGoodsNum" />

      <div class="shop-main-content">
        <div style="padding: 0 15px">
          <van-swipe v-if="showBanner" class="banner-content" :autoplay="5000" indicator-color="white">
            <van-swipe-item v-for="(item, index) in bannerData" :key="index" @click="openService">
              <img :src="item.imgHref" alt="">
            </van-swipe-item>
          </van-swipe>

          <div class="block-content sale-number">
            <div v-for="item in saleDataRef" :key="item.title" class="item">
              <div class="number">
                <count-to
                  v-if="Number(item.number) > 0"
                  prefix="$"
                  :startVal="0"
                  :endVal="item.number"
                  :decimals="2"
                  :duration="1500"
                  :class="{ mini: Number(item.number) > 9999999 }"
                  class="number-count"
                ></count-to>
                <h3 v-else class="number-count">$0.00</h3>
              </div>
              <div class="title" :class="{'is-ar': isArLang}">
                <img :src="item.icon" alt="">
                <p>{{ t(item.title) }}</p>
              </div>
            </div>
          </div>

          <notice-block ref="noticeBlockRef" @done="hasGetNotceDone"></notice-block>

          <div class="block-content today-data">
            <p class="title">{{ t('todayData') }}</p>
            <div class="content" :class="{'is-ar': isArLang}">
              <div
                v-for="item in visitorsDataRef"
                :key="item.title"
                class="item"
              >
                <div class="number">
                  <count-to
                    v-if="Number(item.number) > 0"
                    :startVal="0"
                    :endVal="item.number"
                    :decimals="item.decimals"
                    :duration="1500"
                    class="number-count"
                  ></count-to>
                  <h3 v-else class="number-count">{{ item.decimals ? '0.00' : 0 }}</h3>
                </div>
                <p>{{ t(item.title) }}</p>
                <div class="icon" :class="{'is-ar': isArLang}">
                  <img :src="item.icon" alt="">
                </div>
              </div>
            </div>
          </div>

          <shop-chart v-if="showCharts" ref="shopChartRef" :sellerId="sellerId" />

          <div class="block-content nav-content">
            <div
              v-for="item in navDataRef"
              :key="item.title"
              class="item"
              @click="openNavPage(item.href)"
            >
              <div class="icon"><img :src="item.icon" alt="" /></div>
              <p>{{ t(item.title) }}</p>
            </div>
          </div>

          <div class="stat-item-content">
            <div v-for="(item, index) in statItemDataRef" :key="item.title" class="item">
              <div class="icon"><img :src="item.icon" alt="" /></div>
              <p class="flex items-center">{{ t(item.title) }}  <van-icon @click="goPolicy" :class="isArLang ? 'mr-2': 'ml-2'" color="#cccccc" size="1rem" v-if="index === 2" name="question" /></p>

              <count-to
                v-if="Number(item.number) > 0"
                :prefix="item.prefix"
                :startVal="0"
                :endVal="item.number"
                :decimals="item.decimals"
                :duration="1500"
                class="number-count"
              ></count-to>
              <h3 v-else class="number-count">0</h3>
            </div>
          </div>
          <div v-if="showNormalState" class="stat-block-content">
            <div
              v-for="item in statBlockDataRef"
              :key="item.title"
              class="item"
              :style="{ 'background-color': item.color }"
            >
              <img :src="blockBg.href" alt="" />
              <p>{{ t(item.title) }}</p>
              <count-to
                v-if="Number(item.number) > 0"
                :startVal="0"
                :endVal="item.number"
                :duration="1500"
                class="number-count"
              ></count-to>
              <h3 v-else class="number-count">0</h3>
            </div>
          </div>

          <div v-else class="stat-block-content">
            <div v-for="item in reportDataRef" :key="item.key" class="item" :style="{'background-color': item.color}">
              <img :src="blockBg.href" alt="" />
              <p>{{ t(item.title) }}</p>
              <count-to v-if="Number(item.number) > 0" :prefix="item.prefix" :decimals="item.decimals" :startVal="0" :endVal='item.number' :duration='1500' class="number-count"></count-to>
              <h3 v-else class="number-count">0</h3>
            </div>
          </div>
        </div>

        <div
          v-if="categoryData.length"
          class="data-block-content category-content"
        >
          <div class="title">
            {{ t('yourCategory') }}<span>({{ categoryData.length }})</span>
          </div>
          <div class="scroll-content">
            <div class="item-content">
              <div
                v-for="item in categoryData"
                :key="item.id"
                class="item"
                @click="openClassPage(item)"
              >
                <img :src="item.iconImg" alt="" />
                <div class="info">
                  <p>{{ item.name }}</p>
                  <p>({{ item.goodCount }})</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="data-block-content goods-content">
          <div class="title">{{ t('saleTop10') }}</div>
          <div v-if="goodsData.length" class="content">
            <goods-item
              v-for="item in goodsData"
              :key="item.id"
              :goods-data="item"
            />
          </div>
          <van-empty v-else :image="empytImg.href" :description="t('noData')" />
        </div>

        <div class="safe-area-inset-bottom"></div>
      </div>
    </van-pull-refresh>
  </div>
</template>

<script>
import { defineComponent, ref, nextTick, onMounted, onActivated, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Toast } from 'vant'
import ShopHeader from './components/ShopHeader.vue'
import NoticeBlock from './components/NoticeBlock.vue'
import ShopChart from './components/ShopChart.vue'
import GoodsItem from './components/GoodsItem.vue'
import NoticPop from './components/NoticPop.vue'
import SignBonusPop from './components/SignBonusPop.vue'
import { CountTo } from 'vue3-count-to'
import { useI18n } from 'vue-i18n'
import { openPage, getImg } from '@/utils'
import { useUserStore } from "@/store/user.js";
import { openService } from '@/utils/index.js'
import { useSystemStore } from '@/store/system.js'
import { getCurrentActivity } from '@/service/activity.api.js'
import clonedeep from 'lodash.clonedeep'
import { arLangCheck } from '@/utils/arLangCheck'
import { reportData } from '@/views/FinancialStatements/config'

import {
  saleData,
  visitorsData,
  navData,
  statItemData,
  statBlockData
} from './config'

import {
  sellerInstrumentPanelHead,
  sellerInstrumentPanelStats,
  sellerGoodsList,
  sellerInfo,
  categoryGoodCount,
  sellerReportHead
} from '@/service/shop.api.js'

export default defineComponent({
  name: 'ShopIndex',
  components: {
    ShopHeader,
    NoticeBlock,
    ShopChart,
    GoodsItem,
    CountTo,
    NoticPop,
    SignBonusPop
  },
  setup() {
    const userStore = useUserStore()
    const route = useRoute()
    const router = useRouter()
    const systemStore = useSystemStore()
    const { locale, t } = useI18n()
    const empytImg = new URL(
      '@/assets/image/public/no_data.png',
      import.meta.url
    )
    const shopChartRef = ref(null)
    const SignBonusPopRef = ref(null)
    const refreshing = ref(false)
    const saleDataRef = ref([...saleData])
    const visitorsDataRef = ref([...visitorsData])
    const statItemDataRef = ref([...statItemData])
    const statBlockDataRef = ref([...statBlockData])
    const blockBg = new URL('@/assets/image/shop/bg_01.png', import.meta.url)

    const sellerGoodsNum = ref(0)
    const categoryData = ref([])
    const goodsData = ref([])
    const sellerId = ref('')

    const shopHeaderRef = ref()
    const noticeBlockRef = ref()

    const isArLang = arLangCheck()

    // 抽奖活动
    const currentActivityId = ref(null)
    getCurrentActivity().then(res => {
      currentActivityId.value = res.id || null
    })

    const openActivity = () => {
      const { origin } = window.location
      if (window.plus) {
        const token = userStore?.userInfo?.token
        window.plus.runtime.openURL(`${origin}/www/#/activity/turntable?id=${currentActivityId.value}&token=${token}`)
      } else {
        openPage(`${origin}/www/#/activity/turntable?id=${currentActivityId.value}`, true)
      }
    }

    // 操作导航栏
    const navDataRef = clonedeep(navData)
    const mode = import.meta.env.MODE
    if ([''].includes(mode)) {
      const index = navDataRef.findIndex(item => item.href === '/sellerLevel')
      navDataRef.splice(index, 1)
    }

    if (['familyShop'].includes(mode)) {
      const index = navDataRef.findIndex(item => item.href === '/shop/promotion')
      navDataRef.splice(index, 1)
    }

    if (!['int'].includes(mode)) {
      const index = navDataRef.findIndex(item => item.href === '/gotoBuyer')
      navDataRef.splice(index, 1)
    }

    const reportDataRef = ref([...reportData])
    const showNormalState = computed(() => {
      return !['argos2'].includes(mode)
    })

    const pageDataInit = async (flag = false) => {
      // 基础信息
      if (!flag) {
        await sellerInfo().then((res) => {
          sellerId.value = res ? res.id : ''
        })
      }

      // 注册奖励
      if (SignBonusPopRef.value) {
        SignBonusPopRef.value.getSignBonusInfo()
      }
      
      if (sellerId.value) {
        categoryGoodCount({ sellerId: sellerId.value }).then((res) => {
          categoryData.value = res || []
        })

        sellerInstrumentPanelHead({ sellerId: sellerId.value }).then((res) => {
          saleDataRef.value[0].number = res.head.totalSales || 0
          saleDataRef.value[1].number = res.head.totalProfit || 0

          visitorsDataRef.value[0].number = res.head.visits1Today || 0
          visitorsDataRef.value[1].number = res.head.visits7Today || 0
          visitorsDataRef.value[2].number = res.head.visits30Today || 0
          visitorsDataRef.value[3].number = res.head.todayOrder || 0
          visitorsDataRef.value[4].number = res.head.todaySales || 0
          visitorsDataRef.value[5].number = res.head.todayProfit || 0

          statItemDataRef.value[0].number = res.head.focusCount || 0
          statItemDataRef.value[1].number = res.head.rating || 0
          statItemDataRef.value[2].number = res.head.creditScore || 0
        })

        sellerInstrumentPanelStats({ sellerId: sellerId.value }).then((res) => {
          statBlockDataRef.value[0].number = res.stats.orderNum || 0
          statBlockDataRef.value[1].number = res.stats.orderIng || 0
          statBlockDataRef.value[2].number = res.stats.orderFinish || 0
          statBlockDataRef.value[3].number = res.stats.orderCancel || 0
          statBlockDataRef.value[4] && (statBlockDataRef.value[4].number = res.stats.orderRefund || 0)
        })

        // 统计报表统计数据
        sellerReportHead({
          sellerId: sellerId.value,
          content_type: 0
        }).then(res => {
          const data = res.head
          reportDataRef.value.forEach(item => {
            item.number = data[item.key]
          })
        })

        if (showCharts.value && shopChartRef.value) {
          shopChartRef.value.getChartData()
        }
      }

      await sellerGoodsList({
        pageNum: 1,
        pageSize: 10,
        isHot: '1'
      }).then((res) => {
        sellerGoodsNum.value = res.sellerGoodsNum || 0
        const data = res.pageList || []
        goodsData.value = data.filter(item => item.soldNum)
      })

      if (!flag) {
        shopHeaderRef.value.getStoreInfo()
      }
    }

    const goPolicy = () => {
      const src = `${window.origin}/promote/#/shippingPolicy?lang=${ locale.value }`
      router.push({
        path: '/web-view',
        query: {
          title: t('卖家政策'),
          src
        }
      })
    }

    const onRefresh = async () => {
      shopHeaderRef.value.getStoreInfo()
      await pageDataInit()
      refreshing.value = false
    }

    const openClassPage = (data) => {
      const { name, categoryId } = data
      const query = {
        name,
        id: categoryId,
        sellerId: sellerId.value
      }

      openPage({
        path: '/shop/class',
        query
      })
    }

    nextTick(async () => {
      const { token, from, lang } = route.query
      if (from === 'shop') {
        if (lang) {
          locale.value = lang
          localStorage.setItem('lang', lang)
        }
        if (token) {
          Toast.loading({duration: 0})
          await userStore.getUserInfo(true, token)
        }
        pageDataInit()
      } else {
        pageDataInit()
      }
    })

    onMounted(() => {
      document.addEventListener('shopHomeRefresh', () => {
        pageDataInit()
      })

      document.addEventListener('langChange', () => {
        noticeBlockRef.value && noticeBlockRef.value.getCmsData()
        pageDataInit()
      })
    })

    onActivated(() => {
      if (sellerId.value) {
        nextTick(() => {
          refreshing.value && (refreshing.value = false)
          shopHeaderRef.value && shopHeaderRef.value.getStoreInfo()
          pageDataInit(true)
          // shopChartRef.value && shopChartRef.value.getChartData()
        })
      }
    })

    const bannerData = [
      {
        imgHref: new URL('@/assets/image/shop/banner/1.png', import.meta.url),
        href: '/customerService'
      },
      {
        imgHref: new URL('@/assets/image/shop/banner/2.png', import.meta.url),
        href: '/customerService'
      }
    ]

    const showBanner = computed(() => {
      return bannerData.length && ['shopee'].includes(mode)
    })

    const showNoticPop = ref(false)
    const showNoticInfo = ref('')
    const hasGetNotceDone = (data) => {
      if (systemStore.showNotic && data) {
        showNoticInfo.value = data
        showNoticPop.value = true
        systemStore.setShowNotic(false)
      }
    }

    const openNavPage = (href) => {
      if (href === '/gotoBuyer') {
        const {hostname, origin} = window.location
        const href = hostname === 'localhost' ? 'https://www.catvg.xyz' : `${origin}`
        window.location.href = href
      } else {
        openPage(href)
      }
    }

    const showCharts = computed(() => {
      return !['int'].includes(mode)
    })

    return {
      t,
      empytImg,
      saleDataRef,
      visitorsDataRef,
      navDataRef,
      statItemDataRef,
      statBlockDataRef,
      blockBg,
      categoryData,
      goodsData,
      sellerId,
      sellerGoodsNum,
      openPage,
      getImg,
      refreshing,
      shopChartRef,
      SignBonusPopRef,
      onRefresh,
      shopHeaderRef,
      noticeBlockRef,
      showBanner,
      bannerData,
      openClassPage,
      goPolicy,
      openService,
      isArLang,
      reportDataRef,
      showNormalState,
      showNoticPop,
      showNoticInfo,
      showCharts,
      currentActivityId,
      hasGetNotceDone,
      openNavPage,
      openActivity
    }
  }
})
</script>

<style lang="scss" scoped>
.not-scroll {
  pointer-events: none !important;
}
.shop-main-content {
  position: relative;
  top: -42px;
  // padding: 0 15px;
  padding-bottom: 20px;
  .block-content {
    background-color: #fff;
    border-radius: 4px;
    margin-bottom: 15px;
  }
  .sale-number {
    padding: 15px 0;
    display: flex;
    align-items: center;
    position: relative;
    &::after {
      content: '';
      display: block;
      width: 1px;
      height: 27px;
      background-color: #f6f6f6;
      position: absolute;
      top: 50%;
      left: 50%;
      margin-top: -13.5px;
      margin-left: 0.5px;
    }
    > .item {
      width: 50%;
      padding: 0 15px 0 25px;
      .number {
        width: 100%;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        .number-count {
          font-size: 24px;
          color: var(--site-main-color);
          font-weight: bold;
          &.mini {
            font-size: 18px;
          }
        }
      }
      > .title {
        margin-top: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        &.is-ar {
          > img {
            margin-left: 4px;
            margin-right: 0;
          }
        }
        > img {
          width: 15px;
          margin-right: 4px;
        }
        > p {
          color: #999;
          font-size: 12px;
        }
      }
    }
  }
  .today-data {
    padding: 15px 17px;
    > .title {
      font-size: 14px;
      color: #000;
      font-weight: bold;
    }
    > .content {
      overflow: hidden;
      margin-top: 20px;
      display: flex;
      flex-wrap: wrap;
      &.is-ar {
        > .item {
          margin-right: 0;
          margin-left: 4%;
          &:nth-child(2n) {
            margin-left: 0;
          }
        }
      }
      > .item {
        width: 48%;
        margin-top: 20px;
        margin-right: 4%;
        background-color: #F7F8FB;
        border-radius: 4px;
        overflow: hidden;
        padding: 15px 10px;
        position: relative;
        &:nth-child(-n + 2) {
          margin-top: 0;
        }
        &:nth-child(2n) {
          margin-right: 0;
        }
        .number {
          width: 100%;
          height: 24px;
          display: flex;
          align-items: center;
          position: relative;
          z-index: 2;
          .number-count {
            font-size: 18px;
            color: #000;
            font-weight: bold;
          }
        }
        > p {
          color: #999;
          font-size: 12px;
          margin-top: 10px;
          line-height: 1;
          position: relative;
          z-index: 2;
        }
        > .icon {
          position: absolute;
          z-index: 1;
          width: 28px;
          height: 28px;
          border-radius: 50%;
          background-color: #fff;
          overflow: hidden;
          right: 10px;
          top: 50%;
          transform: translateY(-50%);
          &.is-ar {
            right: calc(100% - 38px) !important;
          }
        }
      }
    }
  }

  .nav-content {
    overflow: hidden;
    padding: 18px 0;
    > .item {
      float: left;
      width: 33.3333%;
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-top: 20px;
      padding: 0 5px;
      &:nth-child(-n + 3) {
        margin-top: 0;
      }
      > .icon {
        width: 30px;
        height: 30px;
      }
      > p {
        width: 100%;
        font-size: 12px;
        color: #000;
        margin-top: 5px;
        text-overflow: ellipsis;
        overflow: hidden;
        white-space: nowrap;
        text-align: center;
      }
    }
  }

  .stat-item-content {
    > .item {
      background-color: #fff;
      border-radius: 4px;
      padding: 15px;
      display: flex;
      align-items: center;
      margin-bottom: 15px;
      > .icon {
        width: 30px;
        height: 30px;
      }
      > p {
        flex: 1;
        font-size: 14px;
        padding: 0 12px;
      }
      .number-count {
        font-size: 18px;
        font-weight: bold;
      }
    }
  }

  .stat-block-content {
    overflow: hidden;
    > .item {
      float: left;
      width: calc((100% - 15px) / 2);
      margin-right: 15px;
      margin-top: 15px;
      padding: 10px;
      border-radius: 4px;
      overflow: hidden;
      position: relative;
      &:nth-child(-n + 2) {
        margin-top: 0;
      }
      &::before {
        content: '';
        display: block;
        width: 72px;
        height: 72px;
        border-radius: 50%;
        background-color: rgba(255, 255, 255, 0.1);
        position: absolute;
        top: -36px;
        right: -36px;
        z-index: 1;
      }
      &:nth-child(2n) {
        margin-right: 0;
      }
      > img {
        width: 100%;
        height: auto;
        position: absolute;
        left: 0;
        bottom: 0;
        z-index: 1;
      }
      > p {
        font-size: 14px;
        color: #fff;
        position: relative;
        z-index: 2;
      }
      .number-count {
        font-size: 20px;
        font-weight: bold;
        color: #fff;
        display: inline-block;
        width: 100%;
        text-align: right;
        margin-top: 20px;
        position: relative;
        z-index: 2;
      }
    }
  }

  .data-block-content {
    margin-top: 23px;
    > .title {
      font-size: 14px;
      color: #333;
      padding: 0 15px;
    }
  }

  .category-content {
    > .scroll-content {
      margin-top: 13px;
      width: 100vw;
      overflow-x: scroll;
      > .item-content {
        white-space: nowrap;
        float: left;
        > .item {
          display: inline-block;
          vertical-align: top;
          width: 120px;
          height: 140px;
          border-radius: 4px;
          overflow: hidden;
          margin-right: 15px;
          position: relative;
          &:first-child {
            margin-left: 15px;
          }
          > img {
            width: 100%;
            height: 100%;
          }
          > .info {
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.4);
            position: absolute;
            top: 0;
            left: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            > p {
              color: #fff;
              font-size: 12px;
              line-height: 16px;
            }
          }
        }
      }
    }
  }

  .goods-content {
    > .content {
      padding: 0 15px;
      margin-top: 13px;
    }
  }

  .banner-content {
    margin-bottom: 15px;
    border-radius: 4px;
    overflow: hidden;
    :deep(.van-swipe-item) {
      width: 100%;
      height: 31.5vw;
      border-radius: 4px;
      overflow: hidden;
      background-color: #fff;
      > img {
        width: 100%;
        height: 100%;
      }
    }
  }
}

.activity-pop-content {
  width: 94px;
  position: fixed;
  top: 50%;
  transform: translateY(-50%);
  right: 15px;
  z-index: 99;
  opacity: 0;
  pointer-events: none;
  transition: all 0.3s ease;
  &.active {
    opacity: 1;
    pointer-events: auto;
  }
  > .content {
    width: 100%;
    position: relative;
    > .close {
      position: absolute;
      right: 0;
      top: -5px;
    }
    > .name {
      position: absolute;
      bottom: -10px;
      left: 50%;
      transform: translateX(-50%);
      text-align: center;
      white-space: nowrap;
      font-size: 11px;
      height: 20px;
      line-height: 20px;
      padding: 0 10px;
      border: 1px solid #FFDE49;
      border-radius: 20px;
      background-image: linear-gradient(#9F3DC8, #C975E5);
      color: #fff;
    }
  }
}
</style>
