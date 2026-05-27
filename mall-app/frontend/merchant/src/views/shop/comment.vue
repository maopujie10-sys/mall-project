<template>
  <div class="merchandise">
    <SetBootSteps/>
    <TableList/>
  </div>
</template>

<script>
import TableList from "./cpn/commenTableList.vue";

export default {
  name: "merchandise",
  components: {
    TableList,
  },
  data() {
    return {};
  },
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

      .ellipsis {
        text-overflow: ellipsis;
        overflow: hidden;
        word-break: break-all;
        display: -webkit-box;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 3;
      }
    }
  }
}
</style>
