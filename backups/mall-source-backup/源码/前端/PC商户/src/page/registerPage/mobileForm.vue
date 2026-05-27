<template>
  <el-form
    :model="registerModel"
    :rules="rules"
    ref="registerForm"
    label-position="top"
  >
    <el-form-item :label="$t('message.home.mobilePhone')" prop="username">
      <div class="form-phone">
        <el-input
          v-model.trim="registerModel.username"
          :placeholder="$t('message.home.pleaseEnterPhoneNumer')"
          maxlength="30"
          @keyup.enter.native="registerEvent"
        ></el-input>
        <VueCountryIntl
          v-model="registerModel.areaCode"
          schema="popover"
          :searchInputPlaceholder="$t('message.home.searchCountry')"
          :noDataText="$t('message.home.noDataFound')"
        >
          <div class="area-code flex-between" slot="reference">
            <span>+{{ registerModel.areaCode }}</span>
            <i class="el-icon-caret-bottom"></i>
          </div>
        </VueCountryIntl>
      </div>
    </el-form-item>
    <el-form-item :label="$t('message.home.setPassword')" prop="password">
      <el-input
        v-model="registerModel.password"
        :type="showPassword ? 'password' : 'text'"
        :placeholder="$t('message.home.pleaseSetLoginPassword')"
        @keyup.enter.native="registerEvent"
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
    <el-form-item
      :label="$t('message.home.confirmPassword')"
      prop="confirmPassword"
    >
      <el-input
        :type="showConfirm ? 'password' : 'text'"
        v-model="registerModel.confirmPassword"
        :placeholder="$t('message.home.plaseeENterConfirmPassword')"
      >
        <template slot="suffix">
          <img
            class="password-icon"
            :src="showConfirm ? imageMap.close : imageMap.open"
            @click="showConfirm = !showConfirm"
          />
        </template>
      </el-input>
    </el-form-item>
    <el-form-item>
      <p class="tips">
        {{ $t("message.home.loginTips") }}
        <span @click="goLogin">{{ $t("message.home.loginIn") }}</span>
      </p>
      <el-button
        class="sing-in-btn"
        type="primary"
        :loading="loading"
        @click="registerEvent"
      >
        {{ $t("message.home.signUp") }}
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script>
import { mapActions, mapMutations } from "vuex";
import { resgisterApi } from "@/api";
import VueCountryIntl from "vue-country-intl";
import common from "@/util/common";
import "vue-country-intl/lib/vue-country-intl.css";
import { BASE_AREA_CODE } from "@/common";
export default {
  name: "EsMobileForm",
  components: { VueCountryIntl },
  data() {
    return {
      loading: false,
      agentCode:'',
      registerModel: {
        username: "",
        password: "",
        confirmPassword: "",
        areaCode: BASE_AREA_CODE,
      },
      showPassword: true,
      showConfirm: true,
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
        confirmPassword: [
          common.ruleUtils.getRule(
            "required",
            this.$t("message.home.plaseeENterConfirmPassword")
          ),
          common.ruleUtils.getRule("validator", "", {
            validator: (rule, value, callback) => {
              if (value !== this.registerModel.password) {
                callback(new Error(this.$t("message.home.twoPawword")));
                return;
              }
              callback();
            },
          }),
        ],
      },
    };
  },
   activated(){
    this.registerModel.username = '';
    this.registerModel.password = '';
    this.registerModel.confirmPassword = '';
    this.$refs.reigsterForm.validateOnRuleChange = false;
  },
  methods: {
    ...mapActions(["getUserInfo"]),
    ...mapMutations({ setToken: "SETTOKEN" }),
    registerEvent() {
      this.$refs.registerForm.validate(async (valid) => {
        if (valid) {
          try {
            if (localStorage.getItem('agentCode')){
              this.agentCode = localStorage.getItem('agentCode');
            }
            this.loading = true;
            const reigsterResult = await resgisterApi({
              // ...this.registerModel,
              username: this.registerModel.username,
              password: (this.registerModel.password),
              confirmPassword: (this.registerModel.confirmPassword),
              ...{
                type: 1,
                re_password: (this.registerModel.password),
                username:
                  this.registerModel.areaCode +
                  " " +
                  this.registerModel.username,
                 agentCode:''
              },
            });
            this.setToken(reigsterResult.data.token);
            await this.getUserInfo(reigsterResult.data);
            this.$refs.registerForm.resetFields();
            this.$message({
              message: this.$t("message.home.registerSuccess"),
              type: "success",
            });
            this.$router.replace("/");
          } finally {
            this.loading = false;
          }
        }
      });
    },
    goLogin() {
      sessionStorage.setItem("path", "/register");
      this.$router.push("/login");
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
   .rigister-content-form .form-phone .vue-country-popover-container {
    left: 12px;
  }
      .rigister-content-form .form-phone .area-code span{
    width: auto;
    padding-left: 0;
  }
  .rigister-content-form .form-phone .area-code {
    width: auto;
  }
}
.vue-country-item.selected .selected-text{
  display: none;
}
</style>
