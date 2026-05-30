<template>
  <div class="page-container ocr-panel">
    <div class="page-header"><h2>OCR </h2>-</div>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header><span>{{ \('ocr.title') }}</span></template>
          <el-upload class="ocr-upload" drag :auto-upload="false" :on-change="handleFile" accept="image/*">
            <el-icon :size="48"><svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/>{{ \('ocr.title') }}</svg></el-icon>
            <div class="el-upload__text">-</div>
          </el-upload>
          <div style="margin-top:12px">
            URL<el-input v-model="imageUrl" placeholder="https://..." clearable style="margin-top:8px" />
          </div>
          <el-select v-model="lang" style="width:100%;margin-top:12px" placeholder=''>
            <el-option label='' value="chi_sim" /><el-option label='' value="chi_tra" />
            <el-option label='' value="eng" /><el-option label='' value="jpn" />
            <el-option label='' value="kor" /><el-option label='' value="auto" />
          </el-select>
          <el-button type="primary" @click="runOcr" :loading="running" style="width:100%;margin-top:12px">OK</el-button>
        </el-card>

        <el-card shadow="never" style="margin-top:16px">
          <template #header><span>{{ \('ocr.title') }}</span></template>
          <el-upload class="batch-upload" drag multiple :auto-upload="false" :on-change="handleBatch" accept="image/*">
            <div class="el-upload__text">-</div>
          </el-upload>
          <div v-if="batchFiles.length" style="margin-top:12px">
            <el-tag v-for="f in batchFiles" :key="f.name" closable @close="batchFiles=batchFiles.filter(x=>x.name!==f.name)" size="small" style="margin-right:6px;margin-bottom:6px">{{ f.name }}</el-tag>
          </div>
          <el-button v-if="batchFiles.length" type="primary" @click="runBatch" :loading="batching" style="width:100%;margin-top:8px"> ({{ batchFiles.length }} )</el-button>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="never" v-if="ocrText">
          <template #header>
            <div class="result-header"><span>{{ \('ocr.title') }}</span><el-button link type="primary" size="small" @click="copyText">OK</el-button><el-button link type="primary" size="small" @click="exportText">OK</el-button></div>
          </template>
          <pre class="ocr-result">{{ ocrText }}</pre>
          <el-divider />
          <div class="stats-row">
            <span>: {{ ocrText.length }}</span>
            <span>: {{ confidence }}%</span>
            <span>: {{ elapsed }}ms</span>
          </div>
        </el-card>

        <el-card shadow="never" style="margin-top:16px">
          <template #header><span>{{ \('ocr.title') }}</span></template>
          <el-table :data="ocrHistory" stripe size="small" max-height="300">
            <el-table-column prop="name" label='' min-width="140" show-overflow-tooltip />
            <el-table-column prop="text" label='' min-width="160" show-overflow-tooltip />
            <el-table-column prop="lang" label='' width="80" />
            <el-table-column prop="date" label='' width="100" />
            <el-table-column label='' width="80"><template #default="{row}"><el-button link type="primary" size="small" @click="ocrText=row.text;confidence=row.confidence">OK</el-button></template></el-table-column>
          </el-table>
          <el-empty v-if="!ocrHistory.length" description='' />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { agentApi } from '@/api/index'

const imageUrl = ref('')
const lang = ref('auto')
const running = ref(false)
const batching = ref(false)
const ocrText = ref('')
const confidence = ref(0)
const elapsed = ref(0)
const batchFiles = ref([])
const ocrHistory = ref([])

function handleFile(file) {
  const reader = new FileReader()
  reader.onload = (e) => { imageUrl.value = e.target.result }
  reader.readAsDataURL(file.raw)
}
function handleBatch(file) { batchFiles.value.push(file) }

async function runOcr() {
  if(!imageUrl.value) { ElMessage.warning('URL'); return }
  running.value = true; ocrText.value = ''; const start = Date.now()
  try {
    const res = await agentApi.post('/agent/vision/ocr', { image_url: imageUrl.value, lang: lang.value })
    if (res?.data?.ok) {
      ocrText.value = res.data.text || ''; confidence.value = res.data.confidence || 95
    } else { ocrText.value = 'OCR: ' + (res?.data?.error || '') }
  } catch (e) { ocrText.value = 'OCR: ' + (e.message || ''); ElMessage.error('OCR') }
  elapsed.value = Date.now() - start; running.value = false
  ocrHistory.value.unshift({ name: '', text: ocrText.value.slice(0,50), lang: lang.value, date: new Date().toLocaleDateString(), confidence: confidence.value })
}

async function runBatch() {
  if(!batchFiles.value.length) return; batching.value = true
  let results = ''; let totalConf = 0; let count = 0
  for(const f of batchFiles.value) {
    try {
      const reader = new FileReader()
      const dataUrl = await new Promise(r => { reader.onload = e => r(e.target.result); reader.readAsDataURL(f.raw) })
      const res = await agentApi.post('/agent/vision/ocr', { image_url: dataUrl, lang: lang.value })
      if(res?.data?.ok) { results += `\n--- ${f.name} ---\n${res.data.text}`; totalConf += res.data.confidence||90; count++ }
    } catch(e) { results += `\n--- ${f.name} ---\n[: ${e.message}]` }
  }
  ocrText.value = results; confidence.value = count ? Math.round(totalConf/count) : 0; batching.value = false
}

function copyText() { navigator.clipboard.writeText(ocrText.value); ElMessage.success('OK') }
function exportText() { const blob = new Blob([ocrText.value], {type:'text/plain'}); const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'ocr_result.txt'; a.click(); ElMessage.success('OK') }
</script>

<style scoped>
.ocr-panel { padding: 24px; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 18px; margin: 0 0 4px; }
.page-header p { color: var(--text-muted); font-size: 13px; margin: 0; }
.ocr-upload { width: 100%; }
.ocr-result { white-space: pre-wrap; font-size: 15px; line-height: 1.8; background: rgba(0,0,0,0.2); padding: 20px; border-radius: 8px; max-height: 400px; overflow-y: auto; }
.result-header { display: flex; justify-content: space-between; align-items: center; }
.stats-row { display: flex; justify-content: space-around; font-size: 12px; color: var(--text-muted); }
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>