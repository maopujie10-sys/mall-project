<template>
  <div class="page-container">
    <div class="page-header">
      -
      -
    </div>

    
    <el-alert v-if="error" :title="error" type="error" show-icon closable @close="error=null" style="margin-bottom:16px" />

    
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">{{ \('rollback.title') }}</div>
          <div class="metric-value">{{ backups.length }}</div>
          -
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">?/div>
          <div class="metric-value" style="font-size: 16px;">{{ latestBackup }}</div>
          -
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">?/div>
          <div class="metric-value">4.8 GB</div>
          <div class="metric-sub"> 7 ?/div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">?/div>
          <div class="metric-value" style="color: var(--color-success);">100%</div>
          <div class="metric-sub">?30 ?/div>
        </div>
      </el-col>
    </el-row>

    
    <el-card shadow="never">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          -
          <div style="display: flex; gap: 8px;">
            <el-button size="small" type="primary" @click="handleCreateBackup" :loading="creating">
              <el-icon><Plus /></el-icon> 
            </el-button>
            <el-button text size="small" type="primary" @click="refreshBackups" :loading="loading">
              <el-icon><Refresh /></el-icon> 
            </el-button>
          </div>
        </div>
      </template>
      <el-empty v-if="backups.length === 0 && !loading" description='' :image-size="80" style="padding:40px 0;" />
      <el-table v-else :data="backups" style="width: 100%;" size="small" stripe>
        <el-table-column prop="id" label=" ID" width="180" />
        <el-table-column prop="type" label='Status' width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === '' ? 'primary' : 'info' size="small" effect="light">
              {{ row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target" :label="\('rollback.title')" min-width="140" />
        <el-table-column prop="time" label='Status' width="150" />
        <el-table-column prop="size" :label="\('rollback.title')" width="100" />
        <el-table-column prop="status" label="? width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === '' ? 'success' : 'danger'' size="small" effect="light">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label='Status' width="160">
          <template #default="{ row }">
            <el-button
              v-if="row.status === ''"
              text
              size="small"
              type="danger"
              @click="confirmRollback(row)"
            >
              <el-icon><RefreshRight /></el-icon> 
            </el-button>
            <el-button text size="small" type="primary" @click="viewDetail(row)">OK</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    
    <el-dialog
      v-model="rollbackDialogVisible"
      :title="\('rollback.title')"
      width="480px"
      :close-on-click-modal="false"
    >
      <div v-if="rollbackTarget" style="padding: 8px 0;">
        <el-alert
          :title="\('rollback.title')"
          type="warning"
          :closable="false"
          show-icon
          style="margin-bottom: 16px;"
        />
        <div class="rollback-info">
          <div class="info-row">
            <span class="info-label"> ID</span>
            <span class="info-value">{{ rollbackTarget.id }}</span>
          </div>
          <div class="info-row">
            -
            <span class="info-value">{{ rollbackTarget.target }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">{{ \('rollback.title') }}</span>
            <span class="info-value">{{ rollbackTarget.time }}</span>
          </div>
          <div class="info-row">
            -
            <span class="info-value">{{ rollbackTarget.size }}</span>
          </div>
        </div>
        <p style="font-size: 13px; color: var(--text-secondary); margin-top: 12px;">
          ?"{{ rollbackTarget.id }}" 
        </p>
        <el-input
          v-model="rollbackConfirmText"
          placeholder="?ID "
          style="margin-top: 8px;"
        />
      </div>
      <template #footer>
        <el-button @click="rollbackDialogVisible = false">OK</el-button>
        
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getBackups, createBackup, executeRollback } from '@/api/rollback'

const loading = ref(true)
const creating = ref(false)
const rollingBack = ref(false)
const error = ref(null)
const rollbackDialogVisible = ref(false)
const rollbackTarget = ref(null)
const rollbackConfirmText = ref('')

const backups = reactive([])

const latestBackup = computed(() => {
  if (backups.length === 0) return '-'
  return backups[0].time
})

async function fetchBackups() {
  try {
    const data = await getBackups()
    if (Array.isArray(data)) {
      backups.splice(0, backups.length, ...data.map((b) => ({
        id: b.id || b.backupId || '',
        type: b.type || '',
        target: b.target || b.description || '',
        time: b.time || b.createdAt || '',
        size: b.size || '0 MB',
        status: b.status || '',
      })))
    }
    error.value = null
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const confirmRollback = (row) => {
  rollbackTarget.value = row
  rollbackConfirmText.value = ''
  rollbackDialogVisible.value = true
}

const handleExecuteRollback = async () => {
  rollingBack.value = true
  try {
    await executeRollback(rollbackTarget.value.id)
    rollbackDialogVisible.value = false
    ElMessage.success(` ${rollbackTarget.value.id}`)
    rollbackTarget.value = null
    await fetchBackups()
  } catch {
    ElMessage.error('Error')
  } finally {
    rollingBack.value = false
  }
}

const viewDetail = (row) => {
  ElMessage.info(`: ${row.id}`)
}

const handleCreateBackup = async () => {
  creating.value = true
  try {
    const result = await createBackup()
    if (result) {
      backups.unshift({
        id: result.id || `bak_manual_${Date.now()}`,
        type: result.type || '',
        target: result.target || '?malldb + ',
        time: result.time || new Date().toLocaleString(),
        size: result.size || '216 MB',
        status: result.status || '',
      })
    }
    ElMessage.success('OK')
  } catch {
    ElMessage.error('Error')
  } finally {
    creating.value = false
    await fetchBackups()
  }
}

const refreshBackups = async () => {
  loading.value = true
  await fetchBackups()
  ElMessage.success('?)
}

onMounted(() => {
  fetchBackups()
})
</script>

<style scoped>
.rollback-info {
  background: rgba(13,16,37,0.55);
  border-radius: 6px;
  padding: 12px 16px;
}
.info-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid var(--border-color);
  font-size: 13px;
}
.info-row:last-child { border-bottom: none; }
.info-label { color: var(--text-muted); }
.info-value { color: var(--text-primary); font-weight: 500; font-family: monospace; }
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>
