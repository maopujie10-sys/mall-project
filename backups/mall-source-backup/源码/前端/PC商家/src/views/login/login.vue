<template>
  <div class="login" :style="loginBg">
    <div class="login-content">
      <div class="login-logo">
        <img :src="logo" alt="" style="height: 100%;"/>
      </div>
      <!--      <div class="shop-name">Argos shop</div>-->
      <div class="shop-text">{{ $t('登录到您的帐户') }}</div>
      <div class="login-container">
        <div class="login-tab">
          <div :class="current===0?'login-tab-item active':'login-tab-item'" @click="handleChange(0)">{{
              $t('邮箱')
            }}
          </div>
          <div :class="current===1?'login-tab-item active':'login-tab-item'" @click="handleChange(1)">{{
              $t('手机号')
            }}
          </div>
        </div>
        <div class="login-input-content">
          <el-form ref="loginForm" :model="loginForm" autocomplete="on" class="login-form" label-position="left">
            <div class="login-input" v-if="current===0">
              <el-form-item prop="username">
                <img :src="require('@/assets/images/login/account.png')" alt="" class="input-icon"/>
                <el-input
                    :placeholder="$t('请输入邮箱')"
                    maxlength="64"
                    id="username"
                    v-model="loginForm.username"
                    ref="username"
                    clearable>
                </el-input>
              </el-form-item>
            </div>
            <div class="login-input" v-else>
              <el-form-item prop="phone">
                <img :src="require('@/assets/images/login/phone2.png')" alt="" class="input-icon"/>
                <el-dropdown class="input-dropdown" placement="bottom" trigger="click" @command="handleCommand"
                             style="cursor: pointer">
                          <span class="el-dropdown-link" placement="bottom-start">
                            +{{ loginForm.religionCode }}<i class="ml-10 el-icon-caret-bottom"></i>
                          </span>
                  <el-dropdown-menu slot="dropdown" class="project-dropdown">
                    <div style="padding: 0 12px;box-sizing: border-box;">
                      <el-input v-model="searchCountry" suffix-icon="el-icon-search" class="icon-search"
                                @input="searchCountryList"></el-input>
                    </div>
                    <el-dropdown-item v-for="(item,index) in countryList" :key="index" :command='item.code'>
                      {{ $t(item.zh) }}(+{{ item.code }})
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </el-dropdown>
                <el-input
                    class="phone-input"
                    :placeholder="$t('请输入手机号')"
                    maxlength="60"
                    ref="username"
                    v-model="loginForm.phone"
                    id="phone"
                    clearable>
                </el-input>
              </el-form-item>
            </div>
            <div class="login-input password">
              <el-form-item prop="password">
                <img :src="require('@/assets/images/login/password.png')" alt="" class="input-icon"/>
                <el-tooltip v-model="capsTooltip" content="Caps lock is On" manual placement="right">
                  <PasswordInput ref="password" v-model="loginForm.password"
                                 :type="passwordType" autocomplete="on" name="password"
                                 :placeholder="$t('请输入你的密码')" @clear="clearPassword"
                                 tabindex="2" @keyup.native="checkCapslock" @blur="capsTooltip = false"
                                 @keyup.enter.native="onLogin"/>
                </el-tooltip>
              </el-form-item>
            </div>
            <div
                style="height: 24px;margin-bottom:12px;display: flex;justify-content: space-between;align-items: center;">
              <div style="margin-right: 24px;font-size: 14px" v-if="!setting.hideLoginProtocol">
                <!--      用户协议、服务条款、商家规则          -->
                <el-checkbox v-model="loginForm.agree" label="1" style="font-size: 12px;color: #999999;">
                  {{ $t('我已阅读并同意') }}
                </el-checkbox>
                <span style="color: #409EFF;cursor: pointer" @click="protocolVisible=true">{{ $t('商家规则') }}</span>
              </div>
              <div></div>
              <el-popover
                  trigger="click"
                  :content="$t('忘记密码？请联系客服。')">
                <el-button slot="reference" type="text">{{ $t('忘记密码') }}</el-button>
              </el-popover>
            </div>
            <el-button style="margin: auto" :disabled="!loginForm.agree&&!setting.hideLoginProtocol" type="primary"
                       class="login-button" :loading="loading" @click.native.prevent="onLogin">
              {{ $t('登录') }}
            </el-button>
          </el-form>
        </div>
      </div>
    </div>
    <Vcode :imgs="imgs" :show="isShowVerification" @close="onClose" @success="onSuccess"
           :sliderText="$t('拖动滑块完成拼图')" style="direction: ltr;"
           :failText="$t('验证失败，请重试')" :successText="$t('验证成功')"/>
    <Globalization style="position: fixed;right: 24px;top: 24px"/>
    <Customer/>
    <el-image :src="loginBg" style="position: fixed;left: 0;top: 0;z-index: -1;height: 100%;width: 100%;" fit="cover"/>
    <Protocol @closeProtocol="closeProtocol" v-if="protocolVisible"/>
  </div>
</template>

<script>
import PasswordInput from "@/components/PasswordInput";
import Vcode from '@/components/Vcode'
import img_1 from '@/assets/images/login/01.png'
import img_2 from '@/assets/images/login/02.png'
import img_3 from '@/assets/images/login/03.png'
import img_4 from '@/assets/images/login/04.png'
import img_5 from '@/assets/images/login/05.png'
import {validEmail} from '@/utils/validate'
import SocialSign from './components/SocialSignin'
import {login2, loginFree} from "@/api/user";
import {setToken} from '@/utils/auth'
import {mapGetters} from "vuex";
import {i18n} from "@/lang";
import country from "@/utils/country";
import Globalization from "@/components/Globalization";
import Customer from "@/components/Customer/index.vue";
import bg from '@/assets/images/login/login-bg.jpg'
import hiveBg from '@/assets/images/login/hive-bg.png'
import justShopBg from '@/assets/images/login/just-shop-bg.png'
import wholesaleBg from '@/assets/images/login/wholesale-bg.jpg'
import Protocol from "@/views/login/protocol.vue";

const setting = require("@/settings");

export default {
  name: 'Login',
  components: {Customer, SocialSign, Vcode, Globalization, PasswordInput, Protocol},
  computed: {
    ...mapGetters(["currentLanguage"])
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
      logo: require('@/assets/images/login/logo.png'),
      setting,
      // regionList: [86, 852, 63, 992],
      // regionCode: 86,
      current: 0,
      imgs: [img_1, img_2, img_3, img_4, img_5],
      isShowVerification: false,
      loginMethod: 'email',
      loginForm: {
        username: '', // email
        password: '',
        phone: '',
        agree: false,
        religionCode: setting.countryCode
      },
      loginRules: {
        username: [{required: true, trigger: 'blur', validator: validateUsername}],
        phone: [{required: true, trigger: 'blur', validator: validateUsername}],
        password: [{required: true, trigger: 'blur', validator: validatePassword}],
      },
      protocolVisible: false,
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
      loginBg: bg,
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
  created() {
    switch (setting.projectTitle) {
      case "FamilyShop":
        this.loginBg = hiveBg
        break;
      case "JustShop":
        this.loginBg = justShopBg
        break;
      case "Hive":
        this.loginBg = hiveBg
        break;
      case "Wholesale":
        this.loginBg = wholesaleBg
        break;
      default:
        this.loginBg = bg
        break;
    }
  },
  mounted() {
    if (this.$route.query.token) {
      this.loginFree(this.$route.query.token)
      return
    }
    if (this.loginForm.username === '') {
      this.$refs.username.focus()
    } else if (this.loginForm.password === '') {
      this.$refs.password.focus()
    }
    this.loginForm.religionCode = parseInt(localStorage.getItem('religionCode') || setting.countryCode)

    this.countryList.sort((a, b) => {
      return this.$t(a.zh).localeCompare(this.$t(b.zh), i18n.locale)
    })
    this.$store.commit('chat/DELETE_CHAT_INTERVAL')
    this.$store.commit('chat/DELETE_MASSAGE_INTERVAL')
    window.addEventListener("keydown", (e) => {
      if (e.keyCode === 9) {
        let activeEl = document.activeElement;
        if (activeEl.id === 'username' || activeEl.id === "phone") {
          this.$refs.password.focus()
        }
      }
    });
  },
  destroyed() {
    // window.removeEventListener('storage', this.afterQRScan)
  },
  methods: {
    closeProtocol() {
      this.protocolVisible = false
    },
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
      this.loginForm.password = ''
    },
    onLogin() {
      if (['HIVE'].includes(setting.projectTitle)) {
        this.handleLogin()
      } else {
        if (!this.loginForm.agree && !this.setting.hideLoginProtocol) {
          this.$message.error(this.$t('请先同意商家规则'))
          return
        }
        this.isShowVerification = true
      }
    },
    onSuccess(msg) {
      // this.isShow = false; // 通过验证后，需要手动关闭模态框
      this.handleLogin()
    },
    onClose() {
      console.log(22)
      this.isShowVerification = false
    },
    clearPassword(value) {
      this.loginForm.password = value
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
      this.isShowVerification = false
      if (this.loading) {
        return
      }
      if (this.current === 0 && this.loginForm.username === '') {
        this.$message.error(this.$t('请输入邮箱'))
        return
      }
      if (this.current === 1 && this.loginForm.phone === '') {
        this.$message.error(this.$t('请输入手机号'))
        return
      }
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
              username: t.loginForm.religionCode + ' ' + t.loginForm.phone
            }
          }
          login2(loginForm).then((e) => {
            console.log(e.data.token)
            setToken(e.data.token)
            let redirect = this.$route.query.redirect
            if (redirect) {
              this.$router.push({path: redirect, query: t.otherQuery})
            } else {
              t.$router.push({path: '/', query: t.otherQuery})
            }
            t.loading = false
            t.isShowVerification = false
          }).catch((e) => {
            t.loading = false
            t.isShowVerification = false
            console.log('错误', e)
          })
        } else {
          console.log('error submit!!')
          return false
        }
      })
    },
    loginFree(token) {
      loginFree({token}).then((e) => {
        setToken(e.data.token)
        let redirect = this.$route.query.redirect
        if (redirect) {
          this.$router.push({path: redirect, query: this.otherQuery})
        } else {
          this.$router.push({path: '/', query: this.otherQuery})
        }
      }).catch((e) => {
        console.log('错误', e)
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

<style scoped lang="scss">
.phone-input {
  ::v-deep {
    .el-input__inner {
      text-indent: 95px;
    }
  }
}

::v-deep {
  .el-dropdown {
    color: #FFFFFF;
  }

  .el-input__inner {
    text-indent: 24px;
  }

  .icon-search .el-input__inner {
    text-indent: 0px;
  }
}

.login {
  width: 100%;
  height: 100%;
  padding: 0;
  margin: auto;
  display: flex;
  justify-content: center;
  align-items: center;

  ::v-deep {
    .el-textarea__inner, .el-input__inner {
      background: transparent !important;
      color: #FFFFFF;
      height: 50px;
    }
  }

  .login-content {
    height: 586px;
    width: 550px;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;

    .login-logo {
      width: auto;
      height: 136px;

      .el-image {
        width: 100%;
        height: 100%;
      }
    }

    .shop-name {
      font-family: 'Roboto';
      font-style: normal;
      height: 30px;
      line-height: 30px;
      font-weight: 600;
      font-size: 30px;
      color: #FFFFFF;
      margin: 12px;
    }

    .shop-text {
      font-family: 'Roboto';
      font-style: normal;
      font-weight: 400;
      font-size: 24px;
      line-height: 28px;
      text-align: center;
      color: #C4C4C4;
      margin-top: 30px;
    }

    .login-container {
      .login-tab {
        display: flex;
        justify-content: center;
        align-items: center;

        .login-tab-item {

          text-align: center;
          margin: 24px 65px;
          font-family: 'Roboto';
          font-style: normal;
          font-weight: 400;
          font-size: 14px;
          line-height: 16px;
          color: #FFFFFF;
          cursor: pointer;
          padding: 0 12px;

          &.active {
            color: #3E73FF;
            position: relative;

            &::after {
              position: absolute;
              content: '';
              background-color: #3E73FF;
              width: 100%;
              height: 2px;
              left: 0;
              bottom: -10px;
            }
          }
        }
      }

      .login-input-content {
        position: relative;

        .login-input {
          margin-bottom: 24px;
          position: relative;


          .input-icon {
            position: absolute;
            left: 12px;
            z-index: 10;
            top: 50%;
            transform: translateY(-50%);
            width: 20px;
            height: 20px;
          }

          &.password {
            position: relative;


          }
        }

        .input-dropdown {
          position: absolute;
          left: 30px;
          z-index: 10;
          top: 50%;
          transform: translateY(-50%);
          width: 80px;
          height: 20px;
          display: flex;
          justify-content: center;
          align-items: center;
        }

        .login-button {
          width: 100%;
          margin-bottom: 24px;
          height: 50px;
        }
      }
    }
  }
}

.project-dropdown {
  //设置高度才能显示出滚动条 !important
  height: 200px;
  overflow: auto;
  width: 378px;
  transform: translate(119px, 2px);
}

.rtl .project-dropdown {
  transform: translate(-119px, 2px);
}
</style>
