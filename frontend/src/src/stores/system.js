import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getSystemMode,
  setSystemMode,
  emergencyKill,
  getEmergencyHistory,
  getPendingApprovals,
  decideApproval,
  getApprovalHistory,
} from '@/api/system'

export const useSystemStore = defineStore('system', () => {
  const currentMode = ref('ai-control')
  const isKilled = ref(false)
  const killTime = ref('')
  const pendingCount = ref(0)
  const loading = ref(false)
  const error = ref(null)

  const modeLabel = computed(() => {
    const map = {
      'ai-control': 'AI ',
      'ai_control': 'AI ',
      assist: '',
      readonly: '',
      'human-control': '',
      human_control: '',
    }
    return map[currentMode.value] || currentMode.value
  })

  const emergencyModeLabel = computed(() => {
    const map = {
      'ai-control': 'AI ',
      'ai_control': 'AI ',
      human_control: '',
      'human-control': '',
      readonly: '',
      assist: '',
    }
    return map[currentMode.value] || currentMode.value
  })

  async function fetchMode() {
    try {
      const data = await getSystemMode()
      if (data && data.mode) {
        currentMode.value = data.mode
        isKilled.value = data.mode === 'human_control' || data.mode === 'human-control'
      }
      if (data && data.pendingCount !== undefined) {
        pendingCount.value = data.pendingCount
      }
    } catch {
      // Silently keep current mode
    }
  }

  async function switchMode(mode) {
    loading.value = true
    error.value = null
    try {
      await setSystemMode(mode)
      currentMode.value = mode
      if (mode !== 'human_control' && mode !== 'human-control') {
        isKilled.value = false
      }
      return true
    } catch (e) {
      error.value = e.message
      return false
    } finally {
      loading.value = false
    }
  }

  async function triggerEmergencyKill() {
    loading.value = true
    error.value = null
    try {
      await emergencyKill()
      currentMode.value = 'human-control'
      isKilled.value = true
      killTime.value = new Date().toLocaleTimeString('zh-CN', { hour12: false })
      return true
    } catch (e) {
      error.value = e.message
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchEmergencyHistory() {
    try {
      return await getEmergencyHistory()
    } catch {
      return []
    }
  }

  async function fetchPendingApprovals() {
    try {
      return await getPendingApprovals()
    } catch {
      return []
    }
  }

  async function handleApproval(taskId, approved) {
    try {
      await decideApproval(taskId, approved)
      return true
    } catch {
      return false
    }
  }

  async function fetchApprovalHistory() {
    try {
      return await getApprovalHistory()
    } catch {
      return []
    }
  }

  return {
    currentMode,
    isKilled,
    killTime,
    pendingCount,
    loading,
    error,
    modeLabel,
    emergencyModeLabel,
    fetchMode,
    switchMode,
    triggerEmergencyKill,
    fetchEmergencyHistory,
    fetchPendingApprovals,
    handleApproval,
    fetchApprovalHistory,
  }
})
