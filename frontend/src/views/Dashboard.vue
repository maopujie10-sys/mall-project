<template>
  <div class="dashboard">
    <!-- ===== 粒子背景 ===== -->
    <div class="dash-particles">
      <span v-for="i in 20" :key="i" class="dp" :style="{ '--x': Math.random()*100+'%', '--d': (i*0.5)+'s', '--s': (2+Math.random()*3)+'px' }"></span>
    </div>

    <!-- ===== 顶部全息头部 ===== -->
    <div class="dash-header">
      <div class="dh-left">
        <div class="dh-icon">
          <div class="dh-core"></div>
          <div class="dh-ring"></div>
        </div>
        <div>
          <h2 class="dh-title">控制中心</h2>
          <p class="dh-sub">Control Panel</p>
        </div>
      </div>
      <div class="dh-right">
        <div class="dh-metrics">
          <span class="dh-dot" :style="{ background: health.score > 80 ? '#52c41a' : health.score > 50 ? '#faad14' : '#ff4d4f' }"></span>
          <span>系统健康度 {{ health.score || 0 }}</span>
        </div>
      </div>
    </div>

    <!-- ===== 健康指标网格 ===== -->
    <div class="metric-grid">
      <!-- 系统健康度 -->
      <div class="holo-card health-card" :class="healthLevel">
        <div class="hc-glow"></div>
        <div class="hc-scanline"></div>
        <div class="hc-content">
          <div class="hc-icon">
            <div class="hc-mini-sphere"></div>
          </div>
          <div class="hc-value">{{ health.score || 0 }}</div>
          <div class="hc-label">系统健康度</div>
          <div class="hc-level">{{ healthLevelText }}</div>
        </div>
      </div>

      <!-- CPU -->
      <div class="holo-card">
        <div class="hc-scanline"></div>
        <div class="mc-header">
          <span class="mc-icon">⚡</span>
          <span class="mc-label">CPU</span>
        </div>
        <div class="mc-value" :style="{ color: metrics.cpu > 80 ? '#ff4d4f' : metrics.cpu > 60 ? '#faad14' : '#52c41a' }">{{ metrics.cpu }}%</div>
        <div class="mc-bar-track">
          <div class="mc-bar-fill" :style="{ width: metrics.cpu+'%', background: metrics.cpu > 80 ? 'linear-gradient(90deg,#ff4d4f,#ff7875)' : metrics.cpu > 60 ? 'linear-gradient(90deg,#faad14,#ffc53d)' : 'linear-gradient(90deg,#52c41a,#73d13d)' }"></div>
        </div>
        <div class="mc-bar-glow" :style="{ width: metrics.cpu+'%' }"></div>
      </div>

      <!-- 内存 -->
      <div class="holo-card">
        <div class="hc-scanline"></div>
        <div class="mc-header">
          <span class="mc-icon">▦</span>
          <span class="mc-label">内存</span>
        </div>
        <div class="mc-value" :style="{ color: metrics.memory_percent > 80 ? '#ff4d4f' : metrics.memory_percent > 60 ? '#faad14' : '#52c41a' }">{{ metrics.memory_percent }}%</div>
        <div class="mc-bar-track">
          <div class="mc-bar-fill" :style="{ width: metrics.memory_percent+'%', background: metrics.memory_percent > 80 ? 'linear-gradient(90deg,#ff4d4f,#ff7875)' : metrics.memory_percent > 60 ? 'linear-gradient(90deg,#faad14,#ffc53d)' : 'linear-gradient(90deg,#52c41a,#73d13d)' }"></div>
        </div>
        <div class="mc-bar-glow" :style="{ width: metrics.memory_percent+'%' }"></div>
        <div class="mc-sub">{{ metrics.memory_used_gb }} / {{ metrics.memory_total_gb }} GB</div>
      </div>

      <!-- 磁盘 -->
      <div class="holo-card">
        <div class="hc-scanline"></div>
        <div class="mc-header">
          <span class="mc-icon">◈</span>
          <span class="mc-label">磁盘</span>
        </div>
        <div class="mc-value" :style="{ color: metrics.disk_percent > 80 ? '#ff4d4f' : metrics.disk_percent > 60 ? '#faad14' : '#52c41a' }">{{ metrics.disk_percent }}%</div>
        <div class="mc-bar-track">
          <div class="mc-bar-fill" :style="{ width: metrics.disk_percent+'%', background: metrics.disk_percent > 80 ? 'linear-gradient(90deg,#ff4d4f,#ff7875)' : metrics.disk_percent > 60 ? 'linear-gradient(90deg,#faad14,#ffc53d)' : 'linear-gradient(90deg,#52c41a,#73d13d)' }"></div>
        </div>
        <div class="mc-bar-glow" :style="{ width: metrics.disk_percent+'%' }"></div>
        <div class="mc-sub">{{ metrics.disk_used_gb }} / {{ metrics.disk_total_gb }} GB</div>
      </div>
    </div>

    <!-- ===== 图表区域 ===== -->
    <div class="chart-grid">
      <div class="holo-card chart-card">
        <div class="hc-scanline"></div>
        <div class="chart-title">
          <span class="chart-dot cpu"></span>
          CPU / 内存趋势
        </div>
        <div class="chart-box" ref="cpuMemChart"></div>
      </div>
      <div class="holo-card chart-card">
        <div class="hc-scanline"></div>
        <div class="chart-title">
          <span class="chart-dot disk"></span>
          磁盘趋势
        </div>
        <div class="chart-box" ref="diskChart"></div>
      </div>
    </div>

    <!-- ===== 快捷操作 ===== -->
    <div class="holo-card action-card">
      <div class="hc-scanline"></div>
      <div class="action-title">快捷操作</div>
      <div class="action-grid">
        <button class="holo-btn primary" @click="goTo('/chat')">
          <span class="hb-glow"></span>
          <span>AI 对话</span>
        </button>
        <button class="holo-btn" @click="goTo('/server')">
          <span class="hb-glow"></span>
          <span>服务器</span>
        </button>
        <button class="holo-btn" @click="goTo('/rotation')">
          <span class="hb-glow"></span>
          <span>域名轮值</span>
        </button>
        <button class="holo-btn" @click="recordMetrics" :disabled="recording">
          <span class="hb-glow"></span>
          <span>{{ recording ? '记录中...' : '记录指标' }}</span>
        </button>
        <button class="holo-btn primary" @click="refreshAll" :disabled="loading">
          <span class="hb-glow"></span>
          <span>{{ loading ? '刷新中...' : '刷新数据' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, nextTick } from "vue"
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

    const healthLevel = computed(() => health.value.level || "unknown")
    const healthLevelText = computed(() => ({ excellent: "优秀", good: "良好", warning: "警告", critical: "危险" }[healthLevel.value] || "未知"))

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
        ElMessage.success("记录成功")
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
      if (typeof echarts === "undefined") {
        const script = document.createElement("script")
        script.src = "https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"
        script.onload = () => renderCharts()
        document.head.appendChild(script)
        return
      }
      const cm = echarts.init(cpuMemChart.value)
      cm.setOption({
        tooltip: { trigger: "axis", backgroundColor: "rgba(10,10,30,0.9)", borderColor: "rgba(102,126,234,0.3)", textStyle: { color: "#e8eaf0", fontSize: 11 } },
        grid: { left: 50, right: 20, bottom: 30, top: 10 },
        xAxis: { type: "category", data: times, axisLabel: { fontSize: 10, color: "#667" }, axisLine: { lineStyle: { color: "rgba(102,126,234,0.15)" } } },
        yAxis: { type: "value", max: 100, axisLabel: { fontSize: 10, color: "#667", formatter: "{value}%" }, splitLine: { lineStyle: { color: "rgba(102,126,234,0.08)" } } },
        series: [
          { name: "CPU", type: "line", data: h.map(p => p.cpu), smooth: true, symbol: "none", lineStyle: { width: 2, color: "#1890ff" }, areaStyle: { color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: "rgba(24,144,255,0.3)" }, { offset: 1, color: "rgba(24,144,255,0.02)" }] } } },
          { name: "内存", type: "line", data: h.map(p => p.memory_percent), smooth: true, symbol: "none", lineStyle: { width: 2, color: "#52c41a" }, areaStyle: { color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: "rgba(82,196,26,0.3)" }, { offset: 1, color: "rgba(82,196,26,0.02)" }] } } },
        ],
        legend: { bottom: 0, textStyle: { fontSize: 11, color: "#889" } },
        backgroundColor: "transparent",
      })
      const dc = echarts.init(diskChart.value)
      dc.setOption({
        tooltip: { trigger: "axis", backgroundColor: "rgba(10,10,30,0.9)", borderColor: "rgba(102,126,234,0.3)", textStyle: { color: "#e8eaf0", fontSize: 11 } },
        grid: { left: 50, right: 20, bottom: 30, top: 10 },
        xAxis: { type: "category", data: times, axisLabel: { fontSize: 10, color: "#667" }, axisLine: { lineStyle: { color: "rgba(102,126,234,0.15)" } } },
        yAxis: { type: "value", max: 100, axisLabel: { fontSize: 10, color: "#667", formatter: "{value}%" }, splitLine: { lineStyle: { color: "rgba(102,126,234,0.08)" } } },
        series: [{ name: "磁盘", type: "line", data: h.map(p => p.disk_percent), smooth: true, symbol: "none", lineStyle: { width: 2, color: "#faad14" }, areaStyle: { color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: "rgba(250,173,20,0.3)" }, { offset: 1, color: "rgba(250,173,20,0.02)" }] } } }],
        legend: { bottom: 0, textStyle: { fontSize: 11, color: "#889" } },
        backgroundColor: "transparent",
      })
      window.addEventListener("resize", () => { cm.resize(); dc.resize() })
    }

    async function refreshAll() {
      loading.value = true
      await Promise.all([fetchMetrics(), fetchHealth(), fetchHistory()])
      loading.value = false
    }

    function goTo(path) { router.push(path) }

    onMounted(async () => {
      await refreshAll()
      chartInterval = setInterval(fetchMetrics, 30000)
    })
    onUnmounted(() => { if (chartInterval) clearInterval(chartInterval) })

    return { loading, recording, metrics, health, history, cpuMemChart, diskChart, healthLevel, healthLevelText, refreshAll, recordMetrics, goTo }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  min-height: 100%;
}

/* ===== 粒子背景 ===== */
.dash-particles {
  position: fixed; inset: 0; pointer-events: none; z-index: 0;
  overflow: hidden;
}
.dp {
  position: absolute;
  width: var(--s); height: var(--s);
  left: var(--x); top: -10px;
  background: rgba(102,126,234,0.3);
  border-radius: 50%;
  animation: dpFall 8s linear infinite;
  animation-delay: var(--d);
}
@keyframes dpFall {
  0% { transform: translateY(-10px) scale(1); opacity: 0; }
  10% { opacity: 0.6; }
  90% { opacity: 0.6; }
  100% { transform: translateY(100vh) scale(0.3); opacity: 0; }
}

/* ===== 全息头部 ===== */
.dash-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  position: relative;
  z-index: 1;
}
.dh-left { display: flex; align-items: center; gap: 14px; }
.dh-icon {
  width: 48px; height: 48px;
  position: relative;
  display: flex; align-items: center; justify-content: center;
}
.dh-core {
  width: 60%; height: 60%;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #667eea, #764ba2);
  box-shadow: 0 0 20px rgba(102,126,234,0.5);
  animation: dhPulse 3s ease-in-out infinite;
}
@keyframes dhPulse {
  0%, 100% { transform: scale(1); opacity: 0.85; }
  50% { transform: scale(1.1); opacity: 1; }
}
.dh-ring {
  position: absolute; inset: 0;
  border-radius: 50%;
  border: 1.5px solid rgba(102,126,234,0.25);
  animation: dhSpin 4s linear infinite;
}
@keyframes dhSpin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.dh-title { margin: 0; font-size: 22px; font-weight: 700; color: #e8eaf0; }
.dh-sub { margin: 2px 0 0; font-size: 12px; color: #667; }
.dh-right { display: flex; align-items: center; gap: 12px; }
.dh-metrics {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; color: #889;
  padding: 6px 14px;
  border-radius: 20px;
  background: rgba(102,126,234,0.08);
  border: 1px solid rgba(102,126,234,0.12);
}
.dh-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  animation: dotBlink 2s ease-in-out infinite;
}
@keyframes dotBlink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

/* ===== 指标网格 ===== */
.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
}

/* ===== 全息卡片 ===== */
.holo-card {
  position: relative;
  background: rgba(13, 16, 37, 0.55);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(102, 126, 234, 0.12);
  border-radius: 14px;
  padding: 20px;
  overflow: hidden;
  transition: all 0.3s ease;
}
.holo-card:hover {
  border-color: rgba(102, 126, 234, 0.3);
  box-shadow: 0 0 30px rgba(102,126,234,0.08);
  transform: translateY(-2px);
}

.hc-scanline {
  position: absolute;
  left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(102,126,234,0.2), transparent);
  animation: hcScan 3s linear infinite;
  pointer-events: none;
}
@keyframes hcScan {
  0% { top: 0; opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { top: 100%; opacity: 0; }
}

/* 健康卡片 */
.health-card {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  min-height: 130px;
}
.health-card.excellent { border-color: rgba(82,196,26,0.3); }
.health-card.good { border-color: rgba(24,144,255,0.3); }
.health-card.warning { border-color: rgba(250,173,20,0.3); }
.health-card.critical { border-color: rgba(255,77,79,0.3); }
.health-card.excellent .hc-glow { background: radial-gradient(ellipse at center, rgba(82,196,26,0.1), transparent 70%); }
.health-card.good .hc-glow { background: radial-gradient(ellipse at center, rgba(24,144,255,0.1), transparent 70%); }
.health-card.warning .hc-glow { background: radial-gradient(ellipse at center, rgba(250,173,20,0.1), transparent 70%); }
.health-card.critical .hc-glow { background: radial-gradient(ellipse at center, rgba(255,77,79,0.1), transparent 70%); }

.hc-glow {
  position: absolute; inset: -50%;
  border-radius: 50%;
  pointer-events: none;
  animation: hcGlow 4s ease-in-out infinite;
}
@keyframes hcGlow {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.2); opacity: 0.8; }
}

.hc-content { position: relative; z-index: 1; }
.hc-icon { margin-bottom: 8px; display: flex; justify-content: center; }
.hc-mini-sphere {
  width: 32px; height: 32px;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #667eea, #764ba2);
  box-shadow: 0 0 15px rgba(102,126,234,0.4);
  animation: dhPulse 3s ease-in-out infinite;
}
.hc-value { font-size: 38px; font-weight: 700; color: #e8eaf0; line-height: 1; margin-bottom: 4px; }
.health-card.excellent .hc-value { color: #52c41a; }
.health-card.good .hc-value { color: #1890ff; }
.health-card.warning .hc-value { color: #faad14; }
.health-card.critical .hc-value { color: #ff4d4f; }
.hc-label { font-size: 12px; color: #889; margin-bottom: 2px; }
.hc-level { font-size: 13px; font-weight: 500; }
.health-card.excellent .hc-level { color: #52c41a; }
.health-card.good .hc-level { color: #1890ff; }
.health-card.warning .hc-level { color: #faad14; }
.health-card.critical .hc-level { color: #ff4d4f; }

/* 指标卡片 */
.mc-header {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 10px;
}
.mc-icon { font-size: 18px; }
.mc-label { font-size: 12px; color: #889; text-transform: uppercase; letter-spacing: 1px; }
.mc-value { font-size: 28px; font-weight: 700; margin-bottom: 10px; transition: color 0.3s; }
.mc-bar-track {
  height: 6px;
  background: rgba(255,255,255,0.05);
  border-radius: 3px;
  overflow: hidden;
  position: relative;
}
.mc-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
}
.mc-bar-glow {
  position: absolute;
  height: 20px;
  top: -7px;
  background: linear-gradient(90deg, transparent, rgba(102,126,234,0.2), transparent);
  filter: blur(8px);
  transition: width 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  pointer-events: none;
}
.mc-sub { font-size: 11px; color: #667; margin-top: 8px; }

/* ===== 图表区 ===== */
.chart-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
}
.chart-card { padding: 16px; }
.chart-title {
  font-size: 13px; font-weight: 600; color: #c0c4d0;
  margin-bottom: 12px;
  display: flex; align-items: center; gap: 8px;
}
.chart-dot {
  width: 8px; height: 8px; border-radius: 50%;
}
.chart-dot.cpu { background: #1890ff; box-shadow: 0 0 8px rgba(24,144,255,0.5); }
.chart-dot.disk { background: #faad14; box-shadow: 0 0 8px rgba(250,173,20,0.5); }
.chart-box { height: 200px; width: 100%; }

/* ===== 快捷操作 ===== */
.action-card { padding: 16px; position: relative; z-index: 1; }
.action-title {
  font-size: 13px; font-weight: 600; color: #c0c4d0;
  margin-bottom: 14px;
}
.action-grid {
  display: flex; gap: 10px; flex-wrap: wrap;
}

.holo-btn {
  position: relative;
  padding: 10px 20px;
  border-radius: 10px;
  border: 1px solid rgba(102,126,234,0.2);
  background: rgba(102,126,234,0.08);
  color: #aab;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
  overflow: hidden;
  display: flex; align-items: center; gap: 6px;
}
.holo-btn:hover {
  border-color: rgba(102,126,234,0.4);
  color: #e8eaf0;
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(102,126,234,0.15);
}
.holo-btn:active { transform: translateY(0); }
.holo-btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none !important; }
.holo-btn.primary {
  background: linear-gradient(135deg, rgba(102,126,234,0.2), rgba(118,75,162,0.15));
  border-color: rgba(102,126,234,0.35);
  color: #e8eaf0;
}
.holo-btn.primary:hover { box-shadow: 0 4px 20px rgba(102,126,234,0.25); }
.hb-glow {
  position: absolute; inset: 0;
  background: linear-gradient(135deg, transparent, rgba(102,126,234,0.05), transparent);
  animation: hbGlow 2s ease-in-out infinite;
  pointer-events: none;
}
@keyframes hbGlow {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

/* ===== 响应式 ===== */
@media (max-width: 900px) {
  .metric-grid { grid-template-columns: repeat(2, 1fr); }
  .chart-grid { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
  .dashboard { padding: 12px; }
  .metric-grid { grid-template-columns: 1fr; }
  .dh-title { font-size: 18px; }
  .dh-sub { font-size: 11px; }
  .hc-value { font-size: 30px; }
  .mc-value { font-size: 22px; }
  .holo-btn { padding: 8px 14px; font-size: 12px; }
}
</style>
