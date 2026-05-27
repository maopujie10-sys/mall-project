import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getServerStatus, getDiskInfo, getPortStatus, getProcessList } from '@/api/server'

export const useServerStore = defineStore('server', () => {
  const systemMetrics = ref({
    cpu: 0,
    cpuCores: '0',
    memory: 0,
    memUsed: '0 GB',
    memTotal: '0 GB',
    disk: 0,
    diskUsed: '0 GB',
    diskTotal: '0 GB',
    loadAvg: '- / - / -',
  })

  const processes = ref([])
  const ports = ref([])
  const loading = ref(false)
  const error = ref(null)

  const cpuColor = computed(() => {
    const v = systemMetrics.value.cpu
    return v > 80 ? 'var(--color-danger)' : v > 50 ? 'var(--color-warning)' : 'var(--color-primary)'
  })

  const memColor = computed(() => {
    const v = systemMetrics.value.memory
    return v > 80 ? 'var(--color-danger)' : v > 50 ? 'var(--color-warning)' : 'var(--color-primary)'
  })

  const diskColor = computed(() => {
    const v = systemMetrics.value.disk
    return v > 80 ? 'var(--color-danger)' : v > 50 ? 'var(--color-warning)' : 'var(--color-primary)'
  })

  async function fetchAll() {
    loading.value = true
    error.value = null
    try {
      const [statusRes, portsRes, procRes] = await Promise.allSettled([
        getServerStatus(),
        getPortStatus(),
        getProcessList(),
      ])

      if (statusRes.status === 'fulfilled') {
        const data = statusRes.value
        systemMetrics.value = {
          cpu: data.cpu ?? 0,
          cpuCores: data.cpuCores ?? '0',
          memory: data.memory ?? 0,
          memUsed: data.memUsed ?? '0 GB',
          memTotal: data.memTotal ?? '0 GB',
          disk: data.disk ?? 0,
          diskUsed: data.diskUsed ?? '0 GB',
          diskTotal: data.diskTotal ?? '0 GB',
          loadAvg: data.loadAvg ?? '- / - / -',
        }
      }

      if (portsRes.status === 'fulfilled') {
        const portsData = portsRes.value
        ports.value = Array.isArray(portsData) ? portsData : portsData?.ports || []
      }

      if (procRes.status === 'fulfilled') {
        const procData = procRes.value
        processes.value = Array.isArray(procData) ? procData : procData?.processes || []
      }
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  return {
    systemMetrics,
    processes,
    ports,
    loading,
    error,
    cpuColor,
    memColor,
    diskColor,
    fetchAll,
  }
})
