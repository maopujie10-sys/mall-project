<template>
  <div class="table-list">
    <div class="table">
      <el-table :data="data" border stripe style="width: 100%">
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column :label="$t('日期')" align="center" prop="dayString"></el-table-column>
        <!--        <el-table-column align="center" label="总销售额" prop="allCount">-->
        <!--          <template slot-scope="scope">-->
        <!--            <div>${{ scope.row.allCount }}</div>-->
        <!--          </template>-->
        <!--        </el-table-column>-->
        <el-table-column :label="$t('总订单')" align="center" prop="orderNum">
        </el-table-column>
        <el-table-column :label="$t('利润')" align="center" prop="totalProfit">
          <template slot-scope="scope">
            <FormatNumberShow :data="scope.row.totalProfit" :currency="true"/>
          </template>
        </el-table-column>
        <el-table-column :label="$t('取消订单')" align="center" prop="orderCancel"></el-table-column>
        <el-table-column :label="$t('退款订单')" align="center" prop="orderReturns"></el-table-column>
      </el-table>
      <!--              <div style="margin-top: 20px; text-align: center">-->
      <!--                <el-pagination background @size-change="handleSizeChange" @current-change="handleCurrentChange" :current-page="currentPage" :page-sizes="[10, 20, 50, 100]" :page-size="pageSize" layout="total, sizes, prev, pager, next, jumper" :total="1">-->
      <!--                </el-pagination>-->
      <!--              </div>-->
    </div>
  </div>
</template>

<script>
import FormatNumberShow from "@/components/FormatNumberShow/index.vue";

export default {
  name: "table-list",
  components: {FormatNumberShow},
  props: {
    type: {
      type: String,
      default: "",
    },
    data: {
      //类型不匹配会警告
      type: Array,
      default: () => {
        return []
      },
      required: true,
      // 返回值不是 true,会警告
    }
  },
  mounted() {
    // TODO: 根据传入的type 去获取数据
    this.getAllData();
  },
  data() {
    return {
      currentPage: 0,
      allData: [],
      pageSize: 10,
    };
  },
  methods: {
    // TODO: 请求获取页面数据
    getAllData() {
    },
    // TODO: 每页几条,去请求获取数据
    handleSizeChange(val) {
      console.log(`每页 ${val} 条`);
    },
    // TODO: 当前第几页,去请求获取数据
    handleCurrentChange(val) {
      console.log(`当前页: ${val}`);
    },
  },
};
</script>

<style lang="scss" scoped>
.table-list {
  width: 100%;
  height: 100%;

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
</style>
