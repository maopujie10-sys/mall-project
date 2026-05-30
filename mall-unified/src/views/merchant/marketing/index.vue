<template>
  <div class="merchant-marketing"><h2>营销中心</h2>
    <div class="card-grid">
      <div class="mkt-card card"><h3>🎫 优惠券</h3><p>创建和管理优惠券</p><el-button size="small">管理</el-button></div>
      <div class="mkt-card card"><h3>🏷️ 限时折扣</h3><p>设置限时促销活动</p><el-button size="small">管理</el-button></div>
      <div class="mkt-card card"><h3>🎁 满减活动</h3><p>满额立减活动设置</p><el-button size="small">管理</el-button></div>
      <div class="mkt-card card"><h3>📢 广告推广</h3><p>商品广告投放</p><el-button size="small">管理</el-button></div>
    </div>
  </div>
</template>

<style scoped>
.merchant-marketing { padding: 0; }
h2 { margin-bottom: 24px; }
.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; }
.mkt-card { padding: 24px; }
.mkt-card h3 { margin-bottom: 8px; }
.mkt-card p { font-size: 13px; color: var(--text-muted); margin-bottom: 16px; }
</style>
