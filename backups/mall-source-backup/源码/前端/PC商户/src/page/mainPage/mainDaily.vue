<template>
  <div class="main-daily app-container" v-loading="httpLoading">
    <div class="main-daily-title flex-between">
      <h1>{{ $t('message.home.dailyNewArrival' /**每日新品上架 */) }}</h1>
      <div class="all" @click="gotoCommodityPage">
        {{ $t('message.home.more' /**更多 */) }}
        <i class="el-icon-arrow-right"></i>
      </div>
    </div>
    <div class="main-daily-content" ref="mainDaily">
      <EsProductView v-for="item in newList" :key="item.isKeep + Math.random()" :item="item" />
    </div>
    <!-- <swiper :options="swiperOptions">
      <swiper-slide v-for="(item, index) in list" :key="index">
        <div class="main-daily-item flex-center">
          <div class="img-content">
            <img :src="item" alt="" />
          </div>
          <span class="amount">$12.00</span>
        </div>
      </swiper-slide>
    </swiper> -->
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import EsProductView from '@/components/product'
import Bus from '@/util/bus'
export default {
  name: 'EsMainDaily',
  components: { EsProductView },
  data() {
    return {
      httpLoading: false,
    }
  },
  computed: {
    ...mapGetters('home', ['newList']),
  },
  methods: {
    ...mapActions('home', ['requestRecommendLList', 'requestRecommendNewLList']),
    gotoCommodityPage() {
      this.$router.push('/commodity')
    },
    async getList(){
      try {
      this.httpLoading = true
      await this.requestRecommendNewLList({ type: 0 ,pageSize: 24,
          pageNum: 1,})
    } finally {
      this.$Gsap.from(this.$refs.mainDaily,{
        delay: 0.5,
        duration: 1,
        y: '+100',
        autoAlpha: 0,
        ease: "back.out(1.7)"
      })
      this.httpLoading = false
    }
    }
  },
   mounted() {
     Bus.$on('cancelKeep', (id)=>{
        console.log('idtuijian1->', id);
        const i = this.newList.findIndex(x => x.id == id)
        if(i>-1){
            this.getList()
        }
      })
      Bus.$on('keepProduct', (id)=>{
        const i = this.newList.findIndex(x => x.id == id)
        if(i>-1){
            this.getList()
        }
      })
    this.getList()
  },
}
</script>

<style lang="scss">
.main-daily {
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
  &-item {
    flex-direction: column;
    .img-content {
      width: 100%;
      margin-bottom: 10px;
    }
    .amount {
      font-size: 16px;
      font-weight: 500;
      color: var(--color-main);
    }
  }
  &-content {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(188px, 165px));
    grid-column-gap: 14px;
    grid-row-gap: 20px;
    align-content: center;
    /* padding: 26px 0; */
  }
  // .swiper-container {
  //   cursor: pointer;
  //   font-size: 12px;
  //   img {
  //     max-width: 310px;
  //     max-height: 148px;
  //     object-fit: cover;
  //     width: 100%;
  //     height: 100%;
  //   }
  // }
}
</style>
