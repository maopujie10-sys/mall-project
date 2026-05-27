<template>
  <div>
    <fx-header :fixed="true">
      <template #title>
        {{ t('电子合同') }}
      </template>
    </fx-header>
    <div style="height: 46px;"/>

    <div v-if="signPdfUrl" class="contract-info-content">
      <view-pdf :source="signPdfUrl" :download="true"></view-pdf>
    </div>

    <van-empty v-if="!signPdfUrl && !pageLoading" :image="empytImg.href" :description="t('noData')" />
  </div>
</template>

<script setup name="ShopContract">
import { ref, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useUserStore } from '@/store/user.js'
import { Toast } from 'vant';
import ViewPdf from '@/components/view-pdf/index.vue'

const { t, locale } = useI18n()
const route = useRoute()
const signPdfUrl = ref('')

const empytImg = new URL('@/assets/image/public/no_data.png', import.meta.url)
const pageLoading = ref(false)
nextTick(async () => {
  const userStore = useUserStore()
  const { token, lang } = route.query
  if (lang) {
    locale.value = lang
    localStorage.setItem('lang', lang)
  }

  if (token) {
    pageLoading.value = true
    Toast.loading({duration: 0})
    await userStore.getUserInfo(true, token)
    Toast.clear()
    pageLoading.value = false
  }
  signPdfUrl.value = userStore.userInfo?.signPdfUrl
})

</script>

<style lang="scss" scoped>
.contract-info-content {
  width: 100%;
  min-height: calc(100vh - 46px);
  background-color: #fff;
}
</style>
