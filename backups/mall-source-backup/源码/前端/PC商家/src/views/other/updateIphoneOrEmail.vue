<template>
  <el-dialog :title="editTitle" :close-on-click-modal="false" :visible="editVisible" width="450px"
             @close="closeDialog" class="updateIphoneOrEmail">
    <div v-if="step===1">
      <div v-if="checkType==='phone'">
        <p v-if="[1,2].includes(this.kycType)" style="margin-bottom: 12px">
          {{ $t('为了保障您的账号安全，请验证后进行下一步操作') }}</p>
        <p class="mb-8 font-12" style="color: #333;margin-top: 24px;">{{ $t('当前手机号') }}</p>
        <p style="display: flex;width: 100%;justify-content: space-between;">
          <span style="font-size: 18px;color: black;padding-right: 24px;">{{ userInfo.phone | formatPhone }}</span>
          <span v-if="userInfo.email"
                style="color: #2C78F8;cursor: pointer;flex: 1;position:relative;text-indent: 24px;text-align: right;"
                @click="changeCheckType('email')">
            <i class="el-icon-sort"
               style="transform: rotate(90deg);text-indent: 0"/>
            {{ $t('切换邮箱接收验证码') }}
          </span>
        </p>
        <div class="flex rounded" style="position: relative;margin-top: 24px;">
          <el-input v-model="beforeCode" :placeholder="$t('请输入验证码')"
                    maxlength="6" @input="beforeCheckCode($event)"/>
          <el-button style="margin-right: 12px;position: absolute;right: 0;top: 0;" type="text" class="send-button"
                     @click="getCodePost('phone',0)">
            {{ !getCode ? $t('发送') : codeCount }}
          </el-button>
        </div>
        <el-button v-if="[1,2].includes(this.kycType)" class="w-full h-44" style="margin-top: 20px" type="primary"
                   @click="getBeforeBindCodePost('phone')"
                   :disabled="!(beforeCode && beforeCode.length===6)">
          {{ $t('下一步') }}
        </el-button>
        <el-button v-else class="w-full h-44" style="margin-top: 20px" type="primary"
                   @click="getBeforeBindCodePost('phone')"
                   :disabled="!(beforeCode && beforeCode.length===6)">
          {{ $t('提交验证') }}
        </el-button>
      </div>
      <div v-else>
        <p v-if="[1,2].includes(this.kycType)" style="margin-bottom: 12px">
          {{ $t('为了保障您的账号安全，请验证后进行下一步操作') }}</p>
        <p class="mb-8 font-12" style="color: #333;margin-top: 24px;">{{ $t('当前绑定邮箱') }}</p>
        <p style="display: flex;width: 100%;justify-content: space-between;">
          <span style="font-size: 18px;color: black;padding-right: 24px;">{{ userInfo.email | formatEmail }}</span>
          <span v-if="userInfo.phone"
                style="color: #2C78F8;cursor: pointer;flex: 1;position:relative;text-indent: 24px;text-align: right;"
                @click="changeCheckType('phone')">
            <i class="el-icon-sort"
               style="transform: rotate(90deg);text-indent: 0"/>
            {{ $t('切换手机接收验证码') }}
          </span>
        </p>
        <div class="flex rounded" style="position: relative;margin-top: 24px;">
          <el-input v-model="beforeCode" :placeholder="$t('请输入验证码')"
                    maxlength="6" @input="beforeCheckCode($event)"/>
          <el-button style="margin-right: 12px;position: absolute;right: 0;top: 0;" type="text" class="send-button"
                     @click="getCodePost('email',0)">
            {{ !getCode ? $t('发送') : codeCount }}
          </el-button>
        </div>
        <el-button v-if="[1,2].includes(this.kycType)" class="w-full h-44" style="margin-top: 20px" type="primary"
                   @click="getBeforeBindCodePost('email')"
                   :disabled="!(beforeCode && beforeCode.length===6)">
          {{ $t('下一步') }}
        </el-button>
        <el-button v-else class="w-full h-44" style="margin-top: 20px" type="primary"
                   @click="getBeforeBindCodePost('email')"
                   :disabled="!(beforeCode && beforeCode.length===6)">
          {{ $t('提交验证') }}
        </el-button>
      </div>
    </div>
    <div v-if="step===0" class="change">
      <div v-if="editTitle === $t('修改手机')">
        <p class="mb-8 font-12" style="color: #333;margin-top: 12px;">{{ $t('手机号') }}</p>
        <div class="c_phone-input-content">
          <img :src="require('@/assets/images/login/phone2.png')" alt="" class="input-icon"/>
          <el-dropdown class="input-dropdown" placement="bottom" trigger="click" @command="handlePhone">
                      <span class="el-dropdown-link" placement="bottom-start">
                        +{{ activeAddress }}<i class="ml-10 el-icon-caret-bottom"></i>
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
              v-model="editPhone.phone"
              @input="checkPhone"
              clearable>
          </el-input>
        </div>
        <p class="mb-8 font-12" style="color: #333;margin-top: 12px;">{{ $t('验证码') }}</p>
        <div class="flex rounded" style="position: relative;">
          <el-input v-model="editPhone.code" :placeholder="$t('请输入验证码')"
                    maxlength="16" @input="checkCode($event,'editPhone')"/>
          <el-button style="margin-right: 12px;position: absolute;right: 0;top: 0;" type="text" class="send-button"
                     @click="getCodePost('phone',1)">
            {{ !getCode ? $t('发送') : codeCount }}
          </el-button>
        </div>
        <p class="mb-8 font-12" style="color: #333;margin-top: 12px;">{{ $t('登录密码') }}</p>
        <PasswordInput v-model="editPhone.password" @clear="editPhone.password=''"
                       :placeholder="$t('请输入登录密码')"/>
        <el-button class="w-full h-44" style="margin-top: 20px" type="primary" @click="phoneBinding">
          {{ $t('确认') }}
        </el-button>
      </div>
      <div v-else>
        <p class="mb-8 font-12" style="color: #333">{{ $t('邮箱') }}</p>
        <div class="flex rounded relative">
          <el-input v-model="editEmail.email" :placeholder="$t('请输入邮箱')" clearable maxlength="100"></el-input>
        </div>
        <p class="mb-8 font-12" style="color: #333;margin-top: 12px;">{{ $t('验证码') }}</p>
        <div class="flex rounded" style="position: relative;">
          <el-input v-model="editEmail.code" :placeholder="$t('请输入验证码')"
                    maxlength="16" @input="checkCode($event,'editEmail')"/>
          <el-button style="margin-right: 12px;position: absolute;right: 0;top: 0;" type="text" class="send-button"
                     @click="getCodePost('email',1)">
            {{ !getCode ? $t('发送') : codeCount }}
          </el-button>
        </div>
        <p class="mb-8 font-12" style="color: #333;margin-top: 12px;">{{ $t('登录密码') }}</p>
        <PasswordInput v-model="editEmail.password" @clear="editEmail.password=''"
                       :placeholder="$t('请输入登录密码')"/>
        <el-button class="w-full h-44" style="margin-top: 20px" type="primary" @click="emailBinding">
          {{ $t('确认') }}
        </el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script>
import PasswordInput from "@/components/PasswordInput/index.vue";
import {
  checkPhoneOrEmail,
  getBeforeBindCodePost,
  getCodePost,
  localuser_bindEmailOrPhone_action_post as bindEmailOrPhone,
  localuser_checkEmailOrPhone_action_post as checkEmailOrPhone
} from "@/api/user";
import countryList from "@/utils/country";
import setting from "@/settings";
import Toast from "@/utils/toast";
import {validEmail} from "@/utils/validate";
import {mapActions, mapGetters} from "vuex";

export default {
  name: "updateIphoneOrEmail",
  data() {
    return {
      beforeCode: '',
      verifyCode: '',
      checkType: 'phone',
      step: 0,
      activeAddress: setting.countryCode,
      searchCountry: '',
      countryList,
      getCode: false,
      codeCount: 60,
      timer: null,
      editTitle: this.$t('修改手机'),
      editPhone: {
        phone: '',
        code: ''
      },
      editEmail: {
        email: '',
        code: ''
      },
      editVisible: false,
      kycType: 0,
    };
  },
  components: {PasswordInput},
  computed: {
    ...mapGetters(['userInfo']),
  },
  filters: {
    formatPhone(value) {
      if (value) {
        // 带国际区号的手机号脱敏
        let index = value.indexOf(' ');
        return value.substring(0, index + 1) + value.substring(index, index + 4) + '****' + value.substring(value.length - 2, value.length);
      }
    },
    formatEmail(value) {
      if (value) {
        return value.replace(/(\w{1})\w{1,}(\w{1})/, '$1****$2')
      }
    }
  },
  methods: {
    ...mapActions("user", ["getInfo"]),
    closeDialog() {
      this.editVisible = false
    },
    changeCheckType(type) {
      this.checkType = type
    },
    changeDialog() {
      this.editVisible = true
      this.beforeCode = ''
      if (this.editTitle === this.$t('修改手机')) {
        if (this.userInfo.phone) {
          this.checkType = 'phone'
        } else {
          this.checkType = 'email'
        }
      } else {
        if (this.userInfo.email) {
          this.checkType = 'email'
        } else {
          this.checkType = 'phone'
        }
      }
      this.step = 1
    },
    changeEditTitle(title, kycType) {
      this.kycType = kycType
      this.editTitle = title
      this.editPhone = {
        phone: '',
        code: ''
      };
      this.editEmail = {
        email: '',
        code: ''
      };
    },
    //手机绑定
    phoneBinding() {
      const t = this
      if (t.editPhone.phone === '') {
        Toast(t.$t('请输入手机号'));
        return
      }
      let data = {
        target: this.activeAddress.replace('+', '') + ' ' + t.editPhone.phone,
        phone: this.activeAddress.replace('+', ' ') + ' ' + t.editPhone.phone,
        verifcode: t.editPhone.code,
        verifyCode: t.verifyCode,
        password: t.editPhone.password,
      }
      bindEmailOrPhone(data).then(res => {
        Toast.success(t.$t('修改成功'));
        this.editVisible = false
        this.getInfo()
        this.$emit('getMerchantInfo')
        this.$emit('infoPost')
      })
    },
    //邮箱绑定
    emailBinding() {
      const t = this
      let rule = /^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/
      let ruleCom = rule.test(t.editEmail.email)
      if (!t.editEmail.email && !ruleCom) {
        Toast(t.$t('请输入正确的邮箱地址'));
        return
      }
      let data = {
        email: t.editEmail.email,
        target: t.editEmail.email,
        verifcode: t.editEmail.code,
        verifyCode: t.verifyCode,
        password: t.editEmail.password,
      }
      bindEmailOrPhone(data).then(res => {
        Toast.success(t.$t('修改成功'));
        this.editVisible = false
        this.getInfo()
        this.$emit('getMerchantInfo')
        this.$emit('infoPost')
      })
    },
    checkPhone(value) {
      value = value.replace(/[^\d]/g, '')
      this.editPhone.phone = value
    },
    beforeCheckCode(value, type) {
      value = value.replace(/[^\d]/g, '')
      this.beforeCode = value
    },
    checkCode(value, type) {
      value = value.replace(/[^\d]/g, '')
      this[type].code = value
    },
    getCodes() {
      this.getCode = true
      const code = setInterval(() => {
        if (this.codeCount === 0) {
          clearInterval(code)
          this.codeCount = 60
          this.getCode = false
        }
        this.codeCount--
      }, 1000)
    },
    phoneNoCheck(phoneNo) {
      try {
        if (phoneNo === '') {
          throw "请输入手机号";
        }
      } catch (e) {
        if (typeof e == "string") {
          Toast(this.$t(e));
        }
        return false;
      }
      return true;
    },
    emailCheck(email) {
      try {
        if (email === '') {
          throw "请输入邮箱";
        }

        if (!validEmail(email)) {
          throw "请输入正确的邮箱地址"
        }
      } catch (e) {
        if (typeof e == "string") {
          Toast(this.$t(e));
        }

        return false;
      }

      return true;
    },
    getBeforeBindCodePost(type = 'phone') {
      let target = '';
      if (type === 'phone') {
        target = this.userInfo.phone
      } else {
        target = this.userInfo.email
      }
      if ([1, 2].includes(this.kycType)) {
        getBeforeBindCodePost({
          target,
          verifcode: this.beforeCode,
        }).then(res => {
          this.verifyCode = res.data.verifyCode
          this.step = 0
          this.codeCount = 0
        })
      } else {
        checkEmailOrPhone({
          target,
          verifcode: this.beforeCode,
        }).then(res => {
          this.editVisible = false
          //提示验证完成
          Toast.success(this.$t('验证完成'));
          //重新请求用户数据
          this.getInfo()
        })
      }
    },
    async getCodePost(type = 'phone', step = 0) {
      if (!this.getCode) {
        let target = '';
        if (type === 'phone') {
          if (!this.phoneNoCheck(this.editPhone.phone || this.userInfo.phone)) {
            return;
          }
          target = this.editPhone.phone ? (this.activeAddress.replace('+', '') + ' ' + this.editPhone.phone) : this.userInfo.phone
        } else {
          target = this.editEmail.email || this.userInfo.email
          if (!this.emailCheck(target)) {
            return;
          }
        }
        if (step === 1 && [1, 2].includes(this.kycType)) {
          let checkPhoneOrEmail = await this.checkPhoneOrEmail({target})
          if (!checkPhoneOrEmail) {
            return
          }
        }
        this.getCodes()
        getCodePost({
          target,
        }).then(res => {
          this.$notify({
            title: this.$t('成功'),
            message: this.$t('验证码发送成功'),
            type: 'success',
            duration: 2000
          })
        })
      }
    },
    checkPhoneOrEmail(data) {
      return new Promise((resolve, reject) => {
        checkPhoneOrEmail(data).then(res => {
          resolve(res)
        }).catch(err => {
          reject(err)
        })
      })
    },
    handlePhone(val) {
      this.activeAddress = val;
    },
    searchCountryList() {
      this.countryList = countryList.filter(item => {
        return item.zh.indexOf(this.searchCountry) > -1 || item.en.toUpperCase().indexOf(this.searchCountry.toUpperCase()) > -1 || item.code.indexOf(this.searchCountry) > -1 || item.tw.indexOf(this.searchCountry) > -1 || item.ko.indexOf(this.searchCountry) > -1
      })
    },
  }
}
</script>

<style scoped lang="scss">

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

.input-icon {
  position: absolute;
  left: 4px;
  z-index: 10;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
}

.phone-input {
  > .el-input__inner {
    padding-left: 114px;
  }
}

.project-dropdown {
  //设置高度才能显示出滚动条 !important
  height: 200px;
  overflow: auto;
  width: 378px;
  transform: translate(119px, 2px);
}
</style>
