<template>
    <div class="shop">
        <van-nav-bar safe-area-inset-top fixed class="nav-bar" left-arrow @click-left="onClickLeft">
            <!-- <div slot="title" class="tab-wrap">
                <router-link :to="'/store/search?sellerId=' + $route.query.sellerId">
                    <van-search shape="round" readonly background="#4fc08d" :placeholder="$t('搜索店铺内商品')">
                        <template #left-icon>
                            <img :src="searchIcon" alt="" class="search-icon" />
                        </template>
                    </van-search>
                </router-link>
            </div> -->
            <template #right v-if="itemName == 'EShop'">
                <van-popover v-model="showPopover" :actions="actions123" placement="bottom-end" @select="handleSelect">
                    <template #reference>
                        <img @click="showPopover = !showPopover" src="@/assets/image/shop/more.png" alt="">
                    </template>
                </van-popover>
            </template>
        </van-nav-bar>
        <!-- <div class="shop-header" :style="{ background: `url(${shopBg}) center no-repeat !important;` }"> -->
        <div class="shop-header" :style="!banner[0] && { background: `url(${shopBg}) no-repeat center / 100% 100%` }">
            <div class="shop-top">
                <div class="shop-info">
                    <div class="shop-info-left">
                        <div class="shop-avatar">
                            <van-skeleton :row="1" class="avatar_picture skeleton" :loading="shopLoading.avatar">
                                <img :src="SellerInfo?.avatar" />
                            </van-skeleton>
                        </div>
                    </div>
                    <div class="shop-info-right">
                        <van-skeleton :row="1" title class="skeleton" :loading="shopLoading.avatar">
                            <p class="title">{{ SellerInfo?.name }}</p>
                            <p class="text nowrap2">{{ $textOmit(SellerInfo?.shopRemark, 40) }}</p>
                        </van-skeleton>

                        <div class="logos">
                            <img v-if="SellerInfo?.facebook" @click="openUrl(SellerInfo?.facebook, 'facebook')"
                                src="@/assets/image/shop/facbook.png" />
                            <img v-if="SellerInfo?.twitter" @click="openUrl(SellerInfo?.twitter, 'twitter')"
                                src="@/assets/image/shop/twitter.png" />
                            <img v-if="SellerInfo?.google" @click="openUrl(SellerInfo?.google, 'google')"
                                src="@/assets/image/shop/google.png" />
                            <img v-if="SellerInfo?.youtube" @click="openUrl(SellerInfo?.youtube, 'youtube')"
                                src="@/assets/image/shop/youtuob.png" />
                            <img v-if="SellerInfo?.instagram" @click="openUrl(SellerInfo?.instagram, 'instagram')"
                                src="@/assets/image/shop/ins.png" />
                        </div>
                    </div>
                </div>
                <div class="shop-followed" @click="addFocusSeller">
                    <img class="starbai" src="@/assets/image/shop/starC.png" v-if="this.SellerInfo?.isFocus == 1" />
                    <img class="starbai" src="@/assets/image/shop/Starbai.png" v-else />
                    <div>{{ $t(collectTitle) }}</div>
                </div>
            </div>
            <div class="shop-bottom">
                <div slot="title" class="tab-wrap">
                    <!-- <div class="tab-item" @click="handleChange(index)" :class="[tab_index === index ? 'active' : '']"
                        v-for="(item, index) in tab_nav_list" :key="index">
                        {{ item }}
                    </div> -->
                    <van-tabs v-model:active="tab_index" @change="handleChange" :line-height="langIsAr ? 0 : '3px'">
                        <van-tab v-for="(item, index) in tab_nav_list" :key="index" :title="item"></van-tab>
                    </van-tabs>
                </div>
                <div style="height: 48px"></div>
                <!-- Recommend -->
            </div>
            <div class="top-banner-div">
                <van-swipe class="my-swipe" style="border-radius: 4px; direction: ltr;" :autoplay="autoplayTime"
                    indicator-color="white">
                    <van-swipe-item v-for="(item, index) in banner" :key="index" style="border-radius: 4px">
                        <van-image fit="cover" radius="4px" :src="item" style="swiper_image">
                            <van-loading type="spinner" size="20" />
                        </van-image>
                    </van-swipe-item>
                </van-swipe>
            </div>
        </div>
        <div class="tab-content">
            <div v-if="tab_index == 0">
                <!-- banner -->
                <!-- <div class="banner-div">
                    <van-skeleton :row="1" class="big_picture skeleton" :loading="shopLoading.banner">
                        <van-swipe class="my-swipe" style="border-radius: 4px" :autoplay="3000" indicator-color="white"
                            height="150">
                            <van-swipe-item v-for="(item, index) in banner" :key="index" style="border-radius: 4px">
                                <van-image radius="4px" :src="item" style="width: 100%; border-radius: 4px"
                                    height="150">
                                        <van-loading type="spinner" size="20" />
                                </van-image>
                            </van-swipe-item>
                        </van-swipe>
                    </van-skeleton>
                </div> -->
                <!-- product -->
                <div class="padd-15">
                    <van-skeleton :row="4" class="shop_skeleton skeleton" :loading="shopLoading.list">
                        <van-skeleton :row="1" class="big_picture skeleton" :loading="shopLoading.banner">
                            <van-pull-refresh style="min-height: 100vh" v-model="refreshing" @refresh="onRefresh"
                                :pulling-text="$t('下拉即可刷新')" :loosing-text="$t('释放即可刷新')" :loading-text="$t('加载中')">
                                <van-list v-model="loading" :finished="finished" :loading-text="$t('加载中')"
                                    :finished-text="$t('没有更多了')" @load="onLoad">
                                    <div class="list">
                                        <GoodInfo :list="list" :index="0" />
                                        <van-empty v-if="list.length == 0" :description="$t('暂无数据')" />
                                    </div>
                                </van-list>
                            </van-pull-refresh>
                        </van-skeleton>
                    </van-skeleton>

                </div>
            </div>
            <!-- Commodity -->
            <div v-else-if="tab_index == 1">
                <div class="top_wrap">
                    <div class="top_head">
                        <div class="search_box">
                            <div class="left" @click="isLeftShow = true">
                                <img src="@/assets/image/commodity/saixuan.png" alt="" />
                            </div>
                            <div slot="title" class="tab-wrap">
                                <router-link :to="'/store/search?sellerId=' + $route.query.sellerId">
                                    <van-search shape="round" readonly background="#4fc08d" :placeholder="$t('搜索店铺内商品')">
                                        <template #left-icon>
                                            <img :src="searchIcon" alt="" class="search-icon" />
                                        </template>
                                    </van-search>
                                </router-link>
                            </div>
                        </div>
                        <!-- 筛选 -->
                        <div class="filter-div">
                            <div :class="['filter-item', filterIndex == index && 'active']"
                                v-for="(item, index) in filter_list" :key="index" @click="selectIndex(item, index)">
                                <div>{{ item }}</div>
                                <div class="right_icon" v-if="index !== 0 && item">
                                    <img v-if="highLow === 1 || filterIndex !== index" src="@/assets/image/shop/1.jpg"
                                        alt="">
                                    <img v-if="highLow === 2 && filterIndex === index" src="@/assets/image/shop/2.jpg"
                                        alt="">
                                    <img v-if="highLow === 3 && filterIndex === index" src="@/assets/image/shop/3.jpg"
                                        alt="">
                                </div>
                            </div>
                        </div>
                    </div>

                </div>

                <!-- product -->
                <div class="padd-15">
                    <van-skeleton :row="4" class="shop_skeleton skeleton" :loading="shopLoading.list">
                        <van-pull-refresh style="min-height: calc(100vh - 450px)" v-model="refreshing" @refresh="onRefresh"
                            :pulling-text="$t('下拉即可刷新')" :loosing-text="$t('释放即可刷新')" :loading-text="$t('加载中')">
                            <van-list v-model="loading" :finished="finished" :loading-text="$t('加载中')"
                                :finished-text="$t('没有更多了')" @load="onLoad">
                                <div class="list">
                                    <GoodInfo :list="list" :index="1" />
                                    <van-empty v-if="list.length == 0" :description="$t('暂无数据')" />
                                </div>
                            </van-list>
                        </van-pull-refresh>
                    </van-skeleton>
                </div>
            </div>
            <!-- Sort -->
            <!-- <div v-else>
                <div class="left" @click="isLeftShow = true">
                    <img src="@/assets/image/commodity/saixuan.png" alt="" />
                </div>
                <div class="padd-15">
                    <van-skeleton :row="4" class="shop_skeleton skeleton" :loading="shopLoading.list">
                        <van-pull-refresh style="min-height: 100vh" v-model="refreshing" @refresh="onRefresh"
                            :pulling-text="$t('下拉即可刷新')" :loosing-text="$t('释放即可刷新')" :loading-text="$t('加载中')">
                            <van-list v-model="loading" :finished="finished" :loading-text="$t('加载中')" :finished-text="$t('没有更多了')"
                                @load="onLoad">
                                <div class="list">
                                    <GoodInfo :list="list" :index="2" />
                                </div>
                            </van-list>
                        </van-pull-refresh>
                    </van-skeleton>
                </div>
            </div> -->

        </div>
        <!-- 侧边选项 -->
        <van-popup :overlay="false" v-model="isLeftShow" position="left" :style="{ height: '100%' }">
            <div class="pop-wrap">
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
                            :class="[item.categoryId == categoryId ? 'active' : '']" :key="index"
                            @click="selectCategory(item)">
                            {{ item.name }}
                        </div>
                    </div> -->
                <div class="pop-center-wrap">
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
        <!-- <van-action-sheet v-model="show" :actions="actions" @cancel="onCancel" :cancel-text="$t('取消')"
            close-on-click-action @select="onSelect" /> -->
    </div>
</template>
<script>
import {
    Swipe,
    SwipeItem,
    Image as VanImage,
    loading,
    PullRefresh,
    List,
    Popup,
    Icon,
    Toast,
    ActionSheet,
    Dialog,
    Skeleton,
    Tab,
    Tabs,
    Empty,
    Collapse, CollapseItem,
    Popover
} from "vant";
import { apiGetCategory, apiCategoryTree } from "@/API/home";
import { getSellerInfo } from "@/API/commodity";
import { sellerGoodsList, focusSeller, focusSellerDel, apiSellerTree } from "@/API/shop";
import { isLogin, priceFormat, getStorage } from "@/utils/utis";
import GoodInfo from "@/page/shop/goodInfo.vue";

export default {
    name: "shop",
    data() {
        return {
            showPopover: false,
            actions123: [
                { text: this.$t('投诉') }
            ],
            nq: "",
            activeName: "",
            tab_index: 0,
            highLow: 1,
            autoplayTime: 3000,
            secondaryCategoryId: "",
            tab_nav_list: [this.$t("推荐"), this.$t("商品")],
            filter_list: [
                this.$t("综合"),
                this.$t("销量"),
                this.$t("价格"),
                this.$t("新品"),
            ],
            banner: [],
            loading: false,
            finished: false,
            refreshing: false,
            isLeftShow: false,
            show: false,
            popupHeight: 0,
            filterIndex: 0,
            searchIcon: require("@/assets/image/index/sousuo.png"),
            shopBg: require('@/assets/image/shop/bg.png'),
            SellerInfo: {},
            list: [],
            page_no: 0,
            categoryList: [],
            categoryId: "",
            isPrice: 0,
            newTime: 0,
            collectTitle: "收藏",
            isHot: 0,
            actions: [],
            isRec: 0,
            active1: 0,
            active2: 0,
            active3: 0,
            actions1: [
                { name: this.$t("价格由高到低"), value: 1 },
                { name: this.$t("价格由低到高"), value: 2 },
            ],
            actions2: [
                { name: this.$t("销售量由高到低"), value: 1 },
                { name: this.$t("销售量由低到高"), value: 2 },
            ],
            actions3: [
                { name: this.$t("时间由远到近"), value: 1 },
                { name: this.$t("时间由近到远"), value: 2 },
            ],
            shopLoading: {
                banner: false,
                avatar: false,
                list: false
            },
            itemName: process.env.VUE_APP_ITEM_NAME,
        };
    },
    components: {
        [Tab.name]: Tab,
        [Tabs.name]: Tabs,
        [Empty.name]: Empty,
        [Skeleton.name]: Skeleton,
        [Swipe.name]: Swipe,
        [SwipeItem.name]: SwipeItem,
        [VanImage.name]: VanImage,
        [loading.name]: loading,
        [PullRefresh.name]: PullRefresh,
        [List.name]: List,
        [Popup.name]: Popup,
        [Icon.name]: Icon,
        [Toast.name]: Toast,
        [Dialog.Component.name]: Dialog.Component,
        [ActionSheet.name]: ActionSheet,
        [Collapse.name]: Collapse,
        [CollapseItem.name]: CollapseItem,
        [Popover.name]: Popover,
        GoodInfo,
    },
    computed: {
        langIsAr() {
            return localStorage.getItem('lang') == 'ar'
        }
    },
    created() {
        let lang = this.$route.query?.lang
        if (lang) {
            switch (lang) {
                case 'zh-CN':
                    lang = 'cn'
                    break;
                case 'zh-TW':
                case 'CN':
                    lang = 'tw'
                    break;
                case 'en-US':
                    lang = 'en'
                    break;
                default:
                    break;
            }
            sessionStorage.setItem('backPath', '/')
            if (lang !== localStorage.getItem('lang')) {
                localStorage.setItem('lang', lang)
                location.reload()
            }
        }
        if (this.$route.query.index) this.tab_index = +(this.$route.query.index)
        this.popupHeight = this.screenHight - 108;
        this.getSellerInfo(this.$route.query.sellerId);
        this.home_category();
        const tempObj = JSON.parse(sessionStorage.getItem("shopState"))
        if (['Argos', 'ArgosShop'].includes(this.itemName)) {
            this.filter_list = ['', this.$t('销量'), this.$t('价格'), ''];
            this.selectIndex({}, 1, 2)
        } else if (tempObj?.filterIndex) {
            this.filterIndex = tempObj.filterIndex
            this.highLow = tempObj.highLow
            this.selectIndex({}, tempObj.filterIndex, tempObj.highLow)
        } else {
            this.onLoad();
        }
    },
    beforeDestroy() {
        document.body.style.overflow = 'auto'
    },
    mounted() {
        document.body.style.overflow = 'hidden'
    },
    methods: {
        handleSelect(action) {
            this.$router.push('/complaint?sellerId=' + this.$route.query.sellerId)
        },
        priceFormat(num) {
            return priceFormat(num);
        },
        getList() {
            this.page_no++;
            var data = {
                pageNum: this.page_no,
                pageSize: 10,
                sellerId: this.$route.query.sellerId,
                isPrice: this.isPrice,
                isNew: this.newTime,
                isHot: this.isHot,
                isRec: this.isRec
            };
            if (this.tab_index == 0) {
                data.isRec = '1'
            } else {
                delete data.isRec
            }
            if (this.categoryId && this.categoryId != "-1") {
                data.categoryId = this.categoryId;
            }
            // if (this.isPrice == 1) {
            //   data.isPrice = this.isPrice
            // }
            // if (this.newTime) {
            //   data.newTime = this.newTime
            // }
            !data.categoryId && delete data.categoryId;
            !data.isHot && delete data.isHot;
            !data.isPrice && delete data.isPrice;
            !data.newTime && delete data.newTime;
            Object.keys(data).forEach(k => {
                if (!data[k]) delete data[k]
            })
            sellerGoodsList(data).then((res) => {
                for (let i = 0; i < res.pageList.length; i++) {
                    this.list.push(res.pageList[i]);
                }
                this.loading = false;
                if (res.pageList.length == 0) {
                    this.finished = true;
                }
                this.shopLoading.list = false

                var obj = {};
                this.list = this.list.reduce((prev, cur) => {
                    obj[cur.id] ? "" : (obj[cur.id] = true && prev.push(cur));
                    return prev;
                }, []);
            });
        },
        //获取分类
        home_category() {
            // apiGetCategory({ sellerId: this.$route.query.sellerId }).then((res) => {
            //     this.categoryList = res
            // });
            apiSellerTree({ sellerId: this.$route.query.sellerId }).then((res) => {
                this.categoryList = res
                this.categoryList.unshift({
                    name: this.$t("全部商品"),
                    categoryId: "-1",
                    subList: [],
                })
                // .filter(item => {
                //     if (item.name && item.subList.length > 0) {
                //         item.subList = item.subList.filter(subItem => subItem.name);
                //     }
                //     return item.name;
                // });
            });
        },
        selectCategory(item, sub) {
            if (item.categoryId == '-1') {
                this.refreshing = true
                this.page_no = 0;
                this.categoryId = '-1'
                this.secondaryCategoryId = ''
                this.isLeftShow = false;
                this.onLoad();
                document.body.scrollTop = 0;
                document.documentElement.scrollTop = 0;
                return
            }
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
        //关注店铺
        addFocusSeller() {
            if (!isLogin()) {
                // Toast(this.$t("请先登录"));
                // Dialog.confirm({
                //     title: this.$t("您还未登录"),
                //     message: this.$t("是否跳转到登录页面"),
                //     confirmButtonText: this.$t("确认"),
                //     cancelButtonText: this.$t("取消"),
                // }).then(() => {
                //     this.$router.push("/login");
                // });
                this.$notifyWarn(this.$t("请先登录"));
                this.$router.push("/login");
                return;
            }
            if (this.SellerInfo?.isFocus == 1) {
                this.delFocusSeller();
            } else {
                let data = {
                    sellerId: this.$route.query.sellerId,
                };
                focusSeller(data).then(() => {
                    this.collectTitle = "已收藏";
                    this.SellerInfo.isFocus = 1;
                    Toast(this.$t("关注成功"));
                });
            }
        },
        //取消关注
        delFocusSeller() {
            let data = {
                sellerId: this.$route.query.sellerId,
            };
            focusSellerDel(data).then(() => {
                this.SellerInfo.isFocus = 0;
                this.collectTitle = "收藏";
                Toast(this.$t("取消成功"));
            });
        },
        onSelect(item) {
            item.value = item.value === 1 ? 2 : 1
            if (this.filterIndex == 1) {
                this.isPrice = 0;
                this.isHot = item.value;
                this.newTime = 0;
            } else if (this.filterIndex == 2) {
                this.isPrice = item.value;
                this.isHot = 0;
                this.newTime = 0;
            } else {
                this.isPrice = 0;
                this.isHot = 0;
                this.newTime = item.value;
            }
            this.page_no = 0;
            this.list = [];
            this.onLoad();
            document.body.scrollTop = 0;
            document.documentElement.scrollTop = 0;
        },
        onCancel() {
            if (this.filterIndex == 1) {
                this.actions1.map((info) => {
                    info.color = "";
                });
                this.isPrice = 0;
            } else if (this.filterIndex == 2) {
                this.actions2.map((info) => {
                    info.color = "";
                });
                this.isHot = 0;
            } else {
                this.actions3.map((info) => {
                    info.color = "";
                });
                this.newTime = 0;
            }
            this.page_no = 0;
            this.list = [];
            this.onLoad();
            document.body.scrollTop = 0;
            document.documentElement.scrollTop = 0;
        },
        selectIndex(item, index, highLow) {
            this.shopLoading.list = true
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
                this.actions = this.actions2;
                this.onSelect({ value: this.highLow - 1 })
            } else if (index == 2) {
                this.actions = this.actions1;
                this.onSelect({ value: this.highLow - 1 })
            } else if (index == 3) {
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
            sessionStorage.setItem("shopState", JSON.stringify({ filterIndex: this.filterIndex, highLow: this.highLow }))
        },
        onClickLeft() {
            const backPath = sessionStorage.getItem("backPath")
            if (backPath) {
                this.$router.replace('/')
                sessionStorage.removeItem("backPath")
            } else {
                this.$router.go(-1);
            }
        },
        handleChange(index) {
            this.isLeftShow = false;
            this.$router.replace({ query: { ...this.$route.query, index } })
            this.shopLoading.list = true
            this.list = [];
            // if (index == this.tab_index) return;
            // index == 0 ? (this.isRec = "1") : (this.isRec = "0");
            this.tab_index = index;
            this.categoryId = undefined;
            this.isPrice = undefined;
            this.newTime = 0;
            this.filterIndex = 0;
            this.page_no = 0;
            const tempObj = JSON.parse(sessionStorage.getItem("shopState"))
            if (['Argos', 'ArgosShop'].includes(this.itemName)) {
                this.filter_list = ['', this.$t('销量'), this.$t('价格'), ''];
                this.selectIndex({}, 1, 2)
            } else if (tempObj?.filterIndex) {
                this.filterIndex = tempObj.filterIndex
                this.highLow = tempObj.highLow
                this.selectIndex({}, tempObj.filterIndex, tempObj.highLow)
            } else {
                this.onLoad();
            }
        },
        // 商家详情
        getSellerInfo(id) {
            let dataJson = {
                sellerId: id,
            };
            getSellerInfo(dataJson).then((res) => {
                this.SellerInfo = res;
                this.collectTitle = this.SellerInfo?.isFocus == 1 ? "已收藏" : "收藏";
                if (res.banner1) {
                    this.banner.push(res.banner1);
                    this.autoplayTime = 0
                }
                if (res.banner2) {
                    this.banner.push(res.banner2);
                    this.autoplayTime = 3000
                }
                if (res.banner3) {
                    this.banner.push(res.banner3);
                    this.autoplayTime = 3000
                }
                this.shopLoading.banner = this.shopLoading.avatar = false

            });
        },
        onRefresh() {
            // 清空列表数据
            this.finished = false;
            this.page_no = 0;
            // 重新加载数据
            // 将 loading 设置为 true，表示处于加载状态
            this.loading = true;
            this.onLoad();
        },
        onLoad() {

            if (this.refreshing) {
                this.list = [];
                this.refreshing = false;
            }

            this.getList();
        },
        openDetails(item) {
            document.body.scrollTop = 0;
            document.documentElement.scrollTop = 0;
            this.$router.push("/CommodityDetails?sellerGoodsId=" + item.id);
        },
        openUrl(url, name) {
            !url && Toast(this.$t("该商户未开通") + " " + name);
            url && (location.href = url);
        },
    },
};
</script>
<style lang="scss" scoped>
html[dir="rtl"] {
    .shop-bottom /deep/ .van-tab--active {
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

.top_wrap {
    width: 100%;
    height: 110px;
}

.top_head {
    width: 100%;
    position: fixed;
    top: 225px;
    left: 0;
    z-index: 99;
    background: #fff;
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

.padd-15 {
    padding: 12px;
    box-sizing: border-box;
}

:deep(.van-pull-refresh) {
    min-height: 0;
}

:deep(.van-tabs) {
    width: 100%;

    .van-tabs__line {
        width: 80px;
        background: var(--main-color) !important;
    }
}

:deep(.van-skeleton__row) {
    margin-top: 10px;
}

:deep(#app) {
    overflow: hidden;
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

.shop {
    width: 100%;
    height: 100%;
    font-size: 14px;
    background: rgba(238, 238, 238, 1);
    overflow: hidden;

    .shop-header {
        // background: url("@/assets/image/shop/bg.png") center no-repeat;
        background-size: 100% 100%;
        background-repeat: no-repeat;
        background-position: center;
        background: rgba(0, 0, 0, 0.5);
        width: 100%;
        height: 130px;
        padding-top: 60px;
        position: relative;
        z-index: 3;

        .top-banner-div {
            width: 100vw;
            position: absolute;
            top: 0;
            left: 0;
            z-index: -1;
            height: 180px;
            //background: white;
            // filter: drop-shadow(0px 6px 12px rgba(55, 63, 69, 0.1));
            border-radius: 4px;
            opacity: .5;

            :deep(.van-swipe__indicators) {
                display: none;
            }

            .swiper_image {
                border-radius: 4px;
                height: auto;
                max-height: 150px;
            }

            .my-swipe {
                height: 100% !important;
                width: 100% !important;

                :deep(.van-swipe-item) {
                    width: 100% !important;
                }

                :deep(.van-swipe__track) {
                    width: 100% !important;
                    height: 100% !important;

                    .van-image,
                    img {
                        // width: 100% !important;
                        height: 100% !important;
                    }
                }
            }

        }

        .shop-top {
            padding-left: 10px;
            display: flex;
            margin-top: 20px;

            .shop-info {
                display: flex;
                flex: 1;
                min-height: 97px;

                .shop-info-left {
                    .shop-avatar {
                        width: 60px;
                        height: 60px;
                        background: #fff;
                        border-radius: 50%;
                        overflow: hidden;
                        display: flex;
                        justify-content: center;
                        align-items: center;

                        img {
                            max-width: 100%;
                            max-height: 100%;
                        }
                    }
                }

                .shop-info-right {
                    padding-left: 10px;
                    width: 100%;
                    // transform: translateY(10px);

                    .title {
                        color: #f5f5f7;
                        font-size: 16px;
                        font-weight: 600;
                        height: 19px;
                    }

                    .text {
                        color: #e0e0e0;
                        font-size: 12px;
                        margin-top: 5px;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        display: -webkit-box;
                        -webkit-box-orient: vertical;
                        -moz-box-orient: vertical;
                        box-orient: vertical;
                        -webkit-line-clamp: 2;
                        line-clamp: 2;
                        min-height: 33px;
                        // height: 28px;
                    }

                    .logos {
                        margin: 10px 0;
                        height: 25px;

                        img {
                            width: 25px;
                            height: 25px;
                            margin-right: 10px;
                        }
                    }
                }
            }

            .shop-followed {
                background-color: var(--main-color);
                height: 25px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #f5f5f7;
                border-top-left-radius: 20px;
                border-bottom-left-radius: 20px;
                margin-top: 20px;
                padding: 0 6px;
                box-sizing: border-box;

                >img {
                    width: 15px;
                    height: 15px;
                    flex-shrink: 0;
                }

                >div {
                    margin-left: 6px;
                }

                .starbai {
                    width: 14px;
                    height: 14px;
                }
            }
        }

        .shop-bottom {
            position: relative;
            padding-bottom: 10px;

            .tab-wrap {
                display: flex;
                position: absolute;
                left: 0;
                top: 0;
                width: 90%;
                height: 48px;
                background: #fff;
                padding: 0 5%;

                .tab-item {
                    flex: 1;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }

                .active {
                    border-bottom: 2px solid var(--main-color);
                }
            }
        }
    }

    .tab-content {
        width: 100%;
        height: 100%;
        padding-top: 30px;
        padding-bottom: 220px;
        box-sizing: border-box;
        // position: absolute;
        // top: 224px !important;
        // left: 0;
        // z-index: 2;
        overflow: scroll;
        background: #fff;

        .banner-div {
            padding: 14px;
            //background: white;
            filter: drop-shadow(0px 6px 12px rgba(55, 63, 69, 0.1));
            border-radius: 4px;
        }

        .filter-div {
            height: 40px;
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

        .left {
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            // margin: 10px 15px 0 15px;
            margin-right: 9px;

            img {
                width: 36px;
                height: 36px;
            }
        }
    }

    .nav-bar {
        background: transparent;
        top: 15px;
        z-index: 4;
    }

    .pop-wrap {
        background: #f5f5f7;
        box-shadow: 8px 0px 6px -1px rgba(138, 138, 138, 0.16);
        width: 165px;
        overflow-y: auto;
        height: calc(100vh - 200px);
        position: relative;
        scrollbar-width: none;
        -ms-overflow-style: none;
        z-index: 999;
        overflow: hidden;

        &::-webkit-scrollbar {
            display: none;
        }

        .pop-header-wrap {
            height: 50px;
            display: flex;
            align-items: center;
            margin: 0 10px;
            border-bottom: 1px solid #e6e6e6;

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
                    width: 20px;
                    height: 20px;
                }
            }
        }

        .pop-center-wrap {
            height: 330px;
            overflow-y: auto;
            padding-bottom: 100px;
            background: #f5f5f7;

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
                border-left: 2px solid var(--main-color);
            }

            .active2 {
                background: #fff;
                border-left: 2px solid var(--main-color);
            }
        }
    }
}

/deep/ [class*="van-hairline"]::after {
    border: none !important;
}

/deep/ .van-nav-bar .van-icon-arrow-left {
    color: #fff;
}

/deep/ .van-nav-bar__title {
    width: 77% !important;
    max-width: 77%;
    padding-left: 20px;
}

/deep/ .van-search {
    padding: 0 !important;
    background: transparent !important;
}

/deep/ .van-search .van-cell {
    padding: 8px 8px 8px 0;
}

/deep/ .van-popup--left {
    top: 78%;
    overflow: hidden;
}

:deep(.van-popup) {
    scrollbar-width: none;
    -ms-overflow-style: none;
    z-index: 999999 !important;
    overflow: hidden !important;
    height: 100%;
    background: #f5f5f7 !important;

    &::-webkit-scrollbar {
        display: none;
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

.search_box {
    display: flex;
    align-items: center;
    padding: 13px 12px 0 12px;

    .tab-wrap {
        width: 100%;
    }
}

.arrow-right {
    width: 10px;
}
</style>
