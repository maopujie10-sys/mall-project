<template>
    <div class="changePassword">
        <fx-header>
            <template #title>
                {{ $t('changeLoginPassword') }}
            </template>
        </fx-header>
        <div class="line"></div>
        <div class="content">
            <ExInput :label="$t('newPassword')" :placeholderText="$t('entryPassword')" :tips="$t('setPasswordTips')"
                v-model="newPassword" typeText="password" />
            <ExInput :label="$t('sureNewPassword')" :placeholderText="$t('entryPassword')" :tips="$t('setPasswordTips')"
                v-model="rePassword" typeText="password" />
            <van-button class="w-full" :disabled="!hightLight" style="margin-top:22px;" type="primary" @click="submit">
                {{ $t('sure') }}
            </van-button>
        </div>
    </div>
</template>

<script setup>
import ExInput from "@/components/ex-input/index.vue";
import { _resetpsw } from "@/service/user.api.js";
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { Toast } from "vant";
const router = useRouter()
const route = useRoute()
const { t } = useI18n()

const newPassword = ref('')
const rePassword = ref('')
const currentType = ref('')
const username = ref('')
const verifcode = ref('')
const account = ref('')

const hightLight = computed(() => {
    if (newPassword.value.length >= 6 && rePassword.value.length >= 6) {
        return true
    } else {
        return false
    }
})

onMounted(() => {
    currentType.value = route.query.type;
    username.value = route.query.username;
    account.value = route.query.account;
    verifcode.value = route.query.verifycode;
    console.log(verifcode.value)
})
const submit = () => {
    if (newPassword.value.length < 6 || newPassword.value.length > 20) {
        Toast(t('setPasswordTips'))
        return false
    }
    
    if (newPassword.value !== rePassword.value) {
        Toast(t('noSamePassword'));
        return false
    }
    _resetpsw({
        username: currentType.value == 1 ? account.value : username.value,
        password: newPassword.value,
        verifcode_type: currentType.value,
        verifcode: verifcode.value,
    }).then((res) => {
        router.push('/passSuccess')
    })
}
</script>

<style lang="scss" scoped>
.changePassword {
    width: 100%;
    box-sizing: border-box;
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
</style>