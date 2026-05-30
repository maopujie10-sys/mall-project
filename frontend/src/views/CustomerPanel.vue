<template>
  <div class="page-container customer-panel">
    <div class="page-header">
      <h2>{{ $t('customer.title') }}</h2>
      -
    </div>

    
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">{{ $t('customer.title') }}</div>
          <div class="metric-value">{{ stats.totalMessages }}</div>
          <div class="metric-sub"> {{ stats.messageTrend }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">{{ $t('customer.title') }}</div>
          <div class="metric-value" style="color: var(--color-primary);">{{ stats.activeConversations }}</div>
          <div class="metric-sub"> {{ stats.unreadCount }} </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">{{ $t('customer.title') }}</div>
          <div class="metric-value" style="color: var(--color-success);">{{ stats.avgResponseTime }}</div>
          <div class="metric-sub">: &lt; 3 </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">{{ $t('customer.title') }}</div>
          <div class="metric-value" style="color: var(--color-warning);">{{ stats.satisfaction }}%</div>
          <div class="metric-sub"> {{ stats.satisfactionCount }} </div>
        </div>
      </el-col>
    </el-row>

    <!--  +  -->
    <div class="panel-body">
      
      <div class="customer-list-panel">
        <div class="list-header">
          <el-input
            v-model="searchKeyword"
            placeholder="..."
            :prefix-icon="Search"
            size="default"
            clearable
          />
        </div>
        <div class="list-filters">
          <el-radio-group v-model="filterType" size="small">
            <el-radio-button value="all"></el-radio-button>
            <el-radio-button value="unread"></el-radio-button>
            <el-radio-button value="urgent"></el-radio-button>
            <el-radio-button value="complaint"></el-radio-button>
          </el-radio-group>
          <div class="list-actions-top">
            <el-button size="small" text @click="markAllReadHandler">OK</el-button>
            <el-button
              size="small" text type="warning"
              :disabled="selectedIds.length === 0"
              @click="transferHuman"
            >
               ({{ selectedIds.length }})
            </el-button>
          </div>
        </div>
        <div class="customer-scroll" v-loading="loading">
          <div v-if="error" class="error-banner">
            <el-icon color="#ff4d4f"><WarningFilled /></el-icon>
            <span>{{ error }}</span>
            <el-button size="small" text type="primary" @click="fetchMessages">OK</el-button>
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
                -
                -
                -
                -
              </div>
            </div>
          </div>
          <div v-if="filteredCustomers.length === 0 && !loading" class="empty-list">
            <p>{{ $t('customer.title') }}</p>
          </div>
        </div>
      </div>

      
      <div class="conversation-panel" :class="{ 'no-selection': !activeCustomer }">
        <template v-if="activeCustomer">
          
          <div class="conversation-header">
            <div class="conv-user-info">
              <el-avatar :size="38" :style="{ background: activeCustomer.avatarColor }">
                {{ activeCustomer.avatar }}
              </el-avatar>
              <div class="conv-user-detail">
                <span class="conv-user-name">{{ activeCustomer.sender }}</span>
                <span class="conv-user-status">
                  <span class="status-dot online"><span class="dot">{{ $t('customer.title') }}</span></span>
                  <span v-if="activeCustomer.type === 'complaint'" class="complaint-flag">
                    <el-icon color="#ff4d4f" :size="14"><WarningFilled /></el-icon> 
                  </span>
                  -
                </span>
              </div>
            </div>
            <div class="conv-actions">
              <el-button
                v-if="activeCustomer.type === 'complaint'"
                type="danger" size="small" plain
                @click="flagComplaint(activeCustomer)"
              >
                <el-icon><WarningFilled /></el-icon> 
              </el-button>
              <el-button type="warning" size="small" plain @click="escalateToHuman(activeCustomer)">
                <el-icon><Switch /></el-icon> 
              </el-button>
              <el-button size="small" @click="handleMarkRead(activeCustomer)">
                <el-icon><Check /></el-icon> 
              </el-button>
            </div>
          </div>

          
          <div class="messages-area" ref="messagesArea">
            
            <div class="message-row msg-left">
              <el-avatar :size="32" :style="{ background: activeCustomer.avatarColor }" class="msg-avatar">
                {{ activeCustomer.avatar }}
              </el-avatar>
              <div class="msg-bubble customer-bubble">
                <div class="msg-text">{{ activeCustomer.content }}</div>
                <div class="msg-time">{{ activeCustomer.time }}</div>
              </div>
            </div>

            
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
                  <el-avatar :size="32" style="background: #1552F0;" class="msg-avatar"></el-avatar>
                </template>
              </div>
            </template>

            <!-- AI  -->
            <div v-if="showSmartReplies" class="smart-replies-row">
              <span class="smart-label">AI </span>
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

          
          <div class="input-area">
            
            <div class="quick-templates">
              <span class="template-label">{{ $t('customer.title') }}</span>
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
                placeholder=" Enter ..."
                resize="none"
                @keydown.enter.exact.prevent="sendReply"
              />
              <div class="input-actions">
                <el-button type="primary" @click="sendReply" :disabled="!replyText.trim()">
                  <el-icon><Promotion /></el-icon> 
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
              <path d="M78 45 L85 52 L92 38" stroke="#1552F0" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>{{ $t('customer.title') }}</svg>
            <h3>{{ $t('customer.title') }}</h3>
            <p>{{ $t('customer.title') }}</p>
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

// =====  =====
const stats = reactive({
  totalMessages: 294,
  messageTrend: '+12%',
  activeConversations: 18,
  unreadCount: 7,
  avgResponseTime: '2.3',
  satisfaction: 94.2,
  satisfactionCount: 156,
})

// ===== API  =====
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
        sender: m.sender || m.customerName || '',
        avatar: m.avatar || (m.sender || '').charAt(0),
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

// =====  =====
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

// =====  =====
const toggleSelect = (msg) => {
  const idx = selectedIds.value.indexOf(msg.id)
  if (idx > -1) {
    selectedIds.value.splice(idx, 1)
  } else {
    selectedIds.value.push(msg.id)
  }
}

// =====  =====
const handleMarkRead = async (msg) => {
  try {
    await markRead(msg.id)
    msg.unread = false
    stats.unreadCount = messages.filter(m => m.unread).length
    ElMessage.success(`${msg.sender}`)
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
    ElMessage.success('OK')
  } catch {
    messages.forEach((m) => (m.unread = false))
    stats.unreadCount = 0
  }
}

// =====  =====
const transferHuman = async () => {
  try {
    await transferToHuman(selectedIds.value)
    messages.forEach(m => {
      if (selectedIds.value.includes(m.id)) m.escalated = true
    })
    ElMessage.success(` ${selectedIds.value.length} `)
    selectedIds.value = []
  } catch {
    ElMessage.warning('Warning')
    messages.forEach(m => {
      if (selectedIds.value.includes(m.id)) m.escalated = true
    })
    selectedIds.value = []
  }
}

// =====  =====
const activeCustomer = ref(null)
const replyText = ref('')
const messagesArea = ref(null)
const showSmartReplies = ref(false)
const smartReplies = ref([])
const conversationMessages = reactive({})

// =====  =====
const quickReplies = [
  { title: '', content: '' },
  { title: '', content: '' },
  { title: '', content: '' },
  { title: '', content: '' },
  { title: '', content: '3-5' },
  { title: '', content: '48' },
  { title: '', content: '24' },
  { title: '', content: '' },
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
  ElMessage.success('OK')
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
      '',
      '',
    ]
  } else if (c.type === 'urgent') {
    smartReplies.value = [
      '',
      '5',
    ]
  } else {
    smartReplies.value = [
      '',
      '',
    ]
  }
  showSmartReplies.value = true
}

const escalateToHuman = (customer) => {
  ElMessageBox.confirm(
    `${customer.sender}`,
    '',
    { confirmButtonText: '', cancelButtonText: '', type: 'warning' }
  ).then(() => {
    customer.escalated = true
    if (!conversationMessages[customer.id]) {
      conversationMessages[customer.id] = []
    }
    conversationMessages[customer.id].push({
      id: Date.now(),
      from: 'system',
      text: '---  ---',
      time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
    })
    ElNotification({
      title: '',
      message: `${customer.sender}`,
      type: 'warning',
      duration: 4000,
    })
    nextTick(() => scrollToBottom())
  }).catch(() => {})
}

const flagComplaint = (customer) => {
  ElMessageBox.confirm(
    `${customer.sender}`,
    '',
    { confirmButtonText: '', cancelButtonText: '', type: 'danger' }
  ).then(() => {
    ElNotification({
      title: '',
      message: `${customer.sender}: L3`,
      type: 'error',
      duration: 5000,
    })
  }).catch(() => {})
}

// =====  =====
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

/* =====  ===== */
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

/* =====  ===== */
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

/* =====  ===== */
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

/*  */
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

/*  */
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

/*  */
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

/*  */
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

/*  */
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
