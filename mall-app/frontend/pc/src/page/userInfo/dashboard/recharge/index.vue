<template>
  <div class="recharge">
    <div class="box-btn" @click="goReacharge">
      <div class="tit" v-if="itemname == 'Hive'">{{ $t("message.home.加值" /** 充值*/) }}</div>
      <div class="tit" v-else>{{ $t("message.home.recharge" /** 充值*/) }}</div>
      <img
        class="icon"
        src="@/assets/image/icon-arrow-down.svg"
        alt="recharge"
      />
    </div>
    <div class="collection">
      <div class="tit">
        {{ $t("message.home.myCommodityCollection" /**商品收藏 */) }}
      </div>
      <div v-if="collectGoodsList.length" class="dash_list">
        <div
          class="item"
          v-for="item in collectGoodsList"
          :key="item.id"
          @click="gotoDetails(item)"
        >
        <div class="discount" v-if="item.discountRatio">
            <span>{{ numberFormatFn(item.discountRatio) * 100 }} %</span>
            <br>
            <span>OFF</span>
          </div>
          <div class="poster">
            <img
              :src="
                item.imgUrl1 || item.imgUrl2 || item.imgUrl3 || item.imgUrl4
              "
              alt="collection-item"
            />
          </div>
          <div class="info">
            <div class="tit">
              {{ item.name || "-" }}
            </div>
            <div class="detail">
              <span class="price"
                >${{
                  numberFormatFn(
                    item.discountPrice
                      ? item.discountPrice
                      : item.sellingPrice
                  )
                }}</span
              >
            </div>
          </div>
        </div>
      </div>
      <el-empty v-else :description="$t('message.home.noData')"></el-empty>
    </div>
    <recharge-method-dialog
      v-model="rechargeMethodDialogVisible"
      @select-currency="updateCurrency"
    />
    <recharge-dialog
      v-model="rechargeDialogVisible"
      :currentCoin="currentCoin"
    />
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
  </div>
</template>

<script>
import RechargeDialog from "@/page/userInfo/dashboard/recharge/recharge-dialog";
import RechargeMethodDialog from "@/page/userInfo/dashboard/recharge/recharge-method-dialog";
import { mapActions, mapGetters } from "vuex";
import { numberFormat } from "@/util";
import EsPayPassword from "@/components/payPassword";
export default {
  components: { RechargeMethodDialog, RechargeDialog, EsPayPassword },
  data() {
    return {
      rechargeMethodDialogVisible: false,
      itemname: process.env.VUE_APP_ITEM_NAME,
      rechargeDialogVisible: false,
      currentCoin: "",
      passwordDialog: false,
      password: "",
      // 0 支付界面 1 设置支付密码 2 确认支付密码
      showModel: 0,
      fouce: false,
      firstPaw: 0,
      secondPaw: 0,
    };
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
  // watch: {
  //   password(val) {
  //     console.log('val ->', val);
  //     if (val) {
        
  //     }
  //   },
  // },
  computed: {
    ...mapGetters({
      collectGoodsList: "user/collectGoodsList",
    }),
    ...mapGetters({ userInfo: "userInfo" }),
  },
  mounted() {
    // console.log("this. ->", this.collectGoodsList);
    this.getDataList();
  },
  methods: {
    numberFormatFn(num) {
      return numberFormat(num);
    },
    ...mapActions({
      requestCollectGoodsList: "user/requestCollectGoodsList",
    }),
    ...mapActions({ setSafewordFunc: "order/setSafewordFunc" }),
    updateCurrency(currency) {
      this.rechargeDialogVisible = true;
      this.currentCoin = currency;
    },
    getDataList() {
      this.requestCollectGoodsList({ pageSize: 8, pageNum: 1 });
    },
    gotoDetails(data) {
      this.$router.push({
        name: "productDetails",
        query: { id: data.id },
      });
    },
    goReacharge() {
      // console.log('222 ->', 222);
      if (!this.userInfo.safeword) {
        // 设置支付密码
        this.passwordDialog = true;
        this.showModel = 1;
        this.$refs.passwordRef.clear();
        // console.log('this.$refs.passwordRef ->', this.$refs.passwordRef);
        return;
      }
      this.$router.push("/userInfo/money-package/recharge");
      this.$store.state.user.currentIndex = 1;
    },
    previous() {
      // if (this.fouce) {
      //     this.$refs.passwordRef.clear();
      // }
      this.showModel = 1;
      // this.$emit('changeShowModel', 1)
      this.$refs.passwordRef.clear();
    },
    setUpPaw() {
      // 设置支付密码
      // this.$emit('changeShowModel', 2)
      const passwordArr = this.$refs.passwordRef.codeData;
      const filterPassword = passwordArr.filter(item => item !== "");
      if(filterPassword.length === 6) {
        this.showModel = 2;
      }else {
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
      // console.log("222 ->", 222);
      try {
        await this.setSafewordFunc({
          safeword,
          re_safeword,
        });
        // this.showModel = 0;
        this.$message.success(this.$t("message.home.setSuccess"));
        this.$router.push("/userInfo/money-package/recharge?index=1");
      } finally {
        this.passwordDialog = false;
        this.$refs.passwordRef.clear();
      }
    },
    output({ data, isfinished }) {
      console.log("data,isfinished ->", data, isfinished);
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
html[dir="rtl"]{
  .recharge {
        margin-right: 52px;
        margin-left: 0;
     .collection > .dash_list > .item > .info{
        padding-left: 0;
        padding-right: 10px;
     }
  }
}
.recharge {
  margin-left: 52px;
  width: 250px;
  display: flex;
  flex-direction: column;

  .collection {
    margin-top: 20px;
    // flex: 1;
    width: 249px;
    border: 1px solid #eeeeee;
    border-radius: 4px;

    > .tit {
      height: 50px;
      line-height: 50px;
      padding: 0 13px;
      border-bottom: 1px solid #eee;
      display: flex;
      align-items: center;
      font-weight: 500;
      color: #333;
    }

    > .dash_list {
      > .item {
        display: flex;
        padding: 10px;
        cursor: pointer;
        position: relative;
        .discount{
            width: 31px;
            height: 32px;
            background: url("../../../../assets/image/discount.png") no-repeat 100%/100%;
            position: absolute;
            top: 0;
            left: 0;
            text-align: center;
            font-size: 11px;
            color: #fff;
            font-weight: 500;
          }
        + .item {
          border-top: 1px solid #eee;
        }
        > .poster {
          width: 60px;
          height: 60px;
          overflow: hidden;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
          > img {
            width: 100%;
            height: auto;
          }
        }

        > .info {
          flex: 1;
          width: 0;
          min-width: 0;
          padding: 3px 0;
          padding-left: 10px;
          display: flex;
          flex-direction: column;

          > .tit {
            width: 100%;
            display: -webkit-box;
            overflow: hidden;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            font-size: 12px;
            line-height: 1.2;
            font-weight: 400;
            color: #333;
          }

          > .detail {
            flex: 1;
            height: 0;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;

            .price {
              color: var(--color-price);
            }

            .num {
              font-size: 12px;
            }
          }
        }
      }
    }
  }
}
</style>
