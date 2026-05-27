<template>
  <div class="main-banner app-container">
    <el-row :gutter="5">
      <el-col :xs="24" :sm="24" :md="14" :lg="14" :xl="14">
        <div class="main-banner-left" v-loading="loading">
          <swiper :options="swiperOptions1">
            <swiper-slide v-for="item in filterBanner" :key="item.id">
              <img :src="item?.imgUrl" alt="" @click="goLink(item.link)" />
            </swiper-slide>
          </swiper>
        </div>
      </el-col>
      <el-col :xs="24" :sm="24" :md="10" :lg="10" :xl="10">
        <div class="main-banner-right flex-start" v-loading="loading">
          <div class="main-banner-right-group">
            <swiper :options="swiperOptions2">
              <swiper-slide
                v-for="(item, idx) in leftBanner.slice(0, 2)"
                :key="idx"
              >
                <img :src="item?.imgUrl" @click="goLink(item.link)" />
              </swiper-slide>
            </swiper>
            <swiper :options="swiperOptions3">
              <swiper-slide
                v-for="(item, idx) in leftBanner.slice(2, 4)"
                :key="idx"
              >
                <img :src="item?.imgUrl" alt="" @click="goLink(item.link)" />
              </swiper-slide>
            </swiper>
          </div>
          <div class="main-banner-right-group">
            <swiper :options="swiperOptions2">
              <swiper-slide
                v-for="(item, idx) in leftBanner.slice(4, 6)"
                :key="idx"
              >
                <img :src="item?.imgUrl" alt="" @click="goLink(item.link)" />
              </swiper-slide>
            </swiper>
            <swiper :options="swiperOptions3">
              <swiper-slide
                v-for="(item, idx) in leftBanner.slice(6, 8)"
                :key="idx"
              >
                <img :src="item?.imgUrl" alt="" @click="goLink(item.link)" />
              </swiper-slide>
            </swiper>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { HomeBanner } from "@/api/home";

export default {
  name: "mainBanner",
  data() {
    return {
      banner1: require("@/assets/image/banner/banner-1.jpeg"),
      banner2: require("@/assets/image/banner/banner2.jpeg"),
      banner3: require("@/assets/image/banner/banner3.jpeg"),
      banner4: require("@/assets/image/banner/right1.jpeg"),
      banner5: require("@/assets/image/banner/right2.jpeg"),
      banner6: require("@/assets/image/banner/right3.jpeg"),
      banner7: require("@/assets/image/banner/right4.jpeg"),
      banner8: require("@/assets/image/banner/right5.jpeg"),
      banner9: require("@/assets/image/banner/right6.jpeg"),
      banner10: require("@/assets/image/banner/right8.jpeg"),
      loading: false,
      swiperOptions1: {
        autoplay: {
          delay: 4500,
          loop:false,
          disableOnInteraction: false,
          roundLengths: true,
        },
      },
      swiperOptions2: {
        autoplay: {
          delay: 4500,
          loop:false,
          disableOnInteraction: false,
          roundLengths: true,
        },
      },
      swiperOptions3: {
        autoplay: {
          delay: 4500,
          loop:false,
          disableOnInteraction: false,
          roundLengths: true,
        },
      },
      filterBanner: [],
      leftBanner: [],
    };
  },

  mounted() {
    this.getBanner();
  },
  methods: {
    goLink(path) {
      if (path) {
        window.open(path, "_self");
      }
    },
    async getBanner() {
      this.loading = true;
      let res = await HomeBanner({
        pageNum: 1,
        pageSize: 8,
        type: "pc",
        imgType: 1,
      });
      if (res.data.result.length >= 1) {
        this.filterBanner = res.data.result;
      } else {
        this.filterBanner = [
          {
            imgUrl: this.banner1,
          },
          {
            imgUrl: this.banner2,
          },
          {
            imgUrl: this.banner3,
          },
        ];
      }
      let rs = await HomeBanner({
        pageNum: 1,
        pageSize: 8,
        type: "pc",
        imgType: 0,
      });
      if (rs.data.result.length >= 1) {
        this.leftBanner = rs.data.result;
      } else {
        this.leftBanner = [
          {
            imgUrl: this.banner4,
          },
          {
            imgUrl: this.banner5,
          },
          {
            imgUrl: this.banner6,
          },
          {
            imgUrl: this.banner7,
          },
          {
            imgUrl: this.banner8,
          },
          {
            imgUrl: this.banner9,
          },
          {
            imgUrl: this.banner10,
          },
          // {
          //   imgUrl:
          //     "https://shy-shop-test.s3.amazonaws.com/PCbanner/sbanner_8.png",
          // },
        ];
      }
      this.loading = false;
    },
  },
};
</script>

<style lang="scss">
.main-banner {
  &-left {
    height: 310px;
    .swiper-container {
      height: 310px !important;
      cursor: pointer;
      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        image-rendering: pixelated;
      }
    }
  }
  &-right {
    // height: 314px;
    &-group {
      display: flex;
      justify-content: center;
      align-content: center;
      flex-direction: column;
      width: 100%;
      .swiper-container {
        height: 152px;
        width: 242px;
        margin-bottom: 6px;
        cursor: pointer;
        &:last-child {
          margin-bottom: 0;
        }
        .swiper-slide {
          height: 152px;
          width: 242px;
          overflow: hidden;
          > img {
            width: 100%;
            height: 100%;
          }
        }
      }
      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
    }
  }
}
.swiper-slide.swiper-slide-active{
  -webkit-transform: translate3d(0px, 0px, 0px) rotateX(0deg) rotateY(0deg) !important;
  -moz-transform: translate3d(0px, 0px, 0px) rotateX(0deg) rotateY(0deg) !important;
  -o-transform: translate3d(0px, 0px, 0px) rotateX(0deg) rotateY(0deg) !important;
  -ms-transform: translate3d(0px, 0px, 0px) rotateX(0deg) rotateY(0deg) !important;
  transform: translate3d(0px, 0px, 0px) rotateX(0deg) rotateY(0deg) !important;
}
</style>
