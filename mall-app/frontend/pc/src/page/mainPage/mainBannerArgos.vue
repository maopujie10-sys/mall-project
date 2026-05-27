<template>
  <div class="main-banner app-container">
    <div class="main-banner-Argos" v-loading="loading">
      <swiper :options="swiperOptions1">
        <swiper-slide v-for="item in filterBanner" :key="item.id">
          <img :src="item.imgUrl" alt="" @click="goLink(item.link)" />
        </swiper-slide>
      </swiper>
    </div>
  </div>
</template>

<script>
  // import { mapGetters, mapActions } from "vuex";
  import { HomeBanner } from "@/api/home";
  export default {
    name: "mainBanner",
    data() {
      return {
        loading: false,
        swiperOptions1: {
          autoplay: {
            delay: 4500,
            disableOnInteraction: false,
            roundLengths: true,
            loop:false
          },
        },
        filterBanner: [],
      };
    },
    computed: {
      // filterBanner() {
      //   return [
      //     "https://argos-shop-online.s3.amazonaws.com/PCbanner/sbanner_9.png",
      //     "https://argos-shop-online.s3.amazonaws.com/PCbanner/sbanner_10.png",
      //     "https://argos-shop-online.s3.amazonaws.com/PCbanner/sbanner_11.png",
      //     "https://argos-shop-online.s3.amazonaws.com/PCbanner/sbanner_12.png",
      //     "https://argos-shop-online.s3.amazonaws.com/PCbanner/sbanner_13.png",
      //   ];
      // return this.homeBanner
      // return this.homeBanner.map(src => src.replace(/imagePath=banner/g, 'imagePath=PCbanner'))
      // },
    },
    methods: {
      goLink(path) {
        if (path) {
          window.open(path, "_blank");
        }
      },
      async requestData() {
        this.loading = true;
        let res = await HomeBanner({
          pageNum: 1,
          pageSize: 5,
          type: "pc",
          imgType: 1,
        });

        if (res.data.result.length > 0) {
          this.filterBanner = res.data.result;
        } else {
          this.filterBanner = [
            {
              imgUrl:
                "https://argos-shop-online.s3.amazonaws.com/PCbanner/sbanner_9.png",
            },
            {
              imgUrl:
                "https://argos-shop-online.s3.amazonaws.com/PCbanner/sbanner_10.png",
            },
            {
              imgUrl:
                "https://argos-shop-online.s3.amazonaws.com/PCbanner/sbanner_10.png",
            },
            {
              imgUrl:
                "https://argos-shop-online.s3.amazonaws.com/PCbanner/sbanner_11.png",
            },
            {
              imgUrl:
                "https://argos-shop-online.s3.amazonaws.com/PCbanner/sbanner_12.png",
            },
          ];

          //     "
        }

        this.loading = false;
      },
    },
    mounted() {
      this.requestData();
    },
  };
</script>

<style lang="scss">
  .main-banner {
    &-Argos {
      height: 400px;
      .swiper-container {
        height: 400px !important;
        cursor: pointer;
        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
          image-rendering: revert;
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
