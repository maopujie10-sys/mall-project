<template>
    <div class="AddressDetails" style="min-height: 100vh;">
        <nationality-list ref="controlChild" :title="$t('选择区域码')" @getName="getName(arguments)"></nationality-list>

        <van-nav-bar safe-area-inset-top fixed :title="$t('新增地址/修改地址')" :right-text="$t('保存')" left-arrow
            @click-left="onClickLeft" @click-right="submitHandle" />
        <div style="width: 100%; height: 46px"></div>

        <div class="form-content">
            <div class="item">
                <el-input :placeholder="$t('收货人姓名')" v-model="formData.contacts" clearable maxlength="64" show-word-limit
                    @input="inputVal('contacts', $event)">
                </el-input>
            </div>
            <div class="item">
                <el-input :placeholder="$t('邮箱')" v-model.trim="formData.email" clearable maxlength="64" show-word-limit>
                </el-input>
            </div>
            <div class="item">
                <el-input :placeholder="$t('手机号')" maxlength="20" :value="formData.phone" @input="handleInputChange">
                    <div slot="prepend" @click="openNational">
                        <p>
                            +<span>{{ dialCode }}</span>
                            <img :src="triangleDown" alt="" class="icon" />
                        </p>
                    </div>
                </el-input>
            </div>
            <div class="address_item">
                <el-select v-model="formData.country" filterable :placeholder="$t('请选择')" :no-data-text="$t('暂无数据')"
                    :no-match-text="$t('暂无数据')" :loading-text="$t('加载中')" @change="onCountryChange">
                    <el-option v-for="item in countryList" :key="item.id" value-key="countryName" :label="item.label"
                        :value="item.countryName">
                    </el-option>
                </el-select>
                <el-select v-if="isProvince" v-model="formData.province" filterable :placeholder="$t('请选择')"
                    :no-data-text="$t('暂无数据')" :no-match-text="$t('暂无数据')" :loading-text="$t('加载中')"
                    @change="onProvinceChange">
                    <el-option v-for="item in provinceList" :key="item.id" value-key="stateName" :label="item.label"
                        :value="item.stateName">
                    </el-option>
                </el-select>
                <el-select v-if="isProvince && isCity" v-model="formData.city" filterable :no-data-text="$t('暂无数据')"
                    :no-match-text="$t('暂无数据')" :loading-text="$t('加载中')" :placeholder="$t('请选择')" @change="onCityChange">
                    <el-option v-for="item in cityList" :key="item.id" value-key="cityName" :label="item.label"
                        :value="item.cityName">
                    </el-option>
                </el-select>
            </div>
            <div class="item">
                <el-input :placeholder="$t('邮编')" maxlength="32" show-word-limit v-model="formData.postcode" clearable>
                </el-input>
            </div>
            <div class="item">
                <el-input type="textarea" :placeholder="$t('收件地址')" v-model="formData.address" resize="none" maxlength="255"
                    show-word-limit :autosize="{ minRows: 3, maxRows: 4 }" clearable>
                </el-input>
            </div>
            <div class="item check">
                <div style="flex: 1">{{ $t("设为默认地址") }}</div>
                <van-switch v-model="checked" size="20px" />
            </div>
        </div>
    </div>
</template>
<script>
import { NavBar, Switch, Toast, Picker, popup } from "vant";
import {
    dizhi_liebiao_post,
    dizhi_xinzeng_post,
    dizhi_xiugai_post,
} from "@/API/user";
import NationalityList from "@/components/NationalityList";
import { apiListCountry, apiListState, apiListCity } from "@/API/common";
import de from "@/i18n/de";
export default {
    data() {
        return {
            triangleDown: require("@/assets/image/me/triangle_down.png"),
            pageDiaCode: false,
            dialCode: localStorage.getItem("dialCode") || 1,
            checked: true,
            showCountryPicker: false,
            showCityPicker: false,
            showProvincePicker: false,
            formData: {
                contacts: "",
                email: "",
                phone: "",
                country: "",
                province: "",
                city: "",
                postcode: "",
                address: "",
                countryId: 0,
                provinceId: 0,
                cityId: 0,
            },
            currentId: null,
            cityList: [],
            provinceList: [],
            countryList: [],
            countryId: 0,
            provinceId: 0,
            isProvince: true,
            isCity: true,
            currentCountryId: null,
        };
    },
    components: {
        [NavBar.name]: NavBar,
        [Switch.name]: Switch,
        NationalityList,
        [Picker.name]: Picker,
        [popup.name]: popup,
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.currentId = id;
            this.getAddressInfo();
        }
        this.getCountry();
    },
    methods: {
        // 获取国家
        async getCountry() {
            const result = await apiListCountry();
            this.countryList = result.data;
        },
        // 获取省/州
        async getStateList(id) {
            console.log(`id ::->`, id);
            const res = await apiListState({ countryId: +id });
            this.provinceList = res.data;
            if (this.provinceList.length == 0) {
                this.isProvince = false;
                this.provinceList = [{ stateName: this.$t("暂无数据"), id: "" }];
            }
        },
        // 获取市
        async getListCity(id) {
            console.log(`id ::->`, id);
            const res = await apiListCity({ stateId: id });
            this.cityList = res.data;
            if (this.cityList.length == 0) {
                this.isCity = false;
                this.cityList = [{ cityName: this.$t("暂无数据"), id: "" }];
            } else {
                this.isCity = true;
            }
        },
        // 城市change
        onCityChange(value) {
            this.cityList.find((item) => {
                if (item.cityName == value) {
                    this.formData.cityId = item.id;
                }
            });
            this.formData.city = value;
        },
        // onCityConfirm(value) {
        //     this.formData.city = value.cityName;
        //     this.showCityPicker = false;
        // },
        onCityCancel() {
            this.showCityPicker = false;
        },
        // 选择国家
        // onCountryConfirm(value) {
        //     this.formData.country = value.countryName;
        //     this.countryId = value.id;
        //     this.isProvince = true;
        //     this.isCity = true;
        //     this.showCountryPicker = false;
        //     this.currentCountryId = value.id;
        //     // 查看有没有省
        //     this.getStateList(value.id);
        // },
        onCountryChange(value) {
            this.countryList.find((item) => {
                if (item.countryName == value) {
                    this.formData.country = value
                    this.formData.countryId = item.id
                    this.currentCountryId = this.countryId = item.id;
                    this.isProvince = true;
                    this.showCountryPicker = false;
                    this.getStateList(item.id);
                }
            })
            this.formData.city = this.formData.province = "";
            this.formData.cityId = this.formData.provinceId = 0;
            // this.formData.country = value.countryName;
            // this.countryId = value.id;
            // this.isProvince = true;
            // this.isCity = true;
            // this.showCountryPicker = false;
            // this.currentCountryId = value.id;
            // // 查看有没有省
            // this.getStateList(value.id);
        },
        onCountryCancel() {
            this.showCountryPicker = false;
        },
        // onProvinceConfirm(value) {
        //     this.formData.province = value.stateName;
        //     this.provinceId = value.id;
        //     this.showProvincePicker = false;
        //     this.getListCity(value.id);
        // },
        onProvinceChange(value) {
            this.provinceList.find((item) => {
                if (item.stateName == value) {
                    this.formData.province = value
                    this.formData.provinceId = item.id
                    this.provinceId = item.id;
                    this.showProvincePicker = false;
                    this.getListCity(item.id);
                }
            })
            this.formData.city = ''
        },
        onProvinceCancel() {
            this.showProvincePicker = false;
        },
        clickCountry() {
            document.activeElement.blur();
            this.showCountryPicker = true;
            this.formData.province = "";
            this.formData.city = "";
        },
        ProvincePicker() {
            document.activeElement.blur();
            this.formData.city = "";
            // 选择省
            if (this.formData.country == "") {
                Toast(this.$t("请输入") + this.$t("国家"));
            } else {
                this.getStateList(this.countryId);
                this.showProvincePicker = true;
            }
        },

        CityPicker() {
            document.activeElement.blur();
            if (this.formData.province == this.$t("暂无数据")) {
                this.formData.city = this.$t("暂无数据");
                // this.city
            } else if (this.formData.country && this.formData.province) {
                this.getListCity(this.provinceId);
                this.showCityPicker = true;
            } else {
                Toast(this.$t("请输入") + this.$t("省区"));
            }
        },
        getAddressInfo() {
            Toast.loading({
                duration: 0,
                // message: this.$t("请求中"),
                forbidClick: true,
            });

            dizhi_liebiao_post({})
                .then((res) => {
                    Toast.clear();
                    const { pageList } = res;
                    const address = pageList.find(
                        (item) => String(item.id) === String(this.currentId)
                    );
                    if (address) {
                        this.checked = Boolean(address.use);
                        this.currentCountryId = address?.countryId
                        if (address.phone.indexOf("|") > -1) {
                            const arr = address.phone.split("|");
                            this.dialCode = arr[0];
                            address.phone = arr[1];
                        }
                        delete address.use;
                        address?.countryId && this.getStateList(address.countryId)
                        address?.provinceId && this.getListCity(address.provinceId)
                        this.formData = {
                            ...address,
                        };
                    }
                })
                .catch((err) => {
                    // Toast.fail(err.msg);
                });
        },

        onClickLeft() {
            this.$router.go(-1);
        },
        // 禁止input框输入表情
        inputVal(type, e) {
            let reg =
                /([0-9|*|#]\uFE0F\u20E3)|([0-9|#]\u20E3)|([\u203C-\u3299]\uFE0F\u200D)|([\u203C-\u3299]\uFE0F)|([\u2122-\u2B55])|(\u303D)|([(\A9)|(\AE)]\u3030)|(\uA9)|(\uAE)|(\u3030)|([\uD83C|\uD83D|\uD83E][\uDC00-\uDFFF])|([\uD83C|\uD83D|\uD83E][\uDC00-\uDFFF][\u200D|\uFE0F])/g;
            setTimeout(() => {
                this.formData[type] = e.replace(reg, "");
            }, 0);
        },
        getName(params) {
            if (!this.pageDiaCode) {
                this.pageDiaCode = true;
            } else {
                this.dialCode = params[2];
                localStorage.setItem("dialCode", this.dialCode);
            }
        },
        openNational() {
            this.$refs.controlChild.open();
        },
        handleInputChange(e) {
            // 限制input只能输入数字
            if (/^[1-9]\d*$|^$/.test(e)) {
                this.formData.phone = e
            }

        },
        submitHandle() {
            if (this.formData.contacts === "") {
                Toast(this.$t("请输入") + this.$t("名称"));
                return;
            }
            if (this.formData.email === "") {
                Toast(this.$t("请输入") + this.$t("邮箱"));
                return;
            } else {
                const reg =
                    /^([A-Za-z0-9_\-\.\w{3,}])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
                if (!reg.test(this.formData.email)) {
                    Toast(this.$t("邮箱格式有误"));
                    return;
                }
            }
            if (this.formData.phone === "") {
                Toast(this.$t("请输入") + this.$t("手机号"));
                return;
            } else {
                const reg = /^[0-9]+[0-9]*$/;
                if (!reg.test(this.formData.phone)) {
                    Toast(this.$t("手机号格式有误"));
                    return;
                }
            }
            if (this.formData.country === "") {
                Toast(this.$t("请输入") + this.$t("国家"));
                return;
            }
            // if (this.formData.province === "") {
            //   Toast(this.$t("请输入") + this.$t("省区"));
            //   return;
            // }
            // if (this.formData.city === "") {
            //   Toast(this.$t("请输入") + this.$t("市"));
            //   return;
            // }
            if (this.formData.postcode === "") {
                // Toast(this.$t("请输入") + this.$t("邮编"));
                this.$notifyWarn(this.$t("请输入") + this.$t("邮编"))
                return;
            }
            if (this.formData.address === "") {
                // Toast(this.$t("请输入") + this.$t("收件地址"));
                this.$notifyWarn(this.$t("请输入") + this.$t("收件地址"))
                return;
            }
            if (this.isProvince && this.formData.province == '') {
                // Toast(this.$t("请选择") + this.$t("省区"));
                this.$notifyWarn(this.$t("请选择") + this.$t("省区"))
                return;
            }
            if (this.isProvince && this.isCity && this.formData.city == '') {
                // Toast(this.$t("请选择") + this.$t("市"));
                this.$notifyWarn(this.$t("请选择") + this.$t("市"))
                return;
            }
            const params = {
                ...this.formData,
                countryId: this.currentCountryId,
                phone: `${this.dialCode}|${this.formData.phone}`,
                use: this.checked ? 1 : 0,
            };

            params.province == '' && delete params.province
            params.city == '' && delete params.city
            let ajaxFn = dizhi_xinzeng_post;
            if (this.currentId) {
                params.id = this.currentId;
                ajaxFn = dizhi_xiugai_post;
            }

            Toast.loading({
                duration: 0,
                message: this.$t("提交中"),
                forbidClick: true,
            });

            ajaxFn(params)
                .then(() => {
                    Toast.success(this.$t("保存成功"));
                    setTimeout(() => {
                        this.$router.go(-1);
                    }, 500);
                })
                .catch((err) => {
                    Toast.clear();
                    // Toast.fail(err.msg);
                });
        },
    },
};
</script>
<style lang="scss" scoped>
.AddressDetails {
    width: 100%;

    /deep/ .van-nav-bar__right {
        .van-nav-bar__text {
            color: val(--main-color) !important;
        }
    }

    /deep/ .el-input {
        input:focus {
            border-color: var(--main-color) !important;
        }
    }

    /deep/ .el-textarea {
        textarea:focus {
            border-color: var(--main-color) !important;
        }
    }

    .nr {
        width: 100%;
        padding: 0 15px;
        box-sizing: border-box;

        .biaoti {
            margin-top: 20px;
            font-style: normal;
            font-weight: 400;
            font-size: 12px;
            line-height: 16px;
            color: #333333;
        }

        .shuru {
            width: 100%;
            margin-top: 11px;
        }

        .tijiao {
            margin-top: 20px;
            width: 100%;
            height: 44px;
            background: var(--main-color);
            border-radius: 4px;
            font-style: normal;
            font-weight: 400;
            font-size: 16px;
            line-height: 44px;
            /* identical to box height, or 100% */

            text-align: center;

            color: #ffffff;
        }

        .moren {
            font-style: normal;
            font-weight: 400;
            font-size: 14px;
            line-height: 16px;
            color: #333333;
            margin-top: 22px;
            display: flex;
            width: 100%;
            justify-content: center;
            align-items: center;
        }
    }
}

.form-content {
    box-sizing: border-box;
    padding: 0 15px;
    padding-bottom: 50px;

    * {
        box-sizing: border-box;
    }

    >.item {
        margin-top: 11px;

        /deep/ .el-input-group--prepend {
            .el-input-group__prepend {
                background-color: transparent !important;
                color: #000 !important;
                border-right: none !important;
                padding: 0 15px !important;

                .icon {
                    width: 10px;
                    height: auto;
                    position: relative;
                    top: -1px;
                    margin-left: 5px;
                }
            }

            .el-input__inner {
                border-left-color: #fff;
            }
        }

        &.check {
            font-style: normal;
            font-weight: 400;
            font-size: 14px;
            line-height: 16px;
            color: #333333;
            display: flex;
            width: 100%;
            justify-content: center;
            align-items: center;
            border: 1px solid #dcdfe6;
            padding: 14px 15px;
            border-radius: 4px;
        }
    }

    .address_item {
        display: flex;
        margin-top: 11px;
        gap: 10px;
    }
}

.van-switch--on {
    background-color: var(--main-color) !important;
}

/deep/ .el-input>.el-input__inner {
    padding-right: 10px !important;
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
}
</style>
