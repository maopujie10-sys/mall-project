<template>
  <div>
    <!-- KPI 汇总卡片 -->
    <el-row :gutter="12" style="margin-bottom:12px">
      <el-col :span="6"><div class="kpi-card c1"><div class="kpi-num">{{ fmt(financeHead?.totalSales||0) }}</div><div class="kpi-label">总销售额</div></div></el-col>
      <el-col :span="6"><div class="kpi-card c2"><div class="kpi-num">{{ fmt(financeHead?.totalProfit||0) }}</div><div class="kpi-label">总利润</div></div></el-col>
      <el-col :span="6"><div class="kpi-card c3"><div class="kpi-num">{{ fmt(financeHead?.totalOrders||0) }}</div><div class="kpi-label">总订单数</div></div></el-col>
      <el-col :span="6"><div class="kpi-card c4"><div class="kpi-num">{{ fmt(financeHead?.pendingProfit||0) }}</div><div class="kpi-label">待结算利润</div></div></el-col>
    </el-row>
    <!-- 日报表 -->
    <el-table :data="financeReport" stripe size="small" v-loading="frl" style="margin-bottom:16px">
      <el-table-column prop="day" label="日期" width="120" />
      <el-table-column prop="sales" label="销售额" width="120" />
      <el-table-column prop="profit" label="利润" width="100" />
      <el-table-column prop="orders" label="订单数" width="80" />
      <el-table-column prop="avgOrderValue" label="客单价" width="100" />
    </el-table>
    <el-tabs type="card">
      <el-tab-pane label='钱包流水'>
        <el-table :data="walletLogs" stripe size="small" v-loading="wl">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="user_id" label="用户ID" width="80" />
          <el-table-column prop="amount" label='金额' width="100" />
          <el-table-column prop="type" label='类型' width="100" />
          <el-table-column prop="create_time" label='时间' width="160" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label='充值'>
        <el-table :data="recharges" stripe size="small" v-loading="rl">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="user_id" label="用户ID" width="80" />
          <el-table-column prop="amount" label='金额' width="100" />
          <el-table-column prop="status" label='状态' width="80" />
          <el-table-column label='操作' width="160">
            <template #default="{row}">
              <el-button size="small" link type="success" @click="auditRecharge({id:row.id,approved:true})">通过</el-button>
              <el-button size="small" link type="danger" @click="auditRecharge({id:row.id,approved:false})">拒绝</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label='提现'>
        <el-table :data="withdraws" stripe size="small" v-loading="wdl">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="user_id" label="用户ID" width="80" />
          <el-table-column prop="amount" label='金额' width="100" />
          <el-table-column prop="status" label='状态' width="80" />
          <el-table-column label='操作' width="160">
            <template #default="{row}">
              <el-button size="small" link type="success" @click="auditWithdraw({id:row.id,approved:true})">通过</el-button>
              <el-button size="small" link type="danger" @click="auditWithdraw({id:row.id,approved:false})">拒绝</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label='返利'>
        <el-table :data="rebates" stripe size="small" v-loading="rbl">
          <el-table-column prop="uuid" label="UUID" width="200" />
          <el-table-column prop="amount" label='金额' width="100" />
          <el-table-column prop="create_time" label='时间' width="160" />
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { getWalletLogs, getRechargePending, getWithdrawPending, getRebateList, auditRecharge as auditR, auditWithdraw as auditW, getMerchantFinanceHead, getMerchantFinanceReport } from '@/api/mall'
import { ElMessage } from 'element-plus'

const walletLogs = ref([]); const wl = ref(false)
const recharges = ref([]); const rl = ref(false)
const withdraws = ref([]); const wdl = ref(false)
const rebates = ref([]); const rbl = ref(false)
const financeHead = ref(null)
const financeReport = ref([]); const frl = ref(false)

function fmt(v) {
  if (v == null) return '0'
  const n = Number(v)
  return Number.isNaN(n) ? String(v) : n.toLocaleString('en-US',{maximumFractionDigits:2})
}

async function loadAll() {
  wl.value = true; rl.value = true; wdl.value = true; rbl.value = true; frl.value = true
  try { const r = await getWalletLogs({ page: 1, size: 50 }); walletLogs.value = r.list || r.records || [] } catch { }
  try { const r = await getRechargePending({ page: 1, size: 50 }); recharges.value = r.list || r.records || [] } catch { }
  try { const r = await getWithdrawPending({ page: 1, size: 50 }); withdraws.value = r.list || r.records || [] } catch { }
  try { const r = await getRebateList({ page: 1, size: 50 }); rebates.value = r.list || r.records || [] } catch { }
  try { financeHead.value = await getMerchantFinanceHead() } catch { }
  try { const r = await getMerchantFinanceReport({ page:1, size:30 }); financeReport.value = r.list || r.records || (Array.isArray(r)?r:[]) } catch { }
  wl.value = false; rl.value = false; wdl.value = false; rbl.value = false; frl.value = false
}
async function auditRecharge(data) { try { await auditR(data); ElMessage.success('OK'); loadAll() } catch { ElMessage.error('Error') } }
async function auditWithdraw(data) { try { await auditW(data); ElMessage.success('OK'); loadAll() } catch { ElMessage.error('Error') } }
onMounted(loadAll)
</script>
<style scoped>
.kpi-card { border-radius:8px; padding:16px; color:#fff; text-align:center; }
.kpi-card.c1 { background: linear-gradient(135deg,#667eea,#764ba2); }
.kpi-card.c2 { background: linear-gradient(135deg,#f093fb,#f5576c); }
.kpi-card.c3 { background: linear-gradient(135deg,#4facfe,#00f2fe); }
.kpi-card.c4 { background: linear-gradient(135deg,#43e97b,#38f9d7); }
.kpi-num { font-size:24px; font-weight:700; }
.kpi-label { font-size:12px; opacity:.9; margin-top:4px; }
</style>