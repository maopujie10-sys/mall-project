<template>
  <div class="page-container db-panel">
    <div class="page-header"><h2>数据库面板</h2><p>MySQL · PostgreSQL · Redis · MongoDB 统一管理</p></div>

    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6" v-for="db in databases" :key="db.id">
        <el-card shadow="hover" class="db-card" :class="{active: activeDb===db.id}" @click="selectDb(db.id)">
          <div class="db-icon">{{ db.icon }}</div>
          <h3>{{ db.name }}</h3>
          <el-tag :type="db.type==='MySQL'?'':db.type==='PostgreSQL'?'success':'warning'" size="small">{{ db.type }}</el-tag>
          <p>{{ db.host }}:{{ db.port }}</p>
          <div class="db-meta"><span :class="{online:db.online}">● {{ db.online?'在线':'离线' }}</span><span>{{ db.tables }}表</span></div>
        </el-card>
      </el-col>
    </el-row>

    <div v-if="activeDb" class="db-workspace">
      <div class="workspace-header">
        <span>{{ activeDbName }}</span>
        <el-button type="primary" size="small" @click="showSqlEditor=!showSqlEditor">SQL查询</el-button>
        <el-button size="small" @click="refreshTables">刷新</el-button>
      </div>

      <el-row :gutter="12">
        <el-col :span="6">
          <el-card shadow="never">
            <template #header><span>数据表</span></template>
            <el-menu :default-active="activeTable" @select="selectTable">
              <el-menu-item v-for="t in tables" :key="t" :index="t">{{ t }}</el-menu-item>
            </el-menu>
          </el-card>
        </el-col>
        <el-col :span="18">
          <el-card shadow="never" v-if="activeTable">
            <template #header><span>{{ activeTable }} — {{ tableRowCount }} 行</span></template>
            <el-table :data="tableData" stripe max-height="calc(100vh - 420px)" border size="small">
              <el-table-column v-for="col in tableColumns" :key="col" :prop="col" :label="col" min-width="130" show-overflow-tooltip />
            </el-table>
          </el-card>
          <el-empty v-else description="选择左侧数据表查看" />
        </el-col>
      </el-row>
    </div>

    <el-dialog v-model="showSqlEditor" title="SQL 查询" width="700px">
      <el-input v-model="sqlQuery" type="textarea" :rows="6" placeholder="SELECT * FROM ..." />
      <el-button type="primary" @click="runSql" :loading="sqlRunning" style="margin-top:12px">执行</el-button>
      <el-table :data="sqlResult" stripe border size="small" style="margin-top:16px" max-height="300" v-if="sqlResult.length">
        <el-table-column v-for="col in sqlColumns" :key="col" :prop="col" :label="col" min-width="120" show-overflow-tooltip />
      </el-table>
      <el-alert v-if="sqlError" :title="sqlError" type="error" style="margin-top:12px" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { agentApi } from '@/api/index'

const databases = ref([
  { id: 'mysql', icon: '🐬', name: 'MySQL', type: 'MySQL', host: 'localhost', port: 3306, online: true, tables: 0 },
  { id: 'pg', icon: '🐘', name: 'PostgreSQL', type: 'PostgreSQL', host: 'localhost', port: 5432, online: false, tables: 0 },
  { id: 'redis', icon: '🔴', name: 'Redis', type: 'Redis', host: 'localhost', port: 6379, online: true, tables: 0 },
  { id: 'mongo', icon: '🍃', name: 'MongoDB', type: 'MongoDB', host: 'localhost', port: 27017, online: false, tables: 0 },
])
const activeDb = ref(null)
const activeDbName = ref('')
const activeTable = ref(null)
const tableRowCount = ref(0)
const tableData = ref([])
const tableColumns = ref([])
const showSqlEditor = ref(false)
const sqlQuery = ref('')
const sqlRunning = ref(false)
const sqlResult = ref([])
const sqlColumns = ref([])
const sqlError = ref('')
const tables = ref([])
const dbStatus = ref({ connected: false, size: '未知', tables: 0 })
const loading = ref(false)

async function selectDb(dbId) {
  activeDb.value = dbId
  const db = databases.value.find(d => d.id === dbId)
  activeDbName.value = db ? db.name : ''
  activeTable.value = null
  tableData.value = []
  await fetchDBStatus()
}
async function refreshTables() { await fetchDBStatus(); ElMessage.success('已刷新') }
async function selectTable(index) {
  activeTable.value = index
  try {
    const r = await agentApi.get('/db/table/' + index)
    if (r?.ok || r?.rows) { tableData.value = r.rows || []; tableColumns.value = r.columns || Object.keys(tableData.value[0] || {}); tableRowCount.value = tableData.value.length }
    else { tableData.value = []; tableColumns.value = []; tableRowCount.value = 0 }
  } catch { tableData.value = []; tableColumns.value = []; tableRowCount.value = 0 }
}
async function runSql() {
  if (!sqlQuery.value) { ElMessage.warning('请输入SQL'); return }
  sqlRunning.value = true; sqlError.value = ''
  try {
    const r = await agentApi.post('/db/query', { sql: sqlQuery.value })
    if (r?.ok) { sqlResult.value = r.rows || []; sqlColumns.value = r.columns || Object.keys(sqlResult.value[0] || {}) }
    else sqlError.value = r?.error || '查询失败'
  } catch (e) { sqlError.value = e.message }
  sqlRunning.value = false
}

async function fetchDBStatus() {
  loading.value = true
  try {
    const r = await agentApi.get('/db/status')
    dbStatus.value = { connected: r?.connected || false, size: r?.size || '未知', tables: r?.table_count || 0 }
    const r2 = await agentApi.get('/db/tables')
    tables.value = (r2?.tables || []).map(function(name) { return typeof name === 'string' ? name : name.name || name })
    // Update table count on active db card
    const db = databases.value.find(d => d.id === activeDb.value)
    if (db) db.tables = tables.value.length
  } catch {
    dbStatus.value.connected = false
  } finally { loading.value = false }
}

function refreshDB() { fetchDBStatus() }
onMounted(function() { fetchDBStatus() })
</script>

<style scoped>
.db-panel { padding: 24px; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 18px; margin: 0 0 4px; }
.page-header p { color: var(--text-muted); font-size: 13px; margin: 0; }
.db-card { text-align: center; cursor: pointer; transition: all 0.2s; }
.db-card:hover { transform: translateY(-4px); }
.db-card.active { border-color: #667eea; box-shadow: 0 0 20px rgba(102,126,234,0.2); }
.db-icon { font-size: 40px; }
.db-card h3 { margin: 8px 0; font-size: 14px; }
.db-card p { font-size: 11px; color: var(--text-muted); margin: 6px 0; }
.db-meta { display: flex; justify-content: center; gap: 12px; font-size: 11px; }
.db-meta .online { color: #52c41a; }
.db-workspace { margin-top: 16px; }
.workspace-header { display: flex; gap: 12px; align-items: center; margin-bottom: 16px; font-weight: 600; }
</style>