<template>
  <div class="filter commodity-filter">
    <h2>{{ this.$t("message.home.classification" /**分类 */) }}</h2>
    <ul>
      <li
        :class="{
          'commodity-filter-item': true,
          'commodity-filter-item-active': currentFilterValue === 'explme',
        }"
        class="first-item"
        @click="changeFilter('explme', 'explme')"
      >
        {{ $t("message.home.AllProducts") }}
      </li>
      <li
        v-for="(item, index) in categoryList"
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
              openList && parCategoryId == item.categoryId
                ? 'el-icon-arrow-down'
                : 'el-icon-arrow-right'
            "
            v-if="item.subList.length"
            style="margin-left: 5px"
          ></i>
        </div>
        <div
          class="list-item"
          v-if="openList && parCategoryId == item.categoryId"
        >
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
</template>

<script>
import { mapActions, mapGetters } from "vuex";
import { CategoryApiList } from "@/api/home";
export default {
  name: "EsFilter",
  data() {
    return {
      currentFilterValue: "",
      categoryList: [],
      openList: false,
      categoryId: "",
      parCategoryId: "",
      scrollTop: 0,
    };
  },
  computed: {
    // ...mapGetters("home", ["categoryList"]),
  },
  activated() {
    this.getCategoryList();
    const currentRouter = this.$router.currentRoute;
    window.addEventListener("scroll", this.windowScroll);
    setTimeout(() => {
      if (this.categoryList.length) {
        if(currentRouter.query.parentId){
          console.log('parentId ->', currentRouter.query.parentId);
          const index = this.categoryList.findIndex(
            (item) => item.categoryId === currentRouter.query.parentId
          );
            this.currentFilterValue = index;
            this.parCategoryId = currentRouter.query.parentId;
            this.categoryId = currentRouter.query.id;
            this.openList = true
          
        } else if (currentRouter.query.id) {
          this.openList = false
          localStorage.setItem("category_id", currentRouter.query.id);
          this.$emit(
            "filterChange",
            this.categoryList.find(
              (item) => item.categoryId === currentRouter.query.id
            ).categoryId
          );
          const index = this.categoryList.findIndex(
            (item) => item.categoryId === currentRouter.query.id
          );
          if (index) {
            this.currentFilterValue = index;
          }
        } else {
          this.currentFilterValue = "explme";
        }
      }
    }, 1000);
  },
  created() {
    // EventBus.$on("sort", (data) => {
    //   console.log("data ->", data);
    // });
  },
  methods: {
    ...mapActions("home", ["requestCategoryList"]),

// windowScroll() {
//     this.scrollTop =
//     window.pageYOffset ||
//     document.documentElement.scrollTop ||
//     document.body.scrollTop
//     console.log(this.scrollTop)
// },
    async getCategoryList() {
      const res = await CategoryApiList();
      // this.categoryList = res.data.filter((item) => {
      //   if (item.name && item.subList.length > 0) {
      //     item.subList = item.subList.filter((subItem) => subItem.name);
      //   }
      //   return item.name;
      // });
      // console.log("this.categoryList ->", this.categoryList);
      this.categoryList = res.data;
      // console.log("res ->", this.categoryList);
    },
    changeFilter(item, index, subItem) {
      const currentRouter = this.$router.currentRoute;
      sessionStorage.setItem("CommodityScrollTop", this.scrollTop);
      this.categoryId = "";
      if (subItem) {
        this.categoryId = subItem.categoryId;
        if (currentRouter.query.id !== subItem.categoryId) {
          this.$router.replace({
            path: "/commodity",
            query: { id: subItem.categoryId },
          });

          localStorage.setItem("category_id", item.categoryId);
        }
      } else {
        this.parCategoryId = item.categoryId;
        this.currentFilterValue = index;
        if (currentRouter.query.id !== item.categoryId) {
          this.$router.replace({
            path: "/commodity",
            query: { id: item.categoryId },
          });

          localStorage.setItem("category_id", item.categoryId);
        }
      }

      /**
       * 防止刷新掉目录参数
       */
      this.$parent.changepage()
      this.$emit("filterChange", item.categoryId);
    },
  },
};
</script>

<style lang="scss">
html[dir="rtl"]{
  .first-item{
    text-align: right;
  } 
  .commodity-filter h2{
    text-align: center;
  }
}
.commodity-filter {
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
  .first-item{
    text-align: left;font-size: 14px;
  }
  &-item {
    // text-align: center;
    width: 100%;
    font-weight: 400;
    font-size: 12px;
    color: var(--color-black);
    padding: 20px 0;
    cursor: pointer;
    &:hover {
      color: var(--color-main);
      border-right: 2px solid var(--color-main);
    }
    &-active {
      color: var(--color-main);
      border-right: 2px solid var(--color-main);
    }
    .list {
      display: flex;
      // justify-content: space-between;
      align-items: center;
    }
    .list-item {
      margin-top: 15px;
      li {
        text-indent: 10px;
        font-size: 12px;
        padding: 5px 0;
        color: var(--color-black) !important;
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
  }
}
</style>
