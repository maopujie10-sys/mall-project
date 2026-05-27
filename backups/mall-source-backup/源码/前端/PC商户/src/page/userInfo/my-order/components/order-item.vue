<template>
  <div class="oder_item_container">
    <div class="left">
      <div class="item">
        <span
          >{{ $t("message.home.serialNumber") }}: {{ data.id }}
          <i
            @click="copy"
            style="cursor: pointer"
            class="el-icon-copy-document"
        /></span>
        <span class="statusText">{{ getOrderStatusLable(data.status) }}</span>
      </div>
      <div class="item">
        <span>{{ $t("message.home.Information") }}：</span>
        <div class="info">
          <span> {{ data.goodsCount }}{{ $t("message.home.Item") }} </span>
          <span> {{ $t("message.home.From") }} {{ data.goodsFrom }} </span>
        </div>
      </div>
      <div class="item">
        <span>{{ $t("message.home.amount") }}</span>
        <span class="amount">
          ${{ numberFormat(data.priceCount + data.fees + data.tax) }}
        </span>
      </div>
    </div>
    <div class="divider" />
    <div class="right">
      <div
        @click="button.func"
        v-for="button in getStatusButtons(data.status)"
        :key="button.key"
        class="button"
        :class="[button.activity ? 'active' : '']"
      >
        {{ button.text }}
      </div>
    </div>
    <div
      v-if="data.status == 6"
      :class="data.returnStatus == 3 ? 'fail return_button' : 'return_button'"
    >
      {{ returnStatusText[data.returnStatus] }}
    </div>
    <!-- 查看物流 -->
    <order-logistics-dialog
      v-model="logisticsDialogVisible"
      :currentOrderInfo="currentOrderInfo"
      :refresh="refresh"
    />
    <order-payment-dialog
      @closePay="closePayDialog"
      v-model="paymentDialogVisible"
      :currentOrderInfo="currentOrderInfo"
      :refresh="refresh"
    />
    <!-- 取消订单 -->
    <order-cancel-dialog
      v-model="cancelDialogVisible"
      :currentOrderInfo="currentOrderInfo"
      :refresh="refresh"
    />
  </div>
</template>
<script>
  import { numberFormat } from "@/util";
  import { getOrderStatusLable } from "@/util/shop";
  import ordermix from "../ordermix";
  export default {
    props: {
      data: {
        type: Object,
        default: () => {},
      },
      refresh: {
        type: Function,
        default: () => {},
      },
    },
    mixins: [ordermix],
    data() {
      return {
        currentOrderInfo: this.data,
        returnStatusText: {
          1: this.$t("message.home.order.refunding"),
          2: this.$t("message.home.order.refundSuccess"),
          3: this.$t("message.home.order.refundFail"),
        },
      };
    },
    methods: {
      getStatusButtons(number) {
        switch (number) {
          case -1:
            return [this.queryButton];
          case 0:
            return [this.queryButton, this.payButton, this.cancelButton];
          case 1:
          case 2:
            return [
              this.queryButton,
              this.sendInfoButton,
              this.returnPayButton,
            ];
          case 3:
            return [
              this.queryButton,
              this.confirmButton,
              this.queryLogisticsButton,
              this.returnPayButton,
            ];
          case 4:
            return [
              this.queryButton,
              this.evaluateButton,
              this.queryLogisticsButton,
            ];
          case 5:
            return [this.queryButton, this.queryLogisticsButton];
          case 6:
            return [this.queryButton, this.queryLogisticsButton];
        }
      },
    },
  };
</script>

<style lang="scss" scoped>
  .oder_item_container {
    display: flex;
    flex-direction: row;
    border: 1px solid #eeeeee;
    border-radius: 4px;
    margin-top: 17px;
    width: 872px;
    align-items: center;
    padding: 13px;
    position: relative;

    .divider {
      border-left: 1px solid #eeeeee;
      height: 92px;
      margin-right: 50px;
      margin-left: 50px;
    }

    .return_button {
      display: flex;
      flex-direction: row;
      justify-content: center;
      align-items: center;
      // width: 82px;
      padding: 0px 10px 0px 10px;
      height: 26px;
      position: absolute;
      right: 0;
      top: 0;
      color: white;
      background: #30c218;
      font-size: 12px;
      border-radius: 0px 4px 0px 0px;
    }
    .fail {
      background-color: red !important;
    }
    .left {
      display: flex;
      flex-direction: column;

      width: 100%;
      font-weight: 400;
      font-size: 12px;

      .item {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        margin-top: 20px;

        .statusText {
          color: #c21818;
        }

        .info {
          display: flex;
          flex-direction: column;
          align-items: flex-end;
        }

        .amount {
          font-family: "Roboto";
          font-style: normal;
          font-weight: 500;
          font-size: 16px;
          line-height: 19px;
          color: var(--color-price);
        }
      }
    }

    .right {
      width: 407px;
      display: flex;
      flex-direction: row;
      flex-wrap: wrap;
      position: relative;
      // justify-content: center;
    }

    .button {
      display: flex;
      justify-content: center;
      align-items: center;
      padding-left: 20px;
      padding-right: 20px;
      height: 28px;
      border: 1px solid #8c8c8c;
      border-radius: 14px;
      color: #333333;
      margin-right: 13px;
      cursor: pointer;
      margin-top: 13px;
      overflow:hidden; //超出的文本隐藏
      text-overflow:ellipsis; //溢出用省略号显示
      white-space:nowrap; //溢出不换行
      &.active {
        color: var(--color-main);
        border: 1px solid var(--color-main);
        background: linear-gradient(0deg, #fff7ec, #fff7ec), #eeeeee;
      }
    }
  }
</style>
