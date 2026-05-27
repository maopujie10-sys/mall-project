<template>
    <div class="Successful_Operation" style="min-height: 100vh;">
        <van-nav-bar safe-area-inset-top :title="$t('支付成功')" fixed class="nav-bar" left-arrow @click-left="onClickLeft">
        </van-nav-bar>
        <div class="wanc">
            <img src="@/assets/image/index/wanc.png" />
        </div>
        <div class="title">{{ $t("支付成功") }}</div>
        <div class="text">
            {{ $t("接收者") }}：{{ (orderInfo.contacts || '') + " " + (orderInfo.phone || '') }}
        </div>
        <div class="text mt10">{{ $t("收件地址") }}：{{ orderInfo.address }}</div>
        <div class="text mt20">
            {{ $t("收货地址错误？现在联系") }}
            <span @click="goToService">{{ $t("客服") }}</span>
        </div>
        <div class="but but-one" @click="goToHome">{{ $t("返回首页") }}</div>
        <div class="but but-two mt20" @click="goToOrder">{{ $t("检查订单") }}</div>
    </div>
</template>
<script>
import { NavBar } from "vant";
import { orderInfoPay } from "@/API/commodity";
export default {
    data() {
        return {
            orderInfo: {},
        };
    },
    components: {
        [NavBar.name]: NavBar,
    },
    mounted() {
        this.init();
    },
    created() { },
    methods: {
        init() {
            let id = this.$route.query.orderId;
            if (id) {
                id = id.split(",");
            }
            let data = {
                orderId: id[0],
                ades: 0,
                type: 1
            };
            orderInfoPay(data).then((res) => {
                this.orderInfo = res.orderInfo;
                // if(this.orderInfo.phone){
                //   this.orderInfo.phone=this.orderInfo.phone.substring(0,3)+'******'+this.orderInfo.phone.substring(this.orderInfo.phone.length-3)
                // }
            });
        },
        onClickLeft() {
            this.$router.push(this.$route.query?.isCart == 1 ? "/cart" : "-1");
        },
        goToHome() {
            this.$router.push("/");
        },
        goToOrder() {
            this.$router.push("/order");
        },
        goToService() {
            const path = this.$store.state.multiItem[process.env.VUE_APP_ITEM_NAME].customer_service
            if (path) {
                
                if(window.plus) {
                    plus.runtime.openURL(path);
                } else {
                    window.open(path)
                }
            } else {
                this.$router.push({ path: "customerServiceIndex?path=customerService" });
            }
        },
    },
};
</script>
<style lang="scss" scoped>
.Successful_Operation {
    font-size: 14px;
    background: #fff;
    padding-top: 46px;
    color: #333333;

    .wanc {
        text-align: center;
        padding-top: 70px;

        img {
            width: 52px;
            height: 52px;
        }
    }

    .title {
        text-align: center;
        font-size: 16px;
        font-weight: bold;
        padding: 30px 0;
    }

    .text {
        text-align: center;
        padding: 0 10px;
        font-size: 12px;

        span {
            
            color: var(--main-color);
        }
    }

    .but {
        margin: 0 10px;
        height: 45px;
        text-align: center;
        line-height: 45px;
        border-radius: 4px;
        font-size: 16px;
    }

    .but-one {
        border: 1px solid #333333;
        margin-top: 50px;
    }

    .but-two {
        background: var(--main-color);
        color: #fff;
    }

    .mt10 {
        margin-top: 10px;
    }

    .mt20 {
        margin-top: 20px;
    }
}
</style>
