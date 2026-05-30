<template>
  <div class="page-container model-center">
    <div class="page-header">
      -
      <p>?   </p>
    </div>

    
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6">
        <div class="metric-card">-<div class="metric-value">{{ models.length }}</div><div class="metric-sub">?{{ providers.length }} ?/div></div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">-<div class="metric-value" style="color:#52c41a">{{ currentModel?.name || '-' }}</div><div class="metric-sub">{{ currentModel?.provider || '' }}</div></div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card"><div class="metric-label">{{ \('model.title') }}</div><div class="metric-value">{{ stats.todayCalls }}</div><div class="metric-sub">?{{ stats.successRate }}%</div></div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card"><div class="metric-label">?/div><div class="metric-value" style="color:#faad14">{{ stats.monthlyCost }}</div><div class="metric-sub"> {{ stats.remaining }}</div></div>
      </el-col>
    </el-row>

    
    <el-card shadow="never">
      <template #header>
        <div class="card-header-row">-<el-button type="primary" size="small" @click="showAdd = true"></el-button></div>
      </template>
      <el-table :data="filteredModels" stripe>
        <el-table-column prop="name" :label="\('model.title')" min-width="160">
          <template #default="{row}"><span class="model-name">{{ row.icon }} {{ row.name }}</span></template>
        </el-table-column>
        <el-table-column prop="provider" label="? width="120"><template #default="{row}"><el-tag size="small">{{ row.provider }}</el-tag></template></el-table-column>
        <el-table-column prop="type" label='' width="100"><template #default="{row}"><el-tag :type="row.type==='text'?'':'warning'' size="small">{{ row.type==='text'?'':'? }}</el-tag></template></el-table-column>
        <el-table-column label='' width="120"><template #default="{row}"><el-progress :percentage="row.speed" :stroke-width="6" :color="speedColor(row.speed)" /></template></el-table-column>
        <el-table-column label='' width="140"><template #default="{row}"><span class="cost"> {{ row.inputPrice }} /  {{ row.outputPrice }}</span></template></el-table-column>
        <el-table-column prop="calls" :label="\('model.title')" width="100" sortable />
        <el-table-column prop="avgLatency" label='' width="100" />
        <el-table-column label="? width="100">
          <template #default="{row}">
            <el-switch v-model="row.enabled" @change="toggleModel(row)" size="small" />
            -
          </template>
        </el-table-column>
        <el-table-column label='' width="200" fixed="right">
          <template #default="{row}">
            <el-button link type="primary" size="small" @click="testSpeed(row)">?/el-button>
            <el-button link type="primary" size="small" @click="setActive(row)" v-if="row.id!==activeModelId">OK</el-button>
            <el-button link type="primary" size="small" @click="editModel(row)">OK</el-button>
            <el-button link type="danger" size="small" @click="removeModel(row)">OK</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    
    <el-card shadow="never" style="margin-top:16px">
      <template #header>-</template>
      <el-radio-group v-model="activeMode" size="large" @change="switchMode">
        <el-radio-button v-for="m in modes" :key="m.id" :value="m.id">
          <div class="mode-option"><div class="mode-name">{{ m.name }}</div><div class="mode-desc">{{ m.desc }}</div></div>
        </el-radio-button>
      </el-radio-group>
    </el-card>

    
    <el-card shadow="never" style="margin-top:16px">
      <template #header>-</template>
      <el-table :data="usageStats" stripe>
        <el-table-column prop="date" :label="\('model.title')" width="120" />
        <el-table-column prop="model" :label="\('model.title')" width="140" />
        <el-table-column prop="calls" :label="\('model.title')" width="100" sortable />
        <el-table-column prop="tokens" label="Token? width="120" sortable />
        <el-table-column prop="cost" label="()" width="100" sortable />
        <el-table-column prop="avgTime" label='' width="100" />
      </el-table>
    </el-card>

    <!-- /?-->
    <el-dialog v-model="showAdd" :title="editingModel?'':''' width="520px">
      <el-form :model="modelForm" label-width="90px">
        <el-form-item :label="\('model.title')"><el-input v-model="modelForm.name" placeholder="?DeepSeek V4" /></el-form-item>
        <el-form-item label="?><el-select v-model="modelForm.provider" style="width:100%"><el-option v-for="p in providers" :key="p" :label="p" :value="p" /></el-select></el-form-item>
        <el-form-item label="API"><el-input v-model="modelForm.apiUrl" placeholder="https://api.example.com/v1" /></el-form-item>
        <el-form-item label="API"><el-input v-model="modelForm.apiKey" type="password" show-password placeholder="sk-..." /></el-form-item>
        <el-form-item label=''><el-radio-group v-model="modelForm.type"><el-radio value="text">?/el-radio><el-radio value="multimodal">?/el-radio></el-radio-group></el-form-item>
        <el-form-item label=''><el-input-number v-model="modelForm.inputPrice" :min="0" :precision="2" :step="0.01" /> <span style="margin-left:4px">?1K tokens</span></el-form-item>
        <el-form-item label=''><el-input-number v-model="modelForm.outputPrice" :min="0" :precision="2" :step="0.01" /> <span style="margin-left:4px">?1K tokens</span></el-form-item>
      </el-form>
      <template #footer><el-button @click="showAdd=false">OK</el-button><el-button type="primary" @click="saveModel" :loading="saving">{{editingModel?'':''}}</el-button></template>
    </el-dialog>

    <!-- ?-->
    <el-dialog v-model="showSpeedResult" title="? width="400px">
      <el-descriptions :column="1" border v-if="speedResult">
        <el-descriptions-item :label="\('model.title')">{{ speedResult.model }}</el-descriptions-item>
        <el-descriptions-item label=''>{{ speedResult.latency }}ms</el-descriptions-item>
        <el-descriptions-item label="oken">{{ speedResult.firstToken }}ms</el-descriptions-item>
        <el-descriptions-item label="Token/?>{{ speedResult.tokensPerSec }}</el-descriptions-item>
        <el-descriptions-item label="?>{{ speedResult.ok ? '?' : '?' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer><el-button @click="showSpeedResult=false">OK</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listModels, switchModel, getModelStatus, testModelSpeed, compareModels } from '@/api/model'

const activeModelId = ref('')
const activeMode = ref('quality')
const showAdd = ref(false)
const showSpeedResult = ref(false)
const editingModel = ref(null)
const saving = ref(false)
const speedResult = ref(null)
const testingModel = ref('')
const loading = ref(true)

const providers = ['DeepSeek', 'OpenAI', 'Anthropic', 'Google', 'Ollama', 'OpenRouter', '?]

const models = ref([])

const stats = reactive({
  todayCalls: 0,
  successRate: 0,
  monthlyCost: ' 0',
  remaining: ' 0',
})

const modes = [
  { id:'quality', name:'?, desc:'? },
  { id:'balanced', name:'', desc:'' },
  { id:'fast', name:'?, desc:'' },
  { id:'economy', name:'', desc:'? },
]

const usageStats = ref([])

const modelForm = reactive({ name:'', provider:'', apiUrl:'', apiKey:'', type:'text', inputPrice:0, outputPrice:0 })

const currentModel = computed(() => models.value.find(m => m.id === activeModelId.value && m.enabled))
const filteredModels = computed(() => models.value)

function speedColor(v) { if (v >= 80) return '#52c41a'; if (v >= 50) return '#faad14'; return '#ff4d4f' }

async function toggleModel(row) {
  try {
    row.enabled = !row.enabled
    ElMessage.success(row.enabled ? `${row.name}  : `${row.name} )
  } catch {}
}

async function setActive(row) {
  if (!row.enabled) { ElMessage.warning('?); return }
  try {
    const res = await switchModel(row.id)
    if (res?.ok) {
      activeModelId.value = row.id
      ElMessage.success(` ${row.name}`)
    }
  } catch { ElMessage.error('Error') }
}

async function testSpeed(row) {
  testingModel.value = row.id
  showSpeedResult.value = true
  speedResult.value = { model:row.name, latency:0, firstToken:0, tokensPerSec:0, ok:false, loading: true }
  try {
    const res = await testModelSpeed(row.id)
    speedResult.value = {
      model: row.name,
      latency: res?.latency_ms || 0,
      firstToken: Math.floor((res?.latency_ms || 500) * 0.3),
      tokensPerSec: res?.latency_ms ? Math.floor(60000 / res.latency_ms) : 0,
      ok: res?.ok !== false,
    }
    if (res?.latency_ms) row.avgLatency = res.latency_ms + 'ms'
  } catch {
    speedResult.value = { model:row.name, latency:0, firstToken:0, tokensPerSec:0, ok:false }
  }
  speedResult.value.loading = false
  testingModel.value = ''
}

function editModel(row) {
  Object.assign(modelForm, { name:row.name, provider:row.provider, apiUrl:row.apiUrl, apiKey:row.apiKey, type:row.type, inputPrice:row.inputPrice, outputPrice:row.outputPrice })
  editingModel.value = row
  showAdd.value = true
}

async function saveModel() {
  if (!modelForm.name || !modelForm.provider) { ElMessage.warning('?); return }
  saving.value = true
  try {
    if (editingModel.value) {
      Object.assign(editingModel.value, { ...modelForm })
      ElMessage.success('?)
    } else {
      const id = 'model_' + Date.now()
      models.value.push({ id, ...modelForm, icon:'', speed:50, calls:0, avgLatency:'-', enabled:true })
      ElMessage.success('?)
    }
    showAdd.value = false
    editingModel.value = null
    Object.assign(modelForm, { name:'', provider:'', apiUrl:'', apiKey:'', type:'text', inputPrice:0, outputPrice:0 })
  } catch { ElMessage.error('Error') }
  saving.value = false
}

async function removeModel(row) {
  if (row.id === activeModelId.value) { ElMessage.warning('?); return }
  try {
    await ElMessageBox.confirm(` "${row.name}", '', { type:'warning' })
    models.value = models.value.filter(m => m.id !== row.id)
    ElMessage.success('?)
  } catch {}
}

function switchMode() {
  ElMessage.success(`${modes.find(m=>m.id===activeMode.value)?.name}`)
}

async function fetchModels() {
  loading.value = true
  try {
    const list = await listModels()
    if (list?.models) {
      models.value = list.models.map(m => ({
        id: m.id || m.model_id,
        name: m.name || m.model_id || '',
        provider: m.provider || '',
        icon: m.icon || '',
        type: m.type || 'text',
        apiUrl: m.api_url || '',
        apiKey: '',
        speed: m.speed || 50,
        inputPrice: m.input_price || 0,
        outputPrice: m.output_price || 0,
        calls: m.calls || 0,
        avgLatency: m.avg_latency || '-',
        enabled: m.enabled !== false,
      }))
    }
    const status = await getModelStatus()
    if (status?.current) activeModelId.value = status.current
    else if (models.value.length > 0) activeModelId.value = models.value[0].id
  } catch {
    // ?
    models.value = []
  }
  loading.value = false
}

onMounted(fetchModels)

</script>

<style scoped>
.model-center { padding: 24px; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 18px; margin: 0 0 4px; }
.page-header p { color: var(--text-muted); font-size: 13px; margin: 0; }
.metric-card { background: rgba(22,33,62,0.7); border-radius: 8px; padding: 18px; border: 1px solid var(--border-color); }
.metric-label { font-size: 12px; color: var(--text-muted); margin-bottom: 6px; }
.metric-value { font-size: 28px; font-weight: 700; }
.metric-sub { font-size: 11px; color: var(--text-muted); margin-top: 4px; }
.card-header-row { display: flex; justify-content: space-between; align-items: center; }
.model-name { font-weight: 500; }
.cost { font-size: 11px; color: var(--text-muted); }
.mode-option { text-align: center; padding: 4px 8px; }
.mode-name { font-weight: 600; font-size: 14px; }
.mode-desc { font-size: 11px; color: var(--text-muted); }
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>
