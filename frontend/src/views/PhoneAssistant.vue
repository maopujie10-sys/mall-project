<template>
  <div class="phone-assistant">
    <div class="page-header">
      <h2>馃摫 AI鐢佃瘽鍔╃悊</h2>
      <p>璇煶IVR 路 鑷姩鎺ュ崟 路 杞汉宸?路 24h鍦ㄧ嚎</p>
      <div class="header-stats">
        <el-statistic title="浠婃棩鏉ョ數" :value="stats.today_calls" />
        <el-statistic title="鑷姩瑙ｅ喅鐜? :value="stats.auto_resolved" suffix="%" />
        <el-statistic title="骞冲潎鏃堕暱" :value="stats.avg_duration" />
        <el-statistic title="鍦ㄧ嚎鍧愬腑" :value="status.active_calls + '/' + status.lines" />
      </div>
    </div>
    <el-tabs v-model="tab">
      <el-tab-pane label="馃摓 閫氳瘽璁板綍" name="logs">
        <el-button @click="simulateDialog=true" size="small" type="primary" style="margin-bottom:12px">馃摓 妯℃嫙鏉ョ數</el-button>
        <el-table :data="logs" stripe size="small">
          <el-table-column prop="time" label="鏃堕棿" width="160" />
          <el-table-column prop="caller" label="鏉ョ數鍙风爜" width="140" />
          <el-table-column prop="intent" label="鎰忓浘" width="120" />
          <el-table-column prop="duration_sec" label="鏃堕暱(绉?" width="90" />
          <el-table-column label="鐘舵€?><template #default="{row}"><el-tag :type="row.resolved?'success':'warning'">{{ row.resolved''宸茶В鍐':'寰呭鐞' }}</el-tag></template></el-table-column>
          <el-table-column prop="note" label="澶囨敞" min-width="150" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="馃幍 IVR鑿滃崟" name="ivr">
        <el-card><pre style="background:#1e1e1e;color:#d4d4d4;padding:16px;border-radius:8px;font-size:13px">{{ JSON.stringify(ivrMenu, null, 2) }}</pre></el-card>
      </el-tab-pane>
      <el-tab-pane label="馃搳 鏁版嵁缁熻" name="stats">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="鎬婚€氳瘽鏁?>{{ stats.total_calls }}</el-descriptions-item>
          <el-descriptions-item label="浠婃棩鏉ョ數">{{ stats.today_calls }}</el-descriptions-item>
          <el-descriptions-item label="瑙ｅ喅鐜?>{{ stats.resolution_rate }}</el-descriptions-item>
          <el-descriptions-item label="鑷姩瑙ｅ喅">{{ stats.auto_resolved }}</el-descriptions-item>
          <el-descriptions-item label="骞冲潎鏃堕暱">{{ stats.avg_duration }}</el-descriptions-item>
          <el-descriptions-item label="杞汉宸?>{{ stats.transferred }}</el-descriptions-item>
        </el-descriptions>
      </el-tab-pane>
    </el-tabs>
    <el-dialog v-model="simulateDialog" title="妯℃嫙鏉ョ數" width="400">
      <el-form label-width="80">
        <el-form-item label="鏉ョ數鍙风爜"><el-input v-model="simCall.caller" placeholder="13800138000" /></el-form-item>
        <el-form-item label="鎰忓浘"><el-select v-model="simCall.intent"><el-option v-for="i in ['鍟嗗搧鍜ㄨ','璁㈠崟鏌ヨ','鍞悗鐢宠','鎶曡瘔寤鸿','鍚堜綔娲借皥']" :key="i" :label="i" :value="i" /></el-select></el-form-item>
        <el-form-item label="澶囨敞"><el-input v-model="simCall.note" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="simulateDialog=false">鍙栨秷</el-button><el-button type="primary" @click="doSimulate">馃摓 鎷ㄦ墦</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"
import { ElMessage } from "element-plus"
import { getPhoneStatus, getPhoneLogs, getIVRMenu, simulateCall, getPhoneStats } from "@/api/phone"
const tab = ref("logs"); const logs = ref([]); const ivrMenu = ref({}); const status = ref({}); const stats = ref({})
const simulateDialog = ref(false); const simCall = ref({caller:"13800138000",intent:"鍟嗗搧鍜ㄨ",note:""})
onMounted(async()=>{
  try{const r=await getPhoneStatus();if(r.ok)status.value=r}catch{}
  try{const r=await getPhoneLogs();if(r.ok)logs.value=r.logs||[]}catch{}
  try{const r=await getIVRMenu();if(r.ok)ivrMenu.value=r.menu||{}}catch{}
  try{const r=await getPhoneStats();if(r.ok)stats.value=r.stats||{}}catch{}
})
async function doSimulate(){
  try{const r=await simulateCall(simCall.value);if(r.ok){ElMessage.success("妯℃嫙鏉ョ數瀹屾垚");logs.value.unshift(r.call);simulateDialog.value=false}}catch(e){ElMessage.error(e.message)}
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
