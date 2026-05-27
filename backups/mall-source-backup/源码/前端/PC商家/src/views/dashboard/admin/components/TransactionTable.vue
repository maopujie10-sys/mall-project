<template>
  <el-card class="table">
    <div class="text" style="margin-bottom: 12px">{{ $t('热销商品Top10') }}</div>
    <!--      {{ transactionData }}-->
    <el-table :data="transactionData" stripe style="width: 100%;" height="476" size="mini">
      <el-table-column :label="'#'" type="index" width="50" align="center"></el-table-column>
      <el-table-column :label="$t('商品名称')" min-width="200" prop="name">
      </el-table-column>
      <el-table-column :label="$t('价格')" align="center">
        <template slot-scope="{row}">
          <FormatNumberShow :data="row.prizes" :currency="true"/>
        </template>
      </el-table-column>
      <el-table-column :label="$t('销量')" prop="sellCount">
        <template slot-scope="{row}">
          <FormatNumberShow :data="row.sellCount"/>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script>
import {transactionList} from "@/api/remote-search";
import FormatNumberShow from "@/components/FormatNumberShow/index.vue";

export default {
  components: {FormatNumberShow},
  filters: {
    statusFilter(status) {
      const statusMap = {
        success: "success",
        pending: "danger",
      };
      return statusMap[status];
    },
    orderNoFilter(str) {
      return str.substring(0, 30);
    },
  },
  props: {
    transactionData: {
      //类型不匹配会警告
      type: Array,
      default: () => [],
      required: true,
      // 返回值不是 true,会警告
    }
  },
  data() {
    return {
      list: [],
    };
  },
  created() {
    // this.fetchData();
  },
  methods: {
    fetchData() {
      transactionList().then((response) => {
        this.list = response.data?.items || [];
      });
    },
  },
};
</script>

<style lang="scss" scoped>
.table {
  background-color: #fff;
  height: 570px;

  .text {
    font-size: 16px;
    font-weight: 600;
    line-height: 40px;
    margin-left: 10px;
    color: rgb(48, 44, 44);
  }
}
</style>
