<template>
  <div v-if="productDetails.imgDes !== null">
    <div v-if="productDetails.imgDes !== '<p><br></p>'">
      <div class="product-details-content" v-if="productDetails.imgDes !== ''">
        <h1 class="title1">
          {{ this.$t("message.home.productDescription" /**商品描述 */) }}
        </h1>
        <div
          class="product-details-content-item flex"
          v-html="productDetails.imgDes"
        ></div>
      </div>
    </div>
  </div>
</template>

<script>
  import { mapGetters } from "vuex";
  export default {
    name: "EsProductDescription",
    computed: {
      ...mapGetters("productDetails", ["productDetails"]),
    },
    mounted() {
      setTimeout(() => {
      }, 1000);
    },
  };
</script>

<style lang="scss">
  .product-details-content {
    width: 957px;
    padding: 20px 0;
    margin-bottom: 28px;
    .title1 {
      font-weight: 600;
      font-size: 20px;
      color: var(--color-title);
      border-bottom: 1px solid var(--color-border);
      padding: 0 37px 19px 55px;
      margin-bottom: 10px;
      margin-left: 0 !important;
    }
    &-item {
      width: 100%;
      flex-direction: column;
      img {
        margin: 40px 0;
      }
    }
  }
  .product-details-content-item{
    display: flex;
    padding: 0 5px;
  }
</style>
