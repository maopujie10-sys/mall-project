<template>
    <div class="footer yongqi">
        <div class="yongqi" v-for="(item, index) of listItem" :key="index" :class="[item.cls, { on: index === idx }]"
            @click="change(item, index)" style="
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                    ">
            <div class="image">
                <img :src="index === idx ? item.srcSelect : item.src"  />
                <span class="activeKey" v-if="index == 2 && cartNum">{{
                    cartNum > 99 ? "99+" : cartNum
                }}</span>
            </div>
            <!--      <div><i :class="index===idx?item.iconSelect:item.icon" v-if="!showIconOrSrc"></i></div>-->
            <span :class="['colorChange', { on: index === idx }]">
                {{ item.name }}
            </span>
        </div>
        <!--    <div class="qiangdan">-->
        <!--      <img v-if="!$store.state.qiangdan.qiangdan_status" @click="qiangdan_sj(true)" class="qiangdan1" src="@/assets/image/bottom/qiangdan.png" />-->
        <!--      <img v-if="$store.state.qiangdan.qiangdan_status" class="qiangdan1 rotateImages" src="@/assets/image/bottom/refresh.png" />-->
        <!--    </div>-->
    </div>
</template>
<script type="text/javascript">
// eslint-disable-next-line
/* eslint-disable */
import { Overlay, Toast, Icon } from "vant";
import { qiangdan_post, qiangdanxiangqing_post } from "@/API/user";
import { mapGetters, mapMutations, mapState } from "vuex";
import { isLogin } from '@/utils/utis'
export default {
    props: {
        idx: {
            type: Number,
            default: 0,
        },
    },
    data() {
        return {
            qiangdan_show: false,
            timer_shijian: "",
            cartNum: 0,
            listItem: [
                {
                    cls: "home",
                    name: this.$t("首页"),
                    path: "/home",
                    icon: 'shouye',
                    src: require("@/assets/image/bottom/home.png"),
                    srcSelect: require(`@/assets/${process.env.VUE_APP_ITEM_NAME}/home2.png`),
                },
                {
                    cls: "commodity",
                    name: this.$t("商品"),
                    path: "/commodity",
                    icon: "24gf-appsBig6",
                    src: require("@/assets/image/bottom/chongzhi.png"),
                    srcSelect: require(`@/assets/${process.env.VUE_APP_ITEM_NAME}/chongzhi2.png`),
                },
                // {
                //   cls: "shop",
                //   name: this.$t("店铺"),
                //   path: "/shop",
                //   src: require('@/assets/image/bottom/company_normal.png'),
                //   srcSelect: require('@/assets/image/bottom/company_normal2.png'),
                // },
                {
                    cla: "cart",
                    name: this.$t("购物车"),
                    path: "/cart",
                    icon: 'gouwuchefill',
                    src: require("@/assets/image/bottom/renwu.png"),
                    srcSelect: require(`@/assets/${process.env.VUE_APP_ITEM_NAME}/renwu2.png`),
                },
                {
                    cla: "me",
                    name: this.$t("我的"),
                    path: "/me",
                    icon: "wode",
                    src: require("@/assets/image/bottom/wode.png"),
                    srcSelect: require(`@/assets/${process.env.VUE_APP_ITEM_NAME}/wode2.png`),
                },
            ]
        };
    },
    components: {
        [Icon.name]: Icon,
        [Overlay.name]: Overlay,
    },
    activated() {
        this.getChartNum();
    },
    mounted() {
        this.getChartNum();
    },
    updated() {
        this.getChartNum();
    },
    computed: mapState({
        count: (state) => state.qiangdan.count,
    }),
    methods: {
        ...mapMutations(["setQiangdan"]),
        ...mapMutations(["qiangdan_status_sj"]),
        ...mapMutations(["qiangdan_tanchuang_sj"]),
        getChartNum() {
            let productList = this.$ls.get("productList")
            this.cartNum = isLogin() ? productList?.length : 0
            // this.cartNum = JSON.parse(
            //     localStorage.getItem("productList")
            // )?.value.reduce(function (prev, cur) {
            //     return (prev += cur.count);
            // }, 0);

        },
        qiangdan_sj(e) {
            const t = this;
            this.qiangdan_status_sj(e);
            qiangdan_post({})
                .then((res) => {
                    // brush_time: 5
                    // orderId: "3987503220907183731"
                    var time = res.brush_time * 1000;
                    t.timer_shijian = setTimeout(function () {
                        t.qiangdan_xq(res.orderId);
                    }, time);
                })
                .catch(function (err) {
                    // Toast('网络波动请刷新页面');
                    t.qiangdan_status_sj(false);
                });
        },
        qiangdan_xq(e) {
            var t = this;
            qiangdanxiangqing_post({ orderId: e })
                .then((res) => {
                    this.qiangdan_status_sj(false);
                    this.setQiangdan(res);
                    this.qiangdan_tanchuang_sj(true);
                })
                .catch(function (err) {
                    // Toast('网络波动请刷新页面');
                    t.qiangdan_status_sj(false);
                });
        },
        change(item, index) {
            if (this.$route.path !== item.path) {
                this.$router.push({ path: item.path });
            }
            this.$emit("change", index);
        },
    },
    watch: {
        count(val) {
            this.getChartNum()
        },
        // '$route'(form, to) {
        //     if (to.path == '/language') {
        //         console.log(`getStorage('lang') ::->`, getStorage('lang'));
        //         // this.handleReload()
        //         // this.$i18n.locale = 'en';
        //         // // 'en'  'tw'  'cn'
        //         // console.log(`this.$i18n ::->`, this.$i18n);
        //     }
        // }
    },
    beforeDestroy() {
        clearTimeout(this.timer_shijian);
    },
};
</script>
<style lang="scss" scoped>
.rotate_bg {
    width: 500px;
    height: 500px;
    background: #59d1b6;
    margin: 200px auto;
}

.rotateImages {
    -webkit-animation: myRotate 1s linear infinite;
    animation: myRotate 1s linear infinite;
}

@-webkit-keyframes myRotate {
    0% {
        -webkit-transform: rotate(0deg);
    }

    50% {
        -webkit-transform: rotate(180deg);
    }

    100% {
        -webkit-transform: rotate(360deg);
    }
}

@keyframes myRotate {
    0% {
        -webkit-transform: rotate(0deg);
    }

    50% {
        -webkit-transform: rotate(180deg);
    }

    100% {
        -webkit-transform: rotate(360deg);
    }
}

.qiangdan {
    width: 44px;
    height: 44px;
    background: white;
    border-radius: 50%;
    position: absolute;
    bottom: 27px;
    display: flex;
    justify-content: center;
    align-items: center;

    //z-index: 999;
    .qiangdan1 {
        width: 38px;
        height: 38px;
    }
}

.footer {
    box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.08);
    display: flex;
    justify-content: center;
    // position: fixed;

    /*left: 0;*/
    bottom: 0;
    //box-sizing: border-box;
    background: #ffffff;
    /*max-width: 100%;*/
    width: 375px;
    height: 56px;
    //z-index: 2000;
}

.yongqi {
    flex: 1;
    padding: 5px;
    box-sizing: border-box;
    font-size: 12px;
    width: 100%;
}

.image {
    position: relative;
    .icon {
        font-size: 25px;
    }
}

.image img {
    width: 20px;
    height: 20px;
    //background: white;
}

div>span {
    display: block;
    font-style: normal;
    font-weight: 400;
    font-size: 10px;
    line-height: 12px;
    /* identical to box height */
    position: relative;
    text-align: center;
    color: #aaaaaa;
    margin-top: 4px;
    white-space: nowrap;

}

.activeKey {
    position: absolute;
    min-width: 15px;
    min-height: 15px;
    line-height: 15px;
    padding: 1px;
    text-align: center;
    border-radius: 10px;
    background-color: red;
    color: #ffffff;
    top: -13px;
    right: -13px;
}

.on {
    color: var(--main-color);
}
</style>
