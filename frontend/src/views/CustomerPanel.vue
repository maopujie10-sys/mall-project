<template>
  <div class="page-container customer-panel">
    <div class="page-header">
      <h2>瀹㈡湇绠＄悊闈㈡澘</h2>
      <p>娑堟伅澶勭悊 路 瀹㈡埛鏈嶅姟 路 鎶曡瘔鐩戞帶</p>
    </div>

    <!-- 缁熻鍗＄墖 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">浠婃棩娑堟伅鎬婚噺</div>
          <div class="metric-value">{{ stats.totalMessages }}</div>
          <div class="metric-sub">杈冩槰鏃?{{ stats.messageTrend }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">娲昏穬浼氳瘽</div>
          <div class="metric-value" style="color: var(--color-primary);">{{ stats.activeConversations }}</div>
          <div class="metric-sub">鍏朵腑 {{ stats.unreadCount }} 鏉℃湭璇?/div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">骞冲潎鍝嶅簲鏃堕棿</div>
          <div class="metric-value" style="color: var(--color-success);">{{ stats.avgResponseTime }}</div>
          <div class="metric-sub">鐩爣: &lt; 3 鍒嗛挓</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">婊℃剰搴?/div>
          <div class="metric-value" style="color: var(--color-warning);">{{ stats.satisfaction }}%</div>
          <div class="metric-sub">鍩轰簬 {{ stats.satisfactionCount }} 鏉¤瘎浠?/div>
        </div>
      </el-col>
    </el-row>

    <!-- 涓讳綋锛氬乏鍒楄〃 + 鍙冲璇?-->
    <div class="panel-body">
      <!-- 宸︿晶瀹㈡埛鍒楄〃 -->
      <div class="customer-list-panel">
        <div class="list-header">
          <el-input
            v-model="searchKeyword"
            placeholder="鎼滅储瀹㈡埛鎴栨秷鎭?.."
            :prefix-icon="Search"
            size="default"
            clearable
          />
        </div>
        <div class="list-filters">
          <el-radio-group v-model="filterType" size="small">
            <el-radio-button value="all">鍏ㄩ儴</el-radio-button>
            <el-radio-button value="unread">鏈</el-radio-button>
            <el-radio-button value="urgent">绱ф€?/el-radio-button>
            <el-radio-button value="complaint">鎶曡瘔</el-radio-button>
          </el-radio-group>
          <div class="list-actions-top">
            <el-button size="small" text @click="markAllReadHandler">鍏ㄩ儴宸茶</el-button>
            <el-button
              size="small" text type="warning"
              :disabled="selectedIds.length === 0"
              @click="transferHuman"
            >
              杞汉宸?({{ selectedIds.length }})
            </el-button>
          </div>
        </div>
        <div class="customer-scroll" v-loading="loading">
          <div v-if="error" class="error-banner">
            <el-icon color="#ff4d4f"><WarningFilled /></el-icon>
            <span>{{ error }}</span>
            <el-button size="small" text type="primary" @click="fetchMessages">閲嶈瘯</el-button>
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
                <span v-if="customer.type === 'complaint'" class="complaint-tag">鎶曡瘔</span>
                <span v-if="customer.type === 'urgent'" class="urgent-tag">绱ф€?/span>
                <span v-if="customer.type === 'inquiry'" class="inquiry-tag">鍜ㄨ</span>
                <span v-if="customer.escalated" class="escalated-tag">宸插崌绾?/span>
              </div>
            </div>
          </div>
          <div v-if="filteredCustomers.length === 0 && !loading" class="empty-list">
            <p>鏆傛棤鍖归厤鐨勫鎴锋秷鎭?/p>
          </div>
        </div>
      </div>

      <!-- 鍙充晶瀵硅瘽绐楀彛 -->
      <div class="conversation-panel" :class="{ 'no-selection': !activeCustomer }">
        <template v-if="activeCustomer">
          <!-- 瀵硅瘽澶撮儴 -->
          <div class="conversation-header">
            <div class="conv-user-info">
              <el-avatar :size="38" :style="{ background: activeCustomer.avatarColor }">
                {{ activeCustomer.avatar }}
              </el-avatar>
              <div class="conv-user-detail">
                <span class="conv-user-name">{{ activeCustomer.sender }}</span>
                <span class="conv-user-status">
                  <span class="status-dot online"><span class="dot"></span>鍦ㄧ嚎</span>
                  <span v-if="activeCustomer.type === 'complaint'" class="complaint-flag">
                    <el-icon color="#ff4d4f" :size="14"><WarningFilled /></el-icon> 鎶曡瘔
                  </span>
                  <span v-if="activeCustomer.type === 'urgent'" class="urgent-flag">绱ф€?/span>
                </span>
              </div>
            </div>
            <div class="conv-actions">
              <el-button
                v-if="activeCustomer.type === 'complaint'"
                type="danger" size="small" plain
                @click="flagComplaint(activeCustomer)"
              >
                <el-icon><WarningFilled /></el-icon> 鏍囪鎶曡瘔
              </el-button>
              <el-button type="warning" size="small" plain @click="escalateToHuman(activeCustomer)">
                <el-icon><Switch /></el-icon> 杞汉宸?
              </el-button>
              <el-button size="small" @click="handleMarkRead(activeCustomer)">
                <el-icon><Check /></el-icon> 鏍囪宸茶
              </el-button>
            </div>
          </div>

          <!-- 娑堟伅鍒楄〃 -->
          <div class="messages-area" ref="messagesArea">
            <!-- 瀹㈡埛鍘熷娑堟伅 -->
            <div class="message-row msg-left">
              <el-avatar :size="32" :style="{ background: activeCustomer.avatarColor }" class="msg-avatar">
                {{ activeCustomer.avatar }}
              </el-avatar>
              <div class="msg-bubble customer-bubble">
                <div class="msg-text">{{ activeCustomer.content }}</div>
                <div class="msg-time">{{ activeCustomer.time }}</div>
              </div>
            </div>

            <!-- 鍥炲娑堟伅鍒楄〃 -->
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
                  <el-avatar :size="32" style="background: #1552F0;" class="msg-avatar">瀹?/el-avatar>
                </template>
              </div>
            </template>

            <!-- AI 鏅鸿兘鍥炲寤鸿 -->
            <div v-if="showSmartReplies" class="smart-replies-row">
              <span class="smart-label">AI 寤鸿鍥炲锛?/span>
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

          <!-- 杈撳叆鍖哄煙 -->
          <div class="input-area">
            <!-- 蹇嵎鍥炲妯℃澘 -->
            <div class="quick-templates">
              <span class="template-label">蹇嵎鍥炲锛?/span>
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
                placeholder="杈撳叆鍥炲鍐呭锛屾寜 Enter 鍙戦€?.."
                resize="none"
                @keydown.enter.exact.prevent="sendReply"
              />
              <div class="input-actions">
                <el-button type="primary" @click="sendReply" :disabled="!replyText.trim()">
                  <el-icon><Promotion /></el-icon> 鍙戦€?
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
            <h3>閫夋嫨涓€浣嶅鎴峰紑濮嬪璇?/h3>
            <p>宸︿晶闈㈡澘鏄剧ず寰呭鐞嗙殑瀹㈡埛娑堟伅</p>
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

// ===== 缁熻鏁版嵁 =====
const stats = reactive({
  totalMessages: 294,
  messageTrend: '+12%',
  activeConversations: 18,
  unreadCount: 7,
  avgResponseTime: '2.3鍒?,
  satisfaction: 94.2,
  satisfactionCount: 156,
})

// ===== API 鏁版嵁 =====
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
        sender: m.sender || m.customerName || '鐢ㄦ埛',
        avatar: m.avatar || (m.sender || '鐢?).charAt(0),
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

// ===== 绛涢€?=====
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

// ===== 閫夋嫨 =====
const toggleSelect = (msg) => {
  const idx = selectedIds.value.indexOf(msg.id)
  if (idx > -1) {
    selectedIds.value.splice(idx, 1)
  } else {
    selectedIds.value.push(msg.id)
  }
}

// ===== 鏍囪宸茶 =====
const handleMarkRead = async (msg) => {
  try {
    await markRead(msg.id)
    msg.unread = false
    stats.unreadCount = messages.filter(m => m.unread).length
    ElMessage.success(`宸叉爣璁般€?{msg.sender}銆嶇殑娑堟伅涓哄凡璇籤)
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
    ElMessage.success('宸插叏閮ㄦ爣璁颁负宸茶')
  } catch {
    messages.forEach((m) => (m.unread = false))
    stats.unreadCount = 0
  }
}

// ===== 杞汉宸?=====
const transferHuman = async () => {
  try {
    await transferToHuman(selectedIds.value)
    messages.forEach(m => {
      if (selectedIds.value.includes(m.id)) m.escalated = true
    })
    ElMessage.success(`宸插皢 ${selectedIds.value.length} 鏉℃秷鎭浆浜哄伐澶勭悊`)
    selectedIds.value = []
  } catch {
    ElMessage.warning('杞汉宸ヨ姹傚凡鎻愪氦')
    messages.forEach(m => {
      if (selectedIds.value.includes(m.id)) m.escalated = true
    })
    selectedIds.value = []
  }
}

// ===== 瀵硅瘽绠＄悊 =====
const activeCustomer = ref(null)
const replyText = ref('')
const messagesArea = ref(null)
const showSmartReplies = ref(false)
const smartReplies = ref([])
const conversationMessages = reactive({})

// ===== 蹇嵎鍥炲妯℃澘 =====
const quickReplies = [
  { title: '闂€欒', content: '鎮ㄥソ锛佸緢楂樺叴涓烘偍鏈嶅姟锛岃闂湁浠€涔堝彲浠ュ府鍔╂偍鐨勶紵' },
  { title: '璇风◢绛?, content: '濂界殑锛屾垜姝ｅ湪涓烘偍鏌ヨ鐩稿叧淇℃伅锛岃绋嶇瓑鐗囧埢銆? },
  { title: '纭闂', content: '鎰熻阿鎮ㄧ殑鍙嶉锛屾垜宸茬粡璁板綍浜嗘偍鐨勯棶棰橈紝浼氬敖蹇负鎮ㄥ鐞嗐€? },
  { title: '鑷存瓑', content: '闈炲父鎶辨瓑缁欐偍甯︽潵涓嶄究锛屾垜浠細绔嬪嵆鏍稿疄骞剁粰鎮ㄤ竴涓弧鎰忕殑绛斿銆? },
  { title: '閫€娆捐鏄?, content: '鎮ㄧ殑閫€娆惧皢鍦?-5涓伐浣滄棩鍐呭師璺繑鍥烇紝璇锋敞鎰忔煡鏀躲€傚鏈夐棶棰樺彲闅忔椂鑱旂郴鎴戜滑銆? },
  { title: '鍙戣揣杩涘害', content: '鎮ㄧ殑璁㈠崟宸插湪澶勭悊涓紝棰勮鍦?8灏忔椂鍐呭彂璐э紝鍙戣揣鍚庝細鐭俊閫氱煡鎮ㄧ墿娴佸崟鍙枫€? },
  { title: '鎶曡瘔鍗囩骇', content: '鎮ㄧ殑鎶曡瘔宸茶褰曞苟鍗囩骇鑷充富绠″鐞嗭紝24灏忔椂鍐呬細鏈変笓浜虹數璇濊仈绯绘偍锛岃淇濇寔鐢佃瘽鐣呴€氥€? },
  { title: '缁撴潫瀵硅瘽', content: '鎰熻阿鎮ㄧ殑鑰愬績绛夊緟锛佸鏋滆繕鏈夊叾浠栭棶棰橈紝闅忔椂鑱旂郴鎴戜滑銆傜鎮ㄧ敓娲绘剦蹇紒' },
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
  ElMessage.success('鍥炲宸插彂閫?)
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
      '鎰熻阿鎮ㄧ殑鍙嶉锛屾垜浠細璁ょ湡瀵瑰緟鎮ㄦ彁鍑虹殑闂銆?,
      '闈炲父鎶辨瓑锛屾垜宸茶褰曟偍鐨勬儏鍐碉紝浼氭湁涓撲汉璺熻繘澶勭悊銆?,
    ]
  } else if (c.type === 'urgent') {
    smartReplies.value = [
      '濂界殑锛屾垜椹笂涓烘偍鏌ヨ锛岃绋嶇瓑锛?,
      '姝ｅ湪涓烘偍鍔犳€ュ鐞嗕腑锛岄璁?鍒嗛挓鍐呯粰鎮ㄧ瓟澶嶃€?,
    ]
  } else {
    smartReplies.value = [
      '濂界殑锛屽凡涓烘偍璁板綍銆傝繕鏈夊叾浠栧彲浠ュ府鍔╂偍鐨勫悧锛?,
      '鎰熻阿鎮ㄧ殑鍜ㄨ锛屽鏈変换浣曠枒闂殢鏃惰仈绯绘垜浠紒',
    ]
  }
  showSmartReplies.value = true
}

const escalateToHuman = (customer) => {
  ElMessageBox.confirm(
    `纭灏嗐€?{customer.sender}銆嶇殑浼氳瘽杞帴鑷充汉宸ュ鏈嶏紵`,
    '杞汉宸ョ‘璁?,
    { confirmButtonText: '纭杞帴', cancelButtonText: '鍙栨秷', type: 'warning' }
  ).then(() => {
    customer.escalated = true
    if (!conversationMessages[customer.id]) {
      conversationMessages[customer.id] = []
    }
    conversationMessages[customer.id].push({
      id: Date.now(),
      from: 'system',
      text: '--- 浼氳瘽宸茶浆鎺ヨ嚦浜哄伐瀹㈡湇锛岃绋嶅€?---',
      time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
    })
    ElNotification({
      title: '宸茶浆鎺ヤ汉宸?,
      message: `瀹㈡埛銆?{customer.sender}銆嶇殑浼氳瘽宸茶浆鎺ヨ嚦浜哄伐瀹㈡湇闃熷垪`,
      type: 'warning',
      duration: 4000,
    })
    nextTick(() => scrollToBottom())
  }).catch(() => {})
}

const flagComplaint = (customer) => {
  ElMessageBox.confirm(
    `纭灏嗐€?{customer.sender}銆嶆爣璁颁负鎶曡瘔瀹㈡埛锛熸鎿嶄綔灏嗛€氱煡涓荤銆俙,
    '鎶曡瘔鏍囪纭',
    { confirmButtonText: '纭鏍囪', cancelButtonText: '鍙栨秷', type: 'danger' }
  ).then(() => {
    ElNotification({
      title: '鎶曡瘔宸叉爣璁?,
      message: `瀹㈡埛銆?{customer.sender}銆嶅凡琚爣璁颁负鎶曡瘔锛岀骇鍒? L3锛屽凡閫氱煡涓荤澶勭悊`,
      type: 'error',
      duration: 5000,
    })
  }).catch(() => {})
}

// ===== 鐢熷懡鍛ㄦ湡 =====
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

/* ===== 涓讳綋甯冨眬 ===== */
.panel-body {
  display: flex;
  gap: 0;
  height: calc(100vh - var(--header-height) - 220px);
  min-height: 500px;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  overflow: hidden;
  background: var(--bg-card);
  box-shadow: var(--shadow-card);
  transition: var(--theme-transition);
}

/* ===== 宸︿晶瀹㈡埛鍒楄〃 ===== */
.customer-list-panel {
  width: 380px;
  min-width: 340px;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  background: var(--bg-card);
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

/* ===== 鍙充晶瀵硅瘽绐楀彛 ===== */
.conversation-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  transition: var(--theme-transition);
}

.conversation-panel.no-selection {
  background: var(--bg-page);
}

/* 瀵硅瘽澶撮儴 */
.conversation-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-card);
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

/* 娑堟伅鍖哄煙 */
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: var(--bg-page);
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
  background: var(--bg-card);
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

/* 鏅鸿兘鍥炲寤鸿 */
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

/* 杈撳叆鍖哄煙 */
.input-area {
  border-top: 1px solid var(--border-color);
  padding: 12px 20px;
  background: var(--bg-card);
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

/* 绌虹姸鎬?*/
.no-conversation {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: var(--text-muted);
  background: var(--bg-page);
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
