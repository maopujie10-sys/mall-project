<template>
  <div class="table-list">
    <el-card>
      <el-form ref="searchForm" :model="form" inline>
        <el-form-item :label="$t('订单状态')" prop="time">

          <el-select v-model="form.evaluationType" :placeholder="$t('请选择')">

            <el-option v-for="item in status_options" :key="item.value" :label="item.label" :value="item.value">
            </el-option>

          </el-select>

        </el-form-item>
        <el-form-item :label="$t('申请日期')" prop="time">

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
    <el-card>
      <el-table ref="multipleTable" :data="tableData" border stripe style="width: 100%">
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column :label="$t('订单号')" align="center" prop="id"></el-table-column>
        <el-table-column :label="$t('申请日期')" align="center" prop="createTime">
          <template slot-scope="scope">
            {{ scope.row.createTime | formatZoneDate }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('退款理由')" align="center" prop="returnReason" width="200">

          <template slot-scope="scope">
            <span v-if="scope.row.returnReason == '1'">{{ $t('未收到货') }}</span>
            <span v-if="scope.row.returnReason == '2'">{{ $t('不喜欢、不想要') }}</span>
            <span v-if="scope.row.returnReason == '3'">{{ $t('卖家发错货') }}</span>

            <span v-if="scope.row.returnReason == '4'">{{ $t('假冒品牌') }}</span>
            <span v-if="scope.row.returnReason == '5'">{{ $t('少发、漏发') }}</span>
            <span v-if="scope.row.returnReason == '6'">{{ $t('收到商品破损') }}</span>
            <span v-if="scope.row.returnReason == '7'">{{ $t('存在质量问题') }}</span>
            <span v-if="scope.row.returnReason == '8'">{{ $t('与商家协商一致退款') }}</span>
            <span v-if="scope.row.returnReason == '9'">{{ $t('其他原因') }}</span>
          </template>

        </el-table-column>
        <el-table-column :label="$t('退款说明')" align="center" prop="returnDetail">
          <template slot-scope="scope">
            {{ scope.row.returnDetail || '--' }}
          </template>
        </el-table-column>
        <!--        <el-table-column-->
        <!--          label="商品名称"-->
        <!--          align="center"-->
        <!--          prop="name"-->
        <!--        ></el-table-column>-->
        <el-table-column :label="$t('商品金额')" align="center" prop="change_money">

          <template slot-scope="scope">
            <div :style="{ color: scope.row.returnPrice > 0 ?  '#409EFF' : '#F56C6C' }">
              <FormatNumberShow :data="scope.row.returnPrice" :currency="true"/>
            </div>
          </template>

        </el-table-column>
        <el-table-column :label="$t('状态')" align="center" prop="change_money">

          <template slot-scope="scope">
            <span v-if="scope.row.returnStatus == '0'">{{ $t('未退款') }}</span>
            <span v-if="scope.row.returnStatus == '1'" style="color: #f59a23">{{ $t('退款中') }}</span>
            <span v-if="scope.row.returnStatus == '2'" style="color: #1abc9c">{{ $t('退款成功') }}</span>
            <span v-if="scope.row.returnStatus == '3'" style="color: #d9001b">{{ $t('退款失败') }}</span>
          </template>

        </el-table-column>
        <el-table-column :label="$t('操作')" align="center" width="80">
          <template slot-scope="scope">
            <div style="display: flex;justify-content: center;">
              <el-button size="mini" @click="openOrder(scope.row)">{{ $t('查看') }}</el-button>
            </div>
          </template>

        </el-table-column>
      </el-table>
      <div style="margin-top: 20px; text-align: center">
        <el-pagination
            :current-page.sync="pageNum"
            :page-size="pageSize"
            :total="totalElements"
            background
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange">
        </el-pagination>
      </div>
    </el-card>
    <el-dialog :title="$t('退款详情')" :visible.sync="orderDialogVisible" width="600px">
      <div class="order-top">
        <div class="header">{{ $t('订单详情') }}</div>
        <div class="main">
          <div class="main-content">

            <div class="right" style="width: 100%;">
              <div class="item">
                <div>{{ $t('申请时间') }}</div>
                <div>{{ userInfo2.createTime | formatZoneDate }}</div>
              </div>
              <div class="item">
                <div>{{ $t('退款单号') }}</div>
                <div>{{ userInfo2.id }}</div>
              </div>
              <div class="item">
                <div>{{ $t('退款金额') }}</div>
                <div>
                  <FormatNumberShow :data="userInfo2.returnPrice" :currency="true"/>
                </div>
              </div>
              <div class="item">
                <div>{{ $t('退款状态') }}</div>
                <div><span v-if="userInfo2.returnStatus == '0'">{{ $t('未退款') }}</span>
                  <span v-if="userInfo2.returnStatus == '1'" style="color: #f59a23">{{ $t('退款中') }}</span>
                  <span v-if="userInfo2.returnStatus == '2'" style="color: #1abc9c">{{ $t('退款成功') }}</span>
                  <span v-if="userInfo2.returnStatus == '3'" style="color: #d9001b">{{ $t('退款失败') }}</span></div>
              </div>
              <div class="item">
                <div>{{ $t('退款说明') }}</div>
                <div>{{ userInfo2.returnDetail || '--' }}</div>
              </div>
              <div class="item">
                <div>{{ $t('退款理由') }}</div>
                <div><span v-if="userInfo2.returnReason == '1'">{{ $t('未收到货') }}</span>
                  <span v-if="userInfo2.returnReason == '2'">{{ $t('不喜欢、不想要') }}</span>
                  <span v-if="userInfo2.returnReason == '3'">{{ $t('卖家发错货') }}</span>

                  <span v-if="userInfo2.returnReason == '4'">{{ $t('假冒品牌') }}</span>
                  <span v-if="userInfo2.returnReason == '5'">{{ $t('少发、漏发') }}</span>
                  <span v-if="userInfo2.returnReason == '6'">{{ $t('收到商品破损') }}</span>
                  <span v-if="userInfo2.returnReason == '7'">{{ $t('存在质量问题') }}</span>
                  <span v-if="userInfo2.returnReason == '8'">{{ $t('与商家协商一致退款') }}</span>
                  <span v-if="userInfo2.returnReason == '9'">{{ $t('其他原因') }}</span></div>
              </div>
              <!--                <div class="item">-->
              <!--                  <div>销售金额</div>-->
              <!--                  <div>${{ userInfo2.prizeReal + userInfo2.profit }}</div>-->
              <!--                </div>-->
            </div>
          </div>
        </div>
      </div>
      <div class="order-bottom" style="width: 100%;">
        <div class="content-left" style="width: 100%;">
          <div class="header">{{ $t('退款产品') }}</div>
          <div class="main">
            <el-table :data="detailOrderData" style="width: 100%">
              <el-table-column :label="$t('封面图')" prop="goodsName" width="70">
                <template slot-scope="scope">
                  <img :src="scope.row.goodsIcon" alt="" style="width: 50px; height: 50px"/>
                </template>
              </el-table-column>
              <el-table-column :label="$t('产品名称')" prop="goodsNum" width="320">
                <template slot-scope="scope">
                  {{ scope.row.goodsName }}
                </template>
              </el-table-column>
              <el-table-column :label="$t('规格')" prop="status" width="160">
                <template slot-scope="scope">
                  <div v-if="!scope.row.attributes||(scope.row.attributes&&scope.row.attributes.length===0)">--</div>
                  <div v-else>
                    <div v-for="(item,index) in scope.row.attributes" :key="index">
                      <span>{{ item.attrName }}:</span>
                      <span>{{ item.attrValue }}</span>
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column :label="$t('数量')" prop="status" width="120">
                <template slot-scope="scope">
                  <div>{{ scope.row.goodsNum }}</div>
                </template>
              </el-table-column>
              <el-table-column :label="$t('单价')" prop="status" width="120">
                <template slot-scope="scope">
                  <FormatNumberShow :data="scope.row.goodsReal" :currency="true"/>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import {api_order_info_action_post, api_order_listGoods_action_post, tuihuo_list_post} from "@/api/user";
import FormatNumberShow from "@/components/FormatNumberShow/index.vue";

export default {
  name: "table-list",
  components: {FormatNumberShow},
  mounted() {
    this.getAllData();
  },
  data() {
    return {
      form: {
        evaluationType: undefined,
        time: []
      },
      orderInfo: {
        order_no: 123123,
        pay: this.$t('钱包'),
        buy_status: this.$t('已采购'),
        bug_money: 12312,
        get: 123,
        time: "31-10-2022",
        pay_status: this.$t('已支付'),
        goods_status: this.$t('已确定'),
        sale_money: 552,
      },
      currentPage: 0,
      status_options: [
        {
          label: this.$t('全部'),
          value: undefined,
        },
        {
          label: this.$t('申请中'),
          value: "1",
        },
        {
          label: this.$t('成功'),
          value: "2",
        },
        {
          label: this.$t('失败'),
          value: "3",
        },
      ],
      tableData: [],
      detailOrderData: [],

      orderDialogVisible: false,
      userInfo2: {},
      pageNum: 1,
      pageSize: 10,
      totalElements: 0,
    };
  },
  methods: {
    openOrder(row) {
      this.userInfo2 = row;
      api_order_info_action_post({orderId: row.id}).then((e) => {
        console.log(e);
        // this.orders_list_data = e.data
        this.orderInfo = e.data.orderInfo;
      });
      api_order_listGoods_action_post({orderId: row.id}).then((e) => {
        console.log(e);
        // this.orders_list_data = e.data
        // this.orderInfo = e.data.orderInfo
        this.detailOrderData = e.data.pageList
      });
      this.orderDialogVisible = true;
    },
    // TODO: 搜索请求
    search() {
      console.log(this.form);
      this.getAllData();
    },
    // TODO: 重置搜索条件并且请求
    reset() {
      this.form.evaluationType = undefined
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
        returnStatus: this.form.evaluationType
      }
      form["pageNum"] = this.pageNum;
      form["pageSize"] = this.pageSize;
      tuihuo_list_post(form).then(res => {
        this.tableData = res.data.pageList
        this.totalElements = res.data.pageInfo.totalElements
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
    padding: 20px;
    background-color: #fff;
    border-radius: 10px;

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
        font-size: 12px;
        font-weight: 800;

        .name {
          font-weight: 800;
          font-size: 12px;
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
            font-size: 12px;
          }
        }

        .right {
          width: 40%;

          .item {
            display: flex;
            line-height: 30px;
            margin: 10px;
            justify-content: space-between;
            font-size: 12px;
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
        font-size: 12px;
        font-weight: 800;

        .name {
          font-weight: 800;
          font-size: 12px;
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

  &.en {
    width: 100px;
  }
}

::v-deep {
  .date .el-date-editor {
    width: 100%;
  }

  .el-table__row {
    font-size: 12px;
  }
}
</style>
