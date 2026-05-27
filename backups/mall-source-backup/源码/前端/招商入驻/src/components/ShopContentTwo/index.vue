<template>
  <div>
    <div v-if="shopData.length" class="shop-content">
      <div v-for="item in shopData" :key="item.id" class="item">
        <shop-item-two :shop-info="item"></shop-item-two>
      </div>
    </div>
    <van-empty v-else :description="$t('暂无数据')" />
  </div>
</template>

<script>
import { Empty } from 'vant'
import ShopItemTwo from './../ShopItemTwo/index.vue'
export default {
  name: 'GoodsContentTwo',
  components: {
    [Empty.name]: Empty,
    ShopItemTwo
  },
  props: {
    shopData: {
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
  padding: 0 15px;
}
</style>