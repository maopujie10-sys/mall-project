<template>
  <el-dialog
    custom-class="detail-dialog"
    :title="$t('message.home.cancelOrder')"
    :visible.sync="dialogVisible"
  >
    <div class="order-item" v-loading="loading">
      <el-form
        :model="model"
        :rules="rules"
        ref="cancelForm"
        label-position="top"
      >
        <el-form-item
          :label="$t('message.home.cancelReason')"
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
      </el-form>
    </div>

    <template slot="footer">
      <el-button
        size="mini"
        type="primary"
        :loading="loading"
        @click="confirmEvent"
      >
        {{ $t("message.home.确认") }}
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
      },
      rules: {
        returnReason: [common.ruleUtils.getRule("required")],
      },

      options: [
        {
          label: this.$t("message.home.cancelOrderMap.0"),
          value: 1,
        },
        {
          label: this.$t("message.home.cancelOrderMap.1"),
          value: 2,
        },
        {
          label: this.$t("message.home.cancelOrderMap.2"),
          value: 3,
        },
        {
          label: this.$t("message.home.cancelOrderMap.3"),
          value: 4,
        },
        {
          label: this.$t("message.home.cancelOrderMap.4"),
          value: 5,
        },
      ],
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
    },
  },
  methods: {
    ...mapActions({
      requestOrderCancel: "order/requestOrderCancel",
      requestGetUserBalanceList: "user/requestGetUserBalanceList",
    }),
    async requestData() {
      this.$refs.cancelForm.validate(async (valid) => {
        if (valid) {
          try {
            this.loading = true;
            await this.requestOrderCancel(
              Object.assign({
                orderId: this.currentOrderInfo.id,
                returnReason: this.model.returnReason,
              })
            );

            this.$notify({
              title: this.$t("message.home.successTips"),
              message: this.$t("message.home.cancelOrderSuccess"),
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
