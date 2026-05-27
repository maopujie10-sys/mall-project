<template>
    <div class="mall">
        <van-nav-bar safe-area-inset-top fixed class="nav-bar" left-arrow @click-left="onClickLeft" :title="$t('订单确认')" />
        <div style="width: 100%; height: 46px"></div>
        <div class="address-wrap" v-if="addressList.length == 0" @click="openAddress">
            <div class="left">
                <img src="../../assets/image/me/dizhi.png" />
                {{ $t("您还没有添加送货地址") }}
            </div>
            <div class="right">
                <van-icon name="arrow" class="arrow-right" />
            </div>
        </div>
        <div class="address-wrap-disabled" v-else @click="openAddress">
            <div class="left">
                <div class="address-title">
                    <img src="../../assets/image/me/dizhi1.png" />
                    <span>{{ addressInfo.contacts }} {{ addressInfo.phone }}</span>
                </div>
                <div class="address-details">
                    {{ addressInfo.address }}
                </div>
            </div>
            <div class="right" >
                <van-icon name="arrow" class="arrow-right" />
            </div>
        </div>
        <van-pull-refresh v-model="refreshing" @refresh="onRefresh" :pulling-text="$t('下拉即可刷新')"
            :loosing-text="$t('释放即可刷新')" :loading-text="$t('加载中')">
            <template>
                <div v-for="(item, index) in list" :key="item.key" class="mall-detail">
                    <van-checkbox class="mall-title" v-model="item.checkedAll"
                        @change="handleCheckItemAll(item.checkedAll, index)">{{ item.sort }}</van-checkbox>
                    <div class="mall-item">
                        <van-checkbox-group v-model="item.checkedValue" @change="mathMoney">
                            <template v-for="(i, n) in item.child">
                                <van-checkbox class="mall-item-checkbox" :name="i.tempId" :key="i.key"
                                    v-if="n < item.moreNum" @click="handlecheckItemClick(item, index, n)">
                                    <div class="mall-item-child">
                                        <div class="mall-item-child-img">
                                            <img :src="currentCoverImg || i.img" class="img" />
                                        </div>
                                        <div style="width: 75%; margin-left: 6px">
                                            <p class="describe">
                                                {{
                                                    i.describe?.length > 42
                                                    ? i.describe.slice(0, 42) + "..."
                                                    : i.describe
                                                }}
                                            </p>
                                            <p v-if="i.attributes" class="sku_box">
                                                <span class="attribute" v-for="(j, p) in i.attributes.attrs" :key="p"
                                                    v-if="j.attrName && j.attrValueName">
                                                    {{ j.attrName }}:{{ j.attrValueName }}</span>
                                            </p>
                                            <div class="price">

                                                <span>${{ priceFormat(i.price) }}</span>
                                                <div class="stepper" @click.stop="mathMoney">
                                                    <van-stepper :disable-input="true" :max="maxBuyNum" integer
                                                        v-model="i.count" @change="mathMoney" />
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </van-checkbox>
                            </template>

                            <div class="show-more" v-show="
                                item.child.length > 1 && item.moreNum < item.child.length
                            " @click="item.moreNum += 2">
                                <p>{{ $t("查看更多") }}</p>
                                <img src="../../assets/image/index/down-icon.png" />
                            </div>
                        </van-checkbox-group>
                    </div>
                </div>
                <van-cell-group inset>
                    <van-cell :title="$t('物品金额')" :value="'$' + priceFormat(total.money)" />
                    <!-- <van-cell :title="$t('折扣')" :value="'-$'+total.discount" class='font-color'/> -->
                    <van-cell :title="$t('运送费')" :value="'+$' + (total.freight > 0 ? priceFormat(total.freight) : '0.00')"
                        class="font-color" />
                    <van-cell :title="$t('税费')" :value="'+$' + (total.freight > 0 ? priceFormat(total.freight) : '0.00')"
                        class="font-color" />
                    <van-cell :title="$t('总计')" :value="'$' + (total.mathMoney > 0 ? priceFormat(total.mathMoney) : '0.00')"
                        class="font-color" />
                </van-cell-group>
                <!-- 付款方式 -->
                <div class="payment-cell" v-show="false">
                    <van-checkbox-group v-model="paymentChecked" style="margin: 10px 0">
                        <van-cell-group inset>
                            <van-cell clickable title="Blance" icon="shop-o">
                                <span class="yellow-color">($666.12)</span>
                                <template #right-icon>
                                    <van-checkbox name="Blance" @click.stop />
                                </template>
                            </van-cell>
                            <van-cell clickable title="PayPal" icon="shop-o">
                                <span>({{ $t("尚未开放") }})</span>
                                <template #right-icon>
                                    <van-checkbox name="PayPal" @click.stop disabled />
                                </template>
                            </van-cell>
                            <van-cell clickable title="Visa" icon="shop-o">
                                <span>({{ $t("尚未开放") }})</span>
                                <template #right-icon>
                                    <van-checkbox name="Visa" @click.stop disabled />
                                </template>
                            </van-cell>
                            <van-cell clickable title="Masercard" icon="shop-o">
                                <span>(Additional <span class="yellow-color">$23</span> handing fee
                                    is required)</span>
                                <template #right-icon>
                                    <van-checkbox name="Masercard" @click.stop />
                                </template>
                            </van-cell>
                        </van-cell-group>
                    </van-checkbox-group>
                </div>
            </template>
        </van-pull-refresh>
        <div class="mall-bottom">
            <span>{{ $t("总计") }}
                <span class="price">${{ total.mathMoney }}</span></span>
            <span>{{ $t("选择") }} <span class="piece">{{ total.piece }}</span>
                {{ $t("个") }}</span>
            <van-button class="button" color="rgba(233, 157, 56, 1)" @click="handleConfri">{{ $t("确认") }}</van-button>
        </div>
        <div style="width: 100%; height: 60px"></div>
    </div>
</template>
<script>
import {
    // NavBar,
    // Tab,
    // Tabs,
    PullRefresh,
    List,
    Checkbox,
    CheckboxGroup,
    Stepper,
    CellGroup,
    Cell,
    Popup,
    Icon,
    Toast,
} from "vant";
import { dizhi_liebiao_post } from "@/API/user";
import { orderSubmit } from "@/API/commodity";
import { ref } from "vue";
import { priceFormat } from '@/utils/utis'
// import EnterPassword from "@/components/EnterPassword/index.vue";
import Big from 'big.js'
export default {
    setup() {
        const checked = ref(["a", "b"]);
        const checkedAll = ref(false);
        const checkboxGroup = ref(null);
        const checkAll = () => {
            checkboxGroup.value.toggleAll(true);
        };
        return {
            checked,
            checkedAll,
            checkAll,
            checkboxGroup,
        };
    },
    data() {
        return {
            priceFormat,
            type: 2, //1直接购买,2购物车购买
            goodsInfo: {}, //单个商品信息
            bugNum: 1, //单个商品选中的数量
            refreshing: false,
            paymentChecked: [],
            checkboxList: [
                { key: 0, title: "Blance", icon: "", open: true },
                { key: 1, title: "PayPal", icon: "", open: false },
                { key: 2, title: "Visa", icon: "", open: false },
                { key: 3, title: "Masercard", icon: "", open: false },
            ],
            list: [],
            addressList: [],
            addressInfo: {},
            orderList: [],
            total: {}, //金额计算数据
            skuId: "",
            attributes: [],
            currentCoverImg: '',
            maxBuyNum: localStorage.getItem('maxBuyNum') || 500,
        };
    },
    components: {
        [List.name]: List,
        [PullRefresh.name]: PullRefresh,
        [Checkbox.name]: Checkbox,
        [CheckboxGroup.name]: CheckboxGroup,
        [Stepper.name]: Stepper,
        [Cell.name]: Cell,
        [CellGroup.name]: CellGroup,
        [Popup.name]: Popup,
        [Icon.name]: Icon,
        [Toast.name]: Toast,
    },
    created() {
        //获取路由参数
        try {
            let { type, goodsInfo, bugNum, currentCoverImg } = this.$route.query;
            this.currentCoverImg = currentCoverImg;
            this.type = type;
            this.goodsInfo = JSON.parse(goodsInfo);
            this.bugNum = bugNum;
        } catch (e) {
            console.log(e);
        }

        this.dizhiliebiao();
        //跳转商品展示
        this.getProduct();

        this.init();
    },
    methods: {
        init() {
            //全选
            if (this.list.length > 0) {
                this.list.forEach((item) => {
                    item.checkedAll = true;
                    if (item.child.length > 0) {
                        item.checkedValue = item.child.map(child => child?.tempId);
                    }
                });
            }
            //计算总金额
            this.mathMoney();
        },
        mathMoney() {
            this.total = {
                money: 0,
                piece: 0,
                discount: 0,
                freight: 0,
                goodsTax: 0,
                mathMoney: 0,
                discountPrice: 0,
            };
            let count = 0
            this.list.forEach((item) => {
                count += item.checkedValue.length
                // this.total.piece = item.checkedValue.length
                item.child.length > 0 &&
                    item.child.forEach((child) => {
                        //num<item.moreNum&&
                        if (item.checkedValue.includes(child.tempId)) {
                            this.total.money = this.$plus(this.total.money, this.$operation(child.price, child.count, 'times'));
                            this.total.freight = this.$plus(this.total.freight, this.$operation(child.freightAmount, child.count, 'times'))
                            this.total.goodsTax = this.$plus(this.total.goodsTax, this.$operation(child.goodsTax, child.count, 'times'))
                        }
                    });
            });
            this.total.piece = count
            this.total.mathMoney = new Big(this.total.money).plus(this.total.freight).plus(this.total.goodsTax).minus(this.total.discount)
            this.total.mathMoney = priceFormat(this.total.mathMoney)
        },
        getProduct() {
            if (this.type == 1) {
                if (this.$route.query.skuId !== "-1") {
                    this.skuId = this.$route.query.skuId || 0;
                    this.attributes = this.goodsInfo.canSelectAttributes.skus.filter(
                        (i) => i.skuId == this.skuId
                    )[0];
                }

                // console.log("attributes ->", attributes);
                let item = {
                    key: 0,
                    sort: this.goodsInfo.storeName,
                    checkedAll: false,
                    checkedValue: [],
                    moreNum: 2,
                    child: [
                        {
                            key: 1,
                            img: this.goodsInfo.imgUrl1 || this.$defaultGoodsImage,
                            price: this.goodsInfo.discountPrice
                                ? this.goodsInfo.discountPrice
                                : this.goodsInfo.sellingPrice,
                            describe: this.goodsInfo.name,
                            attributes: this.attributes || [],
                            count: this.bugNum,
                            id: this.goodsInfo.id,

                            freightAmount: this.goodsInfo.freightAmount,
                            goodsTax: this.goodsInfo.goodsTax,
                        },
                    ],
                };
                this.list.push(item);
            } else {
                //   console.log("this.goodsInfo ->", this.list);
                this.list = this.$ls.get("cartList");
            }
        },
        // 单选
        handlecheckItemClick(item, index, n) {
            if (this.list[index].child[n].selected == undefined) this.list[index].child[n].selected = true
            this.list[index].child[n].selected = !this.list[index].child[n].selected;
            let count = 0;
            let num = 0;
            let len = this.list[index].child.length;
            this.list[index].child.forEach((sub) => {
                if (sub.selected) count += 1;
                else num += 1;
                if (num == len) this.list[index].checkedAll = false;
                if (count != 0) this.list[index].checkedAll = true;
            });

        },
        //类全选
        handleCheckItemAll(value, index) {
            this.list[index].checkedValue = [];
            this.$nextTick(() => {
                this.list[index].child.forEach((item, num) => {
                    item.selected = value;
                    value && this.list[index].checkedValue.push(item.tempId);
                });
            });
            // this.list[index].checkedValue = [];
            // if (value) {
            //   this.list[index].child.forEach((item, num) => {
            //     if (num < this.list[index].moreNum) {
            //       this.list[index].checkedValue.push(item.id);
            //     }
            //   });
            // }
            this.mathMoney();
        },
        onRefresh() {
            // 清空列表数据
            this.finished = false;
            this.loading = true;
            this.onLoad();
        },
        onLoad() {
            if (this.refreshing) {
                this.refreshing = false;
            }
        },
        onClickLeft() {
            this.$router.go(-1);
            // this.$router.push({ path: "/cart" });
        },
        // 确认
        handleConfri() {
            if (!(this.total.piece > 0)) {
                Toast(this.$t("请选择要购买的商品"));
                return;
            }
            let dataJson = {
                orderInfo: "",
                addressId: this.addressInfo.id,
            };
            if (this.type == 1) {
                dataJson.orderInfo = `${this.goodsInfo.id},${this.$route.query.skuId || "-1"
                    },${this.list[0].child[0].count}`;
            } else {
                this.list.forEach((item) => {
                    item.child.length > 0 &&
                        item.child.forEach((child) => {
                            if (item.checkedValue.includes(child.tempId)) {
                                dataJson.orderInfo += `${child.id},${child?.skuId || "-1"},${child.count
                                    },`;
                            }
                        });
                });
            }
            orderSubmit(dataJson).then((res) => {
                this.orderList = res.orderList;
                let productList = this.$ls.get("productList") || [];
                let ids = [];
                productList?.forEach((item) => {
                    this.list.forEach(({ child }) => {
                        child.forEach(({ id, selected }) => {
                            if (id == item.id && selected) ids.push(id);
                        });
                    });
                });
                this.$router.push({
                    path: "/PendingPayment",
                    query: {
                        orderList: JSON.stringify(this.orderList),
                        total: this.total.mathMoney,
                        ids,
                        isCart: this.$route.query?.isCart || 0,
                    },
                });
                // this.pwtStatus=true
            });
        },
        //获取地址列表
        dizhiliebiao() {
            dizhi_liebiao_post({})
                .then((res) => {
                    if (!res.pageList?.[0]?.country) return
                    this.addressList = res.pageList;
                    let address = JSON.parse(this.$ls.get("address"));
                    if (address) {
                        this.addressInfo = address;
                        this.$ls.remove("address");
                        return;
                    }
                    this.addressList.map((item) => {
                        item.phone =
                            item.phone.indexOf("|") > -1
                                ? item.phone.split("|")[1]
                                : item.phone;
                        if (item.use === 1) {
                            this.addressInfo = item;
                        }
                    });
                })
                .catch(() => { });
        },
        openAddress() {
            this.$router.push("/AddressList?c=1");
        },
    },

};
</script>
<style lang="scss" scoped>
.attribute {
    font-size: 12px;
    color: #333;
    margin-right: 10px;
}

.mall {
    position: relative;
    background: rgba(238, 238, 238, 1);
    min-height: 100%;
    font-size: 14px;
    box-sizing: border-box;
    overflow-x: hidden;
    .mall-detail {
        margin-bottom: 20px;
        padding: 0 15px;

        .mall-title {
            font-size: 14px;
            margin: 14px 0;
        }

        .mall-item {
            // width: 345px;
            background: #fff;
            height: auto;

            .mall-item-child {
                width: 100%;
                display: flex;
                justify-content: space-around;
                align-items: center;

                .mall-item-child-img {
                    width: 62px;
                    height: 62px;
                    display: table-cell;

                    img {
                        max-width: 100%;
                        max-height: 100%;
                        display: block;
                        margin: auto;
                    }
                }

                .price {
                    color: var(--main-color);
                    font-size: 16px;
                    font-weight: 500;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-top: 10px;
                }

                .describe {
                    font-size: 14px;
                    color: #000;
                    width: 100%;
                    // height: 40px;
                    width: 195px;
                    display: -webkit-box;
                    -webkit-box-orient: vertical;
                    -moz-box-orient: vertical;
                    box-orient: vertical;
                    -webkit-line-clamp: 2;
                    line-clamp: 2;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }

                .stepper {
                    width: 100%;
                    display: flex;
                    justify-content: flex-end;
                    align-items: center;
                    margin-right: 10px;
                }
            }
        }

        .mall-item-checkbox {
            border-bottom: 1px solid #eee;
            width: 100%;
            min-height: 107px;
            padding-bottom: 10px;

            .sku_box {
                display: flex;
                flex-wrap: wrap;
            }
        }

        .mall-item-checkbox:nth-last-child(2) {
            border: none;
        }

        .show-more {
            color: #000;
            font-size: 12px;
            text-align: center;

            img {
                width: 16px;
                height: 16px;
            }
        }
    }

    .mall-empty {
        height: calc(100vh);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;

        .img {
            width: 100px;
        }

        .text {
            font-size: 16px;
            margin: 20px 0;
        }

        .button {
            min-width: 100px;
            height: 40px;
        }
    }

    .mall-bottom {
        width: 100%;
        background: #fff;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 14px;
        padding: 8px 7px;
        position: fixed;
        bottom: 0;
        box-sizing: border-box;
        .checkbox {
            font-size: 14px;
            margin: 14px 0;
        }

        .price {
            color: var(--main-color);
            font-size: 16px;
            font-weight: 600;
        }

        .piece {
            color: var(--main-color);
        }

        .button {
            min-width: 100px;
        }
    }
}

.address-wrap {
    height: 45px;
    margin: 0 15px;
    background: url("../../assets/image/me/bg.png") no-repeat center center;
    background-size: cover;
    display: flex;
    padding: 0 15px;
    align-items: center;
    margin-top: 15px;

    .left {
        flex: 1;
        color: #ffffff;
        display: flex;
        align-items: center;

        img {
            height: 22px;
            margin-right: 10px;
        }
    }

    .right {
        .arrow-right {
            color: #ffffff;
            font-size: 16px;
        }
    }
}

.address-wrap-disabled {
    background: #fff;
    margin: 0 15px;
    margin-top: 15px;
    display: flex;
    padding: 20px 15px 20px 15px;
    align-items: center;
    overflow: hidden;
    box-sizing: border-box;
    .left {
        flex: 1;

        .address-title {
            display: flex;
            align-items: center;
            color: #333333;

            img {
                height: 22px;
                margin-right: 10px;
            }
        }

        .address-details {
            color: #999999;
            width: 240px;
            word-wrap: break-word;
            padding-left: 35px;
            margin-top: 10px;
        }
    }

    .right {
        .arrow-right {
            font-size: 16px;
        }
    }
}

/deep/ .van-checkbox__icon--checked .van-icon {
    background-color: var(--main-color) !important;
    border-color: var(--main-color) !important;
}

/deep/ .van-checkbox__icon {
    font-size: 16px !important;
    padding: 0 11px;
}

.payment-cell /deep/ .van-cell__value {
    text-align: start;
}

.font-color /deep/ .van-cell__value {
    color: var(--main-color);
}

.yellow-color {
    color: var(--main-color);
}

/deep/ .van-checkbox__label--disabled {
    color: #333333;
}

/deep/ .van-checkbox__label {
    flex-grow: 1;
    width: 100%;
}

/deep/ .van-button {
    margin-right: 14px;
}

/deep/ .van-stepper {
    margin-right: 13px;
}

/deep/ .van-pull-refresh {
    padding-bottom: 20px;
}
</style>