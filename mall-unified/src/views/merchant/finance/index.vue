<template>
  <div class="merchant-finance">
    <h2>财务报表</h2>
    <div class="stats-row">
      <div class="stat-card card"><span class="num">¥{{ head?.totalRevenue || '0.00' }}</span><span class="lbl">总营收</span></div>
      <div class="stat-card card"><span class="num">¥{{ head?.todayRevenue || '0.00' }}</span><span class="lbl">今日营收</span></div>
      <div class="stat-card card"><span class="num">{{ head?.totalOrders || 0 }}</span><span class="lbl">总订单</span></div>
      <div class="stat-card card"><span class="num">¥{{ head?.pendingSettlement || '0.00' }}</span><span class="lbl">待结算</span></div>
    </div>
    <div class="card"><h3>营收明细</h3>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="orderCount" label="订单数" width="100" />
        <el-table-column label="营收" width="120"><template #default="{row}">¥{{ row.revenue || 0 }}</template></el-table-column>
        <el-table-column label="成本" width="120"><template #default="{row}">¥{{ row.cost || 0 }}</template></el-table-column>
        <el-table-column label="利润" width="120"><template #default="{row}">¥{{ (row.revenue || 0) - (row.cost || 0) }}</template></el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { get, post, put, del } from '@/api/index'

const head = reactive({}); const list = ref([]); const loading = ref(false)

onMounted(async () => {
  try { const r = await getFinanceHead(); Object.assign(head, r.data || r) } catch {}
  loading.value = true
  try { const r = await getFinanceReport({ page: 1, size: 30 }); list.value = (r.data || r).list || (r.data || r).rows || [] } catch {} finally { loading.value = false }
})
</script>

<style scoped>
.merchant-finance { padding: 0; }
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-card { text-align: center; padding: 24px; }
.num { display: block; font-size: 24px; font-weight: 700; color: var(--color-primary); }
.lbl { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
</style>
