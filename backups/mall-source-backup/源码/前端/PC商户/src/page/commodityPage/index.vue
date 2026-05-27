<template>
  <div class="commodity">
    <EsHeaderView />
    <div class="app-container app-center">
      <div class="commodity-wrap flex-start">
        <EsFilterView @filterChange="filterChange" />
        <div class="commodity-content">
          <EsSortView @sort="sortEvent" :isRenew="isRenew" />
          <div v-loading="loading">
            <div class="commodity-content-list" ref="activeScoll">
              <EsProductView
                v-for="(item, index) in sellerGoodsList"
                :key="index"
                :item="item"
              />
            </div>
            <div class="no-data" v-if="!sellerGoodsList.length">
              <el-empty :description="$t('message.home.noData')"></el-empty>
            </div>
            <div class="common-pagination" v-if="sellerGoodsList.length">
              <el-pagination
                background
                class="es-pagination"
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
    </div>
    <EsFooterView />
  </div>
</template>

<script>
import EsProductView from "@/components/product";
import EsFilterView from "./filter.vue";
import EsSortView from "./sort.vue";
// import { isEmpty } from "lodash";
import { mapActions, mapGetters } from "vuex";

export default {
  name: "EsCommodity",
  components: { EsProductView, EsSortView, EsFilterView },
  data() {
    return {
      loading: false,
      pageNum: 1,
      isRenew: false,
      pageSize: 20,
      total: 0,
      beforeSortParams: {},
      sort: [],
      scrollTop: 0,
    };
  },
  computed: {
    ...mapGetters("home", ["sellerGoodsList", "categoryList"]),
  },
  activated() {
    // this.requestCategoryList();
    this.requestData();
    // console.log('2 ->', 2);
  },
  // watch: {
  //   $route(to, from) {
  //     console.log('to ->', to);
  //     console.log('from ->', from);
  //     if(to.path == '/commodity'){
  //       window.scrollTo(0, 111);
  //     }
  //     // this.windowScroll();

  //           // window.scrollTo(0, this.scrollTop);
  //   },
  // },
  methods: {
    ...mapActions("home", ["requestSellerGoodsList", "requestCategoryList"]),
    changeFilter(item, index) {
      this.currentFilterValue = index;
    },
    changepage() {
      this.pageNum = 1;
      this.requestData();
    },
    async requestData(params = {}) {
      try {
        const currentRouter = this.$router.currentRoute;
        const categoryId = currentRouter.query.id || params.categoryId;

        if (!categoryId && this.beforeSortParams) {
          this.loading = true;
          await this.requestSellerGoodsList({
            pageNum: this.pageNum,
            pageSize: this.pageSize,
            ...this.beforeSortParams,
          }).then((res) => {
            this.total = res.pageInfo.totalElements;
            if (this.sellerGoodsList.length) {
              this.$Gsap.fromTo(this.$refs.activeScoll, {
                delay: 0,
                duration: 1.5,
                y: "100",
                autoAlpha: 0,
                ease: "back.out(1.7)",
              },{
                delay: 0,
                duration: 1,
                y: "0",
                autoAlpha: 1,
                ease: "back.out(1.7)",
              }
              );
            }
          });
        } else {
          const sortParams = Object.prototype.hasOwnProperty.call(
            params,
            "categoryId"
          )
            ? this.beforeSortParams
            : {};
          this.loading = true;

          await this.requestSellerGoodsList({
            ...sortParams,
            ...params,
            categoryId,
            pageNum: this.pageNum,
            pageSize: this.pageSize,
          }).then((res) => {
            this.total = res.pageInfo.totalElements;
           if (this.sellerGoodsList.length) {
              this.$Gsap.fromTo(this.$refs.activeScoll, {
               delay: 0,
                duration: 1.5,
                y: "100",
                autoAlpha: 0,
                ease: "back.out(1.7)",
              },{
                delay: 0,
                duration: 1,
                y: "0",
                autoAlpha: 1,
                ease: "back.out(1.7)",
              });
            }
          });
        }
      } finally {
        this.loading = false;
      }
    },
    currentChange(page) {
      this.pageNum = page;
      document.documentElement.scrollTop = 0;
      this.requestData(this.sort);
    },
    filterChange(categoryId) {
      this.requestData({ categoryId });
      this.isRenew = true;
    },
    sortEvent(data) {
      console.log("data ->", data);
      this.sort = data;
      this.pageNum = 1;
      this.beforeSortParams = data;
      this.requestData(data);
    },
  },
};
</script>

<style lang="scss">
.commodity {
  &-wrap {
    align-items: flex-start;
    margin-top: -13px !important;

    ul {
      list-style: none;
      margin: 0;
      padding: 0;
    }
  }

  .commodity-wrap {
    min-height: calc(100vh - 361.5px);
  }

  &-filter {
    width: 180px;
    border-right: 1px solid var(--color-border);

    h2 {
      width: 100%;
      // text-align: center;
      font-weight: 600;
      font-size: 16px;
      color: var(--color-title);
      border-bottom: 1px solid var(--color-border);
      padding: 20px 0;
      margin-bottom: 20px;
    }

    &-item {
      // text-align: center;
      width: 100%;
      font-weight: 400;
      font-size: 14px;
      color: var(--color-black);
      padding: 12px 0;
      cursor: pointer;

      &:hover {
        color: var(--color-main);
        border-right: 2px solid var(--color-main);
      }

      &-active {
        color: var(--color-main);
        border-right: 2px solid var(--color-main);
      }
    }
  }

  &-content {
    width: 100%;

    &-list {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(186px, 165px));
      grid-column-gap: 11px;
      grid-row-gap: 20px;
      align-content: center;
      padding: 22px 28px;
    }

    &-pagination {
      width: 100%;
      text-align: center;
      padding: 40px 0;
    }
  }
  .no-data {
    display: flex;
    justify-content: center;
  }
}
</style>
