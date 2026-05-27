<template>
    <div class="fx-account px-4 pt-4">
        <h1 class="font-bold text-3xl">交易</h1>
        <div class="text-lg mt-2"> <strong>ID:</strong><span>Q1061745713(USD)</span></div>
        <p class="mt-2 text-gray">账户余额</p>
        <div class="text-3xl font-bold">123,456.12</div>
        <div class="flex mt-2 gap-x-4">
            <div class="flex-1 flex flex-col gap-y-2">
                <p class="text-gray">净值</p>
                <p class="text-xl font-bold">123,456.12</p>
                <van-button type="primary" @click="onRoute('/exchange/channel-in')">充值</van-button>
            </div>
            <div class="flex-1 flex flex-col gap-y-2">
                <p class="text-gray">未结盈利</p>
                <p class="text-xl font-bold">123,456.12</p>
                <van-button @click="onRoute('/exchange/channel-out')">提现</van-button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
const router = useRouter()

const onRoute = (path) => {
    router.push(path)
}
</script>
<style lang="scss" scoped>
:deep(.van-button--primary) {
    background: #2555F8 !important;
}

:deep(.van-button--default) {
    background: #F1F1F1 !important;
}
</style>