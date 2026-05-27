<template>
  <el-dialog
    custom-class="detail-dialog"
    :title="$t('message.home.orderDetails')"
    :visible.sync="dialogVisible"
  >
    <div class="order-item" v-loading="loading">
      <div class="option-list">
        <div class="option-item">
          <div class="label">{{ $t("message.home.serialNumber") }}：</div>
          <div class="value">
            <p>{{ orderDetails.id }}</p>
            <p class="tips">{{ orderDetails.createTime }}</p>
          </div>
        </div>
        <!-- <div class="option-item">
          <div class="label">{{ $t("message.home.orderName") }}：</div>
          <div class="value">{{ orderDetails.contacts }}</div>
        </div> -->
        <!-- <div class="option-item">
          <div class="label">{{ $t("message.home.orderEmail") }}：</div>
          <div class="value">{{ orderDetails.email || "--" }}</div>
        </div> -->
        <div class="option-item">
          <div class="label">{{ $t("message.home.orderAddress") }}：</div>
          <div class="value">
            <p>
              {{ orderDetails.postcode }} {{ orderDetails.province }}
              {{ orderDetails.city }}
            </p>
            <p>{{ orderDetails.country }}</p>
            <p>{{ orderDetails.address }}</p>
            <p>{{ orderDetails.contacts }}</p>
            <p>
              {{
                orderDetails.phone?.indexOf("|") > -1
                  ? orderDetails.phone.split("|")[1]
                  : orderDetails.phone
              }}
            </p>
          </div>
        </div>
        <div class="option-item">
          <div class="label">{{ $t("message.home.orderAmount") }}：</div>
          <div class="value">
            <span class="price">{{ orderDetails.goodsCount ?? '-' }}</span>
          </div>
        </div>
        <div class="option-item">
          <div class="label">{{ $t("message.home.orderPrefix") }}：</div>
          <div class="value">
            <span class="price">{{ numberFormatFn(getOrderPrefix) }}</span>
          </div>
        </div>
        
    
        <div class="option-item block">
          <!-- <div class="label">{{ $t("message.home.orderCommodity")  }}：</div> -->
          <div class="value" v-for="item in orderGoods" :key="item.id">
            <div class="product-item">
              <img :src="item.goodsIcon" alt="order-detail-product" />
              <span class="title">
                {{ item.goodsName }}
              </span>
            </div>
            <div class="option-item">
              <div class="label">{{ $t("message.home.orderQuantity") }}：</div>
              <div class="value">
                <span>{{ item.goodsNum }}</span>
              </div>
            </div>
            <div class="option-item">
              <div class="label">{{ $t("message.home.orderTime") }}：</div>
              <div class="value">
                <span>{{ orderDetails.createTime }}</span>
              </div>
            </div>
            <div class="option-item">
              <div class="label">{{ $t("message.home.orderUnitprice") }}：</div>
              <div class="value">
                <span class="price">${{ numberFormatFn(item.goodsReal) }}</span>
              </div>
            </div>
            <div class="option-item">
              <div class="label">{{ $t("message.home.orderFreight") }}：</div>
              <div class="value">
                <span class="price">${{ numberFormatFn(item.fees) }}</span>
              </div>
            </div>
            <div class="option-item">
              <div class="label">{{ $t("message.home.orderTax") }}：</div>
              <div class="value">
                <span class="price">${{ numberFormatFn(item.tax) }}</span>
              </div>
            </div>
            <div class="option-item">
              <div class="label">{{ $t("message.home.orderTotal") }}：</div>
              <div class="value">
                <span class="price"
                  >${{ numberFormatFn(item.goodsReal * item.goodsNum) }}</span
                >
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <template slot="footer">
      <el-button v-if="isPay" size="mini" plain @click="handleCancel">
        <!-- 取消支付 -->
        {{ $t("message.home.order.cancel") }}
      </el-button>
      <el-button
        v-if="isPay"
        size="mini"
        plain
        type="primary"
        @click="handlePayment"
      >
        <!-- 立即支付 -->
        {{ $t("message.home.order.payment") }}
      </el-button>

      <el-button
        v-if="isRemind"
        size="mini"
        type="primary"
        :loading="remindLoading"
        plain
        @click="handleRemind"
      >
        {{ $t("message.home.order.remind" /** 提醒发货 */) }}
      </el-button>

      <el-button v-if="isLogistics" size="mini" type="primary" plain @click="handleLogistics">
        {{ $t('message.home.order.logistics' /** 查看物流 */) }}
      </el-button>


      <el-button v-if="isConfirm" size="mini" plain @click="handleReturn">
        {{ $t("message.home.order.return" /** 申请退货 */) }}
      </el-button>

      <el-button
        v-if="isConfirm"
        size="mini"
        :loading="receiptLoading"
        plain
        type="primary"
        @click="handleReceipt"
      >
        {{ $t("message.home.order.confirm" /** 确认收货 */) }}
      </el-button>

      <el-button v-if="isEvaluate" size="mini" plain @click="handleEvaluation">
        {{ $t("message.home.order.evaluate" /** 立即评价 */) }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script>
import { mapActions, mapGetters } from "vuex";
import { numberFormat } from "@/util";
import { accAdd, accTimes } from "@/util/math";
export default {
  name: "order-detail-dialog",
  props: {
    value: {
      type: Boolean,
      default: false,
    },
    currentOrderInfo: {
      type: Object,
      default: () => {},
    },
    remindLoading: {
      type: Boolean,
      default: false,
    },
    receiptLoading: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      dialogVisible: this.value || false,
      loading: false,
    };
  },
  watch: {
    value(val) {
      this.dialogVisible = val;
    },
    dialogVisible(val) {
      console.log(val);
      if (val !== this.value) {
        this.$emit("input", val);
      }
      if (val) this.requestData();
    },
  },
  computed: {
    ...mapGetters({
      orderDetails: "order/orderDetails",
      orderGoods: "order/orderGoods",
    }),
    // 状态（-1=已取消）（0=待付款）（1=待发货）（2=已确认）（3=待收货）（4=已收获）（5=已评价）（6=退款)
    isPay() {
      return this.currentOrderInfo.status === 0;
    },
    isEvaluate() {
      return this.currentOrderInfo.status === 4;
    },
    isRemind() {
      return this.currentOrderInfo.status === 1;
    },
    isConfirm() {
      return this.currentOrderInfo.status === 3;
    },
    isRefundSuccess() {
      return this.currentOrderInfo.status === 6;
    },
    isLogistics() {
      return [3, 4].includes(this.currentOrderInfo.status)
    },
    getOrderPrefix() {
      let total = 0;
      if (Array.isArray(this.orderGoods)) {
        this.orderGoods.forEach((item) => {
          total += accAdd( accTimes(item.goodsReal, item.goodsNum), item.fees, item.tax)
        })
      }
      return total
    }
  },
  methods: {
    ...mapActions({
      requestOrderDetailsList: "order/requestOrderDetailsList",
      requestOrderGoodsList: "order/requestOrderGoodsList",
    }),
    async requestData() {
      try {
        this.loading = true;
        await this.requestOrderDetailsList({
          orderId: this.currentOrderInfo.id,
        });
        await this.requestOrderGoodsList({ orderId: this.currentOrderInfo.id });
        // console.log(' ->', );
      } finally {
        this.loading = false;
      }
    },
    numberFormatFn(num) {
      return numberFormat(num);
    },

    handleCancel() {
      this.$emit("cancel");
    },

    handlePayment() {
      this.$emit("payment");
    },

    handleRemind() {
      this.$emit("remind");
    },

    handleReturn() {
      this.$emit("return");
    },

    handleReceipt() {
      this.$emit('receipt')
    },

    handleEvaluation() {
      this.$emit('evaluation')
    },

    handleLogistics() {
      this.$emit('logistics')
    }
  },
};
</script>

<style lang="scss" scoped>
.block {
  margin: 20px 0;
}

.tips {
  padding-top: 16px;
  font-size: 13px;
  color: #999;
}
</style>
