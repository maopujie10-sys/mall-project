<template>
  <div class="table-list">
    <div class="search">
      <el-form inline :model="form" ref="searchForm">
        <el-form-item :label="$t('订单类型')" prop="order_status">
          <el-select :placeholder="$t('请选择')" v-model="form.order_status">
            <el-option v-for="item in order_options" :key="item.value" :label="item.label" :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('下单时间')" prop="time">
          <el-date-picker :end-placeholder="$t('结束日期')" :start-placeholder="$t('开始日期')"
                          :range-separator="$t('至')" v-model="form.time" type="datetimerange"
                          value-format="yyyy-MM-dd HH:mm:ss">
          </el-date-picker>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">{{ $t('查询') }}</el-button>
        </el-form-item>
        <el-form-item>
          <el-button @click="reset">{{ $t('重置') }}</el-button>
        </el-form-item>
      </el-form>
    </div>
    <div class="table">
      <el-table border :data="tableData" stripe style="width: 100%">
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column :label="$t('订单类型')" align="center" prop="content_type">
          <template slot-scope="scope">
            <div>
              {{ $t(getOrderType(scope.row.content_type)) }}
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="$t('流水号')" align="center" prop="id"></el-table-column>
        <el-table-column :label="$t('变更金额')" align="center" prop="change_money">
          <template slot-scope="scope">
            <div :style="{ color: scope.row.amount > 0 ?  '#67C23A' : '#F56C6C'}" v-if="scope.row.amount != 0">
              <!--              {{-->
              <!--                scope.row.amount > 0-->
              <!--                  ? "+$" + scope.row.amount.toFloor(2)-->
              <!--                  : "-$" + scope.row.amount.toFloor(2).replace('-', '')-->
              <!--              }}-->
              <template v-if="scope.row.amount > 0">
                +
                <FormatNumberShow :data="scope.row.amount" :currency="true"/>
              </template>
              <template v-else>
                -
                <FormatNumberShow :data="(scope.row.amount+'').replace('-', '')" :currency="true"/>
              </template>
              <el-popover
                  placement="right"
                  trigger="click"
                  width="300"
                  v-if="scope.row.content_type == 'order-income'&&scope.row.detail.length>0"
              >
                <div class="show-money-content">
                  <div class="show-money-title">{{ $t('利润去哪里了？') }}</div>
                  <div>
                    <div class="show-money-step" v-for="(item,index) in [$t('一级返佣'),$t('二级返佣'),$t('三级返佣')]"
                         :key="index">
                      <div>
                        {{ item }}
                      </div>
                      <div v-for="(sitem,sindex) in scope.row.detail" :key="`s`+sindex" v-if="sitem.level===index+1">
                        <FormatNumberShow :data="sitem.rebate" :currency="true"/>
                      </div>
                    </div>
                  </div>
                </div>
                <i class="el-icon-question" slot="reference"
                   style="cursor: pointer;color: #cccccc;margin-left: 4px;font-size: 16px;position: relative;top: 2px;"></i>
              </el-popover>
            </div>
            <span v-else="scope.row.amount == 0">$0</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('变更前')" align="center" prop="amount_before">
          <template slot-scope="scope">
            <FormatNumberShow :data="scope.row.amount_before" :currency="true"/>
          </template>
        </el-table-column>
        <el-table-column :label="$t('变更后')" align="center" prop="amount_after">
          <template slot-scope="scope">
            <FormatNumberShow :data="scope.row.amount_after" :currency="true"/>
          </template>
        </el-table-column>
        <el-table-column :label="$t('账变时间')" align="center" prop="createTimeStr">
          <template slot-scope="scope">
            {{ scope.row.createTimeStr | formatZoneDate }}
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top: 20px; text-align: center">
        <!--        <el-pagination background @size-change="handleSizeChange" @current-change="handleCurrentChange"-->
        <!--                       :current-page="currentPage" :page-sizes="[10, 20, 50, 100]" :page-size="pageSize"-->
        <!--                       layout="total, sizes, prev, pager, next, jumper" :total="tableData.length">-->
        <!--        </el-pagination>-->
        <el-row>
          <el-button type="primary" @click="fenye('b')">{{ $t("上一页") }}</el-button>
          <el-button type="primary" style="margin-left: 10px;" @click="fenye('a')">{{ $t("下一页") }}</el-button>
        </el-row>
      </div>
    </div>
  </div>
</template>

<script>
import {zijinjilu_post} from "@/api/user";
import FormatNumberShow from "@/components/FormatNumberShow";

export default {
  name: "table-list",
  mounted() {
    this.getAllData()
  },
  components: {
    FormatNumberShow
  },
  data() {
    return {
      currentPage: 0,
      // 充值
      // 提现
      // 推广佣金
      // 商品采购
      // 商品退款
      // 订单收入
      // 直通车购买
      // 冻结余额
      // 解冻余额
      order_options: [
        {
          label: this.$t('全部'),
          value: "",
        },
        {
          label: this.$t('充值订单'),
          value: "recharge",
        },
        {
          label: this.$t('提现订单'),
          value: "withdraw",
        },
        {
          label: this.$t('推广佣金'),
          value: "brokerage",
        },
        {
          label: this.$t('商品采购'),
          value: "push-order",
        },
        {
          label: this.$t('商品退款'),
          value: "return-order-seller",
        },
        {
          label: this.$t('订单收入'),
          value: "order-income",
        },
        {
          label: this.$t('购买直通车'),
          value: "combo-order",
        },
        {
          label: this.$t('冻结余额'),
          value: "freeze_seller_money",
        },
        {
          label: this.$t('解冻余额'),
          value: "unfreeze_seller_money",
        },
        {
          label: this.$t('活动赠送'),
          value: "first-recharge-bonus",
        },
        {
          label: this.$t("升级礼金"),
          value: "mall_level_upgrade_award",
        },
        {
          label: this.$t("赠送彩金"),
          value: "jackpot",
        },
        {
          label: this.$t("邀请奖励"),
          value: "invitation-rewards",
        },
      ],
      form: {
        order_status: "",
        time: null,
      },
      tableData: [],
      pageNum: 1,
      pageSize: 10,
    };
  },
  watch: {
    'form.order_status': function (val) {
      this.pageNum = 1
    },
  },
  methods: {
    showContent() {
      this.$message({
        message: this.$t('变更金额说明'),
        type: 'warning'
      });
    },
    fenye(x) {
      if (x == 'a') {
        this.pageNum++
      }
      if (x == 'b') {
        if (this.pageNum == '1') {
          return
        }
        this.pageNum--
      }
      this.getAllData()
    },
    getOrderType(type) {
      return this.order_options.find(item => item.value === type)?.label
    },
    // TODO: 搜索请求
    search() {
      console.log(this.form);
      this.getAllData();
    },
    // TODO: 重置搜索条件并且请求
    reset() {
      this.$refs.searchForm.resetFields();
      this.getAllData();
    },
    // TODO: 每页几条,去请求获取数据
    handleSizeChange(val) {
      console.log(`每页 ${val} 条`);
      this.getAllData();
    },
    // TODO: 当前第几页,去请求获取数据
    handleCurrentChange(val) {
      console.log(`当前页: ${val}`);
      this.getAllData();
    },
    // TODO: 获取列表数据
    getAllData() {
      var form = {
        content_type: this.form.order_status,
        beginTime: this.form.time ? this.form.time[0] : undefined,
        endTime: this.form.time ? this.form.time[1] : undefined,
        page_no: this.pageNum,
        pageSize: this.pageSize
      }
      zijinjilu_post(form).then(({data}) => {
        let arr = [];
        data?.forEach(item => {
          if (this.order_options.find(res => res.value === item.content_type)) {
            arr.push(item)
          }
        })
        this.tableData = arr
      })
    },
  },
};
</script>

<style lang="scss" scoped>
.table-list {
  width: 100%;
  height: 100%;

  .search {
    padding: 20px 20px 0px 20px;
    background-color: #fff;
    margin-bottom: 10px;
    border-radius: 10px;
  }

  .table {
    padding: 20px;
    background-color: #fff;
    border-radius: 10px;
  }

  .detail {
    border: 1px solid #ccc;
    border-radius: 3px;
    margin-bottom: 20px;

    .header {
      line-height: 40px;
      padding-left: 10px;
      border-bottom: 1px solid #ccc;
    }

    .main-price {
      .item {
        display: flex;
        line-height: 30px;
        margin: 10px;
        justify-content: space-between;
        font-size: 16px;
        font-weight: 800;

        .name {
          font-weight: 800;
          font-size: 16px;
        }
      }

      .top {
        border-top: 1px solid #ccc;
        padding-top: 10px;
      }
    }
  }

  .btn {
    text-align: center;

    ::v-deep .el-button {
      color: #fff;
      background-color: #000;
    }
  }

  .order-top {
    border: 1px solid #ccc;
    border-radius: 3px;
    margin-bottom: 20px;

    .header {
      line-height: 40px;
      padding-left: 10px;
      border-bottom: 1px solid #ccc;
    }

    .main {
      .border {
        border-top: 1px solid #ccc;
      }

      &-content {
        display: flex;
        justify-content: space-between;
        margin: 0 10px;

        .left {
          width: 45%;

          .item {
            display: flex;
            line-height: 30px;
            margin: 10px;
            justify-content: space-between;
            font-size: 16px;
            font-weight: 800;
          }
        }

        .right {
          width: 40%;

          .item {
            display: flex;
            line-height: 30px;
            margin: 10px;
            justify-content: space-between;
            font-size: 16px;
            font-weight: 800;
          }
        }
      }
    }
  }

  .order-bottom {
    display: flex;
    justify-content: space-between;

    .content-left,
    .content-right {
      border: 1px solid #ccc;
      border-radius: 3px;
      margin-bottom: 20px;

      .header {
        line-height: 40px;
        padding-left: 10px;
        border-bottom: 1px solid #ccc;
      }
    }

    .content-left {
      width: calc(70% - 20px);
    }

    .content-right {
      width: 30%;

      .item {
        display: flex;
        line-height: 30px;
        margin: 10px;
        justify-content: space-between;
        font-size: 16px;
        font-weight: 800;

        .name {
          font-weight: 800;
          font-size: 16px;
        }
      }

      .top {
        border-top: 1px solid #ccc;
        padding-top: 10px;
      }
    }
  }

  //::v-deep .el-dialog__header {
  //  background-color: #ccc;
  //  font-weight: 700;
  //  color: #000000;
  //}
  //::v-deep .el-dialog__headerbtn .el-dialog__close {
  //  color: #333;
  //}
}

.el-icon-question {
  font-size: 24px;
}

.show-money-content {
  min-width: 100px;

  .show-money-title {
    font-size: 14px;
    margin-bottom: 12px;
    font-weight: 600;
  }

  .show-money-step {
    height: 32px;
    line-height: 32px;
    border: solid #e5e5e5 1px;
    border-radius: 4px;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;

    > div {
      height: 100%;
      padding: 0 12px;

      &:nth-child(1) {
        display: block;
        background-color: #e5e5e5;
      }
    }
  }
}
</style>
