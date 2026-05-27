<template>
  <div class="transaction-password">
    <div class="page-title" style="cursor: pointer" @click="goBack">
      <i class="el-icon-arrow-left"></i>
      {{ $t("message.home.transactionPassword") }}
    </div>
    <el-form ref="form" class="form" :model="form" :rules="rules">
      <el-form-item
        v-if="isBindSafePassword"
        :label="$t('message.home.oldPassword')"
        prop="oldPassword"
      >
        <el-input
          v-model="form.oldPassword"
          maxlength="6"
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
          maxlength="6"
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
          maxlength="6"
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
          common.ruleUtils.getRule("sixNumber"),
        ],
        newPassword: [
          common.ruleUtils.getRule(
            "required",
            this.$t("message.home.plaseeEnterNewPassword")
          ),
          common.ruleUtils.getRule("sixNumber"),
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
  computed: {
    isBindSafePassword() {
      return this.$store.state.userInfo.safeword !== 0;
    },
  },
  mounted() {
    if (!this.isBindSafePassword) {
      this.form.oldPassword = "1";
    }
  },
  methods: {
    ...mapActions("user", [
      "requestSetSafePasswordList",
      "requestUpdateSafePasswordList",
    ]),
    goto() {
      this.$message({
        message: this.$t("message.home.successTips"),
        type: "success",
      });
      this.$router.replace("/userInfo/dashboard?index=1");
      this.$store.state.user.currentIndex = 0;
      this.$store.dispatch("getUserInfo");
    },
    goBack() {
      this.$router.push("/userInfo/setup");
    },
    update() {
      this.$refs.form.validate(async (valid) => {
        if (valid) {
          try {
            this.loading = true;
            if (this.isBindSafePassword) {
              await this.requestUpdateSafePasswordList({
                old_safeword: this.form.oldPassword,
                safeword: this.form.newPassword,
                re_safeword: this.form.confirmPassword,
              });
              this.goto();
              return;
            }
            await this.requestSetSafePasswordList({
              safeword: this.form.newPassword,
              re_safeword: this.form.confirmPassword,
            });
            this.goto();
          } finally {
            this.loading = false;
          }
        }
      });
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
.transaction-password {
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
