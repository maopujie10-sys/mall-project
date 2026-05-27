<template>
  <div class="money">
    <SetBootSteps/>
    <TableList/>
  </div>
</template>

<script>
import TableList from "./cpn/TableList.vue";
import {zijinjilu_post} from "@/api/user";

export default {
  name: "money",
  components: {
    TableList,
  },
  data() {
    return {};
  },
  mounted() {
    // this.zijinjilu_post_get()
  },
  methods: {
    zijinjilu_post_get() {
      zijinjilu_post({}).then((e) => {
        console.log(e)
      })
    }
  }
};
</script>

<style lang="scss" scoped>
.money {
  background-color: #f0f2f5;
  padding: 20px;
  height: 100%;
}


::v-deep {
  .el-table__body-wrapper, .el-table__header-wrapper {
    .cell {
      text-align: center;
    }
  }
}
</style>
