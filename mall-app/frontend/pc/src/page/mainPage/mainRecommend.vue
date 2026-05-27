<template>
  <div class="main-recommend app-container" v-loading="httpLoading">
    <h1>{{ $t("message.home.recommendedProducts" /**推荐产品 */) }}</h1>
    <div class="main-recommend-content">
      <EsProductView
        v-for="item in recommendList"
        :key="item.isKeep + Math.random()"
        :item="item"
      />
    </div>
  </div>
</template>

<script>
  import { mapGetters, mapActions } from "vuex";
  import EsProductView from "@/components/product";
  import Bus from '@/util/bus'
  export default {
    name: "EsMainRecommend",
    components: { EsProductView },
    data() {
      return {
        httpLoading: false,
      };
    },
    computed: {
      ...mapGetters("home", ["recommendList"]),
      isExistRecomend() {
        return !!this.recommendList.length;
      },
    },
    methods: {
      ...mapActions("home", [
        "requestRecommendLList",
        "requestRecommendNewLList",
      ]),
      // Bus.$on('cencalKeep',)
      async getList(){
        // this.recommendList = []
         try {
        this.httpLoading = true;
        // await this.requestRecommendLList({ params: { recTime: Date.now() }, type: 0 })
        await this.requestRecommendNewLList({
          type: 1,
          pageSize: 24,
          pageNum: 1,
        });
      } finally {
        this.httpLoading = false;
        this.$emit("onload");
      }
      }
    },
    async mounted() {
      
      Bus.$on('cancelKeep', (id)=>{
        console.log('idtuijian->', id);
        const i = this.recommendList.findIndex(x => x.id == id)
        if(i>-1){
          // this.$nextTick(() => {
            this.getList()
          // })
        }
      })
      Bus.$on('keepProduct', (id)=>{
        const i = this.recommendList.findIndex(x => x.id == id)
        if(i>-1){
          // this.$nextTick(() => {
            this.getList()
          // })
        }
      })
      this.getList()
    },
  };
</script>

<style lang="scss">
  .main-recommend {
    margin-top: 26px;
    h1 {
      font-weight: 700;
      font-size: 16px;
      color: var(--color-grey);
    }
    &-content {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(188px, 165px));
      grid-column-gap: 14px;
      grid-row-gap: 20px;
      align-content: center;
      margin-top: 15px;
    }
  }
</style>
