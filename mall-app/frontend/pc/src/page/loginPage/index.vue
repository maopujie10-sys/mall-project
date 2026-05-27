<template>
  <div class="login">
    <EsHeaderView />
    <div class="app-container app-center">
      <div class="login-content">
        <el-row :gutter="20">
          <el-col :xs="0" :sm="12" :md="12" :lg="12" :xl="12">
            <div
              class="login-content-left flex-center"
              v-if="itemname !== 'Argos' && itemname !== 'FamilyShop' && itemname !== 'SM-wholesale shop'&& itemname !== 'ArgosShop'"
            >
              <img
                class="login-content-banner"
                :src="require('@/assets/image/loginBg.png')"
                alt="login"
              />
            </div>
            <div
              class="login-content-left flex-center"
              v-else-if="itemname == 'FamilyShop'"
              
            >
              <img
                class="login-content-banner"
                :src="require('@/assets/image/loginbg1.png')"
                alt="login"
              />
            </div>
            <div
              class="login-content-left flex-center"
              v-else-if="itemname == 'SM-wholesale shop'"
            >
              <img
                class="login-content-banner"
                :src="require('@/assets/image/loginbg2.jpg')"
                alt="login"
              />
            </div>
            <div class="login-content-left flex-center" v-else>
              <img
                class="login-content-banner"
                :src="require('@/assets/image/argoslogo.png')"
                alt="login"
              />
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12">
            <div class="login-content-right">
              <h1>{{ $t("message.home.loginIn") }}</h1>
              <div class="login-content-tab">
                <el-button
                  :type="isAccountLogin ? 'primary' : ''"
                  @click="changeLoginType(1)"
                >
                  {{ $t("message.home.orderEmail") }}
                </el-button>
                <el-button
                  :type="isAccountLogin ? '' : 'primary'"
                  @click="changeLoginType(2)"
                >
                  {{ $t("message.home.mobile") }}
                </el-button>
              </div>
              <div class="login-content-form">
                <EsAccountForm v-if="isAccountLogin" />
                <EsMobileForm v-else />
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
      <EsIconTips />
    </div>

    <EsFooterView />
  </div>
</template>

<script>
import EsAccountForm from "./accountForm.vue";
import EsMobileForm from "./mobileForm.vue";
import EsIconTips from "@/components/iconTips";
export default {
  name: "EsLogin",
  components: { EsAccountForm, EsMobileForm, EsIconTips },
  data() {
    return {
      // 1 账号登录 2 手机登录
      type: 1,
      itemname: process.env.VUE_APP_ITEM_NAME,
    };
  },
  computed: {
    isAccountLogin() {
      return this.type === 1;
    },
  },
  methods: {
    changeLoginType(type) {
      this.type = type;
    },
  },
};
</script>

<style lang="scss">
html[dir="rtl"]{
  .el-form-item /deep/ .el-form-item__error{
    right: 0;
    left: auto;
  }
  .el-input {
      .el-input__suffix {
          left: 5px;
          right: auto;
          margin-left: 10px;
      }
    }
   .el-input--suffix .el-input__inner {
          padding-left: 15px;
          padding-right: 15px;
      }  
}
.vue-country-item.selected .selected-text{
  display: none;
}
.login {
  &-content {
    border: 1px solid var(--color-border);
    border-radius: 4px;
    padding: 20px;
    max-width: 1074px;
    margin: 20px auto 30px auto;
    &-banner {
      width: 100%;
      height: 100%;
      max-width: 514px;
      max-height: 534px;
    }
    &-right {
      h1 {
        font-weight: 600;
        font-size: 36px;
        color: var(--color-black);
        margin: 15px 0 35px 0;
      }
    }

    &-tab {
      .el-button {
        min-width: 98px;
        height: 34px;
        margin-right: 20px;
        font-weight: 500;
        font-size: 14px;
        padding: 0;
      }
      margin-bottom: 20px;
    }
    &-form {
      .forgot-password {
        color: var(--color-main);
        font-size: 14px;
        font-weight: 400;
        cursor: pointer;
      }
      .el-form--label-top .el-form-item__label {
        display: initial;
        padding-bottom: 8px;
        font-weight: 500;
        font-size: 14px;
      }
      .el-input {
        .el-input__suffix {
          margin-right: 10px;
        }
        .el-input__inner {
          height: 50px;
          max-width: 500px;
        }
      }
      //   .el-input-group {
      //     .el-input-group__prepend {
      //       background-color: var(--color-white);
      //       width: 64px;
      //     }
      //     .el-input__inner {
      //       border-left: 0;
      //     }
      //   }
      .sing-in-btn {
        max-width: 500px;
        width: 100%;
        height: 58px;
        margin-top: 30px;
        font-weight: 700;
        font-size: 14px;
      }
      .tips {
        // width: 100%;
        // text-align: center;
        font-weight: 400;
        font-size: 14px;
        color: var(--color-title);
        span {
          color: var(--color-main);
          cursor: pointer;
        }
      }
      .form-phone {
        position: relative;
        cursor: pointer;
        .el-input__inner {
          padding-left: 100px;
        }
        .vue-country-popover-container {
          position: absolute;
          top: 50%;
          left: 0;
          transform: translateY(-50%);
        }
        .area-code {
          width: 80px;
          span {
            display: inline-block;
            width: 50px;
            padding-left: 15px;
          }
        }
      }
    }
  }

  &-bottom {
    max-width: 1000px;
    margin: 52px auto 107px auto;
    &-item {
      flex-direction: column;
    }
    span {
      font-weight: 500;
      font-size: 12px;
      margin-top: 15px;
    }
  }
}

.vue-country-intl-popover {
  z-index: 9999;
  .vue-country-item.selected {
    background-color: var(--color-main);
  }
  .vue-country-item:not(.selected):hover {
    background-color: var(--color-main);
  }
}

</style>
