<template>
  <div class="shop-promotion">
    <fx-header :fixed="true">
      <template #title>
        {{ t('shopPromotion') }}
      </template>
    </fx-header>
    <div style="height: 46px;" />
    <van-pull-refresh v-model="refreshing" :pulling-text="t('pullingText')" :loosing-text="t('loosingText')" :loading-text="t('loading')" @refresh="onRefresh">
      <van-list v-model:loading="loading" :finished="finished" :loading-text="t('loading')" :finished-text="listData.length ? t('product.3') : ''" @load="getLevelData">
        <div class="promotion-info">
          <div v-for="item in promotionDataRef" :key="item.key" class="item" :class="{'is-ar': isArLang}">
            <p>{{ t(item.title) }}</p>
            <van-field
              v-model="item.value"
              center
              label=""
              placeholder=""
            >
              <template #button>
                <van-button @click="copyHandle(item.value)" size="small" type="primary">{{ t('copy') }}</van-button>
              </template>
            </van-field>
          </div>
        </div>

        <div class="intro-content">
          <p v-html="t('promotionIntro', {level1: levelOne, level2: levelTwo, level3: levelThree})"></p>
          <p>{{ t('以下是分成计算公式：') }}</p>
          <p>{{ t('一级') }} {{ t('好友分成计算公式：佣金 = 商品销售利润 x') }}<span>{{ levelOne }}%</span></p>
          <p>{{ t('二级') }} {{ t('好友分成计算公式：佣金 = 商品销售利润 x') }}<span>{{ levelTwo }}%</span></p>
          <p>{{ t('三级') }} {{ t('好友分成计算公式：佣金 = 商品销售利润 x') }}<span>{{ levelThree }}%</span></p>
          <p>{{ t('我们提供详细的分成计算公式，以便您清晰了解佣金的计算方式。我们鼓励您了解平台的邀请制度规则，以便更好地管理和规划您的佣金收入。我们感谢您的参与，并期待与您共同发展。') }}</p>
        </div>

        <div class="team-content">
          <van-tabs v-model:active="navActive" title-inactive-color="#999999" @change="navChange">
            <van-tab v-for="item in teamNav" :key="item.key" :title="t(item.title)"></van-tab>
          </van-tabs>

          <div v-if="listData.length" class="list-content">
            <div v-for="(item, index) in listData" :key="index" class="item">
              <div class="avatar">
                <img :src="item.avatarImg" alt="">
              </div>
              <div class="info">
                <p class="name">{{ item.name }}</p>
                <p class="rebate">{{ `${(t('shopRebate'))}：$${numberStrFormat(item.income || 0)}`}}</p>
                <div>
                  <!-- <p>{{ `${(t('shopCountOrder'))}：${item.orderCount}`}}</p> -->
                  <p>{{ `${(t('storeName'))}：${item.username}`}}</p>
                  
                  <p>{{ `${(t('shopRegTime'))}：${formatZoneDate(item.regTime)}`}}</p>
                </div>
              </div>
            </div>
          </div>
          <van-empty v-if="!listData.length && !loading" :image="empytImg.href" :description="t('noData')" />
        </div>
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script>
import { defineComponent, ref, computed, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { Toast } from 'vant'
import useClipboard from 'vue-clipboard3'
import { formatZoneDate, numberStrFormat } from '@/utils'
import { arLangCheck } from '@/utils/arLangCheck'
import { promotionData, teamNav } from './../config'
import {
  sellerPromotional,
  promoteLevel
} from '@/service/shop.api.js'

export default defineComponent({
  name: 'shopPromotion',
  setup() {
    const isArLang = arLangCheck()
    const { t } = useI18n()

    const empytImg = new URL('@/assets/image/public/no_data.png', import.meta.url)
    const promotionDataRef = ref([...promotionData])
    const { toClipboard } = useClipboard()
    const copyHandle = async (txt) => {
      try {
        await toClipboard(txt)
        Toast(t('copySuccess'))
      } catch (e) {
        console.error(e);
      }
    }

    const navActive = ref(0)
    const currentLevel = computed(() => {
      return teamNav[navActive.value].key
    })
    const listData = ref([])
    const refreshing = ref(false)
    const loading = ref(true)
    const finished = ref(false)
    const page = ref({
      pageNo: 1,
      pageSize: 10
    })

    const dataFormate = async (data) => {
      const dataArr = []
      for (let i = 0; i < data.length; i++) {
        const obj = {
          ...data[i]
        }
        if (isNaN(Number(data[i].avatar))) {
          obj.avatarImg = data[i].avatar
          dataArr.push(obj)
        } else {
          const avatarNum = data[i].avatar || 'd'
          await import(`./../../../assets/image/avatar/head_${avatarNum}.jpg`).then((res) => {
            obj.avatarImg = res.default
            dataArr.push(obj)
          })
        }
      }
      return dataArr
    }
    
    const getLevelData = async () => {
      const params = {
        ...page.value,
        level: currentLevel.value
      }
      await promoteLevel(params).then(async res => {
        const pageList = res.pageList || []
        console.log(pageList);
        const data = await dataFormate(pageList)

        console.log(data);
        listData.value = page.value.pageNo === 1 ? data : [...listData.value, ...data]
        
        loading.value = false
        refreshing.value = false
        
        finished.value = data.length < page.value.pageSize
        page.value.pageNo++
      }).catch(() => {
        refreshing.value = false
        loading.value = false
        finished.value = true
      })
  
      sellerPromotional().then(res => {
        const uuu = window.location.hostname
        promotionDataRef.value[0].value = res.download && res.code ? `${res.download}/#?usercode=${res.code}&lang=${locale.value}` : `https://${uuu}/promote?usercode=${res.code}&lang=${locale.value}`
        promotionDataRef.value[1].value = res.code || ''
        levelOne.value = Number((Number(res.promoRate1) * 100).toFixed(2))
        levelTwo.value = Number((Number(res.promoRate2) * 100).toFixed(2))
        levelThree.value = Number((Number(res.promoRate3) * 100).toFixed(2))
        Toast.clear()
      }).catch(() => {
        Toast.clear()
      })
    }

    const onRefresh = () => {
      loading.value = true
      page.value.pageNo = 1
      getLevelData()
    }

    const navChange = () => {
      listData.value = []
      finished.value = false
      onRefresh()
    }

    const { locale } = useI18n()
    const lang = ref(locale.value)
    const levelOne = ref(0)
    const levelTwo = ref(0)
    const levelThree = ref(0)

    nextTick(() => {
      Toast.loading({
        duration: 0,
        message: t('loading'),
        forbidClick: true
      })

      sellerPromotional().then(res => {
        promotionDataRef.value[0].value = res.download && res.code ? `${res.download}/#?usercode=${res.code}&lang=${locale.value}` : ''
        promotionDataRef.value[1].value = res.code || ''

        levelOne.value = Number((Number(res.promoRate1) * 100).toFixed(2))
        levelTwo.value = Number((Number(res.promoRate2) * 100).toFixed(2))
        levelThree.value = Number((Number(res.promoRate3) * 100).toFixed(2))
        Toast.clear()
      }).catch(() => {
        Toast.clear()
      })
    })
    
    return {
      promotionDataRef,
      navActive,
      teamNav,
      refreshing,
      loading,
      finished,
      listData,
      empytImg,
      lang,
      t,
      formatZoneDate,
      levelOne,
      levelTwo,
      levelThree,
      isArLang,
      copyHandle,
      navChange,
      getLevelData,
      onRefresh,
      numberStrFormat
    }
  }
})
</script>

<style lang="scss" scoped>
.shop-promotion {
  min-height: 100vh;
  background-color: #fff;
  .promotion-info {
    padding: 0 15px 15px 15px;
    background-color: #fff;
    > .item {
      margin-top: 10px;
      &.is-ar {
        :deep(.van-cell) {
          .van-field__body {
            input {
              border: 1px solid #ddd;
              border-right: 1px solid #ddd;
              border-top-left-radius: 0;
              border-bottom-left-radius: 0;
              border-top-right-radius: 4px;
              border-bottom-right-radius: 4px;
              text-align: right;
            }
            .van-field__button {
              padding-left: 0;
              .van-button {
                border-radius: 4px;
                border-top-right-radius: 0;
                border-bottom-right-radius: 0;
              }
            }
          }
        }
      }
      > p {
        color: #333;
        font-size: 14px;
      }
      :deep(.van-cell) {
        padding: 0;
        margin-top: 5px;
        .van-field__body {
          input {
            border: 1px solid #ddd;
            border-right: none;
            height: 40px;
            border-top-left-radius: 4px;
            border-bottom-left-radius: 4px;
            padding: 0 10px;
            pointer-events: none;
          }
          .van-field__button {
            padding-left: 0;
            .van-button {
              width: 86px;
              height: 40px;
              border-radius: 4px;
              background-color: var(--site-main-color);
              border-color: var(--site-main-color);
              border-top-left-radius: 0;
              border-bottom-left-radius: 0;
            }
          }
        }
      }
    }
  }
  .intro-content {
    padding: 15px;
    border-top: 10px solid #EFF2F6;
    background-color: #fff;
    > p {
      font-size: 13px;
      line-height: 20px;
      color: #333333;
      margin-top: 8px;
      &:first-child {
        margin-top: 0;
      }
      ::v-deep(span),
      span {
        color: #1552F0;
      }
    }
  }
  .team-content {
    border-top: 10px solid #EFF2F6;
    :deep(.van-tabs) {
      border-bottom: 1px solid #eee;
    }
    .list-content {
      > .item {
        display: flex;
        padding: 15px;
        border-bottom: 1px solid #eee;
        background-color: #fff;
        > .avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          overflow: hidden;
        }
        > .info {
          flex: 1;
          padding-left: 10px;
          font-size: 12px;
          line-height: 14px;
          color: #999;
          > .rebate {
            color: #333;
            margin-top: 15px;
          }
          > div {
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: 10px;
            > p {
              &:first-child {
                color: #333;
              }
            }
          }
        }
      }
    }
  }
}
</style>
