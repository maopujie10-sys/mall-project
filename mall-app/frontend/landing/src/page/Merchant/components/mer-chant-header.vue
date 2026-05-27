<template>
  <div class="mer-chant-header">
    <div class="down-header">
      <router-link to="" class="left">
        <img :src="itemname=='SIMON' || itemname == 'Azedi'?require(`@/assets/image/${itemname}/logo1.svg`):itemname=='AntMall'?require(`@/assets/image/${itemname}/logo.svg`):itemname == 'TikTok' || itemname == 'Shop2u' ? require(`@/assets/image/${itemname}/logo.png`):itemname == 'Laz' ? require(`@/assets/image/${itemname}/logo1.svg`):require(`@/assets/image/${itemname}/shoplogo.svg`)" :style="itemname == 'Azedi'?'height:73Px':''"/>
      </router-link>

      <div class="right">
        <el-dropdown @command="handleSetLang" :trigger="'click'">
          <div class="cn-wrap">
            <img class="cn-img" :src="languageIcon" />
            <img class="down-img" src="@/assets/image/Merchant/down.png" />
          </div>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item
              :command="index"
              v-for="(item, index) in lang"
              :key="index"
            >
              <div class="lang-item" v-if="item?.name !== itemname">
                <img :src="item.icon" />
                {{ item.title }}
              </div>
            </el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </div>
    </div>
    <div class="content">
      <!--      <img v-if="url" src="@/assets/image/Merchant/image37.png" />-->
      <!--      <img v-else src="@/assets/image/Merchant/bg.png" alt="" />-->
      <div class="content-text">
        <p class="title" v-if="title">
          {{ title }}
          <span><br/>{{shippingInfo}}</span>
        </p>
        <p class="title" v-else>{{ itemname=='Mbuy'?'Argos':itemname }} {{ $t("商家入驻") }}</p>
        <p v-if="url">
          {{ $t("titleInfo",{name:itemname=='Mbuy'?'Argos':itemname}) }}<br />
          {{ $t("titleInfo1") }}
        </p>
        <div v-if="itemname == 'Argos'" style="margin-top: 5px">
          <p>{{$t("Are you new to managing a store and in need of guidance? Don't worry! we offer comprehensive consultation services to assist you every step of the way. For further support, please reach out to our dedicated tutors via：")}}</p>
          <p style="margin-top: 4px">Telegram : <a href="https://t.me/Colleen88888888">@Colleen88888888</a> </p>
          <p style="margin-top: 4px">WhatsApp: +44 7451260989</p>
          <p style="margin-top: 4px">{{$t("They will be more than happy to assist you throughout the entire process.")}}</p>
        </div>
      </div>
    </div>
    <img :src="banner" class="bg-image" />
  </div>
</template>

<script>
import { Dropdown, DropdownItem, DropdownMenu } from "element-ui";
import { mapGetters, mapMutations } from "vuex";

export default {
  name: "mer-chant-header",
  props: ["title", "url","shippingInfo"],
  data() {
    return {
      banner: require("@/assets/image/banner.jpg"),
      itemname: process.env.VUE_APP_ITEM_NAME,
      lang: [
        {
          title: "English",
          key: "en-US",
          icon: require("@/assets/image/language/usa.png"),
        },
        {
          title: "Deutsch",
          key: "de",
          icon: require("@/assets/image/language/de.png"),
        },
        {
          title: "Français",
          key: "fr",
          icon: require("@/assets/image/language/fr.png"),
        },
        {
          title: "Русский",
          key: "ru",
          icon: require("@/assets/image/language/ru.png"),
        },

        {
          title: "Español",
          key: "es",
          icon: require("@/assets/image/language/es.png"),
        },
        {
          title: "Português",
          key: "pt",
          icon: require("@/assets/image/language/pt.png"),
        },
        {
          title: "Italiano",
          key: "it",
          icon: require("@/assets/image/language/it.png"),
        },
        {
          title: "Melayu",
          key: "ms",
          icon: require("@/assets/image/language/ms.png"),
        },
        {
          title: "Afrikaans",
          key: "af",
          icon: require("@/assets/image/language/af.png"),
        },
        {
          title: "Ελληνικά",
          key: "el",
          icon: require("@/assets/image/language/els.png"),
        },
        {
          title: "中文繁体",
          key: "CN",
          name: 'Mbuy',
          icon: require("@/assets/image/language/tw.png"),
        },
        {
          title: "中文简体",
          key: "zh-CN",
          name: 'Mbuy',
          icon: require("@/assets/image/language/cn.png"),
        },
        {
          title: "Türkçe",
          key: "tr",
          icon: require("@/assets/image/language/tr.png"),
        },

        {
          title: "日本語",
          key: "ja",
          icon: require("@/assets/image/language/ja.png"),
        },
        {
          title: "한국어",
          key: "ko",
          icon: require("@/assets/image/language/ko.png"),
        },
        {
          title: "ภาษาไทย",
          key: "th",
          icon: require("@/assets/image/language/th.png"),
        },
        {
          title: "Filipino",
          key: "ph",
          icon: require("@/assets/image/language/ph.png"),
        },
        {
          title: "العربية",
          key: "ar",
          icon: require("@/assets/image/language/ar.png"),
        },
        {
          title: "Tiếng Việt",
          key: "vi",
          icon: require("@/assets/image/language/vi.png"),
        },
        {
          title: "हिन्दी",
          key: "hi",
          icon: require("@/assets/image/language/hi.png"),
        },
        {
          title: "Bahasa Indonesia",
          key: "id",
          icon: require("@/assets/image/language/id.png"),
        },
      ],
    };
  },
  computed: {
    languageIcon() {
      const language = this.$store.getters.language;
      const icon = {
        "zh-CN": require("@/assets/image/language/cn.png"),
        "en-US": require("@/assets/image/language/usa.png"),
        "en": require("@/assets/image/language/usa.png"),
        CN: require("@/assets/image/language/tw.png"),
        cn: require("@/assets/image/language/tw.png"),
        de: require("@/assets/image/language/de.png"),
        fr: require("@/assets/image/language/fr.png"),
        es: require("@/assets/image/language/es.png"),
        el: require("@/assets/image/language/els.png"),
        it: require("@/assets/image/language/it.png"),
        pt: require("@/assets/image/language/pt.png"),
        ru: require("@/assets/image/language/ru.png"),
        ja: require("@/assets/image/language/ja.png"),
        ko: require("@/assets/image/language/ko.png"),
        th: require("@/assets/image/language/th.png"),
        tr: require("@/assets/image/language/tr.png"),
        ms: require("@/assets/image/language/ms.png"),
        af: require("@/assets/image/language/af.png"),
        ph: require("@/assets/image/language/ph.png"),
        ar: require("@/assets/image/language/ar.png"),
        vi: require("@/assets/image/language/vi.png"),
        hi: require("@/assets/image/language/hi.png"),
        id: require("@/assets/image/language/id.png"),
      };
      return icon[language];
    },
    ...mapGetters({
      activeLang: "language",
    }),
  },
  created() {
    this.$i18n.locale = this.$store.getters.language
  },
  components: {
    [DropdownMenu.name]: DropdownMenu,
    [DropdownItem.name]: DropdownItem,
    [Dropdown.name]: Dropdown,
  },
  methods: {
    ...mapMutations(["setLanguage"]),
    handleSetLang(index) {
      // console.log('header');
      let path = this.$route.path; //先获取路由路径
      this.$router.replace(path);
      if(window.parent){
        window.parent.postMessage({'lang':this.lang[index].key}, '*')
      }
      // 设置i18n.locale 组件库会按照上面的配置使用对应的文案文件
      this.$i18n.locale = this.lang[index].key;
      // // 提交mutations
      this.setLanguage(this.lang[index].key);
      location.reload();
    },
  },
};
</script>

<style lang="scss" scoped>
html[dir="rtl"]{
    .down-img{
      margin-left: 0;
      margin-right: 5Px;
    }
    .lang-item img{
      margin-left: 5Px;
      margin-right: 0;
    }
    @media screen and (max-width: 500px){
      .mer-chant-header .content .content-text{
        left: auto;
      }
    }
}
.mer-chant-header {
  font-size: 14Px;
  background: transparent;
  position: relative;
  min-height: 440Px;

  .bg-image {
    position: relative;
    width: 100%;
    height: 100%;
    z-index: -1;
  }

  .down-header {
    height: 70Px;
    width: 1200Px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    position: absolute;
    top: 0;
    left: 50% !important;
    transform: translateX(-50%);
    z-index: 10;
    .left {
      flex: 1;
      cursor: pointer;

      img {
        height: 43Px;
      }
    }

    .right {
      display: flex;
      cursor: pointer;

      .cn-wrap {
        display: flex;
        align-items: center;

        .cn-img {
          width: 20Px;
          height: 20Px;
          border-radius: 50%;
        }

        .down-img {
          margin-left: 5Px;
        }
      }
    }
  }

  .content {
    width: 1200Px;
    height: 420Px;
    margin: 0 auto;
    position: absolute;
    padding-bottom: 100Px;
    left: 50% !important;
    transform: translateX(-50%);

    img {
      width: 100%;
    }

    .content-text {
      width: 58%;
      position: absolute;
      top: 12%;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: flex-start;

      p {
        width: 100%;
        font-size: 20Px;
        color: rgba(166, 166, 166, 1);
      }

      .title {
        color: var(--color-main);
        font-size: 48Px;
        margin-bottom: 4Px;
        margin-top: 25px;
      }
    }
  }
}
.el-dropdown-menu {
  height: 240Px !important;
  overflow-y: auto !important;
}
.rtl {
  .cn-img {
    margin-left: 6px;
    margin-right: 0;
  }
  .el-dropdown-menu {
    .lang-item{
      >img{
        margin-left: 6px;
        margin-right: 0;
      }
    }
  }
}
@media screen and (max-width: 500px) {
  .mer-chant-header {
    min-width: 100% !important;
    background: #212121;
    font-size: 14px;
    position: relative;
    height: 380px;

    .bg-image {
      position: absolute;
      width: 180%;
      height: 100%;
      z-index: 0;
      top: 0;
      right: 0;
      object-fit: cover;
    }

    .down-header {
      width: 100% !important;
      position: relative;
      z-index: 2;

      .left {
        padding-left: 15px !important;
      }

      .right {
        padding-right: 15px;
      }
    }

    .content {
      width: 100% !important;
      margin: 0 auto;
      position: relative;
      z-index: 4;
      padding: 0 15px;
      height: auto;
      img {
        width: 100%;
      }

      .content-text {
        width: 88%;
        position: absolute;
        top: 0;
        left: 30px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: flex-start;
        padding-bottom: 15px;
        margin-bottom: 15px;
        p {
          width: 100%;
          font-size: 12px;
          color: rgba(166, 166, 166, 1);
        }

        .title {
          color: var(--color-main);
          font-size: 14px;
        }
      }
    }
  }
}

.lang-item {
  display: flex;
  align-items: center;

  img {
    width: 20px;
    height: 20px;
    margin-right: 5px;
  }
}
</style>
