<template>
  <div class="page-container customer-panel">
    <div class="page-header">
      <h2>客服管理面板</h2>
      <p>消息处理 · 客户服务 · 投诉监控</p>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">今日消息总量</div>
          <div class="metric-value">{{ stats.totalMessages }}</div>
          <div class="metric-sub">较昨日 {{ stats.messageTrend }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">活跃会话</div>
          <div class="metric-value" style="color: var(--color-primary);">{{ stats.activeConversations }}</div>
          <div class="metric-sub">其中 {{ stats.unreadCount }} 条未读</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">平均响应时间</div>
          <div class="metric-value" style="color: var(--color-success);">{{ stats.avgResponseTime }}</div>
          <div class="metric-sub">目标: &lt; 3 分钟</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">满意度</div>
          <div class="metric-value" style="color: var(--color-warning);">{{ stats.satisfaction }}%</div>
          <div class="metric-sub">基于 {{ stats.satisfactionCount }} 条评价</div>
        </div>
      </el-col>
    </el-row>

    <!-- 主体：左列表 + 右对话 -->
    <div class="panel-body">
      <!-- 左侧客户列表 -->
      <div class="customer-list-panel">
        <div class="list-header">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索客户或消息..."
            :prefix-icon="Search"
            size="default"
            clearable
          />
        </div>
        <div class="list-filters">
          <el-radio-group v-model="filterType" size="small">
            <el-radio-button value="all">全部</el-radio-button>
            <el-radio-button value="unread">未读</el-radio-button>
            <el-radio-button value="urgent">紧急</el-radio-button>
            <el-radio-button value="complaint">投诉</el-radio-button>
          </el-radio-group>
          <div class="list-actions-top">
            <el-button size="small" text @click="markAllReadHandler">全部已读</el-button>
            <el-button
              size="small" text type="warning"
              :disabled="selectedIds.length === 0"
              @click="transferHuman"
            >
              转人工 ({{ selectedIds.length }})
            </el-button>
          </div>
        </div>
        <div class="customer-scroll" v-loading="loading">
          <div v-if="error" class="error-banner">
            <el-icon color="#ff4d4f"><WarningFilled /></el-icon>
            <span>{{ error }}</span>
            <el-button size="small" text type="primary" @click="fetchMessages">重试</el-button>
          </div>
          <div
            v-for="customer in filteredCustomers"
            :key="customer.id"
            class="customer-item"
            :class="{
              active: activeCustomer?.id === customer.id,
              unread: customer.unread,
              selected: selectedIds.includes(customer.id)
            }"
            @click="openConversation(customer)"
          >
            <div class="customer-check" @click.stop="toggleSelect(customer)">
              <el-checkbox :model-value="selectedIds.includes(customer.id)" size="small" />
            </div>
            <div class="customer-avatar-col">
              <el-badge :value="customer.unread" :hidden="customer.unread === 0" :max="99">
                <el-avatar :size="44" :style="{ background: customer.avatarColor }">
                  {{ customer.avatar }}
                </el-avatar>
              </el-badge>
            </div>
            <div class="customer-info">
              <div class="customer-top">
                <span class="customer-name">{{ customer.sender }}</span>
                <span class="customer-time">{{ customer.time }}</span>
              </div>
              <div class="customer-preview">{{ customer.content }}</div>
              <div class="customer-tags">
                <span v-if="customer.type === 'complaint'" class="complaint-tag">投诉</span>
                <span v-if="customer.type === 'urgent'" class="urgent-tag">紧急</span>
                <span v-if="customer.type === 'inquiry'" class="inquiry-tag">咨询</span>
                <span v-if="customer.escalated" class="escalated-tag">已升级</span>
              </div>
            </div>
          </div>
          <div v-if="filteredCustomers.length === 0 && !loading" class="empty-list">
            <p>暂无匹配的客户消息</p>
          </div>
        </div>
      </div>

      <!-- 右侧对话窗口 -->
      <div class="conversation-panel" :class="{ 'no-selection': !activeCustomer }">
        <template v-if="activeCustomer">
          <!-- 对话头部 -->
          <div class="conversation-header">
            <div class="conv-user-info">
              <el-avatar :size="38" :style="{ background: activeCustomer.avatarColor }">
                {{ activeCustomer.avatar }}
              </el-avatar>
              <div class="conv-user-detail">
                <span class="conv-user-name">{{ activeCustomer.sender }}</span>
                <span class="conv-user-status">
                  <span class="status-dot online"><span class="dot"></span>在线</span>
                  <span v-if="activeCustomer.type === 'complaint'" class="complaint-flag">
                    <el-icon color="#ff4d4f" :size="14"><WarningFilled /></el-icon> 投诉
                  </span>
                  <span v-if="activeCustomer.type === 'urgent'" class="urgent-flag">紧急</span>
                </span>
              </div>
            </div>
            <div class="conv-actions">
              <el-button
                v-if="activeCustomer.type === 'complaint'"
                type="danger" size="small" plain
                @click="flagComplaint(activeCustomer)"
              >
                <el-icon><WarningFilled /></el-icon> 标记投诉
              </el-button>
              <el-button type="warning" size="small" plain @click="escalateToHuman(activeCustomer)">
                <el-icon><Switch /></el-icon> 转人工
              </el-button>
              <el-button size="small" @click="handleMarkRead(activeCustomer)">
                <el-icon><Check /></el-icon> 标记已读
              </el-button>
            </div>
          </div>

          <!-- 消息列表 -->
          <div class="messages-area" ref="messagesArea">
            <!-- 客户原始消息 -->
            <div class="message-row msg-left">
              <el-avatar :size="32" :style="{ background: activeCustomer.avatarColor }" class="msg-avatar">
                {{ activeCustomer.avatar }}
              </el-avatar>
              <div class="msg-bubble customer-bubble">
                <div class="msg-text">{{ activeCustomer.content }}</div>
                <div class="msg-time">{{ activeCustomer.time }}</div>
              </div>
            </div>

            <!-- 回复消息列表 -->
            <template v-for="msg in conversationMessages[activeCustomer.id]" :key="msg.id">
              <div v-if="msg.from === 'system'" class="system-message">{{ msg.text }}</div>
              <div v-else class="message-row" :class="msg.from === 'customer' ? 'msg-left' : 'msg-right'">
                <template v-if="msg.from === 'customer'">
                  <el-avatar :size="32" :style="{ background: activeCustomer.avatarColor }" class="msg-avatar">
                    {{ activeCustomer.avatar }}
                  </el-avatar>
                  <div class="msg-bubble customer-bubble">
                    <div class="msg-text">{{ msg.text }}</div>
                    <div class="msg-time">{{ msg.time }}</div>
                  </div>
                </template>
                <template v-else>
                  <div class="msg-bubble agent-bubble">
                    <div class="msg-text">{{ msg.text }}</div>
                    <div class="msg-time">{{ msg.time }}</div>
                  </div>
                  <el-avatar :size="32" style="background: #1552F0;" class="msg-avatar">客</el-avatar>
                </template>
              </div>
            </template>

            <!-- AI 智能回复建议 -->
            <div v-if="showSmartReplies" class="smart-replies-row">
              <span class="smart-label">AI 建议回复：</span>
              <span
                v-for="(reply, idx) in smartReplies"
                :key="idx"
                class="smart-chip"
                @click="sendSmartReply(reply)"
              >
                {{ reply }}
              </span>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="input-area">
            <!-- 快捷回复模板 -->
            <div class="quick-templates">
              <span class="template-label">快捷回复：</span>
              <template v-for="tpl in quickReplies" :key="tpl.title">
                <el-popover placement="top" :width="280" trigger="hover" :content="tpl.content">
                  <template #reference>
                    <el-tag size="small" class="template-tag" @click="sendSmartReply(tpl.content)">
                      {{ tpl.title }}
                    </el-tag>
                  </template>
                </el-popover>
              </template>
            </div>
            <div class="input-row">
              <el-input
                v-model="replyText"
                type="textarea" :rows="2"
                placeholder="输入回复内容，按 Enter 发送..."
                resize="none"
                @keydown.enter.exact.prevent="sendReply"
              />
              <div class="input-actions">
                <el-button type="primary" @click="sendReply" :disabled="!replyText.trim()">
                  <el-icon><Promotion /></el-icon> 发送
                </el-button>
              </div>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="no-conversation">
            <svg viewBox="0 0 120 120" width="80" height="80" fill="none">
              <circle cx="60" cy="60" r="50" stroke="#d9d9d9" stroke-width="2" stroke-dasharray="8 4"/>
              <path d="M35 45 L55 45 M35 55 L65 55 M35 65 L50 65" stroke="#d9d9d9" stroke-width="2.5" stroke-linecap="round"/>
              <circle cx="85" cy="45" r="18" fill="#1552F0" opacity="0.1"/>
              <path d="M78 45 L85 52 L92 38" stroke="#1552F0" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <h3>选择一位客户开始对话</h3>
            <p>左侧面板显示待处理的客户消息</p>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import { Search, Check, Switch, Promotion, WarningFilled } from '@element-plus/icons-vue'
import { getMessages, markRead, markAllRead, transferToHuman } from '@/api/customer'

// ===== 统计数据 =====
const stats = reactive({
  totalMessages: 294,
  messageTrend: '+12%',
  activeConversations: 18,
  unreadCount: 7,
  avgResponseTime: '2.3分',
  satisfaction: 94.2,
  satisfactionCount: 156,
})

// ===== API 数据 =====
const selectedIds = ref([])
const loading = ref(true)
const error = ref(null)
let pollTimer = null
const messages = reactive([])

const avatarColors = ['#1552F0', '#52c41a', '#faad14', '#722ed1', '#eb2f96', '#13c2c2', '#2f54eb', '#a0d911']

async function fetchMessages() {
  try {
    const data = await getMessages()
    if (Array.isArray(data)) {
      messages.splice(0, messages.length, ...data.map((m, i) => ({
        id: m.id || i + 1,
        sender: m.sender || m.customerName || '用户',
        avatar: m.avatar || (m.sender || '用').charAt(0),
        avatarColor: m.avatarColor || avatarColors[i % avatarColors.length],
        content: m.content || m.message || '',
        time: m.time || '-',
        type: m.type || 'inquiry',
        unread: m.unread !== undefined ? m.unread : true,
        escalated: m.escalated || false,
      })))
      stats.unreadCount = messages.filter(m => m.unread).length
      stats.activeConversations = messages.length
    }
    error.value = null
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// ===== 筛选 =====
const searchKeyword = ref('')
const filterType = ref('all')

const filteredCustomers = computed(() => {
  let result = [...messages]
  if (filterType.value === 'unread') {
    result = result.filter(c => c.unread)
  } else if (filterType.value === 'urgent') {
    result = result.filter(c => c.type === 'urgent')
  } else if (filterType.value === 'complaint') {
    result = result.filter(c => c.type === 'complaint')
  }
  if (searchKeyword.value.trim()) {
    const kw = searchKeyword.value.trim().toLowerCase()
    result = result.filter(c =>
      c.sender.toLowerCase().includes(kw) ||
      c.content.toLowerCase().includes(kw)
    )
  }
  return result
})

// ===== 选择 =====
const toggleSelect = (msg) => {
  const idx = selectedIds.value.indexOf(msg.id)
  if (idx > -1) {
    selectedIds.value.splice(idx, 1)
  } else {
    selectedIds.value.push(msg.id)
  }
}

// ===== 标记已读 =====
const handleMarkRead = async (msg) => {
  try {
    await markRead(msg.id)
    msg.unread = false
    stats.unreadCount = messages.filter(m => m.unread).length
    ElMessage.success(`已标记「${msg.sender}」的消息为已读`)
  } catch {
    msg.unread = false
    stats.unreadCount = messages.filter(m => m.unread).length
  }
}

const markAllReadHandler = async () => {
  try {
    await markAllRead()
    messages.forEach((m) => (m.unread = false))
    stats.unreadCount = 0
    ElMessage.success('已全部标记为已读')
  } catch {
    messages.forEach((m) => (m.unread = false))
    stats.unreadCount = 0
  }
}

// ===== 转人工 =====
const transferHuman = async () => {
  try {
    await transferToHuman(selectedIds.value)
    messages.forEach(m => {
      if (selectedIds.value.includes(m.id)) m.escalated = true
    })
    ElMessage.success(`已将 ${selectedIds.value.length} 条消息转人工处理`)
    selectedIds.value = []
  } catch {
    ElMessage.warning('转人工请求已提交')
    messages.forEach(m => {
      if (selectedIds.value.includes(m.id)) m.escalated = true
    })
    selectedIds.value = []
  }
}

// ===== 对话管理 =====
const activeCustomer = ref(null)
const replyText = ref('')
const messagesArea = ref(null)
const showSmartReplies = ref(false)
const smartReplies = ref([])
const conversationMessages = reactive({})

// ===== 快捷回复模板 =====
const quickReplies = [
  { title: '问候语', content: '您好！很高兴为您服务，请问有什么可以帮助您的？' },
  { title: '请稍等', content: '好的，我正在为您查询相关信息，请稍等片刻。' },
  { title: '确认问题', content: '感谢您的反馈，我已经记录了您的问题，会尽快为您处理。' },
  { title: '致歉', content: '非常抱歉给您带来不便，我们会立即核实并给您一个满意的答复。' },
  { title: '退款说明', content: '您的退款将在3-5个工作日内原路返回，请注意查收。如有问题可随时联系我们。' },
  { title: '发货进度', content: '您的订单已在处理中，预计在48小时内发货，发货后会短信通知您物流单号。' },
  { title: '投诉升级', content: '您的投诉已记录并升级至主管处理，24小时内会有专人电话联系您，请保持电话畅通。' },
  { title: '结束对话', content: '感谢您的耐心等待！如果还有其他问题，随时联系我们。祝您生活愉快！' },
]

const openConversation = (customer) => {
  activeCustomer.value = customer
  showSmartReplies.value = false
  replyText.value = ''
  if (!conversationMessages[customer.id]) {
    conversationMessages[customer.id] = []
  }
  nextTick(() => scrollToBottom())
}

const scrollToBottom = () => {
  if (messagesArea.value) {
    messagesArea.value.scrollTop = messagesArea.value.scrollHeight
  }
}

const sendReply = () => {
  if (!replyText.value.trim() || !activeCustomer.value) return
  const customer = activeCustomer.value
  const now = new Date()
  const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`

  if (!conversationMessages[customer.id]) {
    conversationMessages[customer.id] = []
  }
  conversationMessages[customer.id].push({
    id: Date.now(),
    from: 'agent',
    text: replyText.value.trim(),
    time: timeStr,
  })

  customer.content = replyText.value.trim()
  customer.time = timeStr
  customer.unread = false
  stats.unreadCount = messages.filter(m => m.unread).length

  replyText.value = ''
  showSmartReplies.value = false
  nextTick(() => scrollToBottom())
  ElMessage.success('回复已发送')
  generateSmartReplies()
}

const sendSmartReply = (text) => {
  replyText.value = text
  sendReply()
}

const generateSmartReplies = () => {
  const c = activeCustomer.value
  if (!c) return
  if (c.type === 'complaint') {
    smartReplies.value = [
      '感谢您的反馈，我们会认真对待您提出的问题。',
      '非常抱歉，我已记录您的情况，会有专人跟进处理。',
    ]
  } else if (c.type === 'urgent') {
    smartReplies.value = [
      '好的，我马上为您查询，请稍等！',
      '正在为您加急处理中，预计5分钟内给您答复。',
    ]
  } else {
    smartReplies.value = [
      '好的，已为您记录。还有其他可以帮助您的吗？',
      '感谢您的咨询，如有任何疑问随时联系我们！',
    ]
  }
  showSmartReplies.value = true
}

const escalateToHuman = (customer) => {
  ElMessageBox.confirm(
    `确认将「${customer.sender}」的会话转接至人工客服？`,
    '转人工确认',
    { confirmButtonText: '确认转接', cancelButtonText: '取消', type: 'warning' }
  ).then(() => {
    customer.escalated = true
    if (!conversationMessages[customer.id]) {
      conversationMessages[customer.id] = []
    }
    conversationMessages[customer.id].push({
      id: Date.now(),
      from: 'system',
      text: '--- 会话已转接至人工客服，请稍候 ---',
      time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
    })
    ElNotification({
      title: '已转接人工',
      message: `客户「${customer.sender}」的会话已转接至人工客服队列`,
      type: 'warning',
      duration: 4000,
    })
    nextTick(() => scrollToBottom())
  }).catch(() => {})
}

const flagComplaint = (customer) => {
  ElMessageBox.confirm(
    `确认将「${customer.sender}」标记为投诉客户？此操作将通知主管。`,
    '投诉标记确认',
    { confirmButtonText: '确认标记', cancelButtonText: '取消', type: 'danger' }
  ).then(() => {
    ElNotification({
      title: '投诉已标记',
      message: `客户「${customer.sender}」已被标记为投诉，级别: L3，已通知主管处理`,
      type: 'error',
      duration: 5000,
    })
  }).catch(() => {})
}

// ===== 生命周期 =====
onMounted(() => {
  fetchMessages()
  pollTimer = setInterval(fetchMessages, 15000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.customer-panel {
  padding: 20px 24px;
}

/* ===== 主体布局 ===== */
.panel-body {
  display: flex;
  gap: 0;
  height: calc(100vh - var(--header-height) - 220px);
  min-height: 500px;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  overflow: hidden;
  background: rgba(22,33,62,0.7);
  box-shadow: var(--shadow-card);
  transition: var(--theme-transition);
}

/* ===== 左侧客户列表 ===== */
.customer-list-panel {
  width: 380px;
  min-width: 340px;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  background: rgba(22,33,62,0.7);
  transition: var(--theme-transition);
}

.list-header {
  padding: 14px;
  border-bottom: 1px solid var(--border-color);
}

.list-filters {
  padding: 10px 14px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.list-actions-top {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.customer-scroll {
  flex: 1;
  overflow-y: auto;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  font-size: 12px;
  color: var(--color-danger);
  background: var(--color-danger-bg);
  border-bottom: 1px solid #ffccc7;
}

.customer-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 14px;
  cursor: pointer;
  border-bottom: 1px solid var(--border-light);
  border-left: 3px solid transparent;
  transition: all 0.15s;
}
.customer-item:last-child { border-bottom: none; }
.customer-item:hover { background: var(--bg-hover); }
.customer-item.active {
  background: var(--color-primary-bg);
  border-left-color: var(--color-primary);
}
.customer-item.selected {
  background: #e6f7ff;
}
.customer-item.unread .customer-name {
  font-weight: 700;
}

.customer-check {
  flex-shrink: 0;
  padding-top: 4px;
}

.customer-avatar-col {
  flex-shrink: 0;
}

.customer-info {
  flex: 1;
  min-width: 0;
}

.customer-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.customer-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.customer-time {
  font-size: 11px;
  color: var(--text-muted);
  flex-shrink: 0;
}

.customer-preview {
  font-size: 12px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 6px;
}

.customer-tags {
  display: flex;
  gap: 4px;
}

.complaint-tag {
  font-size: 10px;
  color: #ff4d4f;
  background: #fff2f0;
  border: 1px solid #ffccc7;
  padding: 1px 6px;
  border-radius: 3px;
  font-weight: 500;
}

.urgent-tag {
  font-size: 10px;
  color: #d48806;
  background: #fffbe6;
  border: 1px solid #ffe58f;
  padding: 1px 6px;
  border-radius: 3px;
  font-weight: 500;
}

.inquiry-tag {
  font-size: 10px;
  color: #1552F0;
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  padding: 1px 6px;
  border-radius: 3px;
  font-weight: 500;
}

.escalated-tag {
  font-size: 10px;
  color: #cf1322;
  background: #fff2f0;
  border: 1px solid #ffccc7;
  padding: 1px 6px;
  border-radius: 3px;
  font-weight: 500;
}

.empty-list {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--text-muted);
  font-size: 13px;
}

/* ===== 右侧对话窗口 ===== */
.conversation-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  transition: var(--theme-transition);
}

.conversation-panel.no-selection {
  background: rgba(13,16,37,0.55);
}

/* 对话头部 */
.conversation-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border-color);
  background: rgba(22,33,62,0.7);
  transition: var(--theme-transition);
}

.conv-user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.conv-user-detail {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.conv-user-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.conv-user-status {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: var(--text-muted);
}

.complaint-flag {
  display: flex;
  align-items: center;
  gap: 3px;
  color: var(--color-danger);
  font-weight: 500;
}

.urgent-flag {
  color: var(--color-warning);
  font-weight: 500;
  font-size: 11px;
  background: var(--color-warning-bg);
  padding: 1px 6px;
  border-radius: 3px;
}

.conv-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

/* 消息区域 */
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: rgba(13,16,37,0.55);
  transition: var(--theme-transition);
}

.message-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 18px;
}

.msg-left { justify-content: flex-start; }
.msg-right { justify-content: flex-end; }

.msg-avatar { flex-shrink: 0; margin-top: 4px; }

.msg-bubble {
  max-width: 65%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.6;
  word-break: break-word;
  position: relative;
}

.customer-bubble {
  background: rgba(22,33,62,0.7);
  border: 1px solid var(--border-color);
  border-top-left-radius: 4px;
  color: var(--text-primary);
  transition: var(--theme-transition);
}

.agent-bubble {
  background: var(--color-primary);
  color: #ffffff;
  border-top-right-radius: 4px;
}

.msg-text { margin-bottom: 4px; }

.msg-time {
  font-size: 10px;
  opacity: 0.6;
  text-align: right;
}

.system-message {
  text-align: center;
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 16px;
  padding: 4px 0;
}

/* 智能回复建议 */
.smart-replies-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  padding: 12px 0;
  border-top: 1px dashed var(--border-color);
  margin-top: 6px;
}

.smart-label {
  font-size: 12px;
  color: var(--text-muted);
  flex-shrink: 0;
}

.smart-chip {
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 14px;
  background: var(--color-primary-bg);
  color: var(--color-primary);
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
  max-width: 240px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.smart-chip:hover {
  border-color: var(--color-primary);
  background: var(--color-primary);
  color: #fff;
}

/* 输入区域 */
.input-area {
  border-top: 1px solid var(--border-color);
  padding: 12px 20px;
  background: rgba(22,33,62,0.7);
  transition: var(--theme-transition);
}

.quick-templates {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.template-label {
  font-size: 12px;
  color: var(--text-muted);
  flex-shrink: 0;
  margin-right: 2px;
}

.template-tag {
  cursor: pointer;
  transition: all 0.15s;
  font-size: 11px !important;
}

.template-tag:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.input-row {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.input-row :deep(.el-textarea) {
  flex: 1;
}

.input-actions {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* 空状态 */
.no-conversation {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: var(--text-muted);
  background: rgba(13,16,37,0.55);
  transition: var(--theme-transition);
}

.no-conversation h3 {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-secondary);
}

.no-conversation p {
  font-size: 13px;
  color: var(--text-muted);
}
</style>
