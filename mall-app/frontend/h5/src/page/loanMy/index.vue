<template>
    <div class="my_loan">
        <van-nav-bar safe-area-inset-top :title="$t('我的贷款')" left-arrow @click-left="$router.go(-1)" fixed ref="header">
        </van-nav-bar>
        <!-- 上方我的贷款 -->
        <div :class="['top_card', isEn && 'en_card']">
            <div class="tt">
                <div class="tl">
                    <span>{{ $t('我的贷款') }}</span>
                    <span>{{ applyAmount }}</span>
                </div>
                <!-- <div :class="['tr', isEn && 'en_tr']">
                    <span>{{ $t('申请贷款') }}</span>
                </div> -->
            </div>
            <div class="tb">
                <div class="item" v-for="(item, index) of cardList" :key="index"
                    :class="isEn && index != 0 && 'en_item'">
                    <span>
                        {{ item.value }}
                        <em>{{ index == 0 ? $t('天') : '' }}</em>
                    </span>
                    <span>{{ item.title }}</span>
                </div>
            </div>
        </div>
        <!-- 贷款记录 -->
        <div class="loan_history">
            <div class="title">{{ $t('贷款记录') }}</div>
            <ul>
                <li v-for="(item, index) of loanHistory" :key="index" :class="isEn && 'en_li'">
                    <img src="@/assets/image/locn/icon.png" alt="">
                    <div class="content">
                        <div class="top">
                            <div class="tleft">
                                <span>{{ priceFormat(item.applyAmount) }}</span>
                                <span>{{ $t('申请日期') }}: {{ $formatZoneDate(item.customerSubmitTime) }}</span>
                            </div>
                            <div class="btn" @click="handleRepayment(item.status, item.id)" v-if="item.status != 1 && item.status != 5">
                                <button v-if="item.status == 2 || item.status == 3">{{ $t('还款') }}</button>
                                <button v-else-if="item.status == 4">
                                    {{ $t('重新申请') }}
                                    <!-- :disabled="isCheckAvailability == 'false'"
                                    :class="isCheckAvailability == 'false' && 'disabled'" -->
                                </button>
                            </div>
                            <div class="null" v-else>--</div>
                        </div>
                        <div class="btm">
                            <span>
                                {{ $t('还款周期') }}:
                                {{ item.creditPeriod }}<em>{{ $t('天') }}</em>
                            </span>
                            <span>{{ $t('固定利率') }}: {{ Math.floor(item.creditRate * 100) + '%' }}</span>
                            <!-- <span v-if="item.status == 1">{{ $t('借款成功') }}</span> -->
                            <span v-if="item.status == 1" style="color: var(--main-color);">{{ $t('申请中') }}</span>
                            <span v-if="item.status == 2" style="color: #2FAA59;">{{ $t('借款成功') }}</span>
                            <span v-if="item.status == 3" style="color: #E43434;">{{ $t('已逾期') }}</span>
                            <span v-if="item.status == 4" style="color: #E43434;">{{ $t('借款失败') }}</span>
                            <span v-if="item.status == 5" style="color: #EB9D38;">{{ $t('已节清') }}</span>
                        </div>
                    </div>
                </li>
            </ul>
            <van-empty v-if="!loanHistory.length" :description="$t('暂无数据')" />
        </div>
        <Footer />
    </div>
</template>
<script>
import { Empty } from 'vant'
import { apiLoanMy, apiLoanMyRecord, apiCheckAvailability } from '@/API/loan'
import { getStorage, priceFormat } from '@/utils/utis'
import Footer from '@/components/Footer'
export default {
    components: { 
        Footer,
        [Empty.name]: Empty
     },
    data() {
        return {
            priceFormat,
            cardList: [
                { title: this.$t('已贷款'), value: 0 },
                { title: this.$t('产生利息'), value: '--' },
                { title: this.$t('预计还款'), value: '--' },
            ],
            isEn: getStorage('lang') !== 'cn' || getStorage('lang') !== 'tw',
            pageNo: 1,
            loanHistory: [],
            applyAmount: '--',
            isCheckAvailability: 'false'
        }
    },
    mounted() {
        this.requireMyLoan()
        this.requireMyLoanRecord()
        this.requireCheckAvailability()
    },
    methods: {
        async requireMyLoan() {
            const res = await apiLoanMy()
            this.cardList[0].value = res.alreadyCreditDays
            this.cardList[1].value = this.priceFormat(res.interest) || '--'
            this.cardList[2].value = this.priceFormat(res.estimatePayment) || '--'
            this.applyAmount = this.priceFormat(res.applyAmount) || '--'
        },
        async requireMyLoanRecord() {
            const res = await apiLoanMyRecord({ pageNo: this.pageNo })
            this.loanHistory = res.elements
        },
        // 还款按钮
        handleRepayment(status, id) {
            if (status == 2 || status == 3) this.$router.push('/repayment/expected?creditId=' + id)
            if (status == 4 || status == 5) this.$router.push('/loan/apply?creditId=' + id)
        },
        async requireCheckAvailability() {
            this.isCheckAvailability = await apiCheckAvailability()
        },
    }
}
</script>

<style lang="scss" scoped>
.my_loan {
    width: 100%;
    min-height: 100vh;
    background: #F3F5F9;
    padding-top: 44px;
    font-size: 14px;
    // padding-bottom: 80px;

    .top_card {
        width: 345px;
        height: 160px;
        background: #fff;
        margin: 11px auto;
        border-radius: 4px;
        padding: 15px;
        box-sizing: border-box;

        &.en_card {
            height: 170px;
        }

        .tt {
            display: flex;
            justify-content: space-between;
            align-items: center;

            .tl {
                display: flex;
                flex-direction: column;
                width: 100%;
                justify-content: center;
                align-items: center;

                span {
                    &:nth-child(1) {
                        font-weight: 600;
                        font-size: 16px;

                    }

                    &:nth-child(2) {
                        margin-top: 10px;
                        font-weight: 600;
                        font-size: 20px;
                        color: var(--main-color);
                    }
                }
            }

            .tr {
                width: 109px;
                height: 34px;
                background: var(--main-color);
                border-radius: 4px;
                display: flex;
                justify-content: center;
                align-items: center;
                color: #fff;
                font-weight: 500;
                font-size: 14px;

                &.en_tr {
                    width: 115px;
                    height: 36px;
                }
            }
        }

        .tb {
            margin-top: 22px;
            padding: 0 20px;
            width: 100%;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-sizing: border-box;

            .item {
                display: flex;
                flex-direction: column;
                // justify-content: center;
                // align-items: center;
                flex: 0 0 33%;
                text-align: center;

                &:nth-child(1) {
                    transform: translateX(-15px);
                }

                &:nth-child(3) {
                    transform: translateX(15px);
                }

                &.en_item {

                    &:nth-child(3) {
                        transform: translate(15px, 7.5px);
                    }

                    &:nth-child(2) {
                        transform: translate(0, 7.5px);
                    }
                }

                span {
                    em {
                        font-size: 14px;
                        font-style: normal;
                    }

                    &:nth-child(1) {
                        font-weight: 600;
                        font-size: 18px;
                        color: var(--main-color);
                    }

                    &:nth-child(2) {
                        margin-top: 6px;
                        font-weight: 400;
                        font-size: 12px;
                        color: #999999;
                    }
                }
            }
        }
    }

    .loan_history {
        margin-top: 19px;
        padding: 0 14px 0 16px;
        min-height: 55vh;

        .title {
            margin-bottom: 11px;
            color: #333;
            font-size: 12px;
        }

        ul {
            width: 100%;

            li {
                width: 100%;
                height: 87px;
                border-radius: 4px;
                background: #fff;
                margin-bottom: 12px;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 0 16px 0 15px;
                box-sizing: border-box;

                &.en_li {
                    position: relative;
                    height: 115px;

                    img {
                        transform: translateY(-20px);
                    }

                    .content {
                        display: flex;
                        flex-direction: column;

                        .top {
                            flex: 0 0 50%;
                            display: flex;

                            .tleft {
                                span {
                                    &:nth-child(2) {
                                        transform: scale(.77) translateX(-28px);
                                    }
                                }
                            }
                            
                            .btn {
                                position: absolute;
                                top: 11px;
                                right: 0;
                                padding: 0 5px;
                                min-width: 70px;
                                min-height: 29px;
                                font-size: 10px;
                                border-radius: 4px 0 0 4px;

                                span {
                                    transform: scale(.9);
                                }
                            }
                        }

                        .btm {
                            flex: 0 0 50%;
                            display: flex;
                            flex-direction: column;
                            position: relative;

                            span {
                                &:nth-child(1) {
                                    transform: none;
                                    font-size: 10px;
                                    margin-bottom: 4px;
                                    transform: translateX(-26px) scale(0.8);
                                    em {
                                        margin-left: 2px;
                                        font-size: 10px;
                                    }
                                }

                                &:nth-child(2) {
                                    transform: none;
                                    font-size: 10px;
                                    margin: 0;
                                    transform: translateX(-26px) scale(0.8);
                                }

                                &:nth-child(3) {
                                    position: absolute;
                                    top: 50%;
                                    right: 7px;
                                    transform: translateY(-50%) scale(0.8);
                                }
                            }
                        }
                    }
                }

                img {
                    flex: 0 0 30px;
                    width: 30px;
                    height: 30px;
                    margin-right: 10px;
                    transform: translateY(-14px);
                }

                .content {
                    flex: 1;
                    width: 100%;

                    .top {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        padding-bottom: 8px;
                        border-bottom: 1px solid #F3F3F3;

                        .tleft {
                            display: flex;
                            flex-direction: column;

                            span {
                                &:nth-child(1) {
                                    color: #333;
                                    font-size: 16px;
                                    font-weight: 700;
                                    line-height: 19px;
                                }

                                &:nth-child(2) {
                                    margin-top: 1px;
                                    color: #999;
                                    font-weight: 500;
                                    font-size: 12px;
                                    text-align: start;
                                    transform: scale(.85) translateX(-15px);
                                }
                            }
                        }
                        .null {
                            width: 83px;
                            height: 24px;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                        }

                        .btn {
                            width: 83px;
                            height: 24px;
                            background: var(--main-color);
                            border-radius: 4px;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            color: #fff;
                            font-weight: 500;
                            font-size: 13px;
                            // border: 1px solid var(--main-color);

                            button {
                                width: 83px;
                                height: 24px;
                                background: transparent;
                                border: none;
                                border-radius: 4px;
                                font-weight: 400;
                                &.disabled {
                                    // opacity: .6;
                                    background: #EDEDED;
                                    color: #AEAEAE;
                                    
                                }
                            }

                            &.again {
                                background: linear-gradient(0deg, #FFF7EC, #FFF7EC), #EEEEEE;
                                color: var(--main-color);
                            }
                        }
                    }

                    .btm {
                        margin-top: 6px;

                        span {
                            color: #999;
                            font-size: 10px;
                            line-height: 14px;
                            transform: scale(.85) translateX(-5px);
                            display: inline-block;

                            // &:nth-child(2) {
                            //     margin: 0 30px 0 15px;
                            // }

                            &:last-child {
                                color: #3F80FF;
                                font-size: 12px;
                                transform: scale(1);
                            }
                        }
                    }
                }
            }
        }
    }
}
</style>