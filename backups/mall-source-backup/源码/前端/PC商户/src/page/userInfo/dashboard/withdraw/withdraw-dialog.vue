<template>
  <el-dialog
    custom-class="wallet-dialog withdraw-dialog"
    :title="$t('message.home.withdraw' /** 提现*/)"
    :center="true"
    :visible.sync="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-form
      ref="withdrawForm"
      label-position="top"
      :model="form"
      :rules="rules"
      v-loading="httpLoading"
    >
      <div class="network-select">
        <div class="right" @click="withdrawRecordVisible = true">
          {{ $t("message.home.records" /**記錄 */) }}
        </div>
        <el-form-item
          :label="$t('message.home.blockchainNetwork' /**区块链网络 */)"
          prop="network"
        >
          <el-radio-group v-model="form.network">
            <el-radio-button
              v-for="item in coinInfo"
              :key="item.blockchain_name"
              :label="item.blockchain_name"
            ></el-radio-button>
          </el-radio-group>
        </el-form-item>
      </div>

      <!-- <div class="qr-code">
        <div id="qrCode" class="qr-code-wrap flex-center">
          <VueQr :size="132" :text="form.address" :margin="0" />
        </div>

        <el-button @click="saveImage">Save QR Code</el-button>
      </div> -->

      <el-form-item
        :label="$t('message.home.withdrawAddress' /**提现地址 */)"
        class="wallet-address"
        prop="address"
      >
        <el-input
          v-model="form.address"
          :placeholder="
            $t('message.home.withdrawInputTips' /** 请输入提币地址*/)
          "
        />
        <span
          :class="{
            'copy-btn': true,
            disabled: isDisabled,
          }"
          @click="copy"
        >
          {{ $t("message.home.copy" /**复制 */) }}
        </span>
      </el-form-item>

      <el-form-item :label="$t('message.home.quantity')" prop="quantity">
        <el-input
          v-model="form.quantity"
          maxlength="10"
          :disabled="userBalance < 1"
          :placeholder="$t('message.home.enterTips')"
        />
      </el-form-item>

      <el-form-item>
        <div class="withdraw-tips flex-between">
          <span>
            {{ $t("message.home.ActualLedger" /**实际账户 */) }}:
            {{ numberFormat(form.arrival) }}
          </span>
          <span>
            {{ $t("message.home.handlingFee" /**手续费 */) }}:
            {{ numberFormat(getRealWithdrawFee) }}%
          </span>
        </div>
      </el-form-item>

      <el-form-item>
        <el-button class="submit-btn" @click="withdraw">
          {{ $t("message.home.confirm" /**确认 */) }}
        </el-button>
      </el-form-item>
    </el-form>
    <EsPayModal
      v-model="payModalShow"
      :payCallback="payCallback"
      :payLoading="btnLoading"
    />
    <EsWidthdrawRecordDialog v-model="withdrawRecordVisible" />
  </el-dialog>
</template>

<script>
  import { mapGetters, mapActions } from "vuex";
  import EsPayModal from "@/page/settlementPage/payModal";
  import EsWidthdrawRecordDialog from "./widthdrawRecordDialog";
  import common from "@/util/common";
  import { copyTextToClipboard, emptyStr, numberFormat } from "@/util";
  import { accTimes, accMinus } from "@/util/math";
  export default {
    name: "withdraw-dialog",
    components: { EsPayModal, EsWidthdrawRecordDialog },
    props: {
      value: {
        type: Boolean,
        default: false,
      },
      currentCoin: {
        type: String,
        default: "",
      },
    },
    data() {
      return {
        dialogVisible: this.value || false,
        form: {
          network: "",
          address: "",
          quantity: "",
          arrival: 0,
        },
        rules: {
          address: [
            common.ruleUtils.getRule("cionAddress"),
            common.ruleUtils.getRule(
              "required",
              this.$t("message.home.pleaseEnterAddress")
            ),
          ],
          quantity: [
            common.ruleUtils.getRule(
              "required",
              this.$t("message.home.pleaseEnterQuantity")
            ),
            common.ruleUtils.getRule("decimalExceedZero"),
            common.ruleUtils.getRule("validator", "", {
              validator: (rule, value, callback) => {
                const max = this.userBalance ? this.userBalance : 10e8;
                if (Number(value) > max) {
                  callback(this.$t("message.home.validatorMaxNumber"));
                }
                callback();
              },
            }),
          ],
        },
        currentSelectBlock: {},
        coinInfo: [],
        payModalShow: false,
        withdrawRecordVisible: false,
        count: 0,
      };
    },
    watch: {
      value(val) {
        if (!val) {
          this.form = {
            network: "",
            address: "",
            quantity: "",
            arrival: 0,
          };
        }
        this.dialogVisible = val;
      },
      dialogVisible(val) {
        if (val !== this.value) {
          this.$emit("input", val);
        }
        if (val) {
          this.requestWithdrawFee();
          this.requestSessionToken();
          this.requestChannelAddress();
          // 提现只支持USDT
          const data = this.rechargeAddress.filter(
            (item) => item.coin === "USDT"
          );
          if (data && data.length) {
            this.form.network = data[0].blockchain_name;
          }
          this.coinInfo = [...data];
        } else {
          this.$refs.withdrawForm?.resetFields();
        }
      },
      "form.network": {
        handler(newValue, oldValue) {
          if (newValue !== oldValue) {
            const data = this.rechargeAddress.find(
              (item) => item.blockchain_name === newValue
            );
            if (data) {
              this.form.address = "";
              this.form.quantity = "";
              this.form.arrival = 0;
              this.currentSelectBlock = { ...data };
            }
          }
        },
        immediate: true,
      },
      "form.quantity": {
        handler(newValue, oldValue) {
          if (newValue !== oldValue) {
            const amount = accTimes(
              newValue,
              accMinus(1, this.withdrawFee ?? 0)
            )?.toFixed(1);
            this.form.arrival = isNaN(amount) ? "" : amount;
          }
        },
      },
    },
    computed: {
      ...mapGetters("user", ["userBalance"]),
      ...mapGetters("withdraw", [
        "sessionToken",
        "httpLoading",
        "btnLoading",
        "withdrawFee",
      ]),
      rechargeAddress() {
        return this.$store.state.recharge.rechargeAddress.filter(
          (item) => item.coin === "USDT"
        );
      },
      getRealWithdrawFee() {
        return this.withdrawFee ? this.withdrawFee * 100 : 0;
      },
      isDisabled() {
        return emptyStr(this.form.address);
      },
    },
    methods: {
      ...mapActions("withdraw", [
        "requestSessionToken",
        "requesWithdraw",
        "requestWithdrawFee",
      ]),
      numberFormat,
      requestChannelAddress() {
        return this.$store.dispatch("recharge/requestRechargeAddress");
      },
      selectCurrency(val) {
        this.$emit("select-currency", val);
        this.dialogVisible = false;
      },
      copy() {
        if (!emptyStr(this.form.address)) {
          copyTextToClipboard(this.form.address);
          this.$notify({
            title: this.$t("message.home.successTips"),
            message: this.$t("message.home.copySuccess"),
            type: "success",
          });
        }
        // else {
        //     this.$notify({
        //         title: this.$t('message.home.fail' /**成功 */),
        //         message: this.$t('message.home.pleaseEnterAddress' /**提现成功 */),
        //         type: 'error',
        //     })
        // }
      },
      async payCallback(password, successCallBack, failCallBack) {
        this.password = password;

        this.requesWithdraw({
          session_token: this.sessionToken,
          amount: this.form.quantity,
          from: this.form.address,
          channel: "USDT",
          safeword: this.password,
        })
          .then((res) => {
            console.log(res);
            this.$notify({
              title: this.$t("message.home.successTips" /**成功 */),
              message: this.$t("message.home.withdrawSuccess" /**提现成功 */),
              type: "success",
            });
            this.$emit("input", false);
            successCallBack && successCallBack();
          })
          .catch((err) => {
            failCallBack && failCallBack();
          });
      },
      withdraw() {
        this.$refs.withdrawForm.validate(async (valid) => {
          if (valid) {
            this.payModalShow = true;
          }
        });
      },
    },
  };
</script>

<style lang="scss" scoped>
  .withdraw-dialog {
    .info {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 27px;
      font-size: 12px;

      .price {
        color: var(--color-main);
      }
    }

    .withdraw-tips {
      span:first-child {
        font-weight: 400;
        font-size: 12px;
        color: var(--color-subtitle);
      }

      span:last-child {
        font-weight: 400;
        font-size: 12px;
        color: var(--color-main);
      }
    }
  }

  .right {
    cursor: pointer;
  }
</style>
