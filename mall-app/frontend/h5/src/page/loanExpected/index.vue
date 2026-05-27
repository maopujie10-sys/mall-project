<template>
    <div class="merchantSettled">
        <van-nav-bar safe-area-inset-top :title="$t('预计还款')" left-arrow @click-left="$router.go(-1)" fixed ref="header">
        </van-nav-bar>
        <div class="merchantSettled-wap">
            <div class="step-div">
                <div>
                    <div class="content content2">
                        <el-form :model="ruleForm" :rules="rules" ref="ruleForm" :label-position="labelPosition"
                            label-width="200px" class="demo-ruleForm">
                            <el-form-item :label="$t('申请人')" prop="name">
                                <el-input disabled :placeholder="$t('真实姓名')" v-model="ruleForm.name"></el-input>
                            </el-form-item>
                            <el-form-item :label="$t('已贷款天数')" prop="days">
                                <el-input disabled :placeholder="`1${$t('天')}`" v-model="ruleForm.days"></el-input>
                            </el-form-item>
                            <el-form-item :label="$t('还款金额')" prop="amount">
                                <el-input :placeholder="$t('请输入还款金额')" disabled v-model="ruleForm.amount"></el-input>
                            </el-form-item>
                            <el-form-item :label="$t('贷款利率')" prop="interestRate">
                                <el-input placeholder="2%" disabled v-model="ruleForm.interestRate"></el-input>
                            </el-form-item>
                            <el-form-item :label="$t('还款方式')" prop="loanMethod">
                                <el-input :placeholder="`${$t('账户余额')}`" disabled
                                    v-model="ruleForm.loanMethod"></el-input>
                            </el-form-item>
                        </el-form>
                    </div>
                    <div class="bottom">
                        <van-button type="primary" :color="mainColor" class="button" @click="sellerRegister">{{
                            $t('确认还款')
                        }}
                        </van-button>
                    </div>
                </div>
            </div>
        </div>
        <!-- 密码弹窗 -->
        <van-popup v-model="pwtStatus" position="bottom">
            <enter-Password :isPasswordShow="pwtStatus" @close="pwtStatus = false"
                @getPassword="getPassword"></enter-Password>
        </van-popup>
        <nationality-list ref='controlChild' :title="$t('选择区域码')" @getName="getName(arguments)">
        </nationality-list>
    </div>
</template>

<script>
import { mapGetters, mapMutations } from "vuex";
import { DropdownMenu, DropdownItem, Dropdown, Form, FormItem, Input, Select, Option, } from 'element-ui'
import { Checkbox, Button, Uploader, Toast, Popup } from "vant";
import { uploadimg } from "@/API/commodity";
import { huoquyue_post, shifoushzhi_zijinmima_post } from "@/API/user";
import { apiLoanRepayForward, apiLoanPay } from '@/API/loan'
import EnterPassword from "@/components/EnterPassword/index.vue";
import NationalityList from '@/components/NationalityList'
export default {
    name: "merchantSettled",
    data() {
        return {
            mainColor: process.env.VUE_APP_MAIN_COLOR,
            screenWidth: document.body.clientWidth,
            uploadCheckIndex: 1,
            areaCode: 1,
            pwtStatus: false,
            ruleForm: {
                loanMethod: '',
                term: '',
                name: '',
                idimg_1: '',
                idimg_2: '',
                idimg_3: '',
                idname: '身份证',
                interestRate: '2%',
                nationality: '',
                sellerImg: '',
                username: '',
                amount: '',
            },
            labelPosition: 'top',
            isCode: true,
            rules: {
                // days: [
                //     { required: true, message: this.$t('请输入贷款天数'), trigger: 'blur' },
                // ],
                // interestRate: [
                //     { required: true, message: this.$t('请输入贷款利率'), trigger: 'blur' },
                // ],
                // name: [
                //     { required: true, message: this.$t('请输入真实姓名'), trigger: 'blur' },
                // ],
                // loanMethod: [
                //     { required: true, message: this.$t('请输入放款金额'), trigger: 'blur' },
                // ],
                amount: [
                    { required: true, message: this.$t('请输入金额'), trigger: 'blur' },
                ],
            },
            fileList1: [],
            fileList2: [],
            fileList3: [],
            fileList4: [],
            CountryList: [
                {
                    label: '中国',
                    value: 'cn',
                    icon: require('@/assets/image/language/cn.png')
                },
            ],
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
            pageDiaCode: true,
        };
    },

    computed: {
        languageIcon() {
            const language = this.$store.getters.language || 'tw'
            const icon = {
                'cn': require('@/assets/image/language/cn.png'),
                'en': require('@/assets/image/language/usa.png'),
                'tw': require('@/assets/image/language/tw.png')
            }
            return icon[language]
        },
        ...mapGetters({
            activeLang: 'language'
        })
    },
    components: {
        EnterPassword,
        NationalityList,
        [DropdownMenu.name]: DropdownMenu,
        [DropdownItem.name]: DropdownItem,
        [Dropdown.name]: Dropdown,
        [Popup.name]: Popup,
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
        if (this.screenWidth >= 500) {
            this.labelPosition = "left"
        } else {
            this.labelPosition = "top"
        }
        this.requireLoanRepayForward()
    },
    watch: {
        tabIndex(val, old) {
            if (val === old) return;
            this.ruleForm.username = '';
        }
    },
    methods: {
        // 还款前信息
        async requireLoanRepayForward() {
            const res = await apiLoanRepayForward({ creditId: this.$route.query.creditId })
            this.ruleForm.name = res.realName
            this.ruleForm.days = res.alreadyCreditDays
            this.ruleForm.interestRate = res.creditRate * 100 + '%'
            this.ruleForm.loanMethod = `${this.$t('账户余额')}: ${res.accountAmount}`
            this.ruleForm.amount = res.estimatePayment
        },
        // 还款请求
        async requireLoanPay(safeword) {
            const res = await apiLoanPay({ creditId: this.$route.query.creditId, safeword })
            this.$router.go(-1)
            this.$notify(this.$t('还款成功'), 'success')
        },
        getPassword(value) {
            this.requireLoanPay(value)
        },
        // 裁剪
        handleCutting() {
            this.isCutting = true;
        },
        // 取消
        handleCancel() {
            this.isCutting = false;
            this.fileList1 = [];
        },
        // 上传
        handleUpload(data) {
            let fileOfBlob = new File([data], "logo.png") // 重命名
            Toast.loading({
                duration: 0,
                message: this.$t('上传中'),
                forbidClick: true,
            })
            let formData = new FormData();//通过formdata上传
            formData.append('file', fileOfBlob)
            formData.append('moduleName', 'selle')

            uploadimg(formData).then((data) => {
                this.ruleForm.sellerImg = data
                this.isCutting = false

                this.fileList1[0].content = data
                // this.fileList1[0].file=fileOfBlob
            }).finally(() => {
                Toast.clear()
            })
        },
        // 裁剪
        handleCropData(data) {
            console.log('裁剪数据');
            console.log(data);
        },
        ...mapMutations(['setLanguage']),
        handleSetLang(index) {
            console.log(index)
            // 设置i18n.locale 组件库会按照上面的配置使用对应的文案文件
            this.$i18n.locale = this.lang[index].key
            // // 提交mutations
            this.setLanguage(this.lang[index].key)
        },
        handleDelete(index) {
            this[`fileList${index}`] = [];
        },
        sellerRegister() {
            this.$refs['ruleForm'].validate((valid) => {
                if (valid) {
                    // this.requireLoanPay()
                    this.handlePay()
                    // this.pwtStatus = true
                } else {
                    return false;
                }
            })
        },
        handlePay() {
            shifoushzhi_zijinmima_post({}).then((res) => {
                if (res.safeword == 1) {
                    this.pwtStatus = true;
                } else {
                    this.$router.push({ path: "/FundPasswordSettings" });
                }
            });
        },
        openNationality(index) {
            if (index === 1) {
                this.isCode = true
            } else {
                this.isCode = false
            }
            this.$refs.controlChild.open()
        },
        getName(params) {
            if (this.isCode) {
                this.areaCode = params[2]
            } else {
                this.ruleForm.nationality = params[0]
            }
        },
        //文件上传
        afterRead1(file) {
            this.imgFile = file.content
            this.isCutting = true
            // Toast.loading({
            //   duration: 0,
            //   message: this.$t('上传中'),
            //   forbidClick: true,
            // })
            // console.log(file)
            // let formData = new FormData();//通过formdata上传
            // formData.append('file', file.file)
            // formData.append('moduleName', 'selle')

            // uploadimg(formData).then((data) => {
            //   Toast.clear()
            //   this.ruleForm.sellerImg = data
            // })

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
                this.ruleForm.idimg_1 = data
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
                this.ruleForm.idimg_2 = data
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
                this.ruleForm.idimg_3 = data
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
.padding-tb {
    padding: 20Px 0 !important;
}

.color-yellow {
    color: var(--main-color) !important;
}

.merchantSettled {
    width: 100%;
    padding-top: 44px;
    overflow: hidden;

    .merchantSettled-wap {
        padding-top: 70px;
        background: #fff;
        display: flex;
        justify-content: center;
        align-items: center;
        width: 1200Px;
        margin: 0 auto;
        overflow: hidden;

        .step-div {
            width: 1197Px;
            background: #fff;

            border-radius: 4Px;
            margin-top: -86Px;

            .content {
                padding: 20Px 30Px;
                overflow: hidden;

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


@media screen and (max-width: 500Px) {
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
                    overflow: hidden;

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

@media screen and (max-width: 500Px) {
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
