<template>
  <div class="chat-page">
    <!-- 左侧：任务步骤 -->
    <div class="chat-sidebar">
      <div class="sidebar-header">任务进度</div>
      <div class="step-list">
        <div v-for="step in steps" :key="step.id" class="step-item" :class="step.status">
          <div class="step-icon">
            <el-icon v-if="step.status === 'done'" color="#52c41a"><CircleCheckFilled /></el-icon>
            <el-icon v-else-if="step.status === 'running'" color="#1890ff" class="spin"><Loading /></el-icon>
            <el-icon v-else-if="step.status === 'failed'" color="#ff4d4f"><CircleCloseFilled /></el-icon>
            <span v-else class="step-dot"></span>
          </div>
          <div class="step-info">
            <div class="step-name">{{ step.name }}</div>
            <div class="step-tool">{{ step.tool }}</div>
            <div v-if="step.evidence" class="step-evidence">{{ step.evidence }}</div>
          </div>
        </div>
      </div>
      <div v-if="steps.length === 0" class="sidebar-empty">
        <el-icon :size="32" color="#d9d9d9"><ChatLineSquare /></el-icon>
        <p>等待任务</p>
      </div>
    </div>

    <!-- 右侧：对话区 -->
    <div class="chat-main">
      <div class="chat-header">
        <span class="mode-badge" :class="currentMode">{{ modeLabel }}</span>
        <span class="chat-title">AI Agent 对话</span>
        <el-button type="danger" text size="small" @click="$router.push('/emergency')">
          <el-icon><WarningFilled /></el-icon> 急救
        </el-button>
      </div>

      <div class="chat-messages" ref="msgContainer">
        <div v-if="messages.length === 0" class="chat-empty">
          <div class="empty-icon">
            <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
              <rect width="64" height="64" rx="16" fill="#e6f7ff"/>
              <path d="M20 24h24M20 32h16M20 40h20" stroke="#1890ff" stroke-width="2.5" stroke-linecap="round"/>
            </svg>
          </div>
          <h3>AI Agent 总控对话</h3>
          <p>输入中文指令，AI 自动分析并执行</p>
          <div class="quick-actions">
            <el-tag v-for="q in quickCommands" :key="q" @click="sendMessage(q)" class="quick-tag">{{ q }}</el-tag>
          </div>
        </div>

        <div v-for="(msg, i) in messages" :key="i" class="msg-row" :class="msg.role">
          <div class="msg-avatar">
            <el-avatar :size="32" :style="msg.role === 'user' ? 'background:#1890ff' : 'background:#52c41a'">
              {{ msg.role === 'user' ? 'U' : 'AI' }}
            </el-avatar>
          </div>
          <div class="msg-body">
            <div class="msg-header">
              <span class="msg-role">{{ msg.role === 'user' ? '你' : 'AI Agent' }}</span>
              <span v-if="msg.risk" class="risk-badge" :class="msg.risk">{{ msg.risk }}</span>
              <span class="msg-time">{{ msg.time }}</span>
            </div>
            <div class="msg-text">{{ msg.text }}</div>
            <div v-if="msg.steps" class="msg-steps">
              <div v-for="s in msg.steps" :key="s.step" class="msg-step-item">
                <el-icon :color="s.ok ? '#52c41a' : '#faad14'"><component :is="s.ok ? 'CircleCheckFilled' : 'Loading'" /></el-icon>
                <span>{{ s.step }}: {{ s.name }}</span>
                <span class="step-detail">{{ s.detail }}</span>
              </div>
            </div>
            <!-- L3/L4 确认按钮 -->
            <div v-if="msg.needConfirm" class="confirm-bar">
              <el-button type="success" @click="confirmAction(msg, true)">✓ 确认执行</el-button>
              <el-button type="danger" @click="confirmAction(msg, false)">✗ 拒绝</el-button>
              <el-button @click="$router.push('/emergency')">转人工接管</el-button>
            </div>
          </div>
        </div>
      </div>

      <div class="chat-input-bar">
        <el-input
          v-model="inputText"
          placeholder="输入指令，如：检查服务器状态、商城为什么打不开..."
          @keyup.enter="sendMessage(inputText)"
          :disabled="isRunning"
          size="large"
        >
          <template #append>
            <el-button type="primary" @click="sendMessage(inputText)" :loading="isRunning" :disabled="!inputText.trim()">
              <el-icon><Promotion /></el-icon> 发送
            </el-button>
          </template>
        </el-input>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, computed, onMounted } from 'vue'
import { useAgentStore } from '@/stores/agent'
import { useSystemStore } from '@/stores/system'
import { storeToRefs } from 'pinia'

const agentStore = useAgentStore()
const systemStore = useSystemStore()

const { messages, steps, isRunning } = storeToRefs(agentStore)
const { currentMode, emergencyModeLabel } = storeToRefs(systemStore)

const inputText = ref('')
const msgContainer = ref(null)

const modeLabel = computed(() => {
  const map = { 'ai-control': 'AI 接管中', 'ai_control': 'AI 接管中', 'assist': '辅助模式', 'readonly': '只读', 'human-control': '人工接管', 'human_control': '人工接管' }
  return map[currentMode.value] || currentMode.value
})

const quickCommands = ['检查服务器状态', '商城打不开了', '备份数据库', '查看Nginx状态', '全站诊断']

function scrollBottom() {
  nextTick(() => {
    if (msgContainer.value) msgContainer.value.scrollTop = msgContainer.value.scrollHeight
  })
}

async function sendMessage(text) {
  const msg = typeof text === 'string' ? text : inputText.value
  if (!msg || !msg.trim() || isRunning.value) return
  inputText.value = ''

  await agentStore.sendMessage(msg)
  scrollBottom()
}

function confirmAction(msg, approved) {
  agentStore.confirmMsgAction(msg, approved)
  scrollBottom()
}

onMounted(() => {
  systemStore.fetchMode()
})
</script>

<style scoped>
.chat-page { display: flex; height: calc(100vh - var(--header-height)); background: var(--bg-page); }

/* 左侧步骤栏 */
.chat-sidebar {
  width: 260px; min-width: 260px;
  background: var(--bg-card); border-right: 1px solid var(--border-color);
  display: flex; flex-direction: column;
}
.sidebar-header {
  padding: 16px 20px; font-size: 14px; font-weight: 600;
  color: var(--text-primary); border-bottom: 1px solid var(--border-color);
}
.step-list { flex: 1; overflow-y: auto; padding: 8px; }
.step-item { display: flex; gap: 10px; padding: 10px 12px; border-radius: 6px; margin-bottom: 4px; transition: background 0.15s; }
.step-item:hover { background: var(--bg-hover); }
.step-item.running { background: var(--color-primary-bg); }
.step-item.failed { background: var(--color-danger-bg); }
.step-icon { width: 24px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.step-dot { width: 8px; height: 8px; border-radius: 50%; border: 2px solid #d9d9d9; }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.step-name { font-size: 13px; color: var(--text-primary); font-weight: 500; }
.step-tool { font-size: 11px; color: var(--text-muted); font-family: monospace; margin-top: 2px; }
.step-evidence { font-size: 11px; color: var(--color-success); margin-top: 2px; }
.sidebar-empty { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: var(--text-muted); gap: 8px; }
.sidebar-empty p { font-size: 13px; }

/* 右侧对话区 */
.chat-main { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.chat-header {
  height: 48px; display: flex; align-items: center; gap: 12px;
  padding: 0 20px; background: var(--bg-card); border-bottom: 1px solid var(--border-color);
}
.mode-badge {
  font-size: 11px; padding: 2px 10px; border-radius: 12px; font-weight: 500;
}
.mode-badge.ai-control { background: var(--color-success-bg); color: var(--color-success); }
.mode-badge.human-control { background: var(--color-danger-bg); color: var(--color-danger); }
.mode-badge.readonly { background: var(--color-warning-bg); color: #d48806; }
.chat-title { font-size: 14px; font-weight: 500; color: var(--text-secondary); flex: 1; }

.chat-messages { flex: 1; overflow-y: auto; padding: 20px; }
.chat-empty { text-align: center; padding: 60px 20px; }
.chat-empty h3 { font-size: 18px; color: var(--text-primary); margin: 20px 0 8px; }
.chat-empty p { font-size: 13px; color: var(--text-secondary); margin-bottom: 20px; }
.quick-actions { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
.quick-tag { cursor: pointer; transition: all 0.15s; }
.quick-tag:hover { background: var(--color-primary-bg); color: var(--color-primary); border-color: var(--color-primary-light); }

.msg-row { display: flex; gap: 12px; margin-bottom: 20px; }
.msg-row.user { flex-direction: row-reverse; }
.msg-avatar { flex-shrink: 0; }
.msg-body { max-width: 75%; }
.msg-row.user .msg-body { text-align: right; }
.msg-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.msg-row.user .msg-header { flex-direction: row-reverse; }
.msg-role { font-size: 12px; font-weight: 600; color: var(--text-secondary); }
.msg-time { font-size: 11px; color: var(--text-muted); }
.msg-text {
  background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px;
  padding: 10px 14px; font-size: 13px; line-height: 1.6; white-space: pre-wrap; color: var(--text-primary);
}
.msg-row.user .msg-text { background: var(--color-primary-bg); border-color: #91d5ff; }
.msg-steps { margin-top: 8px; display: flex; flex-direction: column; gap: 4px; }
.msg-step-item {
  display: flex; align-items: center; gap: 8px; font-size: 12px;
  padding: 6px 10px; background: #fafafa; border-radius: 4px; color: var(--text-secondary);
}
.step-detail { font-size: 11px; color: var(--text-muted); margin-left: auto; }

.confirm-bar {
  margin-top: 12px; padding: 12px; background: var(--color-warning-bg);
  border: 1px solid #ffe58f; border-radius: 8px; display: flex; gap: 8px;
}

.chat-input-bar { padding: 12px 20px; background: var(--bg-card); border-top: 1px solid var(--border-color); }
</style>
