<template>
  <div id="app">
    <EsShopCartView v-if="isLogin" />
    <keep-alive>
      <router-view v-if="isRouterAlive" class="view">
      </router-view>
    </keep-alive>
    
    <router-view v-if="!isRouterAlive"></router-view>
    <ClientHeight/>
    
  </div>
</template>

<script>
  import { mapActions, mapMutations, mapGetters } from "vuex";
  import ClientHeight from "@/components/clientHeight/index.vue";
  export default {
    name: "App",
    data() {
      return {
        tuozhuaizuobiao: {
          width: 0,
          height: 0,
          top: 0,
          left: 0,
        },
        show_kefu: false,
        kefu_url: "",
        host_url: "",
        language: "",
        itemname: process.env.VUE_APP_ITEM_NAME,
      };
    },
    components: {
      ClientHeight,
    },
    computed: {
      ...mapGetters(["existToken", "isLogin"]),
      isRouterAlive() {
        return this.$route.meta.keepAlive;
      },
    },
    /**
     * 此代码会存在bug， beforeunload, 只应该处理存储token
     * refresh时去获取一次用户信息，更新用户相关状态，而不能是整个store
     */
    created() {
      localStorage.setItem("scroll", 0);
      const currentRouter = this.$router.currentRoute;
      console.log('currentRouter ->', currentRouter);
      if (currentRouter.query.code) {
        localStorage.setItem("agentCode", currentRouter.query.code);
      }
      let link = document.head.querySelector("link");
      link.href = this.itemname =='Shopify'?require('@/assets/image/shopify.webp'): this.itemname == 'TikTok-Wholesale' || this.itemname =='SM-wholesale shop' ? require(`@/assets/image/${this.itemname}/logo.svg`):this.itemname !== 'TikTok' && this.itemname !== 'Laz'? require(`@/assets/image/${this.itemname}/${this.itemname}logo.svg`): require(`@/assets/image/${this.itemname}/${this.itemname}logo.png`);
      document.title = this.itemname;
      if(this.itemname == 'TikTok' || this.itemname == 'TikTok-Wholesale'){
        document.documentElement.style.setProperty(`--color-main`, '#000');
        document.documentElement.style.setProperty(`--color-submain`, '#000');
        document.documentElement.style.setProperty(`--hover-color`, '#404040');
        document.documentElement.style.setProperty(`--background`, '#fff');
        document.documentElement.style.setProperty(`--bg-border-color`, '#404040');
        document.documentElement.style.setProperty(`--active-button`, '#404040');
        document.documentElement.style.setProperty(`--color-footer`, '#EB174F');
      }
      if(this.itemname == 'Hive' || this.itemname == 'Green Mall'){
        document.documentElement.style.setProperty(`--color-main`, '#56B069');
        document.documentElement.style.setProperty(`--color-submain`, '#56B069');
        document.documentElement.style.setProperty(`--hover-color`, '#255D83');
        document.documentElement.style.setProperty(`--background`, '#fff');
        document.documentElement.style.setProperty(`--active-button`, '#56B069');
        document.documentElement.style.setProperty(`--bg-border-color`, '#56B069');
        document.documentElement.style.setProperty(`--color-footer`, '#56B069');
      }
      if(this.itemname == 'Laz'){
        document.documentElement.style.setProperty(`--color-main`, '#110288');
        document.documentElement.style.setProperty(`--color-submain`, '#0A0057');
        document.documentElement.style.setProperty(`--hover-color`, '#FC019D');
        document.documentElement.style.setProperty(`--background`, '#fff');
        document.documentElement.style.setProperty(`--bg-border-color`, '#FC019D');
        document.documentElement.style.setProperty(`--active-button`, '#FC019D');
        document.documentElement.style.setProperty(`--color-footer`, '#FC019D');
      }
      if(this.itemname == 'INT Overstock'){
        document.documentElement.style.setProperty(`--color-main`, '#1A4E8A');
        document.documentElement.style.setProperty(`--color-submain`, '#0D2D58');
        document.documentElement.style.setProperty(`--hover-color`, '#0079D2');
        document.documentElement.style.setProperty(`--background`, '#fff');
        document.documentElement.style.setProperty(`--bg-border-color`, '#1A4E8A');
        document.documentElement.style.setProperty(`--active-button`, '#0D2D58');
        document.documentElement.style.setProperty(`--color-footer`, '#0079D2');
      }
      if(this.itemname == 'AntMall'){
        document.documentElement.style.setProperty(`--color-main`, '#1C1196');
        document.documentElement.style.setProperty(`--color-submain`, '#0A0639');
        document.documentElement.style.setProperty(`--hover-color`, '#0A0639');
        document.documentElement.style.setProperty(`--background`, '#fff');
        document.documentElement.style.setProperty(`--bg-border-color`, '#0A0639');
        document.documentElement.style.setProperty(`--active-button`, '#0A0639');
        document.documentElement.style.setProperty(`--color-footer`, '#F78F22');
      }
      if(this.itemname == 'SM-wholesale shop'){
        document.documentElement.style.setProperty(`--color-main`, '#002FFF');
        document.documentElement.style.setProperty(`--color-submain`, '#0023BD');
        document.documentElement.style.setProperty(`--hover-color`, '#0023BD');
        document.documentElement.style.setProperty(`--background`, '#fff');
        document.documentElement.style.setProperty(`--bg-border-color`, '#0023BD');
        document.documentElement.style.setProperty(`--active-button`, '#0023BD');
        document.documentElement.style.setProperty(`--color-footer`, '#F78F22');
      }
      // if (sessionStorage.getItem('store')) {
      //   this.$store.replaceState(
      //       Object.assign(
      //           {},
      //           this.$store.state,
      //           JSON.parse(sessionStorage.getItem('store'))
      //       )
      //   );
      // }
      // 在页面刷新时将store保存到sessionStorage里
      // window.addEventListener('beforeunload', () => {
      //   sessionStorage.setItem('store', JSON.stringify(this.$store.state));
      // });
      
    },
    mounted() {
      if (this.existToken) {
        this.getUserInfo();
      }
      const rtlLangs = ['ar', 'ur', 'fa', 'pr'];
      const lang = localStorage.getItem('ES_LANG')
      if (rtlLangs.includes(lang)) {
        document.documentElement.setAttribute('dir', 'rtl');
      } else {
        document.documentElement.setAttribute('dir', 'ltr');
      }
    },
    methods: {
      ...mapActions(["getUserInfo"]),
      ...mapMutations({
        updateCheckProductPay: "shopCart/updateCheckProductPay",
        updateShopCart: "shopCart/updateShopCart",
      }),
      //拖拽事件
      resize(newRect) {
        this.tuozhuaizuobiao.width = newRect.width;
        this.tuozhuaizuobiao.height = newRect.height;
        this.tuozhuaizuobiao.top = newRect.top;
        this.tuozhuaizuobiao.left = newRect.left;
      },
      activateEv() {
        // 结局文本框无法输入的问题
        if (this.$refs["chat"] && this.$refs["chat"].$refs["input"]) {
          this.$refs["chat"].$refs["input"].focus();
        }
      },
    },
  };
</script>

<style>
  #app {
    min-height: 100vh;
    overflow-x: hidden;
  }
  html,body{
    scroll-behavior: smooth;
  }
  body {
    margin: 0;
    overflow: visible;
  }

  /* 客服 */
  .service-box {
    position: fixed;
    right: 15px;
    bottom: 1px;
    cursor: pointer;
    z-index: 9999;
  }

  .vdr.active:before {
    display: none;
  }
</style>
<style scoped lang="scss">
  .kefu {
    position: fixed;
    right: 500px;
    top: 200px;
    cursor: pointer;
    z-index: 3;
  }

  .embed-responsive-item {
    width: 100%;
    height: 100%;
    border: none;
  }

  .kefu-title {
    width: 100%;
    height: 61px;
    position: relative;
    text-align: center;
    background: linear-gradient(
      90.3deg,
      rgba(45, 45, 53, 0.71) 0.21%,
      #23232e 99.83%
    );
    border-radius: 10px 10px 0px 0px;
  }

  .kegu-nrkegu-nr {
    width: 100%;
    height: 559px;
  }

  .kefu-title span {
    text-align: center;
    font-style: normal;
    font-weight: 400;
    font-size: 20px;
    line-height: 61px;
    color: #ffffff;
  }

  .kefu-title img {
    position: absolute;
    width: 30px;
    height: 30px;
    right: 21px;
    top: 16px;
  }

  .kefu-tuozhuai {
    box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.5);
    outline: none;
    background: #ffffff;
    border-radius: 10px;
  }
</style>
