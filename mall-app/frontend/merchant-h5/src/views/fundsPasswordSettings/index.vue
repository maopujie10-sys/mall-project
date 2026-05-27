<template>
    <div class="changePassword">
        <fx-header>
            <template #title>
                {{ $t('设置资金密码') }}
            </template>
        </fx-header>
        <div class="line"></div>
        <div class="content">
            <ExInput :label="$t('资金密码')" :placeholderText="$t('请输入6位数数字密码')" v-model="oldPassword"
                typeText="password" />
            <ExInput :label="$t('再次输入资金密码')" :placeholderText="$t('请再次输入6位数数字密码')"
                v-model="rePassword" typeText="password" />
            <van-button class="w-full" style="margin-top:10px;" type="primary" :loading="subLoading" @click="submit">{{ $t('sure') }}</van-button>
        </div>
    </div>
</template>

<script setup>
import ExInput from "@/components/ex-input/index.vue";
import { _setSafewordReg } from '@/service/user.api.js'
import { ref } from "vue";
import { Toast } from "vant";
import { useUserStore } from '@/store/user';
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
const { t } = useI18n()
const router = useRouter()

const userStore = useUserStore()
const subLoading = ref(false)

const oldPassword = ref('')
const rePassword = ref('')

const submit = () => {
    if (oldPassword.value === '') {
        Toast(t('请输入6位数数字密码'))
        return
    }
    if (oldPassword.value !== rePassword.value) {
        Toast(t('两次密码输入不一致'))
        return
    }
    subLoading.value = true
    _setSafewordReg({
        safeword: oldPassword.value
    }).then(async (res) => {
        await userStore.getUserInfo(true)
        Toast(t('设置成功'))
        subLoading.value = false
        setTimeout(() => {
            router.back()
        }, 1000);
    }).catch(err => {
        subLoading.value = false
    })
}
</script>

<style lang="scss" scoped>
.changePassword {
    width: 100%;
    box-sizing: border-box;
    background-color: #fff;
    height: 100vh;
}

.line {
    width: 100%;
    height: 2px;
    background: #F5F5F5;
}

.content {
    padding: 16px;
    font-size: 13px;
}

.hightLight {
    background: #2C78F8;
    color: #fff;
}
</style>
