<template>
  <div class="page-container">
    <div class="page-header">
      <h2>閸ョ偞绮存稉顓炵妇</h2>
      <p>婢跺洣鍞ょ粻锛勬倞 璺?閻楀牊婀伴崶鐐寸泊 璺?閺佺増宓侀幁銏狀槻</p>
    </div>

    <!-- 闁挎瑨顕ら幓鎰仛 -->
    <el-alert v-if="error" :title="error" type="error" show-icon closable @close="error=null" style="margin-bottom:16px" />

    <!-- 缂佺喕顓稿鍌濐潔 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">婢跺洣鍞ら幀缁樻殶</div>
          <div class="metric-value">{{ backups.length }}</div>
          <div class="metric-sub">閸忋劑鍎存径鍥﹀敜鐠佹澘缍?/div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">閺堚偓鏉╂垵顦禒?/div>
          <div class="metric-value" style="font-size: 16px;">{{ latestBackup }}</div>
          <div class="metric-sub">閼奉亜濮╂径鍥﹀敜濮濓絽鐖?/div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">閹宕伴悽銊р敄闂?/div>
          <div class="metric-value">4.8 GB</div>
          <div class="metric-sub">娣囨繄鏆€ 7 婢垛晛宸婚崣?/div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">閸ョ偞绮撮幋鎰閻?/div>
          <div class="metric-value" style="color: var(--color-success);">100%</div>
          <div class="metric-sub">鏉?30 婢?/div>
        </div>
      </el-col>
    </el-row>

    <!-- 婢跺洣鍞ょ拋鏉跨秿鐞涖劍鐗?-->
    <el-card shadow="never">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: 600;">婢跺洣鍞ょ拋鏉跨秿</span>
          <div style="display: flex; gap: 8px;">
            <el-button size="small" type="primary" @click="handleCreateBackup" :loading="creating">
              <el-icon><Plus /></el-icon> 閹靛濮╂径鍥﹀敜
            </el-button>
            <el-button text size="small" type="primary" @click="refreshBackups" :loading="loading">
              <el-icon><Refresh /></el-icon> 閸掗攱鏌?
            </el-button>
          </div>
        </div>
      </template>
      <el-empty v-if="backups.length === 0 && !loading" description="閺嗗倹妫ゆ径鍥﹀敜鐠佹澘缍? :image-size="80" style="padding:40px 0;" />
      <el-table v-else :data="backups" style="width: 100%;" size="small" stripe>
        <el-table-column prop="id" label="婢跺洣鍞?ID" width="180" />
        <el-table-column prop="type" label="缁鐎? width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === '閸忋劑鍣? ? 'primary' : 'info'" size="small" effect="light">
              {{ row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target" label="婢跺洣鍞ら惄顔界垼" min-width="140" />
        <el-table-column prop="time" label="婢跺洣鍞ら弮鍫曟？" width="150" />
        <el-table-column prop="size" label="婢堆冪毈" width="100" />
        <el-table-column prop="status" label="閻樿埖鈧? width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === '閹存劕濮? ? 'success' : 'danger'" size="small" effect="light">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="閹垮秳缍? width="160">
          <template #default="{ row }">
            <el-button
              v-if="row.status === '閹存劕濮?"
              text
              size="small"
              type="danger"
              @click="confirmRollback(row)"
            >
              <el-icon><RefreshRight /></el-icon> 閸ョ偞绮?
            </el-button>
            <el-button text size="small" type="primary" @click="viewDetail(row)">
              鐠囷附鍎?
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 閸ョ偞绮寸涵顔款吇瀵湱鐛?-->
    <el-dialog
      v-model="rollbackDialogVisible"
      title="閸ョ偞绮寸涵顔款吇"
      width="480px"
      :close-on-click-modal="false"
    >
      <div v-if="rollbackTarget" style="padding: 8px 0;">
        <el-alert
          title="濮濄倖鎼锋担婊冪殺鐟曞棛娲婅ぐ鎾冲鏉╂劘顢戦悧鍫熸拱閿涘矁顕禒鏃傜矎绾喛顓?
          type="warning"
          :closable="false"
          show-icon
          style="margin-bottom: 16px;"
        />
        <div class="rollback-info">
          <div class="info-row">
            <span class="info-label">婢跺洣鍞?ID</span>
            <span class="info-value">{{ rollbackTarget.id }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">婢跺洣鍞ら惄顔界垼</span>
            <span class="info-value">{{ rollbackTarget.target }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">婢跺洣鍞ら弮鍫曟？</span>
            <span class="info-value">{{ rollbackTarget.time }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">婢跺洣鍞ゆ径褍鐨?/span>
            <span class="info-value">{{ rollbackTarget.size }}</span>
          </div>
        </div>
        <p style="font-size: 13px; color: var(--text-secondary); margin-top: 12px;">
          鐠囩柉绶崗?"{{ rollbackTarget.id }}" 绾喛顓婚崶鐐寸泊閹垮秳缍?
        </p>
        <el-input
          v-model="rollbackConfirmText"
          placeholder="鐠囩柉绶崗銉ヮ槵娴?ID 绾喛顓?
          style="margin-top: 8px;"
        />
      </div>
      <template #footer>
        <el-button @click="rollbackDialogVisible = false">閸欐牗绉?/el-button>
        <el-button
          type="danger"
          @click="handleExecuteRollback"
          :disabled="rollbackConfirmText !== rollbackTarget?.id"
          :loading="rollingBack"
        >
          绾喛顓婚崶鐐寸泊
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
        type: b.type || '閸忋劑鍣?,
        target: b.target || b.description || '',
        time: b.time || b.createdAt || '',
        size: b.size || '0 MB',
        status: b.status || '閹存劕濮?,
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
    ElMessage.success(`瀹告彃娲栧姘冲殾 ${rollbackTarget.value.id}`)
    rollbackTarget.value = null
    await fetchBackups()
  } catch {
    ElMessage.error('閸ョ偞绮存径杈Е')
  } finally {
    rollingBack.value = false
  }
}

const viewDetail = (row) => {
  ElMessage.info(`閺屻儳婀呮径鍥﹀敜鐠囷附鍎? ${row.id}`)
}

const handleCreateBackup = async () => {
  creating.value = true
  try {
    const result = await createBackup()
    if (result) {
      backups.unshift({
        id: result.id || `bak_manual_${Date.now()}`,
        type: result.type || '閹靛濮?,
        target: result.target || '閺佺増宓佹惔?malldb + 闁板秶鐤嗛弬鍥︽',
        time: result.time || new Date().toLocaleString(),
        size: result.size || '216 MB',
        status: result.status || '閹存劕濮?,
      })
    }
    ElMessage.success('閹靛濮╂径鍥﹀敜鐎瑰本鍨?)
  } catch {
    ElMessage.error('婢跺洣鍞ゆ径杈Е')
  } finally {
    creating.value = false
    await fetchBackups()
  }
}

const refreshBackups = async () => {
  loading.value = true
  await fetchBackups()
  ElMessage.success('婢跺洣鍞ら崚妤勩€冨鎻掑煕閺?)
}

onMounted(() => {
  fetchBackups()
})
</script>

<style scoped>
.rollback-info {
  background: var(--bg-page);
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
