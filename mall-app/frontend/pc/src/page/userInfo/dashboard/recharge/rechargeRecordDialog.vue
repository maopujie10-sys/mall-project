<template>
  <el-dialog
    custom-class="wallet-dialog recharge-dialog"
    :title="$t('message.home.rechargeRecord')"
    :center="true"
    :visible.sync="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :append-to-body="true"
  >
    <div v-loading="tableLoading" style="min-height: 200px">
      <div v-if="staticListData.length">
        <div class="record" v-for="item in tableListData" :key="item.order_no">
          <div class="record-item flex-between">
            <div class="label">{{ $t("message.home.serialNumber") }}：</div>
            <div class="label">
              {{ item.order_no }}
              <i class="el-icon-copy-document" @click="copy(item.order_no)"></i>
            </div>
          </div>
          <div class="record-item flex-between">
            <div class="label">{{ $t("message.home.time") }}：</div>
            <div class="label">{{ item.createTime }}</div>
          </div>
          <div class="record-item flex-between">
            <div class="label">{{ $t("message.home.amount") }}：</div>
            <div class="value">{{ item.amount }}</div>
          </div>
          <div class="record-item flex-between">
            <div class="label">{{ $t("message.home.orderStatus") }}：</div>
            <div :class="orderStatusMap[item.state].class">
              {{ orderStatusMap[item.state].text }}
            </div>
          </div>
        </div>
      </div>
      <el-empty
        v-if="!staticListData.length && !tableLoading"
        :description="$t('message.home.noData')"
      ></el-empty>
    </div>
    <div
      v-if="!tableLoading && staticListData.length"
      class="common-pagination"
    >
      <el-pagination
        background
        layout="prev, pager, next"
        class="es-pagination"
        :current-page="pageNum"
        :page-size="pageSize"
        :total="staticListData.length"
        @current-change="currentChange"
      />
    </div>
  </el-dialog>
</template>

<script>
  import { mapGetters, mapActions } from "vuex";
  import { copyTextToClipboard } from "@/util";
  export default {
    props: {
      value: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        dialogVisible: this.value || false,
        orderStatusMap: {
          0: {
            text: this.$t("message.home.processing" /** 处理中*/),
            class: "value",
          },
          1: {
            text: this.$t("message.home.successTips" /**成功 */),
            class: "success",
          },
          2: {
            text: this.$t("message.home.fail" /**失败 */),
            class: "fail",
          },
        },
        tableLoading: true,
        pageNum: 1,
        pageSize: 2,
        staticListData: [],
      };
    },
    watch: {
      value(val) {
        this.dialogVisible = val;
      },
      dialogVisible(val) {
        if (val !== this.value) {
          this.$emit("input", val);
        }
        if (val) {
          this.getListData();
        }
      },
    },
    computed: {
      ...mapGetters("recharge", ["rechargeRecordList"]),
      tableListData() {
        const offset = (this.pageNum - 1) * this.pageSize;
        return this.staticListData.slice(offset, this.pageSize + offset);
      },
    },
    methods: {
      ...mapActions("recharge", ["requestRechargeRecordList"]),
      copy(id) {
        copyTextToClipboard(id);
        this.$notify({
          title: this.$t("message.home.successTips" /**成功 */),
          message: this.$t("message.home.copySuccess" /**复制成功 */),
          type: "success",
        });
      },
      async getListData() {
        this.tableLoading = true;
        await this.requestRechargeRecordList()
          .then((res) => {
            this.staticListData = res || [];
            this.tableLoading = false;
          })
          .catch(() => {
            this.tableLoading = false;
          });
      },
      currentChange(page) {
        this.pageNum = page;
      },
    },
  };
</script>

<style lang="scss" scoped>
  .recharge-dialog {
    .record {
      border: 1px solid var(--color-border);
      margin: 0 0 15px 0;
      .record-item {
        font-weight: 400;
        font-size: 14px;
        padding: 16px 10px;
        border-bottom: 1px solid var(--color-border);
        &:last-child {
          border-bottom: 0;
        }
        .label {
          color: var(--color-title);
        }
        .value {
          color: var(--color-main);
        }
        .success {
          color: var(--color-success);
        }
        .fail {
          color: var(--color-fail);
        }
        .el-icon-copy-document {
          cursor: pointer;
        }
      }
    }
  }
</style>
