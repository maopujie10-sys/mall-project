<template>
  <div class="goods-item-content" @click="openDetails">
    <div class="poster"><img :src="goodsData.imgUrl1 || goodsData.imgUrl2 || goodsData.imgUrl3 || goodsData.imgUrl4" alt="" /></div>
    <div class="content">
      <div class="price">{{ goodsData.unit || '$' }}{{ goodsData.sellingPrice ?? '0' }}</div>
      <div class="text"><span>{{ $t('已售') }}</span> {{ goodsData.soldNum ?? '0' }}</div>
      <div class="name">{{ goodsData.name ?? '-' }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GoodsItemOne',
  props: {
    goodsData: {
      type: Object,
      required: true,
      default: function() {
        return {}
      }
    }
  },
  methods: {
    openDetails() {
      this.$router.push({
        path: '/CommodityDetails',
        query: {
          sellerGoodsId: this.goodsData.id
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
  .goods-item-content {
    * {
      box-sizing: border-box;
    }
    > .poster {
      width: 100%;
      height: 154px;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 10px;
      > img {
        width: 100%;
        height: auto;
      }
    }
    > .content {
      padding: 10px;
      > .price {
        color: var(--color-main);
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 4px;
      }
      > .text {
        color: #999999;
        font-size: 12px;
        margin-bottom: 2px;
      }
      > .name {
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 2;
        margin-top: 5px;
        font-size: 14px;
      }
    }
  }
</style>