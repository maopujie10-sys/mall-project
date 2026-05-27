<template>
  <div id="app" style="width: 100%; height: 100%">
    <!-- 页面缓存 -->
    <keep-alive>
      <router-view v-if="$route.meta.keepAlive"></router-view>
    </keep-alive>
    <router-view v-if="!$route.meta.keepAlive"></router-view>
    <!-- 页面缓存 -->
  </div>
</template>

<script>
import {Overlay} from "vant";
import {mapMutations} from "vuex";
import {getStorage,dateFormat,loadJs} from '@/utils/utis'

export default {
  name: "App",
  data() {
    return {
      show: false,
      timer: "",
      itemname: process.env.VUE_APP_ITEM_NAME,
    };
  },
  components: {
    [Overlay.name]: Overlay,
  },
  created() {
    let link = document.head.querySelector("link");
    link.href = this.itemname == 'Azedi'||this.itemname == 'Sam-wholesaleShop'?require(`@/assets/image/${this.itemname}/logo.svg`) : this.itemname == 'INT Overstock' ? require(`@/assets/image/${this.itemname}/ico.png`) : this.itemname == 'TikTok-Wholesale' || this.itemname == 'SM-wholesale shop'|| this.itemname == 'SIMON'|| this.itemname == 'Alibaba'|| this.itemname == 'Sky City'? require(`@/assets/image/${this.itemname}/logo.svg`):this.itemname == 'TikTok' || this.itemname == 'Laz' ? require(`@/assets/image/${this.itemname}/${this.itemname}logo.png`) : require(`@/assets/image/${this.itemname}/${this.itemname}logo.svg`)
    document.title = this.itemname;
    if (this.itemname == 'Argos Shop') {
        document.title = "Argos | Order online today for fast home delivery";
      }
    // document.documentElement.style.setProperty(*--main-color*, process. env. VUE_APP MAIN COLOR)
    if (this.itemname == 'TikTok' || this.itemname == 'TikTok-Wholesale' || this.itemname == 'SIMON') {
      document.documentElement.style.setProperty(`--color-main`, '#EB174F');
    }
    if (this.itemname == 'Hive' || this.itemname == 'GreenMall') {
      document.documentElement.style.setProperty(`--color-main`, '#56B069');
    }
    if (this.itemname == 'Laz') {
      document.documentElement.style.setProperty(`--color-main`, '#FC019D');
    }
    if (this.itemname == 'INT Overstock') {
      document.documentElement.style.setProperty(`--color-main`, '#0079D2');
    }
    if (this.itemname == 'Azedi') {
      document.documentElement.style.setProperty(`--color-main`, '#16ADDA');
    }
    if (this.itemname == 'Worten') {
      document.documentElement.style.setProperty(`--color-main`, '#ED241D');
    }
    if (this.itemname == 'Sam-wholesaleShop') {
      document.documentElement.style.setProperty(`--color-main`, '#004B8E');
    }

  },
  mounted() {
    const lang = getStorage('merchant-landing-page-lang');
    this.$nextTick(() => {
      if (['ar'].includes(lang)) {
        document.body.className = 'rtl';
        document.body.style.direction = 'rtl';
      } else {
        document.body.className = 'ltr';
        document.body.style.direction = 'ltr';
      }
    });
    //this.insertIm()
  },
  watch: {
    $route(to) {
      this.changeLang(to);
    },
  },
  methods: {
    ...mapMutations(["setLanguage"]),
    async insertIm(){
        let lang = localStorage.getItem('merchant-landing-page-lang')
        if (this.itemname == 'FamilyShop'){
          await loadJs(`https://lt.xhduh.com/im_create_iframe.js?router=client&id=${Math.random()}`)
          if (lang == 'CN' || lang == 'zh-CN') lang = 'zh-CN'
          else lang = 'en'
            im_create_iframe_client.setParams({
              userType: 1,
              userName: this.$t('游客'),
              lastLoginTime: dateFormat(new Date()),
              lang:'en',
            });
            im_create_iframe_client.eventOrder(() => {});
        }
      },
    handleSetLang(lang) {
      // 设置i18n.locale 组件库会按照上面的配置使用对应的文案文件
      document.documentElement.setAttribute('lang', lang)
      this.$i18n.locale = lang;
      // 提交mutations
      let path = this.$route.path; // 先获取路由路径
      if (this.$route.query.avatar) {
        if (this.$route.query.avatar == "undefined") {
          localStorage.setItem("avater", "1");
        } else {
          localStorage.setItem("avater", this.$route.query.avatar);
        }
      } else {
        localStorage.setItem("avater", "1");
      }
      if (this.$route.query.usercode) {
        localStorage.setItem("usercode", this.$route.query.usercode);
      }
      if (!window.parent.origin.indexOf('ww') == false) {
        this.$router.replace(path);
      }
      location.reload();
      this.setLanguage(lang);
    },
    changeLang(to) {
      document.body.scrollTop = 0;
      console.log('to ->', to);
      document.documentElement.scrollTop = 0;
      // this.token = to.query.token;
      if(to.query.token && to.query.name){
        sessionStorage.setItem('SellToken',to.query.token)
        sessionStorage.setItem('itemName',to.query.name)
      }
      //  this.itemname = to.query.name;
      if (to.query.lang && !to.query) {
        this.handleSetLang("en-US")
      }
      if (to.query.lang) {
        console.log(to.query.lang);
        switch (to.query.lang) {
          case "zh-CN":
          case "cn":
            this.handleSetLang("zh-CN");
            break;
          case "en":
          case "en-US":
            this.handleSetLang("en-US");
            break;
          case "zh-TW":
          case "TW":
          case "tw":
            this.handleSetLang("CN");
            break;
          case "null":
            this.handleSetLang("en-US");
            break;
          case "af":
            this.handleSetLang("af");
            break;
          case "ja":
            this.handleSetLang("ja");
            break;
          case "ko":
            this.handleSetLang("ko");
            break;
          case "th":
            this.handleSetLang("th");
            break;
          case "ms":
            this.handleSetLang("ms");
            break;
          case "el":
            this.handleSetLang("el");
            break;
          case "es":
            this.handleSetLang("es");
            break;
          case "fr":
            this.handleSetLang("fr");
            break;
          case "de":
            this.handleSetLang("de");
            break;
          case "it":
            this.handleSetLang("it");
            break;
          case "pt":
            this.handleSetLang("pt");
            break;
          case "ru":
            this.handleSetLang("ru");
            break;
          case "tr":
            this.handleSetLang("tr");
            break;
          case "ph":
            this.handleSetLang("ph");
            break;
          case "ar":
            this.handleSetLang("ar");
            break;
          case "vi":
            this.handleSetLang("vi");
            break;
          case "id":
            this.handleSetLang("id");
            break;
          case "hi":
            this.handleSetLang("hi");
            break;
            // Add more cases for specific language codes here if needed
          default:
            // Fallback to "en-US" for unknown language codes
            this.handleSetLang("en-US");
        }
      }
    },
  },
}
</script>

<style lang="scss">
@import "@/assets/init.scss";
.im_create_iframe_client_wrapper,.im_create_iframe_client_wrapper_open {
  z-index: 9999999 !important;
}
//返回
.van-nav-bar .van-icon {
  color: #333333;
}

.van-uploader__upload-icon {
  font-size: 48px !important;
}

.van-uploader__upload {
  background-color: white !important;
  border: 1px dashed #b8bcc5;
}

// tab标签短横线颜色
.van-tabs__line {
  background-color: #1552f0 !important;
}

.van-tab__text {
  font-size: 14px !important;
}

.van-nav-bar__text {
  color: #999999;
}
</style>
