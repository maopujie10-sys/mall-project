<template>
  <div class="settings-page">
    <h2 class="page-title">{{ $t('common.settings') }}</h2>

    <div class="card menu-card">
      <div class="menu-item" @click="$router.push('/m/me')">
        <span>{{ $t('user.profile') }}</span>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M9 6l6 6-6 6" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/></svg>
      </div>
      <div class="menu-item" @click="$router.push('/m/me')">
        <span>{{ $t('user.security') }}</span>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M9 6l6 6-6 6" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/></svg>
      </div>
      <div class="menu-item" @click="$router.push('/m/address')">
        <span>{{ $t('user.address') }}</span>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M9 6l6 6-6 6" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/></svg>
      </div>
      <div class="menu-item" @click="toggleLang">
        <span>{{ $t('common.language') }}</span>
        <span class="menu-val">简体中文</span>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M9 6l6 6-6 6" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/></svg>
      </div>
    </div>

    <!-- 退出登录 -->
    <div class="card menu-card" v-if="userStore.isLoggedIn">
      <div class="menu-item danger" @click="handleLogout">
        <span>{{ $t('common.logout') }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const { locale } = useI18n()
const userStore = useUserStore()

function toggleLang() {
  locale.value = locale.value === 'zh' ? 'en' : 'zh'
  localStorage.setItem('lang', locale.value === 'zh' ? 'cn' : 'en')
}

function handleLogout() {
  userStore.logout()
  router.push('/m')
}
</script>

<style scoped>
.settings-page { min-height: 100vh; background: var(--bg-secondary); padding: 16px 14px; }
.page-title { font-size: 18px; font-weight: 700; color: var(--text-primary); margin-bottom: 16px; }
.card { background: var(--bg-primary); border-radius: var(--border-radius); box-shadow: var(--shadow-sm); margin-bottom: 12px; }
.menu-item { display: flex; align-items: center; gap: 10px; padding: 16px; border-bottom: 1px solid var(--border-color); font-size: 14px; color: var(--text-primary); cursor: pointer; transition: background var(--transition-fast); }
.menu-item:last-child { border-bottom: none; }
.menu-item:hover { background: var(--bg-secondary); }
.menu-item.danger { color: var(--color-danger); justify-content: center; }
.menu-val { margin-left: auto; font-size: 13px; color: var(--text-muted); }
</style>
