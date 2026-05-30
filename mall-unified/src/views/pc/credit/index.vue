<template>
  <div class="pc-credit fade-in">
    <h2>信用中心</h2>
    <div class="stats-row">
      <div class="stat-card card"><span class="num">¥{{ credit?.balance || '0.00' }}</span><span class="lbl">可用额度</span></div>
      <div class="stat-card card"><span class="num">¥{{ credit?.used || '0.00' }}</span><span class="lbl">已用额度</span></div>
      <div class="stat-card card"><span class="num">{{ credit?.level || 1 }}</span><span class="lbl">信用等级</span></div>
    </div>
    <div class="card"><h3>贷款记录</h3><el-table :data="loans" empty-text="暂无记录"><el-table-column prop="amount" label="金额" /><el-table-column prop="status" label="状态" /><el-table-column prop="createTime" label="申请时间" /></el-table></div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { post } from '@/api/index'
const credit = reactive({})
const loans = ref([])
onMounted(async () => {
  try { const r = await post('/api/credit!info.action'); Object.assign(credit, r.data || r) } catch {}
  try { const r = await post('/api/loan!list.action'); loans.value = (r.data || r).list || [] } catch {}
})
</script>

<style scoped>
.pc-credit { padding: 24px 0; }
.stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-card { text-align: center; padding: 24px; }
.num { display: block; font-size: 24px; font-weight: 700; color: var(--color-primary); }
.lbl { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
</style>
