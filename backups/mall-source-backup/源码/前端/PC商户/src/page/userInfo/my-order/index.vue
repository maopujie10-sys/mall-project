<template>
  <div class="my-order">
    <div class="page-title">{{ $t("message.home.myOrder") }}</div>
    <div class="tabs">
      <div
        v-for="tab in tabs"
        :key="tab.value"
        class="tab-item"
        :class="{ active: tabActive === tab.value }"
        @click="tabChange(tab.value)"
      >
        {{ tab.label }}
      </div>
    </div>
    <div style="width: 872px" v-loading="loading">
      <span v-if="orderList.length">
        <order-item
          v-for="item in orderList"
          :key="item.id"
          :data="item"
          :refresh="requestData"
        />
      </span>
      <el-empty
        v-if="!orderList.length && !loading"
        :description="$t('message.home.noData')"
      ></el-empty>
    </div>
    <div v-if="orderList.length || total" class="common-pagination">
      <el-pagination
        background
        layout="prev, pager,next"
        class="es-pagination"
        :page-size="pageSize"
        :pager-count="5"
        :current-page="pageNum"
        :total="total"
        @current-change="currentChange"
      />
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters } from "vuex";
import OrderItem from "./components/order-item";
export default {
  name: "my-order",
  components: { OrderItem },
  data() {
    return {
      tabs: [
        {
          label: this.$t("message.home.all"),
          value: "",
        },
        {
          label: this.$t("message.home.pending"), // 待支付
          value: "0",
        },
        // {
        //   label: this.$t("message.home.cancelled"), // 以取消
        //   value: '-1',
        // },
        {
          label: this.$t("message.home.delivered"), // 待发货
          value: "1",
        },
        // {
        //   label: this.$t("message.home.confirmed"), // 已确认
        //   value: '2',
        // },
        {
          label: this.$t("message.home.receipt"), // 待收货
          value: "3",
        },
        // {
        //   label: this.$t("message.home.harvested"), // 已收货
        //   value: '4',
        // },
        {
          label: this.$t("message.home.comment"), // 已评价
          value: "4",
        },
        {
          label: this.$t("message.home.refund"), // 已退款
          value: "6",
        },
      ],
      tabActive: "",
      loading: false,
      pageNum: 1,
      pageSize: 5,
      total: 0,
    };
  },
  computed: {
    ...mapGetters({
      orderList: "order/orderList",
    }),
  },
  watch: {
    async tabActive(newValue, oldValue) {
      if (newValue !== oldValue) {
        this.requestData(newValue ? { status: newValue } : {});
      }
    },
  },
  async mounted() {
    this.requestData();
  },
  activated() {
    this.requestData();
  },
  methods: {
    tabChange(tab) {
      if (this.tabActive !== tab) {
        this.pageNum = 1;
        // this.loading = true
        this.tabActive = tab;
      }
    },
    ...mapActions({
      requestOrderList: "order/requestOrderList",
    }),
    async requestData(params = {}) {
      if (this.loading) {
        return;
      }
      this.loading = true;
      this.requestOrderList({
        ...params,
        ...{
          pageNum: this.pageNum,
          pageSize: this.pageSize,
          status: this.tabActive,
        },
      })
        .then((res) => {
          this.total = res.pageInfo?.totalElements || 0;
          this.loading = false;
        })
        .catch((err) => {
          console.log(err);
          this.loading = false;
        });
      console.log(this.loading);
    },
    currentChange(page) {
      this.pageNum = page;
      this.requestData();
    },
  },
};
</script>

<style lang="scss" scoped>
html[dir='rtl'] {
  .my-order {
    margin-left: 0;
    margin-right: 50px;
  }
}
.my-order {
  // width: 702px;
  margin-top: 32px;
  margin-left: 50px;
  flex: 1;

  .tabs {
    margin-top: 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 30px;
    // border: 1px solid #eeeeee;
    border-radius: 4px;
    width: 100%;
    // padding: 0 25px;

    .tab-item {
      height: 100%;
      display: flex;
      align-items: center;
      // border-bottom: 2px solid transparent;
      cursor: pointer;
      user-select: none;
      padding: 0 20px;
      background-color: #eeeeee;
      border-radius: 5px;
      color: #999999;

      &.active {
        // border-bottom: 2px solid var(--color-main);
        background-color: var(--color-main);
        color: white;
      }
    }
  }

  .order-list {
    /deep/ .option-list {
      .option-item {
        display: flex;
        align-items: flex-start;
        margin-bottom: 10px;
        padding: 10px 0;

        + .option-item {
          border-top: 1px solid #eee;
        }

        &.block {
          display: block;

          .value {
            flex: inherit;
            max-width: 100%;
            text-align: left;
          }
        }

        .label {
          flex: 1;
          font-size: 14px;
          color: #333333;
        }

        .value {
          flex: 2;
          max-width: 300px;
          font-size: 14px;
          color: #666666;
          text-align: right;

          .text {
            font-weight: 600;
            font-size: 14px;
            color: #000000;
          }

          .desc {
            font-weight: 500;
            font-size: 12px;
            color: #999999;
            margin-top: 4px;
          }

          .price {
            font-weight: 500;
            font-size: 16px;
            color: var(--color-price);
          }

          .detail-link {
            font-size: 14px;
            line-height: 16px;
            color: var(--color-main);
            cursor: pointer;
            user-select: none;
          }

          .product-item {
            display: flex;
            width: 100%;
            align-items: center;
            margin-top: 15px;

            img {
              width: 62px;
              height: 62px;
            }

            .title {
              flex: 1;
              margin-left: 18px;
              font-weight: 400;
              font-size: 14px;
            }
          }
        }
      }
    }

    /deep/ .actions {
      display: flex;
      align-items: center;
      justify-content: flex-end;

      > * + * {
        margin-left: 16px;
      }

      .status {
        text-align: right;

        &.unReturn {
          color: #999;
        }

        &.running {
          color: var(--color-main);
        }

        &.success {
          color: #32aa15;
        }

        &.fail {
          color: #e10015;
        }
      }
    }
  }
}
</style>
