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
    <aside class="sidebar">
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
          <div class="nav-section-label" v-show="!sidebarCollapsed">核心</div>
          <router-link to="/friday" class="nav-item" :class="{ active: isActive('/friday') }">
            <span class="nav-icon">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 2a10 10 0 0 1 7 10 10 10 0 0 1-7 10"/><path d="M12 2a10 10 0 0 0-7 10 10 10 0 0 0 7 10"/><circle cx="12" cy="12" r="4"/></svg>
            </span>
            <span class="nav-label" v-show="!sidebarCollapsed">Friday 神经网络</span>
          </router-link>
          <router-link to="/dashboard" class="nav-item" :class="{ active: isActive('/dashboard') }">
            <span class="nav-icon">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
            </span>
            <span class="nav-label" v-show="!sidebarCollapsed">数据总览</span>
          </router-link>
          <router-link to="/chat" class="nav-item" :class="{ active: isActive('/chat') }">
            <span class="nav-icon">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            </span>
            <span class="nav-label" v-show="!sidebarCollapsed">AI 对话</span>
          </router-link>
        </div>

        <!-- AI 大脑 -->
        <div class="nav-section">
          <div class="nav-section-label" v-show="!sidebarCollapsed">AI 大脑</div>
          <router-link to="/ai-brain" class="nav-item" :class="{ active: isActive('/ai-brain') }">
            <span class="nav-icon"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg></span>
            <span class="nav-label" v-show="!sidebarCollapsed">AI 大脑</span>
          </router-link>
                    <router-link to="/agents" class="nav-item" :class="{ active: isActive('/agents') }">
            <span class="nav-icon"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg></span>
            <span class="nav-label" v-show="!sidebarCollapsed">Agent面板</span>
          </router-link>
          <router-link to="/trends" class="nav-item" :class="{ active: isActive('/trends') }">
            <span class="nav-icon"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg></span>
            <span class="nav-label" v-show="!sidebarCollapsed">热点监控</span>
          </router-link>
          <router-link to="/memory" class="nav-item" :class="{ active: isActive('/memory') }">
            <span class="nav-icon"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg></span>
            <span class="nav-label" v-show="!sidebarCollapsed">记忆中心</span>
          </router-link>
          <router-link to="/models" class="nav-item" :class="{ active: isActive('/models') }">
            <span class="nav-icon"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg></span>
            <span class="nav-label" v-show="!sidebarCollapsed">模型中心</span>
          </router-link>
          <router-link to="/evolution" class="nav-item" :class="{ active: isActive('/evolution') }">
            <span class="nav-icon"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg></span>
            <span class="nav-label" v-show="!sidebarCollapsed">进化报告</span>
          </router-link>
          <router-link to="/scraper" class="nav-item" :class="{ active: isActive('/scraper') }">
            <span class="nav-icon"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg></span>
            <span class="nav-label" v-show="!sidebarCollapsed">采集中心</span>
          </router-link>
          <router-link to="/virtual" class="nav-item" :class="{ active: isActive('/virtual') }">
            <span class="nav-icon"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg></span>
            <span class="nav-label" v-show="!sidebarCollapsed">虚拟数据</span>
          </router-link>
        </div>

        <!-- 基础设施 -->
        <div class="nav-section">
        <!-- 运营 -->
        <div class="nav-section">
          <div class="nav-section-label" v-show="!sidebarCollapsed">运营</div>
          <router-link to="/mall" class="nav-item" :class="{ active: isActive('/mall') }">
            <span class="nav-icon">🛒</span>
            <span class="nav-label" v-show="!sidebarCollapsed">商城管理</span>
          </router-link>
          <router-link to="/site" class="nav-item" :class="{ active: isActive('/site') }">
            <span class="nav-icon">🌐</span>
            <span class="nav-label" v-show="!sidebarCollapsed">网站检测</span>
          </router-link>
          <router-link to="/customer" class="nav-item" :class="{ active: isActive('/customer') }">
            <span class="nav-icon">💬</span>
            <span class="nav-label" v-show="!sidebarCollapsed">客服</span>
          </router-link>
        </div>

        <!-- 系统 -->
        <div class="nav-section">
          <div class="nav-section-label" v-show="!sidebarCollapsed">系统</div>
          <router-link to="/database" class="nav-item" :class="{ active: isActive('/database') }">
            <span class="nav-icon">🗄️</span>
            <span class="nav-label" v-show="!sidebarCollapsed">数据库</span>
          </router-link>
          <router-link to="/approval" class="nav-item" :class="{ active: isActive('/approval') }">
            <span class="nav-icon">✅</span>
            <span class="nav-label" v-show="!sidebarCollapsed">审批中心</span>
          </router-link>
          <router-link to="/security" class="nav-item" :class="{ active: isActive('/security') }">
            <span class="nav-icon">🔒</span>
            <span class="nav-label" v-show="!sidebarCollapsed">安全中心</span>
          </router-link>
          <router-link to="/rollback" class="nav-item" :class="{ active: isActive('/rollback') }">
            <span class="nav-icon">⏪</span>
            <span class="nav-label" v-show="!sidebarCollapsed">备份回滚</span>
          </router-link>
          <router-link to="/alert" class="nav-item" :class="{ active: isActive('/alert') }">
            <span class="nav-icon">🔔</span>
            <span class="nav-label" v-show="!sidebarCollapsed">告警中心</span>
          </router-link>
          <router-link to="/tasks" class="nav-item" :class="{ active: isActive('/tasks') }">
            <span class="nav-icon">📋</span>
            <span class="nav-label" v-show="!sidebarCollapsed">自动任务</span>
          </router-link>
          <router-link to="/self-service" class="nav-item" :class="{ active: isActive('/self-service') }">
            <span class="nav-icon">🔧</span>
            <span class="nav-label" v-show="!sidebarCollapsed">自助服务</span>
          </router-link>
          <router-link to="/plugins" class="nav-item" :class="{ active: isActive('/plugins') }">
            <span class="nav-icon">🧩</span>
            <span class="nav-label" v-show="!sidebarCollapsed">插件系统</span>
          </router-link>
          <router-link to="/rotation" class="nav-item" :class="{ active: isActive('/rotation') }">
            <span class="nav-icon">🔄</span>
            <span class="nav-label" v-show="!sidebarCollapsed">轮值</span>
          </router-link>
          <router-link to="/video" class="nav-item" :class="{ active: isActive('/video') }">
            <span class="nav-icon">🎬</span>
            <span class="nav-label" v-show="!sidebarCollapsed">视频分析</span>
          </router-link>
          <router-link to="/ocr" class="nav-item" :class="{ active: isActive('/ocr') }">
            <span class="nav-icon">📝</span>
            <span class="nav-label" v-show="!sidebarCollapsed">OCR识别</span>
          </router-link>
        </div>
          <div class="nav-section-label" v-show="!sidebarCollapsed">基础设施</div>
          <router-link to="/server" class="nav-item" :class="{ active: isActive('/server') }">
            <span class="nav-icon"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg></span>
            <span class="nav-label" v-show="!sidebarCollapsed">服务器</span>
          </router-link>
          <router-link to="/docker" class="nav-item" :class="{ active: isActive('/docker') }">
            <span class="nav-icon"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="3" width="15" height="12" rx="2"/><path d="M5 7h2M9 7h2M5 11h2M9 11h2"/><rect x="8" y="9" width="8" height="10" rx="2"/></svg></span>
            <span class="nav-label" v-show="!sidebarCollapsed">Docker</span>
          </router-link>
          <router-link to="/nginx" class="nav-item" :class="{ active: isActive('/nginx') }">
            <span class="nav-icon"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10"/><path d="M12 2a15.3 15.3 0 0 0-4 10"/></svg></span>
            <span class="nav-label" v-show="!sidebarCollapsed">Nginx</span>
          </router-link>
        </div>
      </nav>

      <div class="sidebar-footer">
        <button class="collapse-btn" @click="sidebarCollapsed = !sidebarCollapsed">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <polyline v-if="!sidebarCollapsed" points="15 18 9 12 15 6"/>
            <polyline v-else points="9 18 15 12 9 6"/>
          </svg>
        </button>
      </div>
    </aside>

    <div class="main-area">
      <header class="top-bar">
        <div class="top-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/friday' }">Friday AI OS</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentTitle">{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="top-right">
          <div class="status-indicators" v-if="currentRoute !== '/friday'">
            <span class="status-dot online"></span>
            <span class="status-label">AI 在线</span>
          </div>
          <div class="mode-tag" :class="currentMode">{{ modeLabel }}</div>
          <button class="theme-btn" @click="theme.toggle">
            <svg v-if="!theme.isDark.value" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/></svg>
            <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
          </button>
          <el-dropdown trigger="click">
            <span class="user-chip">
              <el-avatar :size="28" style="background: linear-gradient(135deg, #667eea, #13c2c2);">F</el-avatar>
            </span>
            <template #dropdown>
              <el-dropdown-menu>                <el-dropdown-item @click="tokenDialogVisible = true">🔑 设置 Token</el-dropdown-item>
                <el-dropdown-item disabled>Friday AI OS v3.0</el-dropdown-item>
                <el-dropdown-item divided>
                  <router-link to="/emergency" style="color: #ff4d4f; text-decoration: none;">🚨 急救面板</router-link>
                </el-dropdown-item>
              </el-dropdown-menu>
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

import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useSystemStore } from '@/stores/system'
import { useThemeStore } from '@/stores/theme'
const isElectron = !!window.electronAPI
const minimizeWin = () => window.electronAPI?.minimize()
const maximizeWin = () => window.electronAPI?.maximize()
const closeWin = () => window.electronAPI?.close()
import { ElMessage } from "element-plus"
import LiveTaskPanel from '@/components/LiveTaskPanel.vue'
import { storeToRefs } from 'pinia'

const route = useRoute()
const system = useSystemStore()
const theme = useThemeStore()
const { currentMode, modeLabel } = storeToRefs(system)

const sidebarCollapsed = ref(false)

const currentTitle = computed(() => route.meta?.title || '')
const currentRoute = computed(() => route.path)

function isActive(path) {
  return route.path === path || route.path.startsWith(path + '/')
}

onMounted(() => {
  theme.initTheme()
  system.fetchMode()
})
</script>

<style scoped>
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
.nav-section-label {
  font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;
  color: rgba(102,126,234,0.4); padding: 12px 10px 6px; white-space: nowrap;
}

.nav-item {
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

</style>

