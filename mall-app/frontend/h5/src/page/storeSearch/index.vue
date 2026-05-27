<template>
  <div class="search-container">
    <van-nav-bar safe-area-inset-top
      fixed
      left-arrow
      :right-text="$t('搜索')"
      @click-right="searchHandle"
      @click-left="$router.go(-1)"
    >
      <template #title>
        <van-search
          v-model="keyword"
          shape="round"
          :clearable="false"
          :placeholder="$t('搜索店铺内商品')"
        >
          <template #left-icon>
            <img
              :src="searchIcon"
              alt=""
              class="search-icon"
              @click="inputHandle"
            />
          </template>
          <template #right-icon>
            <van-icon
              v-if="keyword"
              name="cross"
              @click="clearHandle"
              size="14"
              color="#333333"
            />
          </template>
        </van-search>
      </template>
    </van-nav-bar>

    <div style="width: 100%; height: 44px"></div>

    <div v-if="!tipsShow && !shopShow && !listShow" class="search-history">
      <div class="title">
        <p>{{ $t("历史搜索") }}</p>
        <div v-if="searchHistory2.length" class="clear" @click="emptyHandle">
          <img :src="clearIcon" alt="" class="search-icon" />
          <p>{{ $t("清空") }}</p>
        </div>
      </div>
      <div v-if="searchHistory2.length" class="content">
        <div
          v-for="(item, index) in searchHistory2"
          :key="index"
          class="item"
          @click="tipsHandle(item, false)"
        >
          <!-- {{ item.name }} -->
          {{ item }}
        </div>
      </div>
      <van-empty v-else :description="$t('暂无记录')" />
    </div>

    <!-- <div v-if="tipsShow" class="search-tips-content">
            <template v-if="tipsData.length">
                <div v-for="(item, index) in tipsData" :key="index" class="item" @click="tipsHandle(item, item.isShop)">
                    <van-icon v-if="item.isShop" name="shop-o" size="18" />
                    <p>{{ item.name }}</p>
                </div>
            </template>
            <van-empty v-else :description="$t('暂无数据')" />
        </div> -->

    <div v-if="tipsShow" class="search-result-content">
      <van-list v-model="loading" :finished="finished" :loading-text="$t('加载中')" @load="onLoad">
        <div style="padding: 0 15px">
          <goods-content-one :goods-data="tipsData" />
          <van-empty
            v-if="!tipsData.length && !listLoading && !loading"
            :description="$t('暂无数据')"
          />
        </div>
      </van-list>
    </div>
    <van-empty v-if="isEmpty" :description="$t('暂无记录')" />
    <div v-if="shopShow" class="shop-list-content">
      <div v-if="activeLang === 'en'" class="tips">
        Find {{ shopData.length }} <span>"{{ keyword }}</span
        >" related stores for you
      </div>
      <div v-else class="tips">
        {{ $t("为您找到") }} <span>"{{ keyword }}</span
        >" {{ $t("相关的店铺") }} {{ shopData.length || 0 }} {{ $t("家") }}
      </div>
      <shop-content-two :shop-data="shopData"></shop-content-two>
    </div>
  </div>
</template>

<script>
  import { Search, Icon, PullRefresh, List, Empty, Toast } from "vant";
  import GoodsContentOne from "@/components/GoodsContentOne/index.vue";
  import ShopContentTwo from "@/components/ShopContentTwo/index.vue";
  import { mapGetters } from "vuex";
  import debounce from "lodash.debounce";
  import {
    searchKeyword,
    searchKeywordGoods,
    searchSeller,
    apiSearchSellerGoods,
  } from "@/API/common";
  export default {
    name: "Search",
    components: {
      [PullRefresh.name]: PullRefresh,
      [Search.name]: Search,
      [List.name]: List,
      [Icon.name]: Icon,
      [Empty.name]: Empty,
      [Toast.name]: Toast,
      GoodsContentOne,
      ShopContentTwo,
    },
    data() {
      return {
        searchIcon: require("@/assets/image/index/sousuo.png"),
        clearIcon: require("@/assets/image/index/shanchu.png"),
        keyword: "",
        tipsShow: false,
        tipsData: [],
        shopData: [],
        shopShow: false,
        listData: [],
        listShow: false,
        listLoading: false,
        loading: false,
        finished: false,
        refreshing: false,
        pageNum: 1,
        pageSize: 20,
        currentGoodsId: null,
        searchHistory2: [],
        isEmpty: false,
      };
    },
    computed: {
      ...mapGetters({
        searchHistory: "searchHistory",
        activeLang: "language",
      }),
    },
    beforeRouteLeave(to, from, next) {
      from.meta.keepAlive = Boolean(to.name === "CommodityDetails");
      next();
    },
    mounted() {
      this.searchHistory2 =
        JSON.parse(localStorage.getItem(this.$route.query.sellerId)) || [];
      this.searchHistory2 = [...new Set(this.searchHistory2)];
      this.tipsData = [];
    },
    methods: {
      onRefresh() {
        this.finished = false;
        this.pageNum = 1;
        this.loading = true;
        this.onLoad();
      },
      onLoad() {
        if (this.refreshing) {
          this.list = [];
          this.refreshing = false;
        }
        this.getListData();
      },
      getListData() {
        if (this.currentGoodsId) {
          searchKeywordGoods({
            goodsId: this.currentGoodsId,
            pageNum: this.pageNum,
            pageSize: this.pageSize,
          })
            .then((res) => {
              const { pageList } = res;
              this.listData =
                this.pageNum === 1 ? pageList : [...this.listData, ...pageList];
              this.pageNum++;
              this.loading = false;
              if (pageList.length < this.pageSize) {
                this.finished = true;
              }
              this.listLoading = false;
              Toast.clear();
            })
            .catch(() => {
              this.loading = false;
              this.listLoading = false;
              Toast.clear();
            });
        } else {
          this.listLoading = false;
          this.finished = true;
          Toast.clear();
          this.listData = [];
        }
      },
      tipsHandle(data, isShop) {
        if (typeof data == "string") {
          this.keyword = data;
          this.searchHandle();
          return;
        }
        if (isShop) {
          this.shopShow = true;
          this.tipsShow = false;
          this.listShow = false;
          searchSeller({
            keyword: this.keyword,
            isHot: "0",
            isPrice: "0",
            isNew: "0",
          }).then((res) => {
            console.log("res ->", res);
            this.shopData = res.sellerList;
          });
        } else {
          this.listShow = true;
          this.tipsShow = false;
          this.shopShow = false;
          this.keyword = data.name;
          this.currentGoodsId = data.goodsId;
          this.$store.dispatch("setSearchHistory", {
            name: data.name,
            goodsId: data.goodsId,
          });
          Toast.loading({
            duration: 0,
            message: this.$t("加载中"),
          });

          this.pageNum = 1;
          this.finished = false;
          this.loading = true;
          this.listLoading = true;
          this.refreshing = true;
          this.listData = [];
          this.onLoad();
        }
      },
      clearHandle() {
        this.tipsShow = false;
        this.listShow = false;
        this.shopShow = false;
        this.keyword = "";
      },
      inputHandle: debounce(function () {
        this.searchHandle();
      }, 200),
      searchHandle() {
        const keyword = String(this.keyword).trim();
        if (keyword == "") return Toast(this.$t("请输入搜索内容"));
        this.tipsShow = true;
        this.listShow = false;
        this.shopShow = false;
        if (keyword) {
          this.searchHistory2.push(keyword);
          this.searchHistory2 = [...new Set(this.searchHistory2)];
          localStorage.setItem(
            this.$route.query.sellerId,
            JSON.stringify(this.searchHistory2)
          );

          apiSearchSellerGoods({
            keyword,
            sellerId: this.$route.query.sellerId,
          })
            .then((res) => {
              // const { goodsList, sellerList } = res
              const { pageList, pageInfo } = res;
              if (!pageList.length) {
                Toast(
                  `${this.$t("未找到与")}${keyword}${this.$t("相关的商品")}`
                );
                this.isEmpty = true
                return
              }
              this.isEmpty = false
              this.listData = pageList;
              this.tipsData = [...pageList];
            })
            .catch((err) => {
              // Toast(err.message)
            });
        } else {
          this.tipsShow = false;
          this.listShow = false;
          this.shopShow = false;
        }
      },
      emptyHandle() {
        this.$store.dispatch("clearSearchHistory");
        localStorage.removeItem(this.$route.query.sellerId);
        this.searchHistory2 = [];
      },
    },
  };
</script>

<style lang="scss" scoped>
  .search-container {
    /deep/ .van-field__left-icon {
      display: flex;
      align-items: center;
      width: 16px;
      margin-right: 8px;

      > img {
        width: 100%;
        height: auto;
      }
    }

    /deep/ .van-nav-bar__left {
      padding-right: 10px !important;
    }

    /deep/ .van-nav-bar__title {
      width: 100% !important;
      position: relative;
    }

    /deep/ .van-search {
      padding: 0 !important;

      .van-search__content {
        background-color: #f6f6f6;
      }
    }

    .search-btn {
      font-size: 12px;
      color: #333;
    }

    .search-history {
      padding: 0 15px;

      > .title {
        padding: 25px 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 16px;
        color: #000;

        > .clear {
          display: flex;
          align-items: center;

          > img {
            width: 14px;
            height: auto;
            margin-right: 5px;
          }

          > p {
            font-size: 12px;
            color: #333;
          }
        }
      }

      > .content {
        overflow: hidden;
        display: flex;
        flex-wrap: wrap;
        justify-content: flex-start;

        &.no {
          display: flex;
          justify-content: center;
          font-size: 14px;
          color: #999;
        }

        > .item {
          float: left;
          padding: 8px 15px;
          background-color: #f6f6f6;
          border-radius: 5px;
          color: #999;
          font-size: 12px;
          margin-right: 14px;
          margin-bottom: 22px;
          max-width: calc(100vw - 30px);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }
    }

    .search-tips-content {
      > .item {
        padding: 23px 15px;
        border-bottom: 1px solid #eee;
        display: flex;
        align-items: center;

        .van-icon {
          margin-right: 5px;
        }

        > p {
          color: #333;
          font-size: 12px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }
    }

    .shop-list-content {
      padding: 20px 15px;

      > .tips {
        font-size: 12px;
        color: #333;

        > span {
        //   color: var(--main-color);
        color: var(--main-color);
        }
      }
    }
  }
</style>
