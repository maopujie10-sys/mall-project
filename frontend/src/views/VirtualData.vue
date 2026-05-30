<template>
  <div class="page-container">
    <div class="page-header"><div><h1>{{ \('virtual.title') }}</h1><p>    ///</p></div><div class="header-actions"><el-button type="primary" @click="generateAll" :loading="allRunning">OK</el-button><el-button type="danger" @click="clearAll">OK</el-button></div></div>
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6" v-for="s in dataStats" :key="s.label"><el-card shadow="never" class="stat-card"><div class="stat-num">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></el-card></el-col>
    </el-row>
    <el-row :gutter="16">
      <el-col :span="16">
        <el-row :gutter="12">
          <el-col :span="8" v-for="gen in generators" :key="gen.key"><el-card shadow="never" class="gen-card" @click="runGenerate(gen.key)"><div class="gen-icon">{{ gen.icon }}</div><div class="gen-name">{{ gen.name }}</div><div class="gen-count"> {{ gen.count }} </div><el-button size="small" type="primary" :loading="gen.running">{{ gen.running?'...':'' }}</el-button></el-card></el-col>
        </el-row>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never" style="margin-bottom:16px"><template #header><span>{{ \('virtual.title') }}</span><el-switch v-model="realtimeRunning" size="small" style="margin-left:10px"/></template>
          <div class="rt-grid"><div class="rt-item"><span class="rt-label">{{ \('virtual.title') }}</span><span class="rt-val">{{ rtStats.onlineUsers }}</span></div><div class="rt-item"><span class="rt-label">{{ \('virtual.title') }}</span><span class="rt-val">{{ rtStats.todayOrders }}</span></div><div class="rt-item"><span class="rt-label">{{ \('virtual.title') }}</span><span class="rt-val">{{ rtStats.activeProducts }}</span></div><div class="rt-item"><span class="rt-label">{{ \('virtual.title') }}</span><span class="rt-val">${{ rtStats.todayRevenue }}</span></div></div>
        </el-card>
        <el-card shadow="never"><template #header><span>{{ \('virtual.title') }}</span></template><div v-for="(item,i) in liveFeed" :key="i" class="feed-item"><span>{{ item.icon }}</span><span>{{ item.text }}</span><span class="feed-time">{{ item.time }}</span></div><el-empty v-if="!liveFeed.length" description=''/></el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script setup>
import { ref, reactive, watch, onMounted } from 'vue'; import { ElMessage, ElMessageBox } from 'element-plus'; import { agentApi } from '@/api/index'
const realtimeRunning = ref(true); const allRunning = ref(false); let feedTimer = null
const dataStats = ref([{label:'',value:0},{label:'',value:0},{label:'',value:0},{label:'',value:'$0'}])
const generators = reactive([{key:'products',icon:'',name:'',count:0,running:false},{key:'users',icon:'',name:'',count:0,running:false},{key:'orders',icon:'',name:'',count:0,running:false},{key:'reviews',icon:'',name:'',count:0,running:false},{key:'categories',icon:'',name:'',count:0,running:false},{key:'transactions',icon:'',name:'',count:0,running:false}])
const rtStats = reactive({ onlineUsers:0, todayOrders:0, activeProducts:0, todayRevenue:0 })
const liveFeed = reactive([])

async function fetchStats() {
  try { const r = await agentApi.get('/agent/virtual/stats'); if(r?.data?.ok) { const d = r.data; dataStats.value = [{label:'',value:d.products||0},{label:'',value:d.users||0},{label:'',value:d.orders||0},{label:'',value:'$'+(d.revenue||0)}]; rtStats.onlineUsers = d.online_users||0; rtStats.todayOrders = d.today_orders||0; rtStats.activeProducts = d.active_products||0; rtStats.todayRevenue = d.today_revenue||0 } } catch(e) {}
}
async function runGenerate(type) {
  const gen = generators.find(g=>g.key===type); if(!gen||gen.running) return; gen.running = true
  try { const r = await agentApi.post('/agent/virtual/generate', {type}); if(r?.data?.ok) { gen.count += r.data.count||100; ElMessage.success(gen.name+'') } } catch(e) { ElMessage.error('Error') }
  gen.running = false; fetchStats()
}
async function generateAll() {
  allRunning.value = true
  for(const gen of generators) { gen.running = true; try { const r = await agentApi.post('/agent/virtual/generate', {type:gen.key}); if(r?.data?.ok) gen.count += r.data.count||100 } catch(e) {}; gen.running = false }
  allRunning.value = false; ElMessage.success('OK'); fetchStats()
}
async function clearAll() {
  try { await ElMessageBox.confirm('','',{type:'warning',confirmButtonText:''}); await agentApi.post('/agent/virtual/clear'); ElMessage.success('OK'); fetchStats() } catch {}
}
watch(realtimeRunning, val => {
  if(val) { feedTimer = setInterval(() => { rtStats.onlineUsers = Math.max(0, rtStats.onlineUsers+Math.floor(Math.random()*3)-1); rtStats.todayOrders += Math.floor(Math.random()*3); rtStats.todayRevenue += Math.floor(Math.random()*500) }, 3000) } else { clearInterval(feedTimer) }
})
onMounted(() => { fetchStats(); if(realtimeRunning.value) { feedTimer = setInterval(() => { rtStats.onlineUsers = Math.max(0, rtStats.onlineUsers+Math.floor(Math.random()*3)-1); rtStats.todayOrders += Math.floor(Math.random()*3); rtStats.todayRevenue += Math.floor(Math.random()*500) }, 3000) } })
</script>
<style scoped>
.page-container { padding: 24px; } .page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; } .page-header h1 { font-size: 20px; margin: 0 0 4px; } .page-header p { font-size: 13px; color: var(--text-muted); margin: 0; } .header-actions { display: flex; gap: 8px; }
.stat-card { text-align: center; } .stat-num { font-size: 32px; font-weight: 700; } .stat-label { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
.gen-card { text-align: center; cursor: pointer; transition: transform .2s; } .gen-card:hover { transform: translateY(-2px); } .gen-icon { font-size: 28px; margin-bottom: 6px; } .gen-name { font-size: 14px; font-weight: 600; margin-bottom: 4px; } .gen-count { font-size: 11px; color: var(--text-muted); margin-bottom: 8px; }
.rt-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; } .rt-item { text-align: center; } .rt-label { font-size: 11px; color: var(--text-muted); display: block; } .rt-val { font-size: 20px; font-weight: 700; }
.feed-item { display: flex; gap: 8px; padding: 6px 0; font-size: 12px; border-bottom: 1px solid rgba(255,255,255,0.04); align-items: center; } .feed-time { color: var(--text-muted); font-size: 10px; margin-left: auto; }
@media (max-width: 768px) { .page-container { padding: 10px; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } }
</style>