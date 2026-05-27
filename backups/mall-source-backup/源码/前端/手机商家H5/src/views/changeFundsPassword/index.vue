<template>
    <div class="changePassword">
        <fx-header>
            <template #title>
                {{ $t('changeFunsPassword') }}
            </template>
        </fx-header>
        <div class="line"></div>
        <div class="content">
            <ExInput :label="$t('原资金密码')" :placeholderText="$t('请输入6位数数字密码')" v-model="oldPassword"
                typeText="password" />
            <ExInput :label="$t('新资金密码')" :placeholderText="$t('请输入6位数数字密码')" v-model="newPassword"
                typeText="password" />
            <ExInput :label="$t('再次输入资金密码')" :placeholderText="$t('请再次输入6位数数字密码')"
                v-model="rePassword" typeText="password" />
            <van-button class="w-full btn-content" type="primary" :loading="subLoading" @click="submit">{{ $t('sure') }}</van-button>
        </div>
    </div>
</template>

<script setup>
import ExInput from "@/components/ex-input/index.vue";
import { _changeFundsPassword } from '@/service/user.api.js'
import { ref, nextTick } from "vue";
import { Toast } from "vant";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
const { t } = useI18n()
const router = useRouter()
const subLoading = ref(false)

const oldPassword = ref('')
const newPassword = ref('')
const rePassword = ref('')

const submit = () => {
    if (oldPassword.value === '') {
        Toast(t('请输入原密码'))
        return
    }
    if (newPassword.value === '') {
        Toast(t('请设置新密码'))
        return
    }

    if (oldPassword.value === newPassword.value) {
        Toast(t('新密码不能与旧密码相同'))
        return
    }

    if (!/^\d{6}$/.test(newPassword.value)) {
        Toast(t('请输入6位数数字密码'))
        return
    }

    if (newPassword.value !== rePassword.value) {
        Toast(t('两次密码输入不一致'))
        return
    }
    subLoading.value = true
    _changeFundsPassword({
        old_safeword: oldPassword.value,
        safeword: newPassword.value,
        re_safeword: rePassword.value
    }).then((res) => {
        Toast(t('changeSuccess'))
        subLoading.value = false
        setTimeout(() => {
            router.back()
        }, 1000);
    }).catch(err => {
        subLoading.value = false
    })
}

nextTick(() => {
    const mode = import.meta.env.MODE
    if (['familyMart'].includes(mode)) {
        router.back()
    }
})
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
    background: var(--site-main-color);
    color: #fff;
}

.btn-content {
    margin-top: 10px;
    background-color: var(--site-main-color);
    border-color: var(--site-main-color);
}
</style>
