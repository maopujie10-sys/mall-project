<template>
  <!-- <el-dialog
    custom-class="detail-dialog"
    :title="$t('message.home.returnApply')"
    :visible.sync="dialogVisible"
  > -->
  <div class="info_page_container" style="width: 480px" v-loading="loading">
    <div
      class="page-title"
      style="cursor: pointer; margin-bottom: 20px"
      @click="goBack"
    >
      <i class="el-icon-arrow-left"></i> {{ $t("message.home.myOrder") }}/{{
        $t("message.home.returnApply")
      }}
    </div>
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
          :maxlength="120"
        />
      </el-form-item>
    </el-form>
    <div>
      <el-button
        size="medium"
        style="width: 480px; height: 44px"
        type="primary"
        :loading="loading"
        @click="confirmEvent"
      >
        {{ $t("message.home.确认") }}
      </el-button>
    </div>
  </div>

  <!-- </el-dialog> -->
</template>

<script>
import { mapActions } from "vuex";
import common from "@/util/common";
import { numberFormat } from "@/util";
export default {
  name: "order-detail-dialog",
  props: {
    // value: {
    //     type: Boolean,
    //     default: false,
    // },
    // currentOrderInfo: {
    //     type: Object,
    //     default: () => { },
    // },
    refresh: {
      type: Function,
    },
  },
  mounted() {},
  data() {
    const { currentOrder: currentOrderInfo = {} } = this.$route.params;
    return {
      currentOrderInfo,
      dialogVisible: this.value || false,
      loading: false,
      model: {
        returnReason: "",
        money: currentOrderInfo.priceCount || 0,
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
    // currentOrderInfo(val) {
    //     // this.dialogVisible = val;
    //     console.log(val)
    //     if (val) {
    //         this.model.money = this.currentOrderInfo.prizeReal;
    //     }
    // },
    // dialogVisible(val) {
    //     console.log(val);
    //     if (val !== this.value) {
    //         this.$emit("input", val);
    //     }
    // },
  },
  mounted() {
    if(this.$route.params.currentOrder){
      // console.log('this.$route.params.currentOrder ->',this.$route.params.currentOrder );
      this.model.money = this.$route.params.currentOrder.prizeReal || this.$route.params.currentOrder.priceCount;
      // console.log('222 ->', 222);
    }
  },
  methods: {
    ...mapActions({
      requestOrderReturn: "order/requestOrderReturn",
      requestGetUserBalanceList: "user/requestGetUserBalanceList",
    }),
    numberFormat,
    goBack() {
      this.$router.push("/userInfo/my-order");
    },
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
            this.$router.push("/userInfo/my-order");
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
