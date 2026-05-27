<template>
  <div class="mer-chant-footer">
    <div class="footer-wrap">
      <div class="bottom-wrap">
        <div class="logo-wrap">
          <img src="@/assets/image/Merchant/logo.png" />
        </div>
        <div class="serviece-wrap">
          <ul>
            <li class="title">{{ $t('我的帐户') }}</li>
            <li><a href="JavaScript:;" @click="openUrl(1)">{{ $t('登录') }}</a></li>
            <li><a href="JavaScript:;" @click="openUrl(2)">{{ $t('收藏商品') }}</a></li>
            <li><a href="JavaScript:;" @click="openUrl(3)">{{ $t('购买记录') }}</a></li>
            <li><a href="JavaScript:;" @click="openUrl(4)">{{ $t('帐户') }}</a></li>

          </ul>
          <ul class="two-footer">
            <li class="title">{{ $t('卖家专区') }}</li>
            <li><a href="JavaScript:;" @click="openUrl(5)">{{ $t('做卖家') }}</a></li>
            <li><a href="#" @click="openUrl(6)">{{ $t('卖家面板登录') }}</a></li>
          </ul>
        </div>
      </div>

      <div class="copyright">
        <p>{{ $t('版权所有© 2019-2022 SHOP PO, LLC. 版权所有') }}</p>
        <p>{{ $t('使用本网站，即表示您同意其服务条款（禁止将本网站上的任何信息用于商业用途）及其隐私政策。 当您使用我们的一个链接进行购买时，我们可能会赚取佣金。') }}</p>
      </div>
    </div>
  </div>
</template>

<script>

import { Toast } from "vant";
import { isLogin } from '@/utils/utis'
export default {
  name: 'mer-chant-footer',
  data() {
    return {
      screenWidth: document.body.clientWidth,
      labelPosition: 'top',
    }
  },
  created() {
    // this.getStatusInfo()
    if (this.screenWidth >= 500) {
      this.labelPosition = "left"
    } else {
      this.labelPosition = "top"
    }
  },
  components: {
    [Toast.name]: Toast
  },
  methods: {
    openUrl(index) {
      switch (index) {
        case 1:
          if (this.labelPosition=="left"){
            location.href = "https://tiktokmall666.com/ww"
          }
          if (this.labelPosition=="top"){
            location.href = "https://tiktokmall666.com/www"
          }
          break;
        case 2:
          if (this.labelPosition=="left"){
            location.href = "https://tiktokmall666.com/ww"
          }
          if (this.labelPosition=="top"){
            location.href = "https://tiktokmall666.com/www"
          }
          break;
        case 3:
          if (this.labelPosition=="left"){
            location.href = "https://tiktokmall666.com/ww"
          }
          if (this.labelPosition=="top"){
            location.href = "https://tiktokmall666.com/www"
          }
          break;
        case 4:
          if (this.labelPosition=="left"){
            location.href = "https://tiktokmall666.com/ww"
          }
          if (this.labelPosition=="top"){
            location.href = "https://tiktokmall666.com/www"
          }
          break;
          case 5:
            if (this.labelPosition=="left"){
              location.href = "https://tiktokmall666.com/ww"
            }
            if (this.labelPosition=="top"){
              location.href = "https://tiktokmall666.com/www"
            }
            break;
          case 6:
            if (this.labelPosition=="left"){
              location.href = "https://tiktokmall666.com/ww"
            }
            if (this.labelPosition=="top"){
              location.href = "https://tiktokmall666.com/www"
            }
          break;
        default:
          break;
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.mer-chant-footer {
  min-width: 1200Px;
  background: #212121;
  font-size: 14Px;

  .footer-wrap {
    width: 1200PX;
    margin: 0 auto;

    .logo-wrap {
      height: 70Px;

      img {
        height: 35Px;
      }
    }
  }

  .bottom-wrap {
    display: flex;
    border-bottom: 1px solid #3F3F3F;
    align-items: center;

    .address-input {
      input {
        width: 288Px;
        height: 43Px;
        background: #FFFFFF;
        border-radius: 4Px;
        border: none;
        padding: 0 20Px;
      }
    }

    .subscribe-but {
      width: 153Px;
      height: 43Px;
      border: 1px solid var(--color-main);
      border-radius: 4Px;
      color: var(--color-main);
      text-align: center;
      line-height: 43Px;
      margin-top: 20Px;
      cursor: pointer;
    }
  }

  .serviece-wrap {
    color: #FFFFFF;
    padding-top: 40Px;
    padding-bottom: 40Px;

    ul {
      display: flex;
      margin-left: 100Px;
      align-items: center;

      li {
        font-size: 12Px;
        margin-right: 50Px;

        a {
          color: #FFFFFF;
        }
      }

      .title {
        font-size: 16Px;
        color: var(--color-main);
        font-weight: bold;
      }
    }

    .two-footer {
      margin-top: 30Px;
    }
  }

  .copyright {
    color: #6B6B6B;
    font-size: 12Px;
    padding: 20Px 0;
  }
}

@media screen and (max-width:500Px) {
  .mer-chant-footer {
    min-width: 100% !important;

    .footer-wrap {
      width: 100% !important;
    }

    .bottom-wrap {
      display: block !important;
      margin-left: 15Px;
      padding-bottom: 20Px;
    }

    .serviece-wrap {
      padding: 0 !important;
      display: block !important;
      margin-left: 0px !important;

      ul {
        margin-left: 0px;
        margin-top: 30PX;
        display: block !important;

        li {
          margin-top: 20Px;
        }
      }
    }

    .copyright {
      padding: 15Px;
    }

    .logo-wrap {
      padding-top: 15Px;
      height: 50Px !important;
    }
  }
}
</style>
