<template>
  <div>
    <el-tabs type="card">
      <el-tab-pane label=''>
        <el-row :gutter="12" style="margin-bottom:12px">
          <el-col :span="12"><div class="metric-card"><div class="metric-label">{{ \('mallSub.title') }}</div><div class="metric-value">{{ inviteStats.total || 0 }}</div></div></el-col>
        </el-row>
        <el-table :data="invites" stripe size="small" v-loading="iv">
          <el-table-column prop="uuid" label="UUID" width="200" />
          <el-table-column prop="inviter_id" label="ID" width="100" />
          <el-table-column prop="invitee_id" label="ID" width="100" />
          <el-table-column prop="create_time" label='' width="160" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label=''>
        <el-table :data="lotteryList" stripe size="small" v-loading="lt">
          <el-table-column prop="activity_id" label="ID" width="200" />
          <el-table-column prop="title" label='' />
          <el-table-column prop="status" label='' width="80" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label=''>
        <el-table :data="promotes" stripe size="small" v-loading="pm">
          <el-table-column prop="uuid" label="UUID" width="200" />
          <el-table-column prop="title" label='' />
          <el-table-column prop="discount" label='' width="80" />
          <el-table-column prop="status" label='' width="80" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label=''>
        <el-table :data="subscribes" stripe size="small" v-loading="sb">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="user_id" label="ID" width="80" />
          <el-table-column prop="plan" label='' width="120" />
          <el-table-column prop="status" label='' width="80" />
          <el-table-column prop="create_time" label='' width="160" />
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { getInviteList, getInviteStats, getLotteryCurrent, getPromoteList, getSubscribeList } from '@/api/mall'

const invites = ref([]); const iv = ref(false)
const inviteStats = ref({})
const lotteryList = ref([]); const lt = ref(false)
const promotes = ref([]); const pm = ref(false)
const subscribes = ref([]); const sb = ref(false)

async function loadAll() {
  iv.value = lt.value = pm.value = sb.value = true
  try { const r = await getInviteList(); invites.value = r.list || r.records || [] } catch { }
  try { inviteStats.value = await getInviteStats() } catch { }
  try { lotteryList.value = [await getLotteryCurrent()] } catch { }
  try { const r = await getPromoteList(); promotes.value = r.list || r.records || [] } catch { }
  try { const r = await getSubscribeList(); subscribes.value = r.list || r.records || [] } catch { }
  iv.value = lt.value = pm.value = sb.value = false
}
onMounted(loadAll)
</script>
<style scoped>
.metric-card { padding: 12px; border-radius: 8px; text-align: center; background: linear-gradient(135deg,#8b5cf6,#7c3aed); color:#fff; }
.metric-label { font-size: 12px; opacity: 0.9; }
.metric-value { font-size: 24px; font-weight: 700; }
</style>