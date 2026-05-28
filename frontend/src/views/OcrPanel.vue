<template>
  <div class="page-container ocr-panel">
    <div class="page-header"><h2>OCR 璇嗗埆</h2><p>鍥剧墖鏂囧瓧璇嗗埆 路 琛ㄦ牸鎻愬彇 路 澶氳瑷€鏀寔 路 鎵归噺澶勭悊</p></div>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header><span>鍥剧墖杈撳叆</span></template>
          <el-upload class="ocr-upload" drag :auto-upload="false" :on-change="handleFile" accept="image/*">
            <el-icon :size="48"><svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/></svg></el-icon>
            <div class="el-upload__text">鎷栨嫿鍥剧墖鎴?em>鐐瑰嚮涓婁紶</em></div>
          </el-upload>
          <div style="margin-top:12px">
            鎴栬緭鍏ュ浘鐗嘦RL锛?el-input v-model="imageUrl" placeholder="https://..." clearable style="margin-top:8px" />
          </div>
          <el-select v-model="lang" style="width:100%;margin-top:12px" placeholder="閫夋嫨璇嗗埆璇█">
            <el-option label="涓枃绠€浣? value="chi_sim" /><el-option label="涓枃绻佷綋" value="chi_tra" />
            <el-option label="鑻辨枃" value="eng" /><el-option label="鏃ユ枃" value="jpn" />
            <el-option label="闊╂枃" value="kor" /><el-option label="鑷姩妫€娴? value="auto" />
          </el-select>
          <el-button type="primary" @click="runOcr" :loading="running" style="width:100%;margin-top:12px">寮€濮嬭瘑鍒?/el-button>
        </el-card>

        <el-card shadow="never" style="margin-top:16px">
          <template #header><span>鎵归噺澶勭悊</span></template>
          <el-upload class="batch-upload" drag multiple :auto-upload="false" :on-change="handleBatch" accept="image/*">
            <div class="el-upload__text">鎷栨嫿澶氬紶鍥剧墖鎴?em>鐐瑰嚮鎵归噺涓婁紶</em></div>
          </el-upload>
          <div v-if="batchFiles.length" style="margin-top:12px">
            <el-tag v-for="f in batchFiles" :key="f.name" closable @close="batchFiles=batchFiles.filter(x=>x.name!==f.name)" size="small" style="margin-right:6px;margin-bottom:6px">{{ f.name }}</el-tag>
          </div>
          <el-button v-if="batchFiles.length" type="primary" @click="runBatch" :loading="batching" style="width:100%;margin-top:8px">鎵归噺璇嗗埆 ({{ batchFiles.length }} 寮?</el-button>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="never" v-if="ocrText">
          <template #header>
            <div class="result-header"><span>璇嗗埆缁撴灉</span><el-button link type="primary" size="small" @click="copyText">澶嶅埗</el-button><el-button link type="primary" size="small" @click="exportText">瀵煎嚭</el-button></div>
          </template>
          <pre class="ocr-result">{{ ocrText }}</pre>
          <el-divider />
          <div class="stats-row">
            <span>瀛楃鏁? {{ ocrText.length }}</span>
            <span>缃俊搴? {{ confidence }}%</span>
            <span>鑰楁椂: {{ elapsed }}ms</span>
          </div>
        </el-card>

        <el-card shadow="never" style="margin-top:16px" v-if="!ocrText">
          <el-empty description="涓婁紶鍥剧墖鎴栬緭鍏RL寮€濮嬭瘑鍒? />
        </el-card>

        <el-card shadow="never" style="margin-top:16px">
          <template #header><span>璇嗗埆鍘嗗彶</span></template>
          <el-table :data="ocrHistory" stripe size="small" max-height="300">
            <el-table-column prop="name" label="鏂囦欢" min-width="140" show-overflow-tooltip />
            <el-table-column prop="text" label="鍐呭棰勮" min-width="160" show-overflow-tooltip />
            <el-table-column prop="lang" label="璇█" width="80" />
            <el-table-column prop="date" label="鏃堕棿" width="100" />
            <el-table-column label="鎿嶄綔" width="80"><template #default="{row}"><el-button link type="primary" size="small" @click="ocrText=row.text;confidence=row.confidence">鏌ョ湅</el-button></template></el-table-column>
          </el-table>
          <el-empty v-if="!ocrHistory.length" description="鏆傛棤璁板綍" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { ocrRecognize } from '@/api/vision'

const imageUrl = ref('')
const ocrText = ref('')
const lang = ref('auto')
const running = ref(false)
const confidence = ref(0)
const elapsed = ref(0)
const batchFiles = ref([])
const batching = ref(false)
const ocrHistory = ref([])

function handleFile(file) {
  if (file?.raw) {
    const reader = new FileReader()
    reader.onload = (e) => { imageUrl.value = e.target.result }
    reader.readAsDataURL(file.raw)
  }
}

function handleBatch(file) {
  if (file?.raw) batchFiles.value.push(file.raw)
}

async function runOcr() {
  if (!imageUrl.value) { ElMessage.warning('璇峰厛涓婁紶鍥剧墖鎴栬緭鍏RL'); return }
  running.value = true
  const start = Date.now()
  try {
    const resp = await ocrRecognize(imageUrl.value)
    if (resp?.ok) {
      ocrText.value = resp.text || ''
      confidence.value = resp.confidence || 85
      elapsed.value = Date.now() - start
      ocrHistory.value.unshift({
        name: imageUrl.value.substring(0, 40),
        text: (resp.text || '').substring(0, 60),
        lang: lang.value,
        confidence: confidence.value,
        date: new Date().toLocaleDateString(),
      })
      ElMessage.success('璇嗗埆瀹屾垚')
    } else {
      ElMessage.error(resp?.error || '璇嗗埆澶辫触')
    }
  } catch (e) {
    ElMessage.error('璇嗗埆璇锋眰澶辫触: ' + (e.message || '鏈煡閿欒'))
  }
  running.value = false
}

async function runBatch() {
  if (!batchFiles.value.length) return
  batching.value = true
  let success = 0
  for (const file of batchFiles.value) {
    try {
      const reader = new FileReader()
      const dataUrl = await new Promise((resolve) => { reader.onload = (e) => resolve(e.target.result); reader.readAsDataURL(file) })
      const resp = await ocrRecognize(dataUrl)
      if (resp?.ok) success++
    } catch {}
  }
  ElMessage.success(`鎵归噺瀹屾垚: ${success}/${batchFiles.value.length} 鎴愬姛`)
  batchFiles.value = []
  batching.value = false
}

function copyText() {
  navigator.clipboard.writeText(ocrText.value)
  ElMessage.success('宸插鍒?)
}

function exportText() {
  const blob = new Blob([ocrText.value], { type: 'text/plain' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `ocr_${Date.now()}.txt`
  a.click()
}
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
</style>