<template>
  <div class="emergency-page">
    <div class="emergency-container">
      <div class="em-header">
        <div class="em-logo">
          <el-icon :size="28" color="#ff4d4f"><WarningFilled /></el-icon>
          <span>绱ф€ラ潰鏉?/span>
        </div>
        <div class="em-mode" :class="currentMode">
          <span class="mode-dot"></span>
          {{ modeLabel }}
        </div>
      </div>

      <div class="kill-section">
        <div class="kill-description">
          鐐瑰嚮涓嬫柟鎸夐挳灏?strong>绔嬪嵆缁堟 AI 鐨勬墍鏈夎嚜涓绘搷浣?/strong>锛岀郴缁熷垏鎹㈠埌浜哄伐鎺ョ妯″紡銆?br/>
          姝ゆ搷浣滃皢鏆傚仠鎵€鏈?Agent銆佸畾鏃朵换鍔″拰鑷姩淇锛岀洿鍒版墜鍔ㄦ仮澶嶃€?        </div>
        <el-button
          class="kill-button"
          :class="{ killed: isKilled }"
          :disabled="isKilled"
          @click="triggerKill"
          size="large"
        >
          <el-icon :size="24"><WarningFilled /></el-icon>
          <span>{{ isKilled ? 'AI - 宸茬粓姝? : '绔嬪嵆缁堟 AI 鑷富鎺у埗' }}</span>
        </el-button>
        <div v-if="isKilled" class="kill-confirm">
          <el-icon :size="18" color="#52c41a"><CircleCheckFilled /></el-icon>
          AI 宸茬粓姝簬 {{ killTime }}锛屽綋鍓嶄负浜哄伐鎺ョ妯″紡
        </div>
      </div>

      <div class="recovery-section">
        <h3>鎭㈠妯″紡閫夋嫨</h3>
        <div class="recovery-buttons">
          <el-button type="primary" size="large" @click="restoreMode('ai_control')" :disabled="!isKilled">
            <el-icon><RefreshRight /></el-icon> 鎭㈠ AI 鎺у埗
          </el-button>
          <el-button size="large" @click="restoreMode('readonly')" :disabled="!isKilled">
            <el-icon><View /></el-icon> 杩涘叆鍙妯″紡
          </el-button>
          <el-button size="large" @click="restoreMode('assist')" :disabled="!isKilled">
            杩涘叆杈呭姪妯″紡
          </el-button>
        </div>
        <div v-if="!isKilled" class="recovery-hint">褰撳墠涓?AI 鎺у埗妯″紡锛屾棤闇€鎭㈠</div>
      </div>

      <div class="history-section">
        <h3>鍒囨崲鍘嗗彶璁板綍</h3>
        <div class="history-list">
          <div v-for="(record, i) in history" :key="i" class="history-item">
            <span class="status-dot" :class="record.mode === 'human_control' ? 'offline' : 'online'">
              <span class="dot"></span>
            </span>
            <span class="history-time">{{ record.time }}</span>
            <el-tag :type="record.mode === 'human_control' ? 'danger' : 'success'" size="small">
              {{ record.mode === 'human_control' ? '浜哄伐鎺ョ' : record.mode === 'ai_control' ? 'AI 鎺у埗' : record.mode }}
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
const { currentMode, isKilled, killTime } = storeToRefs(systemStore)

const loading = ref(true)

const modeLabel = computed(() => {
  const map = { 'ai-control': 'AI 鎺у埗妯″紡', 'ai_control': 'AI 鎺у埗妯″紡', 'human-control': '浜哄伐鎺ョ', 'human_control': '浜哄伐鎺ョ', 'readonly': '鍙妯″紡', 'assist': '杈呭姪妯″紡' }
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
  } catch {} finally { loading.value = false }
}

const triggerKill = async () => {
  try {
    await ElMessageBox.confirm(
      '纭绔嬪嵆缁堟 AI 鐨勬墍鏈夎嚜涓绘搷浣滐紵杩欏皢鏆傚仠鎵€鏈?Agent銆佸畾鏃朵换鍔″拰鑷姩淇鍔熻兘锛岀郴缁熷皢鍒囨崲鍒颁汉宸ユ帴绠℃ā寮忋€?,
      '纭 - Kill Switch',
      { confirmButtonText: '纭缁堟', cancelButtonText: '鍙栨秷', type: 'error', confirmButtonClass: 'el-button--danger' }
    )
    const success = await systemStore.triggerEmergencyKill()
    if (success) {
      history.value.unshift({ time: killTime.value, mode: 'human_control', reason: 'Kill Switch 瑙﹀彂' })
      ElMessage.error('AI 宸茬粓姝紝褰撳墠涓轰汉宸ユ帴绠℃ā寮?)
    } else {
      ElMessage.error('Kill Switch 瑙﹀彂澶辫触')
    }
  } catch {}
}

const restoreMode = async (mode) => {
  const labels = { ai_control: 'AI 鎺у埗', readonly: '鍙', assist: '杈呭姪' }
  const success = await systemStore.switchMode(mode)
  if (success) {
    const now = new Date().toLocaleTimeString('zh-CN', { hour12: false })
    history.value.unshift({ time: now, mode, reason: `鎵嬪姩鎭㈠ ${labels[mode]} 妯″紡` })
    if (mode === 'ai_control') {
      ElMessage.success('宸叉仮澶?AI 鎺у埗妯″紡锛孉gent 灏嗛噸鏂板紑濮嬪伐浣?)
    } else {
      ElMessage.warning(`宸茶繘鍏?{labels[mode]}妯″紡`)
    }
  } else {
    ElMessage.error('鎭㈠妯″紡鍒囨崲澶辫触')
  }
}

onMounted(() => {
  systemStore.fetchMode()
  fetchHistory()
})
</script>

<style scoped>
.emergency-page { min-height: 100vh; background: #f0f2f5; display: flex; justify-content: center; padding: 40px 24px; }
.emergency-container { width: 100%; max-width: 680px; }
.em-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; }
.em-logo { display: flex; align-items: center; gap: 10px; font-size: 22px; font-weight: 700; color: #262626; }
.em-mode { display: flex; align-items: center; gap: 6px; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 500; }
.em-mode.ai-control { background: #f6ffed; color: #52c41a; border: 1px solid #b7eb8f; }
.em-mode.human-control { background: #fff2f0; color: #ff4d4f; border: 1px solid #ffccc7; }
.em-mode.readonly { background: #fffbe6; color: #d48806; border: 1px solid #ffe58f; }
.mode-dot { width: 8px; height: 8px; border-radius: 50%; background: currentColor; }
.kill-section { background: #fff; border: 1px solid #ffccc7; border-radius: 12px; padding: 32px; text-align: center; margin-bottom: 24px; }
.kill-description { font-size: 14px; color: #595959; margin-bottom: 24px; line-height: 1.8; }
.kill-button { width: 100%; max-width: 440px; height: 72px !important; font-size: 18px !important; font-weight: 600 !important; border-radius: 12px !important; background: #ff4d4f !important; border-color: #ff4d4f !important; color: #fff !important; display: flex !important; align-items: center; justify-content: center; gap: 12px; }
.kill-button:hover { background: #ff7875 !important; border-color: #ff7875 !important; }
.kill-button.killed { background: #d9d9d9 !important; border-color: #d9d9d9 !important; color: #8c8c8c !important; cursor: not-allowed; }
.kill-confirm { margin-top: 16px; display: flex; align-items: center; justify-content: center; gap: 8px; color: #52c41a; font-size: 14px; font-weight: 500; }
.recovery-section { background: #fff; border: 1px solid #f0f0f0; border-radius: 12px; padding: 24px 32px; margin-bottom: 24px; }
.recovery-section h3 { font-size: 16px; font-weight: 600; margin-bottom: 16px; }
.recovery-buttons { display: flex; gap: 12px; }
.recovery-hint { font-size: 13px; color: #8c8c8c; margin-top: 12px; }
.history-section { background: #fff; border: 1px solid #f0f0f0; border-radius: 12px; padding: 24px 32px; }
.history-section h3 { font-size: 16px; font-weight: 600; margin-bottom: 16px; }
.history-item { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border-light, #f5f5f5); font-size: 13px; }
.history-item:last-child { border-bottom: none; }
.history-time { color: #8c8c8c; font-family: monospace; width: 50px; }
.history-reason { color: #595959; margin-left: auto; }
</style>