<template>
  <div class="page-shell">
    <div class="page-header"><h2>{{ \('competitor.title') }}</h2><p>++</p></div>
    <el-card><template #header></template>
      <el-input v-model="targetUrl" placeholder="URL"/>
      <el-input v-model="targetName" placeholder='Enter...' style="margin-top:8px"/>
      <el-button type="primary" style="margin-top:8px" @click="addTarget" :loading="adding">OK</el-button>
    </el-card>
    <el-card style="margin-top:16px"><template #header><el-button size="small" @click="refreshReports" style="float:right">OK</el-button></template>
      <el-empty v-if="!reports.length" description=''/>
      <div v-for="r in reports" :key="r.url||r.id" class="comp-item">
        <div><span class="comp-name">{{ r.name }}</span><span class="comp-url">{{ r.url?.slice(0,40) }}</span></div>
        <div><el-tag size="small" :type="r.status===''?'warning':'success''>{{ r.status }}</el-tag>
        <span class="comp-price" v-if="r.price">${{ r.price }}</span></div>
      </div>
    </el-card>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"; import { ElMessage } from "element-plus"; import { agentApi } from "@/api"
const targetUrl = ref(''); const targetName = ref(''); const reports = ref([]); const adding = ref(false)

async function addTarget() {
  if(!targetUrl.value) return; adding.value = true
  try {
    const r = await agentApi.post("/agent/competitor/add", { url: targetUrl.value, name: targetName.value||targetUrl.value })
    if(r?.data?.ok) { reports.value.push(r.data.target||{name:targetName.value,url:targetUrl.value,status:''}); ElMessage.success('OK'); targetUrl.value=''; targetName.value='' }
  } catch(e) { ElMessage.error(e.message) }; adding.value = false
}
async function refreshReports() {
  try {
    const r = await agentApi.get("/agent/competitor/list")
    if(r?.data?.ok) reports.value = (r.data.targets||[]).map(t=>({...t,status:t.active?'':''}))
  } catch(e) {}
}
onMounted(() => refreshReports())
</script>
<style scoped>
.page-shell { max-width: 900px; margin: 0 auto; padding: 20px; }
.page-header { margin-bottom: 16px; } .page-header h2 { font-size: 20px; color: #e0e0ff; margin: 0; } .page-header p { font-size: 12px; color: rgba(255,255,255,0.5); margin: 4px 0; }
.comp-item { display: flex; justify-content: space-between; align-items: center; padding: 10px; background: rgba(102,126,234,0.06); border-radius: 8px; margin-bottom: 6px; }
.comp-name { color: #e0e0e0; font-size: 13px; } .comp-url { color: rgba(255,255,255,0.3); font-size: 11px; margin-left: 8px; } .comp-price { color: #52c41a; font-size: 12px; margin-left: 8px; }
@media (max-width: 768px) { .page-shell { padding: 10px; } }
</style>