<template>
  <div class="product-details">
    <EsHeaderView />
    <div class="app-container contain" v-loading="loading">
      <div class="product-details-contain">
        <EsProductInfo :id="id" />
        <EsProductDescription />
        <EsProductComment />
        <EsProductDetailsInfo />
      </div>
      <EsProductMerchant ref="recChild" />
    </div>
    <EsProductLike ref="likeChild" />
    <EsIconTips />
    <EsFooterView />
  </div>
</template>

<script>
import { mapActions, mapGetters } from "vuex";
import EsProductInfo from "@/components/productInfo";
import EsProductDescription from "./productDescription.vue";
import EsProductDetailsInfo from "./productDetails.vue";
import EsProductComment from "./productComment.vue";
import EsProductMerchant from "./productMerchant.vue";
import EsProductLike from "./productLike.vue";
import EsIconTips from "@/components/iconTips";
export default {
  name: "EsProductDetails",
  components: {
    EsProductInfo,
    EsProductDescription,
    EsProductDetailsInfo,
    EsProductComment,
    EsProductMerchant,
    EsProductLike,
    EsIconTips,
  },
  data() {
    return {
      loading: false,
      id: "",
    };
  },
  methods: {
    ...mapActions("productDetails", ["requestProductDetails"]),
  },
  computed: {
    ...mapGetters({
      productDetails: "productDetails/productDetails",
    }),
    ...mapGetters(["isLogin"]),
  },
  async mounted() {
    const currentRouter = this.$router.currentRoute;
    this.id = currentRouter.query.id;
    if (!this.id) {
      this.$router.replace("/");
      return;
    }
    try {
      this.loading = true;
      await this.requestProductDetails({
        sellerGoodsId: this.id,
      });
    } finally {
      this.loading = false;
      localStorage.setItem("sellerId", this.productDetails.seller.id);
      localStorage.setItem("sellerRecId", this.productDetails.seller.id);
      if (this.isLogin) {
        this.$refs.recChild.getLike();
        this.$refs.likeChild.getLike();
      }
      if (!this.productDetails.id) {
        // this.$message({
        //   message: this.$t("message.home.switchLang"),
        // });
        this.$router.replace("/");
      }
    }
  },
  beforeRouterUpdate(to, from, next) {},
  watch: {
    $route: function (to, from) {
      if (to) {
        localStorage.removeItem("sellerId");
        localStorage.removeItem("sellerRecId");
        location.reload();
      }
    },
  },
};
</script>

<style lang="scss">
.contain {
  display: flex;
}
.product-details {
  &-contain {
    align-items: flex-start;
  }

  &-bottom {
    max-width: 1000px;
    margin: 52px auto 107px auto;
    &-item {
      flex-direction: column;
    }
    span {
      font-weight: 500;
      font-size: 12px;
      margin-top: 15px;
    }
  }
}
</style>
