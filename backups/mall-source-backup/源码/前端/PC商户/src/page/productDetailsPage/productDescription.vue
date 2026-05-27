<template>
  <div class="product-description" v-if="productDetails.des">
    <h1 class="title1">
      {{ this.$t("message.home.productDescription" /**商品描述 */) }}
    </h1>
    <p v-html="productDetails.des"></p>
  </div>
</template>

<script>
  import { mapGetters } from "vuex";
  export default {
    name: "EsProductDescription",
    computed: {
      ...mapGetters("productDetails", ["productDetails"]),
    },
  };
</script>

<style lang="scss">
  .product-details-content {
    border: 1px solid var(--color-border);
    padding: 20px 6px;
    margin-top: 28px;
  }
  .product-description {
    width: 957px;
    border: 1px solid var(--color-border);
    padding: 20px 0;
    margin-bottom: 28px;

    .title1 {
      font-weight: 600;
      font-size: 20px;
      color: var(--color-title);
      border-bottom: 1px solid var(--color-border);
      padding: 0 37px 19px 55px;
      margin-left: 0 !important;
    }
    p {
      font-weight: 400;
      font-size: 12px;
      color: var(--color-title);
      padding: 25px 40px;
      line-height: 17px;
    }
  }
  .product-details-content-item img {
    max-width: 100% !important;
  }
  .product-details-content-item .aplus-v2 {
    max-width: 100% !important;
  }
  .product-details-content-item p {
    display: flex;
    flex-direction: column;
  }
</style>
