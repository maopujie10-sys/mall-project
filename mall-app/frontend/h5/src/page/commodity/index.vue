<template>
    <div class="commodity">
        <van-nav-bar safe-area-inset-top fixed :title="$t('商品')" />
        <div style="width: 100%;" class="h46"></div>
        <div style="width: 100%;" class="h46"></div>
        <div style="width: 100%;" class="h56"></div>
        <div class="commodity_header">
            <div class="list_icon" @click="isLeftShow = true">
                <img src="@/assets/image/commodity/saixuan.png" alt="" />
            </div>
            <van-tabs v-model="discount" @change="toggleTabs" :line-height="langIsAr ? 0 : '3px'">
                <van-tab :title="$t('全部商品')"></van-tab>
                <van-tab :title="$t('活动折扣')"></van-tab>
            </van-tabs>
            <div class="search_icon" @click="$router.push('/search?discount=' + discount)">
                <img src="@/assets/image/commodity/sousuo.png" alt="" />
            </div>
        </div>
        <div class="filter-div">
            <div :class="['filter-item', filterIndex == index && 'active']" v-for="(item, index) in filter_list"
                :key="index" @click="selectIndex(item, index)">
                <div>{{ item }}</div>
                <div class="right_icon" v-if="index !== 0 && item">
                    <img v-if="highLow === 1 || filterIndex !== index" :src="filterIcons.icon1" alt="">
                    <img v-if="highLow === 2 && filterIndex === index" :src="filterIcons.icon2" alt="">
                    <img v-if="highLow === 3 && filterIndex === index" :src="filterIcons.icon3" alt="">
                </div>
            </div>
        </div>
        <div class="padd-15">
            <van-skeleton :row="8" class="commodity_skeleton skeleton" :loading="isLoading">
                <van-pull-refresh style="min-height: 100vh" v-model="refreshing" @refresh="onRefresh"
                    :pulling-text="$t('下拉即可刷新')" :loosing-text="$t('释放即可刷新')" :loading-text="$t('加载中')">
                    <van-list v-model="loading" :finished="finished" @load="onLoad" :loading-text="$t('加载中')">
                        <div class="list">
                            <div v-for="(item, index) in list" class="list-item commodity" @click="openDetails(item)"
                                :key="index">
                                <div class="commodity-img">
                                    <img :src="item.imgUrl1 || $defaultGoodsImage" alt="" />
                                </div>
                                <div class="money padd-10">
                                    ${{ priceFormat(item.discountPrice || item.sellingPrice) }}
                                </div>
                                <div class="text padd-10">
                                    {{ $t("卖出") }} {{ priceFormatInt(item.soldNum) }}
                                </div>
                                <!-- <div class="text padd-10">{{$t('浏览量')}} 8464</div> -->
                                <div class="title padd-10 nowrap2">{{ $textOmit(item.name) }}</div>
                                <!-- 活动折扣 -->
                                <div class="discount_box" v-if="item.discountRatio >= 0.01">
                                    <span>{{ (item.discountRatio * 100).toFixed(0) }}%</span>
                                    <span>OFF</span>
                                </div>
                            </div>
                        </div>
                        <van-empty v-if="!list.length" :description="$t('暂无数据')" />
                    </van-list>
                </van-pull-refresh>
            </van-skeleton>
        </div>
        <div style="width: 100%; height: 90px"></div>
        <van-popup :overlay="false" v-model="isLeftShow" position="left">
            <div class="pop-wrap">
                <div class="top"></div>
                <div class="pop-header-wrap">
                    <div class="pop-header-wrap-left">
                        <img src="@/assets/image/commodity/saixuan.png" alt="" />
                        {{ $t("筛选") }}
                    </div>
                    <div class="pop-header-wrap-right" @click="isLeftShow = false">
                        <img src="@/assets/image/commodity/guanbi.png" alt="" />
                    </div>
                </div>
                <!-- <div class="pop-center-wrap">
                    <div class="center-item" v-for="(item, index) in categoryList"
                        :class="[item.categoryId == categoryId ? 'active' : '']" :key="index" @click="selectCategory(item)">
                        {{ item.name }}
                    </div>
                </div> -->
                <div class="pop-center-wrap" id="pop-center">
                    <van-collapse v-model="activeName" accordion>
                        <template v-for="(item, index) of categoryList">
                            <van-collapse-item :title="item.name" :name="index" v-if="item.subList.length">
                                <span v-for="(sub, j) of item.subList" :key="j" @click="selectCategory(item, sub)"
                                    :class="[sub.categoryId == secondaryCategoryId ? 'center-item active2' : 'center-item']">
                                    {{ sub.name || sub.id }}
                                </span>
                            </van-collapse-item>
                            <div class="center-item" v-else @click="selectCategory(item)"
                                :class="[item.categoryId == categoryId ? 'active' : '']">
                                {{ item.name || item.id }}
                            </div>
                        </template>
                    </van-collapse>
                </div>
            </div>
        </van-popup>
        <transition name="fade">
            <van-icon v-show="isShowTopBtn" @click="handleToTop" class="to_top" class-prefix="icon" name="huidaodingbu" />
        </transition>
    </div>
</template>
<script>
import { NavBar, Tab, Tabs, PullRefresh, List, Popup, Skeleton, Empty, Collapse, CollapseItem, Icon } from "vant";
import { apiCategoryTree, home_sellerGoods, home_category } from "@/API/home";
import { priceFormat, deduplication, priceFormatInt } from "@/utils/utis";
export default {
    data() {
        return {
            priceFormatInt,
            itemName: process.env.VUE_APP_ITEM_NAME,
            isShowTopBtn: false,
            activeName: '',
            list: [],
            loading: false,
            finished: false,
            refreshing: false,
            isLeftShow: false,
            screenHight: document.body.clientHeight,
            popupHeight: "100%",
            searchIcon: require("@/assets/image/index/sousuo.png"),
            filterIcons: {
                icon1: require("@/assets/image/shop/1.jpg"),
                icon2: require(`@/assets/${process.env.VUE_APP_ITEM_NAME}/2.jpg`),
                icon3: require(`@/assets/${process.env.VUE_APP_ITEM_NAME}/3.jpg`),
            },
            categoryList: [],
            page_no: 0,
            discount: 0,
            categoryId: "",
            secondaryCategoryId: "",
            scrollValue: "",
            isLoading: true,
            filter_list: [this.$t('综合'), this.$t('销量'), this.$t('价格'), this.$t('新品')],
            filterIndex: 0,
            page_no: 0,
            isPrice: 0,
            newTime: 0,
            isHot: 0,
            actions: [],
            active1: 0,
            active2: 0,
            active3: 0,
            actions1: [{ name: this.$t('价格由高到低'), value: 1 }, { name: this.$t('价格由低到高'), value: 2 }],
            actions2: [{ name: this.$t('销售量由高到低'), value: 1 }, { name: this.$t('销售量由低到高'), value: 2 }],
            actions3: [{ name: this.$t('时间由远到近'), value: 1 }, { name: this.$t('时间由近到远'), value: 2 }],
            shopLoading: true,
            highLow: 1,
            itemName: process.env.VUE_APP_ITEM_NAME,
            mainColor: process.env.VUE_APP_MAIN_COLOR,
        };
    },
    components: {
        [Skeleton.name]: Skeleton,
        [Empty.name]: Empty,
        [NavBar.name]: NavBar,
        [Tab.name]: Tab,
        [Tabs.name]: Tabs,
        [Icon.name]: Icon,
        [List.name]: List,
        [PullRefresh.name]: PullRefresh,
        [Popup.name]: Popup,
        [Collapse.name]: Collapse,
        [CollapseItem.name]: CollapseItem,
    },
    computed: {
        langIsAr() {
            return localStorage.getItem('lang') == 'ar'
        }

    },
    mounted() {
        this.apiCategoryTree();
        window.addEventListener("scroll", () => {
            this.isShowTopBtn = document.documentElement.scrollTop || document.body.scrollTop > 500
        });

    },
    created() {
        const tempObj = JSON.parse(sessionStorage.getItem("commodityState"))

        if (['Argos', 'ArgosShop'].includes(this.itemName)) {
            this.filter_list = ['', this.$t('销量'), this.$t('价格'), ''];
            this.selectIndex({}, 1, 3)
        } else if (this.itemName == 'INT Overstock') {
            this.selectIndex({}, 1, 3)
        } else if (tempObj?.filterIndex) {
            this.filterIndex = tempObj.filterIndex
            this.highLow = tempObj.highLow
            this.selectIndex({}, tempObj.filterIndex, tempObj.highLow)
        } else {
            this.onLoad();
        }


    },
    beforeRouteLeave(to, from, next) {
        if (from.meta.keepAlive) {
            this.scrollValue = window.scrollY;
            localStorage.setItem("position", this.scrollValue);
        }
        next();
    },
    activated() {
        let position = localStorage.getItem("position");

        this.$nextTick(() => {
            //必须使用nextTick（在下次 DOM 更新循环结束之后执行延迟回调）
            if (position !== undefined) {
                window.scroll(0, position);
            }
        });
    },
    methods: {
        priceFormat(num) {
            return priceFormat(num);
        },
        toggleTabs() {
            this.list = [];
            scrollTo(0, 0);
            // sessionStorage.removeItem("commodity_list")
        },
        onRefresh() {
            this.isLoading = true
            // 清空列表数据
            this.finished = false;
            this.page_no = 0;
            // 重新加载数据
            // 将 loading 设置为 true，表示处于加载状态
            // this.loading = true;
            this.onLoad();
        },
        //获取分类
        apiCategoryTree() {
            apiCategoryTree().then((res) => {
                this.categoryList = res
                // .filter(item => {
                //     if (item.name && item.subList.length > 0) {
                //         item.subList = item.subList.filter(subItem => subItem.name);
                //     }
                //     return item.name;
                // });
                this.categoryList.unshift({ name: this.$t('全部商品'), subList: [] })
            });
            // home_category().then((res) => {
            //     this.categoryList = res.pageList
            //     this.categoryList.unshift({ name: this.$t('全部商品'), subList: [] })
            //     this.categoryList.push({name: '', subList: []})
            //     this.categoryList.push({name: '', subList: []})
            // });
        },
        selectCategory(item, sub) {
            this.isLoading = true
            this.page_no = 0;
            this.list = [];
            this.categoryId = item?.categoryId;
            if (sub) this.secondaryCategoryId = sub.categoryId;
            else this.secondaryCategoryId = '';
            this.isLeftShow = false;
            this.onLoad();
            document.body.scrollTop = 0;
            document.documentElement.scrollTop = 0;
        },
        onLoad() {
            this.shopLoading = true
            if (this.refreshing) {
                this.list = [];
                this.refreshing = false;
            }
            this.tuanduimingxi_post()
        },
        tuanduimingxi_post() {
            // if (sessionStorage.getItem('commodity_list') && this.page_no == 0 && this.discount != 1) {
            //     this.list = JSON.parse(sessionStorage.getItem('commodity_list'))
            //     this.shopLoading = this.loading = false;
            //     this.loading = this.isLoading = false;
            // }
            this.page_no++;
            var data = {
                'pageNum': this.page_no,
                'pageSize': 10,
                'categoryId': this.$route.query.categoryId,
                'isPrice': this.isPrice,
                'newTime': this.newTime,
                'isHot': this.isHot,
                discount: this.discount
            };
            !data.categoryId && delete data.categoryId;
            !data.discount && delete data.discount;
            !data.isHot && delete data.isHot;
            !data.isPrice && delete data.isPrice;
            !data.newTime && delete data.newTime;
            if (this.categoryId) {
                data.categoryId = this.categoryId;
            }
            if (this.secondaryCategoryId) {
                data.categoryId = this.secondaryCategoryId;
            }
            home_sellerGoods(data).then((res) => {

                for (let i = 0; i < res.pageList.length; i++) {
                    this.list.push(res.pageList[i]);
                }
                // if (this.page_no == 1 && this.discount != 1) {
                //     sessionStorage.setItem("commodity_list", JSON.stringify(this.list))
                // }
                this.list = deduplication(this.list, 'id');
                this.shopLoading = this.loading = false;
                this.loading = this.isLoading = false;
                if (res.pageList.length == 0) {
                    this.finished = true;
                }

            });
        },
        openDetails(item) {
            document.body.scrollTop = 0;
            document.documentElement.scrollTop = 0;
            this.$router.push("/CommodityDetails?sellerGoodsId=" + item.id);
        },
        selectIndex(item, index, highLow) {
            // sessionStorage.removeItem("commodity_list")
            this.shopLoading = this.isLoading = true
            if (!highLow) {
                if (this.filterIndex === index) {
                    this.highLow = this.highLow === 2 ? 3 : this.highLow === 3 ? 2 : 2
                } else {
                    this.highLow = 2
                }
            } else {
                this.highLow = highLow
            }
            this.filterIndex = index;
            if (index == 1) {
                // this.isPrice = 0
                // this.newTime = ''
                this.actions = this.actions2;
                this.onSelect({ value: this.highLow - 1 })
            } else if (index == 2) {
                this.actions = this.actions1;
                // this.isPrice = 1
                // this.newTime = ''
                this.onSelect({ value: this.highLow - 1 })
            } else if (index == 3) {
                // this.isPrice = 0
                // this.newTime = 'new'
                this.actions = this.actions3;
                this.onSelect({ value: this.highLow - 1 })
            } else {
                this.isPrice = 0
                this.newTime = ''
                this.isPrice = 0;
                this.newTime = 0;
                this.isHot = 0;
                this.page_no = 0;
                this.list = [];
                this.onLoad();
                document.body.scrollTop = 0;
                document.documentElement.scrollTop = 0;
            }

            this.filterIndex = index;
            sessionStorage.setItem("commodityState", JSON.stringify({ filterIndex: this.filterIndex, highLow: this.highLow }))
        },
        onSelect(item) {
            if (this.filterIndex == 1) {
                this.isPrice = 0
                this.isHot = item.value
                this.newTime = 0
                this.actions2.map(info => {
                    info.color = ''
                    if (info.value == item.value) {
                        info.color = this.mainColor
                    }
                })
            } else if (this.filterIndex == 2) {
                this.isPrice = item.value
                this.isHot = 0
                this.newTime = 0
                this.actions1.map(info => {
                    info.color = ''
                    if (info.value == item.value) {
                        info.color = this.mainColor
                    }
                })
            } else {
                this.isPrice = 0
                this.isHot = 0
                this.newTime = item.value
                this.actions3.map(info => {
                    info.color = ''
                    if (info.value == item.value) {
                        info.color = this.mainColor
                    }
                })
            }
            this.page_no = 0
            this.list = []
            this.onLoad();
            document.body.scrollTop = 0
            document.documentElement.scrollTop = 0
        },
        handleToTop() {
            scrollTo({
                top: 0,
                left: 0,
                behavior: 'smooth'
            });
        },
    },
    watch: {
        discount(val) {
            this.page_no = 0;
            this.isLoading = true
            this.onLoad()
        },
        isLeftShow(val) {
            if (val) {
                this.$nextTick(() => {
                    const el = document.getElementById("pop-center");
                    el.style.height = Math.floor(this.screenHight / 23) + "rem";
                });
            }
        },
    }
};
</script>
<style lang="scss" scoped>
html[dir="rtl"] {
    .commodity_header /deep/ .van-tab--active {
        position: relative;

        &::after {
            content: '';
            width: 50px;
            height: 3px;
            background: var(--main-color);
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            border-radius: 2px;
        }
    }
}

:deep(.van-list__finished-text) {
    margin-top: 10px;
}

:deep(.van-cell) {
    background: transparent;
    padding: 18px 16px;

    &:active {
        background-color: transparent;
    }

    .van-cell__title {
        font-size: 12px !important;
    }

    i {
        font-size: 12px;
    }
}

:deep(.van-collapse-item__title--expanded) {

    color: var(--main-color);
}

:deep(.van-collapse-item__content) {
    font-size: 12px !important;
    color: #333333;
    background: transparent !important;
    padding: 0;

    .center-item {
        padding: 0 32px !important;
        width: 100%;
    }
}

.commodity_header {
    position: fixed;
    top: 46px;
    left: 0;
    z-index: 1888;
    // margin-top: 13px;
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 15px 0 15px;
    box-sizing: border-box;
    background: #fff;

    :deep(.van-tabs) {
        // flex: 0 0 220px;
        flex: 1;

        .van-tabs__line {
            width: 90px;
            // background: var(--main-color) !important;
            background: var(--main-color) !important;
        }

    }

    .search_icon,
    .list_icon {
        width: 36px;
        height: 36px;

        img {
            width: 100%;
            height: 100%;
        }
    }

    // .search_icon {
    //     display: flex;
    //     justify-content: center;
    //     align-items: center;
    //     border: 1px solid #F6F6F6;
    //     border-radius: 50%;
    //     img {
    //         width: 12px;
    //         height: 12px;
    //     }
    // }
}

.commodity {
    position: relative;
    background: #fff;
    min-height: 100%;
    font-size: 14px;

    .pw1 {
        width: 375px;
    }

    .padd-15 {
        padding: 0 15px;
        box-sizing: border-box;
    }

    .padd-10 {
        padding: 0 10px;
        box-sizing: border-box;
    }

    .search-wrap {
        display: flex;
        align-items: center;
        position: fixed;
        top: 44px;
        left: 0;
        width: 100%;
        z-index: 1;
        background: #fff;

        .left {
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;

            img {
                width: 36px;
                height: 36px;
            }
        }

        .right {
            flex: 1;

            .van-search .van-cell {
                padding: 8px 8px 8px 0;
            }
        }
    }

    .list {
        margin-top: 15px;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;

        .list-item {
            width: calc(50% - 7px);
            min-height: 260px;
            border: 1px solid #eeeeee;
            margin-bottom: 10px;
            border-radius: 4px;
            position: relative;

            .commodity-img {
                // width: 130px;
                height: 156px;
                // height: 160px;
                padding: 4.8px;
                display: flex;
                justify-content: center;
                align-items: center;

                img {
                    height: fit-content;
                    width: auto;
                    max-height: 100%;
                    max-width: 100%;
                }
            }

            .money {

                color: var(--main-color);
                font-weight: 500;
                font-size: 16px;
                margin-top: 10px;
            }

            .text {
                color: #999999;
                font-size: 12px;
                margin-top: 3px;
            }

            .title {
                min-height: 35px;
                overflow: hidden;
                text-overflow: ellipsis;
                display: -webkit-box;
                -webkit-box-orient: vertical;
                -moz-box-orient: vertical;
                box-orient: vertical;
                -webkit-line-clamp: 2;
                line-clamp: 2;
                margin-top: 4px;
            }
        }

        // .list-item:nth-child(even) {
        //     margin-left: 10px;
        // }
    }

    :deep(.van-popup) {
        scrollbar-width: none;
        -ms-overflow-style: none;
        z-index: 1998 !important;
        overflow: hidden !important;
        height: 100%;

        &::-webkit-scrollbar {
            display: none;
        }
    }

    .pop-wrap {
        box-shadow: 8px 0px 6px -1px rgba(138, 138, 138, 0.16);
        width: 180px;
        // height: 600px;
        height: 87.5vh;
        position: relative;
        top: 50px;
        overflow-y: hidden;
        scrollbar-width: none;
        -ms-overflow-style: none;
        background: #f5f5f7;

        &::-webkit-scrollbar {
            display: none;
        }

        .pop-header-wrap {
            height: 50px;
            width: 165px;
            display: flex;
            align-items: center;
            border-bottom: 1px solid #e6e6e6;
            background: #f5f5f7;
            position: fixed;
            top: 46px;
            left: 0;
            z-index: 1666;

            .pop-header-wrap-left {
                flex: 1;
                color: #333333;
                font-size: 12px;
                display: flex;
                align-items: center;

                img {
                    width: 24px;
                    height: 24px;
                    margin-right: 5px;
                }
            }

            .pop-header-wrap-right {
                display: flex;
                align-items: center;

                img {
                    width: 24px;
                    height: 24px;
                }
            }
        }

        .pop-center-wrap {
            height: 480px;
            transform: translateY(46px);
            overflow-y: auto;

            .center-item {
                display: flex;
                justify-content: flex-start;
                align-items: center;
                height: 45px;
                padding: 0 18px;
                font-size: 12px;
                position: relative;
            }

            .active {
                background: #fff;

                color: var(--main-color);
                // border-left: 2px solid var(--main-color);
                border-left: 2px solid var(--main-color);
            }

            .active2 {
                background: #fff;
                // border-left: 2px solid var(--main-color);
                border-left: 2px solid var(--main-color);
            }
        }
    }
}

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

.filter-div {
    position: fixed;
    top: 96px;
    left: 0;
    z-index: 99;
    width: calc(100% - 28px);
    height: 46px;
    box-sizing: border-box;
    background: #fff;
    margin: 0 14px 0 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    overflow-x: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;

    &::-webkit-scrollbar {
        display: none;
    }

    .right_icon {
        margin-left: 5px;
        transform: translateY(-1px);

        img {
            width: 10px;
            height: 15px;
            vertical-align: middle;
        }
    }

    .filter-item {
        margin-left: 20px;
        font-size: 14px;
        display: flex;
        align-items: center;
        justify-content: center;

        &:first-child {
            margin-left: 0;
        }

        &.active {
            color: var(--main-color);
        }

        div {
            white-space: nowrap;
        }

        // .icons {
        //     display: flex;
        //     flex-direction: column;
        //     justify-content: flex-start;
        //     align-items: center;

        //     .top-icon {
        //         width: 15px;
        //         height: 9px;
        //         margin-left: 3px;
        //     }

        //     .top-icon1 {
        //         margin-top: 5px;
        //     }

        //     .top-bg-icon {
        //         background: url("@/assets/image/shop/top1.png") center no-repeat;
        //         background-size: 100% 100%;
        //     }

        //     .down-bg-icon {
        //         background: url("@/assets/image/shop/top2.png") center no-repeat;
        //         background-size: 100% 100%;
        //     }
        // }
    }
}

/deep/ .van-popup {
    background: transparent !important;
    // top: 50px;
}

/deep/ .van-nav-bar__content {
    height: 50px;
}
</style>

