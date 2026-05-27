<template>
  <div class="chat-page">
    <!-- 左侧：任务步骤 -->
    <div class="chat-sidebar">
      <div class="sidebar-header">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/></svg>
        <span>任务进度</span>
        <span class="task-count" v-if="steps.length">{{ steps.length }}</span>
      </div>
      <div class="step-list">
        <div v-for="step in steps" :key="step.id" class="step-item" :class="step.status">
          <div class="step-icon">
            <el-icon v-if="step.status === 'done'" color="#52c41a"><CircleCheckFilled /></el-icon>
            <el-icon v-else-if="step.status === 'running'" color="#667eea" class="spin"><Loading /></el-icon>
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
        <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="#d9d9d9" stroke-width="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        <p>等待任务</p>
        <span>在下方输入指令</span>
      </div>
    </div>

    <!-- 右侧：对话区 -->
    <div class="chat-main">
      <div class="chat-header">
        <div class="ch-left">
          <span class="mode-badge" :class="currentMode">{{ modeLabel }}</span>
          <span class="chat-title">AI Agent 对话</span>
        </div>
        <div class="ch-right">
          <el-button text size="small" @click="clearChat">清空</el-button>
          <el-button type="danger" text size="small" @click="$router.push('/emergency')">
            <el-icon><WarningFilled /></el-icon> 急救
          </el-button>
        </div>
      </div>

      <div class="chat-messages" ref="msgContainer">
        <div v-if="messages.length === 0" class="chat-empty">
          <div class="empty-visual">
            <div class="brain-anim">
              <span class="brain-pulse"></span>
              <svg viewBox="0 0 64 64" width="64" height="64" fill="none">
                <circle cx="32" cy="32" r="28" stroke="url(#brainGrad)" stroke-width="2" stroke-dasharray="175" stroke-dashoffset="0">
                  <animate attributeName="stroke-dashoffset" from="350" to="0" dur="3s" repeatCount="indefinite"/>
                </circle>
                <defs><linearGradient id="brainGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#667eea"/><stop offset="100%" stop-color="#764ba2"/></linearGradient></defs>
              </svg>
            </div>
          </div>
          <h3>AI MallBrain 对话</h3>
          <p>输入中文指令，AI 自动分析并执行</p>
          <div class="quick-cmds">
            <div v-for="q in quickCommands" :key="q" class="quick-chip" @click="sendMessage(q)">{{ q }}</div>
          </div>
          <div class="capability-hints">
            <span class="hint-tag">🛒 采集商品</span>
            <span class="hint-tag">👥 生成数据</span>
            <span class="hint-tag">🧠 AI运维</span>
            <span class="hint-tag">📈 进化报告</span>
            <span class="hint-tag">💾 创建备份</span>
          </div>
        </div>

        <div v-for="(msg, i) in messages" :key="i" class="msg-row" :class="msg.role">
          <div class="msg-avatar">
            <div class="avatar-circle" :class="msg.role">
              {{ msg.role === 'user' ? 'U' : 'AI' }}
            </div>
          </div>
          <div class="msg-body">
            <div class="msg-header">
              <span class="msg-role">{{ msg.role === 'user' ? '你' : 'AI Agent' }}</span>
              <span v-if="msg.risk" class="risk-badge" :class="msg.risk">{{ msg.risk }}</span>
              <span class="msg-time">{{ msg.time }}</span>
            </div>
            <div class="msg-content" v-html="formatMsg(msg.text)"></div>
            <div v-if="msg.steps" class="msg-steps">
              <div v-for="s in msg.steps" :key="s.step" class="msg-step-item">
                <el-icon :color="s.ok ? '#52c41a' : '#faad14'"><component :is="s.ok ? 'CircleCheckFilled' : 'Loading'" /></el-icon>
                <span>{{ s.step }}: {{ s.name }}</span>
                <span class="step-detail">{{ s.detail }}</span>
              </div>
            </div>
            <!-- 确认按钮 -->
            <div v-if="msg.needConfirm" class="confirm-bar">
              <el-button type="success" @click="confirmAction(msg, true)">✓ 确认执行</el-button>
              <el-button type="danger" @click="confirmAction(msg, false)">✗ 拒绝</el-button>
              <el-button @click="$router.push('/emergency')">转人工接管</el-button>
            </div>
          </div>
        </div>
      </div>

      <div class="chat-input-bar">
        <div class="input-wrap">
          <el-input
            v-model="inputText"
            placeholder="告诉AI你想做什么... 比如：扫描商城健康度 / 采集手机配件 / 查看进化报告"
            @keyup.enter="sendMessage(inputText)"
            :disabled="isRunning"
            size="large"
            class="chat-input"
          >
            <template #prefix>
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#667eea" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
            </template>
            <template #append>
              <el-button type="primary" @click="sendMessage(inputText)" :loading="isRunning" :disabled="!inputText.trim()">
                <el-icon><Promotion /></el-icon> 发送
              </el-button>
            </template>
          </el-input>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useAgentStore } from '@/stores/agent'
import { useSystemStore } from '@/stores/system'
import { storeToRefs } from 'pinia'

const agentStore = useAgentStore()
const systemStore = useSystemStore()
const { currentMode, modeLabel } = storeToRefs(systemStore)

const inputText = ref('')
const msgContainer = ref(null)
const isRunning = ref(false)

const messages = ref([])
const steps = ref([])

const quickCommands = [
  '扫描商城健康度',
  '生成进化报告',
  '从eBay采集手机配件',
  '生成虚拟用户数据',
  '创建完整备份',
]

function formatMsg(text) {
  if (!text) return ''
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br/>')
}

function scrollBottom() {
  nextTick(() => {
    if (msgContainer.value) msgContainer.value.scrollTop = msgContainer.value.scrollHeight
  })
}

async function sendMessage(text) {
  const msg = typeof text === 'string' ? text : inputText.value
  if (!msg || !msg.trim() || isRunning.value) return
  inputText.value = ''

  // 添加用户消息
  messages.value.push({
    role: 'user',
    text: msg,
    time: new Date().toLocaleTimeString(),
  })
  scrollBottom()

  isRunning.value = true

  // 模拟AI响应
  await new Promise(r => setTimeout(r, 800))

  const response = generateAIResponse(msg)
  messages.value.push({
    role: 'ai',
    text: response.text,
    risk: response.risk,
    time: new Date().toLocaleTimeString(),
    needConfirm: response.needConfirm,
    steps: response.steps,
  })

  if (response.steps) {
    steps.value = response.steps.map((s, i) => ({
      id: i + 1,
      ...s,
      status: 'done',
      tool: response.tool || '',
    }))
  }

  isRunning.value = false
  scrollBottom()
}

function generateAIResponse(msg) {
  const lower = msg.toLowerCase()

  if (lower.includes('扫描') || lower.includes('健康')) {
    return {
      text: '**意图**: AI扫描商品\n**类别**: AI大脑\n**风险等级**: L1\n\n🔍 正在扫描全站68件商品...\n\n📊 扫描结果：\n- 🔥 热销: 12件\n- ✅ 正常: 45件\n- ❄️ 冷门: 8件\n- 💀 死品: 3件\n\n⚠ 发现品类缺口: 母婴玩具、美妆护肤\n💡 建议从eBay采集补充',
      risk: 'L1',
      tool: 'mallbrain.scan',
      steps: [
        { step: 1, name: '识别意图: AI扫描商品', status: 'done' },
        { step: 2, name: '风险评估: L1', status: 'done' },
        { step: 3, name: '调用 AI大脑 工具', status: 'done', detail: '扫描完成' },
      ]
    }
  }

  if (lower.includes('进化') || lower.includes('报告') || lower.includes('学得怎么样')) {
    return {
      text: '**意图**: 进化报告\n**类别**: AI进化\n**风险等级**: L1\n\n🧬 AI进化报告：\n- 30天成功率: 87.5% ↗\n- 已学知识: 156条\n- 用户纠正: 23次\n- 进化趋势: 持续上升\n\n💡 建议: 价格优化成功率达70%，建议学习更多定价策略',
      risk: 'L1',
      tool: 'evolution.report',
      steps: [
        { step: 1, name: '生成进化报告', status: 'done', detail: '87.5%成功率' },
      ]
    }
  }

  if (lower.includes('采集')) {
    return {
      text: '**意图**: 启动商品采集\n**类别**: 采集\n**风险等级**: L2\n\n🛒 正在从多平台采集商品...\n\n已创建采集任务：\n- eBay > ' + msg.replace(/采集|从|商品|的/g, '').trim() + '\n- 预计采集: 50件\n- 自动上传COS: ✅\n- 保留原始规格和价格: ✅\n\n任务已加入队列，完成后自动通知。',
      risk: 'L2',
      tool: 'scraper.start',
      steps: [
        { step: 1, name: '创建采集任务', status: 'done', detail: 'eBay' },
        { step: 2, name: '开始采集...', status: 'done', detail: '进行中' },
      ]
    }
  }

  if (lower.includes('虚拟') || lower.includes('生成数据') || lower.includes('造数据')) {
    return {
      text: '**意图**: 生成虚拟数据\n**类别**: 虚拟数据\n**风险等级**: L3\n\n⚠ **需要确认**：即将生成虚拟数据\n\n规模: 中型商城\n- 👤 虚拟用户: 5,000人\n- 📦 虚拟商品: 200件\n- 📋 虚拟订单: 2,000单\n- ⭐ 商品评价: 800条\n\n此操作会修改数据库，请确认执行。',
      risk: 'L3',
      needConfirm: true,
      tool: 'virtual.generate',
    }
  }

  if (lower.includes('备份')) {
    return {
      text: '**意图**: 创建备份\n**类别**: 备份\n**风险等级**: L2\n\n💾 正在创建完整备份...\n\n✅ 数据库备份完成\n✅ 配置文件备份完成\n📁 备份位置: /backups/2024-05-28/\n\n备份已安全存储。',
      risk: 'L2',
      tool: 'backup.create',
    }
  }

  if (lower.includes('运维') || lower.includes('自动管理')) {
    return {
      text: '**意图**: AI自动运维\n**类别**: AI大脑\n**风险等级**: L3\n\n⚠ **需要确认**：AI将自动执行以下运维操作\n\n- 💀 下架3件死品\n- 🛒 采集8件新品填补缺口\n- 📦 为12件商品补充库存\n\n此操作会自动备份，可回滚。',
      risk: 'L3',
      needConfirm: true,
      tool: 'mallbrain.auto',
    }
  }

  if (lower.includes('help') || lower.includes('帮助')) {
    return {
      text: '**可用功能**:\n\n🛒 **采集商品** — 从eBay/AliExpress/Amazon采集\n👥 **生成数据** — 一键生成虚拟用户/商品/订单\n🧠 **AI运维** — 自动管理商城健康\n📈 **进化报告** — 查看AI学习进度\n💾 **创建备份** — 安全备份数据库\n🔍 **扫描商城** — 分析商品健康度\n\n试试对我说：扫描商城健康度',
      risk: 'L1',
    }
  }

  return {
    text: '🤔 收到: ' + msg + '\n\n我已理解您的意图，正在处理中...\n\n💡 提示: 试试说 "扫描商城" / "进化报告" / "采集商品" / "生成数据"',
    risk: 'L1',
  }
}

function confirmAction(msg, approved) {
  if (approved) {
    msg.text += '\n\n✅ 已确认执行！操作进行中...'
    msg.needConfirm = false
  } else {
    msg.text += '\n\n❌ 已取消执行。'
    msg.needConfirm = false
  }
  scrollBottom()
}

function clearChat() {
  messages.value = []
  steps.value = []
}

onMounted(() => {
  systemStore.fetchMode()
})
</script>

<style scoped>
.chat-page { display: flex; height: calc(100vh - 52px); }

/* 左侧 */
.chat-sidebar {
  width: 240px; min-width: 240px;
  background: var(--bg-card); border-right: 1px solid var(--border-color);
  display: flex; flex-direction: column;
}
.sidebar-header {
  padding: 16px; font-size: 13px; font-weight: 600;
  color: var(--text-primary); border-bottom: 1px solid var(--border-color);
  display: flex; align-items: center; gap: 8px;
}
.task-count {
  margin-left: auto;
  background: #667eea; color: #fff;
  font-size: 10px; padding: 1px 6px; border-radius: 10px;
}
.step-list { flex: 1; overflow-y: auto; padding: 8px; }
.step-item { display: flex; gap: 10px; padding: 10px; border-radius: 8px; margin-bottom: 4px; transition: background 0.15s; }
.step-item:hover { background: var(--bg-hover); }
.step-item.running { background: rgba(102,126,234,0.08); }
.step-item.failed { background: rgba(255,77,79,0.06); }
.step-icon { width: 22px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.step-dot { width: 8px; height: 8px; border-radius: 50%; border: 2px solid #d9d9d9; }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.step-name { font-size: 12px; color: var(--text-primary); font-weight: 500; }
.step-tool { font-size: 10px; color: var(--text-muted); font-family: monospace; margin-top: 2px; }
.step-evidence { font-size: 10px; color: #52c41a; margin-top: 2px; }
.sidebar-empty { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: var(--text-muted); gap: 4px; }
.sidebar-empty p { font-size: 13px; margin: 0; }
.sidebar-empty span { font-size: 11px; }

/* 右侧 */
.chat-main { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.chat-header {
  height: 48px; display: flex; align-items: center; justify-content: space-between;
  padding: 0 20px; background: var(--bg-card); border-bottom: 1px solid var(--border-color);
}
.ch-left { display: flex; align-items: center; gap: 10px; }
.mode-badge { font-size: 11px; padding: 2px 10px; border-radius: 10px; font-weight: 500; }
.mode-badge.ai-control { background: rgba(82,196,26,0.1); color: #52c41a; }
.mode-badge.human-control { background: rgba(255,77,79,0.1); color: #ff4d4f; }
.mode-badge.readonly { background: rgba(250,173,20,0.1); color: #d48806; }
.chat-title { font-size: 14px; font-weight: 500; color: var(--text-secondary); }

.chat-messages { flex: 1; overflow-y: auto; padding: 20px; }
.chat-empty { text-align: center; padding: 40px 20px; }

.brain-anim { position: relative; display: inline-block; margin-bottom: 20px; }
.brain-pulse {
  position: absolute; inset: -10px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(102,126,234,0.15), transparent);
  animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse { 0%, 100% { transform: scale(0.95); opacity: 0.5; } 50% { transform: scale(1.05); opacity: 1; } }

.chat-empty h3 { font-size: 18px; color: var(--text-primary); margin: 0 0 6px; }
.chat-empty p { font-size: 13px; color: var(--text-muted); margin: 0 0 20px; }
.quick-cmds { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-bottom: 16px; }
.quick-chip {
  padding: 6px 14px; border-radius: 16px;
  background: var(--bg-card); border: 1px solid var(--border-color);
  font-size: 12px; color: var(--text-secondary); cursor: pointer;
  transition: all 0.15s;
}
.quick-chip:hover { background: rgba(102,126,234,0.08); border-color: #667eea; color: #667eea; }
.capability-hints { display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; }
.hint-tag { font-size: 11px; color: var(--text-muted); padding: 3px 10px; background: var(--bg-page); border-radius: 8px; }

.msg-row { display: flex; gap: 12px; margin-bottom: 20px; }
.msg-row.user { flex-direction: row-reverse; }
.msg-avatar { flex-shrink: 0; }
.avatar-circle {
  width: 32px; height: 32px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 600;
}
.avatar-circle.user { background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; }
.avatar-circle.ai { background: linear-gradient(135deg, #52c41a, #237804); color: #fff; }

.msg-body { max-width: 70%; }
.msg-row.user .msg-body { text-align: right; }
.msg-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.msg-row.user .msg-header { flex-direction: row-reverse; }
.msg-role { font-size: 11px; font-weight: 600; color: var(--text-muted); }
.msg-time { font-size: 10px; color: var(--text-muted); }
.risk-badge { font-size: 10px; padding: 1px 6px; border-radius: 8px; font-weight: 500; }
.risk-badge.L1 { background: rgba(82,196,26,0.1); color: #52c41a; }
.risk-badge.L2 { background: rgba(24,144,255,0.1); color: #1890ff; }
.risk-badge.L3 { background: rgba(250,173,20,0.1); color: #d48806; }

.msg-content {
  background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px;
  padding: 12px 16px; font-size: 13px; line-height: 1.7; white-space: pre-wrap; color: var(--text-primary);
}
.msg-row.user .msg-content { background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1)); border-color: rgba(102,126,234,0.2); }

.msg-steps { margin-top: 8px; display: flex; flex-direction: column; gap: 4px; }
.msg-step-item {
  display: flex; align-items: center; gap: 8px; font-size: 11px;
  padding: 6px 10px; background: var(--bg-page); border-radius: 6px; color: var(--text-secondary);
}
.step-detail { font-size: 10px; color: var(--text-muted); margin-left: auto; }

.confirm-bar {
  margin-top: 12px; padding: 12px; background: rgba(250,173,20,0.08);
  border: 1px solid rgba(250,173,20,0.2); border-radius: 10px; display: flex; gap: 8px;
}

.chat-input-bar { padding: 14px 20px; background: var(--bg-card); border-top: 1px solid var(--border-color); }
.chat-input :deep(.el-input__wrapper) { border-radius: 12px; box-shadow: none; border: 1px solid var(--border-color); }
.chat-input :deep(.el-input__wrapper:hover) { border-color: #667eea; }
</style>
