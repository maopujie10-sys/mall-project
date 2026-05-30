<template>
  <div class="emergency-page">
    <div class="emergency-container">
      
      <div class="em-header">
        <div class="em-logo">
          <el-icon :size="28" color="#ff4d4f"><WarningFilled /></el-icon>
          <span>{{ $t('emergency.title') }}</span>
        </div>
        <div class="em-mode" :class="currentMode">
          <span class="mode-dot">{{ $t('emergency.title') }}</span>
          {{ modeLabel }}
        </div>
      </div>

      <!-- Kill Switch -->
      <div class="kill-section">
        <div class="kill-description">
          <strong> AI </strong>-
        </div>
        <el-button
          class="kill-button"
          :class="{ killed: isKilled }"
          :disabled="isKilled"
          @click="triggerKill"
          size="large"
        >
          <el-icon :size="24"><WarningFilled /></el-icon>
          <span>{{ isKilled ? ' - ' : ' AI ' }}</span>
        </el-button>
        <div v-if="isKilled" class="kill-confirm">
          <el-icon :size="18" color="#52c41a"><CircleCheckFilled /></el-icon>
          AI  {{ killTime }} 
        </div>
      </div>

      
      <div class="recovery-section">
        <h3>{{ $t('emergency.title') }}</h3>
        <div class="recovery-buttons">
          <el-button type="primary" size="large" @click="restoreMode('ai_control')" :disabled="!isKilled">
            <el-icon><RefreshRight /></el-icon>  AI 
          </el-button>
          <el-button size="large" @click="restoreMode('readonly')" :disabled="!isKilled">
            <el-icon><View /></el-icon> 
          </el-button>
          <el-button size="large" @click="restoreMode('assist')" :disabled="!isKilled">OK</el-button>
        </div>
        <div v-if="!isKilled" class="recovery-hint"> AI </div>
      </div>

      
      <div class="history-section">
        <h3>{{ $t('emergency.title') }}</h3>
        <div class="history-list">
          <div v-for="(record, i) in history" :key="i" class="history-item">
            <span class="status-dot" :class="record.mode === 'human_control' ? 'offline' : 'online'">
              <span class="dot">{{ $t('emergency.title') }}</span>
            </span>
            <span class="history-time">{{ record.time }}</span>
            <el-tag :type="record.mode === 'human_control' ? 'danger' : 'success'" size="small">
              {{ record.mode === 'human_control' ? '' : record.mode === 'ai_control' ? 'AI ' : record.mode }}
            </el-tag>
            <span class="history-reason">{{ record.reason }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useSystemStore } from '@/stores/system'
import { storeToRefs } from 'pinia'

const systemStore = useSystemStore()
const { currentMode, isKilled, killTime, emergencyModeLabel } = storeToRefs(systemStore)

const loading = ref(true)

const modeLabel = computed(() => {
  const map = { 'ai-control': 'AI ', 'ai_control': 'AI ', 'human-control': '', 'human_control': '', 'readonly': '', 'assist': '' }
  return map[currentMode.value] || currentMode.value
})

const history = ref([])

async function fetchHistory() {
  try {
    const data = await systemStore.fetchEmergencyHistory()
    if (Array.isArray(data)) {
      history.value = data.map((r) => ({
        time: r.time || '-',
        mode: r.mode || 'ai_control',
        reason: r.reason || r.description || '',
      }))
    }
  } catch {
    // Keep existing history
  } finally {
    loading.value = false
  }
}

const triggerKill = async () => {
  try {
    await ElMessageBox.confirm(
      ' AI ',
      '  Kill Switch',
      { confirmButtonText: '', cancelButtonText: '', type: 'error', confirmButtonClass: 'el-button--danger' }
    )
    const success = await systemStore.triggerEmergencyKill()
    if (success) {
      history.value.unshift({ time: killTime.value, mode: 'human_control', reason: 'Kill Switch ' })
      ElMessage.error('AI ')
    } else {
      ElMessage.error('Kill Switch ')
    }
  } catch {
    // User cancelled
  }
}

const restoreMode = async (mode) => {
  const labels = { ai_control: 'AI ', readonly: '', assist: '' }
  const success = await systemStore.switchMode(mode)
  if (success) {
    const now = new Date().toLocaleTimeString('zh-CN', { hour12: false })
    history.value.unshift({ time: now, mode, reason: `${labels[mode]}` })
    if (mode === 'ai_control') {
      ElMessage.success(' AI ')
    } else {
      ElMessage.warning(`${labels[mode]}`)
    }
  } else {
    ElMessage.error('Error')
  }
}

onMounted(() => {
  systemStore.fetchMode()
  fetchHistory()
})
</script>

<style scoped>
.emergency-page {
  min-height: 100vh;
  background: rgba(240,242,245,0.15);
  display: flex;
  justify-content: center;
  padding: 40px 24px;
}
.emergency-container {
  width: 100%;
  max-width: 680px;
}
.em-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}
.em-logo { display: flex; align-items: center; gap: 10px; font-size: 22px; font-weight: 700; color: #262626; }
.em-mode { display: flex; align-items: center; gap: 6px; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 500; }
.em-mode.ai-control { background: #f6ffed; color: #52c41a; border: 1px solid #b7eb8f; }
.em-mode.human-control { background: #fff2f0; color: #ff4d4f; border: 1px solid #ffccc7; }
.em-mode.readonly { background: #fffbe6; color: #d48806; border: 1px solid #ffe58f; }
.mode-dot { width: 8px; height: 8px; border-radius: 50%; background: currentColor; }

.kill-section {
  background: #fff;
  border: 1px solid #ffccc7;
  border-radius: 12px;
  padding: 32px;
  text-align: center;
  margin-bottom: 24px;
}
.kill-description { font-size: 14px; color: #595959; margin-bottom: 24px; line-height: 1.8; }
.kill-button {
  width: 100%;
  max-width: 440px;
  height: 72px !important;
  font-size: 18px !important;
  font-weight: 600 !important;
  border-radius: 12px !important;
  background: #ff4d4f !important;
  border-color: #ff4d4f !important;
  color: #fff !important;
  display: flex !important;
  align-items: center;
  justify-content: center;
  gap: 12px;
}
.kill-button:hover { background: #ff7875 !important; border-color: #ff7875 !important; }
.kill-button.killed { background: #d9d9d9 !important; border-color: #d9d9d9 !important; color: #8c8c8c !important; cursor: not-allowed; }
.kill-confirm { margin-top: 16px; display: flex; align-items: center; justify-content: center; gap: 8px; color: #52c41a; font-size: 14px; font-weight: 500; }

.recovery-section {
  background: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 12px;
  padding: 24px 32px;
  margin-bottom: 24px;
}
.recovery-section h3 { font-size: 16px; font-weight: 600; margin-bottom: 16px; }
.recovery-buttons { display: flex; gap: 12px; }
.recovery-hint { font-size: 13px; color: #8c8c8c; margin-top: 12px; }

.history-section {
  background: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 12px;
  padding: 24px 32px;
}
.history-section h3 { font-size: 16px; font-weight: 600; margin-bottom: 16px; }
.history-item { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border-light, #f5f5f5); font-size: 13px; }
.history-item:last-child { border-bottom: none; }
.history-time { color: #8c8c8c; font-family: monospace; width: 50px; }
.history-reason { color: #595959; margin-left: auto; }
</style>
