<template>
    <div class="PendingPayment">
        <van-nav-bar safe-area-inset-top fixed left-arrow @click-left="onClickLeft" />
        <div class="pay-header">
            <div class="title">
                {{ $t("待付款") }}
            </div>
            <!-- <div class="text"> The order will be closed automatically</div> -->
        </div>
        <div class="pay-list">
            <div class="header-title">
                {{ $t("付款方式") }}
            </div>
            <div class="list">
                <div class="item" v-for="(item, index) of payMethod" :key="index">
                    <div class="left">
                        <img class="icon" :src="icons[index]" />
                        <div class="title">{{ item.name }}</div>
                        <div class="text" v-if="index == 0">
                            (&nbsp;<span>${{ money ? priceFormat(money) : '0.00' }}</span>&nbsp;)
                        </div>
                        <div class="not_open" v-else>
                            ({{ item.balance }})
                        </div>
                    </div>
                    <div class="right">
                        <img src="@/assets/image/public/gou.png" v-if="item.selected" />
                        <span v-else></span>
                    </div>
                </div>
            </div>
        </div>
        <div class="bottom-wrap">
            <div class="fixed-wrap">
                <div class="left">
                    {{ $t("总计") }}：
                    <span>${{ total }}</span>
                </div>
                <div class="right" @click="handlePay">{{ $t("支付") }}</div>
            </div>
        </div>
        <!-- 密码弹窗 -->
        <van-popup v-model="pwtStatus" position="bottom">
            <enter-Password :isPasswordShow="pwtStatus" @close="pwtStatus = false"
                @getPassword="getPassword"></enter-Password>
        </van-popup>
    </div>
</template>
<script>
import EnterPassword from "@/components/EnterPassword/index.vue";
import { NavBar, Popup } from "vant";
import { huoquyue_post, shifoushzhi_zijinmima_post } from "@/API/user";
import { orderPay } from "@/API/commodity";
import { priceFormat } from '@/utils/utis'

export default {
    data() {
        return {
            money: 0,
            pwtStatus: false,
            orderList: [],
            total: 0,
            payMethod: [
                { name: this.$t('余额'), balance: '', selected: true },
                { name: 'PayPal', balance: this.$t('您所在的地区尚未开放'), selected: false },
                { name: 'Visa', balance: this.$t('您所在的地区尚未开放'), selected: false },
                { name: 'Mastercard', balance: this.$t('您所在的地区尚未开放'), selected: false },
            ],
            icons: [
                require('@/assets/image/public/qianbao.png'),
                require('@/assets/image/public/pay.png'),
                require('@/assets/image/public/visa.png'),
                require('@/assets/image/public/master.png'),
            ],
            priceFormat
        };
    },
    components: {
        [NavBar.name]: NavBar,
        [Popup.name]: Popup,
        [EnterPassword.name]: EnterPassword,
    },
    mounted() {
        this.getMoneyInfo();
        this.orderList = JSON.parse(this.$route.query.orderList);
        this.total = this.$route.query.total;
        localStorage.removeItem("cartList");
        //   localStorage.removeItem("productList");
        // console.log(
        //   " 比较->",
        //   this.RemoveSameItem(
        //     this.$ls.get("cartList"),
        //     this.orderList,
        //     "checkedAll"
        //   )
        // );
    },
    created() { },
    methods: {
        // RemoveSameItem(listOne, listTwo, key) {
        //   let newList = [];
        //   loop: for (let itemOne of listOne) {
        //     for (let itemTwo of listTwo) {
        //       if (itemOne[key] == itemTwo[key]) {
        //         continue loop;
        //       }
        //     }
        //     newList.push(itemOne);
        //   }
        //   return newList.concat(listTwo);
        // },
        clear() {
            // const list=[]
            // this.$ls.get("cartList") = list;
        },
        onClickLeft() {
            history.go(-2);
        },
        //获取资金密码
        getMoneyInfo() {
            huoquyue_post().then((res) => {
                this.money = res.money;
            });
        },
        //pay
        handlePay() {
            shifoushzhi_zijinmima_post({}).then((res) => {
                if (res.safeword == 1) {
                    this.pwtStatus = true;
                } else {
                    this.$router.push({ path: "/FundPasswordSettings" });
                }
            });
        },
        //输入完密码
        getPassword(value) {
            let data = {
                safeword: value.substring(0, 6),
                orderId: "",
            };
            this.orderList.forEach((item) => {
                data.orderId += item.orderId + ",";
            });
            let productList = this.$ls.get("productList") || [];
            const ids = this.$route.query.ids || []
            // 购物车多个物品时
            // 我也不知道为啥循环一次删不完  就多循环两次...
            productList.forEach((item, index) => {
                if (ids?.includes(item.id)) {
                    productList.splice(index, 1)
                }
            })
            // 我也不知道为啥循环一次删不完  就多循环两次...
            productList.forEach((item, index) => {
                if (ids?.includes(item.id)) {
                    productList.splice(index, 1)
                }
            })
            // 我也不知道为啥循环一次删不完  就多循环两次...
            productList.forEach((item, index) => {
                if (ids?.includes(item.id)) {
                    productList.splice(index, 1)
                }
            })
            orderPay(data).then(() => {
                // 如果购物车物品跟单独购买的商品一样时会把购物车那个商品清了, 
                // 如果不需要这个判断isCart=0是单独购买 isCart=1是购物车点进来的购买
                this.$ls.set("productList", productList)
                this.$router.push({
                    path: "/SuccessfulOperation",
                    query: { orderId: data.orderId, isCart: this.$route.query?.isCart || 0 },
                });
            });
        },
    },
};
</script>
<style lang="scss" scoped>
.PendingPayment {
    font-size: 14px;
    background: #eef2f6;
    height: 100%;

    .pay-header {
        height: 220px;
        background: url("@/assets/image/me/bg2.png") no-repeat center;
        background-size: 100% 100%;
        padding: 0 15px;

        .title {
            font-size: 16px;
            color: #ffffff;
            font-weight: 500;
            padding-top: 100px;
        }

        .text {
            color: #ffffff;
            font-size: 12px;
            padding-top: 10px;
        }

    }

    .pay-list {
        margin: 0 15px;
        background: #fff;
        margin-top: -40px;
        padding: 0 10px;

        .header-title {
            height: 60px;
            line-height: 60px;
            border-bottom: 1px solid #eeeeee;
            color: #000000;
        }

        .list {
            .item {
                display: flex;
                align-items: center;
                border-bottom: 1px solid #eeeeee;
                padding: 15px 0;
                &:nth-child(1) {
                    .icon {
                        width: 16px;
                        height: 16px;
                    }
                }
                &:nth-child(2) {
                    .icon {
                        width: 13px;
                        height: 16px;
                    }
                }
                &:nth-child(3) {
                    .icon {
                        width: 18px;
                        height: 16px;
                    }
                }
                &:nth-child(4) {
                    .icon {
                        width: 18px;
                        height: 10px;
                    }
                }
                .left {
                    flex: 1;
                    display: flex;
                    align-items: center;

                    img {
                        width: 22px;
                        display: block;
                    }

                   

                    .title {
                        font-size: 16px;
                        margin: 0 10px;
                    }

                    .text {
                        font-weight: 500;
                        
                        color: var(--main-color);
                        font-size: 16px;
                    }

                    .not_open {
                        font-size: 12px;
                        color: #999;
                    }
                }
            }
        }

        .right {
            span {
                display: block;
                width: 14px;
                height: 14px;
                background: #d9d9d9;
                border-radius: 50%;
            }

            img {
                width: 14px;
                height: 14px;
            }
        }
    }

    .bottom-wrap {
        background: #ffffff;
        height: 53px;
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;

        .fixed-wrap {
            margin: 0 15px;
            display: flex;
            align-items: center;
            margin-top: 6px;

            .left {
                flex: 1;
                font-size: 16px;

                span {
                    
                    color: var(--main-color);
                    font-weight: 500;
                }
            }

            .right {
                width: 108px;
                height: 40px;
                background: var(--main-color);
                color: #fff;
                font-size: 16px;
                text-align: center;
                line-height: 40px;
            }
        }
    }
}

/deep/ .van-nav-bar {
    background: transparent;
}

/deep/ .van-nav-bar .van-icon {
    color: #fff;
}

.van-hairline--bottom::after {
    border-bottom-width: 0px;
}
</style>
