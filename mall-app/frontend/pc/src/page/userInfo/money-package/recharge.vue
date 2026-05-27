<template>
  <!-- <el-dialog custom-class="wallet-dialog" :title="$t('message.home.recharge')" :visible.sync="dialogVisible"
      :close-on-click-modal="false" :close-on-press-escape="false"> -->
  <div class="info_page_container" style="width: 480px">
    <div
      class="page-title"
      style="cursor: pointer; margin-bottom: 20px"
      @click="goBack"
    >
      <i class="el-icon-arrow-left"></i>
      {{ $t("message.home.myPurse") }}/{{ $t("message.home.recharge") }}
    </div>
    <!-- v-if="itemname == 'Shop2u'" -->
    <el-form v-if="itemname == 'Shop2u' || itemname == 'SM-wholesale shop'">
      <el-form-item :label="$t('message.home.rechargeMethod')">
        <el-select
          style="width: 100%"
          v-model="rachargeTypeV"
          @change="changeType(rachargeTypeV)"
        >
          <el-option
            v-for="item in rachargeType"
            :key="item.value || item.productType"
            :label="item.productType"
            :value="item.value || item.productType"
          >
          </el-option>
        </el-select>
      </el-form-item>
    </el-form>

    <el-form
      ref="rechargeForm"
      label-position="top"
      :model="form"
      :rules="rules"
      v-loading="httpLoading"
      v-if="rachargeTypeV == 'Virtual'"
    >
      <!-- <div class="network-select">
       
        <el-form-item :label="$t('message.home.blockchainNetwork' /**区块链网络 */)" prop="network">
          <el-radio-group v-model="form.network">
            <el-radio-button v-for="item in coinInfo" :key="item.blockchain_name"
              :label="item.blockchain_name"></el-radio-button>
          </el-radio-group>
        </el-form-item>
      </div> -->

      <el-form-item :label="$t('message.home.充值币种')" prop="coin">
        <el-select style="width: 100%" v-model="form.coin">
          <el-option
            v-for="item in Object.keys(groupBlockAddress)"
            :key="item"
            :label="item"
            :value="item"
            :disabled="item != 'USDT' && itemname === 'Inchoi'"
          >
          </el-option>
          <div
            :key="$t('message.home.银行卡')"
            class="el-select-dropdown__item"
            @click="openService"
          >
            {{ $t("message.home.银行卡") }}
          </div>
        </el-select>
      </el-form-item>

      <el-form-item
        :label="$t('message.home.blockchainNetwork' /**区块链网络 */)"
        prop="blockId"
      >
        <el-select style="width: 100%" v-model="form.blockId">
          <el-option
            v-for="item in groupBlockAddress[form.coin]"
            :key="item.id"
            :label="`${item.coin}-${item.blockchain_name}`"
            :value="item.id"
          >
          </el-option>
        </el-select>
      </el-form-item>

      <div class="qr-code">
        <div id="qrCode" class="qr-code-wrap flex-center">
          <VueQr :size="132" :text="form.address" :margin="0" />
        </div>

        <!-- <img src="@/assets/image/qrcode.svg" alt="qrcode" /> -->
        <el-button class="qr-btn" @click="saveImage">
          {{ $t("message.home.saveQr" /**保存二維碼 */) }}
        </el-button>
      </div>

      <el-form-item
        :label="$t('message.home.rechargeAddress')"
        class="wallet-address"
        prop="address"
      >
        <el-input
          v-model="form.address"
          :placeholder="$t('message.home.plaseEnterRechargeAddress')"
          disabled
        />
        <span
          :class="{
            'copy-btn': true,
            disabled: isDisabled,
          }"
          @click="copy"
        >
          {{ $t("message.home.copy") }}
        </span>
      </el-form-item>

      <el-form-item :label="$t('message.home.quantity')" prop="quantity">
        <el-input
          v-model="form.quantity"
          maxlength="12"
          onkeyup="if(isNaN(value))execCommand('undo')"
          onafterpaste="if(isNaN(value))execCommand('undo')"
          :placeholder="$t('message.home.pleaseEnterAmount')"
        />
      </el-form-item>

      <el-form-item
        :label="`${$t('message.home.expectedArrival')}(${$t(
          'message.home.currentRate'
        )}1 : ${numberFormat(currentSelectBlock.fee)})`"
      >
        <el-input
          :value="numberFormat(arrival)"
          disabled
          :placeholder="$t('message.home.expectedArrival')"
        />
      </el-form-item>

      <el-form-item
        :label="$t('message.home.uploadTips')"
        class="image-uploader"
        prop="image"
      >
        <el-upload
          :action="UploadApi"
          :show-file-list="false"
          :on-error="onUploadError"
          :before-upload="beforeUpload"
          :on-success="onSuccess"
          :data="uploadParams"
          accept=".jpg,.jpeg,.png,.bmp,.pdf,.JPG,.JPEG,.PBG,.BMP,.PDF"
        >
          <img v-if="form.image" :src="form.image" class="image" alt="image" />
          <img v-else src="@/assets/image/camera.png" alt="camera" />
        </el-upload>
        <div class="label">{{ $t("message.home.clickUpload") }}</div>
      </el-form-item>

      <el-form-item>
        <el-button
          type="primary"
          style="width: 100%"
          :loading="btnLoading"
          @click="recharge"
        >
          {{ $t("message.home.btnSure") }}
        </el-button>
      </el-form-item>
    </el-form>
    <!-- 银行卡充值 -->
    <el-form
      v-if="rachargeTypeV == 'Bank' && itemname == 'SM-wholesale shop' || itemname == 'Shop2u'"
      :model="bankForm"
    >
      <el-form-item :label="$t('message.home.充值币种')" prop="coin">
        <el-select
          style="width: 100%"
          v-model="bankForm.frenchCurrency"
          @change="getcurrency"
        >
          <el-option
            v-for="item in currencyList"
            :key="item.bank_code"
            :label="item.bank_code"
            :value="item.bank_code"
          >
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item :label="$t('message.home.充值金额')">
        <el-input
          v-model="bankForm.amount"
          :placeholder="$t('message.home.pleaseEnterAmount')"
          @input="inputHandler"
          @change="quantityHandler"
        />
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          style="width: 100%"
          :loading="btnLoading"
          :disabled="bankBtn"
          @click="bankReharge"
        >
          {{ $t("message.home.btnSure") }}
        </el-button>
      </el-form-item>
    </el-form>

    <!-- G -->
    <el-form :model="gcashFrom" v-if="rachargeTypeV == 'GCash'">
      <el-form-item :label="$t('message.home.充值币种')" prop="coin">
        <el-select
          style="width: 100%"
          v-model="gcashFrom.coin"
          @change="getcurrency(gcashFrom.coin)"
        >
          <el-option
            v-for="item in currencyList"
            :key="item.bank_code"
            :label="item.bank_code"
            :value="item.bank_code"
          >
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item :label="$t('message.home.充值金额')">
        <el-input
          v-model="gcashFrom.amount"
          :placeholder="$t('message.home.pleaseEnterAmount')"
          @input="inputHandler('GCash')"
          @change="quantityCash"
        />
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          style="width: 100%"
          :loading="btnLoading"
          :disabled="gcashbtn"
           :key="1"
          @click="gcashReharge"
        >
          {{ $t("message.home.btnSure") }}
        </el-button>
      </el-form-item>
    </el-form>

    <el-form :model="gcash2From" v-if="rachargeTypeV == 'GCash2.0'">
      <el-form-item :label="$t('message.home.充值币种')" prop="coin">
        <el-select
          style="width: 100%"
          v-model="gcash2From.coin"
          @change="getcurrency(gcash2From.coin, 'GCash2.0')"
        >
          <el-option
            v-for="item in currencyList"
            :key="item.bank_code"
            :label="item.bank_code"
            :value="item.bank_code"
          >
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item :label="$t('message.home.充值金额')">
        <el-input
          v-model="gcash2From.amount"
          :placeholder="$t('message.home.pleaseEnterAmount')"
          @input="inputHandler(gcash2From.coin, 'GCash2.0')"
          @change="quantityGCash"
        />
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          style="width: 100%"
          :loading="btnLoading"
          :disabled="gcashPbtn"
           :key="2"
          @click="gcashPhpReharge"
        >
          {{ $t("message.home.btnSure") }}
        </el-button>
      </el-form-item>
    </el-form>

    <el-form :model="gcash3From" v-if="rachargeTypeV == 'GCash3.0'">
      <el-form-item :label="$t('message.home.充值币种')" prop="coin">
        <el-select
          style="width: 100%"
          v-model="gcash3From.coin"
          @change="getcurrency(gcash3From.coin, 'GCash3.0')"
        >
          <el-option
           v-for="item in currencyList"
            :key="item.bank_code"
            :label="item.bank_code"
            :value="item.bank_code"
          >
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item :label="$t('message.home.充值金额')">
        <el-input
          v-model="gcash3From.amount"
          :placeholder="$t('message.home.pleaseEnterAmount')"
          @input="inputHandler(gcash3From.coin, 'GCash3.0')"
          @change="quantityGCash3"
        />
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          style="width: 100%"
          :loading="btnLoading"
          :disabled="gcash3btn"
          :key="3"
          @click="gcash3PhpReharge"
        >
          {{ $t("message.home.btnSure") }}
        </el-button>
      </el-form-item>
    </el-form>


    <el-form :model="mayaFrom" v-if="rachargeTypeV == 'Maya'">
      <el-form-item :label="$t('message.home.充值币种')" prop="coin">
        <el-select
          style="width: 100%"
          v-model="mayaFrom.coin"
          @change="getcurrency(mayaFrom.coin, 'Maya')"
        >
          <el-option
           v-for="item in currencyList"
            :key="item.bank_code"
            :label="item.bank_code"
            :value="item.bank_code"
          >
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item :label="$t('message.home.充值金额')">
        <el-input
          v-model="mayaFrom.amount"
          :placeholder="$t('message.home.pleaseEnterAmount')"
          @input="inputHandler(mayaFrom.coin, 'Maya')"
          @change="quantitymaya"
        />
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          style="width: 100%"
          :disabled="mayabtn"
          :key="4"
          @click="mayaPhpReharge"
        >
          {{ $t("message.home.btnSure") }}
        </el-button>
      </el-form-item>
    </el-form>

    <el-form :model="GCashPayFrom" v-if="rachargeTypeV == 'GCash pay'">
      <el-form-item :label="$t('message.home.充值币种')" prop="coin">
        <el-select
          style="width: 100%"
          v-model="GCashPayFrom.coin"
          @change="getcurrency(GCashPayFrom.coin, 'GCash pay')"
        >
          <el-option
            v-for="item in currencyList"
            :key="item.bank_code"
            :label="item.bank_code"
            :value="item.bank_code"
          >
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item :label="$t('message.home.充值金额')">
        <el-input
          v-model="GCashPayFrom.amount"
          :placeholder="$t('message.home.pleaseEnterAmount')"
          @input="inputHandler(GCashPayFrom.coin, 'GCash pay')"
          @change="quantityGcashPay"
        />
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          style="width: 100%"
          :disabled="GCashPayBtn"
          :key="4"
          @click="GCashPaySubmit"
        >
          {{ $t("message.home.btnSure") }}
        </el-button>
      </el-form-item>
    </el-form>
    <!-- <EsRechargeRecordDialog v-model="rechargeRecordVisible" /> -->
    <EsOnlineServiceView v-model="showOnlieService" />
  </div>
</template>

<script>
import { mapActions, mapGetters } from "vuex";
import VueQr from "vue-qr";
import {
  copyTextToClipboard,
  downloadImage,
  emptyStr,
  numberFormat,
} from "@/util";
import {
  UploadApi,
  getFeeApi,
  getRechargeListApi,
  submitBankRechargeApi,
  submitGcashRecharge,
  submitGcashPhpRecharge,
  gcash3PhpRecharge,
  mayaPhpRecharge,
  subGcashPay
} from "@/api";
import { ES_TOKEN } from "@/common";
import common from "@/util/common";
import { groupBy } from "lodash";
// import EsRechargeRecordDialog from './rechargeRecordDialog'

export default {
  name: "recharge-dialog",
  components: { VueQr },
  data() {
    return {
      loading: false,
      mayabtn: true,
      bankBtn:true,
      GCashPayBtn:true,
      showOnlieService: false,
      rachargeTypeV: "Virtual",
      minAmount: 0,
      maxAmount: 0,
      form: {
        address: "",
        quantity: "",
        arrival: "",
        image: "",
        coin: "",
        blockId: "",
      },
      bankForm: {
        frenchCurrency: "",
        amount: "",
      },
      gcashFrom: {
        amount: "",
        coin:""
      },
      gcashbtn: true,
      gcashPbtn: true,
      rachargeType: [
        {
          productType: this.$t("message.home.加密货币"),
          value: "Virtual",
        }
      ],
      itemname: process.env.VUE_APP_ITEM_NAME,
      rules: {
        quantity: [
          common.ruleUtils.getRule(
            "required",
            this.$t("message.home.pleaseEnterQuantity")
          ),
          common.ruleUtils.getRule("decimalSix"),
          common.ruleUtils.getRule("validator", "", {
            validator: (rule, value, callback) => {
              if (Number(value) > 10e8) {
                callback(this.$t("message.home.validatorMaxNumber"));
              }
              callback();
            },
          }),
        ],
        image: [
          common.ruleUtils.getRule(
            "required",
            this.$t("message.home.uploadPhoto")
          ),
        ],
      },
      gcash2From: {
        amount: "",
        coinList: [],
        coin: "",
      },
      gcash3From: {
        amount: "",
        coinList: [],
        coin: "",
      },
      mayaFrom:{
        amount: "",
        coinList: [],
        coin: "",
      },
      GCashPayFrom:{
        amount: "",
        coinList: [],
        coin: "",
      },
      currentSelectBlock: {},
      groupBlockAddress: {},
      UploadApi,
      gcashMinAmount: 0,
      gcashMaxAmount: 0,
      currencyList: [],
      uploadParams: {
        moduleName: "recharge",
        token: localStorage.getItem(ES_TOKEN),
      },
      rechageList:[],
      gcash3btn: true
    };
  },
  watch: {
    
    "form.coin": {
      handler(v) {
        if (v !== "") {
          this.autoSetBlock(this.groupBlockAddress[v][0]);
        }
      },
    },
    "form.blockId": {
      handler(v) {
        if (v !== "") {
          this.autoSetBlock(this.rechargeAddress.find((x) => x.id == v));
        }
      },
    },
  },
  computed: {
    ...mapGetters("recharge", [
      "sessionToken",
      "httpLoading",
      "btnLoading",
      "rechargeAddress",
    ]),
    isDisabled() {
      return emptyStr(this.form.address);
    },
    arrival() {
      return (this.form.quantity * this.currentSelectBlock.fee).toFixed(2);
    },
  },

  async mounted() {
    this.loading = true;
    try {
      await Promise.all([
        this.requestRechargeAddress(),
        this.requestSessionToken(),
      ]);
      this.$nextTick(() => {
        if (this.rechargeAddress.length > 0) {
          const n = this.itemname == "Inchoi" ? 2 : 0;
          this.form.coin = this.rechargeAddress[n].coin;
          this.autoSetBlock(this.rechargeAddress[n]);
        }
      });
    } finally {
      this.loading = false;
      this.groupAddress();
    }
  },
  methods: {
    ...mapActions("recharge", [
      "requestSessionToken",
      "requesRecharge",
      "requestRechargeAddress",
    ]),
    async changeType(e) {
      this.rachargeType.filter((item)=>{
        if(item.productType == e) {
          this.currencyList = item.range
        }
      })
        const { form, bankForm, gcash2From, gcash3From, mayaFrom, GCashPayFrom } = this;
        const resetForms = [form, bankForm, gcash2From, gcash3From, mayaFrom, GCashPayFrom];

        resetForms.forEach(form => {
          form.address = "";
          form.quantity = "";
          form.arrival = "";
          form.image = "";
          form.coin = "";
          form.blockId = "";
        });

        bankForm.frenchCurrency = "";
        bankForm.amount = "";
        gcash2From.coin = "";
        gcash2From.amount = "";
        gcash3From.coin = "";
        gcash3From.amount = "";
        mayaFrom.coin = "";
        mayaFrom.amount = "";
        GCashPayFrom.coin = "";
        GCashPayFrom.amount = "";

        this.bankBtn = true;
        this.gcash3btn = true;
        this.gcashbtn = true;
        this.gcashPbtn = true;
        this.mayabtn = true;

        this.getSesstionToken();
      },
    async getSesstionToken() {
      await this.requestSessionToken();
    },
    async gcashReharge() {
      // console.log('this.gcashFrom.amount ->', this.gcashFrom.amount);
      const res = await submitGcashRecharge({
        session_token: this.sessionToken,
        amount: this.gcashFrom.amount,
      });
      // console.log('res ->', res);
      if (res.code == 0) {
        window.open(res.data, "_blank");
        this.$router.push("/userInfo/money-package");
      }
    },
    async gcashPhpReharge() {
      let pageUrl = window.location.origin + "/userInfo/money-package";
      if (
        this.gcash2From.amount >= this.minAmount &&
        this.gcash2From.amount <= this.maxAmount
      ) {
        const res = await submitGcashPhpRecharge({
          session_token: this.sessionToken,
          amount: this.gcash2From.amount,
          pageUrl,
        });
        if (res.code == 0) {
          window.open(res.data, "_blank");
          this.$router.push("/userInfo/money-package");
        }
      }
    },
    async GCashPaySubmit(){
      let pageUrl = window.location.origin + "/userInfo/money-package";
      if (
        this.GCashPayFrom.amount >= this.minAmount &&
        this.GCashPayFrom.amount <= this.maxAmount
      ) {
        const res = await subGcashPay({
          session_token: this.sessionToken,
          amount: this.GCashPayFrom.amount,
          pageUrl,
        });
        if (res.code == 0) {
          window.open(res.data, "_blank");
          this.$router.push("/userInfo/money-package");
        }
      }
    },
    async gcash3PhpReharge(){
      let pageUrl = window.location.origin + "/userInfo/money-package";
      if (
        this.gcash3From.amount >= this.minAmount &&
        this.gcash3From.amount <= this.maxAmount) {
        const res = await gcash3PhpRecharge({
          session_token: this.sessionToken,
          amount: this.gcash3From.amount,
          pageUrl,
        });
        if (res.code == 0) {
          window.open(res.data, "_blank");
          this.$router.push("/userInfo/money-package");
        }
    }
    },
    async mayaPhpReharge(){
      let pageUrl = window.location.origin + "/userInfo/money-package";
      if (
        this.mayaFrom.amount >= this.minAmount &&
        this.mayaFrom.amount <= this.maxAmount) {
        const res = await mayaPhpRecharge({
          session_token: this.sessionToken,
          amount: this.mayaFrom.amount,
          pageUrl,
        });
        if (res.code == 0) {
          window.open(res.data, "_blank");
          this.$router.push("/userInfo/money-package");
        }
     }
    },
    inputHandler(type, e) {
      if (e == "GCash2.0") {
        if (!this.gcash2From.coin) {
          this.$message.error(this.$t("message.home.请先选择币种"));
          this.gcash2From.amount = "";
          return;
        }
        this.gcash2From.amount = this.gcash2From.amount.replace(/[^\d.]/g, ""); // 只保留数字和小数点
        this.gcash2From.amount = this.gcash2From.amount.replace(
          /^(\d+\.?\d{0,2}).*/g,
          "$1"
        );
         if (this.gcash2From.amount >= this.minAmount && this.gcash2From.amount <= this.maxAmount) {
            this.gcashPbtn = false;
          } else {
            this.gcashPbtn = true;
          }
      } else if(e == "Maya"){
        if (!this.mayaFrom.coin) {
          this.$message.error(this.$t("message.home.请先选择币种"));
          this.mayaFrom.amount = "";
          return;
        }
        this.mayaFrom.amount = this.mayaFrom.amount.replace(/[^\d.]/g, ""); // 只保留数字和小数点
        this.mayaFrom.amount = this.mayaFrom.amount.replace(
          /^(\d+\.?\d{0,2}).*/g,
          "$1"
        );
        if (this.mayaFrom.amount >= this.minAmount && this.mayaFrom.amount <= this.maxAmount) {
          // console.log('444 ->', 444);
            this.mayabtn = false;
          } else {
            this.mayabtn = true;
          }
      }else if(e == "GCash3.0"){
        if (!this.gcash3From.coin) {
          this.$message.error(this.$t("message.home.请先选择币种"));
          this.gcash3From.amount = "";
          return;
        }
        this.gcash3From.amount = this.gcash3From.amount.replace(/[^\d.]/g, ""); // 只保留数字和小数点
        this.gcash3From.amount = this.gcash3From.amount.replace(
          /^(\d+\.?\d{0,2}).*/g,
          "$1"
        );
        if (this.gcash3From.amount >= this.minAmount && this.gcash3From.amount <= this.maxAmount) {
            this.gcash3btn = false;
          } else {
            this.gcash3btn = true;
          }
      } else if(e == "GCash pay"){
        if (!this.GCashPayFrom.coin) {
          this.$message.error(this.$t("message.home.请先选择币种"));
          this.GCashPayFrom.amount = "";
          return;
        }
        this.GCashPayFrom.amount = this.GCashPayFrom.amount.replace(/[^\d.]/g, ""); // 只保留数字和小数点
        this.GCashPayFrom.amount = this.GCashPayFrom.amount.replace(
          /^(\d+\.?\d{0,2}).*/g,
          "$1"
        );
        if (this.GCashPayFrom.amount >= this.minAmount && this.GCashPayFrom.amount <= this.maxAmount) {
            this.GCashPayBtn = false;
          } else {
            this.GCashPayBtn = true;
          }
      }else {
        if (type !== "GCash" && e !== "GCash2.0") {
          if (!this.bankForm.frenchCurrency) {
            this.$message.error(this.$t("message.home.请先选择币种"));
            this.bankForm.amount = "";
            return;
          }
          
          this.bankForm.amount = this.bankForm.amount.replace(/[^\d.]/g, ""); // 只保留数字和小数点
          this.bankForm.amount = this.bankForm.amount.replace(
            /^(\d+\.?\d{0,2}).*/g,
            "$1"
          ); // 限制最多两位小数
          if (this.bankForm.amount >= this.minAmount && this.bankForm.amount <= this.maxAmount) {
            this.bankBtn = false;
          } else {
            this.bankBtn = true;
          }
        } else {
          // console.log('222222 ->', 222222);
          this.gcashFrom.amount = this.gcashFrom.amount.replace(/[^\d.]/g, "");
          this.gcashFrom.amount = this.gcashFrom.amount.replace(
            /^(\d+\.?\d{0,2}).*/g,
            "$1"
          );
          if (this.gcashFrom.amount >= this.minAmount && this.gcashFrom.amount <= this.maxAmount) {
            this.gcashbtn = false;
          } else {
            this.gcashbtn = true;
          }
        }
      } 
    },
    quantityGcashPay(){
    if (this.GCashPayFrom.amount > this.maxAmount) {
            this.$message({
              message:
                this.$t("message.home.充值金额不得大于") + this.maxAmount,
              type: "info",
            });

            // this.bankForm.amount = this.maxAmount;
          }
          if (this.GCashPayFrom.amount < this.minAmount) {
            this.$message({
              message:
                this.$t("message.home.充值金额不得小于") + this.minAmount,
              type: "info",
            });
            // this.bankForm.amount = this.minAmount;
          }
    },
    quantityCash() {
      if (this.gcashFrom.amount > this.maxAmount) {
        this.$message({
          message:
            this.$t("message.home.充值金额不得大于") + this.maxAmount,
          type: "info",
        });

        // this.bankForm.amount = this.maxAmount;
      }
      if (this.gcashFrom.amount < this.minAmount) {
        this.$message({
          message:
            this.$t("message.home.充值金额不得小于") + this.minAmount,
          type: "info",
        });
        // this.bankForm.amount = this.minAmount;
      }
    },
    quantityHandler() {
      if (this.bankForm.amount > this.maxAmount) {
        this.$message({
          message: this.$t("message.home.充值金额不得大于") + this.maxAmount,
          type: "info",
        });
        // this.bankForm.amount = this.maxAmount;
      }
      if (this.bankForm.amount < this.minAmount) {
        this.$message({
          message: this.$t("message.home.充值金额不得小于") + this.minAmount,
          type: "info",
        });
        // this.bankForm.amount = this.minAmount;
      }
    },
    quantityGCash() {
      if (this.gcash2From.amount > this.maxAmount) {
        this.$message({
          message: this.$t("message.home.充值金额不得大于") + this.maxAmount,
          type: "info",
        });
        // this.bankForm.amount = this.maxAmount;
      }
      if (this.gcash2From.amount < this.minAmount) {
        this.$message({
          message: this.$t("message.home.充值金额不得小于") + this.minAmount,
          type: "info",
        });
      }
    },
    quantityGCash3 (){
      if (this.gcash3From.amount > this.maxAmount) {
        this.$message({
          message: this.$t("message.home.充值金额不得大于") + this.maxAmount,
          type: "info",
        });
        // this.bankForm.amount = this.maxAmount;
      }
      if (this.gcash3From.amount < this.minAmount) {
        this.$message({
          message: this.$t("message.home.充值金额不得小于") + this.minAmount,
          type: "info",
        });
      }
    },
    quantitymaya(){
      if (this.mayaFrom.amount > this.maxAmount) {
          this.$message({
            message: this.$t("message.home.充值金额不得大于") + this.maxAmount,
            type: "info",
          });
          // this.bankForm.amount = this.maxAmount;
        }
        if (this.mayaFrom.amount < this.minAmount) {
          this.$message({
            message: this.$t("message.home.充值金额不得小于") + this.minAmount,
            type: "info",
          });
        }
    },
    numberFormat,
    openService() {
      this.$message({
            message: this.$t("购买失败,联系客服") ,
            type: "error",
          });

      
      this.showOnlieService = true;
    },
    getcurrency(v) {
        this.currencyList.filter((item) => {
          if (item.bank_code == v) {
            this.maxAmount = item.max_amount;
            this.minAmount = item.min_amount;
          }
        });
    },
    // 银行卡充值
    async bankReharge() {
      if (!this.bankForm.frenchCurrency) {
        this.$message.error(this.$t("message.home.请先选择币种"));
        return;
      }
      if (!this.bankForm.amount) {
        this.$message.error(this.$t("message.home.pleaseEnterAmount"));
        return;
      }
      if (this.bankForm.amount > this.maxAmount) {
        this.$message({
          message: this.$t("message.home.充值金额不得大于") + this.maxAmount,
          type: "info",
        });
        return;
      }
      if (this.bankForm.amount < this.minAmount) {
        this.$message({
          message: this.$t("message.home.充值金额不得小于") + this.minAmount,
          type: "info",
        });
        return;
      }

      const res = await submitBankRechargeApi({
        session_token: this.sessionToken,
        amount: this.bankForm.amount,
        frenchCurrency: this.bankForm.frenchCurrency,
      });
      // console.log('res ->', res);
      if (res.code == 0) {
        window.open(res.data, "_blank");
        this.$router.push("/userInfo/money-package");
      }
    },
    goBack() {
      this.$router.push("/userInfo/money-package");
    },
    async autoSetBlock(block) {
      const resp = await getFeeApi(block.coin);
      if (resp.code === "0" && resp.data?.price) {
        block.fee = resp.data.price;
      }
      this.currentSelectBlock = block;
      this.form.blockId = block.id;
      this.form.address = block.address;
    },
    // session_token&amount=700&frenchCurrency=THB

    async getMoneyType() {
      const res = await getRechargeListApi();
      if (res.code == 0) {
        this.rechageList = res.data
        this.rachargeType = this.rachargeType.concat(this.rechageList);
        // this.currencyList = res.data;
      }
    },
    groupAddress() {
      this.groupBlockAddress = groupBy(this.rechargeAddress, "coin");
      this.getMoneyType();
    },

    copy() {
      if (!emptyStr(this.form.address)) {
        copyTextToClipboard(this.form.address);
        this.$notify({
          title: this.$t("message.home.successTips" /**成功 */),
          message: this.$t("message.home.copySuccess" /**提现成功 */),
          type: "success",
        });
      }
    },
    saveImage() {
      const $$qrImage = document.querySelector("#qrCode img");
      if ($$qrImage) {
        downloadImage($$qrImage.src);
      }
    },
    beforeUpload(file) {
      // const type = [".jpeg", ".png", ".jpg",'.bmp',".JPEG", ".PNG", ".JPG",'.BMP']
      // if (!type.includes(file.type)) {
      //               this.$message.error('请上传正确的图片格式');
      //               return false;
      //           }
      this.$message({
        message: this.$t("message.home.uploading"),
        type: "info",
      });
    },

    onUploadError() {
      this.$message.close();
      this.$message({
        message: this.$t("message.home.uploadError"),
        type: "error",
      });
    },

    onSuccess(response) {
      this.form.image = response.data;
      this.$message.close();
      this.$message({
        message: this.$t("message.home.uploadSuccess"),
        type: "success",
      });
    },
    recharge() {
      this.$refs.rechargeForm.validate(async (valid) => {
        if (valid) {
          let res = await this.requesRecharge({
            session_token: this.sessionToken,
            amount: this.form.quantity,
            from: "123",
            blockchain_name: this.currentSelectBlock.blockchain_name,
            img: this.form.image,
            coin: this.form.coin,
            channel_address: this.form.address,
            tx: "123",
          });

          this.$notify({
            title: this.$t("message.home.successTips"),
            message: this.$t("message.home.withdrawSuccess"),
            type: "success",
          });
          this.$router.push("/userInfo/money-package");
          // this.$emit('input', false)
          // console.log('res ->', res);
        }
      });
    },
  },
};
</script>

<style lang="scss" scoped>
html[dir="rtl"] {
  .el-form-item /deep/ .el-form-item__error {
    right: 0;
    left: auto;
  }
  .info_page_container {
    margin-left: 0;
    margin-right: 34px;
    .wallet-address .copy-btn {
      right: auto;
      left: 15px;
    }
    .qr-btn {
      margin-left: 0;
      margin-right: 20px;
    }
  }
}
.qr-code {
  display: flex;
  flex-direction: row;
  align-items: center;
}
.qr-btn {
  height: 40px;
  margin-left: 20px;
}
.qr-code-wrap {
  width: 150px;
  height: 150px;
  background-color: var(--color-white);
  border: 1px solid var(--color-border);
}

.right {
  cursor: pointer;
}

.image-uploader {
  .el-upload {
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    height: 96px;

    &:hover {
      border-color: #409eff;
    }
  }

  .image {
    width: 96px;
    height: 96px;
    display: block;
  }

  .label {
    width: 93px;
    text-align: center;
    margin-top: -15px;
    font-size: 12px;
    color: #999999;
  }
}

.wallet-address {
  position: relative;

  .copy-btn {
    position: absolute;
    top: 0;
    bottom: 0;
    right: 15px;
    z-index: 1;
    color: #1d91ff;
    user-select: none;
    display: block;
    cursor: pointer;

    &.disabled {
      color: #aaa;
      cursor: default;
    }
  }
}
</style>
