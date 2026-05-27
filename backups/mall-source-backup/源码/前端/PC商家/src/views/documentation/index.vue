<template>
  <div class="app-container">
    <SetBootSteps/>
    <el-card>
      <el-button v-for="(item, index) in allTabs" :key="index" :type="type === item.type?'primary':''"
                 @click="handleClick(index)">{{ item.tabName }}
      </el-button>
    </el-card>
    <el-card>
      <TableList :data="orders_list_data" :type="type" @showCityName="qingchu" @sousuo="sousuo2"/>
      <div style="margin-top: 20px; text-align: center">
        <el-pagination :current-page="pageNum" :page-size="pageSize" :page-sizes="[10, 20, 50, 100]"
                       :total="totalElements" background layout="total, sizes, prev, pager, next, jumper"
                       @size-change="handleSizeChange" @current-change="handleCurrentChange">
        </el-pagination>
      </div>
    </el-card>
  </div>
</template>

<script>
import TableList from "./cpn/TableList.vue";
import {orders_list, seller_info_action_post} from "@/api/user";
import {formatDate} from '@/filters/index'

export default {
  name: "order",
  components: {
    TableList,
  },
  data() {
    return {
      activeName: this.$t('全部订单'),
      type: undefined,
      allTabs: [
        {
          tabName: this.$t('全部订单'),
          number: 1000,
          type: undefined,
        },
        {
          tabName: this.$t('待采购'),
          number: 1000,
          type: 0,
        },
        {
          tabName: this.$t('已采购'),
          number: 1000,
          type: 1,
        },
      ],
      orders_list_data: {},
      pageNum: 1,
      pageSize: 10,
      totalElements: 0,
      form: {},
      info: ""//用户信息
    };
  },
  created() {
    seller_info_action_post({}).then((e) => {
      this.info = e.data;
      this.orders_list_post();
    }).catch((e) => {
    })
  },
  methods: {
    // TODO: 每页几条,去请求获取数据
    handleSizeChange(val) {
      this.pageSize = val;
      this.orders_list_post();
    },
    // TODO: 当前第几页,去请求获取数据
    handleCurrentChange(val) {
      this.pageNum = val;
      this.orders_list_post();
    },
    formatDate,
    sousuo2(e) {
      this.form = {
        payStatus: e.order_status,
        status: e.goods_status,
        begin: this.formatDate(e.time && e.time[0]),
        end: this.formatDate(e.time && e.time[1])
      };
      if (e.order_no) {
        this.form.orderId = e.order_no
      }
      this.orders_list_post();
    },
    qingchu(e) {
      this.form = {
        payStatus: e.order_status,
        status: e.goods_status,
        begin: this.formatDate(e.time && e.time[0]),
        end: this.formatDate(e.time && e.time[1])
      };
      if (e.order_no) {
        this.form.orderId = e.order_no
      }
      this.orders_list_post();
    },
    handleClick(index) {
      this.activeName = this.allTabs[index].tabName;
      this.type = this.allTabs[index].type;
      this.pageNum = 1
      this.orders_list_post();
    },
    orders_list_post() {
      var data = this.form;
      data["sellerId"] = this.info.id;
      data["pageNum"] = this.pageNum;
      data["pageSize"] = this.pageSize;
      data["purchStatus"] = this.type;
      orders_list(data).then((e) => {
        this.orders_list_data = e.data;
        this.totalElements = e.data.pageInfo.totalElements
      });
    },
  },
};
</script>

<style lang="scss" scoped>
.order {
  background-color: #f0f2f5;
  padding-top: 20px;

  ::v-deep .is-top {
    background-color: #fff;
  }
}
</style>
