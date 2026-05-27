<template>
  <div class="settlement">
    <EsHeaderView />
    <div class="settlement-content app-container">
      <h1 class="title">{{ $t("message.home.checkout") }}</h1>
      <h2 class="subtitle">{{ $t("message.home.shippingAddress") }}</h2>
      <div class="settlement-receiver flex-between" @click="selectAddressEvent">
        <div>
          <div class="userinfo">
            <span>
              {{ paySelectAddress.contacts }} +{{ paySelectAddress.phone }}
            </span>
          </div>
          <p class="address">
            {{ paySelectAddress.country }} {{ paySelectAddress.province }}
            {{ paySelectAddress.city }}
            {{ paySelectAddress.address }}
          </p>
        </div>
        <div><i class="el-icon-arrow-right"></i></div>
      </div>
      <EsOrderList />
      <EsOrderSum :checkGoods="chcekData" />
      <EsPayMethod />
      <div class="settlement-pay flex-between">
        <div class="settlement-pay-label">
          {{ $t("message.home.Opt") }}
          <span>{{ checkNum }}</span>
          {{ $t("message.home.piece") }}
        </div>
        <el-button type="primary" @click="pay">
          <span>{{ $t("message.home.subOrder") }}</span>
          <span>${{ checkTotalAmount }}</span>
        </el-button>
      </div>
      <EsIconTips />
    </div>
    <EsFooterView />
    <EsPayModal
      v-model="payModalShow"
      :payCallback="payCallback"
      @changeShowModel="changeShowModel"
    />
    <AddressDialog
      v-model="addAddressModalShow"
      @showAddAddressView="showAddAddressView"
    />
    <!-- <AddAddressDialog :addAddressView="addAddressView" @showAddAddressView="showAddAddressView" /> -->
    <EsAddAddress v-model="addAddressView" />
  </div>
</template>

<script>
import { mapGetters, mapActions, mapMutations } from "vuex";
import EsIconTips from "@/components/iconTips";
import EsOrderSum from "./orderSum.vue";
import EsOrderList from "./orderList.vue";
import EsPayMethod from "./payMethod.vue";
import EsPayModal from "./payModal.vue";
import AddressDialog from "./address";
// import AddAddressDialog from './addAddress'
import { setShopCartLocal, getShopCartLocal } from "@/util/shop";
import { numberFormat } from "@/util";
import EsAddAddress from "@/components/addAddress";

// import { SetSafewordApi } from "@/api";

export default {
  name: "EsSettlement",
  components: {
    EsIconTips,
    EsOrderSum,
    EsOrderList,
    EsPayMethod,
    EsPayModal,
    AddressDialog,
    // AddAddressDialog,
    EsAddAddress,
  },
  data() {
    return {
      payModalShow: false,
      addAddressModalShow: false,
      selectAddress: {},
      currentSubmitOrderIds: [],
      addAddressView: false,
      chcekData: [],
      checkNum: 0,
      lastSubmit: {
        orderIds: "",
        addressId: "",
        orderInfo: {},
      },
    };
  },
  computed: {
    ...mapGetters({
      addressList: "user/addressList",
      defaultAddress: "user/defaultAddress",
      paySelectAddress: "user/paySelectAddress",
      checkProductPay: "shopCart/checkProductPay",
      userBalance: "user/userBalance",
      userInfo: "userInfo",
    }),
    checkCount() {
      return this.checkProductPay.reduce(
        (a, b) => a + b.list.reduce((i, l) => i + l.checkTotal, 0),
        0
      );
    },
    checkTotalAmount() {
      return numberFormat(
        this.getChcekData().reduce(
          (a, b) =>
            a +
            ((b.price || b.discountPrice || b.sellingPrice) +
              (b.goodsTax ?? 0) +
              (b.freightAmount ?? 0)) *
              b.checkTotal,
          0
        )
      );
    },
    isDisabledPayBtn() {
      return (
        this.userBalance <= 0 ||
        this.checkCount <= 0 ||
        this.userBalance < this.checkTotalAmount
      );
    },
    // checkProduct() {
    //     console.log('-----11111111----')
    //     return this.getChcekData();
    // }
  },
  async mounted() {
    await this.requestAddressList();
    this.$nextTick(() => {
      this.updatePaySelectAddress(this.defaultAddress);
    });
  },
  methods: {
    ...mapMutations({
      updatePaySelectAddress: "user/updatePaySelectAddress",
      updateCheckProductPay: "shopCart/updateCheckProductPay",
      updateShopCart: "shopCart/updateShopCart",
    }),
    ...mapActions({
      requestAddressList: "user/requestAddressList",
      requestOrderPay: "order/requestOrderPay",
      setSafewordFunc: "order/setSafewordFunc",
      requestOrderSubmit: "order/requestOrderSubmit",
    }),
    changeShowModel(e) {
      this.showModel = e;
    },
    showAddAddressView(bool) {
      this.addAddressView = !this.addAddressView;
      if (!this.addAddressView) {
        this.requestAddressList();
      }
    },
    getChcekData() {
      let data = [];
      this.checkProductPay.forEach((item) => {
        data = [
          ...data,
          ...item.list.filter(
            (listItem) => item.checkList.indexOf(listItem.Identifier) > -1
          ),
        ];
      });
      this.chcekData = data;
      // console.log("this.checkData ->", this.data);
      this.checkNum = data.length;
      return data;
    },
    async pay() {
      if (!this.paySelectAddress?.id) {
        return this.$message.error(
          this.$t("message.home.ShippingAddressNotSet" /* 未设置收货地址 */)
        );
      }

      const checkData = this.getChcekData();
      // const ids = checkData.map((item) => item.id)
      // console.log(this.paySelectAddress, this.defaultAddress)

      checkData.map((item) => [item.id, item.checkTotal]).join(",");

      const orderInfo = checkData
        .map((item) => [item.id, item.skuid || -1, item.checkTotal])
        .join(",");
      if (!orderInfo) {
        return this.$message.error(
          this.$t("message.home.NoProductSelected" /* 请选择商品 */)
        );
      }
      const addressId = this.paySelectAddress.id;
      if (
        !(
          this.lastSubmit.orderIds &&
          this.lastSubmit.addressId == addressId &&
          this.lastSubmit.orderInfo == orderInfo
        )
      ) {
        const result = await this.requestOrderSubmit({
          orderInfo: orderInfo,
          addressId: addressId,
        });
        this.currentSubmitOrderIds = result.orderList.map(
          (item) => item.orderId
        );
        localStorage.setItem(
          "currentSubmitOrderIds",
          this.currentSubmitOrderIds
        );
        this.lastSubmit = {
          orderInfo,
          orderIds: this.currentSubmitOrderIds,
          addressId,
        };
        // console.log(JSON.stringify(this.lastSubmit))
      } else {
        console.log("-----use last submit----");
      }
      if (!this.userInfo.safeword) {
        // 设置支付密码
        this.payModalShow = true;
        this.showModel = 1;
        return;
      }
      if (!this.checkoutAmount()) {
        console.log(11111222);
        return;
      }
      this.payModalShow = true;
    },
    cleartCheckData(ids) {
      this.checkProductPay.forEach((item) => {
        item.list = item.list.filter((listItem) => !ids.includes(listItem.id));
      });
      this.updateCheckProductPay(
        this.checkProductPay.filter((item) => !!item.list.length)
      );
    },
    selectAddressEvent() {
      this.addAddressModalShow = true;
    },
    async payCallback(password, successCallBack, failCallBack) {
      if (!this.checkoutAmount()) {
        return;
      }
      if (!this.currentSubmitOrderIds.length) {
        this.currentSubmitOrderIds = localStorage.getItem(
          "currentSubmitOrderIds"
        );
      }
      console.log("this.currentSubmitOrderIds ->", this.currentSubmitOrderIds);
      await this.requestOrderPay({
        orderId: this.currentSubmitOrderIds.join(","),
        safeword: password,
      })
        .then(() => {
          // let shopCartData = getShopCartLocal();
          const shopCartData = getShopCartLocal().then(result =>{
            console.log('getShopCartLocal ->', result);
            return result;
          });
          const checkData = this.getChcekData();
          if (shopCartData && shopCartData.length) {
            const checkIds = checkData.map((item) => item.attrTime);
            shopCartData = shopCartData.filter(
              (item) => !checkIds.includes(item.attrTime)
            );
            // console.log('2232323 ->', 2232323);
            // 支付成功后，清除购物车中的订单
            // console.log('shopCartData ->', shopCartData);
            this.getShopCartLocal(shopCartData);
          }
      const list = []
          this.updateShopCart(list)
          successCallBack && successCallBack();
          this.$router.replace("/paySuccess");
        })
        .catch(() => {
          failCallBack && failCallBack();
        })
        .finally(() => {
          localStorage.removeItem("currentSubmitOrderIds");
          this.payModalShow = false;
        });
    },
    checkoutAmount() {
      if (this.isDisabledPayBtn) {
        if (this.checkTotalAmount.at(0) == "0") {
          this.$message({
            message: this.$t(
              "message.home.NoProductSelected" /**还未选择商品 */
            ),
            type: "error",
          });
        } else {
          this.$message({
            message: this.$t("message.home.balanceNot" /**余额不足，请充值 */),
            type: "error",
          });
        }
        this.payModalShow = false;
        return false;
      }
      return true;
    },
  },
};
</script>

<style lang="scss">
.settlement {
  &-content {
    .title {
      font-weight: 600;
      font-size: 24px;
      color: var(--color-title);
      margin-bottom: 12px;
    }

    .subtitle {
      font-weight: 600;
      font-size: 20px;
      color: var(--color-title);
      margin-bottom: 15px;
    }
  }

  &-receiver {
    border: 1px solid var(--color-border);
    padding: 16px 20px;
    border-radius: 4px;
    margin-bottom: 12px;
    cursor: pointer;

    .userinfo {
      font-weight: 500;
      font-size: 12px;
      color: var(--color-title);
      margin-bottom: 5px;
    }

    .address {
      display: inline-block;
      font-weight: 500;
      max-width: 1000px !important;
      overflow:hidden; //超出的文本隐藏
      text-overflow:ellipsis; //溢出用省略号显示
      white-space:nowrap; //溢出不换行
      font-size: 12px;
      color: var(--color-subtitle);
    }

    div:first-child {
      flex: 1;
    }

    div:last-child {
      width: 50px;
      text-align: right;
    }
  }

  &-pay {
    border: 1px solid var(--color-border);
    padding: 11px 20px;
    margin: 40px 0;

    &-label {
      font-weight: 500;
      font-size: 12px;
      color: var(--color-title);

      span {
        color: var(--color-main);
      }
    }

    .el-button {
      font-weight: 700;
      font-size: 14px;
      color: var(--color-white);

      span:first-child {
        margin-right: 10px;
      }
    }
  }
}
</style>
