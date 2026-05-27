<template>
  <el-dialog
    custom-class="wallet-dialog"
    :title="$t('message.home.recharge')"
    :visible.sync="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-form
      ref="rechargeForm"
      label-position="top"
      :model="form"
      :rules="rules"
      v-loading="httpLoading"
    >
      <div class="network-select">
        <div class="right" @click="rechargeRecordVisible = true">
          {{ $t("message.home.records") }}
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

      <div class="qr-code">
        <div id="qrCode" class="qr-code-wrap flex-center">
          <VueQr :size="132" :text="form.address" :margin="0" />
        </div>

        <!-- <img src="@/assets/image/qrcode.svg" alt="qrcode" /> -->
        <el-button @click="saveImage">
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
          maxlength="10"
          :placeholder="$t('message.home.pleaseEnterAmount')"
        />
      </el-form-item>

      <el-form-item
        :label="`${$t('message.home.expectedArrival')}(${$t(
          'message.home.currentRate'
        )}1:${currentSelectBlock.fee})`"
      >
        <el-input
          v-model="form.arrival"
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
          :on-progress="onProgress"
          :on-error="onUploadError"
          :before-upload="beforeUpload"
          :on-success="onSuccess"
          :data="uploadParams"
        >
          <img v-if="form.image" :src="form.image" class="image" alt="image" />
          <img v-else src="@/assets/image/camera.png" alt="camera" />
        </el-upload>
        <div class="label">{{ $t("message.home.clickUpload") }}</div>
      </el-form-item>

      <el-form-item>
        <el-button class="submit-btn" :loading="btnLoading" @click="recharge">
          {{ $t("message.home.confirm") }}
        </el-button>
      </el-form-item>
    </el-form>
    <EsRechargeRecordDialog v-model="rechargeRecordVisible" />
  </el-dialog>
</template>

<script>
  import { mapActions, mapGetters } from "vuex";
  import VueQr from "vue-qr";
  import { copyTextToClipboard, downloadImage, emptyStr } from "@/util";
  import { UploadApi, getFeeApi } from "@/api";
  import { ES_TOKEN } from "@/common";
  import common from "@/util/common";
  import EsRechargeRecordDialog from "./rechargeRecordDialog";

  export default {
    name: "recharge-dialog",
    components: { VueQr, EsRechargeRecordDialog },
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
        rechargeRecordVisible: false,
        selected: "balance",
        form: {
          network: "",
          address: "",
          quantity: "",
          arrival: "",
          image: "",
        },
        rules: {
          quantity: [
            common.ruleUtils.getRule(
              "required",
              this.$t("message.home.pleaseEnterQuantity")
            ),
            common.ruleUtils.getRule("decimalExceedZero"),
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
        currentSelectBlock: {},
        coinInfo: [],
        UploadApi,
        uploadParams: {
          moduleName: "recharge",
          token: localStorage.getItem(ES_TOKEN),
        },
      };
    },
    watch: {
      value(val) {
        if (!val) {
          this.form = {
            network: "",
            address: "",
            quantity: "",
            arrival: "",
            image: "",
          };
        }
        this.dialogVisible = val;
      },
      dialogVisible(val) {
        if (val !== this.value) {
          this.$emit("input", val);
        }
        if (val) {
          this.requestSessionToken();
          const data = this.rechargeAddress.filter(
            (item) => item.coin === this.currentCoin
          );
          if (data && data.length) {
            this.form.network = data[0].blockchain_name;
          }
          this.coinInfo = [...data];
        } else {
          this.$refs.rechargeForm?.resetFields();
        }
      },
      "form.network": {
        handler(newValue, oldValue) {
          if (newValue !== oldValue) {
            const data = this.rechargeAddress.find(
              (item) => item.blockchain_name === newValue
            );
            // console.log(data)
            if (data) {
              this.form.address = data.address;
              this.form.quantity = "";
              this.form.arrival = 0;
              this.currentSelectBlock = { ...data };
              this.getAutoFee(data.coin);
            }
          }
        },
        immediate: true,
      },
      "form.quantity": {
        handler(newValue, oldValue) {
          if (newValue !== oldValue) {
            this.form.arrival = (
              newValue * this.currentSelectBlock.fee
            ).toFixed(2);
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
    },
    methods: {
      ...mapActions("recharge", [
        "requestSessionToken",
        "requesRecharge",
        "requestRechargeAddress",
      ]),

      async getAutoFee(coin) {
        const resp = await getFeeApi(coin);
        if (resp.code === "0" && resp.data?.price) {
          this.currentSelectBlock.fee = resp.data.price;
        }
      },

      selectCurrency(val) {
        this.$emit("select-currency", val);
        this.dialogVisible = false;
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
        this.$message({
          message: this.$t("message.home.uploading"),
          type: "info",
          // duration:0,
        });
      },
      onProgress() {
        // this.$message({
        //     message:this.$t('message.home.uploading'),
        //     type:"info",
        //     duration:0,
        // })
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
            await this.requesRecharge({
              session_token: this.sessionToken,
              amount: this.form.quantity,
              from: "123",
              blockchain_name: this.form.network,
              img: this.form.image,
              coin: this.currentCoin,
              channel_address: this.form.address,
              tx: "123",
            });
            this.$notify({
              title: this.$t("message.home.successTips"),
              message: this.$t("message.home.withdrawSuccess"),
              type: "success",
            });
            this.$emit("input", false);
          }
        });
      },
    },
  };
</script>

<style lang="scss" scoped>
  .qr-code-wrap {
    width: 150px;
    height: 150px;
    background-color: var(--color-white);
    border: 1px solid var(--color-border);
  }

  .right {
    cursor: pointer;
  }
</style>
