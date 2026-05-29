<template>
  <div class="self-healing-panel">
    <div class="page-header">
      <h1>🩺 异常自愈中心</h1>
      <p>7×24自动巡检 · 智能诊断 · 自动修复 · 数字免疫系统</p>
    </div>

    <!-- 操作栏 -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="24">
        <el-card shadow="never">
          <el-space>
            <el-button type="primary" :loading="patrolLoading" @click="doPatrol">🔍 立即巡检</el-button>
            <el-button type="warning" :loading="fixLoading" @click="doAutoFix">🔧 一键自愈</el-button>
            <el-select v-model="historyDays" style="width:120px" @change="loadHistory">
              <el-option :value="1" label="最近1天"/>
              <el-option :value="7" label="最近7天"/>
              <el-option :value="30" label="最近30天"/>
            </el-select>
            <el-button @click="loadHistory">🔄 刷新</el-button>
          </el-space>
        </el-card>
      </el-col>
    </el-row>

    <!-- 统计卡片 -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6" v-for="card in statCards" :key="card.label">
        <el-card shadow="never" :class="['stat-card', card.type]">
          <div class="stat-value">{{ card.value }}</div>
          <div class="stat-label">{{ card.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 巡检结果 -->
    <el-card v-if="patrolResult" shadow="never" style="margin-bottom:20px">
      <template #header>📋 最新巡检结果</template>
      <el-descriptions :column="3" border size="small">
        <el-descriptions-item label="检查项">{{ patrolResult.total_checks || 0 }}</el-descriptions-item>
        <el-descriptions-item label="通过">{{ patrolResult.checks_passed || 0 }}</el-descriptions-item>
        <el-descriptions-item label="发现问题">{{ (patrolResult.issues || []).length }}</el-descriptions-item>
      </el-descriptions>
      <el-table v-if="patrolResult.issues && patrolResult.issues.length" :data="patrolResult.issues" size="small" style="margin-top:12px">
        <el-table-column prop="severity" label="级别" width="80">
          <template #default="{row}"><el-tag :type="sevType(row.severity)" size="small">{{ row.severity }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="source" label="来源" width="100"/>
        <el-table-column prop="detail" label="详情"/>
      </el-table>
      <el-empty v-else description="一切正常，未发现异常" :image-size="60"/>
    </el-card>

    <!-- 修复结果 -->
    <el-card v-if="fixResult" shadow="never" style="margin-bottom:20px">
      <template #header>🔧 修复结果</template>
      <el-descriptions :column="3" border size="small">
        <el-descriptions-item label="尝试修复">{{ fixResult.attempted || 0 }}</el-descriptions-item>
        <el-descriptions-item label="已修复">{{ fixResult.fixed || 0 }}</el-descriptions-item>
        <el-descriptions-item label="失败">{{ fixResult.failed || 0 }}</el-descriptions-item>
      </el-descriptions>
      <el-table v-if="fixResult.results && fixResult.results.length" :data="fixResult.results" size="small" style="margin-top:12px">
        <el-table-column prop="id" label="异常ID" width="120"/>
        <el-table-column prop="result.action" label="操作"/>
        <el-table-column label="状态" width="100">
          <template #default="{row}"><el-tag :type="row.result.fixed ? 'success' : 'danger'" size="small">{{ row.result.fixed ? '已修复' : '失败' }}</el-tag></template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 异常历史 -->
    <el-card shadow="never">
      <template #header>📊 异常历史 (最近{{ historyDays }}天)</template>
      <el-table :data="anomalies" size="small" v-loading="historyLoading" empty-text="暂无异常记录，系统运行正常">
        <el-table-column prop="id" label="ID" width="100"/>
        <el-table-column prop="severity" label="级别" width="80">
          <template #default="{row}"><el-tag :type="sevType(row.severity)" size="small">{{ row.severity }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="source" label="来源" width="100"/>
        <el-table-column prop="description" label="描述" min-width="200"/>
        <el-table-column prop="detected_at" label="检测时间" width="170"/>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{row}">
            <el-tag :type="row.status==='resolved'?'success':row.status==='open'?'danger':'warning'" size="small">
              {{ row.status === 'resolved' ? '已解决' : row.status === 'open' ? '待处理' : '处理中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{row}">
            <el-button v-if="row.status !== 'resolved'" type="primary" size="small" link @click="doResolve(row.id)">标记解决</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { runPatrol, autoFix, getAnomalyHistory, resolveAnomaly } from '@/api/heal'

const patrolLoading = ref(false)
const fixLoading = ref(false)
const historyLoading = ref(false)
const historyDays = ref(7)
const patrolResult = ref(null)
const fixResult = ref(null)
const anomalies = ref([])
const historySummary = ref({})

const statCards = computed(() => [
  { label: '异常总数', value: historySummary.value.total || 0, type: 'total' },
  { label: '待处理', value: historySummary.value.open || 0, type: 'open' },
  { label: '已解决', value: historySummary.value.resolved || 0, type: 'resolved' },
  { label: '自动修复', value: historySummary.value.auto_fixed || 0, type: 'auto' },
])

function sevType(sev) {
  return { P1: 'danger', P2: 'warning', P3: '', P4: 'info' }[sev] || ''
}

async function doPatrol() {
  patrolLoading.value = true
  try {
    const { data } = await runPatrol()
    patrolResult.value = data
    ElMessage.success(`巡检完成：${data.checks_passed || 0}项通过，${(data.issues || []).length}个问题`)
  } catch (e) {
    ElMessage.error('巡检失败')
  } finally { patrolLoading.value = false }
}

async function doAutoFix() {
  fixLoading.value = true
  try {
    const { data } = await autoFix()
    fixResult.value = data
    ElMessage.success(`修复完成：${data.fixed || 0}/${data.attempted || 0}`)
    loadHistory()
  } catch (e) {
    ElMessage.error('修复失败')
  } finally { fixLoading.value = false }
}

async function loadHistory() {
  historyLoading.value = true
  try {
    const { data } = await getAnomalyHistory(historyDays.value)
    historySummary.value = data
    anomalies.value = data.recent || []
  } catch (e) {
    ElMessage.error('加载历史失败')
  } finally { historyLoading.value = false }
}

async function doResolve(id) {
  try {
    await resolveAnomaly(id)
    ElMessage.success('已标记解决')
    loadHistory()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => loadHistory())
</script>

<style scoped>
.self-healing-panel { padding: 0; }
.page-header { margin-bottom: 20px; }
.page-header h1 { font-size: 22px; margin: 0 0 4px; }
.page-header p { color: var(--text-muted); font-size: 13px; margin: 0; }
.stat-card { text-align: center; }
.stat-card .stat-value { font-size: 32px; font-weight: 700; }
.stat-card .stat-label { font-size: 13px; color: var(--text-muted); margin-top: 4px; }
.stat-card.total .stat-value { color: #1677ff; }
.stat-card.open .stat-value { color: #ff4d4f; }
.stat-card.resolved .stat-value { color: #52c41a; }
.stat-card.auto .stat-value { color: #722ed1; }
</style>
