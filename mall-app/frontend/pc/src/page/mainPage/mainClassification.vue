<template>
  <div class="main-classification app-container" v-loading="httpLoading">
    <div class="main-classification-title flex-between">
      <h1>
        {{ $t("message.home.recommendclass") }}
      </h1>
      <div class="all" @click="gotoClassificationPage">
        {{ $t("message.home.all" /**全部 */) }}
        <i class="el-icon-arrow-right"></i>
      </div>
    </div>
    <swiper
      :options="swiperOptions"
      ref="mainClassification"
      @mouseenter.native="mouseEnter"
      @mouseleave.native="mouseLeave"
    >
      <swiper-slide v-for="(item, index) in categoryList" :key="index"  @mouseenter="onEnterTd($event.target)">
        <div
          class="main-classification-item flex-center"
          @click="gotoCommodityPage(item.categoryId)"
        >
          <div class="img-content">
            <img :src="item.iconImg" alt="" />
          </div>
          <span :title="item.name">{{ item.name }}</span>
        </div>
      </swiper-slide>
    </swiper>
  </div>
</template>

<script>
// import { mapGetters, mapActions } from "vuex";
import { RecommendCategory } from "@/api/home";
export default {
  name: "EsMainClassification",
  data() {
    return {
      swiperOptions: {
        slidesPerView: 11,
        // spaceBetween: 6,
        autoplay: {
          delay: 3500,
          disableOnInteraction: false,
        },
      },
      httpLoading: false,
      categoryList: [],
    };
  },
  computed: {
    // ...mapGetters("home", ["categoryList"]),
  },
  methods: {
    // ...mapActions("home", ["requestCategoryList"]),
    onEnterTd(e){
      this.$Gsap.from(e,{
          delay: 0,
          duration: .5,
          scale:1.1,
          ease: "inOut"
        })
    },
    mouseEnter() {
      this.$refs.mainClassification.$swiper.autoplay.stop();
    },
    mouseLeave() {
      this.$refs.mainClassification.$swiper.autoplay.start();
    },
    showText(e){
      console.log('e ->', e);
    },
    hideText(){},
    async getCategorylist() {
      let res = await RecommendCategory({ pageSize: 50, pageNum: 1 });
      if (res.code == 0) {
        this.categoryList = res.data?.pageList;
      }
    },
    gotoCommodityPage(id) {
      this.$router.push({ name: "commodity", query: { id } });
    },
    gotoClassificationPage() {
      this.$router.push("/classification");
    },
  },
  async mounted() {
    try {
      this.httpLoading = true;
      // await this.requestCategoryList();
      this.getCategorylist();
    } finally {
      this.httpLoading = false;
    }
  },
};
</script>

<style lang="scss">
.main-classification {
  margin-top: 26px;
  margin-bottom: 16px;
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
    &:hover {
      .img-content {
        border-color: var(--color-main);
        transition: ease-in-out ;
        transform:scale(.95)
      }
      span {
        color: var(--color-main);
      }
    }
    .img-content {
      // padding: 5px 19px;
      border: 1px solid var(--color-border);
       
      margin-bottom: 7px;
      border-radius: 3px;
      width: 92px;
      height: 64px;
      display: flex;
      align-items: center;
      justify-content: center;
      > img {
        width: 52px !important;
        height: 52px !important;
        object-fit: contain;
      }
    }
    span {
      display: inline-block;
      max-width: 90px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }
  .swiper-container {
    cursor: pointer;
    font-size: 12px;
    // img {
    //   max-width: 92px;
    //   max-height: 64px;
    //   object-fit: cover;
    //   width: 100%;
    //   height: 100%;
    // }
  }
}
</style>
