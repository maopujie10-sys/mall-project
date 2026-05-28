<template>
  <div class="app-shell" :class="{ collapsed: sidebarCollapsed, dark: theme.isDark.value }">
    <!-- Electron 窗口标题栏 -->
    <header v-if="isElectron" class="electron-titlebar">
      <div class="titlebar-drag">
        <span class="titlebar-text">🎯 Friday AI OS</span>
      </div>
      <div class="titlebar-actions">
        <button class="tb-btn" @click="minimizeWin" title="最小化">─</button>
        <button class="tb-btn" @click="maximizeWin" title="最大化">□</button>
        <button class="tb-btn tb-close" @click="closeWin" title="关闭">✕</button>
      </div>
    </header>
    <aside class="sidebar" :class="{'mobile-open':mobileMenuOpen}">
      <div class="sidebar-brand" @click="$router.push('/friday')">
        <div class="brand-icon">
          <svg viewBox="0 0 40 40" width="32" height="32">
            <defs>
              <linearGradient id="fridayGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#667eea"/>
                <stop offset="100%" style="stop-color:#13c2c2"/>
              </linearGradient>
            </defs>
            <rect width="40" height="40" rx="10" fill="url(#fridayGrad)"/>
            <circle cx="20" cy="20" r="14" fill="none" stroke="white" stroke-width="1.5" opacity="0.6"/>
            <circle cx="20" cy="20" r="6" fill="white" opacity="0.9"/>
            <line x1="20" y1="6" x2="20" y2="14" stroke="white" stroke-width="2" stroke-linecap="round"/>
            <line x1="20" y1="26" x2="20" y2="34" stroke="white" stroke-width="2" stroke-linecap="round"/>
            <line x1="6" y1="20" x2="14" y2="20" stroke="white" stroke-width="2" stroke-linecap="round"/>
            <line x1="26" y1="20" x2="34" y2="20" stroke="white" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="brand-text" v-show="!sidebarCollapsed">
          <span class="brand-title">Friday AI OS</span>
          <span class="brand-sub">超级AI数字生命体</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <!-- 核心 -->
                <div class="nav-section">
          <div class="nav-section-label" v-show="!sidebarCollapsed"><span class="sec-icon">🤖</span> 核心</div>
          <router-link to="/friday" class="nav-item" :class="{ active: isActive('/friday') }"><span class="nav-icon">🧠</span><span>Friday 大脑</span></router-link>
          <router-link to="/dashboard" class="nav-item" :class="{ active: isActive('/dashboard') }"><span class="nav-icon">📊</span><span>仪表盘</span></router-link>
          <router-link to="/chat" class="nav-item" :class="{ active: isActive('/chat') }"><span class="nav-icon">💬</span><span>AI 对话</span></router-link>
        </div>
        <div class="nav-section">
          <div class="nav-section-label" v-show="!sidebarCollapsed"><span class="sec-icon">🧠</span> AI 能力</div>
          <router-link to="/ai-brain" class="nav-item" :class="{ active: isActive('/ai-brain') }"><span class="nav-icon">🧠</span><span>AI 大脑</span></router-link>
          <router-link to="/agents" class="nav-item" :class="{ active: isActive('/agents') }"><span class="nav-icon">🤖</span><span>Agent 列表</span></router-link>
          <router-link to="/trends" class="nav-item" :class="{ active: isActive('/trends') }"><span class="nav-icon">📈</span><span>趋势监控</span></router-link>
          <router-link to="/memory" class="nav-item" :class="{ active: isActive('/memory') }"><span class="nav-icon">💾</span><span>记忆中心</span></router-link>
          <router-link to="/models" class="nav-item" :class="{ active: isActive('/models') }"><span class="nav-icon">🔬</span><span>模型中心</span></router-link>
          <router-link to="/evolution" class="nav-item" :class="{ active: isActive('/evolution') }"><span class="nav-icon">🌱</span><span>进化报告</span></router-link>
          <router-link to="/video" class="nav-item" :class="{ active: isActive('/video') }"><span class="nav-icon">🎬</span><span>视频分析</span></router-link>
          <router-link to="/ocr" class="nav-item" :class="{ active: isActive('/ocr') }"><span class="nav-icon">🔍</span><span>OCR 识别</span></router-link>
        </div>
        <div class="nav-section">
          <div class="nav-section-label" v-show="!sidebarCollapsed"><span class="sec-icon">🛠️</span> 系统运维</div>
          <router-link to="/server" class="nav-item" :class="{ active: isActive('/server') }"><span class="nav-icon">🖥️</span><span>服务器</span></router-link>
          <router-link to="/docker" class="nav-item" :class="{ active: isActive('/docker') }"><span class="nav-icon">🐳</span><span>Docker</span></router-link>
          <router-link to="/nginx" class="nav-item" :class="{ active: isActive('/nginx') }"><span class="nav-icon">🔧</span><span>Nginx</span></router-link>
          <router-link to="/network" class="nav-item" :class="{ active: isActive('/network') }"><span class="nav-icon">🌐</span><span>网络工具</span></router-link>
          <router-link to="/github" class="nav-item" :class="{ active: isActive('/github') }"><span class="nav-icon">🐙</span><span>GitHub MCP</span></router-link>
          <router-link to="/phone" class="nav-item" :class="{ active: isActive('/phone') }"><span class="nav-icon">📞</span><span>AI电话助理</span></router-link>
          <router-link to="/emergency" class="nav-item" :class="{ active: isActive('/emergency') }"><span class="nav-icon">🚨</span><span>急救面板</span></router-link>
          <router-link to="/files" class="nav-item" :class="{ active: isActive('/files') }"><span class="nav-icon">📁</span><span>文件管理</span></router-link>
          <router-link to="/audit" class="nav-item" :class="{ active: isActive('/audit') }"><span class="nav-icon">📋</span><span>审计日志</span></router-link>
          <router-link to="/self-service" class="nav-item" :class="{ active: isActive('/self-service') }"><span class="nav-icon">🔧</span><span>自助服务</span></router-link>
        </div>
        <div class="nav-section">
          <div class="nav-section-label" v-show="!sidebarCollapsed"><span class="sec-icon">🛡️</span> 安全合规</div>
          <router-link to="/security" class="nav-item" :class="{ active: isActive('/security') }"><span class="nav-icon">🛡️</span><span>安全中心</span></router-link>
          <router-link to="/approval" class="nav-item" :class="{ active: isActive('/approval') }"><span class="nav-icon">✅</span><span>审批中心</span></router-link>
          <router-link to="/rollback" class="nav-item" :class="{ active: isActive('/rollback') }"><span class="nav-icon">🔄</span><span>回滚中心</span></router-link>
          
        </div>
          <div class="nav-item" style="color:#ff4d4f;cursor:pointer" @click="emergencyVisible=true"><span class="nav-icon">🚨</span><span>急救面板</span></div>
        <div class="nav-section">
          <div class="nav-section-label" v-show="!sidebarCollapsed"><span class="sec-icon">📊</span> 监控与数据</div>
          <router-link to="/alert" class="nav-item" :class="{ active: isActive('/alert') }"><span class="nav-icon">🔔</span><span>告警中心</span></router-link>
          <router-link to="/tasks" class="nav-item" :class="{ active: isActive('/tasks') }"><span class="nav-icon">📋</span><span>任务中心</span></router-link>
          <router-link to="/site" class="nav-item" :class="{ active: isActive('/site') }"><span class="nav-icon">🔍</span><span>站点检测</span></router-link>
          <router-link to="/rotation" class="nav-item" :class="{ active: isActive('/rotation') }"><span class="nav-icon">🌐</span><span>域名轮值</span></router-link>
          <router-link to="/database" class="nav-item" :class="{ active: isActive('/database') }"><span class="nav-icon">🗄️</span><span>数据库</span></router-link>
          <router-link to="/scraper" class="nav-item" :class="{ active: isActive('/scraper') }"><span class="nav-icon">🕷️</span><span>采集中心</span></router-link>
        </div>
        <div class="nav-section">
          <div class="nav-section-label" v-show="!sidebarCollapsed"><span class="sec-icon">🏪</span> 运营扩展</div>
          <router-link to="/mall" class="nav-item" :class="{ active: isActive('/mall') }"><span class="nav-icon">🏪</span><span>商城管理</span></router-link>
          <router-link to="/customer" class="nav-item" :class="{ active: isActive('/customer') }"><span class="nav-icon">👥</span><span>客服系统</span></router-link>
          <router-link to="/virtual" class="nav-item" :class="{ active: isActive('/virtual') }"><span class="nav-icon">🎮</span><span>虚拟数据</span></router-link>
          <router-link to="/image-process" class="nav-item" :class="{ active: isActive('/image-process') }"><span class="nav-icon">🖼️</span><span>商品图处理</span></router-link>
          <router-link to="/multilang" class="nav-item" :class="{ active: isActive('/multilang') }"><span class="nav-icon">🌍</span><span>多语言发布</span></router-link>
          <router-link to="/batch-upload" class="nav-item" :class="{ active: isActive('/batch-upload') }"><span class="nav-icon">📋</span><span>批量上架</span></router-link>
          <router-link to="/auto-reply" class="nav-item" :class="{ active: isActive('/auto-reply') }"><span class="nav-icon">🤖</span><span>自动回复</span></router-link>
          <router-link to="/order-alert" class="nav-item" :class="{ active: isActive('/order-alert') }"><span class="nav-icon">🔔</span><span>订单预警</span></router-link>
          <router-link to="/plugins" class="nav-item" :class="{ active: isActive('/plugins') }"><span class="nav-icon">🧩</span><span>技能市场</span></router-link>
        </div>
                </el-dropdown-item>
              </el-dropdown-menu>
            <div class="ai-float-widget"><el-button class="ai-float-btn" @click="floatDialog=true" title="AI 助手"><el-icon :size="22"><ChatDotRound /></el-icon></el-button></div>
<el-dialog v-model="floatDialog" title="💬 AI 助手" width="380" :close-on-click-modal="false" class="float-chat-dialog"><div class="float-chat-body"><div class="float-msg-area" ref="floatMsgRef"><div v-for="(m,i) in floatMessages" :key="i" class="float-msg-row" :class="m.role"><div class="float-msg-text">{{ m.text }}</div></div><div v-if="floatMessages.length===0" style="text-align:center;color:#999;padding:40px 0;font-size:13px">输入问题，AI 帮你解答</div></div><div class="float-input-row"><el-input v-model="floatInput" placeholder="输入问题..." size="small" @keyup.enter="sendFloatMsg" :disabled="floatLoading"><template #append><el-button @click="sendFloatMsg" :loading="floatLoading" :disabled="!floatInput.trim()" size="small">发送</el-button></template></el-input></div></div></el-dialog>
</template>
          </el-dropdown>
        </div>
      </header>

      <main class="content-area">
        <router-view v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
    <LiveTaskPanel />
    <el-dialog v-model="emergencyVisible" title="🚨 急救面板" width="520px" top="8vh"><EmergencyPanel :embedded="true" /></el-dialog>
    <!-- 全局 AI 浮动图标 -->
  </div>
</template>

<script setup>

const tokenDialogVisible = ref(false)
const tokenInput = ref(localStorage.getItem('agent_token') || '')

function saveToken() {
  localStorage.setItem('agent_token', tokenInput.value)
  tokenDialogVisible.value = false
  ElMessage.success('Token 已保存')
}

import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useSystemStore } from '@/stores/system'
import { useThemeStore } from '@/stores/theme'
const isElectron = !!window.electronAPI
const minimizeWin = () => window.electronAPI?.minimize()
const maximizeWin = () => window.electronAPI?.maximize()
const closeWin = () => window.electronAPI?.close()
import { ElMessage } from "element-plus"
import LiveTaskPanel from '@/components/LiveTaskPanel.vue'
import EmergencyPanel from '@/views/EmergencyPanel.vue'
import { storeToRefs } from 'pinia'

const route = useRoute()
const emergencyVisible = ref(false)
function switchLang(lang) { if (window.__vue_app__?.config?.globalProperties?.$i18n) { window.__vue_app__.config.globalProperties.$i18n.locale = lang; localStorage.setItem("lang", lang) } }
const system = useSystemStore()
const theme = useThemeStore()
const { currentMode, modeLabel } = storeToRefs(system)

const sidebarCollapsed = ref(false)
const mobileMenuOpen = ref(false)

const currentTitle = computed(() => route.meta?.title || '')
const currentRoute = computed(() => route.path)

function isActive(path) {
  return route.path === path || route.path.startsWith(path + '/')
}

onMounted(() => {
  theme.initTheme()
  system.fetchMode()
})

const floatDialog = ref(false)
const floatInput = ref("")
const floatLoading = ref(false)
const floatMessages = ref([])
const floatMsgRef = ref(null)

async function sendFloatMsg() {
  const text = floatInput.value.trim()
  if (!text || floatLoading.value) return
  floatInput.value = ""
  floatMessages.value.push({role:"user",text})
  floatLoading.value = true
  try {
    const {agentApi} = await import("@/api")
    const r = await agentApi.post("/agent/chat",{message:text})
    floatMessages.value.push({role:"ai",text:r.response||r.reply||r.message||"收到"})
  } catch(e) {
    floatMessages.value.push({role:"ai",text:"连接失败: "+(e.message||"")})
  }
  floatLoading.value = false
  setTimeout(()=>{if(floatMsgRef.value)floatMsgRef.value.scrollTop=floatMsgRef.value.scrollHeight},100)
}

</script>

<style scoped>
.ai-float-widget{position:fixed;bottom:24px;right:24px;z-index:9999}
.ai-float-btn{width:56px;height:56px;border-radius:50%;background:linear-gradient(135deg,#667eea,#764ba2);border:none;color:#fff;box-shadow:0 4px 16px rgba(102,126,234,0.4);cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s}
.float-chat-body{display:flex;flex-direction:column;height:400px}
.float-msg-area{flex:1;overflow-y:auto;padding:12px}
.float-msg-row{margin-bottom:10px}
.float-msg-text{display:inline-block;padding:8px 12px;border-radius:8px;font-size:13px;max-width:85%;line-height:1.5}
.float-msg-row .float-msg-text{background:#f0f0f0;color:#333}
.float-msg-row.user{text-align:right}
.float-msg-row.user .float-msg-text{background:#1890ff;color:#fff}
.float-input-row{padding:8px 12px;border-top:1px solid #eee}

.app-shell { display: flex; height: 100vh; background: var(--bg-page); overflow: hidden; }

.sidebar {
  width: 240px; min-width: 240px;
  background: #0a0d1a;
  display: flex; flex-direction: column;
  border-right: 1px solid rgba(102,126,234,0.1);
  transition: width 0.25s, min-width 0.25s;
  z-index: 200;
}
.collapsed .sidebar { width: 68px; min-width: 68px; }

.sidebar-brand {
  display: flex; align-items: center; gap: 12px;
  padding: 20px 18px; cursor: pointer;
  border-bottom: 1px solid rgba(102,126,234,0.1);
}
.brand-text { display: flex; flex-direction: column; overflow: hidden; }
.brand-title { font-size: 15px; font-weight: 700; color: #fff; letter-spacing: -0.3px; }
.brand-sub { font-size: 10px; color: rgba(102,126,234,0.6); }

.sidebar-nav { flex: 1; overflow-y: auto; overflow-x: hidden; padding: 12px 10px; }
.nav-section { margin-bottom: 4px; }
.nav-section .sec-icon { margin-right: 4px; }
.nav-section-label {
  font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;
  color: rgba(102,126,234,0.4); padding: 12px 10px 6px; white-space: nowrap;
}

.nav-item { display: flex; align-items: center; gap: 8px; }
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: 8px;
  color: rgba(255,255,255,0.5); text-decoration: none;
  font-size: 13px; transition: all 0.15s; margin-bottom: 2px; white-space: nowrap;
}
.nav-item:hover { background: rgba(102,126,234,0.1); color: rgba(255,255,255,0.85); }
.nav-item.active {
  background: linear-gradient(135deg, rgba(102,126,234,0.2), rgba(19,194,194,0.15));
  color: #fff;
}
.nav-item.active::before {
  content: ''; position: absolute; left: 0; top: 50%; transform: translateY(-50%);
  width: 3px; height: 20px;
  background: linear-gradient(180deg, #667eea, #13c2c2);
  border-radius: 0 3px 3px 0;
}
.nav-icon { width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.nav-label { flex: 1; overflow: hidden; text-overflow: ellipsis; }

.sidebar-footer { padding: 12px; border-top: 1px solid rgba(102,126,234,0.1); }
.collapse-btn {
  width: 100%; padding: 8px; border: none;
  background: rgba(102,126,234,0.08); color: rgba(255,255,255,0.3);
  border-radius: 6px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.15s;
}
.collapse-btn:hover { background: rgba(102,126,234,0.15); color: rgba(255,255,255,0.6); }

.main-area { flex: 1; display: flex; flex-direction: column; min-width: 0; background: var(--bg-page); }

.top-bar {
  height: 52px; min-height: 52px;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 20px;
  background: var(--bg-card); border-bottom: 1px solid var(--border-color);
  z-index: 100;
}
.top-left { display: flex; align-items: center; }
.top-right { display: flex; align-items: center; gap: 14px; }

.status-indicators { display: flex; align-items: center; gap: 6px; }
.status-dot { width: 7px; height: 7px; border-radius: 50%; }
.status-dot.online { background: #52c41a; box-shadow: 0 0 6px rgba(82,196,26,0.5); }
.status-label { font-size: 11px; color: var(--text-muted); }

.mode-tag { font-size: 11px; padding: 3px 10px; border-radius: 10px; font-weight: 500; }
.mode-tag.ai-control { background: rgba(82,196,26,0.12); color: #52c41a; }
.mode-tag.human-control { background: rgba(255,77,79,0.12); color: #ff4d4f; }

.theme-btn {
  display: flex; align-items: center; justify-content: center;
  width: 32px; height: 32px; border-radius: 6px;
  border: 1px solid var(--border-color);
  background: var(--bg-card); color: var(--text-secondary);
  cursor: pointer; transition: all 0.15s; padding: 0;
}
.theme-btn:hover { background: var(--bg-hover); }

.user-chip { display: flex; align-items: center; padding: 3px 8px; border-radius: 6px; cursor: pointer; transition: background 0.15s; }
.user-chip:hover { background: var(--bg-hover); }

.content-area { flex: 1; overflow-y: auto; overflow-x: hidden; }
.page-fade-enter-active, .page-fade-leave-active { transition: opacity 0.2s; }
.page-fade-enter-from, .page-fade-leave-to { opacity: 0; }

/* Electron 标题栏 */
.electron-titlebar {
  position: fixed; top: 0; left: 0; right: 0; height: 32px;
  display: flex; align-items: center; justify-content: space-between;
  background: #0a0d1a; z-index: 9999; -webkit-app-region: drag;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.titlebar-drag { flex: 1; display: flex; align-items: center; padding-left: 12px; }
.titlebar-text { font-size: 12px; color: rgba(255,255,255,0.5); letter-spacing: 0.5px; }
.titlebar-actions { display: flex; -webkit-app-region: no-drag; }
.tb-btn {
  width: 46px; height: 32px; border: none; background: transparent;
  color: rgba(255,255,255,0.6); font-size: 12px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.15s;
}
.tb-btn:hover { background: rgba(255,255,255,0.1); color: #fff; }
.tb-close:hover { background: #e81123; color: #fff; }
/* Adjust sidebar and main content for title bar */
.app-shell { padding-top: 32px; }
/* Restore sidebar height to fill */
.sidebar { height: calc(100vh - 32px); top: 32px; }
.main-area { height: calc(100vh - 32px); overflow-y: auto; }

/* 通知面板 */
.notif-item { display: flex; gap: 10px; padding: 10px; border-radius: 6px; cursor: pointer; transition: background 0.15s; margin-bottom: 4px; }
.notif-item:hover { background: #f5f5f5; }
.notif-item.unread { background: #e6f7ff; }
.notif-icon { font-size: 20px; flex-shrink: 0; }
.notif-body { flex: 1; min-width: 0; }
.notif-title { font-size: 13px; font-weight: 500; color: #333; }
.notif-msg { font-size: 12px; color: #666; margin-top: 2px; }
.notif-time { font-size: 11px; color: #bbb; margin-top: 4px; }



/* 📱 响应式：手机 */
@media (max-width: 768px) {
  .sidebar { position: fixed !important; left: -260px !important; top: 0 !important; height: 100vh !important; z-index: 9999 !important; transition: left 0.3s !important; }
  .sidebar.mobile-open { left: 0 !important; }
  .sidebar-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 9998; }
  .sidebar-overlay.show { display: block; }
  .main-area { margin-left: 0 !important; }
  .desktop-only { display: none !important; }
  .mobile-menu-btn { display: flex !important; }
}
.mobile-menu-btn { display: none; }

.ai-float-btn {
  position: fixed; bottom: 32px; right: 32px; z-index: 9999;
  width: 56px; height: 56px; border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #13c2c2);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; box-shadow: 0 4px 20px rgba(102,126,234,0.4);
  transition: all 0.3s; border: none;
}
@media (max-width: 768px) {
  .ai-float-btn { bottom: 20px; right: 20px; width: 48px; height: 48px; }
}
</style>












/* 📱 手机底部导航 */
.mobile-bottom-nav {
  display: none;
  position: fixed; bottom: 0; left: 0; right: 0;
  height: 60px; background: var(--bg-card);
  border-top: 1px solid var(--border-color);
  z-index: 9997;
  justify-content: space-around;
  align-items: center;
  padding-bottom: env(safe-area-inset-bottom);
}
.mb-item {
  display: flex; flex-direction: column;
  align-items: center; gap: 2px;
  text-decoration: none; color: var(--text-muted);
  font-size: 10px; padding: 4px 8px;
  border-radius: 8px; transition: all 0.15s;
}
.mb-item .router-link-active,
.mb-item.active { color: #667eea; }
.mb-item span:first-child { font-size: 20px; }
@media (max-width: 768px) {
  .mobile-bottom-nav { display: flex; }
  .content-area { padding-bottom: 70px; }
}
