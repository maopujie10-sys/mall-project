<template>
    <div class="resetSuccess">
        <fx-header :back="false" @back="loginOut">
        </fx-header>
        <div class="content">
            <div class="imgBox"><img src="@/assets/image/success.png" alt=""></div>
            <div class="mt-4 font-700 font-24">{{ $t('passwordChangeSuccess') }}</div>
            <div class="text-grey mt-5">{{ $t('useNewPasswordLogin') }}!</div>
            <van-button class="w-full" style="margin-top:82px;" type="primary" @click="loginOut">{{ $t('login') }}
            </van-button>
        </div>
    </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useUserStore } from '@/store/user';
const router = useRouter()
const userStore = useUserStore()

const loginOut = () => {
    userStore.userInfo = {}
    router.push('/login')
}
</script>

<style lang="scss" scoped>
.resetSuccess {
    width: 100%;
    box-sizing: border-box;
}

.content {
    font-size: 12px;
    padding: 16px;
    text-align: center;
}

.imgBox {
    width: 62px;
    height: 62px;
    margin: auto;

    img {
        width: 100%;
        height: 100%;
    }
}
</style>