<template>
  <div class="mp-shell">
    <div class="mp-header">
      <h2>Multi-Platform Publisher</h2>
      <p>Publish short videos to TikTok, YouTube Shorts, Instagram Reels & more</p>
    </div>
    
    <el-row :gutter="16">
      <el-col :xs="24" :md="16">
        <!-- Video Upload -->
        <el-card style="margin-bottom:12px">
          <template #header>Upload Video</template>
          <div v-if="!videoFile && !videoUrl" class="mp-upload-zone" @click="$refs.fileInput.click()">
            <span style="font-size:40px">+</span>
            <p>Click to upload or drag video here</p>
            <p style="font-size:11px;color:rgba(255,255,255,.3)">MP4, MOV, AVI — max 500MB</p>
          </div>
          <div v-else class="mp-preview">
            <video :src="videoPreviewUrl" controls style="width:100%;max-height:300px;border-radius:8px"/>
            <el-button size="small" @click="videoFile=null;videoUrl=''" style="margin-top:8px">Remove</el-button>
          </div>
          <input ref="fileInput" type="file" accept="video/*" @change="onVideoFile" style="display:none"/>
        </el-card>
        
        <!-- Video Info -->
        <el-card style="margin-bottom:12px">
          <template #header>Video Info</template>
          <el-form label-position="top">
            <el-form-item label="Title">
              <el-input v-model="form.title" placeholder="Enter video title..." maxlength="150" show-word-limit/>
            </el-form-item>
            <el-form-item label="Description">
              <el-input v-model="form.description" type="textarea" :rows="3" placeholder="Video description with hashtags..." maxlength="2200" show-word-limit/>
            </el-form-item>
            <el-form-item label="Tags">
              <el-input v-model="form.tags" placeholder="tag1, tag2, tag3"/>
            </el-form-item>
            <el-form-item label="Schedule (optional)">
              <el-date-picker v-model="form.schedule" type="datetime" placeholder="Publish later?" style="width:100%"/>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :md="8">
        <!-- Platforms -->
        <el-card style="margin-bottom:12px">
          <template #header>Target Platforms</template>
          <el-checkbox-group v-model="targetPlatforms">
            <el-checkbox v-for="p in platforms" :key="p.id" :label="p.id" border style="width:100%;margin-bottom:8px;padding:10px">
              <span style="font-size:18px;margin-right:8px">{{ p.icon }}</span>
              <span>{{ p.name }}</span>
              <el-tag size="small" :type="p.status==='connected'?'success':'info'" style="margin-left:8px">{{ p.status==='connected'?'Ready':'Setup' }}</el-tag>
            </el-checkbox>
          </el-checkbox-group>
        </el-card>
        
        <!-- AI Enhance -->
        <el-card style="margin-bottom:12px">
          <template #header>AI Enhance</template>
          <el-checkbox v-model="aiOptimize" border style="width:100%;margin-bottom:8px">Auto-optimize title & description</el-checkbox>
          <el-checkbox v-model="aiHashtags" border style="width:100%;margin-bottom:8px">Generate trending hashtags</el-checkbox>
          <el-checkbox v-model="aiSchedule" border style="width:100%">Smart schedule (best posting time)</el-checkbox>
        </el-card>
        
        <!-- Publish Button -->
        <el-button type="primary" @click="doPublish" :loading="publishing" style="width:100%;height:48px;font-size:16px" :disabled="!videoFile&&!videoUrl">
          {{ form.schedule ? 'Schedule Publish' : 'Publish Now' }}
        </el-button>
      </el-col>
    </el-row>
    
    <!-- Results -->
    <el-card v-if="results.length" style="margin-top:16px">
      <template #header>Publish Results</template>
      <el-table :data="results" size="small" stripe>
        <el-table-column prop="platform" label="Platform" width="150"/>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{row}">
            <el-tag :type="row.status==='published'?'success':row.status==='scheduled'?'warning':'danger'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="url" label="Link" min-width="200">
          <template #default="{row}">
            <a v-if="row.url" :href="row.url" target="_blank" style="color:#667eea">{{ row.url }}</a>
            <span v-else style="color:rgba(255,255,255,.3)">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="Note" min-width="150"/>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from "vue"; import { ElMessage } from "element-plus"; import { agentApi } from "@/api"

const videoFile = ref(null); const videoUrl = ref(''); const videoPreviewUrl = ref('')
const form = ref({ title: '', description: '', tags: '', schedule: null })
const targetPlatforms = ref(['tiktok', 'youtube'])
const aiOptimize = ref(true); const aiHashtags = ref(true); const aiSchedule = ref(false)
const publishing = ref(false); const results = ref([])

const platforms = ref([
  { id: 'tiktok', name: 'TikTok', icon: '🎵', status: 'connected' },
  { id: 'youtube', name: 'YouTube Shorts', icon: '▶️', status: 'connected' },
  { id: 'instagram', name: 'Instagram Reels', icon: '📷', status: 'setup' },
  { id: 'facebook', name: 'Facebook Reels', icon: '📘', status: 'setup' },
  { id: 'snapchat', name: 'Snapchat Spotlight', icon: '👻', status: 'setup' },
  { id: 'xiaohongshu', name: 'RED / Xiaohongshu', icon: '📕', status: 'setup' },
  { id: 'kuaishou', name: 'Kuaishou', icon: '⚡', status: 'setup' },
  { id: 'bilibili', name: 'Bilibili', icon: '📺', status: 'setup' },
])

function onVideoFile(e) {
  const f = e.target.files?.[0]
  if (!f) return
  videoFile.value = f
  videoPreviewUrl.value = URL.createObjectURL(f)
  if (!form.value.title) form.value.title = f.name.replace(/\.[^.]+$/, '')
}

async function doPublish() {
  if (!targetPlatforms.value.length) return ElMessage.warning('Select at least one platform')
  if (!form.value.title) return ElMessage.warning('Enter a title')
  
  publishing.value = true; results.value = []
  try {
    const fd = new FormData()
    if (videoFile.value) fd.append('file', videoFile.value)
    else fd.append('video_url', videoUrl.value)
    fd.append('title', form.value.title)
    fd.append('description', form.value.description)
    fd.append('tags', form.value.tags)
    fd.append('platforms', JSON.stringify(targetPlatforms.value))
    fd.append('ai_optimize', String(aiOptimize.value))
    fd.append('ai_hashtags', String(aiHashtags.value))
    if (form.value.schedule) fd.append('schedule', form.value.schedule.toISOString())
    
    const r = await agentApi.post("/agent/media/publish", fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    if (r?.data?.ok) {
      results.value = r.data.results || []
      const published = results.value.filter(x => x.status === 'published').length
      const scheduled = results.value.filter(x => x.status === 'scheduled').length
      ElMessage.success(`Published: ${published}, Scheduled: ${scheduled}`)
    } else {
      ElMessage.error(r?.data?.error || 'Publish failed')
    }
  } catch (e) { ElMessage.error(e.message) }
  publishing.value = false
}
</script>

<style scoped>
.mp-shell { max-width: 1100px; margin: 0 auto; padding: 20px; }
.mp-header { margin-bottom: 16px; }
.mp-header h2 { font-size: 22px; color: #e0e0ff; margin: 0; }
.mp-header p { font-size: 13px; color: rgba(255,255,255,0.5); margin: 4px 0 0; }
.mp-upload-zone { border: 2px dashed rgba(255,255,255,.2); border-radius: 12px; padding: 40px; text-align: center; cursor: pointer; transition: .2s; }
.mp-upload-zone:hover { border-color: #667eea; background: rgba(102,126,234,.05); }
.mp-upload-zone p { color: rgba(255,255,255,.5); margin: 4px 0 0; }
.mp-preview video { background: #000; }
@media (max-width: 768px) { .mp-shell { padding: 10px; } }
</style>