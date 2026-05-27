<template>
  <div class="order-item">
    <div class="option-list">
      <div class="option-item">
        <div class="label">{{ $t('message.home.serialNumber') }}：</div>
        <div class="value">
          <div class="text">
            {{ data.id }}
            <i class="el-icon-copy-document" @click="copy"></i>
          </div>
          <div class="desc">{{ data.createTime }}</div>
        </div>
      </div>
      <div class="option-item">
        <div class="label">{{ $t('message.home.Information') }}：</div>
        <div class="value">
          <div class="text">{{ data.goodsCount }}{{ $t('message.home.Item') }}</div>
          <div class="desc">{{ $t('message.home.From') }} {{ data.goodsFrom }}</div>
        </div>
      </div>
      <div class="option-item">
        <div class="label">{{ $t('message.home.amount') }}：</div>
        <div class="value">
          <span class="price">${{ numberFormatFn(data.priceCount) }}</span>
        </div>
      </div>
      <div class="option-item">
        <div class="label">{{ $t('message.home.Operate') }}：</div>
        <div class="value">
          <span class="detail-link" @click="openDetails">
            {{ $t('message.home.CheckDetails') }}
          </span>
        </div>
      </div>
    </div>
    <div class="actions">
        <el-button v-if="isPay" size="mini" plain @click="cancelOrder">
        {{ $t('message.home.order.cancel' /** 取消订单 */) }}
      </el-button>
       <el-button v-if="isPay" type="primary" size="mini" plain @click="payOrder">
        {{ $t('message.home.order.payment' /** 立即付款 */) }}
      </el-button>

      <el-button v-if="isRemind" size="mini" type="primary" :loading="remindLoading" plain @click="remindOrder">
        {{ $t('message.home.order.remind' /** 提醒发货 */) }}
      </el-button>

      <el-button v-if="isLogistics" size="mini" type="primary" plain @click="logisticsOrder">
        {{ $t('message.home.order.logistics' /** 查看物流 */) }}
      </el-button>

      <el-button v-if="isConfirm" size="mini" plain @click="returnOrder">
        {{ $t('message.home.order.return' /** 申请退货 */) }}
      </el-button>
      <el-button v-if="isConfirm" size="mini" :loading="receiptLoading" plain type="primary" @click="receiptOrder">
        {{ $t('message.home.order.confirm' /** 确认收货 */) }}
      </el-button>

      <el-button v-if="isEvaluate" size="mini" plain @click="evaluationOrder">
        {{ $t('message.home.order.evaluate' /** 立即评价 */) }}
      </el-button>
  
      <div v-if="isRefundSuccess">
        <span class="status unReturn" v-if="!Boolean(data.returnStatus)">{{ $t('message.home.order.noRefund' /** 未退款 */) }}</span>
        <span class="status running" v-if="Number(data.returnStatus) === 1">{{ $t('message.home.order.refunding' /** 退款中 */) }}</span>
        <span class="status success" v-if="Number(data.returnStatus) === 2">{{ $t('message.home.order.refundSuccess' /** 退款成功 */) }}</span>
        <span class="status fail" v-if="Number(data.returnStatus) === 3">{{ $t('message.home.order.refundFail' /** 退款失败 */) }}</span>
      </div>
    </div>
    <!-- 详情 -->
    <order-detail-dialog 
      v-model="detailDialogVisible" 
      :currentOrderInfo="currentOrderInfo"
      :remindLoading="remindLoading"
      :receiptLoading="receiptLoading"
      @cancel="cancelOrder" 
      @payment="payOrder"
      @remind="remindOrder"
      @return="returnOrder"
      @receipt="receiptOrder"
      @evaluation="evaluationOrder"
      @logistics="logisticsOrder"
    />
    <!-- 评论 -->
    <order-evaluation-dialog 
      v-model="evaluationDialogVisible" 
      :currentOrderInfo="currentOrderInfo" 
      :refresh="refresh" 
      @closeDetails="closeDetails"
    />
    <!-- 立即支付 -->
    
    <!-- 申请退货 -->
    <order-return-dialog 
      v-model="returnDialogVisible" 
      :currentOrderInfo="currentOrderInfo" 
      :refresh="refresh"
      @closeDetails="closeDetails"
    />
    <!-- 查看物流 -->
    <order-logistics-dialog 
      v-model="logisticsDialogVisible" 
      :currentOrderInfo="currentOrderInfo" 
      :refresh="refresh"
      @closeDetails="closeDetails"
    />
    <order-payment-dialog 
      v-model="paymentDialogVisible" 
      :currentOrderInfo="currentOrderInfo" 
      :refresh="refresh" 
      @closeDetails="closeDetails"
    />
    <!-- 取消订单 -->
    <order-cancel-dialog 
      v-model="cancelDialogVisible" 
      :currentOrderInfo="currentOrderInfo" 
      :refresh="refresh"
      @closeDetails="closeDetails"
    />
  </div>
</template>

<script>
import OrderDetailDialog from '@/page/userInfo/my-order/components/order-detail-dialog';
import OrderEvaluationDialog from '@/page/userInfo/my-order/components/order-evaluation-dialog';
import OrderPaymentDialog from '@/page/userInfo/my-order/components/order-payment-dialog';
import OrderCancelDialog from '@/page/userInfo/my-order/components/order-cancel-dialog';
import OrderReturnDialog from '@/page/userInfo/my-order/components/order-return-dialog';
import OrderLogisticsDialog from '@/page/userInfo/my-order/components/order-logistics-dialog';
import { copyTextToClipboard, numberFormat } from '@/util';
import { ES_REMIND_ORDER } from '@/common'
import { mapActions, mapGetters, mapMutations } from 'vuex';
export default {
  components: {
    OrderPaymentDialog,
    OrderEvaluationDialog,
    OrderDetailDialog,
    OrderCancelDialog,
    OrderReturnDialog,
    OrderLogisticsDialog
  },
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
  data() {
    return {
      evaluationDialogVisible: false,
      detailDialogVisible: false,
      paymentDialogVisible: false,
      cancelDialogVisible: false,
      returnDialogVisible: false,
      logisticsDialogVisible: false,
      currentOrderId: '',
      currentOrderInfo: {},
      receiptLoading: false,
      remindLoading: false
    };
  },
  computed: {
    ...mapGetters('order', ['remindList']),
    // 状态（-1=已取消）（0=待付款）（1=待发货）（2=已确认）（3=待收货）（4=已收获）（5=已评价）（6=退款)
    isPay() {
      return this.data.status === 0;
    },
    isEvaluate() {
      return this.data.status === 4;
    },
    isRemind() {
      return this.data.status === 1;
    },
    isConfirm() {
      return this.data.status === 3;
    },
    isRefundSuccess() {
      return this.data.status === 6;
    },
    isLogistics() {
      return [3, 4].includes(this.data.status)
    },
    showRemind() {
      return !this.remindList.includes(this.data.id)
    }
  },
  methods: {
    ...mapActions({
      requestOrderCancel: 'order/requestOrderCancel',
      requestOrderReceipt: 'order/requestOrderReceipt',
      requestOrderReturn: 'order/requestOrderReturn',
    }),
    ...mapMutations({
      updateRemindList: 'order/updateRemindList'
    }),
    openDetails() {
      this.currentOrderInfo = { ...this.data };
      this.detailDialogVisible = true;
    },
    closeDetails() {
      this.detailDialogVisible = false;
      this.paymentDialogVisible = false;
    },
    // 支付
    payOrder() {
      this.currentOrderInfo = { ...this.data };
      this.paymentDialogVisible = true;
    },
    // 取消
    cancelOrder() {
      this.isCancelStatus = true;
      this.currentOrderInfo = { ...this.data };
      this.cancelDialogVisible = true;
    },
    // 退货
    returnOrder() {
      this.currentOrderInfo = { ...this.data };
      this.returnDialogVisible = true;
    },
    // 评论
    evaluationOrder() {
      this.currentOrderInfo = { ...this.data };
      this.evaluationDialogVisible = true;
    },
    // 查看物流
    logisticsOrder() {
      this.currentOrderInfo = { ...this.data };
      this.logisticsDialogVisible = true;
    },
    // 提醒商户
    remindOrder() {
      const orderId = this.data.id
      if (!this.remindList.includes(orderId)) {
        this.$confirm(this.$t('message.home.remindContent'), this.$t('message.home.remindTitle'), {
          confirmButtonText: this.$t('message.home.confirm'),
          cancelButtonText: this.$t('message.home.cancel'),
          type: 'warning',
        }).then(() => {
          this.remindLoading = true
          setTimeout(() => {
            this.remindList.push(orderId);
            this.updateRemindList(this.remindList);
            localStorage.setItem(ES_REMIND_ORDER, JSON.stringify(this.remindList))
            this.$notify({
              title: this.$t("message.home.successTips"),
              message: this.$t("message.home.remindSuccess"),
              type: "success",
            });
            this.remindLoading = false
          }, 1000)
        })
      } else {
        this.$message.warning(this.$t('message.home.remindRepeat'))
      }
    },
    // 确认收获
    receiptOrder() {
      this.$confirm(this.$t('message.home.confirmReceiveGoods'), this.$t('message.home.hint'), {
        confirmButtonText: this.$t('message.home.confirm'),
        cancelButtonText: this.$t('message.home.cancel'),
        type: 'warning',
      })
        .then(async () => {
          try {
            this.receiptLoading = true;
            await this.requestOrderReceipt({ orderId: this.data.id });
            this.refresh && this.refresh();
            this.$notify({
              title: this.$t('message.home.successTips'),
              message: this.$t('message.home.operationSuccess'),
              type: 'success',
            });
            this.closeDetails()
          } finally {
            this.receiptLoading = false;
          }
        })
        .catch(() => {});
    },
    copy() {
      copyTextToClipboard(this.data.id);
      this.$notify({
        title: this.$t('message.home.successTips'),
        message: this.$t('message.home.copySuccess'),
        type: 'success',
      });
    },

    numberFormatFn(num) {
      return numberFormat(num);
    },
  },
};
</script>

<style lang="scss" scoped>
.order-item {
  border: 1px solid #eeeeee;
  padding: 10px 20px 20px;
  margin-top: 20px;
  display: flex;
  flex-direction: row;
   width: 872px;
  .el-icon-copy-document {
    cursor: pointer;
  }
}
</style>
