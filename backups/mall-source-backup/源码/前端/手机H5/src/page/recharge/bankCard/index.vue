<template>
    <div class="bank_card">
        <van-nav-bar safe-area-inset-top fixed :title="itemName == 'Hive' ? $t('加值') : $t('充值')" left-arrow
            @click-left="$router.push({ path: '/rechargeList', dir: 'left' })" :right-text="$t('记录')"
            @click-right="$router.push({ path: '/rechargeRecord' })" />
        <div style="width: 100%;" class="h46"></div>
        <el-form ref="form" :model="form" label-width="80px">
            <el-form-item :label="$t('选择币种')" v-if="!isGcash">
                <el-select v-model="form.currency" :placeholder="$t('请选择币种')" filterable :no-match-text="$t('无匹配数据')"
                    @change="handleChange">
                    <el-option v-for="item of coinList" :key="item.bank_code" :label="item.bank_code"
                        :value="item.bank_code"></el-option>
                </el-select>
            </el-form-item>
            <el-form-item :label="$t('充值金额')">
                <el-input type="number" step="0.01" v-model="form.price" :placeholder="`${min}-${max}`" @input="handleInput"
                    @change="handleInputChange" clearable></el-input>
            </el-form-item>
        </el-form>
        <div class="btn">
            <van-button block type="primary" :disabled="btnDis" @click="onSubmit">{{ $t('确认') }}</van-button>
        </div>
        <van-popup v-model="showPopup">
            <div class="popup_wrap">
                <div class="title">
                    {{ $t('请前往') }}{{ payName }}，{{ $t('继续完成支付') }}
                </div>
                <div class="path">
                    {{ path }}
                </div>
                <div class="btn">
                    <van-button type="primary" @click="handleAccess">{{ $t('继续访问') }}</van-button>
                </div>
            </div>
        </van-popup>
    </div>
</template>
<script>
import { apigetCoinList, apiSubmitRecharge, apiPhpRecharge, apiGcash2Recharge, apiGcash3Recharge, apiMayaRecharge, apiGCashPayRecharge } from '@/API/common'
import { session_token } from '@/API/user'
import { Toast, Popup } from 'vant'
export default {
    components: {
        [Toast.name]: Toast,
        [Popup.name]: Popup,
    },
    data() {
        return {
            itemName: process.env.VUE_APP_ITEM_NAME,
            coinList: [],
            max: '',
            min: '',
            form: {
                currency: '',
                price: ''
            },
            session_token: '',
            btnDis: true,
            isGcash: true,
            showPopup: false,
            path: ''
        }
    },
    computed: {
        payName() {
            return this.$route.query?.type == 'Maya' ? 'Maya' : 'GCash'
        }
    },
    async created() {
        session_token({}).then(res => {
            this.session_token = res.session_token
        })
        const { type, min, max } = this.$route.query
        this.isGcash = type != 'Bank'

        
        if (type == 'Bank') {
            Toast.loading({
                message: this.$t('加载中...'),
                forbidClick: true,
                duration: 0
            });
            try {
                const res = await apigetCoinList()
                this.coinList = res.filter(item => item.productType == type)[0].range
                this.form.currency = this.coinList[27].bank_code
                this.max = this.coinList[27].max_amount
                this.min = this.coinList[27].min_amount
                Toast.clear()
            } catch (error) {
                Toast.clear()
                this.$router.back()
            }
        } else {
            this.max = max
            this.min = min
        }
    },
    methods: {
        async onSubmit() {
            this.$toast.loading()
            if (this.form.price == '') return this.$notify(this.$t('请输入充值数量'))
            await session_token({}).then(res => {
                this.session_token = res.session_token
            })
            if (this.isGcash) {
                const typeToApiMap = {
                    'GCash2.0': apiGcash2Recharge,
                    'GCash3.0': apiGcash3Recharge,
                    'Maya': apiMayaRecharge,
                    'GCash pay': apiGCashPayRecharge,
                };
                const requestFn = typeToApiMap[this.$route.query?.type] || apiPhpRecharge;

                const params = {
                    amount: this.form.price,
                    session_token: this.session_token,
                    token: localStorage.getItem('token'),
                }
                if (['GCash2.0', 'GCash3.0', 'Maya', 'GCash pay'].includes(this.$route.query?.type)) {
                    params.pageUrl = window.location.href.split('#/')[0] + '#/me'
                }
                const path = await requestFn(params)
                if (window?.plus) {
                    plus.runtime.openURL(path)
                } else {
                    if (this.isIos()) {
                        this.path = path
                        this.showPopup = true
                    } else {
                        window.open(path)
                    }
                }
            } else {
                const path = await apiSubmitRecharge({
                    amount: this.form.price,
                    frenchCurrency: this.form.currency,
                    session_token: this.session_token
                })
                if (window?.plus) {
                    plus.runtime.openURL(path)
                } else {

                    if (this.isIos()) {
                        this.path = path
                        this.showPopup = true
                    } else {
                        window.open(path)
                    }
                }
            }
            this.$toast.clear()

        },
        // 判断是否是IOS
        isIos() {
            const u = navigator.userAgent;
            return !!u.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/);
        },

        handleChange(val) {
            this.form.price = ''
            const tempArr = this.coinList.filter(item => item.bank_code == val)
            this.max = tempArr[0].max_amount
            this.min = tempArr[0].min_amount
        },
        // 申请金额不能大于最大值
        handleInput() {
            this.form.price = this.form.price.replace(/[^\d.]/g, ""); // 非数字和小数点替换为空字符串
            this.form.price = this.form.price.replace(/\.{2,}/g, "."); // 连续出现多个小数点替换为单个小数点
            this.form.price = this.form.price.replace(/^\./g, ""); // 第一个字符如果是小数点则替换为空字符串
            this.form.price = this.form.price.replace(".", "$#$").replace(/\./g, "").replace("$#$", "."); // 将第一个小数点替换为$#$，去除所有小数点，再将$#$替换回小数点
            this.form.price = this.form.price.replace(/^(\-)*(\d+)\.(\d{0,2}).*$/, "$1$2.$3"); // 最多允许输入2位小数
            if (this.form.price > this.max) {
                this.form.price = this.max
            } else if (this.form.price < 1) {
                this.form.price = ''
            }
            this.btnDis = this.form.price < this.min
        },
        // 申请金额不能小于最小值
        handleInputChange() {
            if (this.form.price < this.min) {
                this.form.price = ''
                this.$notify(`${this.$t('申请金额不能小于')}${this.min}`)
                return
            }
            this.form.price = Number(this.form.price).toFixed(2)
        },
        // 查询Gcash最大最小值
        async handleGcashQuery(params) {
            const data = await apigetCoinList(params)
            return data[0]
        },
        handleAccess() {
            this.showPopup = false
            window.open(this.path)
        }
    }
}


</script>


<style lang="scss" scoped>
.popup_wrap {
    width: 86vw;
    padding: 15px;
    overflow: hidden;

    .title {
        font-size: 14px;
        text-align: left;
        line-height: 28px;
    }

    .path {
        font-size: 12px;
        text-align: left;
        line-height: 28px;
        color: #999999;
        border-bottom: 1px solid #E5E5E5;
        overflow: hidden;

    }

    .btn {
        margin-top: 15px;
        display: flex;
        justify-content: flex-end;
        align-items: center;
    }
}

.btn {
    padding: 0 15px;
}

:deep(.el-form) {
    padding: 0 15px;
}

:deep(.el-form-item) {
    display: flex;
    flex-direction: column;

    .el-form-item__content {
        margin: 0 !important;
    }
}

:deep(.van-button) {
    background: var(--main-color);
}

:deep(.el-form-item__label) {
    width: 100% !important;
    text-align: start !important;
}

:deep(.el-select) {
    width: 100%;
}
</style>
