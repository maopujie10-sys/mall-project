<template>
  <div class="app-container">
    <SetBootSteps/>
    <el-card>
      <span v-for="(item, index) in items" :class="{'btn-active': From.content_type == item.type}"
            class="button-item"
            @click="handleSelect(item, index)">{{ item.label }}</span>
    </el-card>
    <el-card>
      <PanelGroup :saleInfo="saleInfo"/>
    </el-card>
    <el-card>
      <TableList :data="report_list_action_data" :type="type"/>
      <div style="margin-top: 20px; text-align: center">
        <el-pagination
            :current-page.sync="pageNum"
            :page-size="pageSize"
            :total="totalElements"
            background
            layout="total, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange">
        </el-pagination>
      </div>
    </el-card>
  </div>
</template>

<script>
import PanelGroup from "./cpn/PanelGroup.vue";
import TableList from "./cpn/TableList.vue";
import {report_head_action, report_list_action, seller_info_action_post} from "@/api/user";
import moment from "moment";

export default {
  name: "financial",
  data() {
    return {
      activeName: this.$t('昨日'),
      type: '1',
      items: [
        {type: "2", label: this.$t('昨日')},
        {type: "1", label: this.$t('今日')},
        {type: "3", label: this.$t('本周')},
        {type: "4", label: this.$t('本月')},
        {type: "5", label: this.$t('全部')},
      ],
      saleInfo: {
        n1: 0,
        n2: 0,
        n3: 0,
        n4: 0,
        n5: 0,
        n6: 0
      },
      From: {
        pageNum: 1,
        pageSiz: 10,
        content_type: 1
      },
      report_head_action_data: {},
      report_list_action_data: [],
      info: {},
      pageNum: 1,
      pageSize: 10,
      totalElements: 0,
    };
  },
  components: {
    PanelGroup,
    TableList,
  },
  mounted() {
    // this.report_head_action_post()
    this.seller_info_action()
  },
  methods: {
    seller_info_action() {
      seller_info_action_post({}).then((e) => {
        console.log(e)
        this.info = e.data
        this.report_list_action_post()
        this.report_head_action_post()
      }).catch((e) => {
      })
    },
    // TODO: 选择范围，去获取处理其他数据
    handleSelect(item, index) {
      // this.items.forEach((tag, i) => {
      //   if (i === index) {
      //     this.type = this.items[i].label;
      //     this.$set(this.items[i], "type", "");
      //   } else {
      //     this.$set(this.items[i], "type", "info");
      //   }
      // });
      this.activeName = this.items[index].label
      this.From.content_type = item.type
      this.pageNum = 1
      this.report_list_action_post()
      this.report_head_action_post()
    },
    report_head_action_post() {
      report_head_action({sellerId: this.info.id, content_type: this.From.content_type}).then((e) => {
        console.log(e)
        this.report_head_action_data = e.data.head
        this.saleInfo.n1 = e.data.head.willIncome
        this.saleInfo.n2 = e.data.head.totalSales
        this.saleInfo.n3 = e.data.head.totalProfit
        this.saleInfo.n4 = e.data.head.orderNum
        this.saleInfo.n5 = e.data.head.orderCancel
        this.saleInfo.n6 = e.data.head.orderReturns
      })
    },
    // TODO: 每页几条,去请求获取数据
    handleSizeChange(val) {
      console.log(`每页 ${val} 条`);

      this.report_list_action_post();
    },
    // TODO: 当前第几页,去请求获取数据
    handleCurrentChange(val) {
      console.log(`当前页: ${val}`);
      this.report_list_action_post();
    },
    report_list_action_post() {
      this.From['sellerId'] = this.info.id
      this.From["pageNum"] = this.pageNum;
      this.From["pageSize"] = this.pageSize;
      report_list_action(this.From).then((e) => {
        this.report_list_action_data = e.data.pageList.sort((a, b) => {
          let dif = moment(a.dayString, 'YYYY-MM-DD').valueOf() - moment(b.dayString, 'YYYY-MM-DD').valueOf()
          return -dif
        })
        this.totalElements = e.data.pageInfo.totalElements
      })
    }
  },
};
</script>

<style lang="scss" scoped>
.financial {
  background-color: #f0f2f5;
  padding: 0 20px 20px 20px;
  height: 100%;
  padding-top: 20px;

  &-tag {
    width: 100%;
    background-color: #fff;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 10px;
  }
}

::v-deep {
  .el-table__body-wrapper, .el-table__header-wrapper {
    .cell {
      text-align: center;
    }
  }
}

.button-item {
  cursor: pointer;
}
</style>
