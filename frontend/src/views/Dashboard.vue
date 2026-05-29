<template>
  <div class="dashboard">
    <div class="page-header">
      <h2>📊 系统仪表盘</h2>
      <p>实时监控 · 历史趋势 · 健康状态</p>
    </div>

    <!-- 健康分 -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6">
        <div class="health-card" :class="healthLevel">
          <div class="health-label">系统健康分</div>
          <div class="health-value">{{ health.score || 0 }}</div>
          <div class="health-level">{{ healthLevelText }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">CPU</div>
          <div class="metric-value" :style="{color: metrics.cpu > 80 ? '#ff4d4f' : metrics.cpu > 60 ? '#faad14' : '#52c41a'}">{{ metrics.cpu }}%</div>
          <el-progress :percentage="metrics.cpu" :stroke-width="6" :color="metrics.cpu > 80 ? '#ff4d4f' : metrics.cpu > 60 ? '#faad14' : '#52c41a'" :show-text="false" />
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">内存</div>
          <div class="metric-value" :style="{color: metrics.memory_percent > 80 ? '#ff4d4f' : metrics.memory_percent > 60 ? '#faad14' : '#52c41a'}">{{ metrics.memory_percent }}%</div>
          <el-progress :percentage="metrics.memory_percent" :stroke-width="6" :color="metrics.memory_percent > 80 ? '#ff4d4f' : metrics.memory_percent > 60 ? '#faad14' : '#52c41a'" :show-text="false" />
          <div class="metric-sub">{{ metrics.memory_used_gb }} / {{ metrics.memory_total_gb }} GB</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">磁盘</div>
          <div class="metric-value" :style="{color: metrics.disk_percent > 80 ? '#ff4d4f' : metrics.disk_percent > 60 ? '#faad14' : '#52c41a'}">{{ metrics.disk_percent }}%</div>
          <el-progress :percentage="metrics.disk_percent" :stroke-width="6" :color="metrics.disk_percent > 80 ? '#ff4d4f' : metrics.disk_percent > 60 ? '#faad14' : '#52c41a'" :show-text="false" />
          <div class="metric-sub">{{ metrics.disk_used_gb }} / {{ metrics.disk_total_gb }} GB</div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表 -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>📈 CPU / 内存 历史趋势（最近60个采样点）</template>
          <div ref="cpuMemChart" style="height:280px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>💾 磁盘使用趋势</template>
          <div ref="diskChart" style="height:280px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-card shadow="never">
      <template #header>⚡ 快捷操作</template>
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        <el-button @click="goTo('/chat')" type="primary">💬 AI 对话</el-button>
        <el-button @click="goTo('/server')">📊 服务器面板</el-button>
        <el-button @click="goTo('/rotation')">🌐 轮值系统</el-button>
        <el-button @click="goTo('/audit')">📋 审计日志</el-button>
        <el-button @click="goTo('/network')">🌐 网络工具</el-button>
        <el-button @click="recordMetrics" :loading="recording">📝 记录指标</el-button>
        <el-button @click="refreshAll" :loading="loading">🔄 刷新</el-button>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from "vue"
import { ElMessage } from "element-plus"
import { agentApi } from "@/api"
import { useRouter } from "vue-router"

export default {
  name: "Dashboard",
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const recording = ref(false)
    const metrics = ref({})
    const health = ref({})
    const history = ref([])
    const cpuMemChart = ref(null)
    const diskChart = ref(null)
    let chartInterval = null

    async function fetchMetrics() {
      try {
        const r = await agentApi.get("/dashboard/metrics")
        metrics.value = r.metrics || {}
      } catch {}
    }

    async function fetchHealth() {
      try {
        const r = await agentApi.get("/dashboard/health-score")
        health.value = r || {}
      } catch { health.value = { score: 0, level: "unknown" } }
    }

    async function fetchHistory() {
      try {
        const r = await agentApi.get("/dashboard/history", { params: { points: 60 } })
        history.value = r.history || []
        renderCharts()
      } catch {}
    }

    async function recordMetrics() {
      recording.value = true
      try {
        await agentApi.post("/dashboard/record")
        ElMessage.success("已记录")
        await fetchHistory()
      } catch { ElMessage.error("记录失败") }
      recording.value = false
    }

    function renderCharts() {
      if (!cpuMemChart.value || !diskChart.value) return
      const h = history.value
      if (h.length < 2) return
      const times = h.map(p => {
        const d = new Date(p.time)
        return d.getHours().toString().padStart(2,"0") + ":" + d.getMinutes().toString().padStart(2,"0")
      })
      // Load ECharts from CDN
      if (typeof echarts === "undefined") {
        const script = document.createElement("script")
        script.src = "https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"
        script.onload = () => renderCharts()
        document.head.appendChild(script)
        return
      }
      // CPU/Memory chart
      const cm = echarts.init(cpuMemChart.value)
      cm.setOption({
        tooltip: { trigger: "axis" },
        grid: { left: 50, right: 20, bottom: 30, top: 10 },
        xAxis: { type: "category", data: times, axisLabel: { fontSize: 10 } },
        yAxis: { type: "value", max: 100, axisLabel: { fontSize: 10, formatter: "{value}%" } },
        series: [
          { name: "CPU", type: "line", data: h.map(p => p.cpu), smooth: true, lineStyle: { width: 2 }, itemStyle: { color: "#1890ff" }, areaStyle: { color: "rgba(24,144,255,0.1)" } },
          { name: "内存", type: "line", data: h.map(p => p.memory_percent), smooth: true, lineStyle: { width: 2 }, itemStyle: { color: "#52c41a" }, areaStyle: { color: "rgba(82,196,26,0.1)" } },
        ],
        legend: { bottom: 0, textStyle: { fontSize: 11 } },
      })
      // Disk chart
      const dc = echarts.init(diskChart.value)
      dc.setOption({
        tooltip: { trigger: "axis" },
        grid: { left: 50, right: 20, bottom: 30, top: 10 },
        xAxis: { type: "category", data: times, axisLabel: { fontSize: 10 } },
        yAxis: { type: "value", max: 100, axisLabel: { fontSize: 10, formatter: "{value}%" } },
        series: [{ name: "磁盘", type: "line", data: h.map(p => p.disk_percent), smooth: true, lineStyle: { width: 2, color: "#faad14" }, areaStyle: { color: "rgba(250,173,20,0.1)" }, itemStyle: { color: "#faad14" } }],
        legend: { bottom: 0, textStyle: { fontSize: 11 } },
      })
      // Resize on window resize
      window.addEventListener("resize", () => { cm.resize(); dc.resize() })
    }

    const healthLevel = computed(() => health.value.level || "unknown")
    const healthLevelText = computed(() => ({ excellent: "🟢 优秀", good: "🔵 良好", warning: "🟡 警告", critical: "🔴 危险" }[healthLevel.value] || "未知"))

    async function refreshAll() {
      loading.value = true
      await Promise.all([fetchMetrics(), fetchHealth(), fetchHistory()])
      loading.value = false
    }

    function goTo(path) { router.push(path) }

    onMounted(async () => {
      await refreshAll()
      // Auto refresh every 30s
      chartInterval = setInterval(fetchMetrics, 30000)
    })
    onUnmounted(() => { if (chartInterval) clearInterval(chartInterval) })

    return { loading, recording, metrics, health, history, cpuMemChart, diskChart, healthLevel, healthLevelText, refreshAll, recordMetrics, goTo }
  }
}
</script>

<style scoped>
.dashboard { padding: 20px; }
.page-header { margin-bottom: 20px; }
.page-header h2 { margin: 0 0 4px; font-size: 20px; }
.page-header p { margin: 0; color: #999; font-size: 13px; }

.health-card {
  padding: 20px; border-radius: 8px; text-align: center; color: #fff;
}
.health-card.excellent { background: linear-gradient(135deg, #52c41a, #73d13d); }
.health-card.good { background: linear-gradient(135deg, #1890ff, #40a9ff); }
.health-card.warning { background: linear-gradient(135deg, #faad14, #ffc53d); }
.health-card.critical { background: linear-gradient(135deg, #ff4d4f, #ff7875); }
.health-label { font-size: 12px; opacity: 0.85; margin-bottom: 4px; }
.health-value { font-size: 42px; font-weight: 700; }
.health-level { font-size: 14px; margin-top: 4px; opacity: 0.9; }

.metric-card { background: rgba(13,16,37,0.55); backdrop-filter: blur(8px); border-radius: 8px; padding: 18px; border: 1px solid rgba(102,126,234,0.12); color: #e8eaf0; }
.metric-label { font-size: 12px; color: #999; margin-bottom: 4px; }
.metric-value { font-size: 28px; font-weight: 700; }
.metric-sub { font-size: 11px; color: #999; margin-top: 6px; }
</style>
