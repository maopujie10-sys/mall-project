锘?template>
  <div class="chat-page">
    <!-- 宸︿晶锛氫换鍔℃楠?-->
    <div class="chat-sidebar">
      <div class="sidebar-header">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/></svg>
        <span>浠诲姟杩涘害</span>
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
        <p>绛夊緟浠诲姟</p>
        <span>鍦ㄤ笅鏂硅緭鍏ユ寚浠?/span>
      </div>
    </div>

    <!-- 鍙充晶锛氬璇濆尯 -->
    <div class="chat-main">
      <div class="chat-header">
        <div class="ch-left">
          <span class="mode-badge" :class="currentMode">{{ modeLabel }}</span>
          <span class="chat-title">AI Agent 瀵硅瘽</span>
        </div>
        <div class="ch-right">
          <el-button text size="small" @click="clearChat">娓呯┖</el-button>
          <el-button :type="continuousMode?'success':'info'" text size="small" @click="toggleContinuousMode">{{continuousMode?'杩炵画':'鍗曟'}}</el-button>
        <el-button text size="small" @click="speakLastResponse">鎾斁</el-button>
        <el-button type="danger" text size="small" @click="$router.push('/emergency')">
            <el-icon><WarningFilled /></el-icon> 鎬ユ晳
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
          <h3>AI MallBrain 瀵硅瘽</h3>
          <p>杈撳叆涓枃鎸囦护锛孉I 鑷姩鍒嗘瀽骞舵墽琛?/p>
          <div class="quick-cmds">
            <div v-for="q in quickCommands" :key="q" class="quick-chip" @click="sendMessage(q)">{{ q }}</div>
          </div>
          <div class="capability-hints">
            <span class="hint-tag">馃洅 閲囬泦鍟嗗搧</span>
            <span class="hint-tag">馃懃 鐢熸垚鏁版嵁</span>
            <span class="hint-tag">馃 AI杩愮淮</span>
            <span class="hint-tag">馃搱 杩涘寲鎶ュ憡</span>
            <span class="hint-tag">馃捑 鍒涘缓澶囦唤</span>
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
              <span class="msg-role">{{ msg.role === 'user' ? '浣? : 'AI Agent' }}</span>
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
            <!-- 纭鎸夐挳 -->
            <div v-if="msg.needConfirm" class="confirm-bar">
              <el-button type="success" @click="confirmAction(msg, true)">鉁?纭鎵ц</el-button>
              <el-button type="danger" @click="confirmAction(msg, false)">鉁?鎷掔粷</el-button>
              <el-button @click="$router.push('/emergency')">杞汉宸ユ帴绠?/el-button>
            </div>
          </div>
        </div>
      </div>

      <SuperInput :disabled="isRunning" @send="onSuperSend" />
    </div>
  </div>
</template>

<script setup>
锘縤mport { ref, nextTick, onMounted, watch } from "vue"
import { useAgentStore } from "@/stores/agent"
import { useSystemStore } from "@/stores/system"
import SuperInput from "@/components/SuperInput.vue"
import { storeToRefs } from "pinia"
import { sendChat } from "@/api/agent"
import { analyzeImage } from "@/api/vision"
import { ElMessage } from "element-plus"

const agentStore = useAgentStore()
const systemStore = useSystemStore()
const { currentMode, modeLabel } = storeToRefs(systemStore)

const inputText = ref("")
const msgContainer = ref(null)
const isRunning = ref(false)
const messages = ref([])
const continuousMode = ref(false)
const superInputRef = ref(null)
const steps = ref([])

const quickCommands = [
  "Check server status",
  "Scan mall health", 
  "Generate evolution report",
  "Check Docker containers",
  "Inspect Nginx logs",
  "Create backup",
  "Check rotation domains",
  "View recent alerts",
]

// ===== Toggle continuous conversation =====
function toggleContinuousMode() {
  continuousMode.value = !continuousMode.value
  if (continuousMode.value) {
    ElMessage.success("Continuous mode ON")
  } else {
    ElMessage.info("Continuous mode OFF")
  }
}

// ===== TTS: speak text aloud =====
function speakText(text) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const clean = text.replace(/<[^>]+>/g, "").replace(/\*\*/g, "").replace(/`/g, "").replace(/```/g, "")
  const u = new SpeechSynthesisUtterance(clean)
  u.lang = "zh-CN"
  u.rate = 1.1
  window.speechSynthesis.speak(u)
}

function speakLastResponse() {
  const last = messages.value.slice().reverse().find(function(m) { return m.role === "ai" })
  if (last) speakText(last.text)
}

// ===== Format message =====
function formatMsg(text) {
  if (!text) return ""
  return text
    .replace(/\*\*(.+?)\*\*/g, "<b>$1</b>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\n/g, "<br>")
}

// ===== Auto scroll =====
function scrollBottom() {
  nextTick(function() {
    if (msgContainer.value) {
      msgContainer.value.scrollTop = msgContainer.value.scrollHeight
    }
  })
}

// ===== REAL API: send to AI backend =====
async function sendMessage(text) {
  const msg = typeof text === "string" ? text : inputText.value
  if (!msg || !msg.trim() || isRunning.value) return
  inputText.value = ""

  messages.value.push({
    role: "user",
    text: msg,
    time: new Date().toLocaleTimeString(),
  })
  scrollBottom()
  isRunning.value = true

  try {
    const res = await sendChat(msg)
    const data = res.data || res

    const aiMsg = {
      role: "ai",
      text: data.response || "AI thinking...",
      risk: data.risk_level || "L1",
      time: new Date().toLocaleTimeString(),
      needConfirm: data.need_confirm || false,
      steps: data.steps || [],
      taskId: data.task_id || "",
    }
    messages.value.push(aiMsg)
    scrollBottom()

    if (data.steps && data.steps.length) {
      steps.value = data.steps.map(function(s, i) {
        return {
          id: i + 1,
          name: s.name || ("Step " + (i + 1)),
          status: s.status || "done",
          tool: s.tool || "",
          evidence: s.evidence || "",
        }
      })
    }

    // Auto-speak in continuous mode
    if (continuousMode.value) {
      speakText(aiMsg.text)
    }
  } catch (err) {
    messages.value.push({
      role: "ai",
      text: "Connection error - backend not available",
      risk: "L4",
      time: new Date().toLocaleTimeString(),
    })
  }

  isRunning.value = false
  scrollBottom()
}

// ===== Handle SuperInput events (text/voice/camera/files) =====
async function onSuperSend(payload) {
  if (isRunning.value) return

  // Process camera photos - analyze with VisionAgent
  if (payload.files && payload.files.length > 0) {
    for (var i = 0; i < payload.files.length; i++) {
      var f = payload.files[i]
      if (f.type === "image" && f.file) {
        try {
          var dataUrl = await fileToDataUrl(f.file)
          messages.value.push({
            role: "user",
            text: "[Photo: " + (f.name || "camera") + "]",
            time: new Date().toLocaleTimeString(),
            image: dataUrl,
          })
          scrollBottom()

          try {
            var visionRes = await analyzeImage(dataUrl)
            if (visionRes && visionRes.data) {
              var desc = visionRes.data.description || visionRes.data.result || "Image analyzed"
              messages.value.push({
                role: "ai",
                text: "[Vision] " + (typeof desc === "string" ? desc : JSON.stringify(desc)),
                risk: "L1",
                time: new Date().toLocaleTimeString(),
              })
              if (continuousMode.value) {
                speakText("I see " + (typeof desc === "string" ? desc.substring(0, 200) : "an image"))
              }
            }
          } catch (e2) {
            messages.value.push({
              role: "ai",
              text: "[Vision] Photo received but analysis unavailable",
              risk: "L1",
              time: new Date().toLocaleTimeString(),
            })
          }
          scrollBottom()
        } catch (e3) {
          console.error("Photo error:", e3)
        }
      }
    }
  }

  // Send text message
  if (payload.text && payload.text.trim()) {
    await sendMessage(payload.text)
  }
}

// Helper: File to data URL
function fileToDataUrl(file) {
  return new Promise(function(resolve, reject) {
    var reader = new FileReader()
    reader.onload = function() { resolve(reader.result) }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

// ===== Confirm/approve =====
function confirmAction(msg, approved) {
  msg.needConfirm = false
  if (approved) {
    sendMessage("confirm task " + (msg.taskId || ""))
  } else {
    messages.value.push({
      role: "ai",
      text: "Task cancelled",
      risk: "L1",
      time: new Date().toLocaleTimeString(),
    })
  }
}

// ===== Clear =====
function clearChat() {
  messages.value = []
  steps.value = []
}

// ===== Watch continuous mode =====
watch(continuousMode, function(val) {
  if (val) {
    ElMessage.success("AI will auto-speak responses")
  }
})

</script>

<style scoped>
.chat-page { display: flex; height: calc(100vh - 52px); }

/* 宸︿晶 */
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

/* 鍙充晶 */
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
