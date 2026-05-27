<template>
  <div>
    <div class="product-details-merchant">
      <div class="product-details-merchant-top flex-start">
        <div class="shop-img">
          <img
            :src="productDetails.seller.avatar"
            :alt="productDetails.seller.name"
            fit="fill"
          />
        </div>
        <h1>{{ productDetails.seller.name }}</h1>
      </div>
      <div class="product-details-merchant-statistics flex-between">
        <div class="all flex-center merchant-statistics" style="width: 50%">
          <h2>{{numberFormatA (productDetails.seller.sellerGoodsNum || 0) }}</h2>
          <span>{{ this.$t("message.home.AllProducts" /** 全部商品*/) }}</span>
        </div>
        <div class="line"></div>
        <div
          class="follower flex-center merchant-statistics"
          style="width: 50%"
        >
          <h2>{{ numberFormatA(focusNum) }}</h2>
          <span>{{ this.$t("message.home.followers" /**关注 */) }}</span>
        </div>
      </div>
      <div class="flex-center merchant-statistics">
        <h2>{{ numberFormatA(productDetails.seller.soldNum + productDetails.seller.fakeSoldNum|| 0) }}</h2>
        <span>{{ this.$t("message.home.sales" /**销售量 */) }}</span>
      </div>
      <el-button type="primary" plain @click="gotoStroe">
        {{ this.$t("message.home.visitStore" /**访问商店 */) }}>
      </el-button>
    </div>
    <div class="titleRe" v-if="merchantGoodsList.length">
      {{ this.$t("message.home.recommendedProducts") }}
    </div>
    <div
      class="product-details-merchant"
      style="border: none; padding: 0"
      v-if="merchantGoodsList.length"
    >
      <EsProductView
        v-for="(item) in merchantGoodsList"
        :key="item.isKeep + Math.random()"
        :item="item"
      />
      <div class="no-data" v-if="!merchantGoodsList.length">
        <el-empty :description="$t('message.home.noData')"></el-empty>
      </div>
    </div>
  </div>
</template>
<script>
import { mapGetters } from "vuex";
import { accAdd } from "@/util/math";
import { AlsoLike } from "@/api/productDetails";
import EsProductView from "./product";
import { numberFormatA } from "@/util";
import Bus from "@/util/bus"; 
export default {
  name: "EsProductMerchant",
  components: { EsProductView },
  computed: {
    ...mapGetters("productDetails", ["productDetails"]),
    ...mapGetters(["isLogin"]),
    focusNum() {
      const seller = this.productDetails.seller;
      return accAdd(seller.focusNum || 0, seller.fake || 0);
    },
  },
  data() {
    return {
      merchantGoodsList: "",
    };
  },
  provide(){
    return {
      getLikeMethed: this.getLike
    }
  },
  mounted() {
    // this.getLike();
    // if (this.isLogin) {
    //   setTimeout(() => {
    //     this.getLike();
    //   }, 500);
    // }
    Bus.$on("updateCollect", (id) => {
        const i = this.merchantGoodsList.findIndex(x => x.id == id);
        if (i > -1) {
          this.getLike();
        }
      });
      Bus.$on("updateUnKeep", (id) => {
        const i = this.merchantGoodsList.findIndex(x => x.id == id);
        if (i > -1) {
          this.getLike();
        }
      });
      Bus.$on('cancelKeep', (id)=>{
        console.log('idtuijian->', id);
        const i = this.merchantGoodsList.findIndex(x => x.id == id)
        if(i>-1){
          this.getLike()
        }
      })
      Bus.$on('keepProduct', (id)=>{
        const i = this.merchantGoodsList.findIndex(x => x.id == id)
        if(i>-1){ 
          this.getLike()
        }
      })
  },
  methods: {
    numberFormatA,
    gotoStroe() {
      sessionStorage.setItem("storeRefresh", true);
      this.$router.push({
        name: "store",
        query: { storeId: this.productDetails.seller.id },
      });
    },
    async getLike() {
      let sellerId = localStorage.getItem("sellerRecId");
      if(sellerId){
        let res = await AlsoLike({
        type: 2,
        sellerId: sellerId,
      });
      this.merchantGoodsList = res.data.splice(0, 3);
      }
      
    },
  },
};
</script>

<style lang="scss">
.product-details {
  .product-details-merchant-top {
    align-items: center;

    .shop-img {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 46px;
      height: 46px;

      img {
        border-radius: 50%;
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
    }
  }

  &-merchant {
    margin-left: 17px;
    border: 1px solid var(--color-border);
    border-radius: 4px;
    padding: 10px;

    &-top {
      padding-bottom: 17px;

      img {
        width: 46px;
        height: 30px;
        object-fit: cover;
      }

      h1 {
        max-width: 130px;
        font-size: 14px;
        line-height: 16px;
        color: var(--color-black);
        text-overflow: ellipsis;
        overflow: hidden;
        white-space: nowrap;
        padding: 0 0 0 8px;
      }
    }

    &-statistics {
      border-top: 1px solid var(--color-border);
      border-bottom: 1px solid var(--color-border);
    }

    .line {
      width: 1px;
      height: 18px;
      background-color: var(--color-border);
    }

    .merchant-statistics {
      flex-direction: column;
      padding: 16px 0;

      h2 {
        font-weight: 700;
        font-size: 14px;
        color: var(--color-title);
        margin-bottom: 5px;
      }

      span {
        font-weight: 400;
        font-size: 12px;
        color: var(--color-title);
      }
    }

    .el-button {
      margin-bottom: 15px;
      width: 192px;
      height: 26px;
      padding: 0;
      font-size: 12px;
      font-weight: 400;
      border-radius: 27px;
    }
  }
}
.titleRe {
  padding: 18px 0;
  margin-left: 17px;
  font-weight: 400;
  font-size: 14px;
}
.product {
  margin-bottom: 10px;
}
</style>
