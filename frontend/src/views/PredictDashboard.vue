<template>
  <div class="page-shell">
    <div class="page-header">
      -
      <p>  /// </p>
      <div class="header-stats">
        <el-statistic title='' :value="stats.metrics?.length||0"/>
        <el-statistic title='' :value="stats.total_points||0"/>
      </div>
    </div>
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card><template #header> </template>
          <el-input v-model="metric" placeholder="(sales/orders/visits)"/>
          <el-input-number v-model="value" :min="0" style="margin-top:8px;width:100%"/>
          <el-button type="primary" style="margin-top:8px" @click="record">OK</el-button>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card><template #header> </template>
          <el-input v-model="forecastMetric" placeholder=''/>
          <el-input-number v-model="horizon" :min="1" :max="30" style="margin-top:8px;width:100%"/>
          <el-button type="primary" style="margin-top:8px" @click="doForecast">{{ horizon }}</el-button>
          <div v-if="result" class="predict-result">
            <div class="pr-trend" :class="result.direction">
              {{ result.direction === "up" ? "" : result.direction === "down" ? "" : "" }} ({{ result.trend_pct }}%)
            </div>
            <div class="pr-values">: {{ result.predictions?.join(", ") || "" }}</div>
            <div class="pr-conf">: {{ result.confidence }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"
import { ElMessage } from "element-plus"
import { agentApi } from "@/api"
const metric = ref('')
const value = ref(0)
const forecastMetric = ref('')
const horizon = ref(7)
const result = ref(null)
const stats = ref({})
async function record() {
  if (!metric.value) return
  try { await agentApi.post("/agent/predict/record", { metric: metric.value, value: value.value }); ElMessage.success('OK'); fetchStats() } catch (e) { ElMessage.error(e.message) }
}
async function doForecast() {
  if (!forecastMetric.value) return
  try {
    const path = "/agent/predict/forecast/" + forecastMetric.value + "?horizon=" + horizon.value
    const r = await agentApi.get(path)
    if (r?.data) result.value = r.data
  } catch (e) { ElMessage.error(e.message) }
}
async function fetchStats() { try { const r = await agentApi.get("/agent/predict/stats"); if (r?.data) stats.value = r.data } catch {} }
onMounted(fetchStats)
</script>
<style scoped>
.page-shell { max-width: 900px; margin: 0 auto; padding: 20px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { font-size: 20px; color: #e0e0ff; margin: 0; }
.page-header p { font-size: 12px; color: rgba(255,255,255,0.5); margin: 4px 0; }
.header-stats { display: flex; gap: 24px; margin-top: 8px; }
.predict-result { margin-top: 12px; padding: 12px; background: rgba(102,126,234,0.08); border-radius: 10px; }
.pr-trend { font-size: 16px; font-weight: 600; }
.pr-trend.up { color: #4ade80; }
.pr-trend.down { color: #f87171; }
.pr-values { font-size: 13px; color: #e0e0e0; margin-top: 6px; }
.pr-conf { font-size: 11px; color: rgba(255,255,255,0.3); margin-top: 4px; }
@media (max-width: 768px) { .page-shell { padding: 10px; } }
</style>
