<template>
  <div class="like" v-if="merchantGoodsList.length">
    <h1 class="title">
      {{ this.$t("message.home.猜你喜欢" /**商品描述 */) }}
    </h1>
    <div class="product-details-content-item1">
      <!-- <div style="width: 166px"> -->
      <EsProductView
        v-for="(item) in merchantGoodsList"
        :key="item.isKeep + Math.random()"
        :item="item"
        :belike="true"
      />
      <!-- </div> -->
      <div class="no-data" v-if="!merchantGoodsList.length">
        <el-empty
          :description="$t('message.home.noData')"
          style="width: 100%"
        ></el-empty>
      </div>
    </div>
  </div>
</template>

<script>
  import { AlsoLike } from "@/api/productDetails";
  import EsProductView from "@/components/product";
  import { mapGetters } from "vuex";
  import Bus from '@/util/bus'
  export default {
    name: "EsProductLike",
    components: { EsProductView },
    computed: { ...mapGetters(["isLogin"]) },
    data() {
      return {
        merchantGoodsList: [],
      };
    },
    mounted() {
      // if (this.isLogin) {
        
      //   setTimeout(() => {
      //     console.log('22 ->', 22);
      //     this.getLike();
      //   }, 500);
      // }
      Bus.$on("updateCollect", (id) => {
        // this.getLike();
        const i = this.merchantGoodsList.findIndex(x => x.id == id);
        if (i > -1) {
          this.getLike();
        }
      });
      Bus.$on("updateUnKeep", (id) => {
        // this.getLike();
        const i = this.merchantGoodsList.findIndex(x => x.id == id);
        if (i > -1) {
          this.getLike();
        }
      });
      Bus.$on("collect", (id) => {
        // this.getLike();
        const i = this.merchantGoodsList.findIndex(x => x.id == id);
        if (i > -1) {
          this.getLike();
        }
      });
      Bus.$on("UnCollect", (id) => {
        // this.getLike();
        const i = this.merchantGoodsList.findIndex(x => x.id == id);
        if (i > -1) {
          this.getLike();
        }
      });
    },
    methods: {
      async getLike() {
        let sellerId = localStorage.getItem("sellerId");
        console.log('sellerId ->', sellerId);
        if(sellerId){
          let res = await AlsoLike({
          type: 1,
          sellerId: sellerId,
        });
          this.merchantGoodsList = res.data?.splice(0, 12);
          
        }
        
        // console.log('res ->', res);
        
      },
    },
  };
</script>

<style lang="scss">
  // .product-details-content {
  //   width: 957px;
  //   padding: 20px 0;
  //   margin-bottom: 28px;
  .like {
    width: 1200px;
    margin: 0 auto;
  }
  .title {
    font-weight: 600;
    font-size: 20px;
    color: var(--color-title);
    margin-bottom: 10px;
    margin-top: 38px;
    margin-left: 0 !important;
  }
  .product-details-content-item1 {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(185px, 165px));
    grid-column-gap: 15px;
    grid-row-gap: 12px;
    align-content: center;
  }
</style>
