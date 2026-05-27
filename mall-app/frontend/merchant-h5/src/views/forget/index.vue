<template>
    <div class="forget">
        <fx-header>
        </fx-header>
        <div class="forgetCont">
            <div class="title textColor">{{ $t('resetLoginPassword') }}</div>
            <div class="flex re-tab text-grey">
                <div :class="activeIndex == 0 ? 'active' : ''" @click="changeIndex(0)">{{ $t('email') }}</div>
                <div :class="activeIndex == 1 ? 'active' : ''" @click="changeIndex(1)">{{ $t('phoneNum') }}</div>
                <div :class="activeIndex == 2 ? 'active' : ''" @click="changeIndex(2)">{{ $t('googleVerify') }}</div>
            </div>
            <ExInput :label="$t('account')" :placeholderText="$t('entryAccount')" v-model="account" :dialCode="dialCode"
                @selectArea="onSelectArea" :area="isArea" :icon="icon" />
            <van-button class="w-full" style="margin-top:10px;" type="primary" @click="next">{{ $t('nextStep') }}
            </van-button>
            <nationality-list ref='controlChildRef' :title="$t('selectArea')" @get-name="getName"></nationality-list>
        </div>
    </div>
</template>

<script setup>
import ExInput from "@/components/ex-input/index.vue";
import { _getUserNameVerifTarget } from "@/service/user.api.js";
import nationalityList from '../authentication/components/nationalityList.vue'
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { Toast } from "vant";
import { useRouter } from "vue-router";
const { t } = useI18n()
const router = useRouter()

const account = ref('')
const activeIndex = ref(0)
const isArea = ref(false)
const dialCode = ref(0) //电话号前缀
let icon = ref('')

const changeIndex = (index) => {
    activeIndex.value = index;
    if (index == 1) {
        isArea.value = true
    } else {
        isArea.value = false
    }
}
const next = () => {
    if (account.value == "") {
        Toast(t("entryAccount"))
        return;
    }
    getUserNameVerifTarget()

}
const getUserNameVerifTarget = () => {

    let type;
    if (activeIndex.value == 0) {
        type = 2
    } else if (activeIndex.value == 1) {
        type = 1
    } else if (activeIndex.value == 2) {
        type = 3
    }
    _getUserNameVerifTarget({
        username: type == 1 ? `${dialCode.value}${account.value}` : account.value,
        verifcode_type: type  //验证类型 1手机 2 邮箱 3谷歌验证器
    }).then((res) => {
        if (type == 1 && !res.phone_authority) {
            Toast(t('noBindPhoneNum'));
            return false
        } else if (type == 2 && !res.email_authority) {
            Toast(t('noBindEmail'));
            return false
        } else if (type == 3 && !res.google_auth_bind) {
            Toast(t('noBindGoogleAuth'));
            return false
        }
        let vertifyAccount;
        if (type == 1) {
            vertifyAccount = res.phone
        } else if (type == 2) {
            vertifyAccount = res.email
        }
        router.push({ name: 'safeVerify', query: { type: type, account: vertifyAccount, username: account.value } })
    })
}

const controlChildRef = ref(null)
const onSelectArea = () => {
    controlChildRef.value.open();
}

const getName = (childname, childcode, childdialCode) => {
    icon.value = childcode;
    dialCode.value = childdialCode;
}
</script>

<style lang="scss" scoped>
.forget {
    width: 100%;
    box-sizing: border-box;
    font-size: 13px;
}

.forgetCont {
    padding: 15px;
    ;
}

.header {
    display: flex;
    justify-content: space-between;
    padding: 0 13px;
    font-size: 14px;
    height: 50px;
    line-height: 50px;
}

.title {
    font-weight: 700;
    font-size: 26px;
    margin-top: 27px;
    margin-bottom: 33px;
}

.re-tab {
    margin-bottom: 22px;

    div {
        padding: 0 18px;
        height: 34px;
        line-height: 34px;
        text-align: center;
        border-radius: 4px;
        margin-right: 10px;
    }

    .active {
        background: #f6f6f6;
    }
}
</style>