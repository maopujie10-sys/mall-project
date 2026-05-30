<template>
  <div class="emergency-page">
    <div class="emergency-container">
      <!-- 头部 -->
      <div class="em-header">
        <div class="em-logo">
          <el-icon :size="28" color="#ff4d4f"><WarningFilled /></el-icon>
          <span>急救面板</span>
        </div>
        <div class="em-mode" :class="currentMode">
          <span class="mode-dot"></span>
          {{ modeLabel }}
        </div>
      </div>

      <!-- Kill Switch -->
      <div class="kill-section">
        <div class="kill-description">
          点击下方按钮将<strong>立即切断 AI 的所有写权限</strong>，系统进入人工接管模式。<br/>
          此操作不影响商城、客服、轮值系统的正常运行。
        </div>
        <el-button
          class="kill-button"
          :class="{ killed: isKilled }"
          :disabled="isKilled"
          @click="triggerKill"
          size="large"
        >
          <el-icon :size="24"><WarningFilled /></el-icon>
          <span>{{ isKilled ? '已切断 - 所有写操作已停止' : '立即切断 AI 写权限' }}</span>
        </el-button>
        <div v-if="isKilled" class="kill-confirm">
          <el-icon :size="18" color="#52c41a"><CircleCheckFilled /></el-icon>
          AI 写权限已于 {{ killTime }} 切断，所有危险操作已被阻止
        </div>
      </div>

      <!-- 模式恢复 -->
      <div class="recovery-section">
        <h3>模式恢复</h3>
        <div class="recovery-buttons">
          <el-button type="primary" size="large" @click="restoreMode('ai_control')" :disabled="!isKilled">
            <el-icon><RefreshRight /></el-icon> 恢复 AI 接管
          </el-button>
          <el-button size="large" @click="restoreMode('readonly')" :disabled="!isKilled">
            <el-icon><View /></el-icon> 切换到只读模式
          </el-button>
          <el-button size="large" @click="restoreMode('assist')" :disabled="!isKilled">
            切换到辅助模式
          </el-button>
        </div>
        <div v-if="!isKilled" class="recovery-hint">当前 AI 接管正常运行，无需切换模式</div>
      </div>

      <!-- 操作记录 -->
      <div class="history-section">
        <h3>最近操作记录</h3>
        <div class="history-list">
          <div v-for="(record, i) in history" :key="i" class="history-item">
            <span class="status-dot" :class="record.mode === 'human_control' ? 'offline' : 'online'">
              <span class="dot"></span>
            </span>
            <span class="history-time">{{ record.time }}</span>
            <el-tag :type="record.mode === 'human_control' ? 'danger' : 'success'" size="small">
              {{ record.mode === 'human_control' ? '人工接管' : record.mode === 'ai_control' ? 'AI 接管' : record.mode }}
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
  const map = { 'ai-control': 'AI 接管中', 'ai_control': 'AI 接管中', 'human-control': '人工接管', 'human_control': '人工接管', 'readonly': '只读模式', 'assist': '辅助模式' }
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
      '此操作将立即切断 AI 的所有写权限，包括：重启服务、修改配置、数据库写操作等。确认继续？',
      '警告 确认 Kill Switch',
      { confirmButtonText: '确认切断', cancelButtonText: '取消', type: 'error', confirmButtonClass: 'el-button--danger' }
    )
    const success = await systemStore.triggerEmergencyKill()
    if (success) {
      history.value.unshift({ time: killTime.value, mode: 'human_control', reason: 'Kill Switch 触发' })
      ElMessage.error('AI 写权限已切断！系统进入人工接管模式')
    } else {
      ElMessage.error('Kill Switch 触发失败')
    }
  } catch {
    // User cancelled
  }
}

const restoreMode = async (mode) => {
  const labels = { ai_control: 'AI 接管', readonly: '只读', assist: '辅助' }
  const success = await systemStore.switchMode(mode)
  if (success) {
    const now = new Date().toLocaleTimeString('zh-CN', { hour12: false })
    history.value.unshift({ time: now, mode, reason: `手动切换到${labels[mode]}模式` })
    if (mode === 'ai_control') {
      ElMessage.success('已恢复 AI 接管模式，写操作权限已恢复')
    } else {
      ElMessage.warning(`已切换到${labels[mode]}模式`)
    }
  } else {
    ElMessage.error('模式切换失败')
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
