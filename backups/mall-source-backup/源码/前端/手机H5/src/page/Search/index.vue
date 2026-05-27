<template>
    <div class="search-container" style="min-height: 100vh;">
        <van-nav-bar safe-area-inset-top fixed left-arrow :right-text="$t('搜索')" @click-right="searchView"
            @click-left="$router.go(-1)">
            <template #title>
                <van-search v-model="keyword" shape="round" :clearable="false" @input="inputHandle"
                    :placeholder="$t('找货源/商品/供应商/求购')">
                    <template #left-icon>
                        <img :src="searchIcon" alt="" class="search-icon" @click="searchHandle" />
                    </template>
                    <template #right-icon>
                        <van-icon v-if="keyword" name="cross" @click="clearHandle" size="14" color="#333333" />
                    </template>
                </van-search>
            </template>
        </van-nav-bar>

        <div style="width: 100%; height: 44px"></div>

        <div v-if="!tipsShow && !shopShow && !listShow" class="search-history">
            <div class="title">
                <p>{{ $t("历史搜索") }}</p>
                <div v-if="searchHistory1.length" class="clear" @click="emptyHandle">
                    <img :src="clearIcon" alt="" class="search-icon" />
                    <p>{{ $t("清空") }}</p>
                </div>
            </div>
            <div v-if="searchHistory1.length" class="content">
                <div v-for="(item, index) in searchHistory1" :key="index" class="item" @click="tipsHandle(item, false)">
                    {{ item }}
                </div>
            </div>
            <van-empty v-else :description="$t('暂无记录')" />
        </div>

        <div v-if="tipsShow" class="search-tips-content">
            <template v-if="tipsData.length">
                <div v-for="(item, index) in tipsData" :key="index" class="item" @click="tipsHandle(item, item.isShop)">
                    <van-icon v-if="item.isShop" name="shop-o" size="18" />
                    <p>{{ item.name }}</p>
                </div>
            </template>
            <van-empty v-else :description="$t('暂无数据')" />
        </div>

        <div v-if="listShow" class="search-result-content">
            <!-- <van-pull-refresh style="min-height: 100vh" v-model="refreshing" @refresh="onRefresh"
                :pulling-text="$t('下拉即可刷新')" :loosing-text="$t('释放即可刷新')" :loading-text="$t('加载中')"> -->
            <!-- <van-list v-model="loading" :finished="finished" :loading-text="$t('加载中')" :finished-text="listData.length ? $t('没有更多了') : ''"
                    @load="onLoad"> -->
            <div style="padding: 0 15px">
                <goods-content-one :goods-data="listData" />
                <van-empty v-if="!listData.length && !listLoading && !loading" :description="$t('暂无数据')" />
            </div>
            <!-- </van-list> -->
            <!-- </van-pull-refresh> -->
        </div>

        <div v-if="shopShow" class="shop-list-content">
            <div v-if="activeLang === 'en'" class="tips">
                Find {{ shopData.length }} <span>"{{ keyword }}</span>" related stores for you
            </div>
            <div v-else class="tips">
                {{ $t("为您找到") }} <span>"{{ keyword }}</span>" {{ $t("相关的店铺") }} {{ shopData.length || 0 }} {{ $t("家") }}
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
} from "@/API/common";
// import { formatData } from "@/utils/utis";
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
            searchHistory1: [],
        };
    },
    computed: {
        ...mapGetters({
            searchHistory: "searchHistory",
            activeLang: "language",
        }),
    },
    watch: {
        $route(to, from) {
            if (to.path == "CommodityDetails") {
                sessionStorage.setItem("searchList", this.listData);
            }
            if (from.path == "CommodityDetails") {
                this.listData = sessionStorage.getItem("searchList");
            }
        },
    },
    mounted() {
        // console.log("this.$router ->", this.$router);
        this.searchHistory1 =
            JSON.parse(localStorage.getItem("searchHistory1")) || [];
        this.searchHistory1 = [...new Set(this.searchHistory1)];
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
            Toast.loading({
                duration: 0,
                message: this.$t("加载中"),
            });
            if (typeof data == "string") {
                this.keyword = data;
                this.searchHandle();
                return;
            }

            let keyword = String(this.keyword).trim();
            // keyword = keyword.replace(/'/g, "\\'");
            if (isShop) {
                this.shopShow = true;
                this.tipsShow = false;
                this.listShow = false;
                this.searchHistory1.unshift(data.keyword);
                this.searchHistory1 = [...new Set(this.searchHistory1)];
                localStorage.setItem(
                    "searchHistory1",
                    JSON.stringify(this.searchHistory1)
                );
                searchSeller({
                    keyword,
                    isHot: "0",
                    isPrice: "0",
                    isNew: "0",
                }).then((res) => {
                    this.shopData = res.sellerList;
                    Toast.clear();
                });
            } else {
                this.searchHistory1.unshift(data.name);
                this.searchHistory1 = [...new Set(this.searchHistory1)];
                localStorage.setItem(
                    "searchHistory1",
                    JSON.stringify(this.searchHistory1)
                );
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
        }, 1000),
        searchView() {
            if (this.keyword.trim() == "") return this.$notify(this.$t('请输入搜索内容'), "warning");
            Toast.loading({
                duration: 0,
                message: this.$t("加载中"),
            });
            this.listData = []
            this.tipsShow = false;
            this.listShow = true;
            this.shopShow = false;
            this.searchHistory1.unshift(this.keyword.trim());
            this.searchHistory1 = [...new Set(this.searchHistory1)];
            localStorage.setItem(
                "searchHistory1",
                JSON.stringify(this.searchHistory1)
            );
            let keyword = String(this.keyword).trim();
            let lang = localStorage.getItem("lang");
            lang = lang.replace(/"/g, "");
            searchKeyword({ keyword, lang, discount: this.$route.query.discount || 0 })
                .then((res) => {
                    const { pageList, pageInfo } = res;
                    this.listData = pageList;
                    Toast.clear();
                })
        },
        // 搜索商品
        searchHandle() {
            let keyword = String(this.keyword).trim();
            // keyword = keyword.replace(/'/g, "\\'");

            if (keyword == "") {
                this.tipsData = [];
                Toast(this.$t("请输入搜索内容"));
            }
            this.tipsShow = true;
            this.listShow = false;
            this.shopShow = false;
            if (keyword) {
                // this.searchHistory1.unshift(keyword);
                // this.searchHistory1 = [...new Set(this.searchHistory1)];
                // localStorage.setItem(
                //   "searchHistory1",
                //   JSON.stringify(this.searchHistory1)
                // );
                this.tipsData = [];
                let lang = localStorage.getItem("lang");
                lang = lang.replace(/"/g, "");
                searchSeller({ keyword, lang, discount: this.$route.query.discount || 0 })
                    .then((res) => {
                        // const { goodsList, sellerList } = res
                        const { goodsList, pageInfo } = res;
                        //   if (!goodsList.length) {
                        //     Toast(
                        //       `${this.$t("未找到与")}${keyword}${this.$t("相关的商品")}`
                        //     );
                        //   }
                        const shopItem = {
                            keyword,
                            name: `"${keyword}" ${this.$t("相关的店铺")}`,
                            isShop: true,
                        };
                        this.listData = goodsList;
                        this.tipsData = [shopItem, ...goodsList];
                        Toast.clear();
                    })
                    .catch((err) => {
                        // Toast(err.message)
                        Toast.clear();
                    });
            } else {
                this.tipsShow = false;
                this.listShow = false;
                this.shopShow = false;
            }
        },
        emptyHandle() {
            this.$store.dispatch("clearSearchHistory");
            localStorage.removeItem("searchHistory1");
            this.searchHistory1 = [];
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

        >img {
            width: 100%;
            height: auto;
        }
    }

    /deep/ .van-nav-bar__left {
        padding-right: 10px !important;
    }

    /deep/ .van-field__control {
        font-size: 10px;
    }

    /deep/ .van-nav-bar__title {
        width: 100% !important;
        max-width: 66% !important;
        position: relative;
        transform: translateX(-5%);
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

        >.title {
            padding: 25px 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 16px;
            color: #000;

            >.clear {
                display: flex;
                align-items: center;

                >img {
                    width: 14px;
                    height: auto;
                    margin-right: 5px;
                }

                >p {
                    font-size: 12px;
                    color: #333;
                }
            }
        }

        >.content {
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

            >.item {
                float: left;
                padding: 8px 15px;
                background-color: #f6f6f6;
                border-radius: 5px;
                color: #999;
                font-size: 12px;
                margin-right: 14px;
                margin-bottom: 22px;
                max-width: 60px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
        }
    }

    .search-tips-content {
        >.item {
            padding: 23px 15px;
            border-bottom: 1px solid #eee;
            display: flex;
            align-items: center;

            .van-icon {
                margin-right: 5px;
            }

            >p {
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

        >.tips {
            font-size: 12px;
            color: #333;

            >span {

                color: var(--main-color);
            }
        }
    }
}
</style>
