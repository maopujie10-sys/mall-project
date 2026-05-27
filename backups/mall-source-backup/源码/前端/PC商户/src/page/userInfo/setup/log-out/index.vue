<template>
  <div class="transaction-password">
    <div class="page-title" style="cursor: pointer" @click="goBack">
      <i class="el-icon-arrow-left"></i>
      {{ $t("message.home.账号注销") }}
    </div>
    <div class="log-container">
      <div>
        <div class="tit-log">{{ $t("message.home.您的账号") }}</div>
        <el-input v-model="accout" disabled />
      </div>
      <div>
        <div class="tit-log">{{ $t("message.home.为什么要离开") }}?</div>
        <el-input
          v-model="logoutReason"
          class="content"
          type="textarea"
          :placeholder="$t('message.home.pleaseInput')"
          resize="none"
          :maxlength="1000"
        />
      </div>
      <div>
        <el-button
          size="medium"
          style="width: 412px; height: 44px; margin-top: 22px"
          type="primary"
          @click="confirmEvent"
        >
          {{ $t("message.home.确定注销") }}
        </el-button>
      </div>
    </div>

    <el-dialog
      :title="$t('message.home.您确认要注销吗?')"
      :visible.sync="centerDialogVisible"
      width="30%"
      center
    >
      <span>{{ $t("message.home.cancelInfo") }}</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="centerDialogVisible = false">{{
          $t("message.home.Cancel")
        }}</el-button>
        <el-button type="primary" @click="openPass()">{{
          $t("message.home.同意注销")
        }}</el-button>
      </span>
    </el-dialog>
    <el-dialog
      class="es-dialog"
      :visible.sync="passwordDialog"
      :center="true"
      :append-to-body="true"
      width="475px"
    >
      <div slot="title" class="dialog-title">
        <span v-if="showModel === 0">{{ $t("message.home.desc3") }}</span>
        <!-- <span v-if="showModel === 1">{{
            $t("message.home.setUpPayPaw")
          }}</span>
          <span v-if="showModel === 2">{{
            $t("message.home.confirmPayPaw")
          }}</span> -->
      </div>
      <div class="pay-modal-content dialog-content">
        <h2 class="pay-modal-title" v-if="showModel !== 2">
          {{ $t("message.home.desc4") }}
        </h2>
        <!-- <h2 class="pay-modal-title" v-if="showModel === 2">
            {{ $t("message.home.desc6") }}
          </h2> -->
        <EsPayPassword
          ref="passwordRef"
          :type="'password'"
          :maxlength="6"
          @output="output"
        />
        <div class="pay-modal-btn">
          <el-button
            type="primary"
            :loading="payLoading"
            @click="pay"
            v-if="showModel === 0"
          >
            {{ $t("message.home.confirm") }}
          </el-button>
          <!-- <el-button
              type="primary"
              :loading="payLoading"
              @click="setUpPaw"
              v-if="showModel === 1"
            >
              {{ $t("message.home.confirm") }}
            </el-button>
            <div v-if="showModel === 2" class="pay-button-view">
              <el-button :loading="payLoading" @click="previous">
                {{ $t("message.home.previous") }}
              </el-button>
              <el-button
                type="primary"
                :loading="payLoading"
                @click="confirmPayPaw"
              >
                {{ $t("message.home.confirm") }}
              </el-button>
            </div> -->
        </div>
      </div>
    </el-dialog>
  </div>
</template>
<script>
import { mapGetters, mapActions } from "vuex";
import { accountCancel } from "@/api/home";
import EsPayPassword from "@/components/payPassword";
export default {
  name: "account-cancellation",
  props: {
    show: {
      type: Boolean,
      default: false,
    },
    payCallback: {
      type: Function,
      default: null,
    },
    payLoading: {
      type: Boolean,
      default: false,
    },
  },
  model: {
    prop: "show",
    event: "update",
  },
  components: {
    EsPayPassword,
  },
  data() {
    return {
      accout: "1",
      logoutReason: "",
      centerDialogVisible: false,
      passwordDialog: false,
      password: "",
      // 0 支付界面 1 设置支付密码 2 确认支付密码
      showModel: 0,
      firstPaw: 0,
      secondPaw: 0,
      fouce: false,
    };
  },
  computed: {
    ...mapGetters(["userInfo"]),
    ...mapGetters("user", ["userBalance"]),
  },
  async mounted() {
    await this.requestGetUserBalanceList();
    this.accout = this.userInfo.username;
  },
  methods: {
    ...mapActions("user", ["requestGetUserBalanceList"]),
     ...mapActions({
      logout: "logout",
    }),
    goBack() {
      this.$router.push("/userInfo/setup");
    },
    confirmEvent() {
      if (this.userBalance) {
        this.$message({
          message: this.$t("message.home.您还有余额,不能注销账号"),
          type: "warning",
        });
      } else if (!this.logoutReason.trim()) {
        this.$message({
          message: this.$t("message.home.请输入注销理由"),
          type: "warning",
        });
      } else {
        this.centerDialogVisible = true;
      }
    },
    openPass() {
      // console.log('this.userInfo ->', this.userInfo);
      if (this.userInfo.safeword) {
        console.log('this.$refs.passwordRef ->',this.$refs['passwordRef'] );
        this.centerDialogVisible = false;
        this.passwordDialog = true;

      this.$refs.passwordRef.clear();
      } else {
        this.suerCancel();
      }
    },

    async suerCancel() {
      if (this.passwordDialog) {
        this.passwordDialog = false;
        this.$refs.passwordRef.clear();
        
      }
      const res = await accountCancel({
        token: sessionStorage.getItem("ES_TOKEN"),
        account: this.accout,
        reason: this.logoutReason,
        cashPassword: this.password ? this.password : "",
      });
      
        if(res.code == '0'){
          this.centerDialogVisible = false
          localStorage.setItem("ES_MESSAGE_LAST_ID", "");
          this.$message({
            message: this.$t("message.home.注销成功"),
            type: "success",
          });
          
          
          this.logout();
          this.$router.push("/");

        } 
      // this.$message({
      //   message: this.$t("message.home.注销成功"),
      //   type: "success",
      // });
      this.centerDialogVisible = false
    },
    pay() {
      this.suerCancel();
    },
    output({ data, isfinished }) {
      this.fouce = true;
      if (isfinished) {
        if (this.showModel === 1) {
          this.firstPaw = data;
        } else if (this.showModel === 2) {
          this.secondPaw = data;
        } else if (this.showModel === 0) {
          this.password = data;
        }
      }
    },
  },
};
</script>
<style lang="scss" scoped>
.transaction-password {
  width: 422px;
}
.log-container {
  margin-top: 28px;
  margin-left: 10px;
  .tit-log {
    margin-top: 12px;
    line-height: 40px;
    font-size: 14px;
  }
}
</style>
