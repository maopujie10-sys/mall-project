<template>
  <div class="main-stroe app-container" v-loading="httpLoading">
    <div class="main-stroe-title flex-between">
      <h1>{{ $t("message.home.recommendedStore" /**推荐店铺 */) }}</h1>
    </div>
    <swiper :options="swiperOptions" ref="recommendStore" 
      @mouseenter.native="mouseEnter"
      @mouseleave.native="mouseLeave"
    >
      <swiper-slide v-for="(item, index) in merchantList" :key="index">
        <EsStore :item="item"/>
      </swiper-slide>
    </swiper>
    <div class="main-stroe-title flex-between">
      <h1>{{ $t("message.home.热销推荐" /**推荐店铺 */) }}</h1>
    </div>
    <div class="main-stroe-content">
      <EsProductView v-for="item in list" :key="item.isKeep+ Math.random()" :item="item" />
    </div>
  </div>
</template>

<script>
  import { mapGetters, mapActions } from "vuex";
  import EsStore from "@/components/store";
  import EsProductView from "@/components/product";
  import { RecommendedProductsNewApi } from "@/api/home";
  import Bus from '@/util/bus'
  export default {
    name: "EsRecommendStore",
    components: { EsStore, EsProductView },
    data() {
      return {
        swiperOptions: {
          slidesPerView: 3,
          spaceBetween: 90,
          autoplay: {
            delay: 3500,
            disableOnInteraction: false,
          },
        },
        httpLoading: false,
        list: [],
      };
    },
    computed: {
      ...mapGetters("home", ["bottomList", "merchantList"]),
    },
    methods: {
       mouseEnter() {
        this.$refs.recommendStore.$swiper.autoplay.stop();
      },
      mouseLeave() {
        this.$refs.recommendStore.$swiper.autoplay.start();
      },
      ...mapActions("home", ["requestRecommendLList", "requestMerchantList"]),
      async getRecommendList() {
        const res = await RecommendedProductsNewApi({
          type: 2,
          pageSize: 24,
        });
        this.list = res.data.result;
      },
    },
    async mounted() {
      Bus.$on('cancelKeep', (id)=>{
        const i = this.list.findIndex(x => x.id === id)
        if(i>-1){
          this.$nextTick(() => {
            this.getRecommendList();
          })
        }
      })
      Bus.$on('keepProduct', (id)=>{
        const i = this.list.findIndex(x => x.id === id)
        if(i>-1){
          this.$nextTick(() => {
            this.getRecommendList();
          })
        }
      })
      try {
        this.httpLoading = true;
        await this.requestMerchantList({ isRec: 1 });
        this.getRecommendList();
      } finally {
        this.httpLoading = false;
        this.$emit("onload");
      }
      

    },
  };
</script>

<style lang="scss">
  .main-stroe {
    margin-top: 26px;
    margin-bottom: 26px;
    &-title {
      h1 {
        font-weight: 700;
        font-size: 16px;
        color: var(--color-grey);
        margin: 24px 0;
      }
      span {
        color: var(--color-main);
        font-size: 12px;
      }
      .all {
        font-size: 12px;
        color: var(--color-main);
        cursor: pointer;
        font-weight: 400;
      }
    }

    &-content {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(188px, 165px));
      grid-column-gap: 14px;
      grid-row-gap: 20px;
      align-content: center;
    }
  }
</style>
