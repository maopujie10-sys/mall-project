<template>
  <div class="commodity">
    <div class="app-container">
      <div class="commodity-wrap flex-start">
        <div class="commodity-filter">
          <h2>{{ this.$t("message.home.classification" /**分类 */) }}</h2>
          <ul>
            <li
        :class="{
          'commodity-filter-item': true,
          'commodity-filter-item-active': currentFilterValue === 'explme',
        }"
        class="first-item"
        @click="changeFilter('explme', 'explme')"
       
      >{{ $t("message.home.AllProducts") }}
      
      </li>
            <li
              v-for="(item, index) in category"
              :key="index"
              :class="{
                'commodity-filter-item': true,
                'commodity-filter-item-active': currentFilterValue === index,
              }"
              @click="changeFilter(item, index)"
            >
              <div class="list" @click="openList = !openList">
                {{ item.name }}
                <i
                  :class="
                    openList &&parCategoryId == item.categoryId ? 'el-icon-arrow-down' : 'el-icon-arrow-right'
                  "
                  v-if="item.subList.length"
                ></i>
              </div>
              <div class="list-item" v-if="openList && parCategoryId == item.categoryId">
                <ul v-if="item.subList.length">
                  <li
                    v-for="(subItem, subIndex) in item.subList"
                    :key="subIndex"
                    @click.stop="changeFilter(item, subIndex, subItem)"
                    :class="subItem.categoryId == categoryId ? 'active' : ''"
                  >
                    {{ subItem.name }}
                  </li>
                </ul>
              </div>
            </li>
          </ul>
        </div>
        <div class="commodity-content">
          <EsSortView
            :search-show="true"
            @sort="sortEvent"
            @search="searchHandle"
            ref="sortView"
          />
          <div>
            <div ref="commodityList">
              <EsLoadingView :loading="loading" >
              <div class="commodity-content-list">
                <EsProductView
                  v-for="(item, index) in merchantGoodsList"
                  :key="index"
                  :item="item"
                />
              </div>
              <div class="no-data" v-if="!merchantGoodsList.length">
                <el-empty :description="$t('message.home.noData')"></el-empty>
              </div>
            </EsLoadingView>
            </div>
            <div
              class="commodity-content-pagination"
              v-if="merchantGoodsList.length"
            >
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
  </div>
</template>

<script>
import EsProductView from "@/components/product";
import { mapActions, mapGetters } from "vuex";
import EsSortView from "@/page/commodityPage/sort.vue";
// import { CategoryApiList } from "@/api/home";
import { SellerClass } from "@/api/productDetails";
import { searchSellerGoods } from "@/api/home";
export default {
  name: "EsStroeSort",
  components: { EsProductView, EsSortView },
  data() {
    return {
      currentFilterValue: 'explme',
      loading: false,
      pageNum: 1,
      pageSize: 20,
      total: 0,
      currentParams: {},
      beforeSortParams: {},
      category: [],
      openList: false,
      categoryId: "",
      parCategoryId: "",
      itemname: process.env.VUE_APP_ITEM_NAME,
      // itemname: 
    };
  },
  computed: {
    ...mapGetters("home", ["merchantGoodsList", "categoryList"]),
  },
  mounted() {
    // this.requestCategoryList();
  if(this.itemname!=='Argos'||itemname !== 'ArgosShop'){
    this.requestData();
  }
    this.getCategoryList();

  },
  activated() {
    const params = JSON.parse(localStorage.getItem("sortParams"));
    const CategoryId = JSON.parse(localStorage.getItem("sortCategoryId"));
    // console.log("CategoryId ->", CategoryId);
    
    this.getCategoryList();
    if (CategoryId) {
      this.requestData({ categoryId: CategoryId });
    }
    this.sortEvent(params);
  },
  watch: {
    "$route.query.id": {
      handler(val) {
        // this.requestCategoryList();
        this.requestData();
      },
      deep: true,
    },
  },
  methods: {
    ...mapActions("home", [
      "requestMerchantGoodsList",
      // "requestCategoryList",
      "updateMerchantGoodsListHandle",
    ]),
    async getCategoryList() {
      const res = await SellerClass({
        sellerId: this.$router.currentRoute.query.storeId,
      });
      this.category = res.data.filter((item) => {
        if (item.name && item.subList.length > 0) {
          item.subList = item.subList.filter((subItem) => subItem.name);
        }
        return item.name;
      });
      // this.category = res.data;
      console.log('this.category ->', res.data);
    },
    searchHandle(keyword) {
      console.log(
        "this.$router.currentRoute.query.id ->",
        this.$router.currentRoute.query.storeId
      );
      if (keyword) {
        this.loading = true;
        searchSellerGoods({
          sellerId: this.$router.currentRoute.query.storeId,
          keyword,
        })
          .then((res) => {
            this.updateMerchantGoodsListHandle(res.data);
            this.loading = false;
          })
          .catch(() => {
            this.loading = false;
          });
      } else {
        this.pageNum = 1;
        this.requestData();
      }
    },
    // async getCategoryList() {
    //   let res = [];
    //   res = await SellerClass({
    //     sellerId: this.$router.currentRoute.query.storeId,
    //   });
    //   const all = [{ name: this.$t("message.home.all"), categoryId: "" }];
    //   this.category = [...all, ...res.data];
    // },
    async requestData(params = {}) {
      const currentRouter = this.$router.currentRoute;
      try {
        this.loading = true;
        const sortParams = Object.prototype.hasOwnProperty.call(
          params,
          "categoryId"
        )
          ? this.beforeSortParams
          : {};
        const qureyParams = JSON.parse(
          JSON.stringify({
            ...{
              sellerId: currentRouter.query.storeId,
              pageNum: this.pageNum,
              pageSize: this.pageSize,
            },
            ...sortParams,
            ...this.currentParams,
            ...params,
          })
        );
        for (const key in qureyParams) {
          if (!qureyParams[key]) {
            delete qureyParams[key];
          }
        }
        await this.requestMerchantGoodsList({
          ...qureyParams,
        }).then((res) => {
          this.total = res.pageInfo.totalElements;
        });
      } finally {
        this.loading = false;
       this.$Gsap.fromTo(this.$refs.commodityList, {
              delay: 0,
              duration:.5,
              y: '100',
              autoAlpha: 0,
              ease: "back.out(1.7)"
            },{
              delay: 0.5,
              duration: 1,
              y: '0',
              autoAlpha: 1,
              ease: "back.out(1.7)"
            })
      }
    },
    changeFilter(item, index, subItem) {
      this.$refs.sortView.searchKey=''
      // console.log('this.$refs.sortView ->', );
      this.categoryId = ''
      if (subItem) {
        this.categoryId = subItem.categoryId;
        this.currentParams = {
          ...this.currentParams,
          ...{ categoryId: subItem.categoryId },
        };
        localStorage.setItem(
          "sortCategoryId",
          JSON.stringify(subItem.categoryId)
        );
        this.requestData({ categoryId: subItem.categoryId });
      } else {
        this.currentFilterValue = index;
        this.parCategoryId = item.categoryId;
        this.currentParams = {
          ...this.currentParams,
          ...{ categoryId: item.categoryId },
        };
        localStorage.setItem("sortCategoryId", JSON.stringify(item.categoryId));
        this.requestData({ categoryId: item.categoryId });
      }
      // this.currentFilterValue = index;
    },
    currentChange(page) {
      this.pageNum = page;
      window.scrollTo(0, 0);
      this.requestData();
    },
    sortEvent(params) {
      console.log("params ->", params);
      localStorage.setItem("sortParams", JSON.stringify(params));
      this.pageNum = 1;
      this.beforeSortParams = params;
      this.requestData(params);
    },
  },
};
</script>

<style lang="scss">
html[dir="rtl"]{
  .first-item{
    text-align: right;
  }
}
.sort-active {
  color: var(--color-main);
}
.first-item{
 text-align: left;
}
.list {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.list-item {
  li {
    text-indent: 10px;
    padding: 5px 0;
    text-align: left;
    color: var(--color-black) !important;
    &:nth-child(1){
      margin-top: 15px;
    }
    &:hover {
      color: var(--color-main) !important;
      // border-right: 2px solid var(--color-main);
    }
    &.active {
      color: var(--color-main) !important;
      // border-right: 2px solid var(--color-main);
    }
  }
}
.sort-icon {
  height: 10px;
  position: relative;
  width: 14px;

  i {
    color: #d9d9d9;
    position: absolute;
  }

  .sort-active {
    color: var(--color-main);
  }
}
.sort-icon-up {
  i {
    bottom: 4px;
  }
}
.sort-icon-down {
  i {
    top: -4px;
  }
}
</style>
