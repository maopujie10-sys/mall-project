<template>
  <div class="lang bg-white">
    <fx-header fixed>
      <template #title>
        {{ t('语言设置') }}
      </template>
    </fx-header>
    <div style="height: 46px;"></div>
    <div v-for="(item, index) in langDataRef" :key="index" class="lang-padding" @click="handleSetLang(item.key)">
      <div class="lang-title flex items-center font-13 textColor">
        <img class="h-6" :class="isArLang ? 'ml-3': 'mr-3'" :src="item.image" alt="">
        {{item.title}}
      </div>
      <div class="lang-flex"></div>
      <van-icon v-if="item.key == locale" name="success" class="icon" />
    </div>
  </div>
</template>
<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from 'vue-router'
import { langData } from './config'
import { useSystemStore } from '@/store/system.js'
import { useChatStore } from "@/store/chat.js";

import { arLangCheck } from '@/utils/arLangCheck'
import cloneDeep from 'lodash.clonedeep'
const { locale, t } = useI18n()
const systemStore = useSystemStore()

const router = useRouter();

const isArLang = arLangCheck()

const langDataRef = computed(() => {
  const data = cloneDeep(langData)
  const mode = import.meta.env.MODE
  const langKey = data.map(item => item.key)
  const showLang = mode === 'mbuy' ? ['en'] : langKey
  const langShowData = data.filter(item => showLang.includes(item.key))
  return langShowData
})

const handleSetLang = (lang) => {
  const rStr = lang === 'ar' ? 'rtl' : 'rtr'
  document.documentElement.setAttribute('dir', rStr)
  systemStore.setIsArLang(lang === 'ar')
  systemStore.setNotCnLang(!['cn', 'tw'].includes(lang))

  locale.value = lang
  localStorage.setItem('lang', lang)

  // IM初始化
  const chatStore = useChatStore()
  chatStore.setChatHandle()
  
  document.dispatchEvent(new CustomEvent('langChange'))
  router.back()
}
</script>
<style lang="scss" scoped>
.lang {
  width: 100%;
  box-sizing: border-box;
}

.CommonProblem-padding {
  padding-left: 25px;
  padding-right: 25px;
}

.lang-padding {
  padding: 22px 18px 22px 18px;
  box-sizing: border-box;
  border-bottom: 1px solid #E5E7ED;
  font-weight: 400;
  font-size: 18px;
  color: #000000;
  display: flex;
  .icon {
    color: var(--site-main-color);
  }
}

.lang-flex {
  flex: 1;
}
</style>
