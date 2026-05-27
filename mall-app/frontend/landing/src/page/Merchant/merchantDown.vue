<template>
  <div class="merchantDown">
    <div class="merchantDown-wrap">
      <div class="down-header">
        <div class="left">
          <img src="@/assets/image/Merchant/logo.png" />
        </div>
        <div class="right">

          <el-dropdown @command="handleSetLang" :trigger="'click'">
            <div class="cn-wrap">
              <img class="cn-img" :src="languageIcon" />
              <img class="down-img" src="@/assets/image/Merchant/down.png" />
            </div>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item :command="index" v-for="(item, index) in lang" :key="index">
                <div class="lang-item">
                  <img :src="item.icon" />
                  {{ item.title }}
                </div>
              </el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </div>
      </div>
      <div class="down-center">
        <div class="title">{{$t('商户管理')}}</div>
        <div class="text">{{$t('请使用网页登录或下载业务管理后台APP')}}
        </div>
        <div class="but-wrap">
          <div class="but" @click="openUrl(1)">
            <img src="@/assets/image/Merchant/iphone.png" />
            IOS
          </div>
          <div class="but ml40" @click="openUrl(1)">
            <img src="@/assets/image/Merchant/andorid.png" />
            Andorid
          </div>
        </div>
        <div class="web-but">
          <div class="left">
            <div>
              <img src="@/assets/image/Merchant/web.png" />
            </div>
            <div class="webAccess" @click="openUrl(2)">
              <p class="web-title1">{{$t('网络访问')}}</p>
              <p class="web-title2">{{$t('无需下载，直接登录即可')}}</p>
            </div>
          </div>
          <div class="right">
            <img src="@/assets/image/Merchant/right.png" />
          </div>
        </div>
      </div>
    </div>
    <mer-chant-footer></mer-chant-footer>

  </div>
</template>

<script>
// import merChantHeader from "./components/mer-chant-header"
import merChantFooter from "./components/mer-chant-footer"
import { DropdownMenu, DropdownItem, Dropdown } from 'element-ui'
import { mapGetters, mapMutations } from "vuex";
export default {
  name: 'merchantDown',
  data() {
    return {
      lang: [
        {
          title: '简体中文',
          key: 'zh-CN',
          icon: require('@/assets/image/language/cn.png')
        },
        {
          title: 'English',
          key: 'en-US',
          icon: require('@/assets/image/language/usa.png')
        },
        {
          title: '繁体中文',
          key: 'CN',
          icon: require('@/assets/image/language/tw.png')
        }
      ],
    }
  },

  computed: {
    languageIcon() {
      const language = this.$store.getters.language || 'CN'
      const icon = {
        'zh-CN': require('@/assets/image/language/cn.png'),
        'en-US': require('@/assets/image/language/usa.png'),
        'CN': require('@/assets/image/language/tw.png')
      }
      return icon[language]
    },
    ...mapGetters({
      activeLang: 'language'
    })
  },
  components: {
    // merChantHeader,
    merChantFooter,
    [DropdownMenu.name]: DropdownMenu,
    [DropdownItem.name]: DropdownItem,
    [Dropdown.name]: Dropdown
    
  },
  created() {

  },
  methods: {
    ...mapMutations(['setLanguage']),
    handleSetLang(index) {
      console.log(index)
      // 设置i18n.locale 组件库会按照上面的配置使用对应的文案文件
      this.$i18n.locale = this.lang[index].key
      // // 提交mutations
      // this.setLanguage(this.lang[index].key)
    },
    openUrl(index) {
      switch (index) {
        case 1:
          location.href = "https://jtxkqp.com/h0o0.app"
          break;
        case 2:
        location.href = "https://tiktokmall666.com/ww"
          break;
        default:
          break;
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.merchantDown {

  // min-width: 1200px;
  .merchantDown-wrap {
    background: url('@/assets/image/Merchant/down-bg.png') no-repeat center center;
    background-size: cover;
    width: 100%;
    min-width: 1200Px;
    margin: 0 auto;

    .down-header {
      height: 70Px;
      width: 1200Px;
      margin: 0 auto;
      display: flex;
      align-items: center;

      .left {
        flex: 1;

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
          }

          .down-img {
            margin-left: 5Px;
          }

        }


      }
    }

    .down-center {
      width: 840Px;
      margin: 0 auto;
      padding: 250Px 30Px;

      .title {
        font-weight: 600;
        font-size: 48Px;
        color: #fff;
        text-align: center;

      }

      .text {
        width: 800Px;
        font-size: 24Px;
        text-align: center;
        color: #fff;
        margin: 0 auto;
        margin-top: 20Px;
      }

      .but-wrap {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 70Px;

        .ml40 {
          margin-left: 40Px;
        }

        .but {
          width: 193Px;
          height: 62Px;
          border: 1px solid #fff;
          font-size: 20Px;
          color: #fff;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;

          img {
            height: 30Px;
            margin-right: 5Px;
            display: block;
          }

        }
      }

      .web-but {
        width: 368Px;
        height: 69Px;
        border: 1px solid #fff;
        margin: 0 auto;
        display: flex;
        padding: 0 20px;
        margin-top: 40Px;
        cursor: pointer;
        align-items: center;

        .left {
          flex: 1;
          display: flex;
          align-items: center;

          img {
            width: 37Px;
          }

          .webAccess {
            .web-title1 {
              font-size: 20Px;
              color: #fff;
            }

            .web-title2 {
              font-size: 12Px;
              color: #fff;
              margin-top: 2Px;
              margin-left: 5Px;
            }
          }
        }

        .right {
          img {
            width: 19Px;
          }
        }
      }
    }
  }
}

.lang-item {
  display: flex;
  align-items: center;

  img {
    width: 20Px;
    height: 20Px;
    margin-right: 5px;
  }
}

@media screen and (max-width:500Px) {
  .merchantDown-wrap {
    min-width: 100% !important;
  }

  .down-header {
    width: 100% !important;

    .left {
      padding-left: 15Px !important;
    }

    .right {
      padding-right: 15Px;
    }
  }

  .down-center {
    width: 100% !important;
    padding: 0 0 40Px 0 !important;

    .text {
      width: 100% !important;
    }

    .but-wrap {
      display: block !important;

      .ml40 {
        margin-left: 0Px !important;
      }

      .but {
        margin-left: 15Px !important;
        margin-top: 35Px;
      }
    }

    .web-but {
      width: 81% !important;
    }
  }
}

</style>
