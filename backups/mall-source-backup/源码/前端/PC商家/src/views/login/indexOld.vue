<template>
  <div class="login-container">
    <Globalization style="position: absolute;top: 48px;right: 48px;z-index: 999;"/>
    <div class="relative z-10" style="height: 100vh">
      <el-row class="h-full">
        <el-col :lg="8" class="relative h-full bg-white">
          <div class="absolute" style="width:69%;top:50%;left:50%;transform: translate(-50%,-50%)">
            <div class="text-center">
              <div>
                <img :src="require('@/assets/images/login/logo.png')" alt="" class="w-130"/>
                <h1 class="mt-26 mb-40 font-36">{{ projectTitle }}</h1>
                <p class="mb-50 font-24" style="color: #666">{{ $t('欢迎客商光临') }}</p>
              </div>
            </div>
            <div class="mb-50 flex font-14 w-full justify-around px-60" style="color: #999999">
              <div :class="{'active': current === 0}" class="text-center pointer w-100 h-36" style="line-height: 36px"
                   @click="handleChange(0)">{{ $t('邮箱') }}
              </div>
              <div :class="{'active': current === 1}" class="text-center pointer w-100 h-36" style="line-height: 36px"
                   @click="handleChange(1)">{{ $t('手机') }}
              </div>
            </div>
            <el-form ref="loginForm" :model="loginForm" autocomplete="on" class="login-form" label-position="left">
              <!--        <template v-if="loginMethod === 'email'">-->

              <el-form-item v-if="current === 0" prop="username">
                <div class="relative w-full">
                  <img :src="require('@/assets/images/login/account.png')" alt="" class="input-icon"/>
                  <el-input ref="username" v-model="loginForm.username" :placeholder="$t('请输入你的邮箱')"
                            autocomplete="on" name="username" tabindex="1" type="text">
                  </el-input>
                </div>
              </el-form-item>

              <el-form-item v-if="current === 1" prop="phone">
                <div class="relative w-full">
                  <img :src="require('@/assets/images/login/phone2.png')" alt="" class="input-icon"/>
                  <el-dropdown class="input-icon2" placement="bottom" trigger="click" @command="handleCommand">
                          <span class="el-dropdown-link">
                            {{ loginForm.religionCode }}<i class="ml-10 el-icon-caret-bottom"></i>
                          </span>
                    <el-dropdown-menu slot="dropdown" class="project-dropdown">
                      <div style="padding: 0 12px;box-sizing: border-box;">
                        <el-input v-model="searchCountry" suffix-icon="el-icon-search"
                                  @input="searchCountryList"></el-input>
                      </div>
                      <el-dropdown-item v-for="(item,index) in countryList" :key="index" :command='item.code'>
                        {{ $t(item.zh) }}(+{{ item.code }})
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </el-dropdown>
                  <el-input ref="phone" v-model="loginForm.phone" :placeholder="$t('请输入你的手机号')"
                            autocomplete="on" class="phone-input" name="phone" tabindex="1" type="text">
                  </el-input>
                </div>
              </el-form-item>

              <el-tooltip v-model="capsTooltip" content="Caps lock is On" manual placement="right">
                <el-form-item prop="password">
                  <div class="relative w-full">
                    <img :src="require('@/assets/images/login/password.png')" alt="" class="input-icon"/>
                    <!--                    <el-input :placeholder="$t('请输入你的密码')" class="w-full" :key="passwordType" ref="password"-->
                    <!--                              v-model="loginForm.password" :type="passwordType" name="password" tabindex="2"-->
                    <!--                              autocomplete="on" @keyup.native="checkCapslock" @blur="capsTooltip = false"-->
                    <!--                              @keyup.enter.native="handleLogin"  show-password></el-input>-->
                    <PasswordInput :key="passwordType" ref="password" v-model="loginForm.password"
                                   :type="passwordType" autocomplete="on" name="password"
                                   :placeholder="$t('请输入你的密码')"
                                   tabindex="2" @blur="capsTooltip = false" @keyup.native="checkCapslock"
                                   @keyup.enter.native="handleLogin"/>
                  </div>
                </el-form-item>
              </el-tooltip>
              <el-button :loading="loading" class="w-full h-50" style="background: #1552F0;border-color: #1552F0;"
                         type="primary" @click.native.prevent="onLogin">
                {{ $t('登录') }}
              </el-button>
            </el-form>
          </div>
        </el-col>
        <!--        -->
        <el-col :lg="16" class="h-full">
          <el-carousel height="100vh" style="background: #F4F6FB;" trigger="click">
            <el-carousel-item>
              <div class="flex justify-center align-center w-full h-full">
                <img :src="require('@/assets/images/login/Group (1).png')" alt="" class="carousel-img"/>
              </div>
            </el-carousel-item>
            <el-carousel-item>
              <div class="flex justify-center align-center w-full h-full">
                <img :src="require('@/assets/images/login/Group.png')" alt="" class="carousel-img"/>
              </div>
            </el-carousel-item>
            <el-carousel-item>
              <div class="flex justify-center align-center w-full h-full">
                <img :src="require('@/assets/images/login/Group 3113.png')" alt="" class="carousel-img"/>
              </div>
            </el-carousel-item>
          </el-carousel>
        </el-col>
      </el-row>
    </div>
    <Vcode :imgs="[img]" :show="isShowVerification" @close="onClose" @success="onSuccess"
           :sliderText="$t('拖动滑块完成拼图')"
           :failText="$t('验证失败，请重试')" :successText="$t('验证成功')"/>
  </div>
</template>

<script>
import img from '@/assets/images/login/Rectangle 1174.png'
import {validEmail} from '@/utils/validate'
import SocialSign from './components/SocialSignin'
import Vcode from '@/components/Vcode'
import {login2} from "@/api/user";
import {setToken} from '@/utils/auth'
import {mapGetters} from "vuex";
import {i18n} from "@/lang";
import country from "@/utils/country";
import Globalization from "@/components/Globalization";
import PasswordInput from "@/components/PasswordInput";
import {projectTitle} from "@/settings";

export default {
  name: 'Login',
  components: {SocialSign, Vcode, Globalization, PasswordInput},
  computed: {
    ...mapGetters(["currentLanguage"]),
  },
  data() {
    const re = /^[0-9]+.?[0-9]*/;//判断字符串是否为数字//判断正整数/[1−9]+[0−9]∗]∗/
    const validateUsername = (rule, value, callback) => {
      console.log('rule', rule, value)
      if (this.current === 0 && !validEmail(value)) {
        console.log(123)
        callback(new Error('Please enter the correct email'))
      } else if (this.current === 1 && !re.test(value / 1) || value.length < 8) {
        console.log(456)
        callback(new Error('Please enter the correct phone'))
      } else {
        callback()
      }
    }

    const validatePassword = (rule, value, callback) => {
      if (value.length < 6) {
        callback(new Error('The password can not be less than 6 digits'))
      } else {
        callback()
      }
    }
    return {
      projectTitle,
      regionList: [86, 852, 63, 992],
      regionCode: 86,
      current: 0,
      img,
      isShowVerification: false,
      loginMethod: 'email',
      loginForm: {
        username: '', // email
        password: '',
        phone: '',
        religionCode: '86'
      },
      loginRules: {
        username: [{required: true, trigger: 'blur', validator: validateUsername}],
        phone: [{required: true, trigger: 'blur', validator: validateUsername}],
        password: [{required: true, trigger: 'blur', validator: validatePassword}],
      },
      passwordType: 'password',
      capsTooltip: false,
      loading: false,
      showDialog: false,
      redirect: undefined,
      otherQuery: {},
      countryList: country,
      activeAddress: '',
      isCanLogin: false,
      userVisible: false,
      kyc_get: {},
      searchCountry: '',
      userProcess: 0,
      countryName: this.$t("请选择国家"),
      countryCode: '',
      languages: [
        {
          name: 'English',
          value: 'en'
        },
        // {
        //   name: '한국어',
        //   value: 'ko'
        // },
        {
          name: `${'简体中文'}`,
          value: 'zh-CN'
        },
        {
          name: `${'繁體中文'}`,
          value: 'zh-TW'
        }
      ],
    };
  },
  watch: {
    currentLanguage: {
      immediate: true,
      deep: false,
      handler(val) {
        this.changeLang(val)
      }
    },
    $route: {
      handler: function (route) {
        const query = route.query
        if (query) {
          this.redirect = query.redirect
          this.otherQuery = this.getOtherQuery(query)
        }
      },
      immediate: true
    },
    loginForm: {
      handler() {
        const res = Object.keys(this.loginForm).filter(key => {
          return this.loginForm[key] === ''
        })
        this.isCanLogin = res.length === 0
      },
      immediate: true,
      deep: true
    }
  },
  mounted() {
    if (this.loginForm.username === '') {
      this.$refs.username.focus()
    } else if (this.loginForm.password === '') {
      this.$refs.password.focus()
    }
    this.loginForm.religionCode = parseInt(localStorage.getItem('religionCode') || '86')

    this.countryList.sort((a, b) => {
      return this.$t(a.zh).localeCompare(this.$t(b.zh), i18n.locale)
    })
    this.$store.commit('chat/DELETE_CHAT_INTERVAL')
    this.$store.commit('chat/DELETE_MASSAGE_INTERVAL')
  },
  destroyed() {
    // window.removeEventListener('storage', this.afterQRScan)
  },
  methods: {
    searchCountryList() {
      this.countryList = country.filter(item => {
        return item.zh.indexOf(this.searchCountry) > -1 || item.en.toUpperCase().indexOf(this.searchCountry.toUpperCase()) > -1 || item.code.indexOf(this.searchCountry) > -1 || item.tw.indexOf(this.searchCountry) > -1 || item.ko.indexOf(this.searchCountry) > -1
      })
    },
    changeLang(val) {
      let lang = ''
      switch (val) {
        case 'en':
          this.langImg = this.en;
          lang = 'en'
          break;
        case 'ko':
          this.langImg = this.ko;
          lang = 'ko'
          break;
        case 'zh-CN':
          this.langImg = this.zhCN;
          lang = 'cn'
          break;
        case 'zh-TW':
          this.langImg = this.zhTW;
          lang = 'tw'
          break;
      }
      this.languageName = (this.languages.find(item => item.value === val) || {name: 'English'}).name
      i18n.locale = lang;
      //刷新页面
    },
    // 打开国家列表底部弹窗
    openBtn() {
      if (!this.disabled2()) {
        this.$refs.controlChild.open()
      }
    },
    disabled2() { // 是否禁用按钮
      return ![0, 3, ''].includes(this.status)
    },
    // 获取到当前选中国家的code值
    getName(params) {
      console.log(params)
      this.countryName = params[0];
      this.countryCode = params[1];
    },
    handleCommand(val) {
      console.log(val)
      this.loginForm.religionCode = val
      localStorage.setItem('religionCode', val)
    },
    handleChange(index) {
      this.current = index
      this.loginForm.username = ''
      this.loginForm.phone = ''
    },
    onLogin() {
      this.isShowVerification = true
    },
    onSuccess(msg) {
      // this.isShow = false; // 通过验证后，需要手动关闭模态框
      this.handleLogin()
    },

    onClose() {
      console.log(22)
      this.isShowVerification = false
    },
    checkCapslock(e) {
      const {key} = e
      this.capsTooltip = key && key.length === 1 && (key >= 'A' && key <= 'Z')
    },
    showPwd() {
      if (this.passwordType === 'password') {
        this.passwordType = ''
      } else {
        this.passwordType = 'password'
      }
      this.$nextTick(() => {
        this.$refs.password.focus()
      })
    },
    handleLogin() {
      const t = this
      this.$refs.loginForm.validate(valid => {
        if (valid) {
          t.loading = true
          let loginForm = {}
          if (t.current === 0) {
            loginForm = {
              password: t.loginForm.password,
              username: t.loginForm.username
            }
          } else if (t.current === 1) {
            loginForm = {
              password: t.loginForm.password,
              username: t.loginForm.religionCode + t.loginForm.phone
            }
          }
          login2(loginForm).then((e) => {
            console.log(e.data.token)
            setToken(e.data.token)
            this.$router.push({path: '/', query: this.otherQuery})
            this.loading = false
            this.isShowVerification = false
          }).catch((e) => {
            this.loading = false
            this.isShowVerification = false
            console.log('错误', e)
          })
        } else {
          console.log('error submit!!')
          return false
        }
      })
    },
    getOtherQuery(query) {
      return Object.keys(query).reduce((acc, cur) => {
        if (cur !== 'redirect') {
          acc[cur] = query[cur]
        }
        return acc
      }, {})
    },
    handleLoginMethod(method) {
      this.loginMethod = method
      this.loginForm.username = ''
      this.loginForm.password = ''
    }
  }
}
</script>

<style lang="scss">
/* 修复input 背景不协调 和光标变色 */
/* Detail see https://github.com/PanJiaChen/vue-element-admin/pull/927 */

$bg: #283443;
$light_gray: #fff;
$cursor: #fff;

@supports (-webkit-mask: none) and (not (cater-color: $cursor)) {
  .login-container .el-input input {
    color: #333;
  }
}

/* reset element-ui css */
.login-container {

  .el-input {
    //display: inline-block;
    height: 50px;

    input {
      -webkit-appearance: none;
      padding: 12px 5px 12px 42px;
      //color: $light_gray;
      height: 50px;
      //caret-color: $cursor;
      color: #333;

      &:-webkit-autofill {
        box-shadow: 0 0 0px 1000px #ffffff inset !important;
        //-webkit-text-fill-color: $cursor !important;
      }
    }
  }

  .el-form-item {
    border-radius: 5px;
    color: #454545;
  }
}
</style>

<style lang="scss" scoped>
$bg: #2d3a4b;
$dark_gray: #889aa4;
$light_gray: #eee;

.active {
  color: #1552F0;
  border-bottom: 2px solid #1552F0;
}

::v-deep {
  .el-form-item {
    //background: rgba(0, 0, 0, 0.47);
  }

  .el-form-item__content {
    display: flex;
    align-items: center;
  }

  .el-input input {
    //padding: 12px 5px 12px 20px;
  }

  .el-carousel__indicator {
    .el-carousel__button {
      background: #C2CCDE;
    }


    &.is-active {


      .el-carousel__button {
        background: #1552f0;
      }
    }
  }

}

.login-container {
  position: relative;
  min-height: 100%;
  width: 100%;
  //background-image: url("~@/assets/images/login/Rectangle 1.png");
  background-size: cover;
  //background-color: $bg;

  &:after {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    content: " ";
    background-color: rgba(0, 0, 0, .6);
  }

  .login-form {
    position: relative;
    width: 100%;
  }

  .tips {
    font-size: 14px;
    color: #fff;
    margin-bottom: 10px;

    span {
      &:first-of-type {
        margin-right: 16px;
      }
    }
  }

  .svg-container {
    padding: 6px 5px 6px 15px;
    color: $dark_gray;
    vertical-align: middle;
    width: 30px;
    display: inline-block;
  }

  .title-container {
    position: relative;

    .title {
      font-size: 26px;
      color: $light_gray;
      margin: 0px auto 40px auto;
      text-align: center;
      font-weight: bold;
    }
  }

  .show-pwd {
    position: absolute;
    right: 10px;
    top: 7px;
    font-size: 16px;
    color: #fff;
    cursor: pointer;
    user-select: none;
  }

  .thirdparty-button {
    position: absolute;
    right: 0;
    bottom: 6px;
  }

  @media only screen and (max-width: 470px) {
    .thirdparty-button {
      display: none;
    }
  }
}

.login-method {
  position: relative;
  padding: 10px 16px;

  &.active:after {
    position: absolute;
    left: 0;
    bottom: 0;
    content: " ";
    width: 100%;
    height: 1px;
    background: #fff;
  }
}

.input-icon {
  position: absolute;
  left: 12px;
  z-index: 10;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
}

.input-icon2 {
  position: absolute;
  left: 30px;
  z-index: 10;
  top: 50%;
  transform: translateY(-50%);
  width: 70px;
  height: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}


.phone-input {
  ::v-deep .el-input__inner {
    padding: 12px 5px 12px 90px !important;
  }
}

.carousel-img {
  position: relative;
  top: 8%;
}

@media screen and (min-width: 1398px) {
  .carousel-img {
    width: 800px;
    height: 800px;
  }
}

@media screen and (max-width: 1398px) {
  .carousel-img {
    width: 700px;
    height: 700px;
  }
}

@media screen and (max-width: 798px) {
  .carousel-img {
    width: 600px;
    height: 600px;
  }
}

@media screen and (max-width: 628px) {
  .carousel-img {
    width: 450px;
    height: 450px;
  }
}

.project-dropdown {
  //设置高度才能显示出滚动条 !important
  height: 200px;
  overflow: auto;
}
</style>
