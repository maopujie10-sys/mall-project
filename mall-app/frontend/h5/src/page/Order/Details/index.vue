<template>
    <div class="page-content">
        <!-- 取消弹窗 -->
        <cancel-dialog v-if="currentData" :dialog-show.sync="cancelShow" :dialog-data="currentData"
            @done="() => $router.back()" />

        <!-- 提醒发货 -->
        <reminds-dialog v-if="currentData" :dialog-show.sync="remindShow" :dialog-data="currentData" />

        <van-nav-bar safe-area-inset-top fixed :title="$t('订单详情')" left-arrow
            @click-left="() => $router.push({ path: '/order', dir: 'left', query: { type: $route.query.index } })" />
        <div style="width: 100%; height: 46px" />

        <div v-if="currentData" class="info-content">
            <div class="order-info-content">
                <div class="item">
                    <p class="p80">{{ $t("流水号") }}：</p>
                    <div>
                        <div class="copy" @click="copyHandle(currentData.id)">
                            <span class="nowrap" style="width: 200px">{{
                                currentData.id
                            }}</span><img :src="copyIcon" alt="" />
                        </div>
                        <p class="tips">{{ $formatZoneDate(currentData.createTime) }}</p>
                    </div>
                </div>
                <div class="item">
                    <p class="p80">{{ $t("收件地址") }}：</p>
                    <div>
                        <p>
                            {{ currentData.postcode }} {{ currentData.province }}
                            {{ currentData.city }}
                        </p>
                        <p>{{ currentData.country }}</p>
                        <p>{{ currentData.address }}</p>
                        <p>{{ currentData.contacts }}</p>
                        <p>
                            {{
                                currentData.phone?.indexOf("|") > -1
                                ? currentData.phone.split("|")[1]
                                : currentData.phone
                            }}
                        </p>
                    </div>
                </div>
                <div class="item">
                    <p class="p80">{{ $t("商品数量") }}：</p>
                    <div>{{ goodsTotalNum }}</div>
                </div>
                <div class="item">
                    <p class="p80">{{ $t("订单总额") }}：</p>
                    <div class="money">
                    ${{ priceFormat(totalPrice + currentData.tax + currentData.fees) }}
                        <!-- ${{ priceFormat($plus($plus(totalPrice, currentData.tax), currentData.fees)) }} -->
                    </div>
                </div>
                <div class="item">
                    <p class="p80">{{ $t("税费") }}：</p>
                    <div class="money">${{ currentData.tax ? priceFormat(currentData.tax) : '0.00' }}</div>
                </div>
                <div class="item">
                    <p class="p80">{{ $t("运费") }}：</p>
                    <div class="money">${{ currentData.fees ? priceFormat(currentData.fees) : '0.00' }}</div>
                </div>
                <div class="item">
                    <p class="p80">{{ $t("总金额") }}：</p>
                    <div class="money">
                        ${{ priceFormat($plus($plus(totalPrice, currentData.tax), currentData.fees)) }}
                    </div>
                </div>
            </div>

            <div v-if="currentData" class="goods-info-content">
                <div v-for="(item, index) in goodsData" :key="index" class="order-info-content">
                    <div class="goods-item" @click="repeatPurchase(item)">
                        <!-- <div class="poster"><img :src="item.goodsIcon" alt="" /></div> -->
                        <div class="poster">
                            <img :src="item.goodsIcon" alt="" />
                        </div>
                        <div class="name">
                            <div class="title">{{ item.goodsName }}</div>
                            <div class="" v-if="item.attributes">
                                <span class="attribute" v-for="(j, p) in item.attributes" :key="p"
                                    v-if="j.attrName && j.attrValue">
                                    {{ j.attrName }}:{{ j.attrValue }}</span>
                            </div>
                        </div>
                    </div>
                    <div class="item">
                        <p>{{ $t("数量") }}：</p>
                        <div>{{ item.goodsNum }}</div>
                    </div>
                    <div class="item">
                        <p>{{ $t("单价") }}：</p>
                        <div class="money">${{ priceFormat(item.goodsReal) }}</div>
                    </div>
                    <div class="item">
                        <p>{{ $t("总价") }}：</p>
                        <div class="money">
                            ${{ priceFormat($operation(item.goodsReal, item.goodsNum, 'times')) }}
                        </div>
                    </div>
                    <div class="item">
                        <p>{{ $t("税费") }}：</p>
                        <div class="money">${{ item.tax ? priceFormat(item.tax) : '0.00' }}</div>
                    </div>
                    <div class="item">
                        <p>{{ $t("运费") }}：</p>
                        <div class="money">${{ item.fees ? priceFormat(item.fees) : '0.00' }}</div>
                    </div>
                    <div class="item">
                        <p>{{ $t("总计") }}：</p>
                        <div class="money">
                            {{ priceFormat(item.goodsReal * item.goodsNum + item.tax + item.fees) }}
                            <!-- ${{ priceFormat($plus($plus(totalPrice, currentData.tax), currentData.fees)) }} -->
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="currentData && Number(currentData.status) !== -1" class="page-footer">
            <div v-if="Number(currentData.status) === 0" class="btn" @click="cancelShow = true">
                {{ $t("取消订单") }}
            </div>
            <div v-if="Number(currentData.status) === 0" class="btn color" @click="openPeddingPay(currentData)">
                {{ $t("立即付款") }}
            </div>
            <div v-if="Number(currentData.status) === 1" class="btn color" @click="remindHandle(currentData)">
                {{ $t("提醒发货") }}
            </div>
            <div v-if="Number(currentData.status) === 3" class="btn" @click="
                openPage('/orderRefund', {
                    id: currentData.id,
                    a: currentData.prizeReal,
                })
            ">
                {{ $t("申请退货") }}
            </div>

            <div v-if="Number(currentData.status) === 3" class="btn color" @click="orderPick(currentData)">
                {{ $t("确认收货") }}
            </div>
            <div v-if="Number(currentData.status) > 0" class="btn"
                @click="openPage('/order/logistics', { id: currentData.id })">
                {{ $t("查看物流") }}
            </div>
            <div v-if="Number(currentData.status) === 4" class="btn"
                @click="openPage('/orderEvaluate', { id: currentData.id })">
                {{ $t("立即评价") }}
            </div>
            <div v-if="Number(currentData.status) === 6" class="tips">
                <span v-if="!Boolean($route.query.returnStatus)">{{ $t("未退款") }}
                </span>
                <span v-if="Number($route.query.returnStatus) === 1" class="running">{{
                    $t("退款中")
                }}</span>
                <span v-if="Number($route.query.returnStatus) === 2" class="success">{{
                    $t("退款成功")
                }}</span>
                <span v-if="Number($route.query.returnStatus) === 3" class="fail">{{
                    $t("退款失败")
                }}</span>
            </div>
        </div>
    </div>
</template>

<script>
import { NavBar, Toast, Dialog } from "vant";
import CancelDialog from "./../components/CancelDialog.vue";
import RemindsDialog from "./../components/RemindsDialog.vue";
import { priceFormat } from "@/utils/utis";
import { orderInfo, orderListGoods, orderReceipt } from "@/API/user";
export default {
    name: "OrderDetails",
    components: {
        [NavBar.name]: NavBar,
        [Toast.name]: Toast,
        [Dialog.name]: Dialog,
        CancelDialog,
        RemindsDialog,
    },
    data() {
        return {
            copyIcon: require("@/assets/image/me/fuzhi1.png"),
            cancelShow: false,
            remindShow: false,
            currentData: null,
            orderId: null,
            totalPrice: 0,
            goodsData: [],
            timezone: "",
        };
    },
    computed: {
        goodsTotalNum() {
            let num = 0;
            this.goodsData.forEach((item) => {
                num += item.goodsNum;
            });
            return num;
        },
    },
    mounted() {
        this.$nextTick(() => {
            const { id } = this.$route.query;
            if (id) {
                this.orderId = id;
                this.getDataInfo();
                this.getOrderGoods();
            } else {
                Toast(this.$t("订单号不存在"));
                setTimeout(() => {
                    this.$router.back();
                }, 1500);
            }
        });
        this.timezone = localStorage.getItem("timeZone");
    },
    methods: {
        repeatPurchase(item) {
            if (item?.isShelf != 1 || item?.isValid != 1) return this.$notify(this.$t('该商品已下架'), 'warning')
            this.$router.push('/CommodityDetails?sellerGoodsId=' + item.goodsId)
        },
        time(t) {
            let dayjs = this.dayjs;
            return dayjs().tz(this.timezone).format(t);
        },
        priceFormat(num) {
            return priceFormat(num);
        },
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

        getDataInfo() {
            Toast.loading({
                duration: 0,
                // message: this.$t("请求中"),
                forbidClick: true,
            });

            orderInfo({
                orderId: this.orderId,
                type: 1
            })
                .then((res) => {
                    this.currentData = res.orderInfo;
                    Toast.clear();
                })
                .catch(() => {
                    Toast.clear();
                });
        },

        getOrderGoods() {
            orderListGoods({
                orderId: this.orderId,
            }).then((res) => {
                this.goodsData = res.pageList || [];
                this.goodsData.forEach((item) => {
                    this.totalPrice += item.goodsReal * item.goodsNum
                    // this.$operation(this.totalPrice, this.$operation(item.goodsReal, item.goodsNum, 'plus'), 'times')
                    // this.totalPrice += this.$operation(item.goodsReal, item.goodsNum, 'times');
                });
            });
        },

        //跳转待支付页面
        openPeddingPay(data) {
            const list = [
                {
                    orderList: data.id,
                },
            ];
            this.$router.push({
                path: "/PendingPayment",
                query: {
                    orderList: JSON.stringify(list),
                    total: this.$operation(data.discountPrice, data.goodsCount, 'times') ||
                        this.$operation(data.priceReal, data.goodsCount, 'times')
                },
            });
        },

        // 提醒发货
        remindHandle(data) {
            const remindStore = localStorage.getItem("remindStore")
                ? JSON.parse(localStorage.getItem("remindStore"))
                : [];
            if (!remindStore.includes(data.id)) {
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
                            this.currentData = null
                            // this.tableChange();
                            this.getDataInfo();
                            // this.getOrderGoods();
                        })
                        .catch(() => {
                            Toast.clear();
                        });
                })
                .catch(() => {
                    console.log("cancel");
                });
        },
    },
};
</script>

<style lang="scss" scoped>
.p80 {
    flex: 0 0 70px;
}

.page-content {
    min-height: 100vh;
    background-color: #f5f5f7;

    * {
        box-sizing: border-box;
    }

    .info-content {
        padding: 10px 15px;
        padding-bottom: 100px;

        .order-info-content {
            padding: 0 10px;
            background-color: #fff;

            >.item {
                padding: 17px 0;
                border-bottom: 1px solid #eee;
                color: #000;
                font-size: 14px;
                display: flex;
                justify-content: space-between;

                .p80 {
                    flex: 0 0 100px;
                }

                >div {
                    flex: 1;
                    // padding-left: 50px;
                    text-align: end;
                    word-break: break-word;

                    &.money {
                        font-size: 16px;
                        
                        color: var(--main-color);
                    }

                    >p {
                        line-height: 21px;

                        &.tips {
                            font-size: 12px;
                            color: #999;
                            margin-top: 6px;
                        }
                    }

                    >.copy {
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
                }

                &:last-child {
                    border-bottom: 0;
                }
            }
        }

        >.goods-info-content {
            margin-top: 16px;

            >.order-info-content {
                margin-bottom: 6px;
            }

            .goods-item {
                display: flex;
                padding: 17px 0;
                border-bottom: 1px solid #eee;

                >.poster {
                    width: 63px;
                    height: 63px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    overflow: hidden;

                    >img {
                        height: fit-content;
                        width: auto;
                        max-height: 100%;
                        max-width: 100%;
                    }
                }

                >.name {
                    word-break: break-word;
                    flex: 1;
                    font-size: 14px;
                    padding-left: 20px;

                    .title {
                        display: -webkit-box;
                        -webkit-box-orient: vertical;
                        -moz-box-orient: vertical;
                        box-orient: vertical;
                        -webkit-line-clamp: 2;
                        line-clamp: 2;
                        overflow: hidden;
                        text-overflow: ellipsis;
                    }

                    .attribute {
                        font-size: 12px;
                        color: #333;
                        margin-right: 10px;
                        margin-top: 5px;
                        display: inline-block;
                    }
                }
            }
        }
    }

    .page-footer {
        width: 100%;
        height: 53px;
        background-color: #fff;
        position: fixed;
        bottom: 0;
        left: 0;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-right: 15px;

        >.btn {
            min-width: 97px;
            height: 32px;
            padding: 0 10px;
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
                // border-color: var(--main-color);
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
}</style>
