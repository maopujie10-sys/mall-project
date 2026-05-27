<template>
  <div class="money_pacakge_contaner" v-loading="loading">
    <div class="top">
      <div class="tit">
        {{ $t("message.home.accountReview") /** 账户总览 */ }}
      </div>
      <div class="content">
        <div style="display: flex; flex-direction: row">
          <div class="package_icon">
            <span class="iconfont icon-qianbao qb"></span>
          </div>
          <div
            style="
              display: flex;
              flex-direction: column;
              justify-content: center;
            "
          >
            <div
              style="display: flex; flex-direction: row; align-items: center"
            >
              <span
                class="blance-num"
                >{{ showBalance ? numberFormat(userBalance) : "*******" }}
              </span>
              <img
                @click="isOpen()"
                style="width: 20px; height: 14px; cursor: pointer"
                :src="
                  require(`@/assets/image/eye-${
                    showBalance ? 'open' : 'close'
                  }.png`)
                "
              />
            </div>
            <div style="font-weight: 400; font-size: 14px; margin-top: 10px">
              {{
                $t("message.home.accountBalance")
                /**账户余额*/
              }}
              (USDT)
            </div>
          </div>
        </div>

        <div class="fl_row">
          <el-button
            @click="(e) => handelTo(e, 'recharge')"
            class="button"
            type="primary"
          >
            {{ itemname == 'Hive'? $t("message.home.加值") : $t("message.home.recharge")}}
          </el-button>
          <el-button
            @click="(e) => handelTo(e, 'withdraw')"
            class="button"
            type="primary"
            plain
          >
            {{ itemname == 'Hive' ?$t("message.home.提领") : $t('message.home.withdraw') }}
          </el-button>
        </div>
      </div>
    </div>

    <div class="fl_col">
      <span>{{ $t("message.home.walletHistory") }}</span>
      <div class="fl_row" style="margin-top: 10px">
        <el-button
          @click="() => (pageInfo.type = 1)"
          class="h_button"
          :type="pageInfo.type == 1 ? 'primary' : 'info'"
          :plain="pageInfo.type == 2"
        >
         {{ itemname == 'Hive'? $t("message.home.加值") : $t("message.home.recharge")}}
        </el-button>
        <el-button
          @click="() => (pageInfo.type = 2)"
          class="h_button"
          :type="pageInfo.type == 2 ? 'primary' : 'info'"
          :plain="pageInfo.type == 1"
        >
           {{ itemname == 'Hive' ?$t("message.home.提领") : $t('message.home.withdraw') }}
        </el-button>
      </div>

      <div class="table_style">
        <el-table
          :data="tableData.elements || []"
          :header-cell-style="{ fontSize: '12px', color: '#333333' }"
        >
          <el-table-column
            prop="createTime"
            :label="$t('message.home.date')"
            align="center"
            width="130"
          >
            <template slot-scope="scope">
              <SpanTenPix :text="$formatZoneDate(scope.row.createTime)" />
            </template>
          </el-table-column>
          <el-table-column
            prop="order_no"
            :label="$t('message.home.serialNumber')"
            align="center"
            width="118"
          >
            <template slot-scope="scope">
              <SpanTenPix :text="scope.row.order_no" />
            </template>
          </el-table-column>
          <el-table-column
            prop="volume"
            align="center"
            :label="
              pageInfo.type == 1
                ?  $t('message.home.rechargeNum')
                : $t('message.home.withdrawNum')
            "
          >
            <template slot-scope="scope">
              <SpanTenPix :text="(scope.row.volume)"></SpanTenPix>
            </template>
          </el-table-column>
          <el-table-column
            prop="coin"
            align="center"
            :label="$t('message.home.coinBlock')"
          >
            <template slot-scope="scope">
              <SpanTenPix
                :text="
                  `${scope.row.coin}` +
                  (pageInfo.type == 1 && !scope.row.isThirdParty ? `-${scope.row.blockchain_name}` : '')
                "
              >
              </SpanTenPix>
            </template>
          </el-table-column>
          <el-table-column
            prop="state"
            align="center"
            :label="$t('message.home.moneyOrderStatus')"
          >
            <template slot-scope="scope">
              <SpanTenPix
                v-if="scope.row.state == 0"
                style="color: var(--color-main)"
                :text="$t('message.home.dealing')"
              >
              </SpanTenPix>
              <SpanTenPix
                v-if="scope.row.state == 1"
                style="color: #30c218"
                :text="$t('message.home.dealSuccess')"
              >
              </SpanTenPix>
              <SpanTenPix
                v-if="scope.row.state == 2"
                style="color: #c21818"
                :text="$t('message.home.dealFail')"
              >
              </SpanTenPix>
            </template>
          </el-table-column>
          <el-table-column
            prop="address"
            align="center"
            width="110"
            :label="
              pageInfo.type == 1
                ? $t('message.home.payCertificate')
                : $t('message.home.handleFee')
            "
          >
            <template slot-scope="scope">
              <SpanTenPix
                :style="!scope.row.isThirdParty ?'color: blue; cursor: pointer':''"
                v-if="pageInfo.type == 1"
                @click.native=" !scope.row.isThirdParty ? handlePreview(scope.row.img) :''"
                :text="pageInfo.type == 1 && !scope.row.isThirdParty ? $t('message.home.view') : '--'"
              ></SpanTenPix>
              <!-- </el-button> -->
              <SpanTenPix
                v-if="pageInfo.type == 2"
                :text="numberFormat(scope.row.fee)"
              />
            </template>
          </el-table-column>
          <el-table-column
            prop="amount"
            align="center"
            :label="$t('message.home.ActualLedger')"
          >
            <template slot-scope="scope">
              <SpanTenPix
                :text="scope.row.amount !== '0.00' && scope.row.state != 0 ? numberFormat(scope.row.amount) :'--'"
              ></SpanTenPix>
            </template>
          </el-table-column>
          <el-table-column
            prop="address"
            align="center"
            :label="
              pageInfo.type == 1
                ? $t('message.home.rechargeAddress')
                : $t('message.home.receivedAddress')
            "
            width="210"
          >
            <template slot-scope="scope">
              <SpanTenPix
                v-if="pageInfo.type == 1 && !scope.row.isThirdParty"
                :text="scope.row.channel_address || '--'
                "
              >
              </SpanTenPix>
              <!-- scope.row.to -->
              <SpanTenPix
                v-else-if="pageInfo.type !== 1 "
                :text="scope.row.to || '--'
                "
              >
              </SpanTenPix>
              <el-tooltip class="item" :disabled='!scope.row.payUrl' v-else-if="pageInfo.type == 1 && scope.row.isThirdParty " effect="light" :content="scope.row.payUrl?$t('message.home.点击去支付'):''" placement="bottom" @click.native="scope.row.payUrl?goPay(scope.row.payUrl):''">
              <SpanTenPix
                :style="scope.row.payUrl?'color: blue; cursor: pointer; width: 400px':''"
                :text="scope.row.payUrl || '--'"
              >
              </SpanTenPix>
              </el-tooltip>
              <SpanTenPix
                v-else
                text="--"
              >
              </SpanTenPix>
            </template>
          </el-table-column>
           <el-table-column
            prop="address"
            align="center"
            :label="$t('message.home.备注')"
            width="200"
          >
          
           <template slot-scope="scope">
             <el-tooltip class="item" effect="dark" :content="scope.row.failure_msg" placement="top" v-if="scope.row.failure_msg">
              <SpanTenPix
                :text="scope.row.failure_msg 
                "
              >
              </SpanTenPix>
              </el-tooltip>
              <SpanTenPix
                v-else
                text="-- 
                "
              >
              </SpanTenPix>
           </template>
           
           </el-table-column>
        </el-table>
      </div>
      <div
        style="
          margin-top: 45px;
          display: flex;
          width: 100%;
          justify-content: center;
        "
      >
        <el-pagination
          background
          layout="prev, pager,next"
          class="es-pagination"
          :page-size="totlePageSize"
          :pager-count="5"
          :current-page="currentPage"
          :total="total"
          @current-change="changePage"
        />
      </div>
    </div>
    <el-dialog
      class="es-dialog"
      :visible.sync="passwordDialog"
      :center="true"
      :append-to-body="true"
      width="475px"
    >
      <div slot="title" class="dialog-title">
        <span v-if="showModel === 0">{{ $t("message.home.desc3") }}</span>
        <span v-if="showModel === 1">{{ $t("message.home.setUpPayPaw") }}</span>
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
            @click="setUpPaw"
            v-if="showModel === 1"
          >
            {{ $t("message.home.confirmPassword") }}
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
              {{ $t("message.home.confirmPassword") }}
            </el-button>
          </div>
        </div>
      </div>
    </el-dialog>
    <el-dialog :visible.sync="preViewDialog">
      <img width="100%" :src="preViewUrl" alt="" />
    </el-dialog>
  </div>
</template>

<script>
import { mapActions, mapGetters } from "vuex";
import { numberFormat } from "@/util";
import SpanTenPix from "./widget/SpanTenPix.vue";
import EsPayPassword from "@/components/payPassword";
export default {
  components: {
    SpanTenPix,
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
      showBalance: false,
      // tableData: [],
      pageInfo: {
        type: 1,
        pageNum: 1,
        page_size: 8,
      },
      loading: true,
      preViewDialog: false,
      preViewUrl: "",
      // totlePageSize: rechargeRecordList.pageSize,
      passwordDialog: false,
      password: "",
      // 0 支付界面 1 设置支付密码 2 确认支付密码
      showModel: 0,
      itemname: process.env.VUE_APP_ITEM_NAME,
    };
  },
  watch: {},
  computed: {
    ...mapGetters("user", ["userBalance"]),
    ...mapGetters("recharge", ["rechargeRecordList"]),
    ...mapGetters("withdraw", ["withdrawRecordList"]),
    ...mapGetters({ userInfo: "userInfo" }),
    tableData() {
      if (this.pageInfo.type == 1) {
        console.log('this.rechargeRecordList ->', this.rechargeRecordList);
        return this.rechargeRecordList;
      } else {
        return this.withdrawRecordList;
      }
    },
    totlePageSize() {
      if (this.pageInfo.type == 1) {
        return this.rechargeRecordList.pageSize;
      } else {
        return this.withdrawRecordList.pageSize;
      }
    },
    currentPage() {
      if (this.pageInfo.type == 1) {
        return this.rechargeRecordList.thisPageNumber;
      } else {
        return this.withdrawRecordList.thisPageNumber;
      }
    },
    total() {
      if (this.pageInfo.type == 1) {
        return this.rechargeRecordList.totalElements;
      } else {
        return this.withdrawRecordList.thisPageNumber;
      }
    },
  },
  async mounted() {
    this.showBalance =
      localStorage.getItem("showBalance") == "false" ? false : true;
    try {
      await Promise.all([
        this.requestGetUserBalanceList(),
        this.requestRechargeRecordList({ page_size: 8 }),
        this.requestwithdrawRecordList({ page_size: 8 }),
      ]);
    } finally {
      this.loading = false;
    }
  },
  watch:{
    $route: async function (to, from) {
      console.log('to ->', to);
      if(to.path == '/userInfo/money-package'){
        try {
        await Promise.all([
          this.requestRechargeRecordList({ page_size: 8 }),
          this.requestwithdrawRecordList({ page_size: 8 }),
        ]);
    } finally {
      this.loading = false;
    }
      }
    }
  }, 
  methods: {
    ...mapActions("user", ["requestGetUserBalanceList"]),
    ...mapActions("recharge", ["requestRechargeRecordList"]),
    ...mapActions("withdraw", ["requestwithdrawRecordList"]),
    ...mapActions({ setSafewordFunc: "order/setSafewordFunc" }),
    isOpen() {
      this.showBalance = !this.showBalance;
      localStorage.setItem("showBalance", this.showBalance);
    },
    numberFormat,
    handelTo(e, type) {
      e.target.blur();
      this.typec = type;
      // console.log("this.typec ->", this.typec);
      // console.log("this.userInfo ->", this.userInfo);
      if (!this.userInfo.safeword) {
        // 设置支付密码
        console.log("1 ->", 1);
        this.passwordDialog = true;
        this.showModel = 1;
        return;
      }
      this.$router.push({ name: `money-package-${type}` });
    },
    goPay(url){
      window.open(url, '_blank');
    },
    previous() {
      this.showModel = 1;
      // this.$emit('changeShowModel', 1)
      this.$refs.passwordRef.clear();
    },
    setUpPaw() {
      // 设置支付密码
      // this.$emit('changeShowModel', 2)
      this.showModel = 2;
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
        // this.showModel = 0;
        location.reload();
        this.$message.success(this.$t("message.home.setSuccess"));
      } finally {
        this.passwordDialog = false;
        this.$refs.passwordRef.clear();
      }
    },
    changePage(pageNum) {
      if (this.pageInfo.type == 1) {
        this.requestRechargeRecordList({ page_no: pageNum, page_size: 8 });
      } else {
        this.requestwithdrawRecordList({ page_no: pageNum, page_size: 8 });
      }
      // console.log(pageNum)
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
    handlePreview(url) {
      this.preViewDialog = true;
      this.preViewUrl = url;
    },
  },
};
</script>

<style scoped lang="scss">
html[dir="rtl"] {
  .money_pacakge_contaner {
    .top .content .package_icon{
      margin-right: 0;
      margin-left: 17px;
    }
    .blance-num{
      margin-left: 14px;
      margin-right: 0;
    }
    .el-button+.el-button{
      margin-right: 10px;
    }
  }
  
}
/deep/.el-table--scrollable-y ::-webkit-scrollbar {
  display: none;
}

/deep/ .el-table .cell {
  // padding: 10px 0 10px 0px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.qb{
  font-size: 32px;
  color: var(--color-main);
}
.money_pacakge_contaner {
  display: flex;
  flex-direction: column;
  .blance-num{
    font-weight: 700; font-size: 24px; margin-right: 14px
  }
  .fl_row {
    display: flex;
    flex-direction: row;
  }

  .fl_col {
    display: flex;
    flex-direction: column;
    padding-top: 24px;
    padding-left: 34px;
  }

  .h_button {
    height: 30px;
    // width: 93px;
    display: flex;
    justify-content: center;
    align-items: center;

    .info {
      background: #eeeeee;
      border: none;
    }
  }

  .table_style {
    width: 863px;
    height: 445px;
    border: 1px solid #eeeeee;
    border-radius: 4px;
    margin-top: 20px;
  }

  .top {
    display: flex;
    flex-direction: column;
    width: 863px;
    height: 168px;
    border-bottom: 1px solid #eeeeee;
    padding-top: 8px;
    padding-left: 34px;

    .tit {
      font-weight: 500;
      font-size: 14px;
    }

    .content {
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      align-items: center;
      margin-top: 50px;

      .button {
        width: 127px;
        height: 34px;
        display: flex;
        justify-content: center;
        align-items: center;
      }

      .package_icon {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 56px;
        height: 56px;
        border-radius: 28px;
        border: 1px solid var(--color-main);
        background: linear-gradient(0deg, #fff7ec, #fff7ec), #eeeeee;
        margin-right: 17px;
      }
    }
  }
}
</style>
