<template>
  <div class="self-healing-panel">
    <div class="page-header">
      <h1>馃┖ 寮傚父鑷剤涓績</h1>
      <p>7脳24鑷姩宸℃ 路 鏅鸿兘璇婃柇 路 鑷姩淇 路 鏁板瓧鍏嶇柅绯荤粺</p>
    </div>

    <!-- 鎿嶄綔鏍?-->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="24">
        <el-card shadow="never">
          <el-space>
            <el-button type="primary" :loading="patrolLoading" @click="doPatrol">馃攳 绔嬪嵆宸℃</el-button>
            <el-button type="warning" :loading="fixLoading" @click="doAutoFix">馃敡 涓€閿嚜鎰</el-button>
            <el-select v-model="historyDays" style="width:120px" @change="loadHistory">
              <el-option :value="1" label="鏈€杩?澶?/>
              <el-option :value="7" label="鏈€杩?澶?/>
              <el-option :value="30" label="鏈€杩?0澶?/>
            </el-select>
            <el-button @click="loadHistory">馃攧 鍒锋柊</el-button>
          </el-space>
        </el-card>
      </el-col>
    </el-row>

    <!-- 缁熻鍗＄墖 -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6" v-for="card in statCards" :key="card.label">
        <el-card shadow="never" :class="['stat-card', card.type]">
          <div class="stat-value">{{ card.value }}</div>
          <div class="stat-label">{{ card.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 宸℃缁撴灉 -->
    <el-card v-if="patrolResult" shadow="never" style="margin-bottom:20px">
      <template #header>馃搵 鏈€鏂板贰妫€缁撴灉</template>
      <el-descriptions :column="3" border size="small">
        <el-descriptions-item label="妫€鏌ラ」">{{ patrolResult.total_checks || 0 }}</el-descriptions-item>
        <el-descriptions-item label="閫氳繃">{{ patrolResult.checks_passed || 0 }}</el-descriptions-item>
        <el-descriptions-item label="鍙戠幇闂">{{ (patrolResult.issues || []).length }}</el-descriptions-item>
      </el-descriptions>
      <el-table v-if="patrolResult.issues && patrolResult.issues.length" :data="patrolResult.issues" size="small" style="margin-top:12px">
        <el-table-column prop="severity" label="绾у埆" width="80">
          <template #default="{row}"><el-tag :type="sevType(row.severity)" size="small">{{ row.severity }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="source" label="鏉ユ簮" width="100"/>
        <el-table-column prop="detail" label="璇︽儏"/>
      </el-table>
      <el-empty v-else description="涓€鍒囨甯革紝鏈彂鐜板紓甯? :image-size="60"/>
    </el-card>

    <!-- 淇缁撴灉 -->
    <el-card v-if="fixResult" shadow="never" style="margin-bottom:20px">
      <template #header>馃敡 淇缁撴灉</template>
      <el-descriptions :column="3" border size="small">
        <el-descriptions-item label="灏濊瘯淇">{{ fixResult.attempted || 0 }}</el-descriptions-item>
        <el-descriptions-item label="宸蹭慨澶?>{{ fixResult.fixed || 0 }}</el-descriptions-item>
        <el-descriptions-item label="澶辫触">{{ fixResult.failed || 0 }}</el-descriptions-item>
      </el-descriptions>
      <el-table v-if="fixResult.results && fixResult.results.length" :data="fixResult.results" size="small" style="margin-top:12px">
        <el-table-column prop="id" label="寮傚父ID" width="120"/>
        <el-table-column prop="result.action" label="鎿嶄綔"/>
        <el-table-column label="鐘舵€? width="100">
          <template #default="{row}"><el-tag :type="row.result.fixed ? 'success' : 'danger'" size="small">{{ row.result.fixed ? '宸蹭慨澶' : '澶辫触' }}</el-tag></template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 寮傚父鍘嗗彶 -->
    <el-card shadow="never">
      <template #header>馃搳 寮傚父鍘嗗彶 (鏈€杩憑{ historyDays }}澶?</template>
      <el-table :data="anomalies" size="small" v-loading="historyLoading" empty-text="鏆傛棤寮傚父璁板綍锛岀郴缁熻繍琛屾甯?>
        <el-table-column prop="id" label="ID" width="100"/>
        <el-table-column prop="severity" label="绾у埆" width="80">
          <template #default="{row}"><el-tag :type="sevType(row.severity)" size="small">{{ row.severity }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="source" label="鏉ユ簮" width="100"/>
        <el-table-column prop="description" label="鎻忚堪" min-width="200"/>
        <el-table-column prop="detected_at" label="妫€娴嬫椂闂? width="170"/>
        <el-table-column prop="status" label="鐘舵€? width="100">
          <template #default="{row}">
            <el-tag :type="row.status==='resolved'?'success':row.status==='open'?'danger':'warning'" size="small">
              {{ row.status === 'resolved' ' '宸茶В鍐' : row.status === 'open' ' '寰呭鐞' : '澶勭悊涓' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="鎿嶄綔" width="120">
          <template #default="{row}">
            <el-button v-if="row.status !== 'resolved'" type="primary" size="small" link @click="doResolve(row.id)">鏍囪瑙ｅ喅</el-button>
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
  { label: '寮傚父鎬绘暟', value: historySummary.value.total || 0, type: 'total' },
  { label: '寰呭鐞?, value: historySummary.value.open || 0, type: 'open' },
  { label: '宸茶В鍐?, value: historySummary.value.resolved || 0, type: 'resolved' },
  { label: '鑷姩淇', value: historySummary.value.auto_fixed || 0, type: 'auto' },
])

function sevType(sev) {
  return { P1: 'danger', P2: 'warning', P3: '', P4: 'info' }[sev] || ''
}

async function doPatrol() {
  patrolLoading.value = true
  try {
    const { data } = await runPatrol()
    patrolResult.value = data
    ElMessage.success(`宸℃瀹屾垚锛?{data.checks_passed || 0}椤归€氳繃锛?{(data.issues || []).length}涓棶棰榒)
  } catch (e) {
    ElMessage.error('宸℃澶辫触')
  } finally { patrolLoading.value = false }
}

async function doAutoFix() {
  fixLoading.value = true
  try {
    const { data } = await autoFix()
    fixResult.value = data
    ElMessage.success(`淇瀹屾垚锛?{data.fixed || 0}/${data.attempted || 0}`)
    loadHistory()
  } catch (e) {
    ElMessage.error('淇澶辫触')
  } finally { fixLoading.value = false }
}

async function loadHistory() {
  historyLoading.value = true
  try {
    const { data } = await getAnomalyHistory(historyDays.value)
    historySummary.value = data
    anomalies.value = data.recent || []
  } catch (e) {
    ElMessage.error('鍔犺浇鍘嗗彶澶辫触')
  } finally { historyLoading.value = false }
}

async function doResolve(id) {
  try {
    await resolveAnomaly(id)
    ElMessage.success('宸叉爣璁拌В鍐?)
    loadHistory()
  } catch (e) {
    ElMessage.error('鎿嶄綔澶辫触')
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
