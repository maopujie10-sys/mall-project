<template>
  <el-dialog
    custom-class="es-dialog"
    :visible.sync="dialogVisible"
    :center="true"
    :close-on-press-escape="false"
    :close-on-click-modal="false"
    :append-to-body="true"
    :destroy-on-close="true"
    width="600px"
  >
    <div slot="title" class="dialog-title">
      <span
        >{{ $t("message.home.addAddress") }}/{{
          $t("message.home.modifyAddress")
        }}</span
      >
    </div>
    <div class="add-address-content">
      <el-form :model="infoModel" :rules="rules" ref="addressForm">
        <el-form-item prop="contacts">
          <el-input
            v-model="infoModel.contacts"
            :placeholder="$t('message.home.consigneeName')"
            :maxlength="64"
          />
        </el-form-item>
        <el-form-item prop="email">
          <el-input
            v-model="infoModel.email"
            :placeholder="$t('message.home.orderEmail')"
            :maxlength="64"
          />
        </el-form-item>
        <el-form-item prop="phone">
          <div class="form-phone">
            <el-input
              v-model="infoModel.phone"
              :placeholder="$t('message.home.pleaseSetMobileNumber')"
              :maxlength="20"
            ></el-input>
            <VueCountryIntl
              v-model="infoModel.areaCode"
              schema="popover"
              :searchInputPlaceholder="$t('message.home.pleaseSetAreaCode')"
              noDataText="No data found"
            >
              <div class="area-code flex-between" slot="reference">
                <span>+{{ infoModel.areaCode || "" }}</span>
                <i class="el-icon-caret-bottom"></i>
              </div>
            </VueCountryIntl>
          </div>
        </el-form-item>
        <div class="check_address">
          <el-form-item prop="country">
            <el-select
              v-model="infoModel.country"
              :placeholder="$t('message.home.nation')"
              filterable
              @focus="getCountryList()"
            >
              <el-option
                v-for="item in countryList"
                :key="item.id"
                :value="item.id"
                :label="item.countryName"
              >
                <span>{{ item.countryName }}</span>
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item>
            <div class="prov-city" >
              <div v-if="prov && editC">{{ prov }}</div>
              <div v-if="itemCity && editC">{{ itemCity }}</div>
            </div>
          </el-form-item>
          <el-form-item prop="province" v-if="!editC && isProvince">
            <el-select
              v-model="infoModel.province"
              :placeholder="$t('message.home.state')"
              filterable
            >
              <el-option
                v-for="item in provinces"
                :key="item.id"
                :label="item.stateName"
                :value="item.id"
              >
                <span style="float: left">{{ item.stateName }}</span>
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item prop="city" v-if="!editC && isCity">
            <el-select
              v-model="infoModel.city"
              :placeholder="$t('message.home.city')"
              filterable
            >
              <el-option
                v-for="item in cities"
                :key="item.id"
                :label="item.cityName"
                :value="item.id"
              >
                <span style="float: left">{{ item.cityName }}</span>
                <!-- <span style="float: right; color: #8492a6; font-size: 13px">{{
                  item.value
                }}</span> -->
              </el-option>
            </el-select>
          </el-form-item>
        </div>
        <el-form-item prop="postcode">
          <el-input
            v-model="infoModel.postcode"
            :placeholder="$t('message.home.postCode')"
            :maxlength="32"
          />
        </el-form-item>
        <el-form-item prop="address">
          <el-input
            v-model="infoModel.address"
            :placeholder="$t('message.home.address')"
            type="textarea"
            :rows="4"
            :maxlength="255"
          />
        </el-form-item>
        <el-form-item>
          <div class="flex-between">
            <span>{{ $t("message.home.desc") }}</span>
            <el-switch
              v-model="infoModel.use"
              active-color="var(--color-main)"
              inactive-color="#ECECEC"
              :active-value="1"
              :inactive-value="0"
            ></el-switch>
          </div>
        </el-form-item>
        <el-form-item>
          <div class="submit-btn flex-center">
            <el-button type="primary" :loading="loading" @click="add">
              {{ $t("message.home.btnSure") }}
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </div>
  </el-dialog>
</template>

<script>
import { mapActions } from "vuex";
import VueCountryIntl from "vue-country-intl";
import common from "@/util/common";
import "vue-country-intl/lib/vue-country-intl.css";
import { apiListCountry, apiListState, apiListCity } from "@/api/userCenter";
import { BASE_AREA_CODE } from "@/common";
export default {
  name: "EsAddress",
  components: { VueCountryIntl },
  props: {
    show: {
      type: Boolean,
      default: false,
    },
    data: {
      type: Object,
      default: () => {},
    },
    isEdit: {
      type: Boolean,
      default: false,
    },
    prov: {
      type: String,
      default: "",
    },
    itemCity: {
      type: String,
      default: "",
    },
  },
  model: {
    prop: "show",
    event: "update",
  },
  data() {
    return {
      changeCounty: false,
      dialogVisible: false,
      infoModel: {
        contacts: "",
        email: "",
        phone: "",
        postcode: "",
        country: "",
        province: "",
        city: "",
        address: "",
        use: 1,
        areaCode: BASE_AREA_CODE,
      },
      isProvince: true,
      isCity: true,
      editC: false,
      countryList: [],
      cities: [],
      provinces: [],
      value: "",
      rules: {
        contacts: [
          common.ruleUtils.getRule(
            "required",
            `${this.$t("message.home.pleaseInput")}${this.$t(
              "message.home.consigneeName"
            )}`
          ),
        ],
        email: [
          common.ruleUtils.getRule(
            "required",
            `${this.$t("message.home.pleaseInput")}${this.$t(
              "message.home.orderEmail"
            )}`
          ),
          common.ruleUtils.getRule("email"),
        ],
        phone: [
          common.ruleUtils.getRule(
            "required",
            `${this.$t("message.home.pleaseSetMobileNumber")}`
          ),
          common.ruleUtils.getRule("phone"),
        ],
        areaCode: [
          common.ruleUtils.getRule(
            "required",
            `${this.$t("message.home.pleaseInput")}${this.$t(
              "message.home.pleaseSetAreaCode"
            )}`
          ),
        ],
        country: [
          common.ruleUtils.getRule(
            "required",
            `${this.$t("message.home.pleaseInput")}${this.$t(
              "message.home.nation"
            )}`
          ),
        ],
        province: [
          common.ruleUtils.getRule(
            "required",
            `${this.$t("message.home.pleaseInput")}${this.$t(
              "message.home.state"
            )}`
          ),
        ],
        city: [
          common.ruleUtils.getRule(
            "required",
            `${this.$t("message.home.pleaseInput")}${this.$t(
              "message.home.city"
            )}`
          ),
        ],
        postcode: [
          common.ruleUtils.getRule(
            "required",
            `${this.$t("message.home.pleaseInput")}${this.$t(
              "message.home.postCode"
            )}`
          ),
          common.ruleUtils.getRule("fourMoreNumber"),
        ],
        address: [
          common.ruleUtils.getRule(
            "required",
            `${this.$t("message.home.pleaseInput")}${this.$t(
              "message.home.address"
            )}`
          ),
        ],
      },
      loading: false,
    };
  },
  watch: {
    dialogVisible(newValue, oldValue) {
      if (newValue !== oldValue) this.$emit("update", newValue);
    },
    show(newValue, oldValue) {
      if (newValue !== oldValue) this.dialogVisible = newValue;
      if (!newValue) {
        for (const key in this.infoModel) {
          if (key === "use") {
            this.infoModel[key] = 0;
          } else if (key === "areaCode") {
            this.infoModel[key] = BASE_AREA_CODE;
          } else {
            this.infoModel[key] = "";
          }
        }
      }
    },
    data: {
      handler(newValue, oldValue) {
        if (newValue && Object.keys(newValue)) {
          if (newValue.phone) {
            let phoneArr = newValue.phone.split(" ");
            this.infoModel = {
              ...newValue,
              ...{ phone: phoneArr[1], areaCode: phoneArr[0] },
            };
          } else {
            this.infoModel = {
              ...newValue,
            };
          }
        }
      },
      immediate: true,
    },
    "infoModel.country": {
      handler(newValue, oldValue) {
        this.infoModel.province = "";
        this.getProvinceList(newValue);
      },
    },
    "infoModel.province": {
      handler(newValue, oldValue) {
        this.provinces.length > 0 && (this.infoModel.city = "");
        if (this.infoModel.province) {
          this.getCityList(newValue);
        }
      },
    },
  },
  created() {
    // this.getCountry();
  },
  mounted() {
    this.dialogVisible = this.show;
    // console.log('this.isEdit ->', this.isEdit);
    if (!this.infoModel) {
      this.getCountry();
    }
    this.editC = this.isEdit
  },
  methods: {
    ...mapActions("user", ["requestAddressAdd", "requestAddressEdit"]),
    async getCountry() {
      this.changeCounty = true;
      
      // this.isEdit = false
      this.editC = false
      this.isCity = false
      const result = await apiListCountry();
      this.countryList = result.data?.data || [];
      // console.log("this.countryList ->", this.countryList);
    },
    getCountryList() {
      if (this.countryList.length == 0) {
        this.getCountry();
      }
    },
    async getProvinceList(id) {
      this.infoModel.city = "";
      const res = await apiListState({ countryId: id });
      this.provinces = res.data?.data || [];
      this.cities = [];
      this.isProvince = true;
      this.isCity = true;
      if (this.provinces.length == 0) {
        this.isProvince = false;
        this.isCity = false;
      }
    },
    async getCityList(id) {
      // console.log('-------------', id)
      if (id) {
        const res = await apiListCity({ stateId: id });
        this.cities = res.data?.data || [];
        this.isCity = true;
      }

      if (this.cities.length == 0) {
        this.isCity = false;
      }
    },
    add() {
      this.$refs.addressForm.validate(async (valid) => {
        this.infoModel.contacts = encodeURIComponent(this.infoModel.contacts);
        if (valid) {
          try {
            this.loading = true;
            const params = {
              ...this.infoModel,
              countryId: this.countryList.find(
                (x) => x.id == this.infoModel.country
              )?.id ?? this.infoModel.countryId ?? 0,
              country:
                this.countryList.find((x) => x.id == this.infoModel.country)
                  ?.countryName ?? this.infoModel.country ?? "",
              province:
                this.provinces.find((x) => x.id === this.infoModel.province)
                  ?.stateName ?? "",
              provinceId: this.provinces.find(
                (x) => x.id === this.infoModel.province
              )?.id  ?? 0,
              cityId: this.cities.find((x) => x.id == this.infoModel.city)
                ?.id ?? 0,
              city:
                this.cities.find((x) => x.id == this.infoModel.city)
                  ?.cityName ?? "",
              phone: this.infoModel.areaCode + " " + this.infoModel.phone,
            };
            params.province == '' && delete params.province
            params.city == '' && delete params.city
            if (this.isEdit) {
              await this.requestAddressEdit(params);
            } else {
              await this.requestAddressAdd(params);
            }
            this.$message({
              type: "success",
              message: this.$t("message.home.operationSuccess"),
            });
            this.dialogVisible = false;
          } finally {
            this.loading = false;
          }
        }
      });
    },
  },
};
</script>

<style lang="scss">
html[dir="rtl"]{
  .el-form-item /deep/ .el-form-item__content /deep/ .el-form-item__error{
    right: 0;
    left: auto;
  }
  .es-dialog .dialog-title{
    width: 100%;
  }
  .add-address-content .form-phone .area-code span{
    padding-left: 0;
    padding-right: 8px;
  }
  .add-address-content .form-phone .area-code{
    width: 60px;
    padding-left: 10px;
  }
  .el-form-item /deep/ .el-form-item__label{
    float: right;
  }
}
.vue-country-item.selected .selected-text{
  display: none;
}
.add-address-content {
  .check_address {
    display: flex;
    gap: 10px;
    margin-bottom: 10px;
  }

  .form-phone {
    position: relative;
    cursor: pointer;

    .el-input__inner {
      padding-left: 100px;
    }

    .vue-country-popover-container {
      position: absolute;
      top: 50%;
      left: 0;
      transform: translateY(-50%);
    }

    .area-code {
      width: 80px;

      span {
        display: inline-block;
        width: 50px;
        padding-left: 8px;
      }
    }
  }

  .submit-btn {
    width: 100%;
    cursor: pointer;

    .el-button {
      width: 100%;
      height: 50px;
      max-width: 450px;
      padding: 0;
    }
  }
}
.prov-city {
  display: flex;
  div {
    background-color: #fff;
    border-radius: 4px;
    border: 1px solid #dcdfe6;
    box-sizing: border-box;
    color: #606266;
    display: inline-block;
    font-size: inherit;
    height: 40px;
    line-height: 40px;
    outline: 0;
    padding: 0 15px;
    max-width: 210px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    &:nth-child(2) {
      margin-left: 20px;
    }
  }
}
.vue-country-intl-popover {
  z-index: 9999;

  .vue-country-item.selected {
    background-color: var(--color-main);
  }

  .vue-country-item:not(.selected):hover {
    background-color: var(--color-main);
  }
}
</style>
