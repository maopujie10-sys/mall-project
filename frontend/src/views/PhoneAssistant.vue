<template>
  <div class="phone-assistant">
    <div class="page-header">
      <h2>📱 AI电话助理</h2>
      <p>语音IVR · 自动接单 · 转人工 · 24h在线</p>
      <div class="header-stats">
        <el-statistic title="今日来电" :value="stats.today_calls" />
        <el-statistic title="自动解决率" :value="stats.auto_resolved" suffix="%" />
        <el-statistic title="平均时长" :value="stats.avg_duration" />
        <el-statistic title="在线坐席" :value="status.active_calls + '/' + status.lines" />
      </div>
    </div>
    <el-tabs v-model="tab">
      <el-tab-pane label="📞 通话记录" name="logs">
        <el-button @click="simulateDialog=true" size="small" type="primary" style="margin-bottom:12px">📞 模拟来电</el-button>
        <el-table :data="logs" stripe size="small">
          <el-table-column prop="time" label="时间" width="160" />
          <el-table-column prop="caller" label="来电号码" width="140" />
          <el-table-column prop="intent" label="意图" width="120" />
          <el-table-column prop="duration_sec" label="时长(秒)" width="90" />
          <el-table-column label="状态"><template #default="{row}"><el-tag :type="row.resolved?'success':'warning'">{{ row.resolved?'已解决':'待处理' }}</el-tag></template></el-table-column>
          <el-table-column prop="note" label="备注" min-width="150" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="🎵 IVR菜单" name="ivr">
        <el-card><pre style="background:#1e1e1e;color:#d4d4d4;padding:16px;border-radius:8px;font-size:13px">{{ JSON.stringify(ivrMenu, null, 2) }}</pre></el-card>
      </el-tab-pane>
      <el-tab-pane label="📊 数据统计" name="stats">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="总通话数">{{ stats.total_calls }}</el-descriptions-item>
          <el-descriptions-item label="今日来电">{{ stats.today_calls }}</el-descriptions-item>
          <el-descriptions-item label="解决率">{{ stats.resolution_rate }}</el-descriptions-item>
          <el-descriptions-item label="自动解决">{{ stats.auto_resolved }}</el-descriptions-item>
          <el-descriptions-item label="平均时长">{{ stats.avg_duration }}</el-descriptions-item>
          <el-descriptions-item label="转人工">{{ stats.transferred }}</el-descriptions-item>
        </el-descriptions>
      </el-tab-pane>
    </el-tabs>
    <el-dialog v-model="simulateDialog" title="模拟来电" width="400">
      <el-form label-width="80">
        <el-form-item label="来电号码"><el-input v-model="simCall.caller" placeholder="13800138000" /></el-form-item>
        <el-form-item label="意图"><el-select v-model="simCall.intent"><el-option v-for="i in ['商品咨询','订单查询','售后申请','投诉建议','合作洽谈']" :key="i" :label="i" :value="i" /></el-select></el-form-item>
        <el-form-item label="备注"><el-input v-model="simCall.note" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="simulateDialog=false">取消</el-button><el-button type="primary" @click="doSimulate">📞 拨打</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"
import { getPhoneStatus, getPhoneLogs, getIVRMenu, simulateCall, getPhoneStats } from "@/api/phone"
const tab = ref("logs"); const logs = ref([]); const ivrMenu = ref({}); const status = ref({}); const stats = ref({})
const simulateDialog = ref(false); const simCall = ref({caller:"13800138000",intent:"商品咨询",note:""})
onMounted(async()=>{
  try{const r=await getPhoneStatus();if(r.ok)status.value=r}catch{}
  try{const r=await getPhoneLogs();if(r.ok)logs.value=r.logs||[]}catch{}
  try{const r=await getIVRMenu();if(r.ok)ivrMenu.value=r.menu||{}}catch{}
  try{const r=await getPhoneStats();if(r.ok)stats.value=r.stats||{}}catch{}
})
async function doSimulate(){
  try{const r=await simulateCall(simCall.value);if(r.ok){ElMessage.success("模拟来电完成");logs.value.unshift(r.call);simulateDialog.value=false}}catch(e){ElMessage.error(e.message)}
}
</script>
<style scoped>
.phone-assistant { padding: 20px; }
.page-header { margin-bottom: 20px; }
.page-header h2 { margin: 0 0 4px; }
.page-header p { margin: 0 0 12px; color: #999; font-size: 13px; }
.header-stats { display: flex; gap: 32px; }
</style>
