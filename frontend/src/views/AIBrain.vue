<template>
  <div class="page-container">
    <div class="page-header">
      <div><h1>AI 商城大脑</h1><p>全自动分析健康度 · 智能选品建议 · 死品检测 · 品类缺口预警</p></div>
      <div class="header-actions">
        <el-button type="primary" @click="runScan" :loading="scanning">全站扫描</el-button>
        <el-button type="success" @click="runAutoOps" :loading="autoRunning">AI自动运维</el-button>
      </div>
    </div>
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6" v-for="c in summaryCards" :key="c.label">
        <el-card shadow="never" :class="['metric-card', c.color]"><div class="metric-num">{{ c.value }}</div><div class="metric-label">{{ c.label }}</div><div class="metric-sub">{{ c.sub }}</div></el-card>
      </el-col>
    </el-row>
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header><div class="panel-header"><span>商品健康度</span><el-select v-model="filterStatus" size="small" style="width:120px"><el-option label="全部" value="all"/><el-option label="热销" value="hot"/><el-option label="正常" value="normal"/><el-option label="冷门" value="cold"/><el-option label="死品" value="dead"/></el-select></div></template>
          <el-table :data="filteredProducts" stripe size="small" max-height="280">
            <el-table-column prop="icon" label="" width="40"/><el-table-column prop="name" label="商品" min-width="180"/><el-table-column prop="category" label="品类" width="110"/><el-table-column prop="price" label="价格" width="100"/><el-table-column prop="sales" label="销量" width="80"/>
            <el-table-column prop="stock" label="库存" width="80"/><el-table-column prop="status" label="状态" width="90"><template #default="{row}"><el-tag :type="row.statusType" size="small">{{ row.status }}</el-tag></template></el-table-column>
            <el-table-column label="操作" width="80"><template #default="{row}"><el-button link type="primary" size="small" @click="handleReplace(row)" v-if="row.status==='死品'">替换</el-button></template></el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never" style="margin-bottom:16px"><template #header><span>品类缺口分析</span></template><div class="gap-list"><div v-for="g in gaps" :key="g.name" class="gap-item"><div class="gap-info"><div class="gap-name">{{ g.name }}</div><div class="gap-bar-wrap"><div class="gap-bar"><div class="gap-fill" :class="g.level" :style="{width:g.percent+'%'}"></div></div><span class="gap-num">{{ g.current }}/{{ g.target }}</span></div></div></div></div></el-card>
        <el-card shadow="never"><template #header><span>AI 智能建议</span></template><div class="ai-suggestions"><div v-for="(s,i) in suggestions" :key="i" class="sug-item"><span>{{ i+1 }}.</span><span>{{ s }}</span></div></div></el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script setup>
import { ref, reactive, computed, onMounted } from 'vue'; import { ElMessage, ElMessageBox } from 'element-plus'; import { agentApi } from '@/api/index'
const scanning = ref(false); const autoRunning = ref(false); const filterStatus = ref('all')
const summaryCards = ref([{ label:'加载中...', value:'-', sub:'', color:'blue' },{ label:'加载中...', value:'-', sub:'', color:'red' },{ label:'加载中...', value:'-', sub:'', color:'gray' },{ label:'加载中...', value:'-', sub:'', color:'orange' }])
const products = ref([]); const gaps = ref([]); const suggestions = ref([])

const filteredProducts = computed(() => {
  if(filterStatus.value==='all') return products.value
  const map = { hot:'热销', normal:'正常', cold:'冷门', dead:'死品' }
  return products.value.filter(p => p.status === map[filterStatus.value])
})

async function fetchBrain() {
  try {
    const r = await agentApi.get('/mall-brain/summary')
    if(r?.data?.ok) {
      const d = r.data
      summaryCards.value = [
        { label:'商品总数', value: d.total_products||0, sub: (d.online_products||0)+'个在线商品', color:'blue' },
        { label:'热销商品', value: d.hot_products||0, sub: '高活跃', color:'red' },
        { label:'死品待换', value: d.dead_products||0, sub: '需替换', color:'gray' },
        { label:'品类缺口', value: d.gap_categories||0, sub: '需补充', color:'orange' }
      ]
      products.value = (d.products||[]).map(p=>({...p, statusType: p.status==='热销'?'danger':p.status==='正常'?'success':p.status==='冷门'?'warning':'info'}))
      gaps.value = (d.gaps||[]).map(g=>({...g, level: g.percent<30?'low':g.percent<60?'mid':'ok'}))
      suggestions.value = d.suggestions || []
    }
  } catch(e) { console.error(e) }
}

async function runScan() {
  scanning.value = true
  try { const r = await agentApi.post('/mall-brain/scan'); if(r?.data?.ok) { ElMessage.success('全站扫描完成: '+r.data.summary); fetchBrain() } } catch(e) { ElMessage.error('扫描失败') }
  scanning.value = false
}
async function runAutoOps() {
  autoRunning.value = true
  try { const r = await agentApi.post('/mall-brain/auto-ops'); if(r?.data?.ok) ElMessage.success('AI自动运维完成: '+r.data.result) } catch(e) { ElMessage.error('运维失败') }
  autoRunning.value = false; fetchBrain()
}
function handleReplace(row) {
  ElMessageBox.confirm('确认要寻找 "'+row.name+'" 的替代品吗？', '替换商品', { confirmButtonText:'确认', cancelButtonText:'取消', type:'warning' })
  .then(async () => { try { await agentApi.post('/mall-brain/replace', {product_id:row.id}); ElMessage.success('已开始替换'); fetchBrain() } catch(e) { ElMessage.error('替换失败') } }).catch(()=>{})
}
onMounted(() => fetchBrain())
</script>
<style scoped>
.page-container { padding: 24px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; } .page-header h1 { font-size: 20px; margin: 0 0 4px; } .page-header p { font-size: 13px; color: var(--text-muted); margin: 0; }
.header-actions { display: flex; gap: 8px; }
.metric-card { text-align: center; border-radius: 12px; border-top: 3px solid transparent; } .metric-card.blue { border-top-color: #667eea; } .metric-card.red { border-top-color: #ff4d4f; } .metric-card.gray { border-top-color: #d9d9d9; } .metric-card.orange { border-top-color: #faad14; }
.metric-num { font-size: 36px; font-weight: 700; } .metric-label { font-size: 13px; color: var(--text-secondary); margin: 4px 0; } .metric-sub { font-size: 11px; color: var(--text-muted); }
.panel-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; font-size: 14px; }
.gap-list { display: flex; flex-direction: column; gap: 12px; } .gap-item { display: flex; align-items: center; justify-content: space-between; gap: 10px; } .gap-info { flex: 1; min-width: 0; } .gap-name { font-size: 13px; font-weight: 500; margin-bottom: 4px; }
.gap-bar-wrap { display: flex; align-items: center; gap: 8px; } .gap-bar { flex: 1; height: 6px; background: rgba(13,16,37,0.55); border-radius: 3px; overflow: hidden; } .gap-fill { height: 100%; border-radius: 3px; transition: width 0.4s; } .gap-fill.low { background: #ff4d4f; } .gap-fill.mid { background: #faad14; } .gap-fill.ok { background: #52c41a; } .gap-num { font-size: 11px; color: var(--text-muted); white-space: nowrap; }
.ai-suggestions { display: flex; flex-direction: column; gap: 8px; } .sug-item { display: flex; align-items: flex-start; gap: 8px; font-size: 12px; color: var(--text-secondary); line-height: 1.5; }
@media (max-width: 768px) { .page-container { padding: 10px; } .page-header { flex-direction: column; gap: 10px; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } }
</style>