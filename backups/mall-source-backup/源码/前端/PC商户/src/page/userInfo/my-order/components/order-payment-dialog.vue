<template>
  <el-dialog  custom-class="payment-dialog" :title="$t('message.home.pendingPayment')" :visible.sync="dialogVisible">
    <div class="wrap">
      <div class="title">{{ $t('message.home.pendingPayment') }}</div>
      <EsPayMethods :showTitle="false" />
      <div class="action">
        <el-button class="pay-btn" @click="pay">{{ $t('message.home.pay') }}</el-button>
      </div>
    </div>
    <EsPayModal v-model="payModalShow" :payCallback="payCallback" />
  </el-dialog>
</template>

<script>
import { mapActions, mapGetters, mapMutations } from 'vuex';
import EsPayModal from '@/page/settlementPage/payModal';
import EsPayMethods from '@/page/settlementPage/payMethod';
export default {
  name: 'order-payment-dialog',
  components: { EsPayModal, EsPayMethods },
  props: {
    value: {
      type: Boolean,
      default: false,
    },
    currentOrderInfo: {
      type: Object,
      default: () => {},
    },
    refresh: {
      type: Function,
    },
  },
  data() {
    return {
      dialogVisible: this.value || false,
      selected: 'balance',
      payModalShow: false,
    };
  },
  computed: {
    ...mapGetters({
      user: 'user/userBalance',
      orderDetails: 'order/orderDetails',
    }),
  },
  watch: {
    value(val) {
      this.dialogVisible = val;
    },
    dialogVisible(val) {
      if (val !== this.value) {
        this.$emit('input', val);
      }
    },
  },
  methods: {
    ...mapActions({
      requestOrderPay: 'order/requestOrderPay',
      requestOrderDetailsList: 'order/requestOrderDetailsList',
    }),
    ...mapMutations({
      updatePaySelectAddress: 'user/updatePaySelectAddress',
    }),
    async pay() {
      await this.requestOrderDetailsList({
        orderId: this.currentOrderInfo.id,
      });
      this.updatePaySelectAddress({
        contacts: this.orderDetails.contacts,
        phone: this.orderDetails.phone,
        country: this.orderDetails.country,
        province: this.orderDetails.province,
        city: this.orderDetails.city,
        address: this.orderDetails.address,
      });
      this.payModalShow = true;
    },
    async payCallback(password, successCallBack, failCallBack) {
      console.log(password);
      try {
        await this.requestOrderPay({
          orderId: this.currentOrderInfo.id,
          safeword: password,
        })
          .then(() => {
            this.$emit('closePay')
            this.refresh && this.refresh()
            this.refresh && this.refresh();
            successCallBack && successCallBack();
            this.payModalShow = false;
            this.$router.replace('/paySuccess');
          })
          .catch(() => {
            failCallBack && failCallBack();
          });
      } catch (error) {}
    },
  },
};
</script>

<style lang="scss" scoped>
.payment-dialog {
  .wrap {
    width: 450px;
    margin: 0 auto;

    .title {
      font-weight: 500;
      font-size: 16px;
      color: #333333;
      margin-bottom: 20px;
    }

    .tip {
      margin-top: 10px;
      font-size: 12px;

      .time {
        color: var(--color-main);
      }

      .desc {
        margin-left: 5px;
      }
    }

    .pay-methods {
      background: linear-gradient(0deg, #fff7ec, #fff7ec), #eeeeee;
      border-radius: 4px;
      padding: 20px 10px;
      margin-top: 26px;
      border: 1px solid var(--color-main);

      .method-item {
        display: flex;
        align-items: center;
        padding: 10px;
        border-radius: 4px;

        + .method-item {
          margin-top: 5px;
        }

        &:hover {
          background-color: rgba(0, 0, 0, 0.05);
        }

        img {
          height: 16px;
        }

        .name {
          flex: 1;
          margin-left: 10px;
          font-weight: 600;
          font-size: 14px;
          color: #000000;

          .price {
            color: var(--color-main);
            font-weight: 700;
          }
        }

        .selected {
          width: 14px;
          height: 14px;
          background-color: #d9d9d9;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;

          img {
            transition-duration: 0.3s;
            width: 0;
            height: 0;
            position: absolute;
          }

          &.active {
            background-color: var(--color-main);

            img {
              visibility: visible;
              width: 14px;
              height: 14px;
              opacity: 1;
            }
          }
        }
      }
    }

    .action {
      padding: 30px 0;
      display: flex;
      align-items: center;
      justify-content: center;

      .el-button {
        width: 100%;
        height: 50px;
        color: #fff;
        background: var(--color-main);
        border-color: var(--color-main);
        border-radius: 4px;
      }
    }
  }
}
</style>
