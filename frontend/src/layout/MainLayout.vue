<template>
  <div class="platform-layout">
    <!-- 顶部导航栏 -->
    <header class="platform-header">
      <div class="header-left">
        <div class="logo">
          <svg class="logo-icon" viewBox="0 0 32 32" width="28" height="28">
            <rect width="32" height="32" rx="6" fill="#1890ff"/>
            <path d="M8 16 L14 10 L20 16 L26 10" stroke="white" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="16" cy="22" r="3" fill="white"/>
          </svg>
          <span class="logo-text">AI Agent 总控</span>
        </div>
        <nav class="top-nav">
          <router-link to="/dashboard" class="nav-item">总控台</router-link>
          <router-link to="/chat" class="nav-item">AI 对话</router-link>
          <router-link to="/server" class="nav-item">服务器</router-link>
          <router-link to="/mall" class="nav-item">商城</router-link>
          <router-link to="/attrs" class="nav-item">属性</router-link>
          <router-link to="/customer" class="nav-item">客服</router-link>
          <router-link to="/rotation" class="nav-item">轮值</router-link>
          <router-link to="/approval" class="nav-item">
            审批 <el-badge :value="pendingCount" :hidden="pendingCount === 0" class="nav-badge"/>
          </router-link>
          <router-link to="/security" class="nav-item">安全</router-link>
        </nav>
      </div>
      <div class="header-right">
        <!-- 主题切换按钮 -->
        <button class="theme-toggle-btn" @click="theme.toggle" :title="theme.isDark.value ? '切换到亮色模式' : '切换到暗色模式'">
          <!-- 太阳图标（亮色模式） -->
          <svg v-if="!theme.isDark.value" class="theme-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="5"/>
            <line x1="12" y1="1" x2="12" y2="3"/>
            <line x1="12" y1="21" x2="12" y2="23"/>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
            <line x1="1" y1="12" x2="3" y2="12"/>
            <line x1="21" y1="12" x2="23" y2="12"/>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
          </svg>
          <!-- 月亮图标（暗色模式） -->
          <svg v-else class="theme-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          </svg>
        </button>
        <div class="mode-indicator" :class="currentMode">
          <span class="mode-dot"></span>
          <span>{{ modeLabel }}</span>
        </div>
        <el-dropdown trigger="click">
          <span class="user-area">
            <el-avatar :size="32" style="background: #1890ff;">A</el-avatar>
            <span class="user-name">Admin</span>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item disabled>运行模式: {{ modeLabel }}</el-dropdown-item>
              <el-dropdown-item divided>
                <router-link to="/emergency" style="color: #ff4d4f; text-decoration: none;">⚡ 急救面板</router-link>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="platform-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useSystemStore } from '@/stores/system'
import { useThemeStore } from '@/stores/theme.js'
import { storeToRefs } from 'pinia'

const system = useSystemStore()
const { currentMode, pendingCount, modeLabel } = storeToRefs(system)

const theme = useThemeStore()

onMounted(() => {
  theme.initTheme()
  system.fetchMode()
})
</script>

<style scoped>
.platform-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-page);
}

/* ===== 顶部导航栏 ===== */
.platform-header {
  height: var(--header-height);
  background: var(--header-bg);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 100;
  transition: var(--theme-transition);
}
.header-left { display: flex; align-items: center; gap: 32px; }

.logo { display: flex; align-items: center; gap: 10px; }
.logo-text { font-size: 16px; font-weight: 600; color: var(--text-primary); letter-spacing: -0.3px; }

.top-nav { display: flex; gap: 4px; }
.top-nav .nav-item {
  padding: 6px 14px;
  font-size: 13px;
  color: var(--text-secondary);
  border-radius: 6px;
  text-decoration: none;
  transition: all 0.15s;
  position: relative;
}
.top-nav .nav-item:hover { color: var(--color-primary); background: var(--color-primary-bg); }
.top-nav .nav-item.router-link-active { color: var(--color-primary); font-weight: 500; background: var(--color-primary-bg); }
.nav-badge { margin-left: 2px; }

.header-right { display: flex; align-items: center; gap: 16px; }

/* 主题切换按钮 */
.theme-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--theme-transition);
  padding: 0;
  outline: none;
}
.theme-toggle-btn:hover {
  background: var(--bg-hover);
  color: var(--color-primary);
  border-color: var(--color-primary-light);
}
.theme-icon {
  transition: transform 0.3s ease;
}

/* 模式指示器 */
.mode-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  background: var(--color-success-bg);
  color: var(--color-success);
  border: 1px solid #b7eb8f;
}
.mode-indicator.human-control { background: var(--color-danger-bg); color: var(--color-danger); border-color: #ffccc7; }
.mode-indicator.readonly { background: var(--color-warning-bg); color: #d48806; border-color: #ffe58f; }
.mode-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--color-success); }
.human-control .mode-dot { background: var(--color-danger); }
.readonly .mode-dot { background: var(--color-warning); }

.user-area {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.15s;
}
.user-area:hover { background: var(--bg-hover); }
.user-name { font-size: 13px; color: var(--text-secondary); }

/* ===== 主内容 ===== */
.platform-main {
  flex: 1;
  padding: 0;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.15s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
