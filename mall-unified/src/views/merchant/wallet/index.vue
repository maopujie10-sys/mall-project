<template>
  <div class="merchant-wallet">
    <h2>钱包</h2>
    <div class="wallet-cards">
      <div class="wc card"><span class="wc-label">可用余额</span><span class="wc-val">¥{{ wallet?.balance || '0.00' }}</span></div>
      <div class="wc card"><span class="wc-label">冻结金额</span><span class="wc-val">¥{{ wallet?.frozen || '0.00' }}</span></div>
      <div class="wc card"><span class="wc-label">累计收入</span><span class="wc-val">¥{{ wallet?.totalIncome || '0.00' }}</span></div>
    </div>
    <div class="actions"><button class="btn btn-primary" @click="showRecharge = true">充值</button><button class="btn btn-outline" @click="showWithdraw = true">提现</button></div>

    <div class="card"><h3>资金流水</h3>
      <el-table :data="logs" stripe><el-table-column prop="type" label="类型" width="100" /><el-table-column label="金额" width="120"><template #default="{row}">¥{{ row.amount || 0 }}</template></el-table-column><el-table-column prop="desc" label="说明" /><el-table-column prop="createTime" label="时间" width="160" /></el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { get, post, put, del } from '@/api/index'

const wallet = reactive({}); const logs = ref([]); const showRecharge = ref(false); const showWithdraw = ref(false)
onMounted(async () => {
  try { const r = await getMerchantWallet(); Object.assign(wallet, r.data || r) } catch {}
  try { const r = await getMerchantWallet(); logs.value = (r.data || r).logs || [] } catch {}
})
</script>

<style scoped>
.merchant-wallet { padding: 0; }
h2 { margin-bottom: 24px; }
.wallet-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
.wc { text-align: center; padding: 24px; }
.wc-label { display: block; font-size: 12px; color: var(--text-muted); margin-bottom: 8px; }
.wc-val { font-size: 24px; font-weight: 700; color: var(--color-primary); }
.actions { display: flex; gap: 12px; margin-bottom: 24px; }
</style>
