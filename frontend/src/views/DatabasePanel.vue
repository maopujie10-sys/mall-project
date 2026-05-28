<template>
  <div class="page-container db-panel">
    <div class="page-header"><h2>鏁版嵁搴撻潰鏉?/h2><p>MySQL 路 PostgreSQL 路 Redis 路 MongoDB 缁熶竴绠＄悊</p></div>

    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6" v-for="db in databases" :key="db.id">
        <el-card shadow="hover" class="db-card" :class="{active: activeDb===db.id}" @click="selectDb(db.id)">
          <div class="db-icon">{{ db.icon }}</div>
          <h3>{{ db.name }}</h3>
          <el-tag :type="db.type==='MySQL'?'':db.type==='PostgreSQL'?'success':'warning'" size="small">{{ db.type }}</el-tag>
          <p>{{ db.host }}:{{ db.port }}</p>
          <div class="db-meta"><span :class="{online:db.online}">鈼?{{ db.online?'鍦ㄧ嚎':'绂荤嚎' }}</span><span>{{ db.tables }}琛?/span></div>
        </el-card>
      </el-col>
    </el-row>

    <div v-if="activeDb" class="db-workspace">
      <div class="workspace-header">
        <span>{{ activeDbName }}</span>
        <el-button type="primary" size="small" @click="showSqlEditor=!showSqlEditor">SQL鏌ヨ</el-button>
        <el-button size="small" @click="refreshTables">鍒锋柊</el-button>
      </div>

      <el-row :gutter="12">
        <el-col :span="6">
          <el-card shadow="never">
            <template #header><span>鏁版嵁琛?/span></template>
            <el-menu :default-active="activeTable" @select="selectTable">
              <el-menu-item v-for="t in tables" :key="t" :index="t">{{ t }}</el-menu-item>
            </el-menu>
          </el-card>
        </el-col>
        <el-col :span="18">
          <el-card shadow="never" v-if="activeTable">
            <template #header><span>{{ activeTable }} 鈥?{{ tableRowCount }} 琛?/span></template>
            <el-table :data="tableData" stripe max-height="calc(100vh - 420px)" border size="small">
              <el-table-column v-for="col in tableColumns" :key="col" :prop="col" :label="col" min-width="130" show-overflow-tooltip />
            </el-table>
          </el-card>
          <el-empty v-else description="閫夋嫨宸︿晶鏁版嵁琛ㄦ煡鐪? />
        </el-col>
      </el-row>
    </div>

    <el-dialog v-model="showSqlEditor" title="SQL 鏌ヨ" width="700px">
      <el-input v-model="sqlQuery" type="textarea" :rows="6" placeholder="SELECT * FROM ..." />
      <el-button type="primary" @click="runSql" :loading="sqlRunning" style="margin-top:12px">鎵ц</el-button>
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

const tables = ref([])
const dbStatus = ref({ connected: false, size: '鏈煡', tables: 0 })
const loading = ref(false)

async function fetchDBStatus() {
  loading.value = true
  try {
    const { data: s } = await agentApi.get('/db/status')
    dbStatus.value = { connected: s.connected || false, size: s.size || '鏈煡', tables: s.table_count || 0 }
    const { data: t } = await agentApi.get('/db/tables')
    tables.value = (t.tables || []).map(function(name) { return { name: name, rows: '?' } })
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