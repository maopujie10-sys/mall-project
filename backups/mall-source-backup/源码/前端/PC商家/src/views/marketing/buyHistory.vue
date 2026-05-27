<template>
  <div class="merchandise">
    <SetBootSteps/>
    <TableList/>
  </div>
</template>

<script>
import TableList from "./cpn/buyHistoryTableList.vue";
import {zhitongche_lishi_post} from "@/api/user";

export default {
  name: "buyHistory",
  components: {
    TableList,
  },
  data() {
    return {
      data: {}
    };
  },
  mounted() {
    // this.zhitongche_lishi()
  },
  methods: {
    zhitongche_lishi() {
      zhitongche_lishi_post().then(res => {

        this.data = res.data.pageList
      }).catch(function (err) {

      })
    }
  }
};
</script>

<style lang="scss" scoped>
.merchandise {
  background-color: #f0f2f5;
  padding: 20px;
  // height: 100%;
}


::v-deep {
  .el-table__body-wrapper, .el-table__header-wrapper {
    .cell {
      text-align: center;
    }
  }
}
</style>
