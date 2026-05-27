import { ref } from 'vue'

const isDark = ref(localStorage.getItem('theme') === 'dark')

export function useThemeStore() {
  const toggle = () => {
    isDark.value = !isDark.value
    const theme = isDark.value ? 'dark' : 'light'
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }

  // init on first import
  const initTheme = () => {
    const theme = isDark.value ? 'dark' : 'light'
    document.documentElement.setAttribute('data-theme', theme)
  }

  return { isDark, toggle, initTheme }
}
