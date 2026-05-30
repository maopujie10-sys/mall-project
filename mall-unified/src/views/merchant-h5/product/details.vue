<template>
  <div class="details">
    <fx-header fixed>
      <template #title>{{t('product.11')}}</template>
    </fx-header>
    <div class="list ml-4 mr-4 mt-4">
          <div class="item pl-3 pr-3 pb-3 pt-3 flex">
            <div class="flex-1 flex left">
              <div class="product-img-wrap w-20 h-20">
                <img class="product-img" :src="info.imgUrl1" />
              </div>
              <div class="product-info" :class="{'is-ar': isArLang}">
                <div class="name">{{info.name}}</div>
                <div class="Specification">
                  <!-- <span>{{t('product.4')}}: {{ info.unit }}</span> -->
                  <span v-if="info.categoryName">{{ info.categoryName }}</span>
                  <span>{{t('product.9')}}: {{info.soldNum}}</span>
                </div>
                <div v-if="info.systemPrice || info.systemPrice === 0" class="money">${{info.discountPrice ? numberStrFormat(info.discountPrice) : numberStrFormat(info.sellingPrice)}}</div>
              </div>
            </div>
            <!-- <div class="number">
              x1
            </div> -->

          </div>
    </div>
    <div v-if="info.systemPrice || info.systemPrice === 0" class="pl-4 pr-4 font-14">
      <div class="flex details-item pl-3 pr-3">
        <div class="title">{{t('product.9')}}</div>
        <div class="text">{{info.soldNum}}</div>
      </div>
      <div class="flex details-item pl-3 pr-3">
        <div class="title">{{ t('product.12') }}</div>
        <div class="text">${{info.discountPrice ? numberStrFormat(info.discountPrice) : numberStrFormat(info.sellingPrice) }}</div>
      </div>
      <!-- <div class="flex details-item pl-3 pr-3">
        <div class="title">Discount Price</div>
        <div class="text">$18.90</div>
      </div> -->
      <div class="flex details-item pl-3 pr-3">
        <div class="title">{{t('product.13')}}</div>
        <div class="text">${{ numberStrFormat(info.systemPrice) }}</div>
      </div>
      <div class="flex details-item pl-3 pr-3">
        <div class="title">{{t('product.14')}}</div>
        <div class="text">${{ info.discountPrice ? numberStrFormat(info.discountPrice - info.systemPrice ) : numberStrFormat(info.sellingPrice - info.systemPrice) }}</div>
      </div>
      <div class="flex details-item pl-3 pr-3">
        <div class="title">{{t('product.15')}}</div>
        <div class="text">{{info.isShelf / 1 === 1  ?  t('product.17') :t('product.18')}}</div>
      </div>
      <div class="flex details-item pl-3 pr-3">
        <div class="title">{{t('product.16')}}</div>
        <div class="text">{{info.recTime / 1 === 1  ? t('product.17') : t('product.18')}}</div>
      </div>
    </div>

    <div v-if="specHeader.length" class="spec-container">
      <div class="spec-content">
        <div class="col-item header">
          <div v-for="item in specHeader" :key="item" class="item">{{ item }}</div>
        </div>
        
        <div v-for="(item, index) in specData" :key="index" class="col-item">
          <div v-for="(_item, _index) in item.goodsAttributeVos" :key="_item.attrValue" class="item">{{ _item.attrValue }}</div>
          <div class="item">${{ numberStrFormat(item.systemPrice) }}</div>
          <div class="item">${{ numberStrFormat(item.sellingPrice) }}</div>
          <div class="item" v-if="item.discountPrice">${{ numberStrFormat(item.discountPrice) }}</div>
          <div class="item" v-else>--</div>
          <div class="item">${{ item.discountPrice ? numberStrFormat(item.discountPrice - item.systemPrice) : numberStrFormat(item.sellingPrice - item.systemPrice) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import {Toast} from "vant";
import { numberStrFormat } from '@/utils'
import { arLangCheck } from '@/utils/arLangCheck'
import { sellerGoodsSkuInfo } from '@/service/product.api'

const isArLang = arLangCheck()

const { t } = useI18n()
const route = useRoute()
let info = ref({})


const specHeader = ref([])
const specData = ref([])

onMounted(() => {
  info.value = JSON.parse(route.query.item)

  console.log(info.value)

  Toast.loading({
    forbidClick: true,
    duration: 0
  });
  sellerGoodsSkuInfo({
    sellerGoodsId: info.value.id
  }).then(res => {
    const data = res.sellerGoodsSkuDtoList || []
    if (data.length) {
      let headerData = [t('采购价'), t('销售价'), t('折扣价'), t('利润')]
      const goodsAttributeVos = data[0].goodsAttributeVos || []
      const specHeaderItem = goodsAttributeVos.map(item => item.attrName)
      headerData = [...specHeaderItem, ...headerData]
      specHeader.value = headerData
    }
    specData.value = data
    Toast.clear()
  })
})
</script>

<style scoped lang="scss">
.details {
  padding-top: 50px;
  padding-bottom: 50px;

  .search-wrap {
    margin: 0 15px;
    border-radius: 25px;
    height: 45px;
    text-align: center;

    .search-icon {
      height: 24px;
    }
  }

  .product-header {
    background: #FFFFFF;
    border-radius: 4px;
    padding: 20px 0;
    margin-top: 20px;

    .moeny {
      font-weight: 600;
      font-size: 20px;
    }

    .title {
      margin-top: 10px;
      color: #999999;
    }

    .after {
      position: relative;

      &::after {
        position: absolute;
        height: 100%;
        width: 1px;
        background: #DDDDDD;
        content: '';
        right: 0;
        top: 0;
      }
    }
  }

  .list {
    position: relative;
    border-bottom: 1px solid #EFF2F6;
    .item {
      background: #FFFFFF;
      border-radius: 4px;
      // align-items: center;
      
      .more-icon {
        width: 20px;
      }

      .product-img {
        width: 100px;
        height: auto;
      }
      .number{
        position: absolute;
        bottom: 12px;
        right: 12px;
        font-weight:700;
        color: var(--site-main-color);
      }
      .left {
        align-items: center;
        display: flex;

        .product-info {
          padding-left: 10px;
          word-break: break-all;
          flex: 1;
          &.is-ar {
            padding-right: 10px;
            padding-left: 0;
          }

          .name {
            font-size: 14px;
            color: #333333;
            font-weight: bold;
            overflow: hidden;
            display: -webkit-box;
            -webkit-box-orient: vertical;
            -webkit-line-clamp: 2;
            -ms-text-overflow: ellipsis;
            text-overflow: ellipsis;
          }

          .Specification {
            font-size: 12px;
            color: #999999;
            span{
              margin-right: 10px;
            }
          }

          .money {
            color: var(--site-main-color);
            font-weight: bold;
          }
        }
      }

    }

    .product-img-wrap {
      position: relative;
      overflow: hidden;
    }

    .delete-wrap {
      padding: 0 15px;
      background: rgba(0, 0, 0, 0.6);
      position: absolute;
      left: 0;
      top: 0;
      font-size: 12px;
      color: #fff;
    }
  }

}
.details-item{
  justify-content: space-between;
  padding-top: 8px;
  padding-bottom: 8px;
  background: #FFFFFF;
  .title{
    color: #999999;
  }
  .text{
    color: #333;
  }
}
:deep(.van-search__content) {
  background: #fff;
}

:deep(.van-field__control) {
  text-align: center;
}

.spec-container {
  overflow-x: scroll;
  width: calc(100vw - 2rem);
  margin: 0 auto;
  margin-top: 20px;
  position: relative;
  .spec-content {
    > .col-item {
      display: flex;
      white-space: nowrap;
      float: left;
      min-width: 100%;
      background-color: #fff;
      border-bottom: 1px solid #ebeef5;
      &.header {
        background-color: var(--site-main-color);
        border-bottom: none;
        color: #fff;
        > .item {
          font-weight: bold;
          background-color: var(--site-main-color);
        }
      }
      > .item {
        min-width: 16.666666%;
        width: 110px;
        font-size: 13px;
        padding: 8px 5px;
        border-right: 1px solid #ebeef5;
        word-break: break-all;
        word-wrap: break-word;
        white-space: normal;
        line-height: 1.4;
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: #fff;
        text-align: center;
        &:last-child {
          border-right: none;
        }
      }
    }
  }
}
</style>