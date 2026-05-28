<template>
  <div class="page-container customer-panel">
    <div class="page-header">
      <h2>鐎广垺婀囩粻锛勬倞闂堛垺婢?/h2>
      <p>濞戝牊浼呮径鍕倞 璺?鐎广垺鍩涢張宥呭 璺?閹舵洝鐦旈惄鎴炲付</p>
    </div>

    <!-- 缂佺喕顓搁崡锛勫 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">娴犲﹥妫╁☉鍫熶紖閹鍣?/div>
          <div class="metric-value">{{ stats.totalMessages }}</div>
          <div class="metric-sub">鏉堝啯妲伴弮?{{ stats.messageTrend }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">濞叉槒绌导姘崇樈</div>
          <div class="metric-value" style="color: var(--color-primary);">{{ stats.activeConversations }}</div>
          <div class="metric-sub">閸忔湹鑵?{{ stats.unreadCount }} 閺夆剝婀拠?/div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">楠炲啿娼庨崫宥呯安閺冨爼妫?/div>
          <div class="metric-value" style="color: var(--color-success);">{{ stats.avgResponseTime }}</div>
          <div class="metric-sub">閻╊喗鐖? &lt; 3 閸掑棝鎸?/div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">濠娾剝鍓版惔?/div>
          <div class="metric-value" style="color: var(--color-warning);">{{ stats.satisfaction }}%</div>
          <div class="metric-sub">閸╄桨绨?{{ stats.satisfactionCount }} 閺壜ょ槑娴?/div>
        </div>
      </el-col>
    </el-row>

    <!-- 娑撹缍嬮敍姘箯閸掓銆?+ 閸欏啿顕拠?-->
    <div class="panel-body">
      <!-- 瀹革缚鏅剁€广垺鍩涢崚妤勩€?-->
      <div class="customer-list-panel">
        <div class="list-header">
          <el-input
            v-model="searchKeyword"
            placeholder="閹兼粎鍌ㄧ€广垺鍩涢幋鏍ㄧХ閹?.."
            :prefix-icon="Search"
            size="default"
            clearable
          />
        </div>
        <div class="list-filters">
          <el-radio-group v-model="filterType" size="small">
            <el-radio-button value="all">閸忋劑鍎?/el-radio-button>
            <el-radio-button value="unread">閺堫亣顕?/el-radio-button>
            <el-radio-button value="urgent">缁毖勨偓?/el-radio-button>
            <el-radio-button value="complaint">閹舵洝鐦?/el-radio-button>
          </el-radio-group>
          <div class="list-actions-top">
            <el-button size="small" text @click="markAllReadHandler">閸忋劑鍎村鑼额嚢</el-button>
            <el-button
              size="small" text type="warning"
              :disabled="selectedIds.length === 0"
              @click="transferHuman"
            >
              鏉烆兛姹夊?({{ selectedIds.length }})
            </el-button>
          </div>
        </div>
        <div class="customer-scroll" v-loading="loading">
          <div v-if="error" class="error-banner">
            <el-icon color="#ff4d4f"><WarningFilled /></el-icon>
            <span>{{ error }}</span>
            <el-button size="small" text type="primary" @click="fetchMessages">闁插秷鐦?/el-button>
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
                <span v-if="customer.type === 'complaint'" class="complaint-tag">閹舵洝鐦?/span>
                <span v-if="customer.type === 'urgent'" class="urgent-tag">缁毖勨偓?/span>
                <span v-if="customer.type === 'inquiry'" class="inquiry-tag">閸溿劏顕?/span>
                <span v-if="customer.escalated" class="escalated-tag">瀹告彃宕岀痪?/span>
              </div>
            </div>
          </div>
          <div v-if="filteredCustomers.length === 0 && !loading" class="empty-list">
            <p>閺嗗倹妫ら崠褰掑帳閻ㄥ嫬顓归幋閿嬬Х閹?/p>
          </div>
        </div>
      </div>

      <!-- 閸欏厖鏅剁€电鐦界粣妤€褰?-->
      <div class="conversation-panel" :class="{ 'no-selection': !activeCustomer }">
        <template v-if="activeCustomer">
          <!-- 鐎电鐦芥径鎾劥 -->
          <div class="conversation-header">
            <div class="conv-user-info">
              <el-avatar :size="38" :style="{ background: activeCustomer.avatarColor }">
                {{ activeCustomer.avatar }}
              </el-avatar>
              <div class="conv-user-detail">
                <span class="conv-user-name">{{ activeCustomer.sender }}</span>
                <span class="conv-user-status">
                  <span class="status-dot online"><span class="dot"></span>閸︺劎鍤?/span>
                  <span v-if="activeCustomer.type === 'complaint'" class="complaint-flag">
                    <el-icon color="#ff4d4f" :size="14"><WarningFilled /></el-icon> 閹舵洝鐦?
                  </span>
                  <span v-if="activeCustomer.type === 'urgent'" class="urgent-flag">缁毖勨偓?/span>
                </span>
              </div>
            </div>
            <div class="conv-actions">
              <el-button
                v-if="activeCustomer.type === 'complaint'"
                type="danger" size="small" plain
                @click="flagComplaint(activeCustomer)"
              >
                <el-icon><WarningFilled /></el-icon> 閺嶅洩顔囬幎鏇＄様
              </el-button>
              <el-button type="warning" size="small" plain @click="escalateToHuman(activeCustomer)">
                <el-icon><Switch /></el-icon> 鏉烆兛姹夊?
              </el-button>
              <el-button size="small" @click="handleMarkRead(activeCustomer)">
                <el-icon><Check /></el-icon> 閺嶅洩顔囧鑼额嚢
              </el-button>
            </div>
          </div>

          <!-- 濞戝牊浼呴崚妤勩€?-->
          <div class="messages-area" ref="messagesArea">
            <!-- 鐎广垺鍩涢崢鐔奉潗濞戝牊浼?-->
            <div class="message-row msg-left">
              <el-avatar :size="32" :style="{ background: activeCustomer.avatarColor }" class="msg-avatar">
                {{ activeCustomer.avatar }}
              </el-avatar>
              <div class="msg-bubble customer-bubble">
                <div class="msg-text">{{ activeCustomer.content }}</div>
                <div class="msg-time">{{ activeCustomer.time }}</div>
              </div>
            </div>

            <!-- 閸ョ偛顦插☉鍫熶紖閸掓銆?-->
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
                  <el-avatar :size="32" style="background: #1552F0;" class="msg-avatar">鐎?/el-avatar>
                </template>
              </div>
            </template>

            <!-- AI 閺呴缚鍏橀崶鐐差槻瀵ら缚顔?-->
            <div v-if="showSmartReplies" class="smart-replies-row">
              <span class="smart-label">AI 瀵ら缚顔呴崶鐐差槻閿?/span>
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

          <!-- 鏉堟挸鍙嗛崠鍝勭厵 -->
          <div class="input-area">
            <!-- 韫囶偅宓庨崶鐐差槻濡剝婢?-->
            <div class="quick-templates">
              <span class="template-label">韫囶偅宓庨崶鐐差槻閿?/span>
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
                placeholder="鏉堟挸鍙嗛崶鐐差槻閸愬懎顔愰敍灞惧瘻 Enter 閸欐垿鈧?.."
                resize="none"
                @keydown.enter.exact.prevent="sendReply"
              />
              <div class="input-actions">
                <el-button type="primary" @click="sendReply" :disabled="!replyText.trim()">
                  <el-icon><Promotion /></el-icon> 閸欐垿鈧?
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
            <h3>闁瀚ㄦ稉鈧担宥咁吂閹村嘲绱戞慨瀣嚠鐠?/h3>
            <p>瀹革缚鏅堕棃銏℃緲閺勫墽銇氬鍛槱閻炲棛娈戠€广垺鍩涘☉鍫熶紖</p>
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

// ===== 缂佺喕顓搁弫鐗堝祦 =====
const stats = reactive({
  totalMessages: 294,
  messageTrend: '+12%',
  activeConversations: 18,
  unreadCount: 7,
  avgResponseTime: '2.3閸?,
  satisfaction: 94.2,
  satisfactionCount: 156,
})

// ===== API 閺佺増宓?=====
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
        sender: m.sender || m.customerName || '閻劍鍩?,
        avatar: m.avatar || (m.sender || '閻?).charAt(0),
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

// ===== 缁涙盯鈧?=====
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

// ===== 闁瀚?=====
const toggleSelect = (msg) => {
  const idx = selectedIds.value.indexOf(msg.id)
  if (idx > -1) {
    selectedIds.value.splice(idx, 1)
  } else {
    selectedIds.value.push(msg.id)
  }
}

// ===== 閺嶅洩顔囧鑼额嚢 =====
const handleMarkRead = async (msg) => {
  try {
    await markRead(msg.id)
    msg.unread = false
    stats.unreadCount = messages.filter(m => m.unread).length
    ElMessage.success(`瀹稿弶鐖ｇ拋鑸偓?{msg.sender}閵嗗秶娈戝☉鍫熶紖娑撳搫鍑＄拠绫?
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
    ElMessage.success('瀹告彃鍙忛柈銊︾垼鐠侀璐熷鑼额嚢')
  } catch {
    messages.forEach((m) => (m.unread = false))
    stats.unreadCount = 0
  }
}

// ===== 鏉烆兛姹夊?=====
const transferHuman = async () => {
  try {
    await transferToHuman(selectedIds.value)
    messages.forEach(m => {
      if (selectedIds.value.includes(m.id)) m.escalated = true
    })
    ElMessage.success(`瀹告彃鐨?${selectedIds.value.length} 閺夆剝绉烽幁顖濇祮娴滃搫浼愭径鍕倞`)
    selectedIds.value = []
  } catch {
    ElMessage.warning('鏉烆兛姹夊銉嚞濮瑰倸鍑￠幓鎰唉')
    messages.forEach(m => {
      if (selectedIds.value.includes(m.id)) m.escalated = true
    })
    selectedIds.value = []
  }
}

// ===== 鐎电鐦界粻锛勬倞 =====
const activeCustomer = ref(null)
const replyText = ref('')
const messagesArea = ref(null)
const showSmartReplies = ref(false)
const smartReplies = ref([])
const conversationMessages = reactive({})

// ===== 韫囶偅宓庨崶鐐差槻濡剝婢?=====
const quickReplies = [
  { title: '闂傤喖鈧瑨顕?, content: '閹劌銈介敍浣哥发妤傛ê鍙存稉鐑樺亶閺堝秴濮熼敍宀冾嚞闂傤喗婀佹禒鈧稊鍫濆讲娴犮儱搴滈崝鈺傚亶閻ㄥ嫸绱? },
  { title: '鐠囬鈼㈢粵?, content: '婵傜晫娈戦敍灞惧灉濮濓絽婀稉鐑樺亶閺屻儴顕楅惄绋垮彠娣団剝浼呴敍宀冾嚞缁嬪秶鐡戦悧鍥у煝閵? },
  { title: '绾喛顓婚梻顕€顣?, content: '閹扮喕闃块幃銊ф畱閸欏秹顩敍灞惧灉瀹歌尙绮＄拋鏉跨秿娴滃棙鍋嶉惃鍕６妫版﹫绱濇导姘晼韫囶偂璐熼幃銊ヮ槱閻炲棎鈧? },
  { title: '閼峰瓨鐡?, content: '闂堢偛鐖堕幎杈ㄧ搼缂佹瑦鍋嶇敮锔芥降娑撳秳绌堕敍灞惧灉娴狀兛绱扮粩瀣祮閺嶇鐤勯獮鍓佺舶閹劋绔存稉顏呭姬閹板繒娈戠粵鏂款槻閵? },
  { title: '闁偓濞嗘崘顕╅弰?, content: '閹劎娈戦柅鈧▎鎯х殺閸?-5娑擃亜浼愭担婊勬）閸愬懎甯捄顖濈箲閸ョ儑绱濈拠閿嬫暈閹板繑鐓￠弨韬测偓鍌氼洤閺堝妫舵０妯哄讲闂呭繑妞傞懕鏃傞兇閹存垳婊戦妴? },
  { title: '閸欐垼鎻ｆ潻娑樺', content: '閹劎娈戠拋銏犲礋瀹告彃婀径鍕倞娑擃叏绱濇０鍕吀閸?8鐏忓繑妞傞崘鍛絺鐠愌嶇礉閸欐垼鎻ｉ崥搴濈窗閻厺淇婇柅姘辩叀閹劎澧垮ù浣稿礋閸欐灚鈧? },
  { title: '閹舵洝鐦旈崡鍥╅獓', content: '閹劎娈戦幎鏇＄様瀹歌尪顔囪ぐ鏇炶嫙閸楀洨楠囬懛鍏呭瘜缁犫€愁槱閻炲棴绱?4鐏忓繑妞傞崘鍛窗閺堝绗撴禍铏规暩鐠囨繆浠堢化缁樺亶閿涘矁顕穱婵囧瘮閻絻鐦介悾鍛粹偓姘モ偓? },
  { title: '缂佹挻娼€电鐦?, content: '閹扮喕闃块幃銊ф畱閼版劕绺剧粵澶婄窡閿涗礁顩ч弸婊嗙箷閺堝鍙炬禒鏍６妫版﹫绱濋梾蹇旀閼辨梻閮撮幋鎴滄粦閵嗗倻顨㈤幃銊ф晸濞茬粯鍓﹁箛顐磼' },
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
  ElMessage.success('閸ョ偛顦插鎻掑絺闁?)
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
      '閹扮喕闃块幃銊ф畱閸欏秹顩敍灞惧灉娴狀兛绱扮拋銈囨埂鐎电懓绶熼幃銊﹀絹閸戣櫣娈戦梻顕€顣介妴?,
      '闂堢偛鐖堕幎杈ㄧ搼閿涘本鍨滃鑼额唶瑜版洘鍋嶉惃鍕剰閸愮绱濇导姘箒娑撴挷姹夌捄鐔荤箻婢跺嫮鎮婇妴?,
    ]
  } else if (c.type === 'urgent') {
    smartReplies.value = [
      '婵傜晫娈戦敍灞惧灉妞诡兛绗傛稉鐑樺亶閺屻儴顕楅敍宀冾嚞缁嬪秶鐡戦敍?,
      '濮濓絽婀稉鐑樺亶閸旂姵鈧儱顦╅悶鍡曡厬閿涘矂顣╃拋?閸掑棝鎸撻崘鍛舶閹劎鐡熸径宥冣偓?,
    ]
  } else {
    smartReplies.value = [
      '婵傜晫娈戦敍灞藉嚒娑撶儤鍋嶇拋鏉跨秿閵嗗倽绻曢張澶婂従娴犳牕褰叉禒銉ュ簻閸斺晜鍋嶉惃鍕偋閿?,
      '閹扮喕闃块幃銊ф畱閸溿劏顕楅敍灞筋洤閺堝鎹㈡担鏇犳瀿闂傤噣娈㈤弮鎯颁粓缁粯鍨滄禒顒婄磼',
    ]
  }
  showSmartReplies.value = true
}

const escalateToHuman = (customer) => {
  ElMessageBox.confirm(
    `绾喛顓荤亸鍡愨偓?{customer.sender}閵嗗秶娈戞导姘崇樈鏉烆剚甯撮懛鍏呮眽瀹搞儱顓归張宥忕吹`,
    '鏉烆兛姹夊銉р€樼拋?,
    { confirmButtonText: '绾喛顓绘潪顒佸复', cancelButtonText: '閸欐牗绉?, type: 'warning' }
  ).then(() => {
    customer.escalated = true
    if (!conversationMessages[customer.id]) {
      conversationMessages[customer.id] = []
    }
    conversationMessages[customer.id].push({
      id: Date.now(),
      from: 'system',
      text: '--- 娴兼俺鐦藉鑼舵祮閹恒儴鍤︽禍鍝勪紣鐎广垺婀囬敍宀冾嚞缁嬪秴鈧?---',
      time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
    })
    ElNotification({
      title: '瀹歌尪娴嗛幒銉ゆ眽瀹?,
      message: `鐎广垺鍩涢妴?{customer.sender}閵嗗秶娈戞导姘崇樈瀹歌尪娴嗛幒銉ㄥ殾娴滃搫浼愮€广垺婀囬梼鐔峰灙`,
      type: 'warning',
      duration: 4000,
    })
    nextTick(() => scrollToBottom())
  }).catch(() => {})
}

const flagComplaint = (customer) => {
  ElMessageBox.confirm(
    `绾喛顓荤亸鍡愨偓?{customer.sender}閵嗗秵鐖ｇ拋棰佽礋閹舵洝鐦旂€广垺鍩涢敍鐔割劃閹垮秳缍旂亸鍡涒偓姘辩叀娑撹崵顓搁妴淇?
    '閹舵洝鐦旈弽鍥唶绾喛顓?,
    { confirmButtonText: '绾喛顓婚弽鍥唶', cancelButtonText: '閸欐牗绉?, type: 'danger' }
  ).then(() => {
    ElNotification({
      title: '閹舵洝鐦斿鍙夌垼鐠?,
      message: `鐎广垺鍩涢妴?{customer.sender}閵嗗秴鍑＄悮顐ｇ垼鐠侀璐熼幎鏇＄様閿涘瞼楠囬崚? L3閿涘苯鍑￠柅姘辩叀娑撹崵顓告径鍕倞`,
      type: 'error',
      duration: 5000,
    })
  }).catch(() => {})
}

// ===== 閻㈢喎鎳￠崨銊︽埂 =====
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

/* ===== 娑撹缍嬬敮鍐ㄧ湰 ===== */
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

/* ===== 瀹革缚鏅剁€广垺鍩涢崚妤勩€?===== */
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

/* ===== 閸欏厖鏅剁€电鐦界粣妤€褰?===== */
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

/* 鐎电鐦芥径鎾劥 */
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

/* 濞戝牊浼呴崠鍝勭厵 */
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

/* 閺呴缚鍏橀崶鐐差槻瀵ら缚顔?*/
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

/* 鏉堟挸鍙嗛崠鍝勭厵 */
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

/* 缁岃櫣濮搁幀?*/
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
