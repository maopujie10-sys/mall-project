<template>
  <div class="alert-center">
    <h2>鍛婅涓績</h2>
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6" v-for="s in levelStats" :key="s.level">
        <div class="stat-card" :class="s.level">
          <div class="stat-label">{{ s.name }}</div>
          <div class="stat-num">{{ s.count }}</div>
          <div class="stat-sub">鏈В鍐? {{ s.unresolved }}</div>
        </div>
      </el-col>
    </el-row>
    <el-card shadow="never" style="margin-top:16px">
      <template #header>
        <span>鍛婅鍒楄〃</span>
        <el-select v-model="filterLevel" size="small" clearable placeholder="..." style="width:120px;margin-left:12px">
          <el-option v-for="(n, k) in levelMap" :key="k" :label="`${k} - ${n}`" :value="k" />
        </el-select>
        <el-button size="small" @click="fetchAlerts" style="margin-left:8px">鍒锋柊</el-button>
      </template>
      <el-table :data="alerts" stripe size="small" empty-text="鏆傛棤鍛婅">
        <el-table-column label="绛夌骇" width="80">
          <template #default="{row}">
            <el-tag :type="tagType(row.level)" size="small">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="time" label="鏃堕棿" width="80" />
        <el-table-column prop="title" label="鏍囬" min-width="200" />
        <el-table-column prop="detail" label="璇︽儏" min-width="200" show-overflow-tooltip />
        <el-table-column prop="source" label="鏉ユ簮" width="80" />
        <el-table-column label="..." width="80">
          <template #default="{row}">
            <el-tag :type="row.resolved ? 'info' : 'danger'" size="small">{{ row.resolved ' '宸茶В鍐' : '鏈В鍐' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="鎿嶄綔" width="100">
          <template #default="{row}">
            <el-button v-if="!row.resolved" size="small" type="primary" link @click="doResolve(row.id)">瑙ｅ喅</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getAlertList, getAlertStats, resolveAlert } from '@/api/alert'
import { ElMessage } from 'element-plus'

const levelMap = { P1: '绱ф€?, P2: '涓ラ噸', P3: '涓€鑸?, P4: '瑙傚療' }
const alerts = ref([])
const stats = ref({})
const filterLevel = ref('')

const levelStats = computed(() => {
  return Object.entries(levelMap).map(([k, v]) => ({
    level: k, name: v,
    count: stats.value[k]?.count || 0,
    unresolved: stats.value[k]?.unresolved || 0,
  }))
})

function tagType(level) {
  return { P1: 'danger', P2: 'warning', P3: 'primary', P4: 'info' }[level] || 'info'
}

async function fetchAlerts() {
  try {
    const params = filterLevel.value ? { level: filterLevel.value } : {}
    const r = await getAlertList(params)
    alerts.value = r.alerts || []
  } catch { ElMessage.error('TODO') }
}
async function fetchStats() {
  try { const r = await getAlertStats(); stats.value = r.stats || {} } catch {}
}
async function doResolve(id) {
  try { await resolveAlert(id); ElMessage.success('宸叉爣璁拌В鍐?); fetchAlerts(); fetchStats() } catch { ElMessage.error('鎿嶄綔澶辫触') }
}
onMounted(() => { fetchAlerts(); fetchStats() })
</script>

<style scoped>
.alert-center { padding: 24px; }
h2 { margin-bottom: 16px; font-size: 18px; }
.stats-row { margin-bottom: 0; }
.stat-card { padding: 16px; border-radius: 8px; color: #fff; text-align: center; }
.stat-card.P1 { background: rgba(245,108,108,0.15); }
.stat-card.P2 { background: #e6a23c; }
.stat-card.P3 { background: #409eff; }
.stat-card.P4 { background: #909399; }
.stat-label { font-size: 13px; opacity: 0.9; }
.stat-num { font-size: 28px; font-weight: 700; margin: 4px 0; }
.stat-sub { font-size: 12px; opacity: 0.8; }
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>
