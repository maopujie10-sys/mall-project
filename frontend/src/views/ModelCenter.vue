<template>
  <div class="page-container model-center">
    <div class="page-header">
      <h2>妯″瀷涓績</h2>
      <p>澶氭ā鍨嬬鐞?路 鏅鸿兘鍒囨崲 路 浣跨敤缁熻</p>
    </div>

    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6">
        <div class="metric-card"><div class="metric-label">鍙敤妯″瀷</div><div class="metric-value">{{ models.length }}</div><div class="metric-sub">璺?{{ providers.length }} 涓钩鍙?/div></div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card"><div class="metric-label">褰撳墠妯″瀷</div><div class="metric-value" style="color:#52c41a">{{ currentModel?.name || '-' }}</div><div class="metric-sub">{{ currentModel?.provider || '' }}</div></div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card"><div class="metric-label">浠婃棩璋冪敤</div><div class="metric-value">{{ stats.todayCalls }}</div><div class="metric-sub">鎴愬姛鐜?{{ stats.successRate }}%</div></div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card"><div class="metric-label">鏈湀娑堣€?/div><div class="metric-value" style="color:#faad14">{{ stats.monthlyCost }}</div><div class="metric-sub">鍓╀綑棰濆害 {{ stats.remaining }}</div></div>
      </el-col>
    </el-row>

    <el-card shadow="never">
      <template #header>
        <div class="card-header-row"><span>妯″瀷鍒楄〃</span><el-button type="primary" size="small" @click="showAdd = true">娣诲姞妯″瀷</el-button></div>
      </template>
      <el-table :data="filteredModels" stripe>
        <el-table-column prop="name" label="妯″瀷鍚嶇О" min-width="160">
          <template #default="{row}"><span class="model-name">{{ row.icon }} {{ row.name }}</span></template>
        </el-table-column>
        <el-table-column prop="provider" label="渚涘簲鍟? width="120"><template #default="{row}"><el-tag size="small">{{ row.provider }}</el-tag></template></el-table-column>
        <el-table-column prop="type" label="绫诲瀷" width="100"><template #default="{row}"><el-tag :type="row.type==='text'?'':'warning'" size="small">{{ row.type==='text'?'鏂囨湰':'澶氭ā鎬? }}</el-tag></template></el-table-column>
        <el-table-column label="閫熷害" width="120"><template #default="{row}"><el-progress :percentage="row.speed" :stroke-width="6" :color="speedColor(row.speed)" /></template></el-table-column>
        <el-table-column label="浠锋牸" width="140"><template #default="{row}"><span class="cost">杈撳叆 楼{{ row.inputPrice }} / 杈撳嚭 楼{{ row.outputPrice }}</span></template></el-table-column>
        <el-table-column prop="calls" label="璋冪敤娆℃暟" width="100" sortable />
        <el-table-column prop="avgLatency" label="骞冲潎寤惰繜" width="100" />
        <el-table-column label="鐘舵€? width="100">
          <template #default="{row}">
            <el-switch v-model="row.enabled" @change="toggleModel(row)" size="small" />
            <el-tag v-if="row.id===activeModelId" type="success" size="small" style="margin-left:6px">褰撳墠</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="鎿嶄綔" width="200" fixed="right">
          <template #default="{row}">
            <el-button link type="primary" size="small" @click="testSpeed(row)">娴嬮€?/el-button>
            <el-button link type="primary" size="small" @click="setActive(row)" v-if="row.id!==activeModelId">鍒囨崲</el-button>
            <el-button link type="primary" size="small" @click="editModel(row)">缂栬緫</el-button>
            <el-button link type="danger" size="small" @click="removeModel(row)">鍒犻櫎</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card shadow="never" style="margin-top:16px">
      <template #header><span>鎺ㄧ悊妯″紡</span></template>
      <el-radio-group v-model="activeMode" size="large" @change="switchMode">
        <el-radio-button v-for="m in modes" :key="m.id" :value="m.id">
          <div class="mode-option"><div class="mode-name">{{ m.name }}</div><div class="mode-desc">{{ m.desc }}</div></div>
        </el-radio-button>
      </el-radio-group>
    </el-card>

    <el-card shadow="never" style="margin-top:16px">
      <template #header><span>浣跨敤缁熻</span></template>
      <el-table :data="usageStats" stripe>
        <el-table-column prop="date" label="鏃ユ湡" width="120" />
        <el-table-column prop="model" label="妯″瀷" width="140" />
        <el-table-column prop="calls" label="璋冪敤娆℃暟" width="100" sortable />
        <el-table-column prop="tokens" label="Token娑堣€? width="120" sortable />
        <el-table-column prop="cost" label="璐圭敤(楼)" width="100" sortable />
        <el-table-column prop="avgTime" label="骞冲潎鍝嶅簲" width="100" />
      </el-table>
    </el-card>

    <el-dialog v-model="showSpeedResult" title="娴嬮€熺粨鏋? width="420px">
      <template v-if="speedResult?.ok">
        <div class="speed-item">鈴?鍝嶅簲寤惰繜: <b>{{ speedResult.latency }}ms</b></div>
        <div class="speed-item">馃殌 棣朤oken: <b>{{ speedResult.firstToken }}ms</b></div>
        <div class="speed-item">馃搳 Token/绉? <b>{{ speedResult.tokensPerSec }}</b></div>
      </template>
      <template v-else>
        <el-empty description="娴嬮€熷け璐ワ紝璇锋鏌ユā鍨嬮厤缃? />
      </template>
    </el-dialog>

    <el-dialog v-model="showAdd" :title="editingModel ? '缂栬緫妯″瀷' : '娣诲姞妯″瀷'" width="500px">
      <el-form :model="modelForm" label-width="80px">
        <el-form-item label="鍚嶇О"><el-input v-model="modelForm.name" /></el-form-item>
        <el-form-item label="渚涘簲鍟?><el-select v-model="modelForm.provider"><el-option v-for="p in providers" :key="p" :label="p" :value="p" /></el-select></el-form-item>
        <el-form-item label="API鍦板潃"><el-input v-model="modelForm.apiUrl" /></el-form-item>
        <el-form-item label="API Key"><el-input v-model="modelForm.apiKey" type="password" /></el-form-item>
        <el-form-item label="绫诲瀷"><el-select v-model="modelForm.type"><el-option label="鏂囨湰" value="text" /><el-option label="澶氭ā鎬? value="multimodal" /></el-select></el-form-item>
        <el-form-item label="杈撳叆浠锋牸"><el-input-number v-model="modelForm.inputPrice" :min="0" :step="0.01" /></el-form-item>
        <el-form-item label="杈撳嚭浠锋牸"><el-input-number v-model="modelForm.outputPrice" :min="0" :step="0.01" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdd = false">鍙栨秷</el-button>
        <el-button type="primary" :loading="saving" @click="saveModel">淇濆瓨</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listModels, routeModel, testModelSpeed } from '@/api/model'

const models = ref([])
const activeModelId = ref('')
const activeMode = ref('quality')
const testingModel = ref('')
const speedResult = ref(null)
const showSpeedResult = ref(false)
const showAdd = ref(false)
const saving = ref(false)
const editingModel = ref(null)

const stats = reactive({ todayCalls: 0, successRate: 100, monthlyCost: '楼0', remaining: '楼500' })
const providers = ['OpenAI', 'Claude', 'DeepSeek', 'Gemini', 'Qwen', 'Groq']

const modes = [
  { id:'quality', name:'楂樿川閲?, desc:'鏈€娣辨帹鐞嗭紝鏈€浣崇粨鏋滐紝鎱絾鍑? },
  { id:'balanced', name:'鍧囪　', desc:'閫熷害涓庤川閲忓吋椤撅紝鎺ㄨ崘鏃ュ父浣跨敤' },
  { id:'fast', name:'瓒呴珮閫?, desc:'鏈€楂樺苟鍙戯紝蹇€熷搷搴旓紝閫傚悎鎵归噺' },
  { id:'economy', name:'鐪侀挶', desc:'鏈€浣庢秷鑰楋紝閫傚悎闈炲叧閿换鍔? },
]

const usageStats = ref([])

const modelForm = reactive({ name:'', provider:'', apiUrl:'', apiKey:'', type:'text', inputPrice:0, outputPrice:0 })

const currentModel = computed(() => models.value.find(m => m.id === activeModelId.value && m.enabled))
const filteredModels = computed(() => models.value)

function speedColor(v) { if (v >= 80) return '#52c41a'; if (v >= 50) return '#faad14'; return '#ff4d4f' }

async function toggleModel(row) {
  try { ElMessage.success(row.enabled ? `${row.name} 宸插惎鐢╜ : `${row.name} 宸茬鐢╜) } catch {}
}

async function setActive(row) {
  if (!row.enabled) { ElMessage.warning('璇峰厛鍚敤璇ユā鍨?); return }
  try {
    await switchModel(row.id)
    activeModelId.value = row.id
    ElMessage.success(`宸插垏鎹㈣嚦 ${row.name}`)
  } catch { ElMessage.error('鍒囨崲澶辫触') }
}

async function testSpeed(row) {
  testingModel.value = row.id
  try {
    const result = await testModelSpeed(row.id)
    if (result?.ok !== false) {
      speedResult.value = result
      row.avgLatency = (result?.latency || '?') + 'ms'
    } else {
      speedResult.value = { ok: false }
    }
    showSpeedResult.value = true
  } catch {
    speedResult.value = { ok: false }
    showSpeedResult.value = true
  }
  testingModel.value = ''
}

function editModel(row) {
  Object.assign(modelForm, { name:row.name, provider:row.provider, apiUrl:row.apiUrl, apiKey:row.apiKey, type:row.type, inputPrice:row.inputPrice, outputPrice:row.outputPrice })
  editingModel.value = row
  showAdd.value = true
}

async function saveModel() {
  if (!modelForm.name || !modelForm.provider) { ElMessage.warning('璇峰～鍐欏悕绉板拰渚涘簲鍟?); return }
  saving.value = true
  try {
    if (editingModel.value) {
      Object.assign(editingModel.value, { ...modelForm })
      ElMessage.success('妯″瀷宸叉洿鏂?)
    } else {
      const id = 'model_' + Date.now()
      models.value.push({ id, ...modelForm, icon:'馃', speed:50, calls:0, avgLatency:'-', enabled:true })
      ElMessage.success('妯″瀷宸叉坊鍔?)
    }
    showAdd.value = false
    editingModel.value = null
    Object.assign(modelForm, { name:'', provider:'', apiUrl:'', apiKey:'', type:'text', inputPrice:0, outputPrice:0 })
  } catch { ElMessage.error('鎿嶄綔澶辫触') }
  saving.value = false
}

async function removeModel(row) {
  if (row.id === activeModelId.value) { ElMessage.warning('涓嶈兘鍒犻櫎褰撳墠浣跨敤鐨勬ā鍨?); return }
  try {
    await ElMessageBox.confirm(`纭畾鍒犻櫎妯″瀷 "${row.name}"锛焋, '纭鍒犻櫎', { type:'warning' })
    models.value = models.value.filter(m => m.id !== row.id)
    ElMessage.success('宸插垹闄?)
  } catch {}
}

async function switchMode() {
  try {
    const result = await routeModel(activeMode.value)
    if (result?.model) {
      ElMessage.success(`宸插垏鎹㈣嚦 ${result.model} (${activeMode.value} 妯″紡)`)
    }
  } catch {
    ElMessage.success(`宸插垏鎹㈣嚦${modes.find(m=>m.id===activeMode.value)?.name}妯″紡`)
  }
}

onMounted(async () => {
  try {
    const resp = await listModels()
    if (resp?.models) models.value = resp.models
  } catch {}
  try {
    const resp = await routeModel('quality')
    if (resp?.model) {
      const found = models.value.find(m => m.name === resp.model)
      if (found) activeModelId.value = found.id
    }
  } catch {}
  try {
    const resp = await getModelStats()
    if (resp?.usage) usageStats.value = resp.usage
  } catch {}
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
.speed-item { padding: 10px 0; font-size: 15px; border-bottom: 1px solid var(--border-color); }
.speed-item:last-child { border-bottom: none; }
.speed-item b { color: var(--color-primary); }
</style>