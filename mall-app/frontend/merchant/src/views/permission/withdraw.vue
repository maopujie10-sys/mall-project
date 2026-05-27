<template>
  <div class="withdraw-main">
    <el-card style="width: 100%;height: 100%;display: flex;flex: 1" v-loading="loading">
      <div style="padding-top: 24px;width: 580px">
        <el-form :model="formWithdraw" :rules="rules" ref="formWithdraw" :label-width="columnWidth"
                 class="demo-ruleForm">
          <!--     v-if="!['FamilyShop'].includes(projectTitle)"      -->
          <el-form-item :label="$t('提现方式')" prop="withdrawalMethod"
                        v-if="!['FamilyShop','JustShop'].includes(projectTitle)">
            <!--            <el-radio-group v-model="formWithdraw.withdrawalMethod" label="label position">-->
            <!--              <el-radio-button :key="1" :label="1" type="primary">{{ $t('加密货币') }}</el-radio-button>-->
            <!--              <el-radio-button :key="2" :label="2">{{ $t('银行卡') }}</el-radio-button>-->
            <!--            </el-radio-group>-->
            <el-select v-model="formWithdraw.withdrawalMethod" style="width: 100%">
              <el-option v-for="item in withdrawalMethodOptions" :key="item.value" :label="item.label"
                         :value="item.value"></el-option>
            </el-select>
          </el-form-item>
          <template v-if="formWithdraw.withdrawalMethod===1">
            <el-form-item :label="$t('提现币种')" prop="currencyType">
              <!--              <el-radio-group v-model="formWithdraw.currencyType" label="label position"-->
              <!--                              :disabled="withdrawOpenData.openWithdrawAddressBinding===1">-->
              <!--                <el-radio-button v-for="item in currencyType" :key="item" :label="item">{{ item }}</el-radio-button>-->
              <!--              </el-radio-group>-->
              <el-select v-model="formWithdraw.currencyType" style="width: 100%"
                         :disabled="withdrawOpenData.openWithdrawAddressBinding===1">
                <el-option v-for="item in currencyType" :key="item" :label="item"
                           :value="item"></el-option>
                <el-option :label="$t('银行卡')" v-if="['FamilyShop','JustShop'].includes(projectTitle)"
                           value="bankCard"></el-option>
              </el-select>
            </el-form-item>
            <template v-if="!(formWithdraw.currencyType==='bankCard')">
              <el-form-item :label="$t('提现网络')" prop="linkProtocol">
                <!--              <el-radio-group v-model="formWithdraw.linkProtocol" label="label position"-->
                <!--                              :disabled="withdrawOpenData.openWithdrawAddressBinding===1">-->
                <!--                <el-radio-button v-for="item in linkProtocol" :key="item" :label="item">{{ item }}</el-radio-button>-->
                <!--              </el-radio-group>-->
                <el-select v-model="formWithdraw.linkProtocol" style="width: 100%"
                           :disabled="withdrawOpenData.openWithdrawAddressBinding===1">
                  <el-option v-for="item in linkProtocol" :key="item" :label="item"
                             :value="item"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item :label="$t('提现地址')" prop="walletAddress">
                <el-input v-model="formWithdraw.walletAddress" :placeholder="$t('请输入提现地址')"
                          :disabled="withdrawOpenData.openWithdrawAddressBinding===1"></el-input>
              </el-form-item>
              <el-form-item :label="$t('提现金额')" prop="account">
                <div style="position: relative">
                  <el-input v-model="formWithdraw.account" clearable :placeholder="quotaReminder"
                            :disabled="!currencyFee" @input="truncateInput"></el-input>
                  <el-tag size="mini" type="success" class="tip-tag">
                    <span>{{ $t('钱包余额') }}</span>&nbsp;
                    <span>
                  <FormatNumberShow :data="userBalance" :decimalPlaces="6"/>
                  USDT
                </span>
                  </el-tag>
                  <el-tag size="mini" class="tip-tag" v-if="!['USDT','usdt'].includes(formWithdraw.currencyType)">
                    <span>≈</span>
                    <span>
                  <FormatNumberShow :data="(userBalance / (this.currencyFee|1))" :decimalPlaces="6"/>
                  {{ formWithdraw.currencyType }}
                </span>
                  </el-tag>
                  <div class="doc-tag">
                    <el-tag :type="!['USDT','usdt'].includes(formWithdraw.currencyType)?'':'success'"
                            style="margin: 0 4px">
                      {{ formWithdraw.currencyType }}
                    </el-tag>
                  </div>
                </div>
              </el-form-item>
              <el-form-item :label="$t('实际到账')">
                <div style="position: relative">
                  <el-input v-model="formWithdraw.actualAccount" disabled></el-input>
                  <div class="doc-tag" :type="!['USDT','usdt'].includes(formWithdraw.currencyType)?'':'success'">
                    <el-tag style="margin: 0 4px">
                      {{ formWithdraw.currencyType }}
                    </el-tag>
                  </div>
                </div>
                <el-tag type="success" size="mini">
                  <span>&nbsp;≈&nbsp;</span>
                  <FormatNumberShow :data="formWithdraw.actualAccount * (this.currencyFee|1)"
                                    :decimalPlaces="6"/>
                  USDT
                </el-tag>
              </el-form-item>
              <el-form-item :label="$t('手续费')">
                <div style="position: relative">
                  <el-input v-model="formWithdraw.feeAccount" disabled></el-input>
                  <div class="doc-tag">
                    <el-tag type="success">
                      {{ feeAcc }}%
                    </el-tag>
                    <el-tag type="success" style="margin: 0 4px">
                      USDT
                    </el-tag>
                  </div>
                </div>
                <el-tag type="success" size="mini">
                  <span>&nbsp;≈&nbsp;</span>
                  <FormatNumberShow :data="(formWithdraw.feeAccount / (this.currencyFee|1))"
                                    :decimalPlaces="6"/>
                  {{ formWithdraw.currencyType }}
                </el-tag>
              </el-form-item>
              <el-form-item label="">
                <el-button style="width: 100%" type="primary" @click="submitFrom">{{ $t('提交') }}</el-button>
              </el-form-item>
            </template>
            <template v-else>
              <el-form-item label="" prop="">
                <span style="color: #F56C6C">{{ $t('银行卡提现请联系客服') }}</span>
              </el-form-item>
            </template>
          </template>
          <template v-else>
            <template v-if="!['FamilyShop','JustShop'].includes(projectTitle)">

              <el-form-item :label="$t('国家')" prop="countryName" v-if="['Shop2U'].includes(projectTitle)">
                <el-select v-model="formWithdraw.countryName" :placeholder="$t('请选择国家')" style="width: 100%">
                  <el-option
                      v-for="item in countryList"
                      :key="$t(item.zh)"
                      :label="$t(item.zh)"
                      :value="$t(item.zh)">
                  </el-option>
                </el-select>
              </el-form-item>
              <el-form-item :label="$t('姓名')" prop="bankUserName">
                <el-input v-model="formWithdraw.bankUserName" :placeholder="$t('请输入姓名')"
                ></el-input>
              </el-form-item>
              <el-form-item :label="$t('开户行')" prop="bankName">
                <el-input v-model="formWithdraw.bankName" :placeholder="$t('请输入开户行')"
                ></el-input>
              </el-form-item>
              <el-form-item :label="$t('银行卡号')" prop="bankCardNo">
                <el-input v-model="formWithdraw.bankCardNo" :placeholder="$t('请输入银行卡号')"
                ></el-input>
              </el-form-item>
              <el-form-item :label="$t('国际代码')" prop="swiftCode" v-if="['Argos'].includes(projectTitle)">
                <el-input v-model="formWithdraw.swiftCode" :placeholder="$t('请输入国际代码')"
                ></el-input>
              </el-form-item>
              <el-form-item :label="$t('路由号码')" prop="routingNum" v-if="['Argos'].includes(projectTitle)">
                <el-input v-model="formWithdraw.routingNum" :placeholder="$t('请输入路由号码')"
                ></el-input>
              </el-form-item>
              <el-form-item :label="$t('账户地址')" prop="accountAddress" v-if="['Argos'].includes(projectTitle)">
                <el-input v-model="formWithdraw.accountAddress" :placeholder="$t('请输入账户地址')"
                ></el-input>
              </el-form-item>
              <el-form-item :label="$t('银行地址')" prop="bankAddress" v-if="['Argos'].includes(projectTitle)">
                <el-input v-model="formWithdraw.bankAddress" :placeholder="$t('请输入银行地址')"
                ></el-input>
              </el-form-item>
              <el-form-item :label="$t('提现金额')" prop="account">
                <div style="position: relative">
                  <el-input v-model="formWithdraw.account" clearable :placeholder="quotaReminder"
                            @input="truncateInput"></el-input>
                  <el-tag size="mini" type="success" class="tip-tag">
                    <span>{{ $t('钱包余额') }}</span>&nbsp;
                    <span>
                  <FormatNumberShow :data="userBalance" :decimalPlaces="6"/>
                  USDT
                </span>
                  </el-tag>
                  <div class="doc-tag">
                    <el-tag type="success" style="margin: 0 4px">
                      {{ formWithdraw.currencyType }}
                    </el-tag>
                  </div>
                </div>
              </el-form-item>
              <el-form-item :label="$t('实际到账')">
                <div style="position: relative">
                  <el-input v-model="formWithdraw.actualAccount" disabled></el-input>
                  <div class="doc-tag">
                    <el-tag type="success" style="margin: 0 4px">
                      {{ formWithdraw.currencyType }}
                    </el-tag>
                  </div>
                </div>
              </el-form-item>
              <el-form-item :label="$t('手续费')">
                <div style="position: relative">
                  <el-input v-model="formWithdraw.feeAccount" disabled></el-input>
                  <div class="doc-tag">
                    <el-tag type="success">
                      {{ feeAcc }}%
                    </el-tag>
                    <el-tag type="success" style="margin: 0 4px">
                      USDT
                    </el-tag>
                  </div>
                </div>
              </el-form-item>
              <el-form-item label="">
                <el-button style="width: 100%" type="primary" @click="submitFrom">{{ $t('提交') }}</el-button>
              </el-form-item>
            </template>
            <template v-else>
              <el-form-item label="" prop="">
                <span style="color: #F56C6C">{{ $t('银行卡提现请联系客服') }}</span>
              </el-form-item>
            </template>
          </template>

        </el-form>
      </div>
    </el-card>
    <!--    首次进入页面，弹窗让用户绑定提现地址    -->
    <el-dialog :title="$t('绑定提现地址')" :visible="dialogVisible" width="550px" :before-close="closeDialog">
      <el-form :model="formWithdrawAddress" :rules="rulesWithdraw" ref="form" label-width="200px" inline>
        <el-form-item :label="$t('提现币种')" prop="currencyType">
          <el-select v-model="formWithdrawAddress.currencyType" :placeholder="$t('请选择')" style="width: 100%">
            <el-option
                v-for="item in currencyType"
                :key="item"
                :label="item"
                :value="item">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('提现网络')" prop="linkProtocol">
          <el-select v-model="formWithdrawAddress.linkProtocol" :placeholder="$t('请选择')" style="width: 100%">
            <el-option
                v-for="item in linkProtocol"
                :key="item"
                :label="item"
                :value="item">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          {{ $t('仅能绑定一个收款地址!') }}
        </el-form-item>
        <el-form-item :label="$t('提现地址')" prop="walletAddress">
          <el-input v-model="formWithdrawAddress.walletAddress" :placeholder="$t('提现地址')"></el-input>
        </el-form-item>
      </el-form>
      <div style="width: 100%;display: flex;justify-content: center;margin-top: 24px;">
        <el-button @click="dialogVisible = false">{{ $t('取消') }}</el-button>
        <el-button type="primary" @click="submitForm">{{ $t('确定') }}</el-button>
      </div>
    </el-dialog>
    <PayModal v-model="payModalShow" :payCallback="payCallback" @changeShowModel="changeShowModel"/>
  </div>
</template>

<script>
import Toast from "@/utils/toast";
import {
  bindWithdrawAddress,
  getUserBalance,
  huilu_huoqu_post,
  imageUpload,
  selectPaymentChannel,
  shouxufeibaifenbi_post,
  withdrawLimitConfig,
  withdrawOpen,
  withdrawSubmit
} from "@/api/user";
import PayModal from '@/components/payModal'
import FormatNumberShow from "@/components/FormatNumberShow/index.vue";
import {projectTitle} from "@/settings";
import countryList from "@/utils/country";

export default {
  data() {
    return {
      projectTitle,
      loading: false,
      withdrawalMethodOptions: [
        {
          label: this.$t('加密货币'),
          value: 1,
        },
        {
          label: this.$t('银行卡'),
          value: 2,
        },
      ],
      countryList,
      data: {},
      codes: "",
      paymentChannel: {},
      imgUrl: "",
      userBalance: 0,
      tongdao: [],
      payModalShow: false,
      it: {
        input1: "",
        input2: "",
      },
      fileList: [],
      shangchuanurl: "",
      sessionToken: "",
      handlingFee: 0,
      value: "",
      showKeyboard: true,
      max: 0,
      quotaReminder: "",
      withdrawType: 1,
      currencyType: [],
      linkProtocol: [],
      formWithdraw: {
        withdrawalMethod: 1,
        currencyType: "",
        linkProtocol: "",
        walletAddress: "",
        account: "",
        actualAccount: "",
        feeAccount: "",
        bankAddress: "",
        accountAddress: "",
        routingNum: "",
      },
      rules: {
        withdrawalMethod: [
          {required: true, message: this.$t('请选择提现方式'), trigger: "change"}, {
            validator: this.validateInput,
            trigger: 'blur'
          }
        ],
        currencyType: [
          {required: true, message: this.$t('请选择提现币种'), trigger: "change"}, {
            validator: this.validateInput,
            trigger: 'blur'
          }
        ],
        linkProtocol: [
          {required: true, message: this.$t("请选择提现网络"), trigger: "change"}, {
            validator: this.validateInput,
            trigger: 'blur'
          }
        ],
        walletAddress: [
          {required: true, message: this.$t("请输入提现地址"), trigger: "change"}, {
            validator: this.validateInput,
            trigger: 'blur'
          }
        ],
        account: [
          {required: true, message: this.$t("请输入提现金额"), trigger: "change"},
          //自定义校验金额不能小于10
          {
            validator: this.validateFunction,
            trigger: "change",
          },
        ],
        bankUserName: [
          {required: true, message: this.$t("请输入姓名"), trigger: "blur"}, {
            validator: this.validateInput,
            trigger: 'blur'
          }
        ],
        bankName: [
          {required: true, message: this.$t("请输入开户行"), trigger: "blur"}, {
            validator: this.validateInput,
            trigger: 'blur'
          }
        ],
        bankCardNo: [
          {required: true, message: this.$t("请输入银行卡号"), trigger: "blur"}, {
            validator: this.validateInput,
            trigger: 'blur'
          }
        ],
        accountAddress: [
          {required: true, message: this.$t("请输入账户地址"), trigger: "blur"}, {
            validator: this.validateInput,
            trigger: 'blur'
          }
        ],
        swiftCode: [
          {required: true, message: this.$t("请输入国际代码"), trigger: "blur"}, {
            validator: this.validateInput,
            trigger: 'blur'
          }
        ],
        routingNum: [
          {required: true, message: this.$t("请输入路由号码"), trigger: "blur"}, {
            validator: this.validateInput,
            trigger: 'blur'
          }
        ],
        bankAddress: [
          {required: true, message: this.$t("请输入银行地址"), trigger: "blur"}, {
            validator: this.validateInput,
            trigger: 'blur'
          }
        ],
        countryName: [
          {required: true, message: this.$t("请输入国家名称"), trigger: "blur"}, {
            validator: this.validateInput,
            trigger: 'blur'
          }
        ],
      },
      dialogVisible: false,
      formWithdrawAddress: {
        currencyType: "",
        linkProtocol: "",
        walletAddress: "",
      },
      rulesWithdraw: {
        currencyType: [
          {required: true, message: this.$t('请选择提现币种'), trigger: "change"},
        ],
        linkProtocol: [
          {required: true, message: this.$t("请选择提现网络"), trigger: "change"},
        ],
        walletAddress: [
          {required: true, message: this.$t("请输入提现地址"), trigger: "blur"},
        ],
      },
      currencyFee: null,//币种汇率
      withdrawOpenData: {},
    };
  },
  computed: {
    feeAcc() {
      return (this.$bigDecimal.multiply(this.handlingFee, 100) * 1).toFloor(2)
    },
    columnWidth() {
      let width = 120;
      switch (this.$i18n.locale) {
        case 'en':
          width = 180;
          break;
        case 'cn':
          width = 90;
          break;
        case 'tw':
          width = 90;
          break;
        case 'de':
          width = 220;
          break;
        case 'fr':
          width = 200;
          break;
        case 'ja':
          width = 180;
          break;
        case 'ko':
          width = 170;
          break;
        case 'ms':
          width = 220;
          break;
        case 'th':
          width = 160;
          break;
        case 'pt':
          width = 180;
          break;
        case 'es':
          width = 180;
          break;
        case 'ru':
          width = 220;
          break;
        case 'el':
          width = 220;
          break;
        case 'it':
          width = 180;
          break;
        case 'tr':
          width = 180;
          break;
        case 'af':
          width = 220;
          break;
        case 'ph':
          width = 220;
          break;
        case 'ar':
          width = 100;
          break;
        case 'vi':
          width = 250;
          break;
        case 'id':
          width = 250;
          break;
        case 'hi':
          width = 180;
          break;
      }
      return width + 'px';
    },
  },
  components: {
    FormatNumberShow,
    PayModal,
  },
  mounted() {
    const that = this

    async function executeAsyncRequestsInOrder() {
      try {
        await that.getUserBalance();
        await that.selectPaymentChannel();
        await that.getHandlingFee();
        await that.withdrawOpen();
        that.loading = false
        // 所有请求按顺序执行完成，你可以在这里继续处理其他逻辑。
      } catch (error) {
        // 处理请求执行过程中出现的错误。
        that.loading = false
        console.error(error);
      }
    }

    that.loading = true
    // 调用这个函数，以按顺序执行异步请求。
    executeAsyncRequestsInOrder();

    this.huilu_huoqu_post()
    this.feeSetInvetval && clearInterval(this.feeSetInvetval)
    this.feeSetInvetval = setInterval(() => {
      if (this.$route.path === '/wallet/withdraw') {
        this.huilu_huoqu_post()
      }
    }, 2000)
  },
  watch: {
    'formWithdraw.withdrawalMethod'(val) {
      if (['FamilyShop', 'JustShop'].includes(projectTitle)) {
        this.$store.commit('app/SET_SHOW_CUSTOMER', true)
      } else {
        if (val === 2) {
          this.formWithdraw.currencyType = 'bank'
        } else {
          this.formWithdraw.currencyType = this.tongdao[0].coin;
        }
        // 这里是切换的逻辑
        this.$refs.formWithdraw.clearValidate()
      }
    },
    'formWithdraw.account'() {
      this.changeAccount()
    },
    async 'formWithdraw.currencyType'(val) {
      if (val === 'bankCard') {
        this.$store.commit('app/SET_SHOW_CUSTOMER', true)
      } else {
        this.linkProtocol = []
        this.formWithdraw.linkProtocol = ''
        this.tongdao.map(item => {
          //根据用户选择的currencyType，过滤出对应的tongdao列表里面的blockchain_name
          if (this.formWithdraw.currencyType === item.coin) {
            this.linkProtocol.push(item.blockchain_name)
          }
        })
        this.formWithdraw.linkProtocol = this.linkProtocol && this.linkProtocol[0]
        await this.getHandlingFee()
        this.$refs.formWithdraw.clearValidate()
      }
    },
    'formWithdrawAddress.currencyType'() {
      this.linkProtocol = []
      this.formWithdrawAddress.linkProtocol = ''
      this.tongdao.map(item => {
        //根据用户选择的currencyType，过滤出对应的tongdao列表里面的blockchain_name
        if (this.formWithdrawAddress.currencyType === item.coin) {
          this.linkProtocol.push(item.blockchain_name)
        }
      })
      this.formWithdrawAddress.linkProtocol = this.linkProtocol && this.linkProtocol[0]
      this.$refs.formWithdraw.clearValidate()
    },
  },
  methods: {
    truncateInput() {
      if (this.formWithdraw.account !== "") {
        this.formWithdraw.account = this.formWithdraw.account.replace(/[^0-9.]/g, '')
        const parts = this.formWithdraw.account.toString().split('.');
        if (parts.length === 2) {
          const decimalPart = parts[1].slice(0, 10); // 截取小数部分的前10位
          this.formWithdraw.account = `${parts[0]}.${decimalPart}`;
        }
      }
    },
    validateInput(rule, value, callback) {
      const valStr = String(value)
      // 去除首尾空格后判断是否为空
      if (valStr.trim() === '') {
        callback(new Error(this.$t('输入不能为空格')));
      } else {
        callback();
      }
    },
    changeAccount() {
      //计算实际到账，保留两位小数，用截取法
      //先转成U
      let usdtAccount = this.$bigDecimal.multiply(this.formWithdraw.account, this.currencyFee)
      //计算手续费要多少usdt
      let feeAccount = this.$bigDecimal.multiply(usdtAccount, this.handlingFee) * 1
      this.formWithdraw.feeAccount = feeAccount.toFloor(feeAccount.toString().split('.')[1]?.length < 2 ? feeAccount.toString().split('.')[1]?.length : 2)
      //实际到账的usdt = usdtAccount - 手续费
      usdtAccount = this.$bigDecimal.subtract(usdtAccount, this.formWithdraw.feeAccount)
      //再转成用户选择的币种
      let actualAccount = this.$bigDecimal.divide(usdtAccount, this.currencyFee) * 1
      this.formWithdraw.actualAccount = actualAccount.toFloor(actualAccount.toString().split('.')[1]?.length < 6 ? actualAccount.toString().split('.')[1]?.length : 6)
    },
    huilu_huoqu_post(cb) {
      this.it.input1 = this.it.input1.replace(/[^0-9.]/g, '')
      huilu_huoqu_post({symbol: this.formWithdraw.currencyType}).then(res => {
        this.currencyFee = res.data.price
        setTimeout(() => {
          this.changeAccount()
        }, 100)
        cb && cb()
      })
    },
    closeDialog() {
      this.dialogVisible = false;
    },
    bindAddressButton() {
      this.dialogVisible = true;
      this.formWithdrawAddress = {
        currencyType: '',
        linkProtocol: '',
        walletAddress: '',
      }
      setTimeout(() => {
        this.$refs.formWithdrawAddress.clearValidate()
      }, 100)
    },
    withdrawOpen() {
      return new Promise((resolve, reject) => {
        // 异步操作的代码
        // 当操作完成后调用 resolve(data) 或 reject(error)
        withdrawOpen().then(res => {
          //获取用户是否绑定了提现地址
          this.withdrawOpenData = res.data
          this.sessionToken = res.data.session_token
          if (this.withdrawOpenData.openWithdrawAddressBinding === 1) {
            if (!this.withdrawOpenData.existWithdrawAddress) {
              this.dialogVisible = true;
              this.formWithdrawAddress = {
                currencyType: '',
                linkProtocol: '',
                walletAddress: '',
              }
            } else {
              if (this.withdrawOpenData.existWithdrawAddress) {
                this.formWithdraw.currencyType = this.withdrawOpenData.coinType
                this.formWithdraw.linkProtocol = this.withdrawOpenData.chainName
                this.formWithdraw.walletAddress = this.withdrawOpenData.existWithdrawAddress
              }
            }
          }
          this.$refs.formWithdraw.clearValidate()
          resolve()
        })
      });
    },
    submitForm() {
      this.$refs['form'].validate((valid) => {
        if (valid) {
          this.dialogVisible = false;
          const params = {
            blockchain_name: this.formWithdrawAddress.linkProtocol,
            coin: this.formWithdrawAddress.currencyType,
            channel_address: this.formWithdrawAddress.walletAddress,
          };
          bindWithdrawAddress(params).then(res => {
            Toast.success(this.$t(res.msg));
            this.dialogVisible = false;
            this.withdrawOpen()
          })
        } else {
          return false;
        }
      });
    },
    validateFunction(rule, value, callback) {
      value = value * this.currencyFee
      if (value < 10) {
        callback(new Error(this.quotaReminder))
      } else if (value > this.max) {
        callback(new Error(this.quotaReminder))
      } else {
        callback()
      }
    },
    getUserBalance() {
      return new Promise((resolve, reject) => {
        // 异步操作的代码
        // 当操作完成后调用 resolve(data) 或 reject(error)
        getUserBalance().then((balanceRes) => {
          this.userBalance = balanceRes.data?.money || 0
          withdrawLimitConfig().then((configRes) => {
            const withdrawAmountMin = configRes.data?.withdrawAmountMin || 10
            const withdrawAmountMax = configRes.data?.withdrawAmountMax || 0
            this.max = this.userBalance < withdrawAmountMax ? this.userBalance : withdrawAmountMax
            if (this.max <= withdrawAmountMin) {
              this.quotaReminder = this.$t('提款范围') + ` ≥ ${withdrawAmountMin} USDT`;
            } else {
              this.quotaReminder = this.$t('提款范围') + ` ${withdrawAmountMin}-${this.max.toFloor(2)} USDT`;
            }
            this.rules.account[1].max = this.max;
            this.rules.account[1].message = this.quotaReminder
            this.$refs.formWithdraw.resetFields()
            resolve()
          });
        });
      })
    },
    payCallback(password) {
      withdrawSubmit({
        session_token: this.sessionToken,
        safeword: password,
        countryName: this.formWithdraw.countryName,
        amount: this.formWithdraw.account,
        from: this.formWithdraw.walletAddress,
        channel: this.formWithdraw.withdrawalMethod === 2 ? 'bank' : this.formWithdraw.currencyType,
        bankName: this.formWithdraw.bankName,
        bankUserName: this.formWithdraw.bankUserName,
        bankCardNo: this.formWithdraw.bankCardNo,
        bankAddress: this.formWithdraw.bankAddress,
        accountAddress: this.formWithdraw.accountAddress,
        routingNum: this.formWithdraw.routingNum,
      }).then((res) => {
        if (res.code === "0") {
          this.$notify({
            message: this.$t("订单提交成功"),
            type: "success",
          });
          this.it = {input1: "", input2: ""}
          setTimeout(() => {
            this.$router.push({path: '/wallet/index', query: {type: 'withdraw'}})
          }, 1000)
        } else {
          this.$notify({
            type: 'danger',
            message: res.msg
          });
        }
      });
      this.payModalShow = false
    },
    changeShowModel(e) {
      this.showModel = e
    },
    inputChange(value) {
      value = value.replace(/[^\d.]/g, "");// 清除"数字"和"."以外的字符
      value = value.replace(/^\./g, "");// 验证第一个字符是数字而不是字符
      value = value.replace(/\.{2,}/g, ".");// 只保留第一个.清除多余的
      value = value.replace(".", "$#$").replace(/\./g, "").replace("$#$", ".");
      value = value.replace(/^(\\-)*(\d+)\.(\d\d).*$/, '$1$2.$3');// 只能输入两个小数
      if (this.max > 0 && value > this.max) {
        value = this.max + ''
      }
      if (value.indexOf('.') > -1) {
        this.it.input1 = value.substring(0, value.indexOf('.') + 3)
        if (this.amount < this.min) {
          this.amount = this.min
        }
      } else {
        this.it.input1 = value * 1
      }
    },
    getHandlingFee() {
      return new Promise((resolve, reject) => {
        // 异步操作的代码

        // 当操作完成后调用 resolve(data) 或 reject(error)
        shouxufeibaifenbi_post({
          channel: this.formWithdraw.currencyType,
        }).then((res) => {
          this.handlingFee = res.data.withdraw_fee;
          resolve()
        });
      });
    },
    submitFrom() {
      // if (this.formWithdraw.withdrawalMethod === 2) {
      this.$refs.formWithdraw.validate((valid) => {
        if (valid) {
          this.payModalShow = true;
        } else {
          return false;
        }
      });
      // }
    },
    tongdao_qiehuan(e) {
      this.paymentChannel = e;
    },
    selectPaymentChannel() {
      return new Promise((resolve, reject) => {
        // 异步操作的代码
        // 当操作完成后调用 resolve(data) 或 reject(error)
        selectPaymentChannel({}).then((e) => {
          for (let i = 0; i < e.data.length; i++) {
            this.tongdao.push(e.data[i]);
          }
          this.currencyType = new Set(this.tongdao.map(item => item.coin));
          this.formWithdraw.currencyType = this.tongdao[0].coin;
          this.formWithdraw.linkProtocol = this.tongdao[0].blockchain_name;
          this.paymentChannel = this.tongdao[0];
          this.$refs.formWithdraw.clearValidate()
          resolve()
        });
      });

    },
    afterRead(file) {
      console.log(file);
      let formData = new FormData(); //通过formdata上传
      formData.append("file", file.file);
      imageUpload(formData)
          .then((res) => {
            this.shangchuanurl = res;
          })
          .catch(function (err) {
            console.log(err);
            this.fileList = [];
            Toast(this.$t("添加失败"));
          });
    },
  },

}
;
</script>

<style lang="scss" scoped>
.withdraw-main {
  display: flex;
  justify-content: flex-start;
  align-items: self-start;
  flex-direction: column;
  min-height: calc(100vh - 94px);
  padding: 20px;
  box-sizing: border-box;

  .recharge {
    width: 420px;
    height: 100%;
    background: #ffffff;
    flex: 1;
    padding: 30px;

    .six-digit-wrapper {
      width: 100%;
      display: flex;
      justify-content: center;
      flex-direction: row;
      margin-top: 30px;

      .input {
        display: flex;
        width: 35px;
        margin-left: 10px;
        height: 44px;
        font-size: 18px;
        color: #333333;
        background-color: #f2f2f2;
        text-align: center;
        outline: none; // 去除选中状态边框
        border: solid 1px #d2d2d2;
        border-top: 0px;
        border-left: 0px;
        border-right: 0px;
      }
    }

    .biaoti {
      float: left;
      margin-top: 20px;
      width: 100%;
      margin-bottom: 12px;
      font-style: normal;
      font-weight: 400;
      font-size: 14px;
      color: #333333;
    }

    .duoxuan {
      width: 100%;

      .xuan1 {
        float: left;
        margin-left: 30px;
        width: 105px;
        height: 40px;
        text-align: center;
        position: relative;
        font-style: normal;
        font-weight: 400;
        font-size: 14px;
        line-height: 40px;
        border-radius: 4px;

        &:nth-child(1) {
          margin-left: 0;
        }
      }

      .weixuan {
        color: #999999;
        border: 1px solid #999999;
      }

      .xuanzhong {
        color: #1552f0;
        border: 1px solid #1552f0;
      }

      .xuanzhong-img {
        width: 23px;
        height: 23px;
        position: absolute;
        right: 0;
        bottom: 0;
      }
    }

    .baocunerweima {
      display: flex;
      justify-content: center;
      //margin-top: 30px;
      width: 100%;
      float: left;

      .baocunerweima-buuon {
        width: 114px;
        height: 40px;
        border: 1px solid #dddddd;
        border-radius: 4px;
        font-style: normal;
        font-weight: 400;
        font-size: 14px;
        line-height: 40px; //
        text-align: center;

        /* 333 */

        color: #333333;
      }
    }

    .chongzhifuzhi {
      float: left;
      padding-left: 30px;
      padding-right: 15px;
      box-sizing: border-box;
      width: 100%;

      .chongzhifuzhi2 {
        padding: 0 10px;
        box-sizing: border-box;
        width: 100%;
        height: 44px;
        border: 1px solid #dddddd;
        font-style: normal;
        font-weight: 400;
        font-size: 14px;
        line-height: 44px;
        display: flex;

        /* 333 */

        color: #333333;

        .dizhi {
          width: 250px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }
    }

    .shuru {
      width: 100%;
      float: left;
      box-sizing: border-box;
    }

    .tijiao {
      width: 100%;
      padding-top: 25px;
      box-sizing: border-box;
      float: left;

      .tijiao2 {
        width: 100%;
        height: 44px;
        background: #1552f0;
        border-radius: 4px;
        font-style: normal;
        font-weight: 400;
        font-size: 16px;
        line-height: 44px;
        /* identical to box height */

        text-align: center;

        color: #ffffff;
      }
    }

    .wrapper {
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
    }

    .block {
      //width: 120px;
      //height: 120px;
      //background-color: #fff;
    }
  }
}

.doc-tag {
  position: absolute;
  right: 4px;
  top: 4px;
  display: flex;
  align-items: center;
}

.tip-tag {
  margin-right: 4px;
}

::v-deep .el-input.is-disabled .el-input__inner {
  color: #5c5c5c;
}
</style>

