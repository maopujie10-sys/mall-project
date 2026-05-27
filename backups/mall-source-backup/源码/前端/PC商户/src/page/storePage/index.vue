<template>
  <div class="store">
    <EsHeaderView :isStore="true" />
    <div class="wrap app-center">
      <div class="head-wrap">
        <img
          :src="filterBanner[0]"
          class="banner"
          v-if="filterBanner.length < 2"
        />
        <swiper :options="option" v-else>
          <swiper-slide v-for="(item, i) in filterBanner" :key="i">
            <img :src="item" alt="" />
          </swiper-slide>
        </swiper>
        <div class="box">
          <div class="container-left">
            <img :src="sellerInfo.avatar" :alt="sellerInfo.name" />
            <div class="desc">
              <p>{{ sellerInfo.name }}</p>
              <span>
                {{ sellerInfo.shopRemark }}
              </span>
              <div class="img-list">
                <a
                  v-if="sellerInfo.facebook"
                  :href="sellerInfo.facebook"
                  target="_blank"
                  referrerpolicy="no-referrer"
                >
                  <img src="../../assets/image/facebook.png" alt="" />
                </a>
                <a
                  v-if="sellerInfo.twitter"
                  :href="sellerInfo.twitter"
                  target="_blank"
                  referrerpolicy="no-referrer"
                >
                  <img src="../../assets/image/twitter.png" alt="" />
                </a>
                <a
                  v-if="sellerInfo.google"
                  :href="sellerInfo.google"
                  target="_blank"
                  referrerpolicy="no-referrer"
                >
                  <img src="../../assets/image/google.png" alt="" />
                </a>
                <a
                  v-if="sellerInfo.youtube"
                  :href="sellerInfo.youtube"
                  target="_blank"
                  referrerpolicy="no-referrer"
                >
                  <img src="../../assets/image/youtube.png" alt="" />
                </a>
                <a
                  v-if="sellerInfo.instagram"
                  :href="sellerInfo.instagram"
                  target="_blank"
                  referrerpolicy="no-referrer"
                >
                  <img src="../../assets/image/instagram.png" alt="" />
                </a>
              </div>
            </div>
          </div>
          <el-button class="btn" @click="follow">
            <i
              :class="
                // 1 已关注 0 未关注
                sellerInfo.isFocus === followStatus.on
                  ? 'el-icon-star-on'
                  : 'el-icon-star-off'
              "
            ></i>
            {{
              sellerInfo.isFocus === followStatus.on
                ? this.$t("message.home.followed" /**關注 */)
                : this.$t("message.home.followers")
            }}
          </el-button>
        </div>
      </div>
      <div class="nav">
        <ul>
          <li
            v-for="(item, index) in navlist"
            :key="index"
            @click="liEvent(index)"
            :class="activeIndex === index ? 'active' : ''"
          >
            {{ $t(item.name) }}
          </li>
        </ul>
      </div>
      <div class="app-container store-content" ref="storePage">
        <EsRecommed ref="EsRecommed" v-if="activeIndex === 0" />
        <EsSort v-else-if="activeIndex === 1" />
        <!-- <EsCommodity v-else-if="activeIndex === 1" /> -->
      </div>
    </div>
    <EsFooterView />
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import EsRecommed from "./recommend.vue";
// import EsCommodity from './commodity.vue'
import EsSort from "./sort.vue";
import { notLogin } from "@/common/pageHook";
import defaultImg from "@/assets/image/shopBanner.png";
import storeBg from "@/assets/image/store_bg.png";
export default {
  name: "EsStore",
  components: { EsRecommed, EsSort },
  data() {
    return {
      navlist: [
        {
          name: "message.home.recommend",
        },
        {
          name: "message.home.allProduct",
        },
        // {
        //   name: 'Commodity',
        // },
        // {
        //   name: 'Sort',
        // },
      ],
      swiperOptions1: {
        // direction: "vertical",
        // 改变swiper样式时，自动初始化swiper
        observer: true,
        // 监测swiper父元素，如果有变化则初始化swiper
        observeParents: true,
        loop: true,
        autoplay: {
          delay: 4500,
          disableOnInteraction: false,
        },
      },
      option: {},
      filterBanner: [],
      activeIndex: 0,
      loading: false,
      isCollect: false,
      followStatus: {
        on: 1, // 已关注
        off: 0, // 未关注
      },
        itemname: process.env.VUE_APP_ITEM_NAME,
        scrollTop: 0,
    };
  },
  computed: {
    ...mapGetters("productDetails", ["sellerInfo"]),
  },
  mounted() {
    if(this.itemname !== 'Argos'||itemname !== 'ArgosShop'){
      this.requestData();
    }
    
    this.getBannerData();
   
  },
  activated() {
     
    this.$nextTick(() => {
      const refresh = this.$route.meta.refresh;
      if (refresh) {
        this.activeIndex = 0;
        this.requestData();
        this.getBannerData();
        this.$nextTick(() => {
          this.$refs.EsRecommed.getListData(true);
        });
      }
    //   window.addEventListener("scroll",()=>{
    //        this.scrollTop = document.documentElement.scrollTop;
    //  })
    });
  },
  beforeRouteEnter(to, from, next) {
    if (from.name !== "productDetails") {
      to.meta.refresh = true;
    } else {
      if (sessionStorage.getItem("storeRefresh")) {
        sessionStorage.removeItem("storeRefresh");
        to.meta.refresh = true;
      } else {
        to.meta.refresh = false;
      }
    }
    next();
  },
  // watch: {
  //   bannerData() {
  //     this.setBannerBg();
  //   },
  // },
  watch:{
    $route(to, from) {
            if(from.path == '/productDetails'){
              console.log('222 ->', 222);
                let pageScollTop = localStorage.getItem('storePagescrollTop');
                this.scrollPageTo(pageScollTop)
            }
        },
  },
  methods: {
    ...mapActions({
      requestSellerInfo: "productDetails/requestSellerInfo",
      requestCollectSellerAdd: "user/requestCollectSellerAdd",
      requestCollectSellerDel: "user/requestCollectSellerDel",
      requestCollectSellerList: "user/requestCollectSellerList",
    }),
    scrollPageTo(top){
      this.$nextTick(()=>{
        document.documentElement.scrollTop = top;
      })
    },
    getBannerData() {
      const data = [];
      // console.log("this.sellerInfo.banner1 ->", this.sellerInfo.banner1);
      if (this.sellerInfo.banner1) {
        data.push(this.sellerInfo.banner1);
        if (this.sellerInfo.banner2) {
          data.push(this.sellerInfo.banner2);
        }
        if (this.sellerInfo.banner3) {
          data.push(this.sellerInfo.banner3);
        }
        this.filterBanner = data;
        this.option = this.swiperOptions1;
      } else {
        if(this.itemname == 'Argos' || this.itemname == 'ArgosShop'){
          this.filterBanner = [storeBg]
        } else{
          this.filterBanner = [defaultImg];
        }
        
      }
    },
    liEvent(index) {
      if (this.activeIndex !== index) {
        this.activeIndex = index;
      }
    },
    async requestData() {
      try {
        const currentRouter = this.$router.currentRoute;
        const id = currentRouter.query.storeId;
        if (!id) {
          return;
        }
        this.loading = true;
        await this.requestSellerInfo({ sellerId: id });
      } finally {
        this.getBannerData();
        this.loading = false;
      }
    },
    async follow() {
      try {
        if (notLogin()) {
          return;
        }
        const currentRouter = this.$router.currentRoute;
        const id = currentRouter.query.storeId;
        if (!id) {
          return;
        }
        if (this.sellerInfo.isFocus === this.followStatus.on) {
          await this.requestCollectSellerDel({
            sellerId: id,
          });
          this.$message.warning(this.$t("message.home.cancelSuccess"));
          await this.requestData();
          return;
        }
        await this.requestCollectSellerAdd({
          sellerId: id,
        });
        this.$message.success(this.$t("message.home.followedSuccess"));
        await this.requestData();
      } finally {
        //
      }
    },
  },
  deactivated(){
    // console.log('22 ->', 22);
    localStorage.setItem('storePagescrollTop',this.scrollTop);
  }
};
</script>

<style lang="scss">
html[dir="rtl"]{
  .store .wrap .head-wrap .box .container-left img{
    margin-right: 0;
    margin-left: 20px;
  }
  .store .wrap .head-wrap .box .container-left{
    padding-right: 86px;
    padding-left: 0;
  }
  .store .wrap .head-wrap .box .btn{
    margin-right: 0;
    margin-left: 34px;
  }
  .commodity-content-list{
    margin-left: 0;
    margin-right: 20px;
  }
  .commodity-content-title{
    padding-left: 28px;
    padding-right: 0;
  }
  .commodity-content-title .search-content{
    right: auto;
    left: 0;
  }
}
.store {
  .wrap {
    width: 100%;
    margin-top: -13px;    
    .head-wrap {
      width: 100%;
      height: 300px;
      background-size: cover;
      background-position: center center;
      background-repeat: no-repeat;
      // padding-top: 58px;
      position: relative;
      overflow: hidden;
      transition: all 1s ease;
      .swiper-container {
        height: 100%;
      }
      .swiper-wrapper img {
        width: 100% !important;
        height: 100% !important;
        object-fit: cover;
      }
      .banner {
        z-index: -1;
        width: 100%;
        position: absolute;
        top: 50%;
        height: 100%;
        transform: translateY(-50%);
        object-fit: cover;
        image-rendering: pixelated;
      }
      .box {
        max-width: 1010px;
        height: 135px;
        left: 0;
        top: 0;
        bottom: 0;
        right: 0;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 4px;
        margin: auto;
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: absolute;
        z-index: 11;
        .bg {
          z-index: -1;
          width: 1010px;
          position: absolute;
          top: 50%;
          transform: translateY(-50%);
        }
        .desc {
          display: flex;
          flex-direction: column;
          justify-content: center;
        }
        .container-left {
          display: flex;
          justify-content: flex-start;
          padding-left: 86px;

          img {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            object-fit: cover;
            margin-right: 20px;
          }

          p {
            font-family: "Roboto";
            font-style: normal;
            font-weight: 600;
            font-size: 18px;
            line-height: 19px;
            margin-bottom: 0;
            color: #f5f5f7;
            -webkit-text-stroke: 0px #333;
            filter: drop-shadow(2px 3px 0px rgba(51, 51, 51,.4));
          }

          span {
            font-family: "PingFang HK";
            font-style: normal;
            font-weight: 400;
            font-size: 12px;
            width: 600px;
            display: inline-block;
            overflow: hidden; //超出的文本隐藏
            text-overflow: ellipsis; //溢出用省略号显示
            white-space: nowrap;
            color: #e0e0e0;
            margin-top: 5px;
          }

          .img-list {
            

            img {
              width: 26px;
              height: 26px;
              margin-right: 10px;
            }
          }
        }

        .btn {
          color: #f5f5f7;
          background: var(--color-main);
          border-radius: 25px;
          width: 95px;
          height: 24px;
          line-height: 24px;
          border: none;
          margin-right: 34px;
          display: flex;
          justify-content: center;
          align-items: center;
          will-change: filter;
          transition: filter 800ms;
          &:hover {
            filter: drop-shadow(0 0 4px var(--color-main));
          }
          i {
            color: #fff;
            font-size: 14px;
          }
        }
      }
    }

    .nav {
      width: 100%;
      padding: 8px 0;
      background: #212121;
      display: flex;
      align-items: center;

      ul {
        width: 100%;
        max-width: 1160px;
        list-style: none;
        margin: 0 auto;
        height: 100%;
        height: 40px;

        li {
          float: left;
          color: #fff;
          margin-right: 59px;
          font-weight: 500;
          cursor: pointer;
          height: 100%;
          line-height: 35px;
        }
      }

      .active {
        border-bottom: 2px solid var(--color-main);
      }
    }
  }

  &-content {
    padding: 27px 0 20px;
  }
}

.commodity {
  &-wrap {
    align-items: flex-start;
    margin-top: -24px;

    ul {
      list-style: none;
      margin: 0;
      padding: 0;
    }
  }

  &-filter {
    width: 170px;
    border-right: 1px solid var(--color-border);

    h2 {
      width: 100%;
      text-align: center;
      font-weight: 600;
      font-size: 14px;
      color: var(--color-title);
      border-bottom: 1px solid var(--color-border);
      padding: 20px 0;
      margin-bottom: 20px;
    }

    &-item {
      text-align: left;
      width: 100%;
      font-weight: 400;
      font-size: 12px;
      color: var(--color-black);
      padding: 12px 0;
      cursor: pointer;

      &:hover {
        color: var(--color-main);
        border-right: 2px solid var(--color-main);
      }

      &-active {
        color: var(--color-main);
        border-right: 2px solid var(--color-main);
      }
    }
  }

  &-content {
    width: 100%;

    &-title {
      color: var(--color-black);
      padding: 22px 28px 0 28px;

      h2 {
        font-weight: 500;
        font-size: 14px;
        color: var(--color-black);
      }

      

      li {
        margin-right: 46px;
        cursor: pointer;

        span {
          font-weight: 500;
          font-size: 14px;
          margin-right: 5px;
        }

        > div {
          flex-direction: column;
        }
      }

      .el-icon-caret-top {
        margin-bottom: -8px;
      }
    }

    &-list {
      width: 100%;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(188px, 165px));
      grid-column-gap: 14px;
      grid-row-gap: 20px;
      align-content: center;
      margin-top: 17px;
      margin-left: 20px;
    }

    &-pagination {
      width: 100%;
      text-align: center;
      padding: 40px 0;
    }

    .no-data {
      display: flex;
      justify-content: center;
    }
  }
}
</style>
