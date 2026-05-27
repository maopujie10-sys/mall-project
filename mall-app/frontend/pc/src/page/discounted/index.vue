<template>
  <div>
    <EsHeaderView />
    <div class="container-box">
      <div class="app-container">
        <div v-loading="loading" ref="list">
          <div v-if="list.length" class="list">
            <EsProductView v-for="item in list" :key="item.id" :item="item" />
          </div>

          <div v-if="!list.length">
            <el-empty :description="$t('message.home.noData')"></el-empty>
          </div>
          <div class="common-pagination">
            <el-pagination
              v-if="list.length"
              background
              layout="prev, pager, next"
              :page-size="pageSize"
              :current-page="pageNum"
              :total="total"
              @current-change="currentChange"
            />
          </div>
        </div>
      </div>
    </div>
    <EsShopCartView v-if="isLogin" />
    <EsFooterView />
  </div>
</template>

<script>
  import EsProductView from "@/components/product";
  import { RecommendedProductsApi } from "@/api/home";
  export default {
    components: { EsProductView },
    data() {
      return {
        list: [],
        loading: true,
        pageNum: 1,
        isRenew: false,
        pageSize: 18,
        total: 0,
      };
    },
    mounted() {
      this.getDicountedList();
    },
    methods: {
      async getDicountedList() {
        const result = await RecommendedProductsApi({
          discount: 1,
          pageNum: this.pageNum,
          pageSize: this.pageSize,
        });

        this.list = result.data.pageList;
        this.loading = false;
        // if(this.list.length){
          this.$Gsap.from(this.$refs.list,{
            delay: 0.5,
            duration: 1,
            y: '+100',
            autoAlpha: 0,
            ease: "back.out(1.7)"
          })
        // }
        this.total = result.data.pageInfo.totalElements;
      },
      currentChange(page) {
        this.pageNum = page;
        this.loading = true;
        this.getDicountedList();
      },
    },
  };
</script>

<style lang="scss" scoped>
  .container-box {
    min-height: 600px;
    .list {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(188px, 165px));
      grid-column-gap: 14px;
      grid-row-gap: 20px;
      align-content: center;
      padding: 26px 0;
    }
    .common-pagination {
      width: 100%;
      text-align: center;
      padding: 40px 0;
    }
  }
</style>
