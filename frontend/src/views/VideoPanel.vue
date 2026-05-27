<template>
  <div class="page-container video-panel">
    <div class="page-header"><h2>视频分析</h2><p>视频理解 · 字幕提取 · 内容分析 · 热点研判</p></div>

    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="16">
        <el-card shadow="never">
          <template #header><span>视频输入</span></template>
          <el-input v-model="videoUrl" placeholder="输入视频URL或本地路径..." clearable>
            <template #append><el-button type="primary" @click="analyze" :loading="analyzing">开始分析</el-button></template>
          </el-input>
          <div class="quick-links" style="margin-top:12px">
            <span>快捷示例：</span>
            <el-tag v-for="s in samples" :key="s.url" @click="videoUrl=s.url;analyze()" style="cursor:pointer;margin-right:8px">{{ s.label }}</el-tag>
          </div>
        </el-card>

        <el-card shadow="never" style="margin-top:16px" v-if="result">
          <template #header><span>分析结果</span></template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="视频时长">{{ result.duration || '-' }}</el-descriptions-item>
            <el-descriptions-item label="分辨率">{{ result.resolution || '-' }}</el-descriptions-item>
            <el-descriptions-item label="文件大小">{{ result.fileSize || '-' }}</el-descriptions-item>
            <el-descriptions-item label="帧率">{{ result.fps || '-' }}</el-descriptions-item>
            <el-descriptions-item label="音频">{{ result.hasAudio ? '有音频' : '无音频' }}</el-descriptions-item>
            <el-descriptions-item label="语言">{{ result.language || '-' }}</el-descriptions-item>
            <el-descriptions-item label="视频分类" :span="2"><el-tag v-for="c in (result.categories||[])" :key="c" size="small" style="margin-right:6px">{{ c }}</el-tag></el-descriptions-item>
            <el-descriptions-item label="内容摘要" :span="2">{{ result.summary || '-' }}</el-descriptions-item>
            <el-descriptions-item label="热点潜力" :span="2"><el-progress :percentage="result.hotScore||0" :color="(result.hotScore||0)>70?'#ff4d4f':(result.hotScore||0)>40?'#faad14':'#52c41a'" :stroke-width="8" /></el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card shadow="never" style="margin-top:16px" v-if="!result && !analyzing">
          <el-empty description="输入视频URL后点击分析" />
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="never">
          <template #header><span>字幕预览</span></template>
          <div v-if="subtitles.length" class="subtitle-box">
            <div v-for="s in subtitles" :key="s.time" class="sub-line">
              <span class="sub-time">{{ s.time }}</span>
              <span class="sub-text">{{ s.text }}</span>
            </div>
          </div>
          <el-empty v-else description="分析视频后自动提取" />
        </el-card>

        <el-card shadow="never" style="margin-top:16px">
          <template #header><span>分析历史</span></template>
          <div v-if="history.length" class="history-list">
            <div v-for="h in history.slice(0,8)" :key="h.id" class="history-item" @click="videoUrl=h.url;analyze()">
              <span class="hist-title">{{ h.title }}</span>
              <span class="hist-date">{{ h.date }}</span>
            </div>
          </div>
          <el-empty v-else description="暂无记录" />
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
  { label: '商品展示', url: 'https://example.com/product.mp4' },
  { label: '直播回放', url: 'https://example.com/live.mp4' },
]

async function analyze() {
  if (!videoUrl.value) { ElMessage.warning('请输入视频URL'); return }
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
        language: resp?.language || '未知',
        categories: resp?.categories || [],
        summary: resp?.summary || '分析中...',
        hotScore: resp?.hotScore || 0,
      }
      if (resp?.subtitles) subtitles.value = resp.subtitles
      history.value.unshift({
        id: Date.now(),
        title: videoUrl.value.substring(0, 50),
        url: videoUrl.value,
        date: new Date().toLocaleDateString(),
      })
      ElMessage.success('视频分析完成')
    } else {
      ElMessage.error('分析失败，请检查视频链接')
    }
  } catch (e) {
    ElMessage.error('请求失败: ' + (e.message || '未知错误'))
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