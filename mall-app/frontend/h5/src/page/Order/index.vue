<template>
    <div class="page-content">
        <!-- 取消弹窗 -->
        <cancel-dialog :dialog-show.sync="cancelShow" :dialog-data="currentData" @done="tableChange" />

        <!-- 提醒发货 -->
        <reminds-dialog :dialog-show.sync="remindShow" :dialog-data="currentData" @done="tableChange" />

        <van-nav-bar safe-area-inset-top fixed :title="$t('我的订单')" left-arrow @click-left="() => $router.push({ path: '/me', dir: 'left' })" />
        <div class="nav-content">
            <van-tabs v-model="currentNav" @change="tableChange">
                <van-tab v-for="(item, index) in navData" :key="index" :title="item.title" :name="item.name" />
            </van-tabs>
        </div>
        <div style="width: 100%; height: 90px" />

        <van-pull-refresh class="pull-content" v-model="refreshing" :pulling-text="$t('下拉即可刷新')"
            :loosing-text="$t('释放即可刷新')" :loading-text="$t('加载中')" @refresh="onRefresh">
            <van-list v-model="loading" :finished="finished" :finished-text="list.length ? $t('没有更多了') : ''" @load="onLoad" :loading-text="$t('加载中')">
                <div v-if="list.length" class="list-content">
                    <div v-for="item in list" :key="item.id" class="item">
                        <div class="info-item">
                            <p>{{ $t("流水号") }}：</p>
                            <div>
                                <div @click="copyHandle(item.id)">
                                    <span class="nowrap" style="width: 200px">{{ item.id }}</span><img :src="copyIcon"
                                        alt="" />
                                </div>
                                <!-- <p>2022.11.07</p> -->
                            </div>
                        </div>
                        <div class="info-item">
                            <p>{{ $t("信息") }}：</p>
                            <div>
                                <div>{{ item.goodsCount }} {{ $t("个商品") }}</div>
                                <p>{{ $t("来自") }} {{ item.goodsFrom }}</p>
                            </div>
                        </div>
                        <div class="info-item money">
                            <p>{{ $t("金额") }}：</p>
                            <div>${{ priceFormat(item.priceCount) }}</div>
                        </div>
                        <div class="info-item opreate">
                            <p>{{ $t("操作") }}：</p>
                            <div @click="
                                openPage('/orderDetails', {
                                    id: item.id,
                                    returnStatus: item.returnStatus,
                                    index: currentNav
                                })
                            ">
                                {{ $t("查看详情") }}
                            </div>
                        </div>
                        <!-- <div class="btn-content">
                <div
                class="btn-item"
                @click="
                  openPage('/orderRefund', { id: item.id, a: item.priceCount })
                "
              >
                {{ $t("申请退货") }}
              </div>
            </div> -->
                        <div v-if="Number(item.status) !== -1" class="btn-content">
                            <div v-if="Number(item.status) === 0" class="btn-item" @click="cancleOrder(item)">
                                {{ $t("取消订单") }}
                            </div>
                            <div v-if="Number(item.status) === 0" class="btn-item color" @click="openPeddingPay(item)">
                                {{ $t("立即付款") }}
                            </div>
                            <div v-if="Number(item.status) === 1" class="btn-item color" @click="remindHandle(item)">
                                {{ $t("提醒发货") }}
                            </div>
                            <div v-if="Number(item.status) === 1" class="btn-item" @click="
                                openPage('/orderRefund', { id: item.id, a: item.priceCount })
                            ">
                                {{ $t("申请退货") }}
                            </div>
                            <div v-if="Number(item.status) === 3" class="btn-item color" @click="orderPick(item)">
                                {{ $t("确认收货") }}
                            </div>
                            <div v-if="Number(item.status) === 4" class="btn-item"
                                @click="openPage('/orderEvaluate', { id: item.id })">
                                {{ $t("立即评价") }}
                            </div>
                            <div v-if="Number(item.status) === 6" class="tips">
                                <span v-if="!Boolean(item.returnStatus)">{{
                                    $t("未退款")
                                }}</span>
                                <span v-if="Number(item.returnStatus) === 1" class="running">{{
                                    $t("退款中")
                                }}</span>
                                <span v-if="Number(item.returnStatus) === 2" class="success">{{
                                    $t("退款成功")
                                }}</span>
                                <span v-if="Number(item.returnStatus) === 3" class="fail">{{
                                    $t("退款失败")
                                }}</span>
                            </div>
                        </div>
                    </div>
                </div>
                <van-empty v-if="!list.length && !loading" :description="$t('暂无数据')" />
            </van-list>
        </van-pull-refresh>

        <div class="order-content">
            <div class="item"></div>
        </div>
        <transition name="fade" >
            <img class="to_top" v-show="isShowTopBtn" @click="handleToTop" src="@/assets/image/commodity/dingbu.png" />
        </transition>
    </div>
</template>

<script>
import {
    NavBar,
    List,
    PullRefresh,
    Empty,
    Tab,
    Tabs,
    Toast,
    Dialog,
} from "vant";
import CancelDialog from "./components/CancelDialog.vue";
import RemindsDialog from "./components/RemindsDialog.vue";
import { isLogin, priceFormat } from "@/utils/utis";
import { orderListMain, orderReceipt } from "@/API/user";
export default {
    name: "Order",
    components: {
        [NavBar.name]: NavBar,
        [List.name]: List,
        [Tab.name]: Tab,
        [Tabs.name]: Tabs,
        [Empty.name]: Empty,
        [Toast.name]: Toast,
        [PullRefresh.name]: PullRefresh,
        [Dialog.name]: Dialog,
        CancelDialog,
        RemindsDialog,
    },
    data() {
        return {
            isShowTopBtn: false,
            copyIcon: require("@/assets/image/me/fuzhi1.png"),
            currentNav: "",
            navData: [
                {
                    title: this.$t("全部"),
                    name: "",
                },
                {
                    title: this.$t("待付款"),
                    name: "0",
                },
                {
                    title: this.$t("待发货"),
                    name: "1",
                },
                {
                    title: this.$t("待收货"),
                    name: "3",
                },
                {
                    title: this.$t("待评价"),
                    name: "4",
                },
                {
                    title: this.$t("退款/售后"),
                    name: "6",
                },
            ],
            loading: false,
            finished: false,
            refreshing: false,
            pageNum: 1,
            pageSize: 10,
            list: [],
            cancelShow: false,
            remindShow: false,
            currentData: {},
            isToask: true,
        };
    },
    mounted() {
        window.addEventListener("scroll", () => {
            this.isShowTopBtn = document.documentElement.scrollTop || document.body.scrollTop > 500
        });
    },
    created() {
        if (!isLogin()) {
            this.$router.push("/");
        } else {
            const { query } = this.$route;
            if (query && query.type) {
                this.currentNav = query.type
            }
        }
        this.onLoad();
    },
    methods: {
        copyHandle(txt) {
            this.$copyText(txt).then(
                () => {
                    Toast(this.$t("复制成功"));
                },
                () => {
                    Toast(this.$t("复制失败"));
                }
            );
        },
        priceFormat(num) {
            return priceFormat(num);
        },
        onRefresh() {
            this.finished = false;
            this.pageNum = 1;
            this.loading = true;
            this.onLoad();
            // this.isToask && Toast(this.$t("刷新成功"));
            this.isToask = true;
        },

        tableChange(val) {
            Toast.loading({
                duration: 0,
                message: this.$t("加载中"),
            });
            this.list = [];

            this.onRefresh();
        },

        onLoad() {
            if (this.refreshing) {
                this.list = [];
                this.refreshing = false;
            }
            this.getTableList();
        },

        getTableList() {
            const params = {
                pageNum: this.pageNum,
                pageSize: this.pageSize,
            };
            if (this.currentNav) {
                params.status = Number(this.currentNav);
            }
            orderListMain(params)
                .then((res) => {
                    const { pageList } = res;
                    this.list =
                        this.pageNum === 1 ? pageList : [...this.list, ...pageList];
                    this.pageNum++;
                    this.loading = false;
                    Toast.clear();
                    if (pageList.length < this.pageSize) {
                        this.finished = true;
                    }
                    var obj = {};
                    this.list = this.list.reduce((prev, cur) => {
                        obj[cur.id] ? "" : (obj[cur.id] = true && prev.push(cur));
                        return prev;
                    }, []);
                })
                .catch(() => {
                    this.loading = false;
                    this.finished = true;
                    Toast.clear();
                });
        },

        // 取消订单
        cancleOrder(data) {
            this.currentData = data;
            this.cancelShow = true;
        },

        // 提醒发货
        remindHandle(data) {
            const remindStore = localStorage.getItem("remindStore")
                ? JSON.parse(localStorage.getItem("remindStore"))
                : [];
            if (!remindStore.includes(data.id)) {
                this.currentData = data;
                this.remindShow = true;
            } else {
                Toast(this.$t("该订单已提醒过啦~"));
            }
        },

        openPage(path, query) {
            const params = {
                path,
            };

            if (query) {
                params.query = query;
            }

            this.$router.push(params);
        },
        //跳转待支付页面
        openPeddingPay(data) {
            const list = [
                {
                    orderList: data.id,
                    orderId: data.id,
                },
            ];
            this.$router.push({
                path: "/PendingPayment",
                query: {
                    orderList: JSON.stringify(list),
                    total: data.priceCount,
                },
            });
        },

        // 收货
        orderPick(data) {
            Dialog.confirm({
                title: this.$t("提示"),
                message: this.$t("确认收货吗？"),
                confirmButtonText: this.$t("确认"),
                cancelButtonText: this.$t("取消"),
            })
                .then(() => {
                    Toast.loading({
                        duration: 0,
                        message: this.$t("提交中"),
                        forbidClick: true,
                    });

                    const params = {
                        orderId: data.id,
                    };
                    orderReceipt(params)
                        .then(() => {
                            Toast.clear();
                            Toast(this.$t("收货成功"));
                            this.isToask = false;
                            setTimeout(() => {
                                this.tableChange();
                            }, 1000);
                        })
                        .catch(() => {
                            Toast.clear();
                        });
                })
                .catch(() => {
                    console.log("cancel");
                });
        },
        handleToTop() {
            scrollTo({
                top: 0,
                left: 0,
                behavior: 'smooth'
            });
        },
    },
};
</script>

<style lang="scss" scoped>
/deep/ .van-nav-bar__content {
    height: 50px;
}

.page-content {
    min-height: 100vh;
    background-color: #f5f5f7;

    * {
        box-sizing: border-box;
    }

    .nav-content {
        width: 100%;
        position: fixed;
        top: 46px;
        left: 0;
        background-color: #fff;
        z-index: 99;

        /deep/ .van-tabs__line {
            background-color: var(--main-color) !important;
        }
    }

    .list-content {
        padding: 13px 15px 0 15px;

        >.item {
            padding: 0 10px;
            margin-bottom: 8px;
            background-color: #fff;

            .info-item {
                padding: 18px 0;
                width: 100%;
                display: flex;
                justify-content: space-between;
                border-bottom: 1px solid #eee;

                &.opreate {
                    border-bottom: none;

                    >div {
                        color: var(--main-color);
                    }
                }

                &.money {
                    >div {
                        font-size: 16px;
                        color: var(--main-color);
                    }
                }

                >p {
                    font-size: 14px;
                    columns: #000;
                    flex: 0 0 100px;
                }

                >div {
                    flex: 1;
                    font-size: 14px;
                    text-align: end;
                    word-break: break-word;
                    // padding-left: 30px;

                    >div {
                        display: flex;
                        justify-content: flex-end;

                        >img {
                            width: 10px;
                            height: 10px;
                            margin-left: 8px;
                            position: relative;
                            top: 3px;
                        }
                    }

                    >p {
                        font-size: 12px;
                        color: #999;
                        margin-top: 6px;
                    }
                }
            }

            .btn-content {
                width: 100%;
                display: flex;
                align-items: center;
                justify-content: flex-end;
                padding-bottom: 15px;
                overflow-x: auto;
                >.btn-item {
                    min-width: 92px;
                    padding: 5px;
                    min-height: 28px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 4px;
                    font-size: 14px;
                    color: #333;
                    border: 1px solid #333;
                    margin-right: 16px;
                    text-align: center;
                    &:last-child {
                        margin-right: 0;
                    }

                    &.color {
                        color: var(--main-color);
                        border-color: var(--main-color);
                    }
                }

                >.tips {
                    font-size: 14px;

                    >span {
                        color: #999;

                        &.success {
                            color: #32aa15;
                        }

                        &.running {
                            color: #1989fa;
                        }

                        &.fail {
                            color: #e10015;
                        }
                    }
                }
            }
        }
    }
}
</style>
