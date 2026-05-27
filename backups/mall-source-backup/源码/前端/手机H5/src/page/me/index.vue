<template>
    <div class="my-container" style="min-height: 100vh;">
        <div class="my-header-content" :style="{ 'background-image': 'url(' + images.headerBg + ')' }">
            <div v-if="userInfo" class="user-info">
                <div class="avatar" @click="$router.push('/avatar/selection?avatar=' + userInfo?.avatar)">
                    <img :src="require(`@/assets/image/avatar/${userInfo?.avatar || 1}.png`)" alt="" />
                </div>
                <div class="name nowrap2">
                    <div class="user">{{ userInfo.username }}</div>
                    <div class="id" @click="copyId(userInfo.usercode)">
                        ID：<span>{{ userInfo.usercode }}</span><img :src="images.copy" alt="" />
                    </div>
                </div>
            </div>
            <div v-else class="user-info">
                <div class="avatar">
                    <img :src="images.avatar" alt="" />
                </div>
                <div class="login">
                    <span @click="openWin('/login', false)">{{ $t("登录") }}</span>/
                    <span @click="openWin('/register', false)">{{ $t("注册") }}</span>
                </div>
            </div>

            <div class="collect-content">
                <div class="item" @click="openWin('/collectGoods', true)">
                    <div>{{ goodNumber }}</div>
                    <p>{{ $t("商品收藏") }}</p>
                </div>
                <div class="item" @click="openWin('/collectShop', true)">
                    <div>{{ shopNumber }}</div>
                    <p>{{ $t("关注店铺") }}</p>
                </div>
            </div>
        </div>

        <div class="my-enter-content">
            <div class="balance-content" v-if="isShelves">
                <div class="tittle">
                    <p>{{ $t("账户余额") }}</p>
                    <span>(USD)</span>
                    <div class="icon" @click="hideMoney">
                        <img v-if="banClose" :src="images.bClose" alt="" />
                        <img v-else :src="images.bOpen" alt="" />
                    </div>
                </div>
                <div v-if="banClose" class="money">******</div>
                <div v-else class="money">
                    {{ userMoney && priceFormat(userMoney.money) || '0.00' }}
                </div>
                <div class="btn">
                    <div class="item" @click="openWin('/withdraw', true)">
                        {{ itemName == 'Hive' ? $t("提领") : $t("提现") }}
                    </div>
                    <div class="item" @click="openWin('/rechargeList', true)">
                        {{ itemName == 'Hive' ? $t("加值") : $t("充值") }}
                    </div>
                </div>
            </div>

            <div class="order-content">
                <div class="tittle">
                    <p>{{ $t("我的订单") }}</p>
                    <div class="all" @click="openOrder(false)">
                        <p>{{ $t("全部") }}</p>
                        <img class="image_reversed" :src="images.arrow" alt="" />
                    </div>
                </div>
                <div class="content">
                    <div class="item" v-for="(item, index) in orderNav" :key="index" @click="openOrder(item.type)">
                        <div class="count" v-if="+item.count > 0">
                            <span class="span">{{ item.count > 9 ? "9+" : item.count }}</span>
                        </div>
                        <div class="icon"><img :src="item.icon" alt="" /></div>
                        <p>{{ item.title }}</p>
                    </div>
                </div>
            </div>

            <div class="merchant-content" :style="{ 'background-image': 'url(' + images.bar + ')' }"
                @click="merchantJump()">
                <div>
                    <img :src="images.icon9" alt="" />
                    <p v-if="userInfo?.roletype == 1">{{ $t("商家登陆") }}</p>
                    <p v-else>{{ $t("商家入驻") }}</p>
                </div>
                <img class="image_reversed" :src="images.arrow1" alt="" />
            </div>
            <div class="loan-content" :style="{ 'background-image': 'url(' + images.loanBg + ')' }"
                @click="$router.push('/loan')" v-if="isShelves">
                <div>
                    <img :src="images.loanIcon" alt="" />
                    <p>{{ $t("贷款申请") }}</p>
                </div>
                <img class="image_reversed" :src="images.arrow1" alt="" />
            </div>
            <div class="nav-content">
                <div v-for="(item, index) in navData" :key="index" class="item" @click="openWin(item.path, item.needLogin)">
                    <div class="name">
                        <img :src="item.icon" alt="" class="icon" />
                        <p>{{ item.name }}</p>
                    </div>
                    <div class="arrow">
                        <p v-if="item.tips">{{ item.tips }}</p>
                        <img class="image_reversed" :src="images.arrow" alt="" />
                    </div>
                </div>
            </div>
        </div>
        <transition name="services">
            <div class="img_box" v-show="!isShowBtn" @click="toCustomerService" :style="{ bottom: isApp ? '12%' : '12%' }">
                <img src="@/assets/image/me/kefu.png" class="customer_service">
            </div>
        </transition>
        <Footer />

    </div>
</template>

<script>
import {
    keepGoodsCount,
    focusSellerCount,
    apicCuntOrderStatus,
} from "@/API/user";
import Footer from "@/components/Footer";
import { priceFormat } from '@/utils/utis'
const languageData = {
    "en": "English",
    "tw": "繁體中文",
    "cn": "简体中文",
    "de": 'Deutsch',
    "ja": '日本語',
    "ms": 'Melayu',
    "th": 'ภาษาไทย',
    "pt": 'Português',
    "es": 'Español',
    "ru": 'Русский',
    "el": 'Ελληνικά',
    "it": 'Italiano',
    "tr": 'Türkçe',
    "af": 'Afrikaans',
    "fr": 'français',
    "ko": '한국어',
};
import { Toast, Dialog, Badge } from "vant";
import { mapGetters } from "vuex";
import { isLogin } from "@/utils/utis";
import { getStatus, apiGetDownloadPath } from "@/API/commodity";
//   api/index!download-url.action  
//   下载链接
export default {
    name: "Me",
    components: {
        Footer,
        [Dialog.Component.name]: Dialog.Component,
        [Badge.name]: Badge,
    },
    data() {
        return {
            priceFormat,
            goodNumber: 0,
            shopNumber: 0,
            isShelves: !process.env.VUE_APP_PUT_ON_SHELVES,
            itemName: process.env.VUE_APP_ITEM_NAME,
            images: {
                headerBg: require(`@/assets/${process.env.VUE_APP_ITEM_NAME}/bg.png`),
                avatar: require("@/assets/image/me/avatar@2x.png"),
                copy: require("@/assets/image/me/fuzhi.png"),
                bClose: require("@/assets/image/me/close.png"),
                bOpen: require("@/assets/image/me/open.png"),
                arrow: require("@/assets/image/me/arrow.png"),
                arrow1: require("@/assets/image/me/arrow1.png"),
                bar: require(`@/assets/${process.env.VUE_APP_ITEM_NAME}/bar.png`),
                icon9: require("@/assets/image/me/icon9.png"),
                loanIcon: require('@/assets/image/me/loan-icon.png'),
                loanBg: require('@/assets/image/me/loan-bg.png'),
            },
            banClose: false,
            isShowBtn: false,
            orderNav: [
                {
                    count: "0",
                    icon: require(`@/assets/${process.env.VUE_APP_ITEM_NAME}/icon1.png`),
                    title: this.$t("待付款"),
                    type: "0",
                    name: "waitPayCount",
                },
                {
                    count: "0",
                    icon: require(`@/assets/${process.env.VUE_APP_ITEM_NAME}/icon2.png`),
                    title: this.$t("待发货"),
                    type: "1",
                    name: "waitDeliverCount",
                },
                {
                    count: "0",
                    icon: require(`@/assets/${process.env.VUE_APP_ITEM_NAME}/icon3.png`),
                    title: this.$t("待收货"),
                    type: "3",
                    name: "waitReceiptCount",
                },
                {
                    count: "0",
                    icon: require(`@/assets/${process.env.VUE_APP_ITEM_NAME}/icon4.png`),
                    title: this.$t("待评价"),
                    type: "4",
                    name: "waitEvaluateCount",
                },
                {
                    count: "0",
                    icon: require(`@/assets/${process.env.VUE_APP_ITEM_NAME}/icon5.png`),
                    title: this.$t("退款/售后"),
                    type: "6",
                    name: "refundCount",
                },
            ],
            navData: [
                {
                    icon: require("@/assets/image/me/icon6.png"),
                    name: this.$t("语言"),
                    tips: languageData[this.$store.getters.language || "en"],
                    path: "/language",
                    needLogin: false,
                },
                // {
                //     icon: require("@/assets/image/me/icon7.png"),
                //     name: this.$t("下载"),
                //     needLogin: false,
                //     path: location.origin + "/app.html?r=" + Math.random(),
                // },
                {
                    icon: require("@/assets/image/me/icon8.png"),
                    name: this.$t("设置"),
                    needLogin: true,
                    path: "/setting",
                },
            ],
            status: 0,
            scrollY: 0,
            isApp: window.plus ? true : false,
            paths: {
                'Argos': 'https://argos.me/',
                'MetaShop': 'https://e-metashop.com/',
                'Tongda': 'https://www.tongdashops.com/',
                'FamilyMart': 'https://familymartex.com/',
                'FamilyShop': 'https://www.familyshopit.com/',
                'Inchoi': 'https://Inchoishop.com/',
                'Hive': 'https://www.hivemalls.com/',
                'TikTokMall': 'https://tiktokmallin.com/',
                'Shop2u': 'https://shop2u.co/',
                'EShop': 'https://ml.thsjbvh.site/',
                'GreenMall': 'https://djeion.com/',
                'SM-wholesaleShop': 'https://justshopmall.com/',
                'ArgosShop': 'https://argosshoppro.com/',
                'Iceland': 'https://icelandmarts.com/',
                'INT Overstock': 'https://overstock8.me/',
                'TikTok-Wholesale': 'https://tiktok-wholesale.com/',
            }
        };
    },
    computed: {
        ...mapGetters({
            userInfo: "userInfo",
            userMoney: "userMoney",
        }),
    },
    created() {
        this.$store.dispatch("getUserInfo");
        this.$store.dispatch("getUserMoney");
        this.getCount();
        if (!window.plus) {
            // 下载链接地址
            // apiGetDownloadPath().then(path => {
            //     // if (this.itemName == 'Mbuy') this.navData[0].path = path
            //     // else this.navData[1].path = path
            //     this.navData[1].path = path
            // })
        }
        if (process.env.VUE_APP_PUT_ON_SHELVES) {
            this.navData.splice(0, 1);
        }
        // if (window.plus) {
        //     //app中删除下载按钮
        //     this.navData.splice(1, 1);
        // }
        this.banClose = localStorage.getItem("banClose") == "true";
    },
    mounted() {
        if (isLogin()) {
            this.getStatusInfo();
            // 获取数量
            apicCuntOrderStatus().then((res) => {
                // waitPayCount  代付款
                // waitDeliverCount  待发货
                // waitReceiptCount 待收货
                // waitEvaluateCount 待评价
                // refundCount 退款
                this.orderNav.forEach((item) => {
                    item.count = res?.[item.name];
                });
            });
        }
        setTimeout(() => {
            window.addEventListener("scroll", this.handleScroll);
        }, 1000);

    },
    methods: {

        handleToggle(path) {
            if (!isLogin()) {
                // Dialog.confirm({
                //     title: this.$t("您还未登录"),
                //     message: this.$t("是否跳转到登录页面"),
                //     confirmButtonText: this.$t("确认"),
                //     cancelButtonText: this.$t("取消"),
                // }).then(() => {
                //     this.$router.push('/login')
                // });
                this.$notifyWarn(this.$t("请先登录"));
                this.$router.push("/login");
                return false;
            } else {
                this.$router.push(path)
            }

        },
        copyId(code) {
            this.$copyText(code).then(
                () => {
                    Toast(this.$t("复制成功"));
                },
                () => {
                    Toast(this.$t("复制失败"));
                }
            );
        },
        open() {
            if (this.status === 0) {
                //   this.$router.push("/merchantSettled");
            } else {
                this.$router.push("/merchantDown");
            }
        },
        merchantJump() {
        
            if (this.userInfo?.roletype != 1) {
                // 商家入驻
                let lang = localStorage.getItem("lang") || "en";
                lang = lang.replace(/"/g, "");
                let path = window?.plus ? this.paths[this.itemName] : location.origin + '/'
                const url = `${path}promote/#/?lang=${lang}&avatar=${this.userInfo?.avatar || 1}`
                if (window.plus) {
                    plus.runtime.openURL(url)
                } else {
                    window.open(url)
                }
            } else {
                // 商家登陆
                let token = localStorage.getItem("token");
                let lang = localStorage.getItem("lang") || "en";
                let path = window?.plus ? this.paths[this.itemName] : location.origin + '/'
                window.location.href = `${path}www/#/?from=shop&token=${token}&lang=${lang}`
            }

            // const query = { url, title: this.$t("商家入驻") };
            // this.$router.push({
            //     path: "/iframe",
            //     query
            // });
        },
        openWin(path, needLogin) {
            if (needLogin && !isLogin()) {
                this.$notifyWarn(this.$t("请先登录"));
                this.$router.push("/login");
                return false;
            }
            if (path.indexOf('http') != -1) {

                if (window.plus) {
                    plus.runtime.openURL(path);
                } else {
                    window.open(path);
                }
            } else {
                scrollTo(0, 0)
                this.$router.push({
                    path,
                });
            }
        },

        openOrder(type) {
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
                return false;
            }

            const params = {
                path: "/order",
            };
            if (type) {
                params.query = {
                    type,
                };
            }

            this.$router.push(params);
        },
        //查询店铺申请进度
        getStatusInfo() {
            getStatus({}).then((res) => {

                this.status = res.status;
            });
        },
        getCount() {
            keepGoodsCount().then((res) => {
                this.goodNumber = res || 0;
            });
            focusSellerCount().then((res) => {
                this.shopNumber = res || 0;
            });
        },
        // 隐藏余额
        hideMoney() {
            this.banClose = !this.banClose
            localStorage.setItem('banClose', this.banClose)
        },
        toCustomerService() {
            const path = this.$store.state.multiItem[process.env.VUE_APP_ITEM_NAME].customer_service
            if (path) {
                if (window.plus) {
                    plus.runtime.openURL(path)
                    return
                } else {
                    window.open(path)
                }
            } else {
                this.$router.push('/customerServiceIndex?path=customerService')
            }
        },
        // 记录滚动条位置
        handleScroll() {
            let Y = document.documentElement.scrollTop || document.body.scrollTop
            if (Math.abs(Y - this.scrollY) > 300) {
                this.isShowBtn = this.scrollY < Y
                this.scrollY = Y
            }
        },
    },
    beforeDestroy() {
        window.removeEventListener('scroll', this.handleScroll)
    },
};
</script>

<style lang="scss" scoped>
.my-container {
    width: 100%;
    box-sizing: border-box;
    min-height: 100vh;
    background-color: #f5f5f7;

    * {
        box-sizing: border-box;
    }

    .img_box {
        position: fixed;
        right: 10px;
        bottom: 10%;
        // transform: translateY(-50%);
        z-index: 999;
        width: 46px;
        height: 46px;
        background: var(--main-color);
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 50%;

        img {
            width: 24.25px;
            height: 26.91px;
        }
    }

    .my-header-content {
        width: 100%;
        height: 211px;
        background-color: var(--main-color);
        color: #fff;
        background-size: cover;
        background-repeat: no-repeat;
        background-position: top center;
        padding: 0 15px;
        padding-top: 40px;

        .user-info {
            width: 100%;
            display: flex;
            align-items: center;

            >.avatar {
                flex: 0 0 50px;
                width: 50px;
                height: 50px;
                border-radius: 50%;
                overflow: hidden;
                margin-right: 10px;

                >img {
                    width: 100%;
                    height: 100%;
                }
            }

            >.login {
                font-size: 20px;
                font-weight: bold;
            }

            >.name {
                >.user {
                    font-size: 18px;
                }

                >.id {
                    font-size: 12px;
                    vertical-align: center;
                    margin-top: 5px;

                    >img {
                        display: inline-block;
                        width: 10px;
                        height: 10px;
                        margin-left: 6px;
                    }
                }
            }
        }

        .collect-content {
            width: 100%;
            display: flex;
            position: relative;
            margin-top: 30px;

            &:after {
                content: "";
                display: block;
                width: 1px;
                height: 22px;
                background-color: #fff;
                position: absolute;
                top: 10px;
                left: 50%;
            }

            >.item {
                width: 50%;
                text-align: center;

                >div {
                    font-size: 18px;
                }

                >p {
                    font-size: 12px;
                    margin-top: 10px;
                }
            }
        }
    }

    .my-enter-content {
        padding: 0 15px;
        // padding-bottom: 60px;
        position: relative;
        top: -20px;

        .balance-content {
            padding: 15px 25px;
            background-color: #fff;
            box-shadow: 0px 5px 5px rgba(148, 148, 148, 0.07);

            >.money {
                text-align: center;
            }

            >.tittle {
                width: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                color: #999;

                >span {
                    padding: 0 6px;
                }

                >.icon {
                    width: 14px;
                    font-size: 16px !important;

                    >img {
                        width: 100%;
                        height: auto;
                    }
                }
            }

            .order-content {
                padding: 15px;
                background-color: #fff;
                margin-top: 11px;

                >.tittle {
                    width: 100%;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;

                    >p {
                        font-size: 14px;
                        color: #333;
                    }

                    >.all {
                        display: flex;
                        align-items: center;

                        >p {
                            font-size: 12px;
                            color: #999;
                            margin-right: 11px;
                        }

                        >img {
                            width: 4px;
                            height: auto;
                        }
                    }
                }

                >.content {
                    display: flex;
                    align-items: flex-start;
                    margin-top: 15px;

                    .item {
                        width: 20%;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        position: relative;

                        &:nth-child(2) {
                            .count {
                                right: 14px;
                            }
                        }

                        &:last-child {
                            .count {
                                right: 16px;
                            }
                        }

                        .count {
                            position: absolute;
                            top: 0;
                            right: 12px;
                            padding: 2px;
                            background: #ea3323;
                            color: #fff;
                            font-size: 10px;
                            border-radius: 50%;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            min-width: 14px;
                            max-width: 18px;
                            height: 14px;

                        }

                        .icon {
                            width: 30px;
                            height: 30px;
                            display: flex;
                            align-items: center;
                            justify-content: center;

                            img {
                                height: 20px;
                                width: auto;
                            }
                        }

                        p {
                            font-size: 12px;
                            color: #000;
                            word-break: break-all;
                            text-align: center;
                            margin-top: 5px;
                            padding: 0 4px;
                        }
                    }
                }
            }

            >.btn {
                width: 100%;
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-top: 10px;

                >.item {
                    width: 127px;
                    height: 34px;
                    border-radius: 5px;
                    font-size: 14px;
                    display: flex;
                    align-items: center;
                    justify-content: center;

                    &:first-child {
                        border: 1px solid #333;
                        color: #333;
                    }

                    &:last-child {
                        background-color: var(--main-color);
                        color: #fff;
                    }
                }
            }
        }

        .order-content {
            padding: 15px;
            background-color: #fff;
            margin-top: 11px;

            >.tittle {
                width: 100%;
                display: flex;
                align-items: center;
                justify-content: space-between;

                >p {
                    font-size: 14px;
                    color: #333;
                }

                >.all {
                    display: flex;
                    align-items: center;

                    >p {
                        font-size: 12px;
                        color: #999;
                        margin-right: 11px;
                    }

                    >img {
                        width: 4px;
                        height: auto;
                    }
                }
            }

            >.content {
                display: flex;
                align-items: flex-start;
                margin-top: 15px;

                .item {
                    width: 20%;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    position: relative;

                    &:nth-child(2) {
                        .count {
                            right: 14px;
                        }
                    }

                    &:last-child {
                        .count {
                            right: 16px;
                        }
                    }

                    .count {
                        position: absolute;
                        top: 0;
                        right: 12px;
                        padding: 2px;
                        background: #ea3323;
                        color: #fff;
                        font-size: 10px;
                        border-radius: 50%;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-width: 15px;
                        max-width: 15px;
                        height: 15px;
                    }

                    .icon {
                        width: 30px;
                        height: 30px;
                        display: flex;
                        align-items: center;
                        justify-content: center;

                        img {
                            height: 20px;
                            width: auto;
                        }
                    }

                    p {
                        font-size: 12px;
                        color: #000;
                        word-break: break-word;
                        margin-top: 5px;
                        padding: 0 4px;
                        text-align: center;
                    }
                }
            }
        }

        .merchant-content {
            width: 100%;
            height: 45px;
            background-size: cover;
            background-repeat: no-repeat;
            background-position: top center;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: 10px;

            >div {
                display: flex;
                align-items: center;

                >img {
                    width: 36px;
                    height: auto;
                }

                >p {
                    font-size: 16px;
                    color: #fff;
                }
            }

            >img {
                width: 4px;
                height: auto;
                margin-right: 15px;
            }
        }

        .loan-content {
            width: 100%;
            height: 45px;
            background-color: rgba(0, 0, 0, .8);
            background-size: cover;
            background-repeat: no-repeat;
            background-position: top center;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: 10px;

            >div {
                display: flex;
                align-items: center;

                >img {
                    width: 22px;
                    height: auto;
                    margin: 0 6.5px;
                }

                >p {
                    font-size: 16px;
                    color: #fff;
                }
            }

            >img {
                width: 4px;
                height: auto;
                margin-right: 15px;
            }
        }
    }

    .nav-content {
        margin-top: 10px;
        transform: none !important;

        >.item {
            width: 100%;
            height: 45px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 15px;
            margin-bottom: 1px;
            background-color: #fff;

            &:last-child {
                margin-bottom: 0;
            }

            >div {
                display: flex;
                align-items: center;

                &.name {
                    flex: 1;

                    >.icon {
                        height: 18px;
                        width: auto;
                        margin-right: 10px;
                    }

                    >p {
                        font-size: 14px;
                        color: #333;
                    }
                }

                &.arrow {
                    display: flex;
                    align-items: center;

                    >p {
                        font-size: 14px;
                        color: #333;
                        margin-right: 10px;
                    }

                    >img {
                        width: 4px;
                        height: auto;
                    }
                }
            }
        }
    }

    .span {
        transform: scale(.8);
    }
}

.services-enter-active,
.services-leave-active {
    transition: opacity .3s
}

.services-enter,
.services-leave-to {
    opacity: 0
}
</style>
