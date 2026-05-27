<template>
  <div class="merchandise">
    <SetBootSteps/>
    <TableList/>
  </div>
</template>

<script>
import TableList from "./cpn/libraryTableList.vue";

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
    }
  }

  .el-image {
    max-width: 120px;
    max-height: 120px;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }
}
</style>
