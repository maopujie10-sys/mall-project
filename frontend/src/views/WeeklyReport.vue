<template>
  <div class="weekly-report-panel">
    <div class="page-header">
      <h1>📊 AI运营周报</h1>
      <p>每周自动汇总 · 订单/商品/用户 · 系统健康 · 告警异常 · 采集竞品</p>
    </div>

    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="24">
        <el-card shadow="never">
          <el-space>
            <el-button type="primary" :loading="genLoading" @click="doGenerate">🤖 AI生成周报</el-button>
            <el-button @click="loadReports">🔄 刷新</el-button>
          </el-space>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最新周报 -->
    <el-card v-if="latestReport" shadow="never" style="margin-bottom:20px">
      <template #header>📋 最新周报 — 第{{ latestReport.week }}周 ({{ latestReport.date }})</template>
      
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

    <!-- 历史周报 -->
    <el-card shadow="never">
      <template #header>📚 历史周报 (最近12周)</template>
      <el-timeline v-if="reports.length">
        <el-timeline-item v-for="r in reports" :key="r.id" :timestamp="'第'+r.week+'周 · '+r.date" placement="top">
          <el-card shadow="never">
            <pre class="summary-text" style="font-size:12px">{{ r.summary }}</pre>
          </el-card>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无周报，点击上方按钮生成"/>
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
    { label: '订单总数', value: d.orders_total || 0 },
    { label: '商品总数', value: d.products_total || 0 },
    { label: '用户总数', value: d.users_total || 0 },
    { label: '本周告警', value: d.alerts_this_week || 0 },
    { label: '客服消息', value: d.customer_messages || 0 },
    { label: '健康分', value: d.avg_health_score || 0 },
  ]
})

async function doGenerate() {
  genLoading.value = true
  try {
    const { data } = await generateWeeklyReport()
    latestReport.value = data.report
    ElMessage.success('周报已生成')
    loadReports()
  } catch (e) { ElMessage.error('生成失败') }
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
</style>
