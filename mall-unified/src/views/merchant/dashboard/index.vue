<template>
  <div class="merchant-dashboard fade-in">
    <div class="stats-grid">
      <div class="stat-card card slide-up">
        <div class="stat-icon">📦</div>
        <div class="stat-val">{{ stats.productsCount || 0 }}</div>
        <div class="stat-label">商品总数</div>
      </div>
      <div class="stat-card card slide-up" style="animation-delay:0.1s">
        <div class="stat-icon">📋</div>
        <div class="stat-val">{{ stats.ordersCount || 0 }}</div>
        <div class="stat-label">今日订单</div>
      </div>
      <div class="stat-card card slide-up" style="animation-delay:0.2s">
        <div class="stat-icon">💰</div>
        <div class="stat-val">¥{{ (stats.revenue || 0).toFixed(2) }}</div>
        <div class="stat-label">今日营收</div>
      </div>
      <div class="stat-card card slide-up" style="animation-delay:0.3s">
        <div class="stat-icon">👁️</div>
        <div class="stat-val">{{ stats.views || 0 }}</div>
        <div class="stat-label">店铺访客</div>
      </div>
    </div>

    <div class="dashboard-grid">
      <div class="card dashboard-chart">
        <h3>销售趋势</h3>
        <div style="height:200px;display:flex;align-items:center;justify-content:center;color:var(--text-muted)">图表区域</div>
      </div>
      <div class="card dashboard-recent">
        <h3>最近订单</h3>
        <div v-if="!recentOrders.length" class="empty-state"><p>暂无订单</p></div>
        <div v-for="o in recentOrders" :key="o.id" class="recent-item">
          <span>{{ o.orderNo || o.id }}</span>
          <span>¥{{ o.amount || o.total }}</span>
          <span class="badge" :class="o.status === 'pending' ? 'badge-warning' : 'badge-success'">{{ o.status || '-' }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { get, post, put, del } from '@/api/index'

const stats = reactive({ productsCount: 0, ordersCount: 0, revenue: 0, views: 0 })
const recentOrders = ref([])

onMounted(async () => {
  try {
    const [dashRes, orderRes] = await Promise.allSettled([getDashboardData(), getMerchantOrders({ page: 1, size: 5 })])
    if (dashRes.status === 'fulfilled' && dashRes.value) {
      const d = dashRes.value.data || dashRes.value
      Object.assign(stats, d)
    }
    if (orderRes.status === 'fulfilled' && orderRes.value) {
      recentOrders.value = ((orderRes.value.data || orderRes.value).list || []).slice(0, 5)
    }
  } catch (e) { /* mock fallback */ }
})
</script>

<style scoped>
.merchant-dashboard { padding: 24px; }
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-card { display: flex; flex-direction: column; align-items: center; padding: 24px; text-align: center; }
.stat-icon { font-size: 28px; margin-bottom: 8px; }
.stat-val { font-size: 24px; font-weight: 700; color: var(--text-primary); }
.stat-label { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
.dashboard-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 16px; }
.dashboard-chart, .dashboard-recent { padding: 24px; }
.dashboard-chart h3, .dashboard-recent h3 { margin-bottom: 16px; }
.recent-item { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid var(--border-color); font-size: 13px; }
.recent-item:last-child { border-bottom: none; }
@media (max-width: 768px) { .stats-grid { grid-template-columns: repeat(2, 1fr); } .dashboard-grid { grid-template-columns: 1fr; } }
</style>
