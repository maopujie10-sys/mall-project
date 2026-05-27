<template>
    <div class="page-content">
        <van-nav-bar safe-area-inset-top fixed :title="$t('提现详情')" left-arrow @click-left="onClickLeft" />
        <div style="width: 100%;" class="h46"></div>

        <div v-if="pageDone && dataInfo" class="info-content">
            <div class="order-info-content">
                <div class="item">
                    <p>{{ $t('订单号') }}：</p>
                    <div class="copy">
                        <span>{{ dataInfo.order_no }}</span>
                        <img @click="copyData(dataInfo.order_no)" src="@/assets/image/me/fuzhi1.png" />
                    </div>
                </div>
                <div class="item">
                    <p>{{ $t('创建时间') }}：</p>
                    <div>{{ dataInfo.create_time }}</div>
                </div>
                <div class="item">
                    <p>{{ $t('提现金额') }}：</p>
                    <div class="money">
                    {{ ['BTC', 'ETH'].includes(dataInfo.coin) ? dataInfo.volume : priceFormat(dataInfo.volume)}}
                    {{ dataInfo.coin }}
                    </div>
                </div>
                <div class="item">
                    <p>{{ $t('订单状态') }}：</p>
                    <div class="money" :class="dataInfo.className">{{ dataInfo.stateStr }}</div>
                </div>
                <div class="item" v-if="dataInfo.state == 2">
                    <p>{{ $t('失败原因') }}：</p>
                    <div class="money" :class="dataInfo.className">{{ dataInfo.failureMsg || '--' }}</div>
                </div>
                <template v-if="dataInfo.coin_blockchain != 'bank'">
                    <div class="item">
                        <p>{{ $t('币种协议') }}：</p>
                        <div>{{ dataInfo.coin_blockchain }}</div>
                    </div>
                    <div class="item">
                        <p>{{ $t('钱包地址') }}：</p>
                        <div class="copy">
                            <span>{{ dataInfo.to }}</span>
                            <img @click="copyData(dataInfo.to)" src="@/assets/image/me/fuzhi1.png" />
                        </div>
                    </div>
                </template>
                <template v-else>
                    <div class="item">
                        <p>{{ $t('开户行') }}：</p>
                        <div>{{ dataInfo.bank }}</div>
                    </div>
                    <div class="item">
                        <p>{{ $t('姓名') }}：</p>
                        <div>{{ dataInfo.bankUserName }}</div>
                    </div>
                    <div class="item">
                        <p>{{ $t('卡号') }}：</p>
                        <div class="copy">
                            <span>{{ dataInfo.bankCardNo }}</span>
                            <img @click="copyData(dataInfo.bankCardNo)" src="@/assets/image/me/fuzhi1.png" />
                        </div>
                    </div>
                </template>
                <div class="item">
                    <p>{{ $t('手续费') }}：</p>
                    <div>{{ priceFormat(dataInfo.fee) }} USDT</div>
                </div>
                <div class="item">
                    <p>{{ $t('实际到账') }}：</p>
                    <div v-if="$t('处理中') == dataInfo.stateStr" class="money">--</div>
                    <div class="money" v-else>{{ priceFormat(dataInfo.amount) }} {{ dataInfo.coin }}</div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import { NavBar, Toast } from 'vant';
import { withdrawDetails } from "@/API/user";
import { priceFormat } from '@/utils/utis'
export default {
    name: 'withdrawRecordDetails',
    components: {
        [NavBar.name]: NavBar,
        [Toast.name]: Toast
    },
    data() {
        return {
            pageDone: false,
            orderNo: null,
            dataInfo: null,
            priceFormat,
            failureMsg: ''
        }
    },
    mounted() {
        this.$nextTick(() => {
            const { order_no, failure_msg } = this.$route.query
            if (order_no) {
                this.orderNo = order_no
                this.failureMsg = failure_msg
                this.getDataInfo()
            } else {
                Toast(this.$t('订单号不存在'));
            }
        })
    },
    methods: {
        onClickLeft() {
            this.$router.go(-1)
        },
        copyData(ea) {
            this.$copyText(ea).then(() => {
                Toast(this.$t('复制成功'))
            }, () => {
                Toast(this.$t('复制失败'))
            })
        },
        getDataInfo() {
            Toast.loading({
                duration: 0,
                message: this.$t('请求中')
            })
            withdrawDetails({ order_no: this.orderNo }).then(res => {
                res.stateStr = ''
                res.className = ''
                if (res.state === 0) {
                    res.stateStr = this.$t('处理中')
                }
                if (res.state === 1) {
                    res.className = 'success'
                    res.stateStr = this.$t('成功')
                }
                if (res.state === 2) {
                    res.className = 'fail'
                    res.stateStr = this.$t('失败')
                }
                this.dataInfo = res
                this.pageDone = true
                Toast.clear()
            }).catch(err => {
                // Toast(err.msg)
                Toast.clear()
            })
        }
    }
}
</script>
<style lang="scss" scoped>
.page-content {
    width: 100%;
    min-height: 100%;
    background: #F5F5F7;

    * {
        box-sizing: border-box;
    }

    .info-content {
        padding: 10px 15px;

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

                >div {
                    flex: 1;
                    padding-left: 50px;
                    text-align: end;

                    &.copy {
                        display: flex;
                        justify-content: flex-end;

                        >span {
                            flex: 1;
                            word-break: break-word;
                        }

                        >img {
                            width: 10px;
                            height: 10px;
                            margin-left: 4px;
                            position: relative;
                            top: 3px;
                        }
                    }

                    &.money {

                        color: var(--main-color);
                    }

                    &.success {
                        color: #0ECB81 !important;
                    }

                    &.fail {
                        color: #FF4141 !important;
                    }
                }

                &:last-child {
                    border-bottom: 0;
                }
            }
        }
    }
}
</style>
