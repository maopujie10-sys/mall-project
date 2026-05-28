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
            <el-descriptions-item label="瑙嗛鏃堕暱">{{ result.duration || '-' }}</el-descriptions-item>
            <el-descriptions-item label="鍒嗚鲸鐜?>{{ result.resolution || '-' }}</el-descriptions-item>
            <el-descriptions-item label="鏂囦欢澶у皬">{{ result.fileSize || '-' }}</el-descriptions-item>
            <el-descriptions-item label="甯х巼">{{ result.fps || '-' }}</el-descriptions-item>
            <el-descriptions-item label="闊抽">{{ result.hasAudio ? '鏈夐煶棰? : '鏃犻煶棰? }}</el-descriptions-item>
            <el-descriptions-item label="璇█">{{ result.language || '-' }}</el-descriptions-item>
            <el-descriptions-item label="瑙嗛鍒嗙被" :span="2"><el-tag v-for="c in (result.categories||[])" :key="c" size="small" style="margin-right:6px">{{ c }}</el-tag></el-descriptions-item>
            <el-descriptions-item label="鍐呭鎽樿" :span="2">{{ result.summary || '-' }}</el-descriptions-item>
            <el-descriptions-item label="鐑偣娼滃姏" :span="2"><el-progress :percentage="result.hotScore||0" :color="(result.hotScore||0)>70?'#ff4d4f':(result.hotScore||0)>40?'#faad14':'#52c41a'" :stroke-width="8" /></el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card shadow="never" style="margin-top:16px" v-if="!result && !analyzing">
          <el-empty description="杈撳叆瑙嗛URL鍚庣偣鍑诲垎鏋? />
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
import { analyzeVideo as analyzeVideoApi } from '@/api/vision'

const videoUrl = ref('')
const analyzing = ref(false)
const result = ref(null)
const subtitles = ref([])
const history = ref([])

const samples = [
  { label: '鍟嗗搧灞曠ず', url: 'https://example.com/product.mp4' },
  { label: '鐩存挱鍥炴斁', url: 'https://example.com/live.mp4' },
]

async function analyze() {
  if (!videoUrl.value) { ElMessage.warning('璇疯緭鍏ヨ棰慤RL'); return }
  analyzing.value = true
  try {
    const resp = await analyzeVideoApi(videoUrl.value)
    if (resp?.ok !== false) {
      result.value = {
        duration: resp?.duration || '?',
        resolution: resp?.resolution || '?',
        fileSize: resp?.fileSize || '?',
        fps: resp?.fps || '?',
        hasAudio: resp?.hasAudio ?? false,
        language: resp?.language || '鏈煡',
        categories: resp?.categories || [],
        summary: resp?.summary || '鍒嗘瀽涓?..',
        hotScore: resp?.hotScore || 0,
      }
      if (resp?.subtitles) subtitles.value = resp.subtitles
      history.value.unshift({
        id: Date.now(),
        title: videoUrl.value.substring(0, 50),
        url: videoUrl.value,
        date: new Date().toLocaleDateString(),
      })
      ElMessage.success('瑙嗛鍒嗘瀽瀹屾垚')
    } else {
      ElMessage.error('鍒嗘瀽澶辫触锛岃妫€鏌ヨ棰戦摼鎺?)
    }
  } catch (e) {
    ElMessage.error('璇锋眰澶辫触: ' + (e.message || '鏈煡閿欒'))
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
</style>