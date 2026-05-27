<template>
    <div class="submit-success-wrap">
        <div class="wanc">
            <img src="@/assets/image/public/wanc.png" />
        </div>
        <div class="title">{{ $t('店铺入住申请已提交，请联系客服获取加速认证') }}</div>
        <div class="success-but-wrap">
            <div class="but but-one" @click="openUrl(2)">{{ $t('联系客服') }}</div>
            <div class="but but-two" @click="openUrl(1)">{{ $t('去登录') }}</div>

        </div>
        <div class="step-wrap">
            <ul>
                <li>
                    <div class="step-img">
                        <div :class="[status === 0 ? 'span-success' : 'span-pidding']"></div>
                    </div>
                    <div class="text">{{ $t('提交申请表') }}</div>
                </li>
                <li>
                    <div class="step-img">
                        <div :class="[status === 1 ? 'span-success' : 'span-pidding']"></div>
                    </div>
                    <div class="text">{{ $t('背景审计') }}</div>
                </li>
                <li>
                    <div class="step-img">
                        <div :class="[status === 2 ? 'span-success' : 'span-pidding']"></div>
                    </div>
                    <div class="text">{{ $t('成为店主') }}</div>
                </li>
            </ul>
        </div>
        <div class="advertise-img">
            <img src="@/assets/image/Merchant/advertise.png" />
        </div>
    </div>
</template>

<script>

import { Toast } from "vant";
import { getStatus } from "@/API/commodity";
export default {
    name: 'submitSuccess',
    data() {
        return {
            status: 0
        }
    },
    computed: {

    },
    created() {
        this.getStatusInfo()
    },
    methods: {
        //查询店铺申请进度
        getStatusInfo() {
            getStatus({}).then((res) => {
                this.status = res.status
            })
        },
        openUrl(index) {
            switch (index) {
                case 1:
                    const base_url = process.env.VUE_APP_IS_APP ? this.$store.state.multiItem[process.env.VUE_APP_ITEM_NAME].app_url : location.origin
                    location.href = base_url + "/ww"
                    break;
                case 2:
                    this.$router.push('/customerService')
                    break;
                default:
                    break;
            }
        }
    }
}
</script>

<style lang="scss" scoped>
.submit-success-wrap {
    width: 1200Px;
    border: 1px solid #EEEEEE;
    border-radius: 4Px;
    margin: 0 auto;
    padding-bottom: 30Px;
    margin-bottom: 30Px;

    .wanc {
        margin-top: 70Px;

        img {
            width: 100Px;
            height: 100Px;
            display: block;
            margin: 0 auto;
        }
    }

    .title {
        font-size: 16Px;
        color: #333333;
        line-height: 22Px;
        width: 700Px;
        margin: 0 auto;
        text-align: center;
        margin-top: 40Px;
    }

    .success-but-wrap {
        display: flex;
        justify-content: center;
        margin-top: 70Px;

        .but {
            width: 255Px;
            height: 50Px;
            border-radius: 4Px;
            text-align: center;
            line-height: 50Px;
            font-size: 16Px;
        }

        .but-one {
            border: 1px solid #EEEEEE;
            color: #333333;
        }

        .but-two {
            background: var(--main-color);
            color: #fff;
            margin-left: 40Px;
        }
    }

    .step-wrap {
        margin-top: 100Px;

        ul {
            display: flex;
            justify-content: center;

            li {
                width: 280Px;
                position: relative;

                .step-img {
                    height: 55Px;
                    display: flex;
                    align-items: center;

                    .span-success {
                        width: 34Px;
                        height: 34Px;
                        background: url('@/assets/image/public/wanc.png');
                        background-size: 100% 100%;
                        margin: 0 auto;
                    }

                    .span-pidding {
                        width: 28Px;
                        height: 28Px;
                        background: url('@/assets/image/Merchant/wanc2.png');
                        background-size: 100% 100%;
                        margin: 0 auto;
                    }

                }

                .text {
                    font-size: 16Px;
                    color: #333333;
                    text-align: center;
                }
            }

            li:not(:last-child) {
                &::after {
                    background: #EEEEEE;
                    position: absolute;
                    content: '';
                    right: 0;
                    top: 40%;
                    width: 110Px;
                    height: 2Px;
                }
            }

            li:not(:first-child) {
                &::before {
                    background: #EEEEEE;
                    position: absolute;
                    content: '';
                    left: 0;
                    top: 40%;
                    width: 110Px;
                    height: 2Px;
                }
            }
        }
    }

    .advertise-img {
        width: 938Px;
        margin: 0 auto;
        margin-top: 40Px;

        img {
            width: 100%;
        }
    }
}

@media screen and (max-width:500Px) {
    .submit-success-wrap {
        width: 100% !important;

        .wanc {
            margin-top: 70Px;

            //   img {}
        }

        .title {
            font-size: 16Px;
            color: #333333;
            line-height: 22Px;
            margin: 0 auto;
            width: 100%;
            text-align: center;
            margin-top: 40Px;
        }

        .success-but-wrap {
            display: block;
            margin-top: 70Px;

            .but {
                width: 80%;
                margin: 0 auto;
            }

            .but-two {
                background: var(--main-color);
                color: #fff;
                margin-left: 40Px;
                margin-top: 20Px;

            }
        }

        .step-wrap {
            margin-top: 30Px;

            ul {
                display: block !important;

                li {
                    width: 280Px;
                    position: relative;
                    margin: 0 auto;
                    margin-top: 20Px;

                    .step-img {
                        height: 55Px;
                        display: flex;
                        align-items: center;

                    }

                    .text {
                        font-size: 16Px;
                        color: #333333;
                        text-align: center;
                    }
                }

                li {
                    &::after {
                        height: 0Px !important;
                    }
                }

                li {
                    &::before {
                        height: 0Px !important;
                    }
                }
            }
        }

        .advertise-img {
            width: 90% !important;

        }
    }
}
</style>
