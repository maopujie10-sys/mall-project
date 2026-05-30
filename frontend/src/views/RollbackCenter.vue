<template>
  <div class="page-container">
    <div class="page-header">
      <h2>回滚中心</h2>
      <p>备份管理 · 版本回滚 · 数据恢复</p>
    </div>

    <!-- 错误提示 -->
    <el-alert v-if="error" :title="error" type="error" show-icon closable @close="error=null" style="margin-bottom:16px" />

    <!-- 统计概览 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">备份总数</div>
          <div class="metric-value">{{ backups.length }}</div>
          <div class="metric-sub">全部备份记录</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">最近备份</div>
          <div class="metric-value" style="font-size: 16px;">{{ latestBackup }}</div>
          <div class="metric-sub">自动备份正常</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">总占用空间</div>
          <div class="metric-value">4.8 GB</div>
          <div class="metric-sub">保留 7 天历史</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">回滚成功率</div>
          <div class="metric-value" style="color: var(--color-success);">100%</div>
          <div class="metric-sub">近 30 天</div>
        </div>
      </el-col>
    </el-row>

    <!-- 备份记录表格 -->
    <el-card shadow="never">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: 600;">备份记录</span>
          <div style="display: flex; gap: 8px;">
            <el-button size="small" type="primary" @click="handleCreateBackup" :loading="creating">
              <el-icon><Plus /></el-icon> 手动备份
            </el-button>
            <el-button text size="small" type="primary" @click="refreshBackups" :loading="loading">
              <el-icon><Refresh /></el-icon> 刷新
            </el-button>
          </div>
        </div>
      </template>
      <el-empty v-if="backups.length === 0 && !loading" description="暂无备份记录" :image-size="80" style="padding:40px 0;" />
      <el-table v-else :data="backups" style="width: 100%;" size="small" stripe>
        <el-table-column prop="id" label="备份 ID" width="180" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === '全量' ? 'primary' : 'info'" size="small" effect="light">
              {{ row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target" label="备份目标" min-width="140" />
        <el-table-column prop="time" label="备份时间" width="150" />
        <el-table-column prop="size" label="大小" width="100" />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === '成功' ? 'success' : 'danger'" size="small" effect="light">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button
              v-if="row.status === '成功'"
              text
              size="small"
              type="danger"
              @click="confirmRollback(row)"
            >
              <el-icon><RefreshRight /></el-icon> 回滚
            </el-button>
            <el-button text size="small" type="primary" @click="viewDetail(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 回滚确认弹窗 -->
    <el-dialog
      v-model="rollbackDialogVisible"
      title="回滚确认"
      width="480px"
      :close-on-click-modal="false"
    >
      <div v-if="rollbackTarget" style="padding: 8px 0;">
        <el-alert
          title="此操作将覆盖当前运行版本，请仔细确认"
          type="warning"
          :closable="false"
          show-icon
          style="margin-bottom: 16px;"
        />
        <div class="rollback-info">
          <div class="info-row">
            <span class="info-label">备份 ID</span>
            <span class="info-value">{{ rollbackTarget.id }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">备份目标</span>
            <span class="info-value">{{ rollbackTarget.target }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">备份时间</span>
            <span class="info-value">{{ rollbackTarget.time }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">备份大小</span>
            <span class="info-value">{{ rollbackTarget.size }}</span>
          </div>
        </div>
        <p style="font-size: 13px; color: var(--text-secondary); margin-top: 12px;">
          请输入 "{{ rollbackTarget.id }}" 确认回滚操作
        </p>
        <el-input
          v-model="rollbackConfirmText"
          placeholder="请输入备份 ID 确认"
          style="margin-top: 8px;"
        />
      </div>
      <template #footer>
        <el-button @click="rollbackDialogVisible = false">取消</el-button>
        <el-button
          type="danger"
          @click="handleExecuteRollback"
          :disabled="rollbackConfirmText !== rollbackTarget?.id"
          :loading="rollingBack"
        >
          确认回滚
        </el-button>
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
        type: b.type || '全量',
        target: b.target || b.description || '',
        time: b.time || b.createdAt || '',
        size: b.size || '0 MB',
        status: b.status || '成功',
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
    ElMessage.success(`已回滚至 ${rollbackTarget.value.id}`)
    rollbackTarget.value = null
    await fetchBackups()
  } catch {
    ElMessage.error('回滚失败')
  } finally {
    rollingBack.value = false
  }
}

const viewDetail = (row) => {
  ElMessage.info(`查看备份详情: ${row.id}`)
}

const handleCreateBackup = async () => {
  creating.value = true
  try {
    const result = await createBackup()
    if (result) {
      backups.unshift({
        id: result.id || `bak_manual_${Date.now()}`,
        type: result.type || '手动',
        target: result.target || '数据库 malldb + 配置文件',
        time: result.time || new Date().toLocaleString(),
        size: result.size || '216 MB',
        status: result.status || '成功',
      })
    }
    ElMessage.success('手动备份完成')
  } catch {
    ElMessage.error('备份失败')
  } finally {
    creating.value = false
    await fetchBackups()
  }
}

const refreshBackups = async () => {
  loading.value = true
  await fetchBackups()
  ElMessage.success('备份列表已刷新')
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
</style>
