<template>
  <div class="commodity">
    <div class="app-container">
      <div class="commodity-wrap flex-start">
        <div class="commodity-content">
          <div class="commodity-content-title flex-start">
            <h2>{{ this.$t("message.home.complex" /**复杂 */) }}</h2>
            <ul class="flex-start">
              <li class="flex-start">
                <span>{{ this.$t("message.home.price" /** 价格*/) }}</span>
                <div class="flex-start">
                  <i class="el-icon-caret-top"></i>
                  <i class="el-icon-caret-bottom"></i>
                </div>
              </li>
              <li class="flex-start">
                <span>{{ $t("message.home.sold") }}</span>
                <div class="flex-start">
                  <i class="el-icon-caret-top"></i>
                  <i class="el-icon-caret-bottom"></i>
                </div>
              </li>
              <li class="flex-start">
                <span>{{ $t("message.home.new") }}</span>
                <div class="flex-start">
                  <i class="el-icon-caret-top"></i>
                  <i class="el-icon-caret-bottom"></i>
                </div>
              </li>
            </ul>
          </div>
          <div>
            <div class="commodity-content-list">
              <EsProductView v-for="(item, index) in testData" :key="index" />
            </div>
            <div class="commodity-content-pagination" v-if="testData.length">
              <el-pagination
                background
                layout="prev, pager, next"
                class="es-pagination"
                :total="1000"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import EsProductView from "@/components/product";
  export default {
    name: "EsStroeCommodity",
    components: { EsProductView },
    data() {
      return {
        testData: new Array(12).fill(""),
      };
    },
  };
</script>

<style lang="scss"></style>
