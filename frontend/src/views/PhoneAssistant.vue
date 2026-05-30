<template>
  <div class="phone-assistant">
    <div class="page-header">
      <h2> AI</h2>
      <p>IVR    ? 24h</p>
      <div class="header-stats">
        <el-statistic :title="$t('phone.title')" :value="stats.today_calls" />
        <el-statistic title="状态" :value="stats.auto_resolved" suffix="%" />
        <el-statistic title='' :value="stats.avg_duration" />
        <el-statistic :title="$t('phone.title')" :value="status.active_calls + '/' + status.lines" />
      </div>
    </div>
    <el-tabs v-model="tab">
      <el-tab-pane label='Status' name="logs">
        
        <el-table :data="logs" stripe size="small">
          <el-table-column prop="time" label='Status' width="160" />
          <el-table-column prop="caller" :label="$t('phone.title')" width="140" />
          <el-table-column prop="intent" label='Status' width="120" />
          <el-table-column prop="duration_sec" label="时长(秒)" width="90" />
          <el-table-column label=""><template #default="{row}"><el-tag :type="row.resolved?'success':'warning'">{{ row.resolved?'已解决':'未解决' }}</el-tag></template></el-table-column>
          <el-table-column prop="note" label='Status' min-width="150" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label=" IVR" name="ivr">
        <el-card><pre style="background:#1e1e1e;color:#d4d4d4;padding:16px;border-radius:8px;font-size:13px">{{ JSON.stringify(ivrMenu, null, 2) }}</pre></el-card>
      </el-tab-pane>
      <el-tab-pane label=" " name="stats">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="">{{ stats.total_calls }}</el-descriptions-item>
          <el-descriptions-item :label="$t('phone.title')">{{ stats.today_calls }}</el-descriptions-item>
          <el-descriptions-item label="">{{ stats.resolution_rate }}</el-descriptions-item>
          <el-descriptions-item :label="$t('phone.title')">{{ stats.auto_resolved }}</el-descriptions-item>
          <el-descriptions-item label=''>{{ stats.avg_duration }}</el-descriptions-item>
          <el-descriptions-item label="">{{ stats.transferred }}</el-descriptions-item>
        </el-descriptions>
      </el-tab-pane>
    </el-tabs>
    <el-dialog v-model="simulateDialog" :title="$t('phone.title')" width="400">
      <el-form label-width="80">
        <el-form-item :label="$t('phone.title')"><el-input v-model="simCall.caller" placeholder="13800138000" /></el-form-item>
        <el-form-item label=''><el-select v-model="simCall.intent"><el-option v-for="i in ['','','','','']" :key="i" :label="i" :value="i" /></el-select></el-form-item>
        <el-form-item label=''><el-input v-model="simCall.note" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="simulateDialog=false">OK</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"
import { getPhoneStatus, getPhoneLogs, getIVRMenu, simulateCall, getPhoneStats } from "@/api/phone"
const tab = ref("logs"); const logs = ref([]); const ivrMenu = ref({}); const status = ref({}); const stats = ref({})
const simulateDialog = ref(false); const simCall = ref({caller:"13800138000",intent:"",note:''})
onMounted(async()=>{
  try{const r=await getPhoneStatus();if(r.ok)status.value=r}catch{}
  try{const r=await getPhoneLogs();if(r.ok)logs.value=r.logs||[]}catch{}
  try{const r=await getIVRMenu();if(r.ok)ivrMenu.value=r.menu||{}}catch{}
  try{const r=await getPhoneStats();if(r.ok)stats.value=r.stats||{}}catch{}
})
async function doSimulate(){
  try{const r=await simulateCall(simCall.value);if(r.ok){ElMessage.success("");logs.value.unshift(r.call);simulateDialog.value=false}}catch(e){ElMessage.error(e.message)}
}
</script>
<style scoped>
.phone-assistant { padding: 20px; }
.page-header { margin-bottom: 20px; }
.page-header h2 { margin: 0 0 4px; }
.page-header p { margin: 0 0 12px; color: #999; font-size: 13px; }
.header-stats { display: flex; gap: 32px; }
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>
