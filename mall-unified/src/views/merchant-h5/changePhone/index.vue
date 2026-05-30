<template>
    <div class="bindVerify h-full bg-white">
        <fx-header>
            <template #title>{{ t(pageTitle) }}</template>
        </fx-header>
        <div class="content">
            <div style="margin-top: 22px;">
                <ExInput :label="t('phoneNum')"
                    :placeholderText="t('entryPhone')" v-model="account" :area="true"
                    @selectArea="onSelectArea" :dialCode="dialCode" :icon="icon" />
            </div>
            <div style="margin-top: 22px;">
                <ExInput :label="$t('登录密码')"
                    :placeholderText="$t('请输入登录密码')" v-model="password" typeText="password" :clearBtn="false" />
            </div>
            <van-button class="w-full" style="margin-top: 30px;" type="primary" :loading="submitLoading" @click="submit">{{ $t('confirm') }}
            </van-button>
        </div>
        <nationality-list ref='controlChildRef' :title="$t('selectArea')" @get-name="getName">
        </nationality-list>
    </div>
</template>

<script setup>
import ExInput from "@/components/ex-input/index.vue";
import { bindEmailOrPhoneSm } from "@/service/user.api.js";
import nationalityList from '../authentication/components/nationalityList.vue'
import { Toast } from 'vant';
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { useUserStore } from '@/store/user';
import countryList from './../authentication/components/countryList.js'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const account = ref('')
const password = ref('')
const dialCode = ref(0) //电话号前缀
const icon = ref('')
const userStore = useUserStore()
const submitLoading = ref(false)
const pageTitle = ref('修改手机号码')

onMounted(() => {
    const phone = userStore.userInfo.phone

    if (phone && !userStore.phoneverif) {
        const phoneArr = phone.split(' ')
        pageTitle.value = 'bindPhone'
        dialCode.value = Number(phoneArr[0])
        account.value = phoneArr[1]

        for (const key in countryList) {
            if (countryList[key].dialCode === Number(phoneArr[0])) {
                icon.value = countryList[key].code
            }
        }
    }
})

const submit = () => {
    if (account.value == '') {
        Toast(t('entryPhone'));
        return
    }
    if (!/^[0-9]+$/.test(account.value)) {
        Toast(t('请输入正确的手机号码'));
        return
    }
    if (password.value == '') {
        Toast(t('请输入登录密码'));
        return
    }

    submitLoading.value = true
    bindPhone()
}

const bindSuccessHandle = async () => {
    await userStore.getUserInfo(true)
    Toast(t('bindSuccess'));
    submitLoading.value = false
    setTimeout(() => {
        const reset = route.query.reset
        reset ? router.go(-2) : router.back()
    }, 1000);
}
const bindPhone = () => {
    bindEmailOrPhoneSm({
        target: `${dialCode.value} ${account.value}`,
        phone: `${dialCode.value} ${account.value}`,
        password: password.value
    }).then((res) => {
        bindSuccessHandle()
    }).catch((err) => {
        console.log(err)
        submitLoading.value = false
    })
}

const getName = (childname, childcode, childdialCode) => {
    console.log(childcode)
    icon.value = childcode;
    dialCode.value = childdialCode;
}

const controlChildRef = ref(null)
const onSelectArea = () => {
    controlChildRef.value.open();
}

</script>

<style lang="scss" scoped>
.bindVerify {
    width: 100%;
    min-height: 100vh;
    box-sizing: border-box;
}

.content {
    font-size: 12px;
    padding: 0 16px;
}

.iptbox {
    height: 44px;
    margin-top: 8px;
    padding: 0 10px;
    padding-left: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-radius: 3px;

    input {
        flex: 1;
        height: 100%;
        border: none;
    }
    input::-webkit-input-placeholder {
        color: #868c9a;
    }

    span {
        color: #1D91FF;
    }
}

.imgbox {
    border: 1px solid #E5E7ED;
    padding: 5px;
    width: 182px;
    height: 182px;
    box-sizing: border-box;

    img {
        width: 100%;
        height: 100%;
    }
}

.code {
    font-size: 15px;
    font-weight: 300;
    line-height: 18px;
    margin-top: 22px;
    height: 18px;

    img {
        width: 14px;
        height: 14px;
        margin-left: 5px;
    }
}

.tips {
    margin-top: 10px;
    color: #999999;
}

.copy {
    border-radius: 4px;
    width: 132px;
    height: 40px;
    margin-top: 16px;
    border: 1px solid #E5E7ED;
    line-height: 40px;
}

.bottom {
    padding: 20px 16px 7px 16px;

    p {
        padding-bottom: 13px;
    }
}

.van-password-input {
    margin: 0;
}

.van-password-input__security li {
    background: #F5F5F5;
    width: 50px;
    height: 50px;
    color: #333;
}

:deep(.van-password-input__security li) {
    background: #F5F5F5;
    width: 50px;
    height: 50px;
    color: #333;
}

:deep(.van-button--primary) {
    background-color: var(--site-main-color);
    border-color: var(--site-main-color);
    border-radius: 4px;
}
:deep(.inputBackground) {
    background-color: #fff !important;
    border-radius: 4px;
    border: 1px solid #eee;
}
</style>
