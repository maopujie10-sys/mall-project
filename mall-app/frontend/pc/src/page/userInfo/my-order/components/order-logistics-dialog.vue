<template>
  <el-dialog
    custom-class="logistics-dialog"
    :title="$t('message.home.order.logistics')"
    :visible.sync="dialogVisible"
  >
    <div class="logistics-list" v-loading="loading">
      <el-steps direction="vertical" :active="logistics.length">
        <el-step
          v-for="item in list"
          :key="item.id"
          :title="
            $t('message.home.订单') + '#' +
            item.orderId +'#' +
            $t('message.home.' + item.text)
          "
          :description="dateFormat(item.updateTime)"
        ></el-step>
      </el-steps>
    </div>
  </el-dialog>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import { numberFormat, dateFormat } from "@/util";
export default {
  name: "order-logistics-dialog",
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
      list: [],
    };
  },
  computed: {
    ...mapGetters("order", ["logistics"]),
  },
  watch: {
    value(val) {
      this.dialogVisible = val;
    },
    dialogVisible(val) {
      if (val !== this.value) {
        this.$emit("input", val);
      }
      if (val) this.requestData();
    },
  },
  methods: {
    ...mapActions({
      requestOrderLogistics: "order/requestOrderLogistics",
    }),
    async requestData() {
      try {
        this.loading = true;
        await this.requestOrderLogistics({
          orderId: this.currentOrderInfo.id,
        });
        console.log("this.logistics ->", this.logistics);
        if (this.logistics) {
          this.list = this.logistics.map((item) => {
            const arr = item.log.split(item.orderId);
            return {
              ...item,
              text: arr[1],
              // log: `${this.$t("message.home.订单")}<span class="log_id">#${
              //   item.orderId
              // }</span>${this.$t(message.home + "." + arr[1])}`,
            };
          });
          console.log("list ->", this.list);
        }
      } finally {
        this.loading = false;
      }
    },
    async submit(item) {
      //
    },
    dateFormat,
    numberFormatFn(num) {
      return numberFormat(num);
    },
  },
};
</script>

<style lang="scss" scoped>
.logistics-dialog {
  .logistics-list {
    height: 400px;
    min-height: 400px;
    padding: 30px 0;

    /deep/ .el-step.is-vertical {
      .el-step__title {
        font-size: 14px;
      }

      .el-step__description {
        font-size: 13px;
      }
    }

    .logistics-item {
      border: 1px solid #eeeeee;
      padding: 50px 22px;

      + .logistics-item {
        margin-top: 18px;
      }

      .product-item {
        display: flex;

        img {
          width: 62px;
          height: 62px;
        }

        .info {
          margin-left: 18px;
          flex: 1;

          .price {
            font-weight: 500;
            font-size: 16px;
            color: var(--color-main);
            margin-top: 7px;
          }

          .el-rate {
            margin-top: 5px;
          }
        }
      }

      .content {
        margin-top: 25px;

        .el-textarea__inner {
          border: 1px solid #efefef;
          height: 70px;
        }
      }
    }
  }

  .action {
    padding: 20px 0;
    display: flex;
    align-items: center;
    justify-content: center;

    .el-button {
      width: 450px;
      height: 50px;
      color: #fff;
      background: var(--color-main);
      border-color: var(--color-main);
      border-radius: 4px;
    }
  }
}
</style>
