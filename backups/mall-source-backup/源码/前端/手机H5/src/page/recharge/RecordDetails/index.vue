<template>
    <div class="page-content">
        <van-image-preview v-if="previewImages.length" v-model="previewShow" :images="previewImages"></van-image-preview>

        <van-nav-bar safe-area-inset-top fixed :title="$t('充值详情')" left-arrow @click-left="onClickLeft" />
        <div style="width: 100%;" class="h46"></div>

        <div v-if="pageDone && dataInfo" class="info-content">
            <div class="order-info-content">
                <div class="item">
                    <p>{{ $t('订单号') }}：</p>
                    <div class="copy" @click="copyData(dataInfo.order_no)">
                        <span style="text-align: end;">{{ dataInfo.order_no }}</span>
                        <img src="@/assets/image/me/fuzhi1.png" />
                    </div>
                </div>
                <div class="item">
                    <p>{{ $t('创建时间') }}：</p>
                    <div>{{ dataInfo.create_time }}</div>
                </div>
                <div class="item">
                    <p>{{ $t('充值数量') }}：</p>
                    <div class="money">{{ dataInfo.volume > 1 ? priceFormat(dataInfo.volume) : dataInfo.volume }} {{
                        dataInfo.coin }}</div>
                </div>
                <div class="item">
                    <p>{{ $t('实际到账') }}：</p>
                    <div class="money" v-if="priceFormat(dataInfo.amount)">{{ priceFormat(dataInfo.amount) }} USDT</div>
                    <div class="money" v-else>--</div>
                </div>

                <div class="item">
                    <p>{{ $t('订单状态') }}：</p>
                    <div class="money" :class="dataInfo.className">{{ dataInfo.stateStr }}</div>
                </div>
                <div class="item" v-if="dataInfo.state == 2">
                    <p>{{ $t('失败原因') }}：</p>
                    <div class="money" :class="dataInfo.className">{{ dataInfo.failureMsg || '--' }}</div>
                </div>
                <div class="item" v-if="dataInfo.coin_blockchain">
                    <p>{{ $t('币种协议') }}：</p>
                    <div>{{ dataInfo.coin_blockchain }}</div>
                </div>
                <div class="item no-border" v-if="dataInfo.channel_address">
                    <p>{{ $t('收款地址') }}：</p>
                    <div class="copy" @click="copyData(dataInfo.channel_address)">
                        <span>{{ dataInfo.channel_address }}</span>
                        <img src="@/assets/image/me/fuzhi1.png" />
                    </div>
                </div>
                <div class="item code-img" v-if="codeImgUrl">
                    <div class="code-img-content">
                        <canvas id="canvas" style="display:none"></canvas>
                        <img :src="codeImgUrl" class="canvas" />
                    </div>
                    <div class="btn">
                        <div @click="saveCodeImg">{{ $t('保存二维码') }}</div>
                    </div>
                </div>
                <div class="item center" v-if="dataInfo.img">
                    <p>{{ $t('支付凭证') }}：</p>
                    <div class="copy">
                        <div class="img-content" @click="previewShow = true">
                            <img :src="dataInfo.img" alt="">
                        </div>
                    </div>
                </div>
            </div>
            <!-- Shop2u 未处理跳转支付按钮 -->
            <van-button block type="primary" v-if="itemName == 'Shop2u' && dataInfo.state == 0 && dataInfo.payUrl"
                class="pay_btn" @click="toPay(dataInfo.payUrl)">
                {{ $t('立即支付') }}
            </van-button>
        </div>
    </div>
</template>
<script>
import { NavBar, Toast, ImagePreview } from 'vant';
import { rechargeBlockchainDetails } from "@/API/user";
import { getImgUrl, priceFormat } from '@/utils/utis'
import QRCode from 'qrcode'
export default {
    name: 'rechargeRecordDetails',
    components: {
        [NavBar.name]: NavBar,
        [Toast.name]: Toast,
        [ImagePreview.Component.name]: ImagePreview.Component
    },
    data() {
        return {
            itemName: process.env.VUE_APP_ITEM_NAME,
            pageDone: false,
            orderNo: null,
            dataInfo: null,
            previewShow: false,
            previewImages: [],
            codeImgUrl: '',
            priceFormat,
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
            rechargeBlockchainDetails({ order_no: this.orderNo }).then(res => {
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
                if (res.img) {
                    this.previewImages = [res.img]
                }
                this.dataInfo = res
                this.pageDone = true
                Toast.clear()
                this.$nextTick(() => {
                    this.createCodeImg(res.from)
                })
            }).catch(err => {
                // Toast(err.msg)
                Toast.clear()
            })
        },
        // 生成二维码
        createCodeImg(txt) {
            const that = this
            const canvas = document.getElementById('canvas')
            QRCode.toCanvas(canvas, txt,
                {
                    width: 124,
                    height: 124,
                    margin: 0
                }, function (error) {
                    if (error) {
                        // console.error(error)
                    } else {
                        that.codeImgUrl = canvas.toDataURL('image/png')
                    }
                })
        },
        saveCodeImg() {
            let myCanvas = document.getElementsByTagName('canvas');
            this.imgUrl = myCanvas[0].toDataURL('image/png')
            this.getUrlBase64(this.imgUrl).then(base64 => {
                let link = document.createElement('a')
                link.href = base64
                link.download = 'qrCode.png'
                link.click()
            })
        },
        getUrlBase64(url) {
            return new Promise(resolve => {
                let canvas = document.createElement('canvas')
                let ctx = canvas.getContext('2d')
                let img = new Image()
                img.crossOrigin = 'Anonymous' //允许跨域
                img.src = url
                img.onload = function () {
                    canvas.height = 300
                    canvas.width = 300
                    ctx.drawImage(img, 0, 0, 300, 300)
                    let dataURL = canvas.toDataURL('image/png')
                    canvas = null
                    resolve(dataURL)
                }
            })
        },
        getImgUrlHandle(path) {
            console.log(`path ::->`, path);
            return getImgUrl(path)
        },
        toPay(path) {
            window.open(path)
        }
    }
}
</script>
<style lang="scss" scoped>
.pay_btn {
    margin-top: 40px;
    background: var(--main-color);
}

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

                &.center {
                    align-items: center;
                }

                >div {
                    flex: 1;
                    padding-left: 50px;
                    text-align: end;

                    &.copy {
                        display: flex;
                        justify-content: flex-end;

                        >span {
                            text-align: start;
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

                    .img-content {
                        width: 62px;
                        height: 56px;
                        border-radius: 4px;
                        background-color: #D9D9D9;
                        overflow: hidden;
                        display: flex;
                        align-content: center;
                        align-items: center;

                        >img {
                            width: 100%;
                            height: auto;
                        }
                    }
                }

                &.code-img {
                    flex-direction: column;
                    align-items: center;

                    >div {
                        padding: 0;
                        flex: 0;
                        text-align: center;

                        &.code-img-content {
                            width: 138px;
                            height: 138px;
                            border: 1px solid #ddd;
                            padding: 6px;
                            display: flex;
                            align-items: center;
                            justify-content: center;

                            >.canvas {
                                width: 124px;
                                height: 124px;
                            }
                        }

                        &.btn {
                            margin-top: 10px;

                            >div {
                                width: 105px;
                                height: 36px;
                                line-height: 34px;
                                border: 1px solid #DDDDDD;
                                border-radius: 4px;
                                font-size: 12px;
                            }
                        }
                    }
                }

                &.no-border,
                &:last-child {
                    border-bottom: none;
                }
            }
        }
    }
}
</style>
