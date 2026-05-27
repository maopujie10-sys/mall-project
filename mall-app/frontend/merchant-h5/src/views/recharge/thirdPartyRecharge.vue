<template>
  <div>
    <div>
      <van-nav-bar ref="navEl" :title="t('recharge')" left-arrow @click-left="onClickLeft" fixed/>
    </div>
    <div class="iframe-content">
      <iframe :src="hrefUrl" class="flex-1"></iframe>
    </div>
  </div>
</template>

<script setup>
import {ref} from "vue";
import {useI18n} from "vue-i18n";
import {useRoute, useRouter} from "vue-router";
const {t} = useI18n()

const route = useRoute()
const router = useRouter()
const hrefUrl = ref('')
hrefUrl.value = route.query.u || ''
if (!hrefUrl.value) {
  onClickLeft()
}

const onClickLeft = () => { // 返回
  router.go(-2)
}
</script>

<style lang="scss" scoped>
.iframe-content {
  width: 100%;
  height: 100vh;
  padding-top: 46px;
  > iframe {
    width: 100%;
    height: 100%;
  }
}
</style>
