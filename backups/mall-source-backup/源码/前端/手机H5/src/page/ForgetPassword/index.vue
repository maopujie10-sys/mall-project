<template>
    <div class="login">
        <nationality-list ref='controlChild' :title="$t('选择区域码')" @getName="getName(arguments)"></nationality-list>
        <Vcode style="direction: ltr;" :imgs="[img1, img2, img3, img4, img5]" :show="show" @success="onSuccess" :canvasHeight="200" @fail="onFail"
            @close="show = false;" :sliderText="$t('拖动滑块以完成拼图')" :successText="$t('验证通过!')" :failText="$t('验证失败,请重试')" />

        <div class="lang-right">
            <router-link to="/language">
                <img class="lang-icon" src="@/assets/image/public/feedback.png" />
            </router-link>
        </div>
        <div class="login-title">{{ $t('忘记密码') }}</div>

        <div class="tab">
            <div class="tab-button" :class=" TabShow === 1 ? 'tab-button-show2' : 'tab-button-show1' " @click=" TabClick(1) ">{{
                $t('手机号') }}</div>
            <div class="tab-button" :class=" TabShow === 2 ? 'tab-button-show2' : 'tab-button-show1' " @click=" TabClick(2) ">{{
                $t('邮箱') }}</div>
        </div>

        <div lass="phone_form">
            <div class="title-input m-t20 m-b10">{{ TabShow === 1 ? $t('手机号') : $t('邮箱') }}</div>
            <div v-if=" TabShow === 1 " class="login-input">
                <el-input :placeholder=" $t('请输入手机号') " maxlength="20" v-model=" formData.username " clearable>
                    <div slot="prepend" @click=" openNational ">
                        <p>+ <span>{{ dialCode }}</span></p>
                    </div>
                </el-input>
            </div>
            <div v-if=" TabShow === 2 " class="login-input">
                <el-input :placeholder=" $t('请输入邮箱') " maxlength="60" v-model=" formData.username " clearable>
                </el-input>
            </div>
            <div class="title-input m-t20 m-b10">{{ $t('验证码') }}</div>
            <div class="login-input code">
                <el-input :placeholder=" $t('请输入验证码') " maxlength="6" v-model=" formData.verifcode ">
                </el-input>
                <div class="btn" :class=" { 'disabled': btnDisabled } " @click=" getCode ">{{ codeBtnTxt }}</div>
            </div>
            <div class="title-input m-t20 m-b10">{{ $t('设置新密码') }}</div>
            <div class="login-input">
                <el-input :placeholder=" $t('请输入 6-12 位由数字或字母组成的密码') " maxlength="20" v-model=" formData.password "
                    show-password clearable>
                </el-input>
            </div>
            <div class="title-input m-t20 m-b10">{{ $t('确认新密码') }}</div>
            <div class="login-input">
                <el-input :placeholder=" $t('请再次输入密码') " maxlength="20" v-model=" formData.confirm_password " show-password
                    clearable>
                </el-input>
            </div>
        </div>
        <div class="tijiao" @click=" post_form ">{{ $t('提交') }}</div>
        <div class="zhuce">
            <div class="zhuce-flex"></div>
            <div class="zhuce-text1">{{ $t('想起密码？') }} </div>
            <router-link to="/login">
                <div class="zhuce-text2">{{ $t('去登录') }}</div>
            </router-link>
            <div class="zhuce-flex"></div>
        </div>

        <!-- <img @click=" tiaozhuan " src="@/assets/image/AppDownload/homeTool1.png" class="kefu-icon" /> -->
    </div>
</template>

<script>
import { Toast } from "vant";
import Vcode from "vue-puzzle-vcode";
import NationalityList from '@/components/NationalityList'
import {
    getIdcode,
    updatePwdByVerify
} from '@/API/common'
export default {
    name: 'ForgetPassword',
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
            formData: {
                username: '',
                password: '',
                confirm_password: '',
                verifcode: ''
            },
            show: false,
            codeBtnTxt: this.$t('收取验证码'),
            count: 60,
            interval: null,
            btnDisabled: false,
            pageDiaCode: false,
            dialCode: localStorage.getItem('dialCode') || 1,
            TabShow: 1
        }
    },
    beforeDestroy() {
        this.interval && clearInterval(this.interval)
    },
    methods: {
        TabClick(e) {
            this.TabShow = e
            this.formData.username = ''
            this.formData.password = ''
            this.formData.confirm_password = ''
            this.formData.verifcode = ''
        },

        tiaozhuan() {
            this.$router.push({ path: 'customerServiceIndex' })
        },

        post_form() {
            if (this.TabShow === 1) {
                if (this.formData.username === '') {
                    Toast(this.$t('请输入手机号'));
                    return
                } else {
                    const reg = /^[0-9]+[0-9]*$/
                    if (!reg.test(this.formData.username)) {
                        Toast(this.$t('手机号格式有误'));
                        return;
                    }
                }
            }

            if (this.TabShow === 2) {
                if (this.formData.username === '') {
                    Toast(this.$t('请输入邮箱'));
                    return
                }
                const reg = /^([A-Za-z0-9_\-\.\w{3,}])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/
                if (!reg.test(this.formData.username)) {
                    Toast(this.$t('邮箱格式有误'));
                    return;
                }
            }


            if (this.formData.verifcode === '') {
                Toast(this.$t('请输入验证码'));
                return
            }

            if (this.formData.password === '') {
                Toast(this.$t('请输入密码'));
                return;
            }

            const reg = /^[a-zA-Z0-9!@#$%^&*()_+{}\[\]:;'"\\|,.<>?~`\-=/]{6,12}$/;
            if (!reg.test(this.formData.password)) {
                Toast(this.$t('请输入 6-12 位由数字或字母组成的密码'));
                return;
            }

            if (this.formData.password !== this.formData.confirm_password) {
                Toast(this.$t('两次密码输入不一致'));
                return;
            }

            this.show = true
        },
        onSuccess() {
            console.log('onSuccess')
            this.submitHandle()
            this.show = false
        },
        onFail() {
            console.log("失败回调");
        },

        submitHandle() {
            const { password, verifcode } = this.formData
            const params = {
                password,
                verifcode,
                verifcode_type: this.TabShow
            }
            params.username = this.TabShow === 1 ? `${this.dialCode}${this.formData.username}` : this.formData.username

            updatePwdByVerify(params).then(res => {
                console.log(res)
            })
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
            if (this.TabShow === 1) {
                if (this.formData.username === '') {
                    Toast(this.$t('请输入手机号'));
                    return
                } else {
                    const reg = /^[0-9]+[0-9]*$/
                    if (!reg.test(this.formData.username)) {
                        Toast(this.$t('手机号格式有误'));
                        return;
                    }
                }
            }

            if (this.TabShow === 2) {
                if (this.formData.username === '') {
                    Toast(this.$t('请输入邮箱'));
                    return
                }
                const reg = /^([A-Za-z0-9_\-\.\w{3,}])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/
                if (!reg.test(this.formData.username)) {
                    Toast(this.$t('邮箱格式有误'));
                    return;
                }
            }

            Toast.loading({
                duration: 0,
                message: this.$t('发送中'),
                forbidClick: true,
            })

            const params = {
                target: this.TabShow === 1 ? `${this.dialCode}${this.formData.username}` : this.formData.username
            }

            getIdcode(params).then(() => {
                Toast.success(this.$t('发送成功'))
                this.timerFn()
            }).catch(err => {
                Toast.clear()
                // (err.msg)
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
        }
    }
}
</script>

<style lang="scss" scoped>
.login {
    width: 100%;
    height: 100%;
    padding: 0 15px;
    box-sizing: border-box;

    /deep/ .el-input {
        input:focus {
            //   border-color: var(--main-color);
            border-color: var(--main-color);
        }
    }

    .wrapper {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
    }

    .lang-right {
        width: 100%;
        display: flex;
        justify-content: end;

        .lang-icon {
            padding: 12px 0 12px 10px;
            width: 20px;
            height: 20px;
        }
    }

    .login-title {
        font-style: normal;
        font-weight: 700;
        font-size: 30px;
        line-height: 35px;

        color: #333333;
        margin-top: 10px;
    }

    .tab {
        margin-top: 30px;
        width: 100%;
        display: flex;
        justify-content: left;

        .tab-button {
            border-radius: 4px;
            //padding: 8px 10px;
            width: 64px;
            height: 34px;
            text-align: center;
            margin-right: 10px;
            line-height: 34px;
        }

        .tab-button-show1 {
            background: #EEEEEE;
            font-style: normal;
            font-weight: 400;
            font-size: 12px;
            //line-height: 14px;
            /* identical to box height, or 117% */
            color: #333333;
        }

        .tab-button-show2 {
            // background: var(--main-color);
            background: var(--main-color);
            font-style: normal;
            font-weight: 400;
            font-size: 12px;
            //line-height: 12px;
            /* identical to box height, or 100% */
            color: #FFFFFF;
        }
    }

    .title-input {
        font-style: normal;
        font-weight: 400;
        font-size: 14px;
        line-height: 16px;
        color: #333333;
    }

    .wangjimima {
        font-style: normal;
        font-weight: 400;
        font-size: 12px;
        line-height: 14px;
        /* identical to box height */
        color: #1D91FF;
        margin-top: 10px;
    }

    .tijiao {
        margin-top: 20px;
        width: 345px;
        height: 44px;
        // background: var(--main-color);
        background: var(--main-color);
        border-radius: 4px;
        font-style: normal;
        font-weight: 400;
        font-size: 16px;
        line-height: 44px;
        /* identical to box height, or 100% */

        text-align: center;

        color: #FFFFFF;
    }

    .zhuce {
        margin-top: 16px;
        width: 100%;
        display: flex;
        justify-content: center;
    }

    .zhuce-flex {
        flex: 1;
    }

    .zhuce-text1 {
        font-style: normal;
        font-weight: 400;
        font-size: 14px;
        line-height: 16px;

        color: #333333;

    }

    .zhuce-text2 {
        font-style: normal;
        font-weight: 400;
        font-size: 14px;
        line-height: 16px;
        color: #4AA8FF;
    }

    .kefu-icon {
        position: fixed;
        width: 50px;
        height: 50px;
        right: 28px;
        bottom: 32px;
    }
}

.phone_form {
    /deep/ .el-input-group__prepend {
        background-color: #eee !important;
        color: #000 !important;
    }
}

.login-input {
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
</style>
