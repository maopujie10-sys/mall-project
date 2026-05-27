import { computed } from 'vue'
import { useSystemStore } from '@/store/system.js'

export const arLangCheck = function() {
  const systemStore = useSystemStore()
  return computed(() => systemStore.isArLang)
}
