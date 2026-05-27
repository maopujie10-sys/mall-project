<template>
  <div class="agrrement-content">
    <div v-for="(item, index) in agreeData" :key="index" class="agree-item">
      <h3>{{ t(item.title) }}</h3>
      <div v-if="item.data.length" class="info">
        <p v-for="(info, _index) in item.data" :key="info">{{ `${index + 1}.${_index + 1} ${t(info)}` }}</p>
      </div>
    </div>
  </div>
</template>

<script setup name="LoginAgreement">
import { nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { agreeData } from './config'

const { t, locale } = useI18n()
const route = useRoute()

nextTick(() => {
  const { lang } = route.query
  if (lang) {
    locale.value = lang
    localStorage.setItem('lang', lang)
  }
})

</script>

<style lang="scss" scoped>
.agrrement-content {
  padding: 20px;
  min-height: 100vh;
  background-color: #fff;
  box-sizing: border-box;
  .agree-item {
    margin-top: 20px;
    &:first-child {
      margin-top: 0;
    }
    > h3 {
      font-size: 14px;
      font-weight: bold;
      color: #333;
      padding-bottom: 10px;
    }
    > .info {
      font-size: 12px;
      color: #333;
      > p {
        margin-top: 8px;
        &:first-child {
          margin-top: 0;
        }
      }
    }
  }
}
</style>
