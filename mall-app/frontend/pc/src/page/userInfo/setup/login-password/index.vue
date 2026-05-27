<template>
  <div class="login-password">
    <div class="page-title" style="cursor: pointer" @click="goBack">
      <i class="el-icon-arrow-left"></i> {{ $t("message.home.LoginPassword") }}
    </div>
    <el-form ref="form" class="form" :model="form" :rules="rules">
      <el-form-item :label="$t('message.home.oldPassword')" prop="oldPassword">
        <el-input
          v-model="form.oldPassword"
          :type="showPassword.oldPassword ? 'text' : 'password'"
          :placeholder="$t('message.home.pleaseEnterOldPassword')"
        >
          <template #suffix>
            <div
              class="eye-icon"
              @click="showPassword.oldPassword = !showPassword.oldPassword"
            >
              <img
                :src="showPassword.oldPassword ? eyeIcon.open : eyeIcon.close"
                alt=""
              />
            </div>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item :label="$t('message.home.newPassword')" prop="newPassword">
        <el-input
          v-model="form.newPassword"
          :type="showPassword.newPassword ? 'text' : 'password'"
          :placeholder="$t('message.home.plaseeEnterNewPassword')"
        >
          <template #suffix>
            <div
              class="eye-icon"
              @click="showPassword.newPassword = !showPassword.newPassword"
            >
              <img
                :src="showPassword.newPassword ? eyeIcon.open : eyeIcon.close"
                alt=""
              />
            </div>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item
        :label="$t('message.home.confirmPassword')"
        prop="confirmPassword"
      >
        <el-input
          v-model="form.confirmPassword"
          :type="showPassword.confirmPassword ? 'text' : 'password'"
          :placeholder="$t('message.home.plaseeENterConfirmPassword')"
        >
          <template #suffix>
            <div
              class="eye-icon"
              @click="
                showPassword.confirmPassword = !showPassword.confirmPassword
              "
            >
              <img
                :src="
                  showPassword.confirmPassword ? eyeIcon.open : eyeIcon.close
                "
                alt=""
              />
            </div>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item>
        <el-button
          class="form-submit-btn"
          type="submit"
          :loading="loading"
          block
          @click="update"
        >
          {{ $t("message.home.btnSure") }}
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { mapActions } from "vuex";
import common from "@/util/common";
export default {
  data() {
    return {
      form: {
        oldPassword: "",
        newPassword: "",
        confirmPassword: "",
      },
      showPassword: {
        oldPassword: false,
        newPassword: false,
        confirmPassword: false,
      },
      eyeIcon: {
        close: require("@/assets/image/eye-close.png"),
        open: require("@/assets/image/eye-open.png"),
      },
      rules: {
        oldPassword: [
          common.ruleUtils.getRule(
            "required",
            this.$t("message.home.pleaseEnterOldPassword")
          ),
          common.ruleUtils.getRule("password"),
        ],
        newPassword: [
          common.ruleUtils.getRule(
            "required",
            this.$t("message.home.plaseeEnterNewPassword")
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
              if (value !== this.form.newPassword) {
                callback(new Error(this.$t("message.home.twoPawword")));
                return;
              }
              callback();
            },
          }),
        ],
      },
      loading: false,
    };
  },
  methods: {
    ...mapActions("user", ["requestUpdateLoginPasswordList"]),
    update() {
      console.log('this.form.newPassword ->', this.form.newPassword);
      this.$refs.form.validate(async (valid) => {
        if (valid) {
          try {
            this.loading = true;
            await this.requestUpdateLoginPasswordList({
              old_password: encodeURIComponent(this.form.oldPassword),
              password: encodeURIComponent(this.form.newPassword),
              re_password: encodeURIComponent(this.form.confirmPassword),
            });
            this.$message({
              message: this.$t("message.home.successTips"),
              type: "success",
            });
            this.$router.replace("/userInfo/dashboard?index=1");
          } finally {
            this.loading = false;
          }
        }
      });
    },
    goBack() {
      this.$router.push("/userInfo/setup");
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
   .el-form-item /deep/ .el-form-item__label{
    float: right;
  }
}
.login-password {
  width: 422px;
  .eye-icon {
    width: 30px;
    height: 40px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    > img {
      width: 14px;
      margin: 0;
    }
  }
}
</style>
