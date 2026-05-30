<template>
  <div class="page-container video-panel">
    <div class="page-header"><h2>{{ \('video.title') }}</h2>-</div>
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="16">
        <el-card shadow="never">
          <template #header><span>{{ \('video.title') }}</span></template>
          <el-input v-model="videoUrl" placeholder="URL..." clearable>
            <template #append><el-button type="primary" @click="analyze" :loading="analyzing">OK</el-button></template>
          </el-input>
        </el-card>
        <el-card shadow="never" style="margin-top:16px" v-if="result">
          <template #header><span>{{ \('video.title') }}</span></template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label=''>{{ result.duration || '-' }}</el-descriptions-item>
            <el-descriptions-item label=''>{{ result.resolution || '-' }}</el-descriptions-item>
            <el-descriptions-item label=''>{{ result.fileSize || '-' }}</el-descriptions-item>
            <el-descriptions-item label=''>{{ result.fps || '-' }}</el-descriptions-item>
            <el-descriptions-item label=''>{{ result.hasAudio ? '' : '' }}</el-descriptions-item>
            <el-descriptions-item label=''>{{ result.language || '-' }}</el-descriptions-item>
            <el-descriptions-item label='' :span="2">{{ result.summary || '-' }}</el-descriptions-item>
            <el-descriptions-item label='' :span="2"><el-progress :percentage="result.hotScore||0" :color="(result.hotScore||0)>70?'#ff4d4f':(result.hotScore||0)>40?'#faad14':'#52c41a'' :stroke-width="8" /></el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <template #header><span>{{ \('video.title') }}</span></template>
          <div v-if="subtitles.length" class="subtitle-box">
            <div v-for="s in subtitles" :key="s.time" class="sub-line"><span class="sub-time">{{ s.time }}</span><span class="sub-text">{{ s.text }}</span></div>
          </div>
          <el-empty v-else description='' />
        </el-card>
        <el-card shadow="never" style="margin-top:16px">
          <template #header><span>{{ \('video.title') }}</span></template>
          <div v-if="history.length" class="history-list">
            <div v-for="h in history.slice(0,8)" :key="h.id" class="history-item" @click="videoUrl=h.url;analyze()"><span class="hist-title">{{ h.title }}</span><span class="hist-date">{{ h.date }}</span></div>
          </div>
          <el-empty v-else description='' />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script setup>
import { ref } from 'vue'; import { ElMessage } from 'element-plus'; import { agentApi } from '@/api/index'
const videoUrl = ref(''); const analyzing = ref(false); const result = ref(null)
const subtitles = ref([]); const history = ref([])
const samples = ref([{label:'1',url:''}, {label:'2',url:''}])

async function analyze() {
  if(!videoUrl.value) { ElMessage.warning('URL'); return }
  analyzing.value = true; result.value = null
  try {
    const res = await agentApi.post('/agent/video/analyze', { video_url: videoUrl.value })
    if(res?.data?.ok) { result.value = res.data; subtitles.value = res.data.subtitles || []; ElMessage.success('Analysis complete') }
    else { ElMessage.error(': ' + (res?.data?.error || '')) }
  } catch(e) { ElMessage.error(': ' + (e.message || '')) }
  analyzing.value = false
  history.value.unshift({ id: Date.now(), title: videoUrl.value.slice(0,40), date: new Date().toLocaleDateString(), url: videoUrl.value })
}
</script>
<style scoped>
.video-panel { padding: 24px; }
.page-header { margin-bottom: 24px; } .page-header h2 { font-size: 18px; margin: 0 0 4px; } .page-header p { color: var(--text-muted); font-size: 13px; margin: 0; }
.subtitle-box { max-height: 350px; overflow-y: auto; }
.sub-line { display: flex; gap: 12px; padding: 6px 0; border-bottom: 1px solid var(--border-color); } .sub-line:last-child { border: none; }
.sub-time { font-family: monospace; font-size: 11px; color: #667eea; min-width: 48px; } .sub-text { font-size: 12px; }
.history-list { max-height: 300px; overflow-y: auto; }
.history-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border-color); cursor: pointer; font-size: 12px; } .history-item:hover { color: #667eea; } .history-item:last-child { border: none; }
.hist-date { color: var(--text-muted); font-size: 11px; }
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } }
</style>