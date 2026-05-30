import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  const locale = ref(localStorage.getItem('locale') || 'zh')
  const theme = ref(localStorage.getItem('theme') || 'light')

  const isDark = computed(() => theme.value === 'dark')

  function setLocale(lang) {
    locale.value = lang
    localStorage.setItem('locale', lang)
  }

  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    localStorage.setItem('theme', theme.value)
    document.documentElement.setAttribute('data-theme', theme.value)
  }

  return { locale, theme, isDark, setLocale, toggleTheme }
}, {
  persist: { key: 'mall-app', storage: localStorage }
})
