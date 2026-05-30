import { defineStore } from "pinia"
import { ref, computed } from "vue"
import {
  getServerStatus, getPortStatus, getProcessList,
  cleanupServer as apiCleanup, browseFiles as apiBrowse,
  deleteFile as apiDelete, killProcess as apiKill,
} from "@/api/server"

export const useServerStore = defineStore("server", () => {
  const systemMetrics = ref({
    cpu: 0, cpuCores: "0",
    memory: 0, memUsed: "0", memTotal: "0",
    disk: 0, diskUsed: "0", diskTotal: "0",
    loadAvg: "- / - / -",
  })
  const processes = ref([])
  const ports = ref([])
  const loading = ref(false)
  const error = ref(null)

  const cpuColor = computed(() => {
    const v = systemMetrics.value.cpu
    return v > 80 ? "var(--color-danger)" : v > 50 ? "var(--color-warning)" : "var(--color-primary)"
  })
  const memColor = computed(() => {
    const v = systemMetrics.value.memory
    return v > 80 ? "var(--color-danger)" : v > 50 ? "var(--color-warning)" : "var(--color-primary)"
  })
  const diskColor = computed(() => {
    const v = systemMetrics.value.disk
    return v > 80 ? "var(--color-danger)" : v > 50 ? "var(--color-warning)" : "var(--color-primary)"
  })

  async function fetchAll() {
    loading.value = true
    error.value = null
    try {
      const [statusRes, portsRes, procRes] = await Promise.allSettled([
        getServerStatus(), getPortStatus(), getProcessList(),
      ])
      if (statusRes.status === "fulfilled") {
        const d = statusRes.value
        systemMetrics.value = {
          cpu: d.cpu ?? 0,
          cpuCores: String(d.cpu_count ?? ""),
          memory: d.memory?.percent ?? d.memory ?? 0,
          memUsed: (d.memory?.used_gb ?? "0") + " GB",
          memTotal: (d.memory?.total_gb ?? "0") + " GB",
          disk: d.disk?.percent ?? d.disk ?? 0,
          diskUsed: (d.disk?.used_gb ?? "0") + " GB",
          diskTotal: (d.disk?.total_gb ?? "0") + " GB",
          loadAvg: d.load ? `${d.load["1min"]} / ${d.load["5min"]} / ${d.load["15min"]}` : "- / - / -",
        }
      }
      if (portsRes.status === "fulfilled") {
        const list = portsRes.value?.listening || []
        ports.value = list.map(p => ({
          port: p.port, service: p.service || `PID:${p.pid}`,
          protocol: p.protocol || "tcp", listening: true,
        }))
      }
      if (procRes.status === "fulfilled") {
        const list = procRes.value?.top20 || []
        processes.value = list.map(p => ({
          name: p.name || "unknown", pid: p.pid || 0,
          cpu: p.cpu_percent || p.cpu || 0,
          mem: p.memory_percent || p.mem || 0,
          uptime: p.uptime || "-", status: "running",
        }))
      }
    } catch (e) { error.value = e.message }
    finally { loading.value = false }
  }

  async function doCleanup() {
    try { return await apiCleanup() } catch { return { ok: false } }
  }

  async function doBrowseFiles(path) {
    try { return await apiBrowse(path) } catch { return { entries: [] } }
  }

  async function doDeleteFile(path) {
    try { return await apiDelete(path) } catch { return { ok: false } }
  }

    async function doUploadFile(path, file) {
    try {
      const { uploadFile } = await import("@/api/server")
      return await uploadFile(path, file)
    } catch { return { ok: false } }
  }
  async function doKillProcess(pid) {
    try { return await apiKill(pid) } catch { return { ok: false } }
  }

  return {
    systemMetrics, processes, ports, loading, error,
    cpuColor, memColor, diskColor,
    fetchAll, doCleanup, doBrowseFiles, doDeleteFile, doUploadFile, doKillProcess,
  }
})

