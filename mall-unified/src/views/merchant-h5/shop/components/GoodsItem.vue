<template>
  <div class="goods-item" @click="getdDtails">
    <div class="poster">
      <img :src="goodsData.imgUrl1 || goodsData.imgUrl2 || goodsData.imgUrl3 || goodsData.imgUrl4" alt="" />
    </div>
    <div class="info-content" :class="{'is-ar': isArLang}">
      <p class="name">{{ goodsData.name }}</p>
      <div>
        <div v-if="showBrowse">{{ t('browse') }}: {{ numberStrFormat(goodsData.viewsNum, 0) }}</div>
        <div>{{ t('sales') }}: {{ numberStrFormat(goodsData.soldNum, 0) }}</div>
      </div>
      <p class="price">${{ numberStrFormat(goodsData.sellingPrice) }}</p>
    </div>
  </div>
</template>

<script>
import { defineComponent, toRefs, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { numberStrFormat } from '@/utils'
import { arLangCheck } from '@/utils/arLangCheck'
import {
  openPage
} from '@/utils'

export default defineComponent({
  name: 'GoodsItem',
  props: {
    goodsData: {
      type: Object,
      default: () => {}
    }
  },
  setup(props) {
    const { t } = useI18n()
    const { goodsData } = toRefs(props)
    const getdDtails = () => {
      openPage({
        path: '/productPage/details',
        query: {
          item: JSON.stringify(goodsData.value)
        }
      })
    }

    const isArLang = arLangCheck()

    const showBrowse = computed(() => {
      const mode = import.meta.env.MODE
      return !['tiktok-wholesale'].includes(mode)
    })

    return {
      t,
      getdDtails,
      showBrowse,
      numberStrFormat,
      isArLang
    }
  }
})
</script>

<style lang="scss" scoped>
.goods-item {
  padding: 10px;
  background-color: #fff;
  border-radius: 4px;
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  &:last-child {
    margin-bottom: 0;
  }
  > .poster {
    width: 78px;
    height: 78px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    > img {
      width: 100%;
      height: auto;
    }
  }
  > .info-content {
    flex: 1;
    padding-left: 10px;
    word-break: break-all;
    &.is-ar {
      padding-left: 0;
      padding-right: 10px;
    }
    > .name {
      font-size: 14px;
      line-height: 18px;
      color: #333;
      word-break: break-all;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 2;
    }
    > div {
      display: flex;
      align-items: center;
      > div {
        font-size: 12px;
        color: #999;
        margin-right: 15px;
        &:last-child {
          margin-right: 0;
        }
      }
    }
    > .price {
      font-size: 16px;
      color: var(--site-main-color);;
    }
  }
}
</style>
