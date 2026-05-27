<template>
  <div class="withdraw">
    <div class="box-btn" @click="goWithdraw">
      <div class="tit" v-if="itemname == 'Hive'">{{ $t("message.home.提领" /**提现 */) }}</div>
      <div class="tit" v-else>{{ $t("message.home.withdraw" /**提现 */) }}</div>
      <img
        class="icon"
        src="@/assets/image/icon-arrow-down.svg"
        alt="withdraw"
      />
    </div>
    <div class="collection" v-loading="addAddressLoading">
      <div class="tit">
        {{ $t("message.home.defaultAddress" /** 默认地址*/) }}
      </div>
      <div v-if="addressList.length" class="add_list">
        <div class="item" v-for="item in addressList" :key="item.id">
          <div class="info">
            <div class="name-and-mobile">
              <span class="name">{{ item.contacts }}</span>
              <span class="mobile">&nbsp;&nbsp;+{{ item.phone }}</span>
            </div>
            <el-switch
              :value="item.use"
              :active-value="1"
              :inactive-value="0"
              @change="setAddressDefalut($event, item)"
            />
          </div>
          <!--  -->
          <div class="address">
            {{ item.country }} {{ item.province }} {{ item.city }}
            {{ item.address }}
          </div>
        </div>
      </div>
      <el-empty v-else :description="$t('message.home.noData')"></el-empty>
    </div>

    <div class="add-btn flex-center" @click="addAdressDialogVisible = true">
      <span>+ {{ $t("message.home.addNewAddress" /** 新增地址*/) }}</span>
    </div>

    <withdrawDialog v-model="dialogVisible" />
    <!-- <WithdrawMethodsDiglog
      v-model="rechargeMethodDialogVisible"
      @select-currency="updateCurrency"
    /> -->
    <EsAddressDialog v-model="addAdressDialogVisible" />
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
import { mapActions, mapGetters } from "vuex";
import WithdrawDialog from "@/page/userInfo/dashboard/withdraw/withdraw-dialog";
import EsAddressDialog from "@/components/addAddress";
import EsPayPassword from "@/components/payPassword";
// import WithdrawMethodsDiglog from '@/page/userInfo/dashboard/recharge/recharge-method-dialog'
export default {
  components: { WithdrawDialog, EsAddressDialog ,EsPayPassword},
  data() {
    return {
      rechargeMethodDialogVisible: false,
      dialogVisible: false,
      addAdressDialogVisible: false,
      addAddressLoading: false,
      currentCoin: "",
      passwordDialog: false,
      password: "",
      // 0 支付界面 1 设置支付密码 2 确认支付密码
      showModel: 0,
      itemname: process.env.VUE_APP_ITEM_NAME,
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
  computed: {
    ...mapGetters("user", ["addressList"]),
     ...mapGetters({ userInfo: "userInfo" }),
  },
  mounted() {
    this.requestAddressList();
  },
  methods: {
    ...mapActions("user", [
      "requestAddressList",
      "requestAddressEdit",
      "requestAddressAdd",
      "requestAddressDel",
    ]),
     ...mapActions({ setSafewordFunc: "order/setSafewordFunc" }),
    handleClose() {
      console.log("111 ::=> ", 111);
      this.dialogVisible = false;
    },
    async setAddressDefalut(value, item) {
      try {
        this.addAddressLoading = true;
        await this.requestAddressEdit({
          ...item,
          ...{ use: value },
        });
      } finally {
        this.addAddressLoading = false;
      }
    },
    goWithdraw() {
      if (!this.userInfo.safeword) {
        // 设置支付密码
        this.passwordDialog = true;
        this.showModel = 1;
        this.$refs.passwordRef.clear();
        return;
      }
      this.$router.push("/userInfo/money-package/withdraw");
      this.$store.state.user.currentIndex = 1;
    },
    // updateCurrency(currency) {
    //   this.dialogVisible = true
    //   this.currentCoin = currency
    // },
     previous() {
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
      console.log("222 ->", 222);
      try {
        await this.setSafewordFunc({
          safeword,
          re_safeword,
        });
        // this.showModel = 0;
        this.$message.success(this.$t("message.home.setSuccess"));
        this.$router.push("/userInfo/money-package/withdraw?index=1");
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
  .withdraw{
    margin-right: 52px;
    margin-left: 0;
  }
}
.withdraw {
  margin-left: 52px;
  display: flex;
  flex-direction: column;

  .collection {
    margin-top: 20px;
    // flex: 1;
    width: 249px;
    border: 1px solid var(--color-border);
    border-radius: 4px;
    position: relative;

    > .tit {
      height: 50px;
      line-height: 50px;
      padding: 0 13px;
      border-bottom: 1px solid var(--color-border);
      display: flex;
      align-items: center;
      font-weight: 500;
      color: var(--color-title);
    }

    > .add_list {
      > .item {
        padding: 10px;
        font-size: 12px;

        + .item {
          border-top: 1px solid var(--color-border);
        }

        > img {
          width: 60px;
          height: 60px;
        }

        > .info {
          display: flex;

          .name-and-mobile {
            flex: 1;
            font-weight: 400;
            color: var(--color-title);
            span {
              display: inline-block;
            }
            .name {
              max-width: 70px;
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }
            .mobile {
              max-width: 70px;
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }
          }
        }

        > .address {
          color: var(--color-subtitle);
          font-weight: 500;
          margin-top: 5px;
          width: 100%;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }
    }
  }

  .add-btn {
    background-color: var(--color-little-grey);
    height: 85px;
    border: 1px solid var(--color-border);
    border-radius: 4px;
    margin-top: 20px;
    cursor: pointer;
    span {
      font-weight: 400;
      font-size: 18px;
      color: var(--color-main);
    }
    &:hover {
      background-color: var(--color-submain1);
    }
  }
}
</style>
