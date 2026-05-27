<template>
  <el-form
    :model="loginModel"
    :rules="rules"
    ref="loginForm"
    label-position="top"
  >
    <el-form-item :label="$t('message.home.mobilePhone')" prop="username">
      <div class="form-phone">
        <el-input
          v-model.trim="loginModel.username"
          :placeholder="$t('message.home.pleaseEnterPhoneNumer')"
          maxlength="30"
          @keyup.enter.native="loginEvent"
        ></el-input>
        <VueCountryIntl
          v-model="loginModel.areaCode"
          schema="popover"
          :searchInputPlaceholder="$t('message.home.searchCountry')"
          :noDataText="$t('message.home.noDataFound')"
        >
          <div class="area-code flex-between" slot="reference">
            <span>+{{ loginModel.areaCode }}</span>
            <i class="el-icon-caret-bottom"></i>
          </div>
        </VueCountryIntl>
      </div>
    </el-form-item>
    <el-form-item :label="$t('message.home.setPassword')" prop="password">
      <el-input
        v-model="loginModel.password"
        :type="showPassword ? 'password' : 'text'"
        :placeholder="$t('message.home.pleaseEnterPassword')"
        @keyup.enter.native="loginEvent"
      >
        <template slot="suffix">
          <img
            class="password-icon"
            :src="showPassword ? imageMap.close : imageMap.open"
            @click="showPassword = !showPassword"
          />
        </template>
      </el-input>
    </el-form-item>
    <div
      style="display: flex; justify-content: space-between; margin-top: 55px"
    >
      <p class="tips">
        {{ $t("message.home.noAccount") }}
        <span @click="goRegister">{{ $t("message.home.signUp") }}</span>
      </p>
      <span class="forgot-password" @click="openService">
        {{ $t("message.home.ForgotPassword") }}
      </span>
    </div>
    <el-form-item>
      <el-button class="sing-in-btn" type="primary" @click="loginEvent">
        {{ $t("message.home.signIn") }}
      </el-button>
    </el-form-item>
    <EsOnlineServiceView v-model="showOnlieService" />
    <Vcode
      :imgs="[img1, img2, img3, img4, img5]"
      :show="showVcoe"
      @success="onVCodeSuccess"
      :canvasHeight="200"
      @close="showVcoe = false"
      :sliderText="$t('message.home.滑动验证')"
      :successText="$t('message.home.vcodePass')"
      :failText="$t('message.home.vcodeFail')"
    />
  </el-form>
</template>

<script>
import { loginApi } from "@/api";
import { mapActions, mapMutations } from "vuex";
import VueCountryIntl from "vue-country-intl";
import common from "@/util/common";
import { BASE_AREA_CODE } from "@/common";
import "vue-country-intl/lib/vue-country-intl.css";
import Vcode from "vue-puzzle-vcode";
import { apiGetCustomerService } from "@/api/common";
export default {
  name: "EsMobileForm",
  components: { VueCountryIntl, Vcode },
  data() {
    return {
      showOnlieService: false,
      itemname: process.env.VUE_APP_ITEM_NAME,
      loginModel: {
        username: "",
        password: "",
        areaCode: BASE_AREA_CODE,
      },
      showPassword: true,
      showVcoe: false,
      img1: require("@/assets/image/slider/1.png"),
      img2: require("@/assets/image/slider/2.png"),
      img3: require("@/assets/image/slider/3.png"),
      img4: require("@/assets/image/slider/4.png"),
      img5: require("@/assets/image/slider/5.png"),
      imageMap: {
        open: require("@/assets/image/eye-open.png"),
        close: require("@/assets/image/eye-close.png"),
      },
      rules: {
        username: [
          common.ruleUtils.getRule(
            "required",
            this.$t("message.home.pleaseEnterPhoneNumer")
          ),
          common.ruleUtils.getRule("phone"),
        ],
        password: [
          common.ruleUtils.getRule(
            "required",
            this.$t("message.home.pleaseEnterPassword")
          ),
          common.ruleUtils.getRule("password"),
        ],
      },
      onlinePath:""
    };
  },
  activated() {
    this.loginModel.username = "";
    this.loginModel.password = "";
    this.loginModel.areaCode = BASE_AREA_CODE;
    this.$refs.loginForm.validateOnRuleChange = false;
    this.getOnlinePath()
  },
  methods: {
    ...mapActions(["getUserInfo"]),
    ...mapMutations({ setToken: "SETTOKEN" }),
    loginEvent() {
      if(this.itemname == 'Hive'){
        this.onVCodeSuccess()
      }else{
        this.showVcoe = true;
      }
    },
    openService() {
          // console.log('this.$refs ->', this.$refs);
          if (this.onlinePath) {
            window.open(
              this.onlinePath,
              "_blank"
            );
          } else {
          this.showOnlieService = true;
          }
        },
    async getOnlinePath() {
      let res = await apiGetCustomerService({code:'customer_service_url'});
      this.onlinePath = res.data.customer_service_url
    },
    onVCodeSuccess() {
      this.showVcoe = false;
      this.$refs.loginForm.validate(async (valid) => {
        if (valid) {
          try {
            this.loading = true;
            const loginResult = await loginApi({
              username: this.loginModel.username,
              password: encodeURIComponent(this.loginModel.password),
              areaCode: this.loginModel.areaCode,
              ...{
                username:
                  this.loginModel.areaCode + " " + this.loginModel.username,
              },
            });
            this.setToken(loginResult.data.token);
            await this.getUserInfo(loginResult.data);
            this.$message({
              message: this.$t(
                "message.home.loginSuccess" /**添加到购物车成功 */
              ),
              type: "success",
            });
            this.$refs.loginForm.resetFields();
            if (sessionStorage.getItem("path") == "/register") {
              this.$router.push("/");
              sessionStorage.setItem("path", "1");
            } else {
              this.$router.go(-1);
            }
          } finally {
            this.loading = false;
          }
        }
      });
    },
    goRegister() {
      this.$router.push("/register");
    },
  },
};
</script>
<style lang="scss" scoped>
html[dir="rtl"]{
  .el-form-item /deep/ .el-form-item__error{
    right: 0;
    left: auto;
  }
  .login-content-form .form-phone .vue-country-popover-container {
    left: 12px;
  }
  .login-content-form .form-phone .area-code span{
    width: auto;
    padding-left: 0;
  }
  .login-content-form .form-phone .area-code {
    width: auto;
  }
  .el-input__inner {
      padding-left: 30px;
      padding-right: 0;
   }
   .vue-country-item.selected .selected-text{
    display: none;
   }
}
.vue-country-item.selected .selected-text{
  display: none;
}
/deep/ .range-text {
  padding-left: 40px;
}
</style>