<template>
  <div class="mobile-layout">
    <!-- 顶部固定导航 -->
    <header class="mobile-header glass">
      <div class="mobile-header-inner">
        <router-link to="/m" class="mobile-logo">TikTokMall</router-link>
        <div class="mobile-header-actions">
          <router-link to="/m/search" class="mobile-icon-btn">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="9" cy="9" r="6" stroke="currentColor" stroke-width="2"/><path d="M14 14l4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          </router-link>
          <router-link to="/m/cart" class="mobile-icon-btn">
            <svg width="20" height="20" viewBox="0 0 22 22" fill="none"><path d="M7 8V6a4 4 0 0 1 8 0v2M3 8h16l-1.5 11h-13L3 8z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </router-link>
        </div>
      </div>
    </header>

    <!-- 主内容 -->
    <main class="mobile-main">
      <slot />
    </main>

    <!-- 底部 TabBar -->
    <nav class="mobile-tabbar glass">
      <router-link to="/m" class="tabbar-item" exact-active-class="tabbar-active">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        <span>首页</span>
      </router-link>
      <router-link to="/m/categories" class="tabbar-item" active-class="tabbar-active">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><rect x="3" y="3" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="2"/><rect x="14" y="3" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="2"/><rect x="3" y="14" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="2"/><rect x="14" y="14" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="2"/></svg>
        <span>分类</span>
      </router-link>
      <router-link to="/m/cart" class="tabbar-item" active-class="tabbar-active">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><circle cx="9" cy="21" r="1" fill="currentColor"/><circle cx="20" cy="21" r="1" fill="currentColor"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        <span>购物车</span>
      </router-link>
      <router-link to="/m/me" class="tabbar-item" active-class="tabbar-active">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2"/></svg>
        <span>我的</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
// 移动端布局 — 直接展示 slot 内容
</script>

<style scoped>
.mobile-layout {
  max-width: 480px;
  margin: 0 auto;
  min-height: 100vh;
  background: var(--bg-secondary);
  box-shadow: var(--shadow-xl);
}
.mobile-header {
  position: sticky; top: 0; z-index: 100;
  height: 48px;
  border-bottom: 1px solid var(--border-color);
}
.mobile-header-inner {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 16px; height: 100%;
}
.mobile-logo { font-size: 18px; font-weight: 700; color: var(--text-primary); }
.mobile-header-actions { display: flex; gap: 8px; }
.mobile-icon-btn {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  color: var(--text-secondary); border-radius: var(--border-radius-sm);
}
.mobile-icon-btn:hover { background: var(--bg-tertiary); }
.mobile-main {
  padding-bottom: calc(var(--mobile-nav-height) + 16px);
  min-height: calc(100vh - 48px - var(--mobile-nav-height));
}
.mobile-tabbar {
  position: fixed; bottom: 0; z-index: 100;
  width: 100%; max-width: 480px;
  height: var(--mobile-nav-height);
  display: flex;
  border-top: 1px solid var(--border-color);
  padding-bottom: env(safe-area-inset-bottom, 0);
}
.tabbar-item {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 2px;
  color: var(--text-muted); font-size: 11px;
  transition: color var(--transition-fast);
}
.tabbar-active { color: var(--color-primary); }
</style>
