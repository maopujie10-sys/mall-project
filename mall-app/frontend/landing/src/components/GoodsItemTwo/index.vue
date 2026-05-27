<template>
  <div class="goods-item">
    <div class="poster">
      <img :src="goodsData.imgUrl1 || goodsData.imgUrl2 || goodsData.imgUrl3 || goodsData.imgUrl4" alt="" />
    </div>
    <div class="info">
      <div class="name">{{ goodsData.name }}</div>
      <div class="price">
        <p>{{ goodsData.unit || '$' }}{{ goodsData.sellingPrice ?? '0' }}</p>
        <p class="old"><span>{{ $t('原价') }}</span> {{ goodsData.systemPrice }}</p>
      </div>
      <p><span>{{ $t('已售') }}</span> {{ goodsData.soldNum }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GoodsItemTwo',
  props: {
    goodsData: {
      type: Object,
      required: true,
      default: function() {
        return {}
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.goods-item {
  * {
    box-sizing: border-box;
  }
  display: flex;
  align-items: center;
  padding: 15px;
  border: 1px solid #eee;
  margin-top: 10px;
  > .poster {
    width: 63px;
    height: 63px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    > img {
      width: 100%;
      height: auto;
    }
  }
  > .info {
    padding-left: 15px;
    flex: 1;
    > .name {
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 2;
      font-size: 14px;
    }
    > .price {
      display: flex;
      align-items: center;
      margin-top: 10px;
      > p {
        font-size: 16px;
        font-weight: bold;
        font-size: 16px;
        color: var(--color-main);
        &.old {
          font-weight: normal;
          color: #999;
          font-size: 12px;
          margin-left: 20px;
          text-decoration: line-through;
        }
      }
    }
    > p {
      color: #999;
      font-size: 11px;
      color: #999;
      margin-top: 10px;
    }
  }
}
</style>
