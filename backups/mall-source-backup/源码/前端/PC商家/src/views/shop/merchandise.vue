<template>
  <div class="merchandise">
    <SetBootSteps/>
    <TableList/>
  </div>
</template>

<script>
import TableList from "./cpn/merchandiseTableList.vue";
import {seller_goods_list_action_post} from "@/api/user";

export default {
  name: "merchandise",
  components: {
    TableList,
  },
  data() {
    return {};
  },
  mounted() {
    // this.seller_goods_list_action()
    // this.getCategory()
  },
  methods: {
    // 获取商品列表
    seller_goods_list_action() {
      seller_goods_list_action_post({}).then((e) => {
        console.log(e)
        // this.promotional = e.data
      })
    },

  }
};
</script>

<style lang="scss" scoped>
.merchandise {
  background-color: #f0f2f5;
  padding: 20px;
  // height: 100%;
}
</style>
