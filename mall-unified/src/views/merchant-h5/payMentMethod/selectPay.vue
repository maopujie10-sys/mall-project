<template>
    <div class="selectPay pb-10">
        <fx-header>
            <template #title>全部收款方式</template>
        </fx-header>
        <van-search v-model="value1" placeholder="请输入搜索关键词" />
        <van-index-bar>
            <van-index-anchor class="index-anchor" index="A" />
            <div @click="openAdd()" class="item-cell ml-4 py-4" v-for="(item, index) in 10" :key="index">Asia Hawala
            </div>
        </van-index-bar>
    </div>

</template>

<script setup>
import { onBeforeMount, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute()
const router = useRouter()
let value1 = ref('')
const openAdd = () => {
    router.push('add')
}
</script>
<style lang="scss" scoped>
.selectPay {
    .index-anchor {
        background: #F5F5F5;
    }
}

:deep(.van-index-bar__index) {
    color: #2555F8;
    font-size: 14px;
    margin-top: 6px;
}

.item-cell {
    border-bottom: 1px solid #EAEBEE;
    ;
}
</style>