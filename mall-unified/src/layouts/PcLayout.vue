<template>
  <div class="pc-layout">
    <!-- 顶部导航栏 -->
    <header class="pc-header glass">
      <div class="container header-inner">
        <!-- Logo -->
        <router-link to="/" class="logo">
          <div class="logo-icon">M</div>
          <span class="logo-text">TikTokMall</span>
        </router-link>

        <!-- 搜索栏 -->
        <div class="search-bar">
          <input
            v-model="searchKeyword"
            type="text"
            :placeholder="$t('common.search')"
            class="search-input"
            @keyup.enter="goSearch"
          />
          <button class="search-btn" @click="goSearch">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="9" cy="9" r="6" stroke="currentColor" stroke-width="2"/><path d="M14 14l4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          </button>
        </div>

        <!-- 右侧操作 -->
        <nav class="header-actions">
          <router-link to="/m/seller/shop" class="nav-link">卖家中心</router-link>
          <router-link to="/cart" class="nav-link cart-link">
            <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M7 8V6a4 4 0 0 1 8 0v2M3 8h16l-1.5 11h-13L3 8z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <span v-if="cartCount" class="cart-badge">{{ cartCount }}</span>
          </router-link>

          <template v-if="userStore.isLoggedIn">
            <div class="user-menu">
              <router-link to="/user" class="nav-link">{{ userStore.userInfo?.username || '我的' }}</router-link>
              <button @click="userStore.logout" class="nav-link logout-btn">退出</button>
            </div>
          </template>
          <template v-else>
            <router-link to="/login" class="btn btn-outline btn-sm">登录</router-link>
            <router-link to="/register" class="btn btn-primary btn-sm">注册</router-link>
          </template>
        </nav>
      </div>
    </header>

    <!-- 分类导航 -->
    <nav class="pc-subnav">
      <div class="container">
        <div class="subnav-list">
          <router-link to="/" class="subnav-item">首页</router-link>
          <router-link to="/categories" class="subnav-item">全部分类</router-link>
          <router-link to="/discount" class="subnav-item subnav-hot">🔥 折扣</router-link>
          <router-link to="/stores" class="subnav-item">品牌店铺</router-link>
        </div>
      </div>
    </nav>

    <!-- 主内容 -->
    <main class="pc-main">
      <div class="container">
        <slot />
      </div>
    </main>

    <!-- 底部 -->
    <footer class="pc-footer">
      <div class="container footer-grid">
        <div class="footer-col">
          <h4>TikTokMall</h4>
          <p>全球跨境电商平台</p>
        </div>
        <div class="footer-col">
          <h4>购物指南</h4>
          <a href="#">购物流程</a>
          <a href="#">支付方式</a>
          <a href="#">配送说明</a>
        </div>
        <div class="footer-col">
          <h4>商家服务</h4>
          <router-link to="/merchant-settle">商家入驻</router-link>
          <a href="#">运营指南</a>
          <a href="#">商家后台</a>
        </div>
        <div class="footer-col">
          <h4>帮助中心</h4>
          <a href="#">常见问题</a>
          <a href="#">联系客服</a>
          <a href="#">用户协议</a>
        </div>
      </div>
      <div class="footer-bottom">
        <p>© 2026 TikTokMall. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const searchKeyword = ref('')
const cartCount = ref(0)

function goSearch() {
  if (searchKeyword.value.trim()) {
    router.push({ path: '/search', query: { q: searchKeyword.value } })
  }
}
</script>

<style scoped>
.pc-header {
  position: sticky;
  top: 0;
  z-index: 100;
  height: var(--header-height);
  border-bottom: 1px solid rgba(0,0,0,0.05);
}
.header-inner { display: flex; align-items: center; gap: 24px; height: 100%; }
.logo { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
.logo-icon {
  width: 36px; height: 36px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  color: white; font-weight: 700; font-size: 18px;
}
.logo-text { font-size: 20px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.5px; }
.search-bar {
  flex: 1; max-width: 500px;
  display: flex; align-items: center;
  background: var(--bg-tertiary);
  border-radius: var(--border-radius);
  border: 2px solid transparent;
  transition: all var(--transition-fast);
}
.search-bar:focus-within {
  border-color: var(--color-primary);
  background: var(--bg-primary);
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
}
.search-input {
  flex: 1; padding: 10px 16px;
  background: transparent; border: none; outline: none;
  font-size: 14px; color: var(--text-primary);
}
.search-btn { padding: 10px 14px; background: transparent; color: var(--text-secondary); }
.header-actions { display: flex; align-items: center; gap: 12px; flex-shrink: 0; }
.nav-link { color: var(--text-secondary); font-size: 14px; padding: 4px 8px; transition: color var(--transition-fast); }
.nav-link:hover { color: var(--color-primary); }
.cart-link { position: relative; }
.cart-badge {
  position: absolute; top: -4px; right: -8px;
  background: var(--color-danger); color: white;
  font-size: 11px; padding: 1px 5px; border-radius: 10px;
}
.user-menu { display: flex; align-items: center; gap: 8px; }
.logout-btn {
  background: none; font-size: 13px; color: var(--text-muted);
  padding: 4px 8px; border-radius: 6px;
}
.logout-btn:hover { color: var(--color-danger); background: rgba(239,68,68,0.08); }

/* 子导航 */
.pc-subnav {
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
}
.subnav-list { display: flex; gap: 4px; padding: 8px 0; }
.subnav-item {
  padding: 6px 16px; border-radius: var(--border-radius-sm);
  font-size: 14px; color: var(--text-secondary);
  transition: all var(--transition-fast);
}
.subnav-item:hover, .subnav-item.router-link-active {
  color: var(--color-primary); background: rgba(99, 102, 241, 0.06);
}
.subnav-hot { color: var(--color-accent); }

/* 主内容 */
.pc-main { min-height: calc(100vh - var(--header-height) - 200px); padding: 24px 0; }

/* 底部 */
.pc-footer {
  background: var(--bg-dark);
  color: rgba(255,255,255,0.7);
  padding: 48px 0 0;
  margin-top: 60px;
}
.footer-grid { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 40px; }
.footer-col h4 { color: white; font-size: 16px; margin-bottom: 16px; }
.footer-col p, .footer-col a {
  display: block; color: rgba(255,255,255,0.5); font-size: 14px;
  margin-bottom: 8px; transition: color var(--transition-fast);
}
.footer-col a:hover { color: var(--color-primary-light); }
.footer-bottom {
  border-top: 1px solid rgba(255,255,255,0.08);
  padding: 20px 0; margin-top: 40px;
  text-align: center; font-size: 13px; color: rgba(255,255,255,0.3);
}

@media (max-width: 768px) { .pc-layout { display: none; /* 手机用 MobileLayout */ } }
</style>
