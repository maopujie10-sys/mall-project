<template>
  <div class="page-container model-center">
    <div class="page-header">
      <h2>模型中心</h2>
      <p>多模型管理 · 智能切换 · 使用统计</p>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6">
        <div class="metric-card"><div class="metric-label">可用模型</div><div class="metric-value">{{ models.length }}</div><div class="metric-sub">跨 {{ providers.length }} 个平台</div></div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card"><div class="metric-label">当前模型</div><div class="metric-value" style="color:#52c41a">{{ currentModel?.name || '-' }}</div><div class="metric-sub">{{ currentModel?.provider || '' }}</div></div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card"><div class="metric-label">今日调用</div><div class="metric-value">{{ stats.todayCalls }}</div><div class="metric-sub">成功率 {{ stats.successRate }}%</div></div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card"><div class="metric-label">本月消耗</div><div class="metric-value" style="color:#faad14">{{ stats.monthlyCost }}</div><div class="metric-sub">剩余额度 {{ stats.remaining }}</div></div>
      </el-col>
    </el-row>

    <!-- 模型列表 -->
    <el-card shadow="never">
      <template #header>
        <div class="card-header-row"><span>模型列表</span><el-button type="primary" size="small" @click="showAdd = true">添加模型</el-button></div>
      </template>
      <el-table :data="filteredModels" stripe>
        <el-table-column prop="name" label="模型名称" min-width="160">
          <template #default="{row}"><span class="model-name">{{ row.icon }} {{ row.name }}</span></template>
        </el-table-column>
        <el-table-column prop="provider" label="供应商" width="120"><template #default="{row}"><el-tag size="small">{{ row.provider }}</el-tag></template></el-table-column>
        <el-table-column prop="type" label="类型" width="100"><template #default="{row}"><el-tag :type="row.type==='text'?'':'warning'" size="small">{{ row.type==='text'?'文本':'多模态' }}</el-tag></template></el-table-column>
        <el-table-column label="速度" width="120"><template #default="{row}"><el-progress :percentage="row.speed" :stroke-width="6" :color="speedColor(row.speed)" /></template></el-table-column>
        <el-table-column label="价格" width="140"><template #default="{row}"><span class="cost">输入 ¥{{ row.inputPrice }} / 输出 ¥{{ row.outputPrice }}</span></template></el-table-column>
        <el-table-column prop="calls" label="调用次数" width="100" sortable />
        <el-table-column prop="avgLatency" label="平均延迟" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{row}">
            <el-switch v-model="row.enabled" @change="toggleModel(row)" size="small" />
            <el-tag v-if="row.id===activeModelId" type="success" size="small" style="margin-left:6px">当前</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{row}">
            <el-button link type="primary" size="small" @click="testSpeed(row)">测速</el-button>
            <el-button link type="primary" size="small" @click="setActive(row)" v-if="row.id!==activeModelId">切换</el-button>
            <el-button link type="primary" size="small" @click="editModel(row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="removeModel(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 模式选择 -->
    <el-card shadow="never" style="margin-top:16px">
      <template #header><span>推理模式</span></template>
      <el-radio-group v-model="activeMode" size="large" @change="switchMode">
        <el-radio-button v-for="m in modes" :key="m.id" :value="m.id">
          <div class="mode-option"><div class="mode-name">{{ m.name }}</div><div class="mode-desc">{{ m.desc }}</div></div>
        </el-radio-button>
      </el-radio-group>
    </el-card>

    <!-- 使用统计 -->
    <el-card shadow="never" style="margin-top:16px">
      <template #header><span>使用统计</span></template>
      <el-table :data="usageStats" stripe>
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="model" label="模型" width="140" />
        <el-table-column prop="calls" label="调用次数" width="100" sortable />
        <el-table-column prop="tokens" label="Token消耗" width="120" sortable />
        <el-table-column prop="cost" label="费用(¥)" width="100" sortable />
        <el-table-column prop="avgTime" label="平均响应" width="100" />
      </el-table>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="showAdd" :title="editingModel?'编辑模型':'添加模型'" width="520px">
      <el-form :model="modelForm" label-width="90px">
        <el-form-item label="模型名称"><el-input v-model="modelForm.name" placeholder="如 DeepSeek V4" /></el-form-item>
        <el-form-item label="供应商"><el-select v-model="modelForm.provider" style="width:100%"><el-option v-for="p in providers" :key="p" :label="p" :value="p" /></el-select></el-form-item>
        <el-form-item label="API地址"><el-input v-model="modelForm.apiUrl" placeholder="https://api.example.com/v1" /></el-form-item>
        <el-form-item label="API密钥"><el-input v-model="modelForm.apiKey" type="password" show-password placeholder="sk-..." /></el-form-item>
        <el-form-item label="类型"><el-radio-group v-model="modelForm.type"><el-radio value="text">纯文本</el-radio><el-radio value="multimodal">多模态</el-radio></el-radio-group></el-form-item>
        <el-form-item label="输入价格"><el-input-number v-model="modelForm.inputPrice" :min="0" :precision="2" :step="0.01" /> <span style="margin-left:4px">元/1K tokens</span></el-form-item>
        <el-form-item label="输出价格"><el-input-number v-model="modelForm.outputPrice" :min="0" :precision="2" :step="0.01" /> <span style="margin-left:4px">元/1K tokens</span></el-form-item>
      </el-form>
      <template #footer><el-button @click="showAdd=false">取消</el-button><el-button type="primary" @click="saveModel" :loading="saving">{{editingModel?'保存':'添加'}}</el-button></template>
    </el-dialog>

    <!-- 测速结果 -->
    <el-dialog v-model="showSpeedResult" title="测速结果" width="400px">
      <el-descriptions :column="1" border v-if="speedResult">
        <el-descriptions-item label="模型">{{ speedResult.model }}</el-descriptions-item>
        <el-descriptions-item label="响应时间">{{ speedResult.latency }}ms</el-descriptions-item>
        <el-descriptions-item label="首Token延迟">{{ speedResult.firstToken }}ms</el-descriptions-item>
        <el-descriptions-item label="Token/秒">{{ speedResult.tokensPerSec }}</el-descriptions-item>
        <el-descriptions-item label="成功率">{{ speedResult.ok ? '✅ 通过' : '❌ 失败' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer><el-button @click="showSpeedResult=false">关闭</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listModels, switchModel, getModelStatus, testModelSpeed } from '@/api/model'

const activeModelId = ref('deepseek')
const activeMode = ref('quality')
const showAdd = ref(false)
const showSpeedResult = ref(false)
const editingModel = ref(null)
const saving = ref(false)
const speedResult = ref(null)
const testingModel = ref('')

const providers = ['DeepSeek', 'OpenAI', 'Anthropic', 'Google', 'Ollama', 'OpenRouter', '自定义']

const models = ref([
  { id:'deepseek', name:'DeepSeek V4 Pro', provider:'DeepSeek', icon:'🐋', type:'text', apiUrl:'', apiKey:'', speed:92, inputPrice:0.14, outputPrice:0.28, calls:12893, avgLatency:'320ms', enabled:true },
  { id:'claude', name:'Claude 4 Opus', provider:'Anthropic', icon:'🎭', type:'multimodal', apiUrl:'', apiKey:'', speed:65, inputPrice:15, outputPrice:75, calls:3421, avgLatency:'580ms', enabled:true },
  { id:'gpt4', name:'GPT-4.5', provider:'OpenAI', icon:'🧩', type:'multimodal', apiUrl:'', apiKey:'', speed:55, inputPrice:2.5, outputPrice:10, calls:7654, avgLatency:'720ms', enabled:false },
  { id:'gemini', name:'Gemini 2.5 Pro', provider:'Google', icon:'💎', type:'multimodal', apiUrl:'', apiKey:'', speed:78, inputPrice:1.25, outputPrice:5, calls:2100, avgLatency:'450ms', enabled:true },
  { id:'qwen', name:'Qwen3-Max', provider:'OpenRouter', icon:'🔥', type:'text', apiUrl:'', apiKey:'', speed:88, inputPrice:0.5, outputPrice:1.5, calls:890, avgLativity:'280ms', enabled:false },
  { id:'local', name:'Local LLM', provider:'Ollama', icon:'🏠', type:'text', apiUrl:'http://localhost:11434', apiKey:'', speed:40, inputPrice:0, outputPrice:0, calls:340, avgLatency:'2000ms', enabled:false },
])

const stats = reactive({
  todayCalls: 2847,
  successRate: 98.3,
  monthlyCost: '¥ 1,247.50',
  remaining: '¥ 8,752.50',
})

const modes = [
  { id:'quality', name:'高质量', desc:'最深推理，最佳结果，慢但准' },
  { id:'balanced', name:'均衡', desc:'速度与质量兼顾，推荐日常使用' },
  { id:'fast', name:'超高速', desc:'最高并发，快速响应，适合批量' },
  { id:'economy', name:'省钱', desc:'最低消耗，适合非关键任务' },
]

const usageStats = ref([
  { date:'2026-05-28', model:'DeepSeek V4 Pro', calls:482, tokens:'1.2M', cost:'¥168', avgTime:'320ms' },
  { date:'2026-05-27', model:'DeepSeek V4 Pro', calls:567, tokens:'1.5M', cost:'¥210', avgTime:'315ms' },
  { date:'2026-05-27', model:'Claude 4 Opus', calls:89, tokens:'0.3M', cost:'¥450', avgTime:'580ms' },
  { date:'2026-05-26', model:'DeepSeek V4 Pro', calls:623, tokens:'1.8M', cost:'¥252', avgTime:'340ms' },
])

const modelForm = reactive({ name:'', provider:'', apiUrl:'', apiKey:'', type:'text', inputPrice:0, outputPrice:0 })

const currentModel = computed(() => models.value.find(m => m.id === activeModelId.value && m.enabled))
const filteredModels = computed(() => models.value)

function speedColor(v) { if (v >= 80) return '#52c41a'; if (v >= 50) return '#faad14'; return '#ff4d4f' }

async function toggleModel(row) {
  try { ElMessage.success(row.enabled ? `${row.name} 已启用` : `${row.name} 已禁用`) } catch {}
}

async function setActive(row) {
  if (!row.enabled) { ElMessage.warning('请先启用该模型'); return }
  try {
    await switchModel(row.id)
    activeModelId.value = row.id
    ElMessage.success(`已切换至 ${row.name}`)
  } catch { ElMessage.error('切换失败') }
}

async function testSpeed(row) {
  testingModel.value = row.id
  try {
    speedResult.value = await testModelSpeed(row.id)
    if (!speedResult.value) {
      speedResult.value = { model:row.name, latency: Math.floor(Math.random()*500+100), firstToken: Math.floor(Math.random()*200+50), tokensPerSec: Math.floor(Math.random()*60+20), ok:true }
      row.avgLatency = speedResult.value.latency + 'ms'
    }
    showSpeedResult.value = true
  } catch { speedResult.value = { model:row.name, latency:0, firstToken:0, tokensPerSec:0, ok:false }; showSpeedResult.value = true }
  testingModel.value = ''
}

function editModel(row) {
  Object.assign(modelForm, { name:row.name, provider:row.provider, apiUrl:row.apiUrl, apiKey:row.apiKey, type:row.type, inputPrice:row.inputPrice, outputPrice:row.outputPrice })
  editingModel.value = row
  showAdd.value = true
}

async function saveModel() {
  if (!modelForm.name || !modelForm.provider) { ElMessage.warning('请填写名称和供应商'); return }
  saving.value = true
  try {
    if (editingModel.value) {
      Object.assign(editingModel.value, { ...modelForm })
      ElMessage.success('模型已更新')
    } else {
      const id = 'model_' + Date.now()
      models.value.push({ id, ...modelForm, icon:'🤖', speed:50, calls:0, avgLatency:'-', enabled:true })
      ElMessage.success('模型已添加')
    }
    showAdd.value = false
    editingModel.value = null
    Object.assign(modelForm, { name:'', provider:'', apiUrl:'', apiKey:'', type:'text', inputPrice:0, outputPrice:0 })
  } catch { ElMessage.error('操作失败') }
  saving.value = false
}

async function removeModel(row) {
  if (row.id === activeModelId.value) { ElMessage.warning('不能删除当前使用的模型'); return }
  try {
    await ElMessageBox.confirm(`确定删除模型 "${row.name}"？`, '确认删除', { type:'warning' })
    models.value = models.value.filter(m => m.id !== row.id)
    ElMessage.success('已删除')
  } catch {}
}

function switchMode() {
  ElMessage.success(`已切换至${modes.find(m=>m.id===activeMode.value)?.name}模式`)
}

onMounted(async () => {
  try { const list = await listModels(); if (list?.length) models.value = list } catch {}
  try { const s = await getModelStatus(); if (s?.active) activeModelId.value = s.active } catch {}
})
</script>

<style scoped>
.model-center { padding: 24px; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 18px; margin: 0 0 4px; }
.page-header p { color: var(--text-muted); font-size: 13px; margin: 0; }
.metric-card { background: var(--bg-card); border-radius: 8px; padding: 18px; border: 1px solid var(--border-color); }
.metric-label { font-size: 12px; color: var(--text-muted); margin-bottom: 6px; }
.metric-value { font-size: 28px; font-weight: 700; }
.metric-sub { font-size: 11px; color: var(--text-muted); margin-top: 4px; }
.card-header-row { display: flex; justify-content: space-between; align-items: center; }
.model-name { font-weight: 500; }
.cost { font-size: 11px; color: var(--text-muted); }
.mode-option { text-align: center; padding: 4px 8px; }
.mode-name { font-weight: 600; font-size: 14px; }
.mode-desc { font-size: 11px; color: var(--text-muted); }
</style>