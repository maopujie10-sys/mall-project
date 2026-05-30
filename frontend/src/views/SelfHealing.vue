<template>
  <div class="self-healing-panel">
    <div class="page-header">
      -
      <p>724      </p>
    </div>

    <!-- ?-->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="24">
        <el-card shadow="never">
          <el-space>
            
            <el-button type="warning" :loading="fixLoading" @click="doAutoFix"> ?/el-button>
            <el-select v-model="historyDays" style="width:120px" @change="loadHistory">
              <el-option :value="1" label="??/>
              <el-option :value="7" label="??/>
              <el-option :value="30" label="?0?/>
            </el-select>
            <el-button @click="loadHistory">OK</el-button>
          </el-space>
        </el-card>
      </el-col>
    </el-row>

    
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6" v-for="card in statCards" :key="card.label">
        <el-card shadow="never" :class="['stat-card', card.type]">
          <div class="stat-value">{{ card.value }}</div>
          <div class="stat-label">{{ card.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    
    <el-card v-if="patrolResult" shadow="never" style="margin-bottom:20px">
      <template #header> </template>
      <el-descriptions :column="3" border size="small">
        <el-descriptions-item :label="\('selfHeal.title')">{{ patrolResult.total_checks || 0 }}</el-descriptions-item>
        <el-descriptions-item label=''>{{ patrolResult.checks_passed || 0 }}</el-descriptions-item>
        <el-descriptions-item :label="\('selfHeal.title')">{{ (patrolResult.issues || []).length }}</el-descriptions-item>
      </el-descriptions>
      <el-table v-if="patrolResult.issues && patrolResult.issues.length" :data="patrolResult.issues" size="small" style="margin-top:12px">
        <el-table-column prop="severity" :label="\('selfHeal.title')" width="80">
          <template #default="{row}"><el-tag :type="sevType(row.severity)" size="small">{{ row.severity }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="source" :label="\('selfHeal.title')" width="100"/>
        <el-table-column prop="detail" :label="\('selfHeal.title')"/>
      </el-table>
      <el-empty v-else description="? :image-size="60"/>
    </el-card>

    
    <el-card v-if="fixResult" shadow="never" style="margin-bottom:20px">
      <template #header> </template>
      <el-descriptions :column="3" border size="small">
        <el-descriptions-item :label="\('selfHeal.title')">{{ fixResult.attempted || 0 }}</el-descriptions-item>
        <el-descriptions-item label="?>{{ fixResult.fixed || 0 }}</el-descriptions-item>
        <el-descriptions-item label=''>{{ fixResult.failed || 0 }}</el-descriptions-item>
      </el-descriptions>
      <el-table v-if="fixResult.results && fixResult.results.length" :data="fixResult.results" size="small" style="margin-top:12px">
        <el-table-column prop="id" label="ID" width="120"/>
        <el-table-column prop="result.action" label=''/>
        <el-table-column label="? width="100">
          <template #default="{row}"><el-tag :type="row.result.fixed ? 'success' : 'danger'' size="small">{{ row.result.fixed ? '? : '' }}</el-tag></template>
        </el-table-column>
      </el-table>
    </el-card>

    
    <el-card shadow="never">
      <template #header>  ({ historyDays }}?</template>
      <el-table :data="anomalies" size="small" v-loading="historyLoading" empty-text="?>
        <el-table-column prop="id" label="ID" width="100"/>
        <el-table-column prop="severity" :label="\('selfHeal.title')" width="80">
          <template #default="{row}"><el-tag :type="sevType(row.severity)" size="small">{{ row.severity }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="source" :label="\('selfHeal.title')" width="100"/>
        <el-table-column prop="description" label='' min-width="200"/>
        <el-table-column prop="detected_at" label="? width="170"/>
        <el-table-column prop="status" label="? width="100">
          <template #default="{row}">
            <el-tag :type="row.status==='resolved'?'success':row.status==='open'?'danger':'warning'' size="small">
              {{ row.status === 'resolved' ? '? : row.status === 'open' ? '? : '? }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label='' width="120">
          <template #default="{row}">
            <el-button v-if="row.status !== 'resolved'' type="primary" size="small" link @click="doResolve(row.id)"></el-button>
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
  { label: '', value: historySummary.value.total || 0, type: 'total' },
  { label: '?, value: historySummary.value.open || 0, type: 'open' },
  { label: '?, value: historySummary.value.resolved || 0, type: 'resolved' },
  { label: '', value: historySummary.value.auto_fixed || 0, type: 'auto' },
])

function sevType(sev) {
  return { P1: 'danger', P2: 'warning', P3: '', P4: 'info' }[sev] || ''
}

async function doPatrol() {
  patrolLoading.value = true
  try {
    const { data } = await runPatrol()
    patrolResult.value = data
    ElMessage.success(`?{data.checks_passed || 0}?{(data.issues || []).length})
  } catch (e) {
    ElMessage.error('Error')
  } finally { patrolLoading.value = false }
}

async function doAutoFix() {
  fixLoading.value = true
  try {
    const { data } = await autoFix()
    fixResult.value = data
    ElMessage.success(`?{data.fixed || 0}/${data.attempted || 0}`)
    loadHistory()
  } catch (e) {
    ElMessage.error('Error')
  } finally { fixLoading.value = false }
}

async function loadHistory() {
  historyLoading.value = true
  try {
    const { data } = await getAnomalyHistory(historyDays.value)
    historySummary.value = data
    anomalies.value = data.recent || []
  } catch (e) {
    ElMessage.error('OK')
  } finally { historyLoading.value = false }
}

async function doResolve(id) {
  try {
    await resolveAnomaly(id)
    ElMessage.success('?)
    loadHistory()
  } catch (e) {
    ElMessage.error('OK')
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
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>
