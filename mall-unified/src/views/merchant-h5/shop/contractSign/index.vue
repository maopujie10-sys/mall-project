<template>
  <div>
    <fx-header :fixed="true">
      <template #title>
        {{ t('签订电子合同') }}
      </template>
    </fx-header>
    <div style="height: 46px;"/>

    <iframe :src="href" class="iframe-content"></iframe>
  </div>
</template>

<script setup name="ShopContractSign">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from "vue-router";
import { useUserStore } from '@/store/user.js'
import { logoData } from '@/views/login/config.js'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const { t, locale } = useI18n()
const mode = import.meta.env.MODE
const currentSys = logoData.find(item => item.key === mode)
const sysName = currentSys ? currentSys.name : 'Argos'

const token = computed(() => {
  return userStore.userInfo?.token || ''
})

const href = ref('')

const { hostname, origin } = window.location
const host = hostname === 'localhost' ? 'https://www.catvg.xyz/promote/#/pact/' : `${origin}/promote/#/pact/`

sessionStorage.removeItem('SellToken')
sessionStorage.setItem('SellToken', token.value)
href.value = `${host}?token=${token.value}&lang=${locale.value}&name=${sysName}`

onMounted(() => {
  const { back } = route.query
  const canBack = back ? Boolean(Number(back)) : false

  window.closePopup = async () => {
    await userStore.getUserInfo(true)
    if (canBack) {
      router.back()
    } else {
      router.push('/shop')
    }
  }
})
</script>

<style lang="scss" scoped>
.iframe-content {
  width: 100%;
  min-height: calc(100vh - 46px);
  background-color: #fff;
  overflow-y: scroll;
}
</style>
