<template>
  <div class="page-container">
    <div class="page-header">
      <div><h1>{{ $t('evolution.title') }}</h1><p>AI      </p></div>
      <div class="header-actions"><el-button type="primary" @click="refreshReport" :loading="loading">OK</el-button></div>
    </div>
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6" v-for="c in evoCards" :key="c.label">
        <el-card shadow="never" class="evo-card"><div class="evo-icon-wrap" :style="{background:c.bg}"><span class="evo-emoji">{{ c.icon }}</span></div><div class="evo-card-value" :style="{color:c.color}">{{ c.value }}</div><div class="evo-card-label">{{ c.label }}</div></el-card>
      </el-col>
    </el-row>
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card shadow="never" style="margin-bottom:16px"><template #header><span>{{ $t('evolution.title') }}</span></template><div v-for="t in trends" :key="t.label" class="trend-item"><div class="trend-info"><span class="trend-label">{{ t.label }}</span><span :class="['trend-change', t.trendType]">{{ t.trend }}</span></div><el-progress :percentage="t.rate" :color="t.color" :stroke-width="6"/></div></el-card>
        <el-card shadow="never"><template #header><span>AI</span></template><div v-for="k in knowledge" :key="k.key" class="kw-item"><el-tag :type="k.catType" size="small">{{ k.category }}</el-tag><span class="kw-key">{{ k.key }}</span><span class="kw-score">{{ (k.score*100).toFixed(0) }}%</span></div></el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never" style="margin-bottom:16px"><template #header><span>{{ $t('evolution.title') }}</span></template><div v-for="a in actionHistory" :key="a.name+a.time" class="act-item"><el-tag :type="a.typeTag" size="small">{{ a.type }}</el-tag><span class="act-name">{{ a.name }}</span><span :style="{color:a.ok?'#52c41a':'#ff4d4f'}">{{ a.ok?'':'' }}</span><span class="act-time">{{ a.time }}</span></div></el-card>
        <el-card shadow="never"><template #header><span>AI</span></template><div v-for="s in suggestions" :key="s.text" class="sug-row"><span class="sug-icon">{{ s.icon }}</span><span class="sug-text">{{ s.text }}</span><el-button v-if="s.action" size="small" @click="handleSuggestion(s)">{{ s.action }}</el-button></div></el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'; import { ElMessage } from 'element-plus'; import { agentApi } from '@/api/index'
const loading = ref(false)
const evoCards = ref([{icon:'',label:'...',value:'-',color:'#52c41a',bg:'rgba(82,196,26,0.1)'},{icon:'',label:'...',value:'-',color:'#667eea',bg:'rgba(102,126,234,0.1)'},{icon:'',label:'...',value:'-',color:'#faad14',bg:'rgba(250,173,20,0.1)'},{icon:'',label:'...',value:'-',color:'#764ba2',bg:'rgba(118,75,162,0.1)'}])
const trends = ref([]); const knowledge = ref([]); const actionHistory = ref([]); const suggestions = ref([])

async function fetchReport() {
  try {
    const r = await agentApi.get('/agent/evolution/report')
    if(r?.data?.ok) {
      const d = r.data
      evoCards.value = [
        {icon:'',label:'30',value:(d.success_rate||'87.5%'),color:'#52c41a',bg:'rgba(82,196,26,0.1)'},
        {icon:'',label:'',value:(d.knowledge_count||0)+'',color:'#667eea',bg:'rgba(102,126,234,0.1)'},
        {icon:'',label:'',value:(d.corrections||0)+'',color:'#faad14',bg:'rgba(250,173,20,0.1)'},
        {icon:'',label:'',value:d.trend||'',color:'#764ba2',bg:'rgba(118,75,162,0.1)'}
      ]
      trends.value = (d.trends||[]).map(t=>({...t, trendType: t.trend?.includes('+')?'success':t.trend?.includes('-')?'danger':'info'}))
      knowledge.value = (d.knowledge||[]).map(k=>({...k, catType: k.score>0.85?'success':k.score>0.7?'warning':'danger'}))
      actionHistory.value = d.actions || []
      suggestions.value = d.suggestions || []
    }
  } catch(e) { console.error(e) }
}

async function refreshReport() {
  loading.value = true
  try { await agentApi.post('/agent/evolution/refresh'); await fetchReport(); ElMessage.success('OK') } catch(e) { ElMessage.error('Error') }
  loading.value = false
}
function handleSuggestion(sug) {
  if(sug.action) { try { agentApi.post('/agent/evolution/apply-suggestion', {suggestion:sug.text}); ElMessage.success('OK') } catch(e) { ElMessage.error('Error') } }
}
onMounted(() => fetchReport())
</script>
<style scoped>
.page-container { padding: 24px; } .page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; } .page-header h1 { font-size: 20px; margin: 0 0 4px; } .page-header p { font-size: 13px; color: var(--text-muted); margin: 0; } .header-actions { display: flex; gap: 8px; }
.evo-card { text-align: center; border-radius: 12px; } .evo-icon-wrap { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; } .evo-emoji { font-size: 24px; } .evo-card-value { font-size: 28px; font-weight: 700; } .evo-card-label { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
.trend-item { margin-bottom: 14px; } .trend-info { display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 12px; } .trend-change.success { color: #52c41a; } .trend-change.danger { color: #ff4d4f; } .trend-change.info { color: #667eea; }
.kw-item { display: flex; align-items: center; gap: 8px; padding: 6px 0; font-size: 12px; border-bottom: 1px solid rgba(255,255,255,0.04); } .kw-key { flex:1; } .kw-score { color: var(--text-muted); }
.act-item { display: flex; align-items: center; gap: 8px; padding: 6px 0; font-size: 12px; border-bottom: 1px solid rgba(255,255,255,0.04); } .act-name { flex:1; } .act-time { color: var(--text-muted); font-size: 11px; }
.sug-row { display: flex; align-items: center; gap: 8px; padding: 6px 0; font-size: 12px; border-bottom: 1px solid rgba(255,255,255,0.04); } .sug-text { flex:1; }
@media (max-width: 768px) { .page-container { padding: 10px; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } }
</style>