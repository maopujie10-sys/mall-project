<template>
    <div id="app" style="width: 100%; height: 100%">
        <transition :name="$router.customRouterData.transitionName">
            <router-view v-slot="{ Component }">
                <keep-alive :include="keepaliveData">
                    <component :is="Component" />
                </keep-alive>
                <component :is="Component" />
            </router-view>
        </transition>
    </div>
</template>

<script>
import { Overlay } from "vant";
import { mapMutations, mapGetters } from "vuex";
import { apiHeartbeat, apiGetMaxBuyNum, apiGetCustomerService } from '@/API/common'
import { apiApplyLoan } from "./API/loan";
export default {
    name: "App",
    data() {
        return {
            show: false,
            timer: "",
            itemData: this.$store.state.multiItem[process.env.VUE_APP_ITEM_NAME],
            itemName: process.env.VUE_APP_ITEM_NAME,
            mainColor: process.env.VUE_APP_MAIN_COLOR,
        };
    },
    components: {
        [Overlay.name]: Overlay,
    },
    created() {

        if (this.$route.query.lang) {
            if (this.$route.query.lang == "cn") {
                this.handleSetLang("cn");
            } else {
                this.handleSetLang("en");
            }
        }
        if (window.plus) {
            this.plusReady();
        } else {
            document.addEventListener("plusready", this.plusReady, false);
        }
        let link = document.head.querySelector("link");
        link.href = require(`@/assets/${this.itemName}/favicon.png`);
        document.title = this.itemName
        // 刷新事件
        window.addEventListener("beforeunload", () => {
            sessionStorage.removeItem("scrollTopCount")
            // sessionStorage.removeItem("showLoading")
        })
        if (localStorage.getItem('lang') == 'en-US') localStorage.setItem('lang', 'en')
        setInterval(() => {
            let token = localStorage.getItem("token");
            token && apiHeartbeat()
        }, 1000 * 60 * 5);
        this.getMaxBuyNum()
        this.getCustomerService()
    },

    methods: {
        plusReady() {
            // H5 plus事件处理
            // eslint-disable-next-line no-undef
            plus.screen.lockOrientation("portrait-primary");

            // 设置系统状态栏背景为红色
            // eslint-disable-next-line no-undef
            // var type = plus.os.name;
            // if (type === "Android" || type === "iOS") {
            //     switch (this.$route.path) {
            //         case "/me":
            //             // eslint-disable-next-line no-undef
            //             plus.navigator.setStatusBarStyle("light");
            //             // eslint-disable-next-line no-undef
            //             plus.navigator.setStatusBarBackground(this.mainColor);
            //             break;
            //         default:
            //             // eslint-disable-next-line no-undef
            //             plus.navigator.setStatusBarStyle("dark");
            //             // eslint-disable-next-line no-undef
            //             plus.navigator.setStatusBarBackground("#ffffff");
            //     }
            // }

        },
        // 获取商品最大购买数
        async getMaxBuyNum() {
            let { mall_max_goods_number_in_order } = await apiGetMaxBuyNum({ code: 'mall_max_goods_number_in_order' })
            localStorage.setItem('maxBuyNum', mall_max_goods_number_in_order)
        },
        // 获取客服地址
        async getCustomerService() {
            let { customer_service_url } = await apiGetCustomerService('?code=customer_service_url')
            if (customer_service_url) {
                this.$store.state.multiItem[this.itemName].customer_service = customer_service_url
            }
        },
        handleSetLang(lang) {
            // 设置i18n.locale 组件库会按照上面的配置使用对应的文案文件
            this.$i18n.locale = lang;
            // 提交mutations
            this.setLanguage(lang);
        },

    },
    watch: {
        "$store.state": function (newVal) {
            if ($store.state.qiangdan.qiangdan_status) {
                this.show = true;
            }
        },
        $route: function (to, from) {
            if (to.name !== 'home') {
                document.body.scrollTop = 0;
                document.documentElement.scrollTop = 0;
            } else {
                setTimeout(() => {
                    window.scrollTo({
                        top: sessionStorage.getItem("scrollTopCount"),
                        behavior: "smooth"
                    });
                }, 500);
            }
        },
    },
    beforeDestroy() {
        clearInterval(this.timer);
    },
};
</script>

<style lang="scss">
@import "@/assets/init.scss";

//返回
.van-nav-bar .van-icon {
    color: #333333;
}

//// 上传图片框大小设置
// .van-uploader__upload {
//    width:120px !important;
//    height:120px !important;
//}

.van-uploader__upload-icon {
    font-size: 48px !important;
}

.van-uploader__upload {
    background-color: white !important;
    border: 2px dashed #b8bcc5;
}

// tab标签短横线颜色
.van-tabs__line {
    background-color: #1552f0 !important;
}

//.van-tabs__wrap{
//  height:88px !important;
//}
//
//.van-tab__text--ellipsis{
//   overflow:visible !important;
//}

.van-tab__text {
    font-size: 14px !important;
}

.van-nav-bar__text {
    color: #999999;
}
</style>
<style lang="scss" scoped>
// .wrapper {
//   //display: flex;
//   //align-items: center;
//   //justify-content: center;
//   //height: 100%;
//   //width: 100%;
// }

.block {
    width: 120px;
    height: 120px;
    background-color: #fff;
}

.zhengti {
    width: 100%;
    max-width: 570px;
    padding: 0 15px;
    //padding-top: 60px;
    box-sizing: border-box;

    .zhengti-top {
        box-sizing: border-box;
        padding: 10px 15px 20px 15px;
        background: linear-gradient(180deg, #ffb545 0%, #ff783f 100%);
        border-radius: 10px;
        position: relative;

        .qiangdanbiaopti {
            position: absolute;
            font-style: normal;
            font-weight: 600;
            font-size: 24px;
            //line-height: 28px;
            text-align: center;
            color: #ffffff;
            left: 0;
            right: 0;
            top: 14px;
            bottom: 0; // 只要左右居中可以不加top、bottom
            // bottom: 30px; 可以另外设置想要的上下位置
            margin: 0 auto;
            width: 300px;
            height: 40px;
        }

        .bj-nr {
            width: 100%;
            height: 110px;
            display: block;
        }

        .shanpin-xinxi {
            position: relative;
            padding: 19px 15px 16px 15px;
            box-sizing: border-box;
            background: white;
            border-radius: 4px;

            .xinxi1 {
                width: 100%;
                display: flex;
                margin-bottom: 15px;
                justify-content: center;
                align-items: center;

                .bao1 {
                    flex: 1;
                    font-style: normal;
                    font-weight: 400;
                    font-size: 14px;
                    line-height: 16px;

                    /* 全局主标题灰色 */

                    color: #999999;
                }

                .bao2 {
                    font-style: normal;
                    font-weight: 400;
                    font-size: 14px;
                    line-height: 16px;
                    text-align: end;
                    color: #333333;
                }
            }

            .shangpin-jianjie {
                width: 100%;
                display: flex;

                .jieshao {
                    //width: 100%;
                    flex: 1;
                    width: 0;
                    box-sizing: border-box;
                    display: flex;
                    flex-direction: column;

                    .jie1 {
                        width: 183px;
                        //height: 35px;
                        font-style: normal;
                        font-weight: 400;
                        font-size: 14px;
                        line-height: 16px;
                        /* 333 */
                        color: #333333;
                    }

                    .jiage {
                        width: 100%;
                        margin-top: 23px;
                        height: 19px;

                        .j1 {
                            font-style: normal;
                            font-weight: 400;
                            font-size: 16px;
                            line-height: 19px;
                            /* identical to box height */
                            float: left;
                            /* 审核中 */

                            color: #1552f0;
                        }

                        .j2 {
                            font-style: normal;
                            font-weight: 400;
                            font-size: 14px;
                            line-height: 19px;
                            text-align: end;
                            /* 审核中 */
                            float: right;
                            color: #1552f0;
                        }
                    }
                }
            }

            .heji {
                text-align: end;
                font-style: normal;
                font-weight: 400;
                font-size: 14px;
                line-height: 16px;
                color: #999999;

                .hejishuzhi {
                    font-style: normal;
                    font-weight: 400;
                    font-size: 18px;
                    line-height: 21px;
                    color: #1552f0;
                }
            }
        }

        .chakan-dingdan {
            margin-top: 22px;
            background: white;
            width: 100%;
            height: 44px;
            font-style: normal;
            font-weight: 400;
            font-size: 16px;
            line-height: 44px;
            /* identical to box height, or 100% */

            text-align: center;

            /* 审核中 */

            color: #1552f0;
        }
    }

    .guanbi {
        width: 24px;
        height: 24px;
        margin-top: 20px;
    }
}

/deep/ .van-nav-bar__arrow {
    font-size: 22px;
}

/deep/ .van-popup__close-icon {
    color: #333333 !important;
}
</style>
<style>
.wrapper {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
}
</style>
