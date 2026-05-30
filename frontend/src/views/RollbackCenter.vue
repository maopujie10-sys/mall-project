<template>
  <div class="page-container">
    <div class="page-header">
      <h2>鍥炴粴涓績</h2>
      <p>澶囦唤绠＄悊 路 鐗堟湰鍥炴粴 路 鏁版嵁鎭㈠</p>
    </div>

    <!-- 閿欒鎻愮ず -->
    <el-alert v-if="error" :title="error" type="error" show-icon closable @close="error=null" style="margin-bottom:16px" />

    <!-- 缁熻姒傝 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">澶囦唤鎬绘暟</div>
          <div class="metric-value">{{ backups.length }}</div>
          <div class="metric-sub">鍏ㄩ儴澶囦唤璁板綍</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">鏈€杩戝浠</div>
          <div class="metric-value" style="font-size: 16px;">{{ latestBackup }}</div>
          <div class="metric-sub">鑷姩澶囦唤正常</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">鎬诲崰鐢ㄧ┖闂</div>
          <div class="metric-value">4.8 GB</div>
          <div class="metric-sub">淇濈暀 7 澶╁巻鍙</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">鍥炴粴鎴愬姛鐜</div>
          <div class="metric-value" style="color: var(--color-success);">100%</div>
          <div class="metric-sub">杩?30 澶</div>
        </div>
      </el-col>
    </el-row>

    <!-- 澶囦唤璁板綍琛ㄦ牸 -->
    <el-card shadow="never">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: 600;">澶囦唤璁板綍</span>
          <div style="display: flex; gap: 8px;">
            <el-button size="small" type="primary" @click="handleCreateBackup" :loading="creating">
              <el-icon><Plus /></el-icon> 鎵嬪姩澶囦唤
            </el-button>
            <el-button text size="small" type="primary" @click="refreshBackups" :loading="loading">
              <el-icon><Refresh /></el-icon> 刷新
            </el-button>
          </div>
        </div>
      </template>
      <el-empty v-if="backups.length === 0 && !loading" description="鏆傛棤澶囦唤璁板綍" :image-size="80" style="padding:40px 0;" />
      <el-table v-else :data="backups" style="width: 100%;" size="small" stripe>
        <el-table-column prop="id" label="澶囦唤 ID" width="180" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === '鍏ㄩ噺' ? 'primary' : 'info'" size="small" effect="light">
              {{ row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target" label="澶囦唤鐩爣" min-width="140" />
        <el-table-column prop="time" label="澶囦唤时间" width="150" />
        <el-table-column prop="size" label="澶у皬" width="100" />
        <el-table-column prop="status" label="..." width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === '鎴愬姛' ? 'success' : 'danger'" size="small" effect="light">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button
              v-if="row.status === '鎴愬姛'"
              text
              size="small"
              type="danger"
              @click="confirmRollback(row)"
            >
              <el-icon><RefreshRight /></el-icon> 鍥炴粴
            </el-button>
            <el-button text size="small" type="primary" @click="viewDetail(row)">
              璇︽儏
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 鍥炴粴确认寮圭獥 -->
    <el-dialog
      v-model="rollbackDialogVisible"
      title="鍥炴粴确认"
      width="480px"
      :close-on-click-modal="false"
    >
      <div v-if="rollbackTarget" style="padding: 8px 0;">
        <el-alert
          title="姝ゆ搷浣滃皢瑕嗙洊褰撳墠杩愯鐗堟湰锛岃浠旂粏确认"
          type="warning"
          :closable="false"
          show-icon
          style="margin-bottom: 16px;"
        />
        <div class="rollback-info">
          <div class="info-row">
            <span class="info-label">澶囦唤 ID</span>
            <span class="info-value">{{ rollbackTarget.id }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">澶囦唤鐩爣</span>
            <span class="info-value">{{ rollbackTarget.target }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">澶囦唤时间</span>
            <span class="info-value">{{ rollbackTarget.time }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">澶囦唤澶у皬</span>
            <span class="info-value">{{ rollbackTarget.size }}</span>
          </div>
        </div>
        <p style="font-size: 13px; color: var(--text-secondary); margin-top: 12px;">
          璇疯緭鍏?"{{ rollbackTarget.id }}" 确认鍥炴粴操作
        </p>
        <el-input
          v-model="rollbackConfirmText"
          placeholder="璇疯緭鍏ュ浠?ID 确认"
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
          确认鍥炴粴
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
        type: b.type || '鍏ㄩ噺',
        target: b.target || b.description || '',
        time: b.time || b.createdAt || '',
        size: b.size || '0 MB',
        status: b.status || '鎴愬姛',
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
    ElMessage.success(`宸插洖婊氳嚦 ${rollbackTarget.value.id}`)
    rollbackTarget.value = null
    await fetchBackups()
  } catch {
    ElMessage.error('鍥炴粴澶辫触')
  } finally {
    rollingBack.value = false
  }
}

const viewDetail = (row) => {
  ElMessage.info(`鏌ョ湅澶囦唤璇︽儏: ${row.id}`)
}

const handleCreateBackup = async () => {
  creating.value = true
  try {
    const result = await createBackup()
    if (result) {
      backups.unshift({
        id: result.id || `bak_manual_${Date.now()}`,
        type: result.type || '鎵嬪姩',
        target: result.target || '鏁版嵁搴?malldb + 閰嶇疆鏂囦欢',
        time: result.time || new Date().toLocaleString(),
        size: result.size || '216 MB',
        status: result.status || '鎴愬姛',
      })
    }
    ElMessage.success('鎵嬪姩澶囦唤瀹屾垚')
  } catch {
    ElMessage.error('澶囦唤澶辫触')
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
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>
