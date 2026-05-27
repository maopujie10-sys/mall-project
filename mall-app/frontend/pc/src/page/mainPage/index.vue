<template>
  <div class="home" id="home">
    <EsHeaderView />
    <MainBanner v-if="itemname !== 'Argos' && itemname !=='INT Overstock' " />
    <MainArgosBanner v-else />
    <MainClassification />
    <MainDaily />

    <div
      v-if="bannerShow"
      :style="{ 'background-image': 'url(' + banner1 + ')' }"
      class="banner-content"
    >
      <div class="content">
        <p>{{ $t("message.home.homeBannertips1") }}</p>
        <p>{{ $t("message.home.homeBannertips2") }}</p>
        <h3>{{ $t("message.home.homeBannertips3") }} $100,000</h3>
        <div @click="joinStore">{{ $t("message.home.homeBannerbtn") }}</div>
      </div>
    </div>
    <MainRecommend @onload="bannerShow = true" />
    <MainRecommendStore @onload="downloadShow = true" />
    <div
      :class="{ active: downloadShow }"
      :style="{ 'background-image': 'url(' + banner2 + ')' }"
      class="download-content"
      v-if="itemname !== 'TikTok-Wholesale'"
    >
      <div class="download">
        <h3 v-if="itemname !== 'Hive'">
          {{ $t("message.home.homeDownloadtips1") }}
        </h3>
        <h3 v-else>{{ $t("message.home.电商批发商场") }}</h3>
        <h3></h3>
        <div class="tips">
          <div class="item">{{ $t("message.home.homeDownloadtips2") }}</div>
          /
          <div class="item">{{ $t("message.home.homeDownloadtips3") }}</div>
        </div>
        <div class="btn-content" v-if="itemname !== 'Hive' && itemname !== 'TikTok-Wholesale'">
          <div class="item" @click="downClickA">
            <img :src="android" alt="" />
            <p>{{ $t("message.home.homeDownloadtips4") }}</p>
          </div>
          <div class="item" @click="downClickI">
            <img :src="iOS" alt="" />
            <p>{{ $t("message.home.homeDownloadtips5") }}</p>
          </div>
        </div>
      </div>
      <!-- <div class="code-content">
        <div class="content">
          <VueQr :size="100" :text="downAppUrl" :margin="0" />
        </div>
        <p>{{ $t("message.home.homeDownloadtips6") }}</p>
      </div> -->
    </div>
    <EsIconTips />
    <EsFooterView />
  </div>
</template>

<script>
import config from "@/config/index";
import { mapGetters } from "vuex";
import MainRecommend from "./mainRecommend.vue";
import MainBanner from "./mainBanner.vue";
import MainArgosBanner from "./mainBannerArgos.vue";
import MainClassification from "./mainClassification.vue";
import MainDaily from "./mainDaily.vue";
import MainRecommendStore from "./mainRecommendStore.vue";
// import VueQr from "vue-qr";

import EsIconTips from "@/components/iconTips";
export default {
  name: "HomeView",
  components: {
    MainRecommend,
    MainBanner,
    MainClassification,
    MainDaily,
    MainRecommendStore,
    EsIconTips,
    MainArgosBanner,
    // VueQr,
  },
  data() {
    return {
      itemname: process.env.VUE_APP_ITEM_NAME,
      bannerShow: false,
      downloadShow: false,
      banner1:
        process.env.VUE_APP_ITEM_NAME == "FamilyShop"
          ? require("@/assets/image/familyShop_banner.png") : process.env.VUE_APP_ITEM_NAME == "SM-wholesale shop"
          ? require("@/assets/image/SM-1.jpg")
          : require("@/assets/image/ads/banner_01.png"),
      banner2: require("@/assets/image/ads/banner_02.png"),
      android: require("@/assets/image/ads/android01.png"),
      iOS: require("@/assets/image/ads/ios01.png"),
      tipsData: [
        {
          icon: require("@/assets/image/ads/icon_01.png"),
          name: "message.home.homeIconTips1",
        },
        {
          icon: require("@/assets/image/ads/icon_02.png"),
          name: "message.home.homeIconTips2",
        },
        {
          icon: require("@/assets/image/ads/icon_03.png"),
          name: "message.home.homeIconTips3",
        },
        {
          icon: require("@/assets/image/ads/icon_04.png"),
          name: "message.home.homeIconTips4",
        },
      ],
      lang: "",
      top: 0,
    };
  },
  computed: {
    ...mapGetters({
      downAppUrl: "home/downAppUrl",
      userInfo: "userInfo",
    }),
  },
  mounted() {
    // window.addEventListener('scroll',this.scrollHandle);//绑定页面滚动事件
    this.lang = localStorage.getItem("ES_LANG") || "en";
    const currentRouter = this.$router.currentRoute;
    if (currentRouter.query.code) {
      localStorage.setItem("agentCode", currentRouter.query.code);
    }
  },
  activated () {
    // console.log('sessionStorage.getItem("scrollY") ->', localStorage.getItem("scroll"));
    if( localStorage.getItem("scroll")){
      document.documentElement.scrollTop = localStorage.getItem("scroll")
    }
    // document.documentElement.scrollTop = this.$route.meta.scrollY
},
beforeDestroy () {
    // console.log('离开 ->');
    localStorage.setItem('scroll', document.documentElement.scrollTop)
    // window.removeEventListener('scroll', this.scrollHandle)
},
  methods: {
    // scrollHandle(e) {
    //    this.top = e.srcElement.scrollingElement.scrollTop; // 获取页面滚动高度
    //   console.log(this.top);
    // },
    joinStore() {
      window.open(
        config.HOST_URL +
          "/promote/#/" +
          "?lang=en" +
          "&avatar=" +
          this.userInfo.avatar
      );
    },
    downClickA() {
      if (this.itemname == "Meta") {
        window.open(config.HOST_URL + "/android.apk", "_blank");
      } else if (this.itemname == "Inchoi") {
        window.open(
          "https://play.google.com/store/apps/details?id=com.in.ceapp.go",
          "_blank"
        );
      } else if(this.itemname == 'Shop2u'){
        window.open("https://play.google.com/store/apps/details?id=com.commerce.app","_blank")
      }else{
        window.open(config.HOST_URL + "/app.html", "_blank");
      }
    },
    downClickI() {
      if (this.itemname == "Meta") {
        window.open(config.HOST_URL + "/IOS.mobileconfig", "_blank");
      }else if(this.itemname == 'Shop2u'){
        window.open("https://apps.apple.com/my/app/shop2u/id6448880380","_blank")
      } else {
        window.open(config.HOST_URL + "/app.html", "_blank");
      }
    },
  },
};
</script>

<style lang="scss" scoped>
html[dir="rtl"]{
  .banner-content{
    justify-content: flex-start;
  }
  .download-content{
    justify-content: flex-end;
  }
  .download-content > div.download > .btn-content > .item:nth-child(1){
    margin-right: 0;
    margin-left: 20px;
  }
}
.banner-content {
  width: 1200px;
  margin: 0 auto;
  height: 352px;
  overflow: hidden;
  background-position: center center;
  background-size: cover;
  background-repeat: no-repeat;
  display: flex;
  justify-content: flex-end;
  > .content {
    width: 650px;
    height: 352px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    > p {
      color: #2e2e23;
      font-size: 42px;
    }
    > h3 {
      color: #fa3835;
      font-size: 42px;
    }
    > div {
      padding: 0 40px;
      height: 50px;
      border-radius: 50px;
      line-height: 50px;
      background-color: #2e2e2e;
      color: #f1ce5a;
      font-size: 16px;
      margin-top: 20px;
      cursor: pointer;
      &:hover {
        background-color: #181818;
      }
    }
  }
}

.download-content {
  width: 1200px;
  margin: 0 auto;
  margin-bottom: 60px;
  height: 297px;
  overflow: hidden;
  background-position: center center;
  background-size: cover;
  background-repeat: no-repeat;
  display: flex;
  align-items: center;
  justify-content: space-between;
  opacity: 0;
  transition: all 0.3s ease;
  &.active {
    opacity: 1;
  }
  > div {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    &.download {
      // margin-left: 72px;
      width: 730px;
      font-weight: bold;
      margin-left: 10px;
      > h3 {
        font-size: 40px;
        letter-spacing: 2px;
        margin-left: 5px;
      }
      > .tips {
        height: 35px;
        line-height: 35px;
        display: flex;
        font-size: 24px;
        margin-top: 10px;
        > .item {
          // width: 100px;
          padding: 0 8px;
        }
      }
      > .btn-content {
        display: flex;
        margin-top: 15px;
        margin-left: 10px;
        > .item {
          // width: 154px;
          height: 37px;
          line-height: 37px;
          background-color: #fff;
          // color: var(--color-main);
          border-radius: 4px;
          border: 1px solid #000;
          display: flex;
          font-size: 14px;
          align-items: center;
          justify-content: center;
          padding: 5px;
          will-change: filter;
          transition: filter 500ms;
          &:nth-child(1) {
            margin-right: 20px;
          }
          &:hover {
            filter: drop-shadow(0 0 4px #333);
          }
          cursor: pointer;
          > img {
            margin-right: 10px;
          }
          p {
            overflow: hidden; //超出的文本隐藏
            text-overflow: ellipsis; //溢出用省略号显示
            white-space: nowrap;
          }
        }
      }
    }
    &.code-content {
      align-items: center;
      margin-right: 50px;
      padding-top: 20px;
      > .content {
        width: 108px;
        height: 108px;
        background-color: #fff;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      > p {
        font-size: 14px;
        color: #fff;
        margin-top: 15px;
      }
    }
  }
}

.tips-content {
  width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-around;
  margin-bottom: 60px;
  > .item {
    display: flex;
    flex-direction: column;
    align-items: center;
    > p {
      font-size: 12px;
      color: #000;
      margin-top: 15px;
    }
  }
}
</style>
