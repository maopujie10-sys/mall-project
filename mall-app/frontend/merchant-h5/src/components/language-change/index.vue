<template>
  <div class="language-container">
    <div class="current" @click="isOpen = !isOpen">
      <div class="nation">
        <img :src="langInfo.image.href" alt="">
      </div>
      <p>{{ langInfo.title }}</p>
      <van-icon name="arrow-down" class="icon" />
    </div>
    <div :class="{'active': isOpen}" class="select-content">
      <div v-for="item in langData" :key="item.key" :class="{'active': item.key === currentLan}" class="item" @click="changeHandle(item.key)">
        <img :src="item.image.href" alt="">
        <p>{{ item.title }}</p>
        <van-icon name="success" class="icon" />
      </div>
    </div>
    <div :class="{'active': isOpen}" class="bg" @click="isOpen = false"></div>
  </div>
</template>

<script setup name="LanguageChange">
import { ref, computed } from 'vue'
import { langData } from '@/views/language/config'
import { useI18n } from 'vue-i18n'
import { useSystemStore } from '@/store/system.js'

const { locale } = useI18n()
const systemStore = useSystemStore()
const langInfo = computed(() => {
  const key = locale.value || 'en'
  const langObj = langData.find(item => item.key === key)
  return langObj
})

const currentLan = computed(() => {
  return locale.value || 'en'
})

const isOpen = ref(false)

const changeHandle = (lang) => {
  const rStr = lang === 'ar' ? 'rtl' : 'rtr'
  document.documentElement.setAttribute('dir', rStr)
  systemStore.setIsArLang(lang === 'ar')
  systemStore.setNotCnLang(!['cn', 'tw'].includes(lang))

  locale.value = lang
  localStorage.setItem('lang', lang)
  
  document.dispatchEvent(new CustomEvent('langChange'))
  isOpen.value = false
}

</script>

<style lang="scss" scoped>
.language-container {
  position: relative;
  > .current {
    display: flex;
    align-items: center;
    cursor: pointer;
    position: relative;
    z-index: 999;
    > .nation {
      width: 30px;
      height: 30px;
      border-radius: 50%;
      border: 1px solid #FFEEC2;
      overflow: hidden;
      > img {
        width: 100%;
        height: 100%;
      }
    }
    > p {
      color: #fff;
      font-size: 14px;
      padding: 0 10px;
    }
    .icon {
      color: #fff;
      font-size: 18px;
    }
  }
  > .select-content {
    position: absolute;
    top: 40px;
    left: 50%;
    transform: translateX(-50%);
    width: 190px;
    padding: 10px;
    background-color: rgba(0, 0, 0, .4);
    background-color: #fff;
    border-radius: 4px;
    height: 300px;
    overflow-y: scroll;
    opacity: 0;
    pointer-events: none;
    z-index: 999;
    &.active {
      opacity: 1;
      pointer-events: auto;
    }
    > .item {
      padding: 5px 0;
      display: flex;
      align-items: center;
      position: relative;
      cursor: pointer;
      &.active {
        > .icon {
          opacity: 1;
        }
        > p {
          color: #1989fa;
        }
      }
      > img {
        width: 24px;
        height: auto;
      }
      > p {
        flex: 1;
        white-space: nowrap;
        font-size: 13px;
        padding: 0 5px;
      }
      > .icon {
        color: #1989fa;
        opacity: 0;
      }
    }
  }
  > .bg {
    width: 100vw;
    height: 100vh;
    background-color: rgba(0, 0, 0, .4);
    position: fixed;
    top: 0;
    left: 0;
    z-index: 998;
    opacity: 0;
    pointer-events: none;
    &.active {
      pointer-events: auto;
    }
  }
}
</style>
