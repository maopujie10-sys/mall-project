<template>
    <div class="recharge">
        <van-nav-bar safe-area-inset-top fixed :title="itemName == 'Hive' ? $t('提领') : $t('提现')" left-arrow
            @click-left="onClickLeft" :right-text="$t('记录')" @click-right="onClick1" />
        <div style="width: 100%;" class="h46"></div>

        <div class="biaoti" style="margin-bottom: 5px;">{{ $t('取款方式') }}</div>
        <div class="shuru">
            <el-select v-model="selectValue" :placeholder="$t('请选择')" @change="onCoinChange">
                <el-option :label="$t('加密货币')" value="0"></el-option>
                <el-option :label="$t('银行卡')" value="1"></el-option>
            </el-select>
        </div>
        <template v-if="selectValue == 0">
            <div class="biaoti" style="margin-bottom: 5px;">{{ $t('币种') }}</div>
            <div class="shuru">
                <el-select v-model="selectCurrency" :placeholder="$t('请选择')" @change="selectCurrencyChange">
                    <el-option v-for="item of withdrawalMethod" :key="item.label" :label="item.label"
                        :value="item.value"></el-option>
                </el-select>
            </div>
            <div class="biaoti">{{ $t('区块链网络') }}</div>
            <div class="duoxuan">
                <div v-for="(item, indx) in blockchainNetwork" :key="indx" class="xuan1 "
                    :class="currentChainName === item ? 'xuanzhong' : 'weixuan'" @click="tongdao_qiehuan(item)">{{ item }}

                    <van-icon class-prefix="icon" v-if="currentChainName == item" name="xuanzejiaobiao"
                        class="xuanzhong-img rtl_selected" />
                </div>
            </div>
            <div class="biaoti" style="margin-bottom: 5px;">{{ $t('地址') }}</div>
            <div class="shuru">
                <el-input :placeholder="$t('请输入地址')" :disabled="allowEditWithdrawAddress" v-model="it.input2" clearable>
                </el-input>
            </div>
        </template>
        <template v-else>
            <div class="biaoti" style="margin-bottom: 5px;">{{ $t('开户行') }}</div>
            <div class="shuru">
                <el-input :placeholder="$t('请输入开户行')" v-model="card.bankName" clearable>
                </el-input>
            </div>
            <div class="biaoti" style="margin-bottom: 5px;">{{ $t('姓名') }}</div>
            <div class="shuru">
                <el-input :placeholder="$t('请输入姓名')" v-model="card.bankUserName" clearable>
                </el-input>
            </div>
            <div class="biaoti" style="margin-bottom: 5px;">{{ $t('卡号') }}</div>
            <div class="shuru">
                <el-input :placeholder="$t('请输入卡号')" v-model="card.bankCardNo" clearable>
                </el-input>
            </div>
        </template>
        <div class="biaoti" style="margin-bottom: 5px;">
            <span>{{ $t('金额') }}</span>
        </div>
        <div class="shuru">
            <el-input :placeholder="$t('请输入金额')" maxlength="10" v-model="it.input1" @input="handleInput" type="number"
                clearable>
            </el-input>
        </div>
        <div class="biaoti current_price">
            {{ $t('当前余额') }}: {{ priceFormat(userMoney?.money) }} USD
            <span v-if="selectValue == 0">≈ {{ exchangeRateConversion }} {{ selectCurrency }}</span>
        </div>
        <!-- <div class="info-tips">
            <p>
                {{ $t('实际到账') }}：{{ ['BTC', 'ETH'].includes(this.selectCurrency) ? priceFormat8(it.input1 - it.input1 *
                    withdraw_fee) : priceFormat(it.input1 - it.input1 * withdraw_fee) }}
                <span>{{ selectValue == 0 ? selectCurrency : 'USD' }}</span>
            </p>
            <p>{{ $t('手续费') }}：{{ (withdraw_fee * 100).toFixed(2) }}%</p>
        </div> -->
        <div class="tijiao" style="padding-top: 20px;">
            <div class="tijiao2" style="width: 100%;" @click="biaodan_tijiao2">{{ $t('提交') }}</div>
        </div>
        <van-overlay :show="show" @click="show = false">
            <div class="wrapper">
                <!--        <div class="block" />-->
                <div style="width: 100%;background:  #F3F5F9;border-radius: 5px 5px 0 0 ;" class="h150">
                    <van-password-input style="margin-top: 30px;" :value="value" :gutter="10" :focused="showKeyboard"
                        @focus="showKeyboard = true" />
                    <div style="text-align: center;font-size: 14px;margin-top: 30px;">{{ $t('资金密码') }}</div>
                </div>
                <!-- 数字键盘 -->
                <van-number-keyboard v-model="value" :show="showKeyboard" @blur="showKeyboard = true" />
            </div>
        </van-overlay>
        <van-overlay :show="bindShow">
            <div class="bind_wrap">
                <div class="title">
                    <span>{{ $t('提款地址绑定') }}</span>
                    <!-- <van-icon name="cross" @click="bindShow = false" /> -->
                </div>
                <div class="biaoti" style="margin-bottom: 5px;">{{ $t('取款方式') }}</div>
                <div class="shuru">
                    <el-select v-model="bindData.coin" :placeholder="$t('请选择取款方式')" @change="handleCoinChange">
                        <el-option v-for="item in withdrawalMethod" :key="item.value" :label="item.label"
                            :value="item.value">
                        </el-option>
                    </el-select>
                </div>
                <div class="biaoti" style="margin-bottom: 5px;">{{ $t('链接协议') }}</div>
                <div class="shuru">
                    <el-select v-model="bindData.blockchain_name" :placeholder="$t('请选择链接协议')"
                        :no-data-text="$t('请先选择取款方式')">
                        <el-option v-for="item in linkProtocolOptions" :key="item.value" :label="item.label"
                            :value="item.value">
                        </el-option>
                    </el-select>
                </div>
                <div class="biaoti" style="margin-bottom: 5px;">{{ $t('收款钱包地址') }}</div>
                <div class="shuru">
                    <el-input :placeholder="$t('请输入钱包地址')" v-model="bindData.channel_address" clearable>
                    </el-input>
                </div>
                <div class="hint">{{ $t('仅能绑定一个收款地址!') }}</div>
                <van-button @click="requestHandleBind" class="submit_btn" block type="primary">{{ $t('确认绑定') }}</van-button>
            </div>
        </van-overlay>
        <!-- <Footer /> -->
    </div>
</template>
<script>
import QRCode from 'qrcode'
import { Toast, Uploader, Overlay, PasswordInput, NumberKeyboard, Icon, Dialog, Tab, Tabs } from 'vant';
import {
    session_token, shifoushzhi_zijinmima_post,
    shouxufeibaifenbi_post, tixian_post,
    tupianshangchuan_post,
    zhifutongdao_post,
    apiWithdrawBefore,
    apiBindAddress,
    apiRealTimeExchangeRates
} from "@/API/user";
import { mapGetters } from 'vuex'
import Footer from '@/components/Footer'
import { isLogin, priceFormat, priceFormat8, deduplication } from '@/utils/utis'
export default {
    data() {
        return {
            priceFormat,
            priceFormat8,
            itemName: process.env.VUE_APP_ITEM_NAME,
            data: {},
            codes: '',
            currentChainName: {},
            imgUrl: '',
            tongdao: [],
            it: {
                input1: '',
                input2: ''
            },
            card: {
                bankName: '',
                bankUserName: '',
                bankCardNo: ''
            },
            fileList: [],
            shangchuanurl: '',
            session_token: '',
            withdraw_fee: '',
            coinType: '',
            value: '',
            allowEditWithdrawAddress: false,
            showKeyboard: true,
            show: false,
            bindShow: false,
            bindData: {
                coin: '',
                blockchain_name: '',
                channel_address: ''
            },
            blockchainNetwork: [''],
            withdrawBefore: {},
            linkProtocol: [],
            linkProtocolOptions: [],
            selectValue: '0',
            selectCurrency: '',
            withdrawalMethod: [],
            currentRate: 0,
        }
    },

    components: {
        Footer,
        QRCode: QRCode,
        [Icon.name]: Icon,
        [Tab.name]: Tab,
        [Tabs.name]: Tabs,
        [Uploader.name]: Uploader,
        [Overlay.name]: Overlay,
        [Dialog.name]: Dialog,
        [PasswordInput.name]: PasswordInput,
        [NumberKeyboard.name]: NumberKeyboard
    },
    async created() {
        if (!isLogin()) {
            this.$router.push('/')
        } else {
            this.$store.dispatch("getUserMoney");
            await this.requestWithdrawBefore()
            this.zhifutongdao()
        }
        if (sessionStorage.getItem('withdraw_price')) {
            this.it.input1 = sessionStorage.getItem('withdraw_price')
            this.it.input2 = sessionStorage.getItem('withdraw_address')
            this.card.bankName = sessionStorage.getItem('withdraw_bankName')
            this.card.bankUserName = sessionStorage.getItem('withdraw_bankUserName')
            this.card.bankCardNo = sessionStorage.getItem('withdraw_bankCardNo')
            this.selectValue = sessionStorage.getItem('withdraw_index')
        }
    },
    computed: {
        ...mapGetters({
            userMoney: "userMoney",
        }),
        exchangeRateConversion() {
            if (!this.currentRate) return 0
            if (['BTC', 'ETH'].includes(this.selectCurrency)) {
                return this.priceFormat8(this.userMoney?.money / this.currentRate)
            }
            return this.priceFormat(this.userMoney?.money / this.currentRate)
        },
    },
    methods: {
        // 获取实时汇率
        async requestLiveRates(symbol) {
            const res = await apiRealTimeExchangeRates({ symbol })
            this.currentRate = res.price
        },
        // 选择币种
        selectCurrencyChange(val) {
            this.it.input1 = ''
            this.blockchainNetwork = []
            const tempItem = this.linkProtocol.filter(item => item.coin == val)
            tempItem.forEach(item => {
                this.blockchainNetwork.push(item.blockchain_name)
            })
            this.coinType = val
            this.currentChainName = this.blockchainNetwork[0]
            this.requestLiveRates(val)
            this.shouxufei()
        },
        async requestWithdrawBefore() {
            const res = await apiWithdrawBefore()
            // allowEditWithdrawAddress   是否允许用户编辑提现地址  0 - 不允许 1 - 允许
            // chainName                  币种协议 ERC20
            // existWithdrawAddress       旧的提现地址 
            // needBindWithdrawAddress    是否提示绑定提现地址 0 - 不提示 1 - 提示
            // openWithdrawAddressBinding 是否开启绑定提现地址 0 - 不开启 1 - 开启
            if (res?.openWithdrawAddressBinding == 0) return
            this.allowEditWithdrawAddress = !!res.existWithdrawAddress
            this.bindShow = !res.existWithdrawAddress
            this.it.input2 = res.existWithdrawAddress
            this.blockchainNetwork = [res.chainName]
            this.currentChainName = this.blockchainNetwork[0]
            this.session_token = res.session_token
            this.coinType = res.coinType
        },
        // 弹框 - 绑定按钮
        async requestHandleBind() {
            if (this.bindData.coin == '') {
                this.$notify(this.$t('请选择取款方式'));
                return
            }
            if (this.bindData.blockchain_name == '') {
                this.$notify(this.$t('请选择链接协议'));
                return
            }
            if (this.bindData.channel_address == '') {
                this.$notify(this.$t('请输入钱包地址'));
                return
            }
            Toast.loading({
                message: this.$t('加载中...'),
                forbidClick: true,
            });
            try {
                await apiBindAddress(this.bindData)
                this.$notify(this.$t('绑定提现地址成功'), 'success');
                this.bindShow = false
                Toast.clear()
                this.blockchainNetwork = [this.bindData.blockchain_name]
                this.it.input2 = this.bindData.channel_address
                this.allowEditWithdrawAddress = true
            } catch (error) {
                Toast.clear()
            }
        },
        // 弹框 - 取款方式变更时
        handleCoinChange(val) {

            const tempArr = this.linkProtocol.filter(item => item.coin == val)
            this.linkProtocolOptions = tempArr.map(item => {
                return {
                    value: item.blockchain_name,
                    label: item.blockchain_name,
                    ...item
                }
            })
            this.bindData.blockchain_name = this.linkProtocolOptions[0].value
        },
        shouxufei() {
            shouxufeibaifenbi_post({
                channel: this.coinType,
            }).then(res => {
                this.withdraw_fee = res.withdraw_fee
            })
        },
        biaodan_tijiao2() {
            
            if (this.it.input1 === '') {
                Toast(this.$t('请输入金额'));
                return
            }
            if (this.userMoney?.money < this.it.input1) {
                return Toast(this.$t('账户余额不足'));
            }
            if (this.selectValue == 0) {
                // 虚拟币
                if (this.it.input2.trim() === '') {
                    Toast(this.$t('请输入地址'));
                    return;
                }
            } else {
                // 银行卡
                if (this.card.bankName.trim() === '') return Toast(this.$t('请输入开户行'))
                if (this.card.bankUserName.trim() === '') return Toast(this.$t('请输入姓名'))
                if (this.card.bankCardNo.trim() === '') return Toast(this.$t('请输入卡号'))
            }
            shifoushzhi_zijinmima_post({}).then(res => {
                if (res.safeword == 1) {
                    this.show = true
                    this.showKeyboard = true
                    if (sessionStorage.getItem('withdraw_price')) {
                        sessionStorage.removeItem('withdraw_price')
                        sessionStorage.removeItem('withdraw_address')
                        sessionStorage.removeItem('withdraw_bankName')
                        sessionStorage.removeItem('withdraw_bankUserName')
                        sessionStorage.removeItem('withdraw_bankCardNo')
                        sessionStorage.removeItem('withdraw_index')
                    }
                } else {
                    sessionStorage.setItem('withdraw_index', this.selectValue)
                    if (this.selectValue == 0) {
                        sessionStorage.setItem('withdraw_price', this.it.input1)
                        sessionStorage.setItem('withdraw_address', this.it.input2)
                    } else {
                        sessionStorage.setItem('withdraw_bankName', this.card.bankName)
                        sessionStorage.setItem('withdraw_bankUserName', this.card.bankUserName)
                        sessionStorage.setItem('withdraw_bankCardNo', this.card.bankCardNo)
                    }


                    this.$router.push({ path: '/FundPasswordSettings' })
                }
            })

        },
        biaodan_tijiao() {
            session_token({}).then(res => {
                this.session_token = res.session_token

                if (this.selectValue == 0) {
                    this.chongzhitijiao()
                } else {
                    const params = {
                        ...this.card,
                        session_token: this.session_token,
                        amount: this.it.input1,
                        channel: 'bank',
                        safeword: this.value
                    }
                    tixian_post(params).then(res => {
                        // Toast(this.$t('提交成功'));
                        Object.keys(this.card).forEach(key => {
                            this.card[key] = ''
                        })
                        
                        this.$router.push('/SubmitCompleted?path=withdrawRecord')
                    }).finally(() => {
                        this.it.input1 = ''
                        this.fileList = []
                        this.shangchuanurl = ''
                        this.value = ''
                        this.show = false
                    })
                }
            })
        },
        chongzhitijiao() {
            console.log('111');
            var data = {
                'session_token': this.session_token,
                'amount': this.it.input1,
                'from': this.it.input2,
                'channel': this.coinType,
                'safeword': this.value
            };
            this.show = false
            this.value = ''
            tixian_post(data).then(res => {
                // Toast(this.$t('提交成功'));
                this.it.input1 = ''
                this.fileList = []
                this.shangchuanurl = ''
                this.$router.push('/SubmitCompleted?path=withdrawRecord')

            }).then(res => {
                console.log('res', res);
            }).catch(e => {
                console.log('ee', e);
            })
        },
        tongdao_qiehuan(e) {
            this.currentChainName = e
            // this.useqrcode1()
        },
        zhifutongdao() {
            zhifutongdao_post({}).then(res22 => {
                // this.code = this.$route.query.usercode
                // this.withdrawalMethod = res22
                const tempArr = res22.map(item => ({ label: item.coin, value: item.coin }))
                this.withdrawalMethod = deduplication(tempArr, 'value')
                // this.coinType = this.selectCurrency = this.withdrawalMethod[0].value
                this.linkProtocol = res22
                for (var i = 0; i < res22.length; i++) {
                    this.tongdao.push(res22[i])
                }

                if (this.allowEditWithdrawAddress) return
                // this.blockchainNetwork = this.tongdao.map(item => item.blockchain_name)
                const tempItem = this.linkProtocol.filter(item => item.coin == this.selectCurrency)
                tempItem.forEach(item => {
                    item.blockchain_name && this.blockchainNetwork.push(item.blockchain_name)
                })
                this.blockchainNetwork = this.blockchainNetwork.filter(item => item)
                this.currentChainName = this.blockchainNetwork[0]
                this.requestLiveRates(this.selectCurrency)
                this.shouxufei()
                // this.bindData.coin = this.tongdao[0]
                // this.useqrcode1()
            })
        },
        afterRead(file) {
            let formData = new FormData();//通过formdata上传
            formData.append('file', file.file);
            tupianshangchuan_post(formData).then(res => {
                this.shangchuanurl = res
            }).catch(function (err) {
                this.fileList = []
                Toast(this.$t('添加失败'));
            })
        },
        copyData(ea) {
            //如果需要回调：
            this.$copyText(ea).then(e => {
                alert(this.$t('复制成功'))
            }, function (e) {
                alert(this.$t('复制失败'))
            })
        },
        copyData2(ea) {
            //如果需要回调：
            this.$copyText(ea).then(e => {
                // alert('复制成功')
            }, function (e) {
                // alert('复制失败')
            })
        },
        // useqrcode1() {//生成二维码
        //     let canvas = document.getElementById('canvas')
        //     let url = this.currentChainName.address
        //     QRCode.toCanvas(canvas, url, function (error) {
        //         if (error) {
        //         } else {
        //         }
        //     })
        //     this.saveImg()//保存图片
        // },
        baocunhaibao() {
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
        //保存图片
        saveImg() {
            let myCanvas = document.getElementsByTagName('canvas');
            this.imgUrl = myCanvas[0].toDataURL('image/png')
        },
        onClickLeft() {
            if (sessionStorage.getItem('withdraw_price')) {
                sessionStorage.removeItem('withdraw_price')
                sessionStorage.removeItem('withdraw_address')
                sessionStorage.removeItem('withdraw_bankName')
                sessionStorage.removeItem('withdraw_bankUserName')
                sessionStorage.removeItem('withdraw_bankCardNo')
                sessionStorage.removeItem('withdraw_index')
            }
            this.$router.push({ path: '/me', dir: 'left' })
            // this.$router.go(-1)
        },
        onClick1() {
            this.$router.push({ path: '/withdrawRecord' })
        },
        onCoinChange(val) {
            if (val == 1) {
                this.coinType = 'bank'
                this.shouxufei()
            } else {
                this.coinType = this.selectCurrency
                this.shouxufei()
            }
            if (['SM-wholesaleShop', 'FamilyShop'].includes(this.itemName)) {
                this.$router.push({ path: '/customerServiceIndex?path=customerService' })
                return
            }
            this.it.input1 = ''
        },
        handleInput(val) {
            if (val > this.userMoney?.money) {
                this.it.input1 = this.userMoney?.money
                return
            } else {
                this.it.input1 = this.it.input1.replace(/[^\d.]/g, ""); // 非数字和小数点替换为空字符串
                this.it.input1 = this.it.input1.replace(/\.{2,}/g, "."); // 连续出现多个小数点替换为单个小数点
                this.it.input1 = this.it.input1.replace(/^\./g, ""); // 第一个字符如果是小数点则替换为空字符串
                this.it.input1 = this.it.input1.replace(".", "$#$").replace(/\./g, "").replace("$#$", "."); // 将第一个小数点替换为$#$，去除所有小数点，再将$#$替换回小数点
                if (['BTC', 'ETH'].includes(this.selectCurrency)) {
                    this.it.input1 = this.it.input1.replace(/^(\-)*(\d+)\.(\d{0,10}).*$/, "$1$2.$3"); // 最多允许输入10位小数
                    this.it.input1 = this.it.input1.replace(/^\D*(\d{0,10}(?:\.\d{0,10})?).*$/g, "$1"); // 最多允许输入10位数字
                } else {
                    this.it.input1 = this.it.input1.replace(/^(\-)*(\d+)\.(\d{0,2}).*$/, "$1$2.$3"); // 最多允许输入2位小数
                    // this.it.input1 = this.it.input1.replace(/^\D*(\d{0,2}(?:\.\d{0,10})?).*$/g, "$1"); // 最多允许输入10位数字
                }

                // this.it.input1 = val
            }
        },

    },
    watch: {
        value(value) {
            if (value.length === 6) {
                this.showKeyboard = false
                this.biaodan_tijiao()
            }
        },
    }
}
</script>
<style lang="scss" scoped>
html[dir="rtl"] {
    .rtl_selected {
        right: -68px;
    }
}

.current_price {
    margin-top: 10px !important;
    margin-bottom: 0 !important;
    font-size: 12px !important;
    color: #79C642 !important;
}

.price_box {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-right: 30px;
    box-sizing: border-box;

    span {
        &:last-child {
            color: #93CA70;
        }
    }
}

.bind_wrap {
    min-height: 380px;
    background: #fff;
    border-radius: 8px;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    padding: 20px 15px;

    .title {
        font-weight: 700;
        font-size: 16px;
        line-height: 19px;
        display: flex;
        justify-content: center;
        align-items: center;

        .van-icon {
            font-size: 20px;
        }
    }

    .el-select,
    .el-input {
        width: 297px;
    }

    .biaoti {
        padding: 0 !important;
        margin-left: 0 !important;
    }

    .shuru {
        float: none !important;
        padding: 0 !important;
    }

    .hint {
        font-weight: 400;
        font-size: 14px;
        color: #FF3E3E;
        margin: 11px 0 21px 0;
        transform: translateY(11px);
    }

    .submit_btn {
        width: 302px;
        height: 44px;
        background: #F89900;
        border-radius: 4px;
        transform: translateY(11px);
    }
}

:deep(.el-select) {
    width: 100%;
}

.recharge {
    width: 100%;
    height: 100%;

    /deep/ .el-input {
        input:focus {
            // border-color: var(--main-color);
            border-color: var(--main-color);
        }
    }

    .biaoti {
        float: left;
        margin-top: 20px;
        width: 100%;
        margin-bottom: 10px;
        font-style: normal;
        font-weight: 400;
        font-size: 14px;
        color: #333333;
        margin-left: 15px;
    }

    .duoxuan {
        width: 100%;

        .xuan1 {
            float: left;
            margin-left: 15px;
            width: 105px;
            height: 40px;
            text-align: center;
            position: relative;
            font-style: normal;
            font-weight: 400;
            font-size: 14px;
            line-height: 40px;
            border-radius: 4px;
        }

        .weixuan {
            color: #999999;
            border: 1px solid #999999;
        }

        .xuanzhong {

            color: var(--main-color);
            border: 1px solid var(--main-color);
        }

        .xuanzhong-img {
            font-size: 40px;
            position: absolute;
            right: -1px;
            bottom: 0;
        }
    }

    .baocunerweima {
        display: flex;
        justify-content: center;
        //margin-top: 30px;
        width: 100%;
        float: left;

        .baocunerweima-buuon {
            width: 114px;
            height: 40px;
            border: 1px solid #DDDDDD;
            border-radius: 4px;
            font-style: normal;
            font-weight: 400;
            font-size: 14px;
            line-height: 40px; //
            text-align: center;

            /* 333 */

            color: #333333;
        }
    }

    .chongzhifuzhi {
        float: left;
        padding-left: 15px;
        padding-right: 15px;
        box-sizing: border-box;
        width: 100%;

        .chongzhifuzhi2 {
            padding: 0 10px;
            box-sizing: border-box;
            width: 100%;
            height: 44px;
            border: 1px solid #DDDDDD;
            font-style: normal;
            font-weight: 400;
            font-size: 14px;
            line-height: 44px;
            display: flex;

            /* 333 */

            color: #333333;

            .dizhi {
                width: 250px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
        }
    }

    .shuru {
        width: 100%;
        float: left;
        padding: 0 15px;
        box-sizing: border-box;
    }

    .tijiao {
        width: 100%;
        padding: 25px 15px;
        box-sizing: border-box;
        float: left;

        .tijiao2 {
            width: 100%;
            height: 44px;
            background: var(--main-color);
            border-radius: 4px;
            font-style: normal;
            font-weight: 400;
            font-size: 16px;
            line-height: 44px;
            /* identical to box height */

            text-align: center;

            color: #FFFFFF;
        }
    }

    .wrapper {
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-end;
        height: 100%;
    }

    //   .block {
    //     //width: 120px;
    //     //height: 120px;
    //     //background-color: #fff;
    //   }
    :deep(.van-number-keyboard) {
        position: sticky;
    }

    .info-tips {
        width: 100%;
        padding: 10px 15px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-sizing: border-box;

        >p {
            font-size: 12px;
            color: #999;

            &:last-child {

                color: var(--main-color);
            }
        }
    }
}

:deep(.van-key__wrapper) {
    &:nth-child(10) {
        svg {
            display: none;
        }
    }
}

:deep(.van-tabs) {
    width: 70%;
    margin: 0 auto;
}

:deep(.van-tabs__line) {
    background: var(--main-color) !important;
}

// :deep(.van-overlay) {
//     z-index: 9999;
// }
</style>
<style>
.van-uploader__upload {
    width: 120px !important;
    height: 120px !important;
}

.el-select-dropdown__item.selected {
    color: #F89900 !important;
}
</style>

