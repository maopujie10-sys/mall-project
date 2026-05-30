<template>
  <div class="dashboard">
    <div class="page-header">
      <h2>馃搳 绯荤粺浠〃鐩?/h2>
      <p>瀹炴椂鐩戞帶 路 鍘嗗彶瓒嬪娍 路 鍋ュ悍鐘舵€?/p>
    </div>

    <!-- 鍋ュ悍鍒?-->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6">
        <div class="health-card" :class="healthLevel">
          <div class="health-label">绯荤粺鍋ュ悍鍒?/div>
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
          <div class="metric-label">鍐呭瓨</div>
          <div class="metric-value" :style="{color: metrics.memory_percent > 80 ? '#ff4d4f' : metrics.memory_percent > 60 ? '#faad14' : '#52c41a'}">{{ metrics.memory_percent }}%</div>
          <el-progress :percentage="metrics.memory_percent" :stroke-width="6" :color="metrics.memory_percent > 80 ? '#ff4d4f' : metrics.memory_percent > 60 ? '#faad14' : '#52c41a'" :show-text="false" />
          <div class="metric-sub">{{ metrics.memory_used_gb }} / {{ metrics.memory_total_gb }} GB</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">纾佺洏</div>
          <div class="metric-value" :style="{color: metrics.disk_percent > 80 ? '#ff4d4f' : metrics.disk_percent > 60 ? '#faad14' : '#52c41a'}">{{ metrics.disk_percent }}%</div>
          <el-progress :percentage="metrics.disk_percent" :stroke-width="6" :color="metrics.disk_percent > 80 ? '#ff4d4f' : metrics.disk_percent > 60 ? '#faad14' : '#52c41a'" :show-text="false" />
          <div class="metric-sub">{{ metrics.disk_used_gb }} / {{ metrics.disk_total_gb }} GB</div>
        </div>
      </el-col>
    </el-row>

    <!-- 鍥捐〃 -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>馃搱 CPU / 鍐呭瓨 鍘嗗彶瓒嬪娍锛堟渶杩?0涓噰鏍风偣锛?/template>
          <div ref="cpuMemChart" style="height:280px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>馃捑 纾佺洏浣跨敤瓒嬪娍</template>
          <div ref="diskChart" style="height:280px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 蹇嵎鎿嶄綔 -->
    <el-card shadow="never">
      <template #header>鈿?蹇嵎鎿嶄綔</template>
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        <el-button @click="goTo('/chat')" type="primary">馃挰 AI 瀵硅瘽</el-button>
        <el-button @click="goTo('/server')">馃搳 鏈嶅姟鍣ㄩ潰鏉?/el-button>
        <el-button @click="goTo('/rotation')">馃寪 杞€肩郴缁?/el-button>
        <el-button @click="goTo('/audit')">馃搵 瀹¤鏃ュ織</el-button>
        <el-button @click="goTo('/network')">馃寪 缃戠粶宸ュ叿</el-button>
        <el-button @click="recordMetrics" :loading="recording">馃摑 璁板綍鎸囨爣</el-button>
        <el-button @click="refreshAll" :loading="loading">馃攧 鍒锋柊</el-button>
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
        ElMessage.success("宸茶褰?)
        await fetchHistory()
      } catch { ElMessage.error("璁板綍澶辫触") }
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
          { name: "鍐呭瓨", type: "line", data: h.map(p => p.memory_percent), smooth: true, lineStyle: { width: 2 }, itemStyle: { color: "#52c41a" }, areaStyle: { color: "rgba(82,196,26,0.1)" } },
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
        series: [{ name: "纾佺洏", type: "line", data: h.map(p => p.disk_percent), smooth: true, lineStyle: { width: 2, color: "#faad14" }, areaStyle: { color: "rgba(250,173,20,0.1)" }, itemStyle: { color: "#faad14" } }],
        legend: { bottom: 0, textStyle: { fontSize: 11 } },
      })
      // Resize on window resize
      window.addEventListener("resize", () => { cm.resize(); dc.resize() })
    }

    const healthLevel = computed(() => health.value.level || "unknown")
    const healthLevelText = computed(() => ({ excellent: "馃煝 浼樼", good: "馃數 鑹ソ", warning: "馃煛 璀﹀憡", critical: "馃敶 鍗遍櫓" }[healthLevel.value] || "鏈煡"))

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
.health-card.excellent { background: rgba(82,196,26,0.12); }
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
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>
