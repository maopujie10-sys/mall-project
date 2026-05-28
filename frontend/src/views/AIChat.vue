<template>
  <div class="ai-console">
    <!-- 顶部状态栏 -->
    <div class="console-topbar">
      <div class="topbar-left">
        <span class="mode-tag" :class="currentMode">{{ modeLabel }}</span>
        <span class="topbar-title">Friday AI OS 总控台</span>
      </div>
      <div class="topbar-center">
        <el-tag size="small" type="success" v-if="modelStatus">🤖 {{ modelStatus }}</el-tag>
        <el-tag size="small" type="warning" v-if="pendingCount">⏳ {{ pendingCount }} 待审批</el-tag>
      </div>
      <div class="topbar-right">
        <el-button text size="small" @click="emergencyDialog = true" type="danger">⚡ 急救</el-button>
      </div>
    </div>

    <div class="console-body">
      <!-- 左侧：工具面板 -->
      <div class="console-tools">
        <el-input v-model="toolSearch" placeholder="搜索工具..." size="small" clearable style="margin-bottom:8px" />
        <div class="tool-categories" v-if="toolGroups.length > 0">
          <div v-for="(group, gi) in toolGroups" :key="gi" class="tool-group">
            <div class="group-header" @click="group.expanded = !group.expanded">
              <span>{{ group.icon }} {{ group.category }}</span>
              <span class="group-count">{{ group.tools.length }}</span>
            </div>
            <div v-show="group.expanded" class="group-tools">
              <div v-for="t in group.tools" :key="t.name" class="tool-item" :class="{active: activeTool === t.name}" @click="executeTool(t)">
                <div class="tool-name">{{ t.display_name }}</div>
                <div class="tool-desc">{{ t.description }}</div>
                <div class="tool-meta">
                  <el-tag :type="riskTag(t.risk_level)" size="small">{{ t.risk_level }}</el-tag>
                  <el-tag v-if="t.need_confirm" size="small" type="warning">需审批</el-tag>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else style="text-align:center;color:#999;padding:20px">暂无匹配工具</div>
      </div>

      <!-- 右侧：对话/结果区 -->
      <div class="console-chat">
        <!-- 消息列表 -->
        <div class="chat-messages" ref="msgContainer">
          <!-- 欢迎消息 -->
          <div v-if="messages.length === 0" class="welcome-screen">
            <div class="welcome-logo">
              <svg width="64" height="64" viewBox="0 0 64 64"><rect width="64" height="64" rx="16" fill="#667eea20"/><text x="32" y="42" text-anchor="middle" font-size="28" fill="#667eea">AI</text></svg>
            </div>
            <h3>Friday AI OS</h3>
            <p class="welcome-sub">65+ 真实工具 · 智能对话 · 自动运维</p>
            <div class="welcome-stats">
              <el-statistic title="可用工具" :value="allTools.length" />
              <el-statistic title="分类" :value="toolGroups.length" />
              <el-statistic title="待审批" :value="pendingCount" />
            </div>
            <div class="welcome-quick">
              <el-button @click="quickTool('server.status')" size="small">📊 查看服务器</el-button>
              <el-button @click="quickTool('docker.ps')" size="small">🐳 Docker 容器</el-button>
              <el-button @click="quickTool('rotation.domains')" size="small">🌐 轮值系统</el-button>
              <el-button @click="quickTool('nginx.status')" size="small">🔧 Nginx 状态</el-button>
              <el-button @click="quickTool('db.status')" size="small">🗄️ 数据库状态</el-button>
              <el-button @click="quickTool('ssl.status')" size="small">🔒 SSL 证书</el-button>
            </div>
          </div>

          <!-- 对话消息 -->
          <div v-for="(msg, i) in messages" :key="i" class="msg-row" :class="msg.role">
            <div class="msg-avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
            <div class="msg-content">
              <div class="msg-header">
                <span class="msg-role-tag">{{ msg.role === 'user' ? '你' : 'Friday AI' }}</span>
                <span class="msg-time">{{ msg.time }}</span>
              </div>
              <div class="msg-text">{{ msg.text }}</div>
              <!-- 工具执行结果 -->
              <div v-if="msg.result" class="msg-result">
                <pre>{{ msg.result }}</pre>
              </div>
              <!-- 表情反应 -->
              <div v-if="msg.role === 'ai' && !msg.typing" class="emoji-reactions">
                <span v-for="emo in reactions" :key="emo.emoji" class="emoji-btn" :class="{active: msg.reacted === emo.emoji}" @click="reactTo(msg, emo.emoji)" :title="emo.label">{{ emo.emoji }}</span>
              </div>
              <!-- 确认按钮 -->
              <div v-if="msg.needConfirm" class="confirm-bar">
                <el-button type="success" @click="confirmAction(msg, true)">✓ 确认执行</el-button>
                <el-button type="danger" @click="confirmAction(msg, false)">✗ 拒绝</el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区 -->
        <div class="chat-input">
          <el-input
            v-model="inputText"
            placeholder="输入指令，或点击左侧工具直接执行..."
            size="large"
            @keyup.enter="sendMessage"
            :disabled="loading"
          >
            <template #prefix>
              <el-icon @click="startVoice" style="cursor:pointer;font-size:18px;margin-right:4px" title="语音输入"><Microphone /></el-icon>
              <el-popover placement="top" :width="280" trigger="click" popper-class="emoji-picker-pop">
                <template #reference>
                  <el-icon style="cursor:pointer;font-size:18px" title="表情"><SmilingFace /></el-icon>
                </template>
                <div class="emoji-picker-grid">
                  <span v-for="e in emojiList" :key="e" class="emoji-pick-item" @click="inputText += e">{{ e }}</span>
                </div>
              </el-popover>
            </template>
            <template #append>
              <el-button type="primary" @click="sendMessage" :loading="loading" :disabled="!inputText.trim()">发送</el-button>
            </template>
          </el-input>
        </div>
      </div>
    </div>

    <!-- 急救弹窗 -->
    <el-dialog v-model="emergencyDialog" title="⚡ 急救面板" width="420">
      <div style="text-align:center;padding:16px">
        <el-button class="kill-btn" :class="{killed:isKilled}" :disabled="isKilled" @click="triggerKill">
          {{ isKilled ? '✅ 已切断 AI 写权限' : '🚫 立即切断 AI 写权限' }}
        </el-button>
        <div v-if="isKilled" style="margin-top:12px">
          <el-button type="primary" @click="restoreMode('ai_control')">恢复 AI 接管</el-button>
          <el-button @click="restoreMode('readonly')" style="margin-left:8px">只读模式</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { agentApi } from '@/api'
import { useSystemStore } from '@/stores/system'
import { storeToRefs } from 'pinia'

const systemStore = useSystemStore()
const { currentMode, modeLabel, isKilled } = storeToRefs(systemStore)

const inputText = ref('')
const messages = ref([])
const loading = ref(false)
const emergencyDialog = ref(false)
const activeTool = ref(null)
const toolSearch = ref('')
const pendingCount = ref(0)
const modelStatus = ref('')
const allTools = ref([])
const msgContainer = ref(null)
const tasks = ref([])

// 表情反应列表
const reactions = [
  { emoji: '👍', label: '赞' },
  { emoji: '❤️', label: '爱心' },
  { emoji: '😄', label: '哈哈' },
  { emoji: '🎉', label: '庆祝' },
  { emoji: '🔥', label: '太棒了' },
  { emoji: '💡', label: '有启发' },
]

// 常用表情列表
const emojiList = ['😀','😃','😄','😁','😆','😅','🤣','😂','🙂','😊','😇','🥰','😍','🤩','😘','😗','😚','😙','🥲','😋','😛','😜','🤪','😝','🤑','🤗','🤭','🫢','🫣','🤫','🤔','🫡','🤐','🤨','😐','😑','😶','🫥','😏','😒','🙄','😬','😮‍💨','🤥','😌','😔','😪','🤤','😴','😷','🤒','🤕','🤢','🤮','🥴','😵','🤯','🥳','🥺','😢','😭','😤','😠','😡','🤬','👋','🤚','🖐','✋','🖖','👌','🤌','🤏','✌️','🤞','🫰','🤟','🤘','🤙','👈','👉','👆','🖕','👇','👍','👎','✊','👊','🤛','🤜','👏','🙌','🫶','👐','🤲','🤝','🙏','🔥','⭐','✨','💡','💪','🚀','🎯','🎉','🎊','💯','✅','❌','❤️','🧡','💛','💚','💙','💜','🖤','🤍','🤎']

function reactTo(msg, emoji) {
  if (msg.reacted === emoji) {
    msg.reacted = ''
  } else {
    msg.reacted = emoji
  }
}

// 工具分类配置
const CATEGORIES = {
  server: { icon: '📊', label: '服务器' },
  docker: { icon: '🐳', label: 'Docker' },
  nginx: { icon: '🔧', label: 'Nginx' },
  rotation: { icon: '🌐', label: '轮值系统' },
  ssl: { icon: '🔒', label: 'SSL证书' },
  mall: { icon: '🏪', label: '商城管理' },
  monitor: { icon: '📈', label: '监控告警' },
  security: { icon: '🛡️', label: '安全防护' },
  db: { icon: '🗄️', label: '数据库' },
  brain: { icon: '🧠', label: '商城大脑' },
  evolution: { icon: '🌱', label: 'AI进化' },
  scraper: { icon: '🕷️', label: '采集中心' },
  playwright: { icon: '🎭', label: '浏览器' },
  autopilot: { icon: '🤖', label: '自动运维' },
  virtual: { icon: '🎮', label: '虚拟数据' },
  notify: { icon: '📢', label: '通知' },
  inspector: { icon: '🔍', label: '巡检' },
  report: { icon: '📋', label: '报告' },
}

const toolGroups = computed(() => {
  const search = toolSearch.value.toLowerCase()
  const groups = {}
  for (const t of allTools.value) {
    if (search && !t.name.includes(search) && !t.display_name.includes(search)) continue
    const cat = t.category || 'other'
    if (!groups[cat]) groups[cat] = { category: cat, icon: CATEGORIES[cat]?.icon || '📦', tools: [], expanded: true }
    groups[cat].tools.push(t)
  }
  return Object.values(groups)
})

function riskTag(level) {
  return { L1: 'success', L2: 'warning', L3: 'danger', L4: 'danger' }[level] || 'info'
}

async function fetchTools() {
  try {
    const r = await agentApi.get('/agent/tools')
    allTools.value = r.tools || []
  } catch { allTools.value = [] }
}

async function fetchTasks() {
  try {
    const r = await agentApi.get('/agent/tasks')
    tasks.value = r.tasks || []
    pendingCount.value = r.pending || 0
  } catch {}
}

async function fetchModelStatus() {
  try {
    const r = await agentApi.get('/agent/friday/models/status')
    modelStatus.value = r.active_model || 'auto'
  } catch { modelStatus.value = '' }
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || loading.value) return
  inputText.value = ''
  messages.value.push({ role: 'user', text, time: now() })
  loading.value = true

  try {
    const r = await agentApi.post('/agent/chat', { message: text })
    const fullText = r.response || r.reply || r.message || '执行完毕'
    const steps = r.steps || []
    const needConfirm = r.need_confirm || false
    const risk = r.risk_level || ''

    // 添加AI消息，先显示打字效果
    const msgIdx = messages.value.length
    messages.value.push({
      role: 'ai', text: fullText, displayText: '', time: now(),
      typing: true, steps, needConfirm, risk,
      result: steps.length ? JSON.stringify(steps, null, 2) : '',
    })

    // 打字机效果：逐字显示
    let charIdx = 0
    const typeInterval = setInterval(() => {
      if (charIdx < fullText.length) {
        messages.value[msgIdx].displayText = fullText.substring(0, charIdx + 1)
        charIdx++
        scrollBottom()
      } else {
        clearInterval(typeInterval)
        messages.value[msgIdx].typing = false
        messages.value[msgIdx].displayText = fullText
      }
    }, 30) // 每30ms一个字

    fetchTasks()
  } catch (e) {
    messages.value.push({ role: 'ai', text: '❌ ' + (e.response?.data?.detail || e.message), time: now() })
  }
  loading.value = false
  scrollBottom()
}

async function executeTool(t) {
  activeTool.value = t.name
  messages.value.push({
    role: 'user',
    text: `执行: ${t.display_name}`,
    time: now()
  })
  loading.value = true

  try {
    const r = await agentApi.post('/agent/chat', { message: `/tool ${t.name}` })
    const reply = r.response || r.reply || '执行完毕'
    messages.value.push({
      role: 'ai', text: reply, time: now(),
      needConfirm: r.need_confirm || false,
      result: r.steps ? JSON.stringify(r.steps, null, 2) : '',
    })
    fetchTasks()
  } catch (e) {
    messages.value.push({ role: 'ai', text: '工具执行失败: ' + (e.response?.data?.detail || e.message), time: now() })
  }
  loading.value = false
  scrollBottom()
}

function quickTool(name) {
  const t = allTools.value.find(x => x.name === name)
  if (t) executeTool(t)
}

function confirmAction(msg, approved) {
  msg.needConfirm = false
  // TODO: 调用确认API
  ElMessage.success(approved ? '已确认执行' : '已取消')
}

function startVoice() {
  try {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SR) { ElMessage.warning('浏览器不支持语音'); return }
    const sr = new SR()
    sr.lang = 'zh-CN'
    sr.onresult = (e) => { inputText.value = e.results[0][0].transcript; sendMessage() }
    sr.start()
  } catch { ElMessage.warning('语音启动失败') }
}

function triggerKill() {
  systemStore.triggerEmergencyKill()
  ElMessage.warning('AI 写权限已切断')
}

function restoreMode(mode) {
  systemStore.switchMode(mode)
  ElMessage.success('模式已切换')
  emergencyDialog.value = false
}

function now() {
  return new Date().toLocaleTimeString('zh-CN', { hour12: false })
}

function scrollBottom() {
  nextTick(() => {
    if (msgContainer.value) msgContainer.value.scrollTop = msgContainer.value.scrollHeight
  })
}

onMounted(() => {
  systemStore.fetchMode()
  fetchTools()
  fetchTasks()
  fetchModelStatus()
})
</script>

<style scoped>
.ai-console {
  display: flex; flex-direction: column;
  height: calc(100vh - var(--header-height, 0px) - 32px);
  background: var(--bg-page, #f5f5f5);
}

.console-topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 16px; background: #fff; border-bottom: 1px solid #e8e8e8;
}
.topbar-left { display: flex; align-items: center; gap: 12px; }
.topbar-title { font-size: 14px; font-weight: 600; color: #333; }
.topbar-center { display: flex; gap: 8px; }
.topbar-right { display: flex; gap: 8px; }
.mode-tag { font-size: 11px; padding: 2px 10px; border-radius: 10px; font-weight: 500; }
.mode-tag.ai-control { background: #e6f7e6; color: #52c41a; }

.console-body {
  display: flex; flex: 1; overflow: hidden;
}

/* 左侧工具面板 */
.console-tools {
  width: 280px; min-width: 280px;
  background: #fff; border-right: 1px solid #e8e8e8;
  display: flex; flex-direction: column; padding: 12px;
  overflow-y: auto;
}
.tool-categories { flex: 1; overflow-y: auto; }
.tool-group { margin-bottom: 4px; }
.group-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 10px; cursor: pointer; border-radius: 6px;
  font-size: 13px; font-weight: 500; color: #555;
}
.group-header:hover { background: #f5f5f5; }
.group-count { font-size: 11px; color: #999; background: #f0f0f0; padding: 0 6px; border-radius: 8px; }

.tool-item {
  padding: 6px 10px 6px 20px; cursor: pointer; border-radius: 4px;
  margin: 1px 0; transition: all 0.1s;
}
.tool-item:hover { background: #f0f5ff; }
.tool-item.active { background: #e6f7ff; border-left: 2px solid #1890ff; }
.tool-name { font-size: 12px; font-weight: 500; color: #333; }
.tool-desc { font-size: 11px; color: #999; margin-top: 2px; }
.tool-meta { display: flex; gap: 4px; margin-top: 4px; }

/* 右侧聊天区 */
.console-chat { flex: 1; display: flex; flex-direction: column; background: #fafafa; }
.chat-messages { flex: 1; overflow-y: auto; padding: 20px; }

/* 欢迎屏 */
.welcome-screen { text-align: center; padding: 40px 20px; }

/* 发光文字效果 */
.msg-text.glowing {
  background: linear-gradient(135deg, #667eea, #764ba2, #667eea);
  background-size: 200% 200%;
  animation: glowShift 3s ease infinite;
  color: #fff !important;
  border-color: transparent !important;
  box-shadow: 0 0 20px rgba(102,126,234,0.3);
}
@keyframes glowShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* 打字闪烁光标 */
.cursor-blink { animation: blink 0.8s infinite; color: #667eea; font-weight: bold; }
@keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0; } }

/* 打字中动画 */
.msg-text.typing { border-color: #667eea; box-shadow: 0 0 8px rgba(102,126,234,0.2); }

/* 打字点动画 */
.typing-dots span { animation: dotBounce 1.4s infinite; opacity: 0; font-size: 20px; line-height: 1; }
.typing-dots span:nth-child(1) { animation-delay: 0s; }
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes dotBounce { 0%,60%,100% { opacity: 0; transform: translateY(0); } 30% { opacity: 1; transform: translateY(-4px); } }

/* 步骤动画 */
.msg-steps { margin-top: 8px; }
.step-item { display: flex; align-items: center; gap: 6px; padding: 4px 8px; font-size: 12px; color: #555; }
.step-icon { font-size: 14px; }
.result-header { font-size: 12px; font-weight: 600; color: #667eea; margin-bottom: 4px; }

/* 风险标签 */
.risk-badge { margin-left: auto; }

/* 表情反应栏 */
.emoji-reactions {
  display: flex; gap: 4px; margin-top: 6px; padding-left: 2px;
}
.emoji-btn {
  font-size: 18px; cursor: pointer; padding: 2px 4px;
  border-radius: 4px; transition: all 0.2s;
  opacity: 0.4; filter: grayscale(0.5);
  line-height: 1;
}
.emoji-btn:hover { opacity: 1; filter: none; transform: scale(1.3); background: #f0f0f0; }
.emoji-btn.active { opacity: 1; filter: none; transform: scale(1.15); background: #e6f7ff; }

/* 表情选择器 */
.emoji-picker-pop { padding: 8px !important; }
.emoji-picker-grid {
  display: flex; flex-wrap: wrap; gap: 2px;
  max-height: 200px; overflow-y: auto;
}
.emoji-pick-item {
  font-size: 22px; cursor: pointer; padding: 3px; border-radius: 4px;
  transition: all 0.15s; line-height: 1;
}
.emoji-pick-item:hover { background: #e6f7ff; transform: scale(1.2); }

.msg-text {
  padding: 10px 14px; background: #fff; border: 1px solid #e8e8e8;
  border-radius: 8px; font-size: 13px; line-height: 1.6; white-space: pre-wrap;
  transition: all 0.3s;
}
.msg-row.user .msg-text { background: #e6f7ff; border-color: #91d5ff; }
.msg-row.user .msg-text.glowing { background: linear-gradient(135deg, #1890ff, #096dd9); color: #fff; }
.welcome-logo { margin-bottom: 16px; }
.welcome-screen h3 { font-size: 22px; color: #333; margin: 0 0 4px; }
.welcome-sub { font-size: 13px; color: #999; margin: 0 0 20px; }
.welcome-stats { display: flex; justify-content: center; gap: 40px; margin-bottom: 24px; }
.welcome-quick { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }

/* 消息 */
.msg-row { display: flex; gap: 12px; margin-bottom: 16px; }
.msg-avatar { font-size: 28px; flex-shrink: 0; }
.msg-content { flex: 1; }
.msg-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.msg-role-tag { font-size: 12px; font-weight: 600; color: #555; }
.msg-time { font-size: 11px; color: #bbb; }

.msg-result pre {
  background: #1e1e1e; color: #d4d4d4; padding: 12px; border-radius: 6px;
  font-size: 11px; overflow-x: auto; margin-top: 8px; max-height: 300px;
}
.confirm-bar { margin-top: 8px; display: flex; gap: 8px; }

/* 输入区 */
.chat-input { padding: 12px 16px; background: #fff; border-top: 1px solid #e8e8e8; }

/* 急救按钮 */
.kill-btn {
  width: 100%; height: 48px; font-size: 15px; font-weight: 600;
  background: #ff4d4f; color: #fff; border: none; border-radius: 8px; cursor: pointer;
}
.kill-btn.killed { background: #d9d9d9; color: #8c8c8c; cursor: not-allowed; }
</style>


