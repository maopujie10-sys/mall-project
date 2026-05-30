<template>
  <div class="page-container video-panel">
    <div class="page-header"><h2>瑙嗛鍒嗘瀽</h2><p>瑙嗛鐞嗚В 路 瀛楀箷鎻愬彇 路 鍐呭鍒嗘瀽 路 鐑偣鐮斿垽</p></div>

    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="16">
        <el-card shadow="never">
          <template #header><span>瑙嗛杈撳叆</span></template>
          <el-input v-model="videoUrl" placeholder="杈撳叆瑙嗛URL鎴栨湰鍦拌矾寰?.." clearable>
            <template #append><el-button type="primary" @click="analyze" :loading="analyzing">寮€濮嬪垎鏋?/el-button></template>
          </el-input>
          <div class="quick-links" style="margin-top:12px">
            <span>蹇嵎绀轰緥锛?/span>
            <el-tag v-for="s in samples" :key="s.url" @click="videoUrl=s.url;analyze()" style="cursor:pointer;margin-right:8px">{{ s.label }}</el-tag>
          </div>
        </el-card>

        <el-card shadow="never" style="margin-top:16px" v-if="result">
          <template #header><span>鍒嗘瀽缁撴灉</span></template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="瑙嗛鏃堕暱">{{ result.duration }}</el-descriptions-item>
            <el-descriptions-item label="鍒嗚鲸鐜?>{{ result.resolution }}</el-descriptions-item>
            <el-descriptions-item label="鏂囦欢澶у皬">{{ result.fileSize }}</el-descriptions-item>
            <el-descriptions-item label="甯х巼">{{ result.fps }}</el-descriptions-item>
            <el-descriptions-item label="闊抽">{{ result.hasAudio ? '鏈夐煶棰? : '鏃犻煶棰? }}</el-descriptions-item>
            <el-descriptions-item label="璇█">{{ result.language }}</el-descriptions-item>
            <el-descriptions-item label="瑙嗛鍒嗙被" :span="2"><el-tag v-for="c in result.categories" :key="c" size="small" style="margin-right:6px">{{ c }}</el-tag></el-descriptions-item>
            <el-descriptions-item label="鍐呭鎽樿" :span="2">{{ result.summary }}</el-descriptions-item>
            <el-descriptions-item label="鐑偣娼滃姏" :span="2"><el-progress :percentage="result.hotScore" :color="result.hotScore>70?'#ff4d4f':result.hotScore>40?'#faad14':'#52c41a'" :stroke-width="8" /></el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="never">
          <template #header><span>瀛楀箷棰勮</span></template>
          <div v-if="subtitles.length" class="subtitle-box">
            <div v-for="s in subtitles" :key="s.time" class="sub-line">
              <span class="sub-time">{{ s.time }}</span>
              <span class="sub-text">{{ s.text }}</span>
            </div>
          </div>
          <el-empty v-else description="鍒嗘瀽瑙嗛鍚庤嚜鍔ㄦ彁鍙? />
        </el-card>

        <el-card shadow="never" style="margin-top:16px">
          <template #header><span>鍒嗘瀽鍘嗗彶</span></template>
          <div v-if="history.length" class="history-list">
            <div v-for="h in history.slice(0,8)" :key="h.id" class="history-item" @click="videoUrl=h.url;analyze()">
              <span class="hist-title">{{ h.title }}</span>
              <span class="hist-date">{{ h.date }}</span>
            </div>
          </div>
          <el-empty v-else description="鏆傛棤璁板綍" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { agentApi } from '@/api/index'

const videoUrl = ref('')
const analyzing = ref(false)
const videoInfo = ref(null)

async function analyzeVideo() {
  if(!videoUrl.value) { ElMessage.warning('璇峰厛杈撳叆瑙嗛URL'); return }
  analyzing.value = true
  videoInfo.value = null
  try {
    const res = await agentApi.get('/agent/friday/vision/video', { params: { video_url: videoUrl.value } })
    if (res?.data?.ok) {
      videoInfo.value = res.data
    } else {
      ElMessage.error('瑙嗛鍒嗘瀽澶辫触: ' + (res?.data?.error || '鏈煡閿欒'))
    }
    ElMessage.success('瑙嗛鍒嗘瀽瀹屾垚')
  } catch (e) {
    ElMessage.error('瑙嗛鍒嗘瀽澶辫触: ' + (e.message || '缃戠粶閿欒'))
  }
  analyzing.value = false
}
</script>

<style scoped>
.video-panel { padding: 24px; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 18px; margin: 0 0 4px; }
.page-header p { color: var(--text-muted); font-size: 13px; margin: 0; }
.quick-links { font-size: 12px; color: var(--text-muted); }
.subtitle-box { max-height: 350px; overflow-y: auto; }
.sub-line { display: flex; gap: 12px; padding: 6px 0; border-bottom: 1px solid var(--border-color); }
.sub-line:last-child { border: none; }
.sub-time { font-family: monospace; font-size: 11px; color: #667eea; min-width: 48px; }
.sub-text { font-size: 12px; }
.history-list { max-height: 300px; overflow-y: auto; }
.history-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border-color); cursor: pointer; font-size: 12px; }
.history-item:hover { color: #667eea; }
.history-item:last-child { border: none; }
.hist-date { color: var(--text-muted); font-size: 11px; }
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>

