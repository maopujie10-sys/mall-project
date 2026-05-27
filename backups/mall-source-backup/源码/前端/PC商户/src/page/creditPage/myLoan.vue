<template>
  <div class="app-container loan">
    <div class="mine">
      <div class="left">
        <div class="title">{{ $t("message.home.myloan") }}</div>
        <div class="money">{{ myloan }}</div>
        <div class="details">
          <div>
            <span>{{ day }}{{ $t("message.home.days") }}</span>
            <p>{{ $t("message.home.loaned") }}</p>
          </div>
          <div>
            <span>{{ Interest }}</span>
            <p>{{ $t("message.home.interest") }}</p>
          </div>
          <div>
            <span>{{ repay }}</span>
            <p>{{ $t("message.home.esRepayment") }}</p>
          </div>
        </div>
      </div>
      <div class="right" v-if="disble">
        <div @click="goPage">
          {{ $t("message.home.applyLoan") }}
        </div>
      </div>
    </div>
    <div class="record-title">{{ $t("message.home.loanHistory") }}</div>
    <div class="record">
      <div v-loading="loading">
        <div class="list" v-for="(item, i) in historyList" :key="i">
          <img src="@/assets/image/record.png" alt="" />
          <div class="item date-box">
            <div class="money">{{ numberFormat(item.applyAmount) }}</div>
            <div class="date">
              {{ $t("message.home.applicantDate") }}:{{
                $formatZoneDate(item.customerSubmitTime)
              }}
            </div>
          </div>
          <div class="item-container">
            <div class="item">
              <span class="date"
                >{{ item.creditPeriod }}{{ $t("message.home.days") }}</span
              >
              <span class="date">{{ $t("message.home.cycle") }}</span>
            </div>
            <div class="item">
              <span class="date">{{ item.creditRate * 100 }}%</span>
              <span class="date">{{ $t("message.home.fixedRate") }}</span>
            </div>
            <div class="status" v-if="item.status == 2">
              {{ $t("message.home.successLoan") }}
            </div>
            <div class="status fail" v-if="item.status == 4">
              {{ $t("message.home.borrow") }}
            </div>
            <div class="status application" v-if="item.status == 1">
              {{ $t("message.home.applicantIn") }}
            </div>
            <div class="status finish" v-if="item.status == 5">
              {{ $t("message.home.repaid") }}
            </div>
            <div class="status overdue" v-if="item.status == 3">
              {{ $t("message.home.overdue") }}
            </div>
            <div
              class="btn"
              v-if="item.status == 2 || item.status == 3"
              @click="Repayment(item.id)"
            >
              {{ $t("message.home.repayment") }}
            </div>
            <div
              class="btn fail-btn"
              v-if="item.status == 4"
              @click="goPage(item.id)"
            >
              {{ $t("message.home.Reapply") }}
            </div>
            <div
              class="default"
              v-if="item.status !== 4 && item.status !== 2 && item.status !== 3"
            >
              --
            </div>
          </div>
        </div>
      </div>
      <div class="common-pagination">
        <el-pagination
          v-if="historyList.length"
          background
          layout="prev, pager, next"
          :page-size="pageSize"
          :current-page="pageNum"
          :total="total"
          @current-change="currentChange"
        />
      </div>
      <el-dialog
        class="es-dialog"
        :visible.sync="dialogVisible"
        width="442px"
        :title="$t('message.home.estirepay')"
      >
        <div>
          <span>{{ $t("message.home.applicant") }}</span>
          <el-input :value="realname" disabled />
          <span>{{ $t("message.home.loanDays") }}</span>
          <el-input :value="alreadyCreditDays" disabled />
          <span>{{ $t("message.home.reAmount") }}</span>
          <el-input :value="numberFormat(estimatePayment)" disabled />
          <span>{{ $t("message.home.rates") }}</span>
          <el-input :value="creditRate + '%'" disabled />
          <span>{{ $t("message.home.accountB") }}</span>
          <el-input :value="numberFormat(accountAmount)" disabled />
          <el-button @click="payContent()">{{
            $t("message.home.repayment")
          }}</el-button>
        </div>
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
          <span v-if="showModel === 1">{{
            $t("message.home.setUpPayPaw")
          }}</span>
          <span v-if="showModel === 2">{{
            $t("message.home.confirmPayPaw")
          }}</span>
        </div>
        <div class="pay-modal-content dialog-content">
          <h2 class="pay-modal-title" v-if="showModel !== 2">
            {{ $t("message.home.desc4") }}
          </h2>
          <h2 class="pay-modal-title" v-if="showModel === 2">
            {{ $t("message.home.desc6") }}
          </h2>
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
              {{ $t("message.home.确认") }}
            </el-button>
            <el-button
              type="primary"
              :loading="payLoading"
              @click="setUpPaw"
              v-if="showModel === 1"
            >
              {{ $t("message.home.确认") }}
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
                {{ $t("message.home.确认") }}
              </el-button>
            </div>
          </div>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import {
  BillCredit,
  CreditHistory,
  BeforePayCredit,
  payCredit,
} from "@/api/credit";
import EsPayPassword from "@/components/payPassword";
import { numberFormat } from "@/util";
import { mapGetters, mapActions } from "vuex";
export default {
  components: {
    EsPayPassword,
  },
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
  data() {
    return {
      historyList: [],
      pageSize: 10,
      pageNum: 1,
      total: 2,
      loading: true,
      dialogVisible: false,
      realname: "",
      creditRate: 0,
      alreadyCreditDays: 0,
      estimatePayment: 0,
      accountAmount: 0,
      passwordDialog: false,
      password: "",
      // 0 支付界面 1 设置支付密码 2 确认支付密码
      showModel: 0,
      myloan: "--",
      day: "--",
      Interest: "--",
      repay: "--",
      disble: false,
      fouce: false,
      firstPaw: 0,
      secondPaw: 0,
    };
  },
  mounted() {
    this.getCreditList();
    this.getCreditHistory(1);
  },
  computed: {
    ...mapGetters({
      userInfo: "userInfo",
    }),
  },
  methods: {
    ...mapActions({
      setSafewordFunc: "order/setSafewordFunc",
    }),
    numberFormat,
    async getCreditList() {
      let res = await BillCredit();
      this.myloan = this.numberFormat(res.data.applyAmount)
        ? this.numberFormat(res.data.applyAmount)
        : "--";
      this.day = res.data.alreadyCreditDays ? res.data.alreadyCreditDays : "--";
      this.Interest = this.numberFormat(res.data.interest)
        ? this.numberFormat(res.data.interest)
        : "--";
      this.repay = this.numberFormat(res.data.estimatePayment)
        ? this.numberFormat(res.data.estimatePayment)
        : "--";
    },
    async getCreditHistory() {
      let res = await CreditHistory({
        pageNo: this.pageNum,
      });
      this.historyList = res.data.elements;
      this.loading = false;
      this.total = res.data.totalElements;
    },
    currentChange(page) {
      this.pageNum = page;
      this.loading = true;
      this.getDicountedList();
    },
    goPage(id) {
      this.$router.push("/credit/application?id=" + id);
    },
    async creditDetail(id) {
      let res = await BeforePayCredit({ pageNo: "1", creditId: id });
      this.realname = res.data.realName;
      this.creditRate = res.data.creditRate * 100;
      this.alreadyCreditDays = res.data.alreadyCreditDays;
      this.estimatePayment = res.data.estimatePayment;
      this.accountAmount = res.data.accountAmount;
    },
    Repayment(id) {
      this.dialogVisible = true;
      this.creditDetail(id);
      this.creditId = id;
    },
    payContent() {
      if (this.fouce) {
        this.$refs.passwordRef.clear();
      }
      if (!this.userInfo.safeword) {
        // 设置支付密码
        this.passwordDialog = true;
        this.showModel = 1;
        return;
      } else {
        this.showModel = 0;
        this.passwordDialog = true;
      }
    },
    previous() {
      this.showModel = 1;
      // this.$emit('changeShowModel', 1)
      this.$refs.passwordRef.clear();
    },
    setUpPaw() {
      // 设置支付密码
      // this.$emit('changeShowModel', 2)
      const passwordArr = this.$refs.passwordRef.codeData;
      const filterPassword = passwordArr.filter((item) => item !== "");
      if (filterPassword.length === 6) {
        this.showModel = 2;
      } else {
        this.$message({
          message: this.$t("message.home.请输入完整的支付密码!"),
          type: "warning",
        });
      }
      this.$refs.passwordRef.clear();
    },
    confirmPayPaw() {
      // 再次确认支付密码
      if (this.firstPaw === this.secondPaw) {
        this.setSafeword(this.firstPaw, this.secondPaw);
      } else {
        this.$message({
          message: this.$t("message.home.twoPawword"),
          type: "warning",
        });
        this.$refs.passwordRef.clear();
      }
    },
    async setSafeword(safeword, re_safeword) {
      try {
        await this.setSafewordFunc({
          safeword,
          re_safeword,
        });
        this.showModel = 0;
        this.$message.success(this.$t("message.home.setSuccess"));
      } catch (error) {}
    },
    async pay() {
      if (this.accountAmount < this.estimatePayment) {
        this.$message({
          message: this.$t("message.home.balanceNot"),
          type: "warning",
        });
      } else {
        this.$refs.passwordRef.clear();
        let res = await payCredit({
          creditId: this.creditId,
          safeword: this.password,
        });

        if (res.code == 1) {
          console.log("222 ->", 222);
          this.$refs.passwordRef.clear();
        }
        if (res.code == 0) {
          this.dialogVisible = false;
          this.$message({
            message: this.$t("message.home.paymentSuccessful"),
            type: "success",
          });
          this.getCreditHistory();
        }
      }
      setTimeout(() => {
        this.passwordDialog = false;
      }, 200);
    },
    output({ data, isfinished }) {
      // console.log("data,isfinished ->", data, isfinished);
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
.loan {
  width: 861px;
  margin: 0 auto;
  .mine {
    width: 100%;
    height: 191px;
    background: linear-gradient(0deg, #fff7ec, #fff7ec), #eeeeee;
    border-radius: 4px;
    padding: 24px 23px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    .left {
      .title {
        font-weight: 600;
        font-size: 20px;
        color: #333;
      }
      .money {
        font-weight: 700;
        font-size: 24px;
        color: var(--color-main);
        margin: 18px 0 28px 0;
      }
      .details {
        width: 345px;
        display: flex;
        justify-content: space-between;
        div {
          display: flex;
          flex-direction: column;
          align-items: center;
          font-size: 14px;
          color: #333333;
          justify-content: space-between;
          height: 46px;
          span {
            margin-bottom: 6px;
          }
        }
      }
    }
    .right {
      width: 127px;
      height: 34px;
      background: var(--color-main);
      border-radius: 5px;
      font-size: 14px;
      text-align: center;
      line-height: 34px;
      color: #ffffff;
      cursor: pointer;
    }
  }
  .record-title {
    font-size: 14px;
    color: #333;
    margin: 28px 0 20px 0;
  }
  .record {
    margin-bottom: 100px;
  }
  .list {
    width: 100%;
    // height: 79px;
    border: 1px solid #efefef;
    border-radius: 4px;
    padding: 28px 23px 10px 28px;
    display: flex;
    align-items: center;
    margin-bottom: 18px;
    img {
      width: 40px;
      height: 40px;
    }
    .item {
      display: flex;
      height: 45px;
      flex-direction: column;
      align-items: center;
      justify-content: space-between;
      // margin-right: 80px;
      .money {
        font-weight: 700;
        font-size: 20px;
        color: #333333;
      }
      .date {
        font-size: 12px;
        color: #999999;
      }
    }
    .item-container {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex: 1;
    }
    .date-box {
      align-items: baseline;
      margin-left: 19px;
      margin-right: 38px;
    }
    .status {
      font-size: 12px;
      width: 52px;
      text-align: center;
      color: #3f80ff;
      // margin-right: 50px;
      // margin-left: 40px;
    }
    .fail {
      color: #e43434;
    }
    .btn {
      width: 127px;
      height: 34px;
      font-weight: 400;
      font-size: 14px;
      text-align: center;
      line-height: 34px;
      color: #ffffff;
      background: var(--color-main);
      border-radius: 5px;
      cursor: pointer;
    }
    .fail-btn {
      background: linear-gradient(0deg, #fff7ec, #fff7ec), #eeeeee;
      border: unset;
      color: var(--color-main);
    }
    .application {
      color: var(--color-main);
    }
    .default {
      width: 127px;
      height: 34px;
      font-weight: 400;
      font-size: 14px;
      text-align: center;
      line-height: 34px;
    }
    .finish {
      color: #2faa59;
    }
    .overdue {
      color: #e43434;
    }
  }
  .es-dialog {
    /deep/ .el-dialog__header {
      height: 56px !important;
      .el-dialog__title {
        text-align: left;
      }
    }
    .el-input {
      margin-top: 14px;
      margin-bottom: 23px;
    }
    .el-button {
      width: 100%;
      background: var(--color-main);
      color: #fff;
      height: 44px;
    }
  }

  .pay-modal-title {
    text-align: left;
    font-weight: 400;
    font-size: 16px;
    color: var(--color-black);
  }

  .pay-modal-content {
    align-items: flex-start !important;

    .el-button {
      width: 100%;
      max-width: 450px;
      height: 50px;
    }

    .pay-modal-btn {
      width: 100%;
      text-align: center;
    }

    .pay-button-view {
      display: flex;
      justify-content: space-between;
    }
  }
}
</style>
