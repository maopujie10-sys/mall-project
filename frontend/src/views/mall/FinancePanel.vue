<template>
  <div>
    <el-tabs type="card">
      <el-tab-pane label=''>
        <el-table :data="walletLogs" stripe size="small" v-loading="wl">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="user_id" label="ID" width="80" />
          <el-table-column prop="amount" label='' width="100" />
          <el-table-column prop="type" label='' width="100" />
          <el-table-column prop="create_time" label='' width="160" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label=''>
        <el-table :data="recharges" stripe size="small" v-loading="rl">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="user_id" label="ID" width="80" />
          <el-table-column prop="amount" label='' width="100" />
          <el-table-column prop="status" label='' width="80" />
          <el-table-column label='' width="160">
            <template #default="{row}">
              <el-button size="small" link type="success" @click="auditRecharge({id:row.id,approved:true})">OK</el-button>
              <el-button size="small" link type="danger" @click="auditRecharge({id:row.id,approved:false})">OK</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label=''>
        <el-table :data="withdraws" stripe size="small" v-loading="wdl">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="user_id" label="ID" width="80" />
          <el-table-column prop="amount" label='' width="100" />
          <el-table-column prop="status" label='' width="80" />
          <el-table-column label='' width="160">
            <template #default="{row}">
              <el-button size="small" link type="success" @click="auditWithdraw({id:row.id,approved:true})">OK</el-button>
              <el-button size="small" link type="danger" @click="auditWithdraw({id:row.id,approved:false})">OK</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label=''>
        <el-table :data="rebates" stripe size="small" v-loading="rbl">
          <el-table-column prop="uuid" label="UUID" width="200" />
          <el-table-column prop="amount" label='' width="100" />
          <el-table-column prop="create_time" label='' width="160" />
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { getWalletLogs, getRechargePending, getWithdrawPending, getRebateList, auditRecharge as auditR, auditWithdraw as auditW } from '@/api/mall'
import { ElMessage } from 'element-plus'

const walletLogs = ref([]); const wl = ref(false)
const recharges = ref([]); const rl = ref(false)
const withdraws = ref([]); const wdl = ref(false)
const rebates = ref([]); const rbl = ref(false)

async function loadAll() {
  wl.value = true; rl.value = true; wdl.value = true; rbl.value = true
  try { const r = await getWalletLogs({ page: 1, size: 50 }); walletLogs.value = r.list || r.records || [] } catch { }
  try { const r = await getRechargePending({ page: 1, size: 50 }); recharges.value = r.list || r.records || [] } catch { }
  try { const r = await getWithdrawPending({ page: 1, size: 50 }); withdraws.value = r.list || r.records || [] } catch { }
  try { const r = await getRebateList({ page: 1, size: 50 }); rebates.value = r.list || r.records || [] } catch { }
  wl.value = false; rl.value = false; wdl.value = false; rbl.value = false
}
async function auditRecharge(data) { try { await auditR(data); ElMessage.success('OK'); loadAll() } catch { ElMessage.error('Error') } }
async function auditWithdraw(data) { try { await auditW(data); ElMessage.success('OK'); loadAll() } catch { ElMessage.error('Error') } }
onMounted(loadAll)
</script>