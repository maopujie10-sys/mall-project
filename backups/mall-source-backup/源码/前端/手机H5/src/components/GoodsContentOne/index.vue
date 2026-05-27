<template>
  <div>
    <div v-if="goodsData.length" class="goods-content">
      <div v-for="item in goodsData" :key="item.id" class="item">
        <goods-item-one :goods-data="item"></goods-item-one>
      </div>
    </div>
  </div>
</template>

<script>
import GoodsItemOne from './../GoodsItemOne/index.vue'
export default {
  name: 'GoodsContentOne',
  components: {
    GoodsItemOne
  },
  props: {
    goodsData: {
      type: Array,
      default: function() {
        return []
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.goods-content {
  width: 100%;
  overflow: hidden;
  > .item {
    box-sizing: border-box;
    width: calc((100% - 15px) / 2);
    height: 267px;
    float: left;
    border: 1px solid #eee;
    margin-right: 15px;
    margin-top: 15px;
    border-radius: 4px;
    &:nth-child(even) {
      margin-right: 0;
    }
  }
}
</style>