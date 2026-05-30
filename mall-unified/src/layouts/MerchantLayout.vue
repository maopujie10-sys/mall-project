<template>
  <div class="merchant-layout">
    <!-- 侧边栏 -->
    <aside class="merchant-sidebar">
      <div class="sidebar-logo">
        <div class="logo-icon">S</div>
        <span>商家中心</span>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/seller/dashboard" class="sidebar-item" active-class="sidebar-active">
          <span class="sidebar-icon">📊</span> 仪表盘
        </router-link>
        <router-link to="/seller/shop" class="sidebar-item" active-class="sidebar-active">
          <span class="sidebar-icon">🏪</span> 店铺管理
        </router-link>
        <router-link to="/seller/products" class="sidebar-item" active-class="sidebar-active">
          <span class="sidebar-icon">📦</span> 商品管理
        </router-link>
        <router-link to="/seller/orders" class="sidebar-item" active-class="sidebar-active">
          <span class="sidebar-icon">📋</span> 订单管理
        </router-link>
        <router-link to="/seller/finance" class="sidebar-item" active-class="sidebar-active">
          <span class="sidebar-icon">💰</span> 财务报表
        </router-link>
        <router-link to="/seller/wallet" class="sidebar-item" active-class="sidebar-active">
          <span class="sidebar-icon">💳</span> 钱包
        </router-link>
        <router-link to="/seller/chat" class="sidebar-item" active-class="sidebar-active">
          <span class="sidebar-icon">💬</span> 客服消息
        </router-link>
        <router-link to="/seller/marketing" class="sidebar-item" active-class="sidebar-active">
          <span class="sidebar-icon">📢</span> 营销中心
        </router-link>
        <router-link to="/seller/settings" class="sidebar-item" active-class="sidebar-active">
          <span class="sidebar-icon">⚙️</span> 设置
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <router-link to="/" class="back-to-mall">← 返回商城</router-link>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="merchant-main">
      <header class="merchant-topbar glass">
        <h2 class="page-title">商家后台</h2>
        <div class="topbar-actions">
          <router-link to="/m/seller/shop" class="btn btn-outline btn-sm">手机端</router-link>
          <button class="btn btn-outline btn-sm" @click="logout">退出</button>
        </div>
      </header>
      <div class="merchant-content">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup>
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
const userStore = useUserStore()
const router = useRouter()
function logout() {
  userStore.logout()
  router.push('/seller/login')
}
</script>

<style scoped>
.merchant-layout { display: flex; min-height: 100vh; background: var(--bg-secondary); }

.merchant-sidebar {
  width: 240px; flex-shrink: 0;
  background: var(--bg-dark); color: white;
  display: flex; flex-direction: column;
}
.sidebar-logo {
  display: flex; align-items: center; gap: 10px;
  padding: 20px; font-size: 18px; font-weight: 700;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.logo-icon {
  width: 32px; height: 32px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
  border-radius: 8px; display: flex; align-items: center; justify-content: center;
}
.sidebar-nav { flex: 1; padding: 12px; }
.sidebar-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px; border-radius: var(--border-radius-sm);
  color: rgba(255,255,255,0.6); font-size: 14px;
  transition: all var(--transition-fast); margin-bottom: 2px;
}
.sidebar-item:hover, .sidebar-active {
  color: white; background: rgba(99, 102, 241, 0.2);
}
.sidebar-icon { font-size: 18px; }
.sidebar-footer { padding: 16px; border-top: 1px solid rgba(255,255,255,0.08); }
.back-to-mall { color: rgba(255,255,255,0.4); font-size: 13px; }

.merchant-main { flex: 1; display: flex; flex-direction: column; }
.merchant-topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px; height: 56px;
  border-bottom: 1px solid var(--border-color);
  position: sticky; top: 0; z-index: 50;
}
.page-title { font-size: 18px; font-weight: 600; }
.topbar-actions { display: flex; gap: 8px; }
.merchant-content { flex: 1; padding: 24px; }

@media (max-width: 768px) {
  .merchant-sidebar { display: none; }
  .merchant-layout { flex-direction: column; }
}
</style>
