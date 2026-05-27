<template>
  <div class="app-container box">
    <el-form
      ref="form"
      :model="form"
      label-width="100%"
      label-position="top"
      :rules="rules"
    >
      <div class="title">{{ $t("message.home.businessloan") }}</div>
      <el-form-item :label="$t('message.home.applicant')" prop="name">
        <el-input
          v-model="form.name"
          :placeholder="
            $t('message.home.enterTips') + $t('message.home.actualName')
          "
        ></el-input>
      </el-form-item>
      <el-form-item :label="$t('message.home.term')" prop="term">
        <el-select
          v-model="form.term"
          :placeholder="$t('message.home.selectPeriod')"
          @change="changeLendable(form.term)"
        >
          <el-option
            v-for="item in lendableDays"
            :key="item.label"
            :value="item.value"
            :label="item.label + $t('message.home.days')"
          >
            <span :style="item.dis && { color: '#999' }"
              >{{ item.label }}{{ $t("message.home.days") }}</span
            >
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item :label="$t('message.home.applicationAmount')" prop="money">
        <el-input
          v-model="form.money"
          :placeholder="maxAmount"
          type="number"
          oninput="value=parseInt(value.replace(/[^\d]/g,''))"
          @input="handleInput"
          @change="handleChange"
        ></el-input>
      </el-form-item>
      <el-form-item :label="$t('message.home.rates')">
        <el-input
          v-model="form.interest"
          :placeholder="rate * 100 + '%'"
          disabled
        ></el-input>
      </el-form-item>
      <el-form-item :label="$t('message.home.collAccount')">
        <el-input
          :placeholder="$t('message.home.accountBalance')"
          disabled
        ></el-input>
      </el-form-item>
      <el-form-item :label="$t('message.home.countryOf')" prop="country">
        <el-select
          v-model="form.country"
          :placeholder="$t('message.home.selectCountry')"
          filterable
        >
          <el-option
            v-for="item in countryList"
            :key="item.id"
            :value="item.id"
            :label="item.countryName"
          >
            <span>{{ countryName || item.countryName }}</span>
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item
        :label="$t('message.home.passPortImg')"
        prop="identification"
      >
        <el-input
          v-model="form.identification"
          @input="identification"
          :placeholder="
            $t('message.home.enterTips') + $t('message.home.passPortImg')
          "
        ></el-input>
      </el-form-item>
      <el-form-item :label="$t('message.home.uploadId')" prop="img">
        <div class="file">
          <div class="item image-uploader">
            <el-upload
              :action="UploadApi"
              :show-file-list="false"
              :on-success="handlePictureCardPreview"
              :data="uploadParams"
              :before-upload="beforeUpload"
              accept=".jpg,.jpeg,.png,.bmp,.pdf,.JPG,.JPEG,.PBG,.BMP,.PDF"
            >
              <img
                v-if="form.dialogImageUrl1"
                :src="form.dialogImageUrl1"
                class="image"
                alt="image"
              />
              <img v-else src="@/assets/image/camera.png" alt="camera" />
            </el-upload>
          </div>
          <div class="item image-uploader">
            <el-upload
              :action="UploadApi"
              :show-file-list="false"
              :on-success="handlePictureCardPreview1"
              :data="uploadParams"
              :before-upload="beforeUpload"
              accept=".jpg,.jpeg,.png,.bmp,.pdf,.JPG,.JPEG,.PBG,.BMP,.PDF"
            >
              <img
                v-if="form.dialogImageUrl2"
                :src="form.dialogImageUrl2"
                class="image"
                alt="image"
              />
              <img v-else src="@/assets/image/camera.png" alt="camera" />
            </el-upload>
          </div>
          <div class="item image-uploader" v-if="itemname !== 'Inchoi' && itemname !== 'Hive'">
            <el-upload
              :action="UploadApi"
              :show-file-list="false"
              :on-success="handlePictureCardPreview2"
              :data="uploadParams"
              :before-upload="beforeUpload"
              accept=".jpg,.jpeg,.png,.bmp,.pdf,.JPG,.JPEG,.PBG,.BMP,.PDF"
            >
              <img
                v-if="form.dialogImageUrl3"
                :src="form.dialogImageUrl3"
                class="image"
                alt="image"
              />
              <img v-else src="@/assets/image/camera.png" alt="camera" />
            </el-upload>
          </div>
        </div>
      </el-form-item>
      <el-form-item :label="$t('message.home.photoExample')">
        <div class="example">
          <div class="item">
            <div class="item-img">
              <img src="@/assets/image/01.png" />
            </div>
            <div class="icon">
              <img src="@/assets/image/gou.png" alt="" />
            </div>
          </div>
          <div class="item">
            <div class="item-img">
              <img src="@/assets/image/02.png" />
            </div>
            <div class="icon">
              <img src="@/assets/image/gou.png" alt="" />
            </div>
          </div>
          <div class="item" v-if="itemname !== 'Inchoi' && itemname !== 'Hive'">
            <div class="item-img">
              <img src="@/assets/image/03.png" />
            </div>
            <div class="icon">
              <img src="@/assets/image/gou.png" alt="" />
            </div>
          </div>
        </div>
      </el-form-item>
      <el-form-item>
        <el-checkbox v-model="form.radio">
          {{ $t("message.home.readAndAgree")
          }}<span class="protocol" @click="goAgree"
            >《{{ $t("message.home.loanAgree") }}》</span
          >
        </el-checkbox>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSubmit">{{
          $t("message.home.submitApplica")
        }}</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { apiListCountry } from "@/api/userCenter";
import { Application, creditConfig, beforereapply } from "@/api/credit";
import { UploadApi } from "@/api";
export default {
  data() {
    return {
      form: {
        name: "",
        money: "",
        term: "",
        interest: "",
        country: "",
        identification: "",
        dialogImageUrl1: "",
        dialogImageUrl2: "",
        dialogImageUrl3: "",
        radio: false,
      },
      itemname: process.env.VUE_APP_ITEM_NAME,
      maxAmount: 0,
      rate: 0,
      lendableDays: [],
      lendableDay: [],
      maxnum: 0,
      minnum: 0,
      dialogVisible1: false,
      dialogVisible2: false,
      dialogVisible3: false,
      creditid: 0,
      countryList: [],
      UploadApi,
      countryName: "",
      uploadParams: {
        moduleName: "selle",
        token: localStorage.getItem("ES_TOKEN"),
      },
      rules: {
        // name: {
        //   required: true,
        //   message: this.$t("message.home.yourName"),
        //   trigger: "blur",
        // },
        name: [
                  { required: true, message: this.$t("message.home.yourName"), trigger: 'blur'},
                  { pattern: /^(?!\s+).*(?<!\s)$/,  message: this.$t("message.home.yourName"), trigger: 'blur' }
            ],
        money: {
          required: true,
          message:
            this.$t("message.home.pleaseInput") +
            this.$t("message.home.applicationAmount"),
          trigger: "blur",
        },
        term: {
          required: true,
          message: this.$t("message.home.selectPeriod"),
          trigger: "change",
        },
        country: {
          required: true,
          message: this.$t("message.home.selectCountry"),
          trigger: "change",
        },
        identification: {
          required: true,
          message:
            this.$t("message.home.pleaseInput") +
            this.$t("message.home.passPortImg"),
          trigger: "blur",
        },
      },
    };
  },
  mounted() {
    this.getCountry();
    if (this.$route.query.id) {
      this.creditid = this.$route.query.id;
      this.reapply(this.creditid);
    }
  },
  methods: {
    changeLendable(val) {
      // console.log('this.lendableDays ->', this.lendableDays);
      let temp = this.lendableDays.find((x) => x.value == val);
      // console.log('temp ->', temp);
      if (temp.dis) {
        this.$message({
          message: this.$t("message.home.notQua"),
        });
        this.form.term = "";
      }
    },
    handleInput() {
      if (this.form.money > this.maxnum) {
        this.form.money = this.maxnum;
        this.$message({
          message: this.$t("message.home.nomax") + this.maxnum,
        });
      } else if (this.form.money < 1) {
        this.form.money = "";
      }
    },
    // 申请金额不能小于最小值
    handleChange() {
      if (this.form.money < this.minnum) {
        this.form.money = "";
        this.$message({
          message: this.$t("message.home.noSmaller") + this.minnum,
          type: "warning",
        });
      }
    },
    async reapply(id) {
      let res = await beforereapply({ creditId: id });
      this.form.name = res.data.realName;
      this.form.term = res.data.creditPeriod;
      this.form.money = res.data.applyAmount;
      this.form.interest = res.data.creditRate * 100 + "%";
      this.form.identification = res.data.identification;
      this.form.dialogImageUrl1 = res.data.imgCertificateBack;
      this.form.dialogImageUrl2 = res.data.imgCertificateFace;
      if (this.itemname !== "Inchoi") {
        this.form.dialogImageUrl3 = res.data.imgCertificateHand;
      }

      let a = this.countryList.filter(
        (item) => item.id == res.data.countryId
      )[0];

      for (let u in a) {
        if (u == "id") {
          this.form.country = a[u];
        }
      }
    },
    identification(val) {
      let codeReg = new RegExp("[A-Za-z0-9]+"), //正则 英文+数字；
        len = val.length,
        str = "";
      for (var i = 0; i < len; i++) {
        if (codeReg.test(val[i])) {
          str += val[i];
        }
      }
      this.form.identification = str;
    },
    onSubmit() {
      let data = {
        realName: this.form.name,
        creditPeriod: this.form.term,
        applyAmount: this.form.money,
        countryId: this.form.country,
        identification: this.form.identification,
        imgCertificateFace: this.form.dialogImageUrl1,
        imgCertificateBack: this.form.dialogImageUrl2,
        imgCertificateHand: this.form.dialogImageUrl3,
        creditId: this.creditid || "",
      };
      if (!this.form.name.trim()) {
        this.$message({
          message: this.$t("message.home.yourName"),
          type: "warning",
        });
      } else if (!this.form.term) {
        this.$message({
          message: this.$t("message.home.selectPeriod"),
          type: "warning",
        });
      } else if (!this.form.money) {
        this.$message({
          message:
            this.$t("message.home.pleaseInput") +
            this.$t("message.home.applicationAmount"),
          type: "warning",
        });
      } else if (!this.form.country) {
        this.$message({
          message: this.$t("message.home.selectCountry"),
          type: "warning",
        });
      } else if (!this.form.identification) {
        this.$message({
          message:
            this.$t("message.home.pleaseInput") +
            this.$t("message.home.passPortImg"),
          type: "warning",
        });
      } else if (!this.form.dialogImageUrl1) {
        this.$message({
          message: this.$t("message.home.uploadPhoto"),
          type: "warning",
        });
      } else if (!this.form.dialogImageUrl2) {
        this.$message({
          message: this.$t("message.home.uploadPhoto"),
          type: "warning",
        });
      } else if (this.itemname !== "Inchoi") {
        if (!this.form.dialogImageUrl3) {
          this.$message({
            message: this.$t("message.home.uploadPhoto"),
            type: "warning",
          });
        } else if (!this.form.radio) {
          this.$message({
            message: this.$t("message.home.checkAgreement"),
            type: "warning",
          });
        }else {
          this.creditApply(data);
        }
      } else if (!this.form.radio) {
        this.$message({
          message: this.$t("message.home.checkAgreement"),
          type: "warning",
        });
      } else {
        this.creditApply(data);
      }
    },
    async creditApply(data) {
      const res = await Application(data);
      if (res.code == "0") {
        this.$message({
          message: this.$t("message.home.returnOrderSuccess"),
          type: "success",
        });
        this.$router.push("/credit");
      }
    },
    goAgree() {
      window.open(window.origin + "/promote/#/contract", "_blank");
    },
    async getCountry() {
      const result = await apiListCountry();
      this.countryList = result.data?.data || [];
      let res = await creditConfig();
      this.maxAmount = res.data.amountMin + "-" + res.data.amountMax;
      this.maxnum = res.data.amountMax;
      this.minnum = res.data.amountMin;
      this.rate = res.data.rate;
      this.lendableDay = res.data.lendableDays;
      res.data.allLendableDays.forEach((x) => {
        res.data.lendableDays.forEach((y) => {
          this.lendableDays.push({
            label: x,
            value: x,
            dis: x !== y,
          });
        });
      });
      this.lendableDays = this.deduplication(this.lendableDays, "value");
      this.lendableDays.forEach((x) => {
        res.data.lendableDays.forEach((y) => {
          if (x.value == y) {
            x.dis = false;
          }
        });
      });
    },
    deduplication(arr, name) {
      const obj = {};
      return arr.reduce((prev, cur) => {
        obj[cur[name]] ? "" : (obj[cur[name]] = true && prev.push(cur));
        return prev;
      }, []);
    },
    beforeUpload(file) {
      this.$message({
        message: this.$t("message.home.uploading"),
        type: "info",
      });
    },
    handlePictureCardPreview(res) {
      this.$message.close();
      this.$message({
        message: this.$t("message.home.uploadSuccess"),
        type: "success",
      });
      this.form.dialogImageUrl1 = res.data;
    },
    handlePictureCardPreview1(res) {
      this.$message.close();
      this.$message({
        message: this.$t("message.home.uploadSuccess"),
        type: "success",
      });
      this.form.dialogImageUrl2 = res.data;
    },
    handlePictureCardPreview2(res) {
      this.$message.close();
      this.$message({
        message: this.$t("message.home.uploadSuccess"),
        type: "success",
      });
      this.form.dialogImageUrl3 = res.data;
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
  .el-select-dropdown__item{
    margin-right: 15px;
  }
}
.box {
  width: 1037px;
  padding: 26px 35px;
  border: 1px solid #eeeeee;
  margin: 0 auto;
  margin-bottom: 25px;
  /deep/.el-input__inner {
    width: 480px;
  }
  .title {
    font-size: 14px;
    color: #333333;
    margin-bottom: 20px;
  }
  .file {
    display: flex;
    .image-uploader {
      margin-right: 15px;
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
  }
  .protocol {
    color: var(--color-main);
  }
  .example {
    display: flex;
    .item {
      display: flex;
      margin-right: 23px;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      .item-img {
        width: 99px;
        height: 64px;
      }
      img {
        width: 100%;
        height: 100%;
      }
      .icon {
        margin-top: 16px;
        width: 19px;
        height: 19px;
      }
    }
  }
}
/deep/ input[type="number"]::-webkit-inner-spin-button,
/deep/ input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
/deep/ input[type="number"] {
  -moz-appearance: textfield;
}
</style>
