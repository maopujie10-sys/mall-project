<template>
  <div class="flex flex-col w-screen h-screen">
    <van-nav-bar ref="navEl" :title="$t(props.query.title)" left-arrow @click-left="onClickLeft" fixed/>
    <iframe :src="props.query.src" class="flex-1 mt-12"></iframe>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n';

const {t} = useI18n()

import { useRouter } from "vue-router";
const router = useRouter()

const props = defineProps(['query'])

console.log(props.query);

const onClickLeft = () => { // 返回
  router.go(-1);
}

</script>

<style scoped>

</style>