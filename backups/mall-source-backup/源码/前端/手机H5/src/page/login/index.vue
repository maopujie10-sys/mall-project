<template>
    <div class="login">
        <nationality-list ref="controlChild" :title="$t('选择区域码')" @getName="getName(arguments)"></nationality-list>
        <Vcode :imgs="[img1, img2, img3, img4, img5]" :show="show" @success="onSuccess" :canvasHeight="200" @fail="onFail" :sliderText="$t('拖动滑块以完成拼图')" style="direction: ltr;"
            @close="show = false"  :successText="$t('验证通过!')" :failText="$t('验证失败,请重试')" />

        <div class="lang-right">
            <div class="lang-left" @click="onClickLeft">
                <van-icon name="arrow-left" />
            </div>
            <router-link to="/language" v-if="isShelves">
                <img class="lang-icon" src="@/assets/image/public/feedback.png" />
            </router-link>
        </div>
        <div class="login-title">{{ $t("登录") }}</div>
        <div class="tab">
            <div class="tab-button" :class="TabShow === 2 ? 'tab-button-show2' : 'tab-button-show1'" @click="TabClick(2)">
                {{ $t("手机号") }}
            </div>
            <div class="tab-button" :class="TabShow === 1 ? 'tab-button-show2' : 'tab-button-show1'" @click="TabClick(1)">
                {{ $t("邮箱") }}
            </div>
        </div>
        <div v-if="TabShow === 1" class="account_form">
            <div class="title-input m-t20 m-b10">{{ $t("邮箱") }}</div>
            <div class="login-input">
                <el-input :placeholder="$t('请输入邮箱')" maxlength="64" v-model.trim="it.input1" clearable>
                </el-input>
            </div>
            <div class="title-input m-t20 m-b10">{{ $t("密码") }}</div>
            <div class="login-input">
                <el-input :placeholder="$t('请输入密码')" maxlength="20" v-model.trim="it.input2" show-password clearable>
                </el-input>
            </div>
        </div>
        <div v-if="TabShow === 2" class="phone_form">
            <div class="title-input m-t20 m-b10">{{ $t("手机号") }}</div>
            <div class="login-input">
                <el-input :placeholder="$t('请输入手机号')" maxlength="20" v-model.trim="it.input1" clearable
                    @input="() => it.input1 = it.input1.replace(/[^\d]/g, '')">
                    <div slot="prepend" @click="openNational">
                        <p>
                            +<span>{{ dialCode }}</span>
                            <img :src="triangleDown" alt="" class="icon" />
                        </p>
                    </div>
                </el-input>

                <!-- <el-input
            :placeholder="$t('请输入手机号')"
            maxlength="20"
            v-model="it.input1"
            clearable>
        </el-input> -->
            </div>
            <div class="title-input m-t20 m-b10">{{ $t("密码") }}</div>
            <div class="login-input">
                <el-input :placeholder="$t('请输入密码')" maxlength="20" v-model.trim="it.input2" show-password clearable>
                </el-input>
            </div>
        </div>
        <div class="wangjimima" @click="handleJump">{{ $t("忘记密码？") }}</div>
        <div class="tijiao" @click="post_form">{{ $t("登录") }}</div>
        <div class="zhuce">
            <div class="zhuce-flex"></div>
            <div class="zhuce-text1">{{ $t("还没有账号？") }}</div>
            <router-link to="/register">
                <div class="zhuce-text2">{{ $t("去注册") }}</div>
            </router-link>
            <div class="zhuce-flex"></div>
        </div>
        <div class="servece_box" @click="handleJump" >
            <img src="@/assets/image/me/kefu.png" >
        </div>
    </div>
</template>

<script>
import { Toast, Icon } from "vant";
import Vcode from "vue-puzzle-vcode";
import loginAxios from "@/API/login";
import NationalityList from "@/components/NationalityList";
import { isLogin } from "@/utils/utis";
export default {
    name: "LoginPage",
    data() {
        return {
            isShelves: !process.env.VUE_APP_PUT_ON_SHELVES,
            itemName: process.env.VUE_APP_ITEM_NAME,
            TabShow: 2,
            it: {
                input1: "",
                input2: "",
            },
            show: false,
            img1: require("@/assets/image/slider/1.png"),
            img2: require("@/assets/image/slider/2.png"),
            img3: require("@/assets/image/slider/3.png"),
            img4: require("@/assets/image/slider/4.png"),
            img5: require("@/assets/image/slider/5.png"),
            triangleDown: require("@/assets/image/me/triangle_down.png"),
            pageDiaCode: false,
            dialCode: localStorage.getItem("dialCode") || 1,
        };
    },
    components: {
        [Toast.name]: Toast,
        [Icon.name]: Icon,
        Vcode,
        NationalityList,
    },
    created() {
        if (isLogin() && this.$route.query.from == "ldy") {
            this.$notify(this.$t('您已登录'), 'success')
            this.$router.push({ path: "/" });
        }
    },
    methods: {
        handleJump() {
            const path = this.$store.state.multiItem[process.env.VUE_APP_ITEM_NAME].customer_service
            if (path) {
                
                if(window.plus) {
                } else {
                    window.open(path)
                }
            } else {
                this.$router.push({ path: "customerServiceIndex?path=customerService" });
            }
            // var url = 'https://ld.ebvsjbv.site/chat/#/customerServiceH5?lang='+this.$i18n.locale
            // if (localStorage.getItem('token')){
            //   url+='&token='+localStorage.getItem('token')
            // }
            // window.location.href=url
            
        },
        // gotoForget() {
        //     this.$router.push({ path: "forgetPassword" });
        // },
        TabClick(e) {
            this.it = {
                input1: "",
                input2: "",
            };
            this.TabShow = e;
        },
        post_form() {
            const t = this;
            if (this.TabShow === 1) {
                if (this.it.input1 === "") {
                    Toast(t.$t("请输入邮箱"));
                    return;
                } else {
                    const reg =
                        /^([A-Za-z0-9_\-\.\w{3,}])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
                    if (!reg.test(this.it.input1)) {
                        Toast(t.$t("邮箱格式有误"));
                        return;
                    }
                }
            }
            if (this.TabShow === 2) {
                if (this.it.input1 === "") {
                    Toast(t.$t("请输入手机号"));
                    return;
                } else {
                    const reg = /^[0-9]+[0-9]*$/;
                    if (!reg.test(this.it.input1)) {
                        Toast(t.$t("手机号格式有误"));
                        return;
                    }
                }
            }

            if (this.it.input2 === "") {
                Toast(t.$t("请输入密码"));
                return;
            }
            if(this.itemName == 'Hive') {
                this.loginSubmit();
            } else {
                this.show = true;
            }
        },
        onSuccess() {
            this.loginSubmit();
            this.show = false;
        },
        onFail() {
            console.log("失败回调");
        },
        loginSubmit() {
            const params = {
                password: encodeURIComponent(this.it.input2)?.trim(),
            };

            params.username =
                this.TabShow === 1
                    ? this.it.input1?.trim()
                    : `${this.dialCode} ${this.it.input1?.trim()}`;

            Toast.loading({
                duration: 0,
                message: this.$t("提交中"),
                forbidClick: true,
            });

            loginAxios
                .zhanghaodenglu(params)
                .then(async (res) => {
                    Toast.clear()
                    // Toast.success(this.$t("登录成功"));
                    this.$notify(this.$t("登录成功"), 'success')
                    localStorage.setItem("token", res.token);
                    let timeZone = this.dayjs.tz.guess();
                    localStorage.setItem("timeZone", timeZone);
                    await this.$store.dispatch("getUserInfo");
                    if(this.$route.query.from == "ldy"){
                        this.$router.push({ path: '/' });
                        return
                    }
                   
                    try {
                        if ('/register' == sessionStorage.getItem('upperLevel')) {
                            this.$router.push({ path: "/" });
                        } else {
                            this.$router.go(-1)
                        }
                    } catch (error) {
                        this.$router.push({ path: "/" });
                    }

                })
                .catch((err) => {
                    Toast.clear()
                });
        },
        getName(params) {
            if (!this.pageDiaCode) {
                this.pageDiaCode = true;
            } else {
                this.dialCode = params[2];
                localStorage.setItem("dialCode", this.dialCode);
            }
        },
        openNational() {
            this.$refs.controlChild.open();
        },
        onClickLeft() {
            this.$router.push('/')
        },
    },

};
</script>

<style lang="scss" scoped>
.login {
    width: 100%;
    height: 100%;
    padding: 0 15px;
    box-sizing: border-box;

    /deep/ .el-input {
        input:focus {
            border-color: var(--main-color) !important;
        }
    }

    .wrapper {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
    }

    // .block {
    //   //width: 120px;
    //   //height: 120px;
    //   //background-color: #fff;
    // }

    .lang-right {
        width: 100%;
        display: flex;
        justify-content: space-between;
        align-items: center;

        .lang-icon {
            padding: 12px 0 12px 10px;
            width: 20px;
            height: 20px;
        }

        .lang-left {
            font-size: 25px;
            color: #333;
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
            padding: 0 10px;
            min-width: 64px;
            min-height: 34px;
            text-align: center;
            margin-right: 10px;
            line-height: 34px;
        }

        .tab-button-show1 {
            background: #eeeeee;
            font-style: normal;
            font-weight: 400;
            font-size: 12px;
            //line-height: 14px;
            /* identical to box height, or 117% */
            color: #333333;
        }

        .tab-button-show2 {
            background: var(--main-color);
            font-style: normal;
            font-weight: 400;
            font-size: 12px;
            //line-height: 12px;
            /* identical to box height, or 100% */
            color: #ffffff;
        }
    }

    .title-input {
        font-style: normal;
        font-weight: 400;
        font-size: 14px;
        line-height: 16px;
        color: #333333;
        white-space: nowrap;
    }

    .wangjimima {
        font-style: normal;
        font-weight: 400;
        font-size: 12px;
        line-height: 14px;
        /* identical to box height */
        color: #1d91ff;
        margin-top: 10px;
    }

    .tijiao {
        margin-top: 20px;
        width: 345px;
        height: 44px;
        background: var(--main-color);
        border-radius: 4px;
        font-style: normal;
        font-weight: 400;
        font-size: 16px;
        line-height: 44px;
        /* identical to box height, or 100% */

        text-align: center;

        color: #ffffff;
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
        color: #4aa8ff;
    }

    // .login-input {
    //   //height: 44px;
    // }
    .kefu-icon {
        position: fixed;
        width: 50px;
        height: 50px;
        right: 28px;
        bottom: 32px;
    }

    .phone_form {
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
    }
}
</style>
