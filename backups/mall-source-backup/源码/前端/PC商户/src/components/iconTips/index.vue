<template>
  <div class="icon-tips">
    <div class="icon-tips-bottom flex-between">
      <div class="icon-tips-bottom-item flex-center">
        <span class="iconfont icon-aixin icon_span" ></span>
        <span>{{ this.$t("message.home.authentic" /**100% 正品 */) }}</span>
      </div>
      <div class="icon-tips-bottom-item flex-center">
        <!-- <img :src="require('@/assets/image/back.png')" alt="Back" /> -->
        <span class="iconfont icon-control-backward icon_span"></span>
        <span>{{ this.$t("message.home.dayReturns7" /**7 天退货 */) }}</span>
      </div>
      <div class="icon-tips-bottom-item flex-center">
        <!-- <img :src="require('@/assets/image/Vector.png')" alt="Vector" /> -->
        <span class="iconfont icon-yunfei icon_span"></span>
        <span>
          {{ this.$t("message.home.shippingDiscounts" /**运费折扣 */) }}
        </span>
      </div>
      <div class="icon-tips-bottom-item flex-center">
        <!-- <img :src="require('@/assets/image/Union.png')" alt="Union" /> -->
         <span class="iconfont icon-qianbao icon_span"></span>
        <span>{{ this.$t("message.home.safePayment" /**安全支付 */) }}</span>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: "EsIconTips",
    data() {
      return {};
    },
  };
</script>

<style lang="scss">
  .icon-tips {
    &-bottom {
      max-width: 957px;
      margin: 52px auto 107px auto;
      &-item {
        flex-direction: column;
        img {
          width: 38px;
        }
      }
      span {
        font-weight: 500;
        font-size: 12px;
        margin-top: 15px;
      }
    }
    .icon_span{
      font-size: 58px;
      color:var(--color-main)
    }
  }
</style>
