<template>
    <div class="page-content" style="min-height: 100vh;">
        <nationality-list ref='controlChild' :title="$t('选择区域码')" @getName="getName(arguments)"></nationality-list>
        <Vcode style="direction: ltr;" :imgs="[img1, img2, img3, img4, img5]" :show="show" @success="onSuccess" :canvasHeight="200"
            @close="show = false;" :sliderText="$t('拖动滑块以完成拼图')" :successText="$t('验证通过!')" :failText="$t('验证失败,请重试')" />

        <van-nav-bar safe-area-inset-top fixed :title=" $t('手机绑定') " left-arrow @click-left=" onClickLeft " />
        <div style="width: 100%;" class="h46"></div>

        <div class="form-content">
            <div class="form-item">
                <div class="title">{{ $t('手机号') }}</div>
                <div class="input-content">
                    <el-input :placeholder=" $t('请输入手机号') " maxlength="20" v-model=" formData.phone " clearable>
                        <div slot="prepend" @click=" openNational ">
                            <p>+<span>{{ dialCode }}</span> <img :src=" triangleDown " alt="" class="icon" /></p>
                        </div>
                    </el-input>
                </div>
            </div>
            <div class="form-item">
                <div class="title">{{ $t('验证码') }}</div>
                <div class="input-content code">
                    <el-input :placeholder=" $t('请输入验证码') " maxlength="6" v-model=" formData.verifcode ">
                    </el-input>
                    <div class="btn" :class=" { 'disabled': btnDisabled } " @click=" getCode ">{{ codeBtnTxt }}</div>
                </div>
            </div>
            <div class="submit-btn" @click=" submitVertify ">{{ $t('提交') }}</div>
        </div>

    </div>
</template>

<script>
import { Toast } from "vant";
import Vcode from "vue-puzzle-vcode";
import NationalityList from '@/components/NationalityList'
import {
    getIdcode
} from '@/API/common'
import {
    savePhone
} from '@/API/user'
export default {
    name: 'BindPhone',
    components: {
        NationalityList,
        Vcode
    },
    data() {
        return {
            img1: require('@/assets/image/slider/1.png'),
            img2: require('@/assets/image/slider/2.png'),
            img3: require('@/assets/image/slider/3.png'),
            img4: require('@/assets/image/slider/4.png'),
            img5: require('@/assets/image/slider/5.png'),
            triangleDown: require('@/assets/image/me/triangle_down.png'),
            show: false,
            pageDiaCode: false,
            dialCode: localStorage.getItem('dialCode') || 1,
            codeBtnTxt: this.$t('收取验证码'),
            count: 60,
            interval: null,
            btnDisabled: false,
            formData: {
                phone: '',
                verifcode: ''
            }
        }
    },
    methods: {
        onClickLeft() {
            this.$router.push({ path: '/Setting', dir: 'left' })

        },

        onSuccess() {
            this.submitHandle()
            this.show = false
        },

        getName(params) {
            if (!this.pageDiaCode) {
                this.pageDiaCode = true
            } else {
                this.dialCode = params[2]
                localStorage.setItem('dialCode', this.dialCode)
            }
        },

        openNational() {
            this.$refs.controlChild.open()
        },

        getCode() {
            if (this.formData.phone === '') {
                Toast(this.$t('请输入手机号'));
                return
            } else {
                const reg = /^[0-9]+[0-9]*$/
                if (!reg.test(this.formData.phone)) {
                    Toast(this.$t('手机号格式有误'));
                    return;
                }
            }

            Toast.loading({
                duration: 0,
                message: this.$t('发送中'),
                forbidClick: true,
            })

            const params = {
                target: `${this.dialCode} ${this.formData.phone}`
            }

            getIdcode(params).then(() => {
                Toast.success(this.$t('发送成功'))
                this.timerFn()
            }).catch(err => {
                Toast.clear()
                // Toast.fail(err.msg)
            })
        },

        timerFn() {
            this.codeBtnTxt = `${this.$t('再次获取')} ${this.count} s`
            this.btnDisabled = true
            this.interval = setInterval(() => {
                if (this.count === 1) {
                    this.count = 60
                    this.codeBtnTxt = this.$t('再次获取')
                    this.btnDisabled = false
                    clearInterval(this.interval)
                } else {
                    this.count -= 1
                    this.codeBtnTxt = `${this.$t('再次获取')} ${this.count} s`
                }
            }, 1000)
        },

        submitVertify() {
            if (this.formData.phone === '') {
                Toast(this.$t('请输入手机号'));
                return
            } else {
                const reg = /^[0-9]+[0-9]*$/
                if (!reg.test(this.formData.phone)) {
                    Toast(this.$t('手机号格式有误'));
                    return;
                }
            }

            if (this.formData.verifcode === '') {
                Toast(this.$t('请输入验证码'));
                return
            }

            this.show = true
        },

        submitHandle() {
            Toast.loading({
                duration: 0,
                message: this.$t('提交中'),
                forbidClick: true,
            })

            const params = {
                ...this.formData,
                phone: `${this.dialCode} ${this.formData.phone}`
            }
            savePhone(params).then(async () => {
                Toast.success(this.$t('绑定成功'))
                await this.$store.dispatch('getUserInfo')
                this.onClickLeft()
            }).catch(err => {
                Toast.clear()
                // Toast.fail(err.msg)
            })
        }
    }
}
</script>

<style lang="scss" scoped>
.page-content {
    * {
        box-sizing: border-box;
    }

    /deep/ .el-input {
        input:focus {
            border-color: var(--main-color) !important;
        }
    }

    .form-content {
        padding: 0 15px;

        .form-item {
            >.title {
                font-size: 14px;
                line-height: 16px;
                color: #333333;
                margin-top: 25px;
                margin-bottom: 10px;
            }

            >.input-content {
                /deep/ .el-input-group--prepend {
                    .el-input-group__prepend {
                        background-color: transparent !important;
                        color: #000 !important;
                        border-right: none !important;
                        padding: 0 15px !important;

                        .icon {
                            width: 10px;
                            height: auto;
                            position: relative;
                            top: -1px;
                            margin-left: 5px;
                        }
                    }

                    .el-input__inner {
                        border-left-color: #fff;
                    }
                }

                &.code {
                    position: relative;

                    >.btn {
                        padding: 0 20px;
                        height: 40px;
                        position: absolute;
                        right: 0;
                        bottom: 0;
                        font-size: 14px;
                        
                        color: var(--main-color);
                        display: flex;
                        align-items: center;
                        justify-content: center;

                        &.disabled {
                            pointer-events: none;
                            opacity: 0.9;
                        }
                    }
                }
            }
        }

        .submit-btn {
            margin-top: 40px;
            width: 345px;
            height: 44px;
            // background: var(--main-color);
            background: var(--main-color);
            border-radius: 4px;
            font-style: normal;
            font-weight: 400;
            font-size: 16px;
            line-height: 44px;
            text-align: center;
            color: #FFFFFF;
        }
    }
}
</style>
