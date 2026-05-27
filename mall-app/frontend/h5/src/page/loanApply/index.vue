<template>
    <div class="merchantSettled">
        <van-nav-bar safe-area-inset-top :title="$t('贷款申请')" left-arrow @click-left="$router.go(-1)" fixed ref="header">
        </van-nav-bar>
        <div class="merchantSettled-wap">
            <div class="step-div">
                <div>
                    <div class="content content2">
                        <el-form :model="ruleForm" :rules="rules" ref="ruleForm" label-position="top" label-width="200px"
                            class="demo-ruleForm">
                            <el-form-item :label="$t('申请人')" prop="realName">
                                <el-input :placeholder="$t('真实姓名')" clearable :maxlength="100"
                                    v-model="ruleForm.realName"></el-input>
                            </el-form-item>
                            <el-form-item :label="$t('贷款期限')" prop="creditPeriod">
                                <el-select v-model="ruleForm.creditPeriod" :placeholder="$t('请选择贷款期限')"
                                    @change="handleSelectChange">
                                    <el-option v-for="item in creditPeriodList" :key="item.value" :label="item.label"
                                        :value="item.value" :style="item.dis && { color: '#999' }">
                                    </el-option>
                                </el-select>
                            </el-form-item>
                            <el-form-item :label="$t('申请金额')" prop="applyAmount">
                                <el-input :placeholder="amountMin + '-' + amountMax" type="number"
                                    v-model="ruleForm.applyAmount" @input="handleInput" @change="handleChange"
                                    clearable></el-input>
                            </el-form-item>
                            <el-form-item :label="$t('贷款利率')" prop="interestRate">
                                <el-input :placeholder="rate * 100 + '%'" disabled></el-input>
                            </el-form-item>
                            <el-form-item :label="$t('放款方式')" prop="loanMethod">
                                <el-input :placeholder="$t('账户余额')" disabled></el-input>
                            </el-form-item>
                            <el-form-item :label="$t('国籍')" prop="countryId">

                                <el-select v-model="countryName" filterable :placeholder="$t('请选择')"
                                    :no-data-text="$t('暂无数据')" :no-match-text="$t('暂无数据')" :loading-text="$t('加载中')"
                                    @change="onCountryChange">
                                    <el-option v-for="item in countryList" :key="item.id" value-key="countryName"
                                        :label="item.countryName" :value="item.id">
                                    </el-option>
                                </el-select>
                            </el-form-item>
                            <el-form-item :label="$t('证件号码/护照号码')" prop="identification">
                                <el-input :placeholder="$t('请输入证件号码或者护照号')" clearable :maxlength="50"
                                    v-model="ruleForm.identification" @change="idCartChange"></el-input>
                            </el-form-item>
                            <el-form-item class="el-form-required-box" :label="$t('证件照/上传护照')">
                                <span class="required">*</span>
                                <div class="uploder-center">
                                    <div class="uploder-two-wrap">
                                        <van-uploader :after-read="afterRead2" v-model="fileList2" @delete="handleDelete(2)"
                                            :max-count="1" accept=".png,.jpg,.jpeg">
                                            <img v-if="creditId" class="card_img" :src="ruleForm.imgCertificateFace"
                                                alt="" />
                                        </van-uploader>
                                        <div class="tips">{{ $t('证件正面') }}</div>
                                    </div>
                                    <div class="uploder-two-wrap">
                                        <van-uploader :after-read="afterRead3" v-model="fileList3" @delete="handleDelete(3)"
                                            :max-count="1" accept=".png,.jpg,.jpeg">
                                            <img v-if="creditId" class="card_img" :src="ruleForm.imgCertificateBack"
                                                alt="" />
                                        </van-uploader>
                                        <div class="tips">{{ $t('证件反面') }}</div>
                                    </div>
                                    <div class="uploder-two-wrap">
                                        <van-uploader :after-read="afterRead4" v-model="fileList4" @delete="handleDelete(4)"
                                            :max-count="1" accept=".png,.jpg,.jpeg">
                                            <img v-if="creditId" class="card_img" :src="ruleForm.imgCertificateHand"
                                                alt="" />
                                        </van-uploader>
                                        <div class="tips">{{ $t('手持证件照') }}</div>
                                    </div>
                                </div>
                                <div style="display: flex; flex-direction: column;">
                                    <div class="el-form-item__label" style="margin-bottom: -26px">{{ $t('拍摄示例') }}</div>
                                    <div class="correct-warp">
                                        <img src="@/assets/image/Merchant/01.png" />
                                        <img src="@/assets/image/Merchant/02.png" />
                                        <img src="@/assets/image/Merchant/03.png" />
                                    </div>
                                </div>
                            </el-form-item>
                        </el-form>
                    </div>
                    <div class="checkout_box">
                        <van-checkbox shape="square" v-model="isAgree">{{ $t('我已阅读并同意') }}</van-checkbox>
                        <span @click="handleJump">《{{ $t('借款协议') }}》</span>
                    </div>

                    <div class="bottom">
                        <van-button type="primary" :color="mainColor" class="button" @click="requireSellerRegister">{{
                            $t('提交申请')
                        }}
                        </van-button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { DropdownMenu, DropdownItem, Dropdown, Form, FormItem, Input, Select, Option } from 'element-ui'
import { Checkbox, Button, Uploader, Toast } from "vant";
import { uploadimg } from "@/API/commodity";
import { apiApplyLoan, apiApplyLoanConfig, apiBeforereApply, apiListCountry } from '@/API/loan'
import { priceFormat, getStorage, isAlphanumeric } from '@/utils/utis'

export default {
    data() {
        return {
            mainColor: process.env.VUE_APP_MAIN_COLOR,
            isAlphanumeric,
            creditPeriodList: [],
            lendableDays: [],
            defaultRate: [],
            amountMax: '',
            amountMin: '',
            rate: '',
            //
            priceFormat,
            getStorage,
            isCutting: false,// 是否裁剪
            imgFile: '',
            ratioWidth: 1,// 裁剪比例：长 自由比例设置为: 0 即可
            ratioHeight: 1,// 裁剪比例：宽 自由比例设置为: 0 即可
            step: 1,
            checked: false,
            screenWidth: document.body.clientWidth,
            type: 'Email',//Email/Moblie
            uploadCheckIndex: 1,
            areaCode: 1,
            isAgree: false,
            countryName: '',
            ruleForm: {
                // loanMethod: this.$t('账户余额'),
                creditPeriod: '',
                realName: '',
                imgCertificateFace: '',
                imgCertificateBack: '',
                imgCertificateHand: '',
                // interestRate: '2%',
                countryId: '',
                applyAmount: '',
                identification: ''
            },
            labelPosition: 'top',
            isCode: true,
            rules: {
                identification: [
                    { required: true, message: this.$t('请输入证件号码或者护照号'), trigger: 'blur' },
                ],
                imgCertificateFace: [
                    { required: true, message: this.$t('请上传身份证正面'), trigger: 'blur' },
                ],
                imgCertificateBack: [
                    { required: true, message: this.$t('请上传身份证反面'), trigger: 'blur' },
                ],
                imgCertificateHand: [
                    { required: true, message: this.$t('请上传手持身份证'), trigger: 'blur' },
                ],
                realName: [
                    { required: true, message: this.$t('请输入真实姓名'), trigger: 'blur' },
                    { pattern: /^\S.*\S$|(^\S{0,1}\S$)/, message: this.$t('首尾不能为空格'), trigger: 'blur' }
                ],
                applyAmount: [
                    { required: true, message: this.$t('请输入金额'), trigger: 'blur' },
                ],
                creditPeriod: [
                    { required: true, message: this.$t('请选择贷款期限'), trigger: 'change' },
                ],
                countryId: [
                    { required: true, message: this.$t('请选择国家'), trigger: 'change' },
                ],
            },
            options: [{ label: this.$t('身份证'), value: '身份证' }, { label: this.$t('护照'), value: '护照' }],
            fileList1: [],
            fileList2: [],
            fileList3: [],
            fileList4: [],
            tabList: [this.$t('电子邮箱'), this.$t('手机号')],
            tabIndex: 0,
            lang: [
                {
                    title: '简体中文',
                    key: 'cn',
                    icon: require('@/assets/image/language/cn.png')
                },
                {
                    title: 'English',
                    key: 'en',
                    icon: require('@/assets/image/language/usa.png')
                },
                {
                    title: '繁体中文',
                    key: 'tw',
                    icon: require('@/assets/image/language/tw.png')
                }
            ],
            countryList: [],
            pageDiaCode: true,
            creditId: this.$route.query?.creditId || null
        };
    },

    components: {
        // NationalityList,
        [DropdownMenu.name]: DropdownMenu,
        [DropdownItem.name]: DropdownItem,
        [Dropdown.name]: Dropdown,

        [Checkbox.name]: Checkbox,
        [Button.name]: Button,
        [Form.name]: Form,
        [FormItem.name]: FormItem,
        [Input.name]: Input,
        [Uploader.name]: Uploader,
        [Select.name]: Select,
        [Option.name]: Option,
        [Toast.name]: Toast
    },
    created() {
        this.requireApplyLoanConfig()
        this?.creditId && this.requireBeforereApply(this.creditId)
        this.requestGetCountryList()
    },
    methods: {
        // 获取国家
        async requestGetCountryList() {
            const { data } = await apiListCountry()
            this.countryList = data
        },
        onCountryChange(id) {
            this.ruleForm.countryId = id
        },
        async requireApplyLoanConfig() {
            const res = await apiApplyLoanConfig()
            res.allLendableDays.forEach(x => {
                res.lendableDays.forEach(y => {
                    this.creditPeriodList.push({
                        label: x + this.$t('天'),
                        value: x,
                        dis: x !== y
                    })
                })
            })
            this.creditPeriodList = this.deduplication(this.creditPeriodList, 'value')
            this.creditPeriodList.forEach(x => {
                res.lendableDays.forEach(y => {
                    if (x.value == y) {
                        x.dis = false
                    }
                })
            })
            this.lendableDays = res.lendableDays
            this.amountMax = res.amountMax
            this.amountMin = res.amountMin
            this.rate = res.rate
        },
        async requireBeforereApply(creditId) {
            const res = await apiBeforereApply({ creditId })
            this.ruleForm.realName = res.realName
            this.ruleForm.applyAmount = res.applyAmount
            this.ruleForm.creditPeriod = res.creditPeriod + ''
            this.handleSelectChange(res.creditPeriod + '')
            this.rate = res.creditRate
            this.ruleForm.countryId = res.countryId
            this.ruleForm.identification = res.identification
            this.ruleForm.imgCertificateFace = res.imgCertificateFace
            this.ruleForm.imgCertificateBack = res.imgCertificateBack
            this.ruleForm.imgCertificateHand = res.imgCertificateHand

        },
        deduplication(arr, name) {
            const obj = {};
            return arr.reduce((prev, cur) => {
                obj[cur[name]] ? '' : obj[cur[name]] = true && prev.push(cur);
                return prev
            }, []);
        },

        handleJump() {
            if (window.plus) {
                window.plus.runtime.openURL(`${window.origin}/promote/#/contract?lang=${getStorage('lang')}`)
            } else {
                window.open(`${window.origin}/promote/#/contract?lang=${getStorage('lang')}`)
            }
        },
        idCartChange() {
            if (!this.isAlphanumeric(this.ruleForm.identification)) {
                this.$notify(this.$t('证件号码/护照号码验证未通过'))
                this.ruleForm.identification = ''
            }
        },


        handleDelete(index) {
            this[`fileList${index}`] = [];
        },
        // 提交申请贷款
        requireSellerRegister() {
            this.$refs['ruleForm'].validate((valid) => {
                if (valid) {
                    if (!this.ruleForm.imgCertificateFace || !this.ruleForm.imgCertificateBack || !this.ruleForm.imgCertificateHand) {
                        // Toast(this.$t('请上传证件照片'))
                        this.$notify(this.$t('请上传证件照片'))
                    } else {
                        if (!this.isAgree) return this.$notify(this.$t('请阅读并同意借款协议'))
                        this.creditId && (this.ruleForm.creditId = this.creditId)
                        apiApplyLoan(this.ruleForm).then(res => {
                            this.$notify(this.$t('申请成功'), 'success')
                            this.$router.replace('/loan/my')
                        }).catch(err => {
                            console.log(`err ::->`, err);
                        })
                    }
                } else {
                    return false;
                }
            })
        },
        handleSelectChange(val) {
            let day = this.lendableDays.find(x => x == val)
            !day && this.$notify(this.$t('未满足资质条件'))
            !day && (this.ruleForm.creditPeriod = '')
        },
        // 申请金额不能大于最大值
        handleInput() {
            if (this.ruleForm.applyAmount > this.amountMax) {
                this.ruleForm.applyAmount = this.amountMax
            } else if (this.ruleForm.applyAmount < 1) {
                this.ruleForm.applyAmount = ''
            }
        },
        // 申请金额不能小于最小值
        handleChange() {
            if (this.ruleForm.applyAmount < this.amountMin) {
                this.ruleForm.applyAmount = ''
                this.$notify(`${this.$t('申请金额不能小于')}${this.amountMin}`)
            }
        },
        openNationality(index) {
            if (index === 1) {
                this.isCode = true
            } else {
                this.isCode = false
            }
            this.$refs.controlChild.open()
        },

        //文件上传
        afterRead2(file) {
            Toast.loading({
                duration: 0,
                message: this.$t('上传中'),
                forbidClick: true,
            })
            let formData = new FormData();//通过formdata上传
            formData.append('file', file.file)
            formData.append('moduleName', 'selle')
            uploadimg(formData).then((data) => {
                this.ruleForm.imgCertificateFace = data
            }).catch((error) => {
                this.fileList2 = [];
                Toast.fail(this.$t('上传失败'));
            }).finally(() => {
                Toast.clear()
            })
        },
        //文件上传
        afterRead3(file) {
            Toast.loading({
                duration: 0,
                message: this.$t('上传中'),
                forbidClick: true,
            })
            let formData = new FormData();//通过formdata上传
            formData.append('file', file.file)
            formData.append('moduleName', 'selle')
            uploadimg(formData).then((data) => {
                this.ruleForm.imgCertificateBack = data
            }).catch((error) => {
                this.fileList3 = [];
                Toast.fail(this.$t('上传失败'));
            }).finally(() => {
                Toast.clear()
            })
        },
        //文件上传
        afterRead4(file) {
            Toast.loading({
                duration: 0,
                message: this.$t('上传中'),
                forbidClick: true,
            })
            let formData = new FormData();//通过formdata上传
            formData.append('file', file.file)
            formData.append('moduleName', 'selle')
            uploadimg(formData).then((data) => {
                this.ruleForm.imgCertificateHand = data
            }).catch((error) => {
                this.fileList4 = [];
                Toast.fail(this.$t('上传失败'));
            }).finally(() => {
                Toast.clear()
            })
        }
    },

};
</script>

<style lang="scss" scoped>
.checkout_box {
    margin-left: 30PX;
    font-size: 14px;
    transform: translateY(20px);
    display: flex;
    justify-content: center;
    align-items: center;

    span {
        color: var(--main-color);
    }
}

.padding-tb {
    padding: 20Px 0 !important;
}

.color-yellow {
    color: var(--main-color) !important;
}

.card_img {
    width: 80px;
    height: 80px;
}

.merchantSettled {
    width: 100%;
    padding-top: 44px;

    .merchantSettled-wap {
        padding-top: 70px;
        background: #fff;
        display: flex;
        justify-content: center;
        align-items: center;
        width: 1200Px;
        margin: 0 auto;

        .step-div {
            width: 1197Px;
            background: #fff;
            border-radius: 4Px;
            margin-top: -86Px;

            .content {
                padding: 20Px 30Px;
                border: 1Px solid #eeeeee;

                .title {
                    font-size: 24Px;
                    color: #333333;
                    font-weight: 700;
                }

                p {
                    font-family: "PingFang HK";
                    font-style: normal;
                    font-size: 14Px;
                    line-height: 20Px;
                    color: #333333;
                    padding: 6Px 0;
                }
            }

            .bottom {
                height: 140Px;
                font-size: 14Px;
                display: flex;
                flex-direction: column;
                justify-content: space-around;
                align-items: center;
                margin: 20Px 0;

                .button {
                    width: 475Px;
                }
            }
        }
    }
}

/deep/ .van-field__label {
    width: 200Px !important;
}

/deep/ .van-tabs__wrap {
    width: 250Px;
}


@media screen and (max-width: 1000Px) {
    .merchantSettled {
        width: 100%;

        .merchantSettled-wap {
            background: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100% !important;

            .step-div {
                width: 100%;
                background: #fff;

                border-radius: 4Px;
                margin-top: -86Px;

                .content {
                    padding: 20Px 30Px;
                    border: 1Px solid #eeeeee;

                    .title p {
                        font-family: "PingFang HK";
                        font-style: normal;
                        font-size: 14Px;
                        line-height: 20Px;
                        color: #333333;
                        padding: 6Px 0;
                    }
                }

                // .content2 {
                //   // padding: 20Px 10Px;
                // }

                .bottom {
                    height: 100Px;
                    font-size: 12Px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-around;
                    align-items: center;
                    margin: 20Px 0;

                    .button {
                        width: 80%;
                    }
                }
            }
        }
    }
}

.el-form-required-box {
    position: relative;
    display: flex;
    flex-direction: column;
    :deep(.el-form-item__content) {
        position: static !important;
    }
    :deep(.el-form-item__label) {
        padding-left: 10px !important;
    }
    .required {
        position: absolute;
        top: 7px;
        left: 0;
        color: #F56C6C;
    }
}

.demo-ruleForm {
    .uploder-wrap {
        display: flex;
        align-items: center;

        .tips {
            font-size: 12Px;
            color: #999999;

            span {
                color: var(--main-color);
            }
        }
    }


    .uploder-center {
        display: flex;

        .uploder-two-wrap {
            margin-right: 30Px;

            .tips {
                color: #333333;
                font-size: 12Px;
                text-align: center;
                line-height: 16Px;
            }
        }
    }

    .correct-warp {
        display: flex;

        img {
            width: 100Px;
            margin-right: 20Px;
        }
    }

    .tab-wrap {
        display: flex;
        margin-top: 20Px;

        .tab-item {
            width: 98Px;
            height: 34Px;
            background: #EEEEEE;
            border-radius: 4Px;
            text-align: center;
            cursor: pointer;
            line-height: 34Px;
            margin-right: 20Px;
            color: #333333;
            font-size: 14Px;
        }

        .active {
            color: #fff !important;
            background: var(--main-color) !important;
        }
    }

    .code-input {
        width: 420Px;
    }

    .code-wrap {
        width: 133Px;
        height: 34Px;
        background: var(--main-color);
        border-radius: 4Px;
        margin-top: 8Px;
        text-align: center;
        line-height: 34Px;
        font-size: 14Px;
        color: #fff;
        cursor: pointer;
    }

    .el-dropdown {
        width: 100%;
    }

    .prepend-wrap {
        display: flex;
        align-items: center;
        padding: 0 20Px;

        .phone_number {
            flex: 1;
        }
    }

    .phone_number_wrap {
        /deep/ .el-input__inner {
            width: 345px;
        }

    }
}

.option-wrap {
    display: flex;
    align-items: center;
    font-size: 14Px;

    img {
        height: 30Px;
        margin-right: 5Px;
    }
}

.lang-item {
    display: flex;
    align-items: center;

    img {
        width: 20Px;
        height: 20Px;
        margin-right: 5px;
    }
}

/deep/ .el-form-item__label {
    text-align: left !important;
    padding: 0 !important;
    transform: translateY(5px);
}

/deep/ .el-form-item {
    margin-bottom: 10px;
}

/deep/ .el-select-dropdown__list {
    padding: 10Px 0 !important;
}

/deep/ .el-select .el-input .el-select__caret {
    font-size: 15Px;
    display: flex;
    align-items: center;
}

.el-select-dropdown__item.selected {
    color: var(--main-color) !important;
}

.el-select .el-input.is-focus .el-input__inner {
    padding-left: 30Px !important;
}

/deep/ .el-input__inner {
    height: 44px;
    width: 345px;
    font-size: 14Px;
    border: 1px solid #EEEEEE;

    &::placeholder {
        font-size: 14Px;
        color: #999999;
    }
}

/deep/ .van-uploader__upload-icon {
    font-size: 35Px !important;
    color: #AAAAAA !important;
}

/deep/.el-input-group__prepend {
    width: 100Px !important;
    padding: 0 !important;
    background: none !important;
    font-size: 14Px;
}

@media screen and (max-width: 1000Px) {
    /deep/ .el-input__inner {
        width: 100% !important;
    }

    /deep/ .el-select {
        width: 100%;
    }

    .phone_number_wrap {
        /deep/ .el-input__inner {
            width: 100% !important;
        }

    }

    .demo-ruleForm .code-input {
        width: 100%;
    }

    .correct-warp {
        img {
            display: block;
            margin-top: 20Px;
            margin-right: 10Px !important;
        }
    }
}

/deep/ .van-checkbox__icon--checked .van-icon {
    background-color: var(--main-color) !important;
    border-color: var(--main-color) !important;
}

/deep/ .el-input.is-disabled .el-input__inner {
    background-color: #fff;
}
</style>
