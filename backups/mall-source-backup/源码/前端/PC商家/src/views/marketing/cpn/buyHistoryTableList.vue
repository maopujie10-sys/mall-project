<template>
  <div class="table-list">
    <el-card>
      <el-form ref="searchForm" :model="form" inline>
        <el-form-item :label="$t('购买日期')" prop="time">

          <el-date-picker v-model="form.time" :end-placeholder="$t('结束日期')"
                          :range-separator="$t('至')" :start-placeholder="$t('开始日期')" type="datetimerange">
          </el-date-picker>

        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">{{ $t('查询') }}</el-button>
        </el-form-item>
        <el-form-item>
          <el-button @click="reset">{{ $t('重置') }}</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    <el-card class="table">
      <!--      {{tableData}}-->
      <el-table ref="multipleTable" :data="tableData" border stripe style="width: 100%">
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column :label="$t('购买套餐')" align="center" prop="name"></el-table-column>
        <el-table-column :label="$t('购买时间')" align="center" prop="startTime">
          <template slot-scope="scope">
            {{ scope.row.startTime | formatZoneDate }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('到期时间')" align="center" prop="stopTime" width="200">
          <template slot-scope="scope">
            {{ scope.row.stopTime | formatZoneDate }}
          </template>
        </el-table-column>
        <!--        <el-table-column-->
        <!--          label="付款方式"-->
        <!--          align="center"-->
        <!--          prop="buy_type"-->
        <!--        ></el-table-column>-->
        <el-table-column :label="$t('付款金额')" align="center" prop="change_after">

          <template slot-scope="scope">
            <div :style="{ color: scope.row.change_after > 0 ?  '#409EFF' : '#F56C6C' }">
              <FormatNumberShow :data="scope.row.prize" :currency="true"/>
            </div>
          </template>

        </el-table-column>
      </el-table>
      <div style="margin-top: 20px; text-align: center">
        <el-pagination :current-page="currentPage" :page-size="pageSize" :page-sizes="[10, 20, 50, 100]"
                       :total="tableData.length" background layout="total, sizes, prev, pager, next, jumper"
                       @size-change="handleSizeChange" @current-change="handleCurrentChange">
        </el-pagination>
      </div>
    </el-card>
  </div>
</template>

<script>
import {zhitongche_lishi_post} from "@/api/user";
import FormatNumberShow from "@/components/FormatNumberShow";

export default {
  name: "table-list",
  components: {
    FormatNumberShow
  },
  mounted() {
    this.getAllData();
  },
  data() {
    return {
      form: {
        startTime: '',
        endTime: '',
        percentage: '',
        discount: '',
        time: []
      },
      currentPage: 0,
      tableData: [],

      pageSize: 10,
    };
  },
  methods: {
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
      this.form.pageSize = val;
      this.getAllData();
    },
    // TODO: 当前第几页,去请求获取数据
    handleCurrentChange(val) {
      console.log(`当前页: ${val}`);
      this.getAllData();
    },
    // TODO: 获取列表数据
    getAllData() {
      console.log("请求获取列表数据");
      const form = {
        begin: this.form.time.length != 0 ? this.form.time[0] : undefined,
        end: this.form.time.length != 0 ? this.form.time[1] : undefined,
      }
      zhitongche_lishi_post(form).then(res => {
        this.tableData = res.data.pageList
      }).catch(function (err) {

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
    background-color: #fff;

    ::v-deep .el-table__header-wrapper thead tr th {
    }
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
    text-align: left;
    margin-bottom: 15px;

    ::v-deep .el-button {
      color: #fff;
      // background-color: rgb(22, 155, 213);
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

.up {
  text-align: right;
  display: inline-block;
  width: 60px;
  margin-left: -20px;
  margin-right: 10px;
}

::v-deep .date .el-date-editor {
  width: 100%;
}
</style>
