<template>
  <div class="weekly-report-panel">
    <div class="page-header">
      <h1>馃搳 AI杩愯惀鍛ㄦ姤</h1>
      <p>姣忓懆鑷姩姹囨€?路 璁㈠崟/鍟嗗搧/鐢ㄦ埛 路 绯荤粺鍋ュ悍 路 鍛婅寮傚父 路 閲囬泦绔炲搧</p>
    </div>

    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="24">
        <el-card shadow="never">
          <el-space>
            <el-button type="primary" :loading="genLoading" @click="doGenerate">馃 AI鐢熸垚鍛ㄦ姤</el-button>
            <el-button @click="loadReports">馃攧 鍒锋柊</el-button>
          </el-space>
        </el-card>
      </el-col>
    </el-row>

    <!-- 鏈€鏂板懆鎶?-->
    <el-card v-if="latestReport" shadow="never" style="margin-bottom:20px">
      <template #header>馃搵 鏈€鏂板懆鎶?鈥?绗瑊{ latestReport.week }}鍛?({{ latestReport.date }})</template>
      
      <el-row :gutter="16" style="margin-bottom:20px">
        <el-col :span="4" v-for="m in metrics" :key="m.label">
          <el-card shadow="never" class="metric-card">
            <div class="metric-val">{{ m.value }}</div>
            <div class="metric-label">{{ m.label }}</div>
          </el-card>
        </el-col>
      </el-row>

      <el-card shadow="never" style="background:#f8f9fa">
        <pre class="summary-text">{{ latestReport.summary }}</pre>
      </el-card>
    </el-card>

    <!-- 鍘嗗彶鍛ㄦ姤 -->
    <el-card shadow="never">
      <template #header>馃摎 鍘嗗彶鍛ㄦ姤 (鏈€杩?2鍛?</template>
      <el-timeline v-if="reports.length">
        <el-timeline-item v-for="r in reports" :key="r.id" :timestamp="'绗?+r.week+'鍛?路 '+r.date" placement="top">
          <el-card shadow="never">
            <pre class="summary-text" style="font-size:12px">{{ r.summary }}</pre>
          </el-card>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="鏆傛棤鍛ㄦ姤锛岀偣鍑讳笂鏂规寜閽敓鎴?/>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { generateWeeklyReport, listWeeklyReports, getLatestWeeklyReport } from '@/api/weekly'

const reports = ref([])
const latestReport = ref(null)
const genLoading = ref(false)

const metrics = computed(() => {
  if (!latestReport.value) return []
  const d = latestReport.value.data || {}
  return [
    { label: '璁㈠崟鎬绘暟', value: d.orders_total || 0 },
    { label: '鍟嗗搧鎬绘暟', value: d.products_total || 0 },
    { label: '鐢ㄦ埛鎬绘暟', value: d.users_total || 0 },
    { label: 'TODO', value: d.alerts_this_week || 0 },
    { label: '瀹㈡湇娑堟伅', value: d.customer_messages || 0 },
    { label: '鍋ュ悍鍒?, value: d.avg_health_score || 0 },
  ]
})

async function doGenerate() {
  genLoading.value = true
  try {
    const { data } = await generateWeeklyReport()
    latestReport.value = data.report
    ElMessage.success('鍛ㄦ姤宸茬敓鎴?)
    loadReports()
  } catch (e) { ElMessage.error('鐢熸垚澶辫触') }
  finally { genLoading.value = false }
}

async function loadReports() {
  try {
    const { data } = await listWeeklyReports()
    reports.value = data.reports || []
    if (!latestReport.value && reports.value.length) {
      latestReport.value = reports.value[0]
    }
  } catch (e) {}
}

onMounted(() => loadReports())
</script>

<style scoped>
.weekly-report-panel { padding: 0; }
.page-header { margin-bottom: 20px; }
.page-header h1 { font-size: 22px; margin: 0 0 4px; }
.page-header p { color: var(--text-muted); font-size: 13px; margin: 0; }
.metric-card { text-align: center; }
.metric-card .metric-val { font-size: 24px; font-weight: 700; color: #1677ff; }
.metric-card .metric-label { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
.summary-text { white-space: pre-wrap; font-family: inherit; margin: 0; line-height: 1.8; }
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>
