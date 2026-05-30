<template>
  <div class="landing">
    <!-- Hero 区 -->
    <section class="hero">
      <div class="hero-bg"></div>
      <div class="hero-content fade-in">
        <div class="hero-badge">🌐 全球跨境电商平台</div>
        <h1 class="hero-title">TikTokMall</h1>
        <p class="hero-subtitle">一键管理 · 三端合一 · 全球卖货</p>

        <div class="hero-actions">
          <a href="/m" class="hero-btn hero-btn-primary">
            <span class="btn-icon">🛒</span>
            立即购物
          </a>
          <a href="/pc" class="hero-btn hero-btn-outline">
            <span class="btn-icon">💻</span>
            PC 商城
          </a>
          <a href="/seller/dashboard" class="hero-btn hero-btn-outline">
            <span class="btn-icon">🏪</span>
            商家管理
          </a>
        </div>

        <div class="hero-features">
          <div class="hero-feat">
            <div class="hero-feat-icon">📱</div>
            <span>手机 H5</span>
          </div>
          <div class="hero-feat">
            <div class="hero-feat-icon">💻</div>
            <span>电脑端</span>
          </div>
          <div class="hero-feat">
            <div class="hero-feat-icon">🏪</div>
            <span>商家后台</span>
          </div>
          <div class="hero-feat">
            <div class="hero-feat-icon">⬇️</div>
            <span>安装 PWA</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 统计区 -->
    <section class="stats section">
      <div class="container">
        <div class="stats-grid">
          <div class="stat-card card slide-up">
            <div class="stat-num">10,000+</div>
            <div class="stat-label">全球商品</div>
          </div>
          <div class="stat-card card slide-up" style="animation-delay: 0.1s">
            <div class="stat-num">50+</div>
            <div class="stat-label">国家地区</div>
          </div>
          <div class="stat-card card slide-up" style="animation-delay: 0.2s">
            <div class="stat-num">99.9%</div>
            <div class="stat-label">服务可用</div>
          </div>
          <div class="stat-card card slide-up" style="animation-delay: 0.3s">
            <div class="stat-num">24/7</div>
            <div class="stat-label">AI 运维</div>
          </div>
        </div>
      </div>
    </section>

    <!-- 入口卡片 -->
    <section class="portals section">
      <div class="container">
        <h2 class="section-title">选择入口</h2>
        <div class="portal-grid">
          <!-- 手机商城 -->
          <a href="/m" class="portal-card card card-hover fade-in">
            <div class="portal-icon-box">📱</div>
            <h3>手机商城</h3>
            <p>随时随地购物，支持 PWA 安装到桌面</p>
            <span class="portal-tag badge badge-primary">PWA Ready</span>
          </a>
          <!-- PC 商城 -->
          <a href="/pc" class="portal-card card card-hover fade-in" style="animation-delay: 0.1s">
            <div class="portal-icon-box">💻</div>
            <h3>电脑商城</h3>
            <p>大屏购物体验，分类浏览更便捷</p>
            <span class="portal-tag badge badge-success">自动适配</span>
          </a>
          <!-- 商家后台 -->
          <a href="/seller/dashboard" class="portal-card card card-hover fade-in" style="animation-delay: 0.2s">
            <div class="portal-icon-box">🏪</div>
            <h3>商家后台</h3>
            <p>商品/订单/财务一站式管理</p>
            <span class="portal-tag badge badge-warning">商家专用</span>
          </a>
          <!-- 商家手机端 -->
          <a href="/m/seller/shop" class="portal-card card card-hover fade-in" style="animation-delay: 0.3s">
            <div class="portal-icon-box">📲</div>
            <h3>商家手机端</h3>
            <p>手机管理店铺，随时随地接单</p>
            <span class="portal-tag badge badge-danger">移动优先</span>
          </a>
        </div>
      </div>
    </section>

    <!-- 底部 -->
    <footer class="landing-footer">
      <p>© 2026 TikTokMall · AI Agent 全权运维 · 全球跨境电商平台</p>
    </footer>
  </div>
</template>

<script setup>
// 落地页 — 纯展示，无逻辑
</script>

<style scoped>
.landing { min-height: 100vh; background: var(--bg-primary); }

/* Hero */
.hero {
  position: relative;
  min-height: 80vh;
  display: flex; align-items: center; justify-content: center;
  text-align: center;
  padding: 80px 20px;
  overflow: hidden;
}
.hero-bg {
  position: absolute; inset: 0;
  background:
    radial-gradient(ellipse 80% 60% at 50% 0%, rgba(99, 102, 241, 0.08), transparent),
    radial-gradient(ellipse 50% 50% at 80% 80%, rgba(245, 158, 11, 0.05), transparent);
}
.hero-content { position: relative; max-width: 640px; }
.hero-badge {
  display: inline-block;
  padding: 6px 20px; border-radius: 20px;
  background: rgba(99, 102, 241, 0.08);
  color: var(--color-primary); font-size: 13px; font-weight: 500;
  margin-bottom: 24px;
}
.hero-title {
  font-size: clamp(36px, 8vw, 64px);
  font-weight: 800; letter-spacing: -1px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 12px;
}
.hero-subtitle {
  font-size: 18px; color: var(--text-secondary);
  margin-bottom: 40px;
}
.hero-actions { display: flex; gap: 16px; justify-content: center; margin-bottom: 48px; flex-wrap: wrap; }
.hero-btn {
  display: flex; align-items: center; gap: 8px;
  padding: 16px 36px; border-radius: var(--border-radius);
  font-size: 16px; font-weight: 600;
  transition: all var(--transition-base);
}
.hero-btn-primary {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: white; box-shadow: 0 8px 24px rgba(99, 102, 241, 0.3);
}
.hero-btn-primary:hover { transform: translateY(-2px); box-shadow: 0 12px 32px rgba(99, 102, 241, 0.4); }
.hero-btn-outline {
  background: var(--bg-primary); border: 2px solid var(--border-color);
  color: var(--text-primary);
}
.hero-btn-outline:hover { border-color: var(--color-primary); color: var(--color-primary); }
.btn-icon { font-size: 20px; }
.hero-features { display: flex; gap: 32px; justify-content: center; flex-wrap: wrap; }
.hero-feat { display: flex; flex-direction: column; align-items: center; gap: 4px; color: var(--text-muted); font-size: 13px; }
.hero-feat-icon { font-size: 28px; }

/* 统计 */
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
.stat-card { text-align: center; padding: 32px 20px; }
.stat-num { font-size: 32px; font-weight: 700; color: var(--color-primary); }
.stat-label { font-size: 14px; color: var(--text-muted); margin-top: 4px; }

/* 入口卡片 */
.section-title { text-align: center; font-size: 28px; font-weight: 700; margin-bottom: 32px; }
.portal-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; }
.portal-card { display: block; position: relative; }
.portal-card h3 { font-size: 18px; margin: 12px 0 8px; color: var(--text-primary); }
.portal-card p { font-size: 14px; color: var(--text-muted); line-height: 1.5; }
.portal-icon-box { font-size: 40px; margin-bottom: 4px; }
.portal-tag { position: absolute; top: 20px; right: 20px; }

/* Footer */
.landing-footer {
  text-align: center; padding: 32px;
  color: var(--text-muted); font-size: 13px;
  border-top: 1px solid var(--border-color);
  margin-top: 60px;
}

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .hero { min-height: auto; padding: 60px 16px; }
  .hero-actions { flex-direction: column; align-items: center; }
  .hero-btn { width: 100%; max-width: 300px; justify-content: center; }
}
</style>
