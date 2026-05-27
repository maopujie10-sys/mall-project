<template>
  <el-form
    :model="registerModel"
    :rules="rules"
    ref="reigsterForm"
    label-position="top"
    
  >
    <el-form-item :label="$t('message.home.orderEmail')" prop="username">
      <div class="ipt_box">
        <el-input
          v-model="registerModel.username"
          :placeholder="$t('message.home.pleaseEnterEmail')"
          @keyup.enter.native="registerEvent"
          :maxlength="64"
          :class="itemname!=='SM-wholesale shop' && itemname=='FamilyShop'? '' :'email_ipt'"
        />
        <!-- <el-button type="primary" class="send_code" v-if="itemname=='SM-wholesale shop'" @click="sendCode()" @submit.native.prevent :disabled='codedis'>{{sendtext}}</el-button> -->
      </div>
      
    </el-form-item>

    <!-- <el-form-item :label="$t('message.home.验证码')" prop="verifcode" v-if="itemname=='SM-wholesale shop'">
      <el-input  v-model.trim="registerModel.verifcode"
          :placeholder="$t('message.home.请输入验证码')"
          oninput="value=value.replace(/[^\d]/g,'')"
          maxlength="6">

      </el-input>
    </el-form-item> -->
    <el-form-item :label="$t('message.home.mobilePhone')" prop="phone" v-if="itemname=='SM-wholesale shop' || itemname=='FamilyShop'">
      <div class="form_phone form-phone">
        
        <el-input
          v-model.trim="registerModel.phone"
          :placeholder="$t('message.home.pleaseEnterPhoneNumer')"
          maxlength="30"
          @keyup.enter.native="registerEvent"
        ></el-input>
        <VueCountryIntl
          v-model="registerModel.areaCode"
          schema="popover"
          :searchInputPlaceholder="$t('message.home.searchCountry')"
          :noDataText="$t('message.home.noDataFound')"
        >
          <div class="area-code flex-between" slot="reference">
            <span>+{{ registerModel.areaCode }}</span>
            <i class="el-icon-caret-bottom"></i>
          </div>
        </VueCountryIntl>
      </div>
    </el-form-item>
    <el-form-item :label="$t('message.home.password')" prop="password">
      <el-input
        v-model="registerModel.password"
        :type="showPassword ? 'password' : 'text'"
        :placeholder="$t('message.home.pleaseEnterPassword')"
        @keyup.enter.native="registerEvent"
      >
        <template slot="suffix">
          <img
            class="password-icon"
            :src="showPassword ? imageMap.close : imageMap.open"
            @click="showPassword = !showPassword"
          />
        </template>
      </el-input>
    </el-form-item>
    <el-form-item
      :label="$t('message.home.confirmPassword')"
      prop="confirmPassword"
    >
      <el-input
        :type="showConfirm ? 'password' : 'text'"
        v-model="registerModel.confirmPassword"
        :placeholder="$t('message.home.plaseeENterConfirmPassword')"
      >
        <template slot="suffix">
          <img
            class="password-icon"
            :src="showConfirm ? imageMap.close : imageMap.open"
            @click="showConfirm = !showConfirm"
          />
        </template>
      </el-input>
    </el-form-item>
    <el-form-item>
      <p class="tips">
        {{ $t("message.home.loginTips") }}
        <span @click="goLogin">{{ $t("message.home.loginIn") }}</span>
      </p>
      <el-button
        class="sing-in-btn"
        type="primary"
        :loading="loading"
        @click="registerEvent"
      >
        {{ $t("message.home.signUp") }}
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script>
import { resgisterApi ,getVeriCodeApi ,JustRegisterApi} from "@/api";
import common from "@/util/common";
import { mapActions, mapMutations } from "vuex";
import VueCountryIntl from "vue-country-intl";
import { BASE_AREA_CODE } from "@/common";
export default {
  name: "EsAccountForm",
  data() {
    return {
      loading: false,
      codedis: false,
      sendtext: this.$t("message.home.发送"),
      itemname: process.env.VUE_APP_ITEM_NAME,
      agentCode:'',
      registerModel: {
        username: "",
        password: "",
        confirmPassword: "",
        areaCode: BASE_AREA_CODE,
        phone: "",
        // verifcode:""
      },
      showPassword: true,
      showConfirm: true,
      imageMap: {
        open: require("@/assets/image/eye-open.png"),
        close: require("@/assets/image/eye-close.png"),
      },
      rules: {
        username: [
          common.ruleUtils.getRule(
            "required",
            this.$t("message.home.inpuEmailErro")
          ),
          common.ruleUtils.getRule("email"),
        ],
        password: [
          common.ruleUtils.getRule(
            "required",
            this.$t("message.home.pleaseEnterPassword")
          ),
          common.ruleUtils.getRule("password"),
        ],
        // usercode: [common.ruleUtils.getRule('sixNumber')],
        confirmPassword: [
          common.ruleUtils.getRule(
            "required",
            this.$t("message.home.plaseeENterConfirmPassword")
          ),
          common.ruleUtils.getRule("validator", "", {
            validator: (rule, value, callback) => {
              if (value !== this.registerModel.password) {
                callback(new Error(this.$t("message.home.twoPawword")));
                return;
              }
              callback();
            },
          }),
        ],
      },
    };
  },
  activated(){
    if(this.registerModel.username){
      this.registerModel.username = '';
      this.registerModel.password = '';
      this.registerModel.confirmPassword = '';
    }
    this.$refs.reigsterForm.validateOnRuleChange = false;
    if(this.itemname == 'SM-wholesale shop' || this.itemname=='FamilyShop'){
      let rule= {
        phone: [
          common.ruleUtils.getRule(
            "required",
            this.$t("message.home.pleaseEnterPhoneNumer")
          ),
          common.ruleUtils.getRule("phone"),
        ],
      // verifcode: [
      //     common.ruleUtils.getRule(
      //       "required",
      //       this.$t("message.home.请输入验证码")
      //     ),
      //   ],
      }
      this.rules = {...this.rules, ...rule}
    }
    
  },
  components:{VueCountryIntl},
  methods: {
    ...mapActions(["getUserInfo"]),
    ...mapMutations({ setToken: "SETTOKEN" }),
  async sendCode (){
    const rule = /^([A-Za-z0-9_\-\.\w{3,}])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/
    if(rule.test(this.registerModel.username)){
        await getVeriCodeApi({target:this.registerModel.username})
        this.$message({
        message: this.$t("message.home.已发送，请注意查收"),
        type: "success",
      });
      let num = 61
      let timer = setInterval(() => {
          num--;
          this.sendtext = num + 's';
          if (num == 0) {
              clearInterval(timer);
              this.sendtext = this.$t("message.home.发送");
              this.codedis = false;   
          }
      },1000)
      this.codedis = true;
    }else{
      
      this.$message({
        message: this.$t("message.home.inpuEmailErro"),
        type: "error",
    })
    }
  },

    registerEvent() {
      
      this.$refs.reigsterForm.validate(async (valid) => {
        if (valid) {
          try {
            if (localStorage.getItem('agentCode')){
              this.agentCode = localStorage.getItem('agentCode');
            }
            this.loading = true;
            const registerModel = {
              username: this.registerModel.username,
              password: this.registerModel.password,
              confirmPassword: this.registerModel.confirmPassword,
              type: 2,
              re_password: this.registerModel.password,
              agentCode: this.agentCode,
            };

            if (this.itemname =='SM-wholesale shop'|| this.itemname=='FamilyShop') {
              registerModel.phone = this.registerModel.areaCode +
                  " " +
                  this.registerModel.phone
               const registerResult = await JustRegisterApi(registerModel)
                this.setToken(registerResult.data.token);
                await this.getUserInfo(registerResult.data);
                this.$refs.reigsterForm.resetFields();
                this.$message({
                  message: this.$t("message.home.registerSuccess"),
                  type: "success",
                });
                this.$router.replace("/");
              
            }else{
              const registerResult = await resgisterApi(registerModel);
              this.setToken(registerResult.data.token);
              await this.getUserInfo(registerResult.data);
              this.$refs.reigsterForm.resetFields();
              this.$message({
                message: this.$t("message.home.registerSuccess"),
                type: "success",
              });
              this.$router.replace("/");
            }
           
          } finally {
            this.loading = false;
          }
        }
      });
    },
    goLogin() {
      sessionStorage.setItem("path", "/register");
      this.$router.push("/login");
    },
  },
};
</script>
<style lang="scss" scoped>
html[dir="rtl"]{
  .el-form-item /deep/ .el-form-item__error{
    right: 0;
    left: auto;
  }
  .el-input {
      .el-input__suffix {
          left: 5px;
          right: auto;
          margin-left: 10px;
      }
    }
   .el-input--suffix .el-input__inner {
          padding-left: 15px;
          padding-right: 15px;
      }  
}
.vue-country-item.selected .selected-text{
  display: none;
}
.ipt_box{
  display: flex;
  max-width: 500px;
  .email_ipt{
     margin-right: 5px;
  }
  .send_code{
    flex: 1;
    min-width: 112px;
  }
}
</style>