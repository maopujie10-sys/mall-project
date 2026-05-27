<template>
  <el-dialog
    custom-class="detail-dialog"
    :title="$t('message.home.returnApply')"
    :visible.sync="dialogVisible"
  >
    <div class="order-item" v-loading="loading">
      <el-form
        :model="model"
        :rules="rules"
        ref="returnForm"
        label-position="top"
      >
        <el-form-item
          :label="$t('message.home.returnReason')"
          prop="returnReason"
        >
          <el-select
            v-model="model.returnReason"
            :style="{ width: '100%' }"
            :placeholder="$t('message.home.cancelOrderTitle')"
          >
            <el-option
              v-for="item in options"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            ></el-option>
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('message.home.returnAmount')" prop="money">
          <el-input
            disabled
            :value="numberFormat(model.money)"
            :placeholder="$t('message.home.pleaseInput')"
          />
        </el-form-item>

        <el-form-item
          :label="$t('message.home.returnRemark')"
          prop="returnDetail"
        >
          <el-input
            v-model="model.returnDetail"
            class="content"
            type="textarea"
            :placeholder="$t('message.home.pleaseInput')"
            resize="none"
          />
        </el-form-item>
      </el-form>
    </div>

    <template slot="footer">
      <el-button
        size="mini"
        type="primary"
        :loading="loading"
        @click="confirmEvent"
      >
        {{ $t("message.home.confirm") }}
      </el-button>
      <el-button size="mini" plain @click="cancelEvent">
        {{ $t("message.home.cancel") }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script>
import { mapActions } from "vuex";
import common from "@/util/common";
import { numberFormat } from "@/util";
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
    refresh: {
      type: Function,
    },
  },
  data() {
    return {
      dialogVisible: this.value || false,
      loading: false,
      model: {
        returnReason: "",
        money: this.currentOrderInfo.priceCount || 0,
        returnDetail: "",
      },
      rules: {
        returnReason: [common.ruleUtils.getRule("required")],
        money: [common.ruleUtils.getRule("required")],
        // returnDetail: [
        //   common.ruleUtils.getRule("required"),
        // ],
      },
      options: [
        {
          label: this.$t("message.home.cancelOrder1"),
          value: 1,
        },
        {
          label: this.$t("message.home.cancelOrder2"),
          value: 2,
        },
        {
          label: this.$t("message.home.cancelOrder3"),
          value: 3,
        },
        {
          label: this.$t("message.home.cancelOrder4"),
          value: 4,
        },
        {
          label: this.$t("message.home.cancelOrder5"),
          value: 5,
        },
        {
          label: this.$t("message.home.cancelOrder6"),
          value: 6,
        },
        {
          label: this.$t("message.home.cancelOrder7"),
          value: 7,
        },
        {
          label: this.$t("message.home.cancelOrder8"),
          value: 8,
        },
        {
          label: this.$t("message.home.cancelOrder9"),
          value: 9,
        },
      ],
    };
  },
  watch: {
    value(val) {
      this.dialogVisible = val;
      if (val) {
        this.model.money = this.currentOrderInfo.priceCount;
      }
    },
    dialogVisible(val) {
      console.log(val);
      if (val !== this.value) {
        this.$emit("input", val);
      }
    },
  },
  methods: {
    ...mapActions({
      requestOrderReturn: "order/requestOrderReturn",
      requestGetUserBalanceList: "user/requestGetUserBalanceList",
    }),
    numberFormat,
    async requestData() {
      this.$refs.returnForm.validate(async (valid) => {
        if (valid) {
          try {
            this.loading = true;
            await this.requestOrderReturn(
              Object.assign({
                orderId: this.currentOrderInfo.id,
                ...this.model,
              })
            );

            this.$notify({
              title: this.$t("message.home.successTips"),
              message: this.$t("message.home.returnOrderSuccess"),
              type: "success",
            });
            this.dialogVisible = false;
            this.$emit("closeDetails");
            this.refresh && this.refresh();
            // 退货成功，更新余额
            this.requestGetUserBalanceList();
          } finally {
            this.loading = false;
          }
        }
      });
    },
    confirmEvent() {
      this.requestData();
    },
    cancelEvent() {
      this.dialogVisible = false;
    },
  },
};
</script>

<style lang="scss" scoped>
.order-item {
  .item {
    margin-bottom: 20px;
    .el-select {
      width: 100%;
    }
  }
}
</style>
