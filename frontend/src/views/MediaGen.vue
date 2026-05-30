<template>
  <div class="mg-shell">
    <div class="mg-header">
      <h2>AI Content Factory</h2>
      <p>Rewrite + Image + Digital Human + Video + Batch + Gallery</p>
    </div>
    
    <el-tabs v-model="tab" type="border-card">
      <!-- TAB 1: Rewrite -->
      <el-tab-pane label="Rewrite" name="rewrite">
        <el-card>
          <el-input v-model="rewrite.text" type="textarea" :rows="5" placeholder="Paste your text here..." style="margin-bottom:10px"/>
          <el-select v-model="rewrite.style" placeholder="Style" style="width:200px;margin-bottom:10px">
            <el-option v-for="s in rewriteStyles" :key="s" :label="s" :value="s"/>
          </el-select>
          <el-button type="primary" @click="doRewrite" :loading="rewrite.loading" style="display:block">Rewrite</el-button>
          <div v-if="rewrite.result" class="mg-output">{{ rewrite.result }}</div>
        </el-card>
      </el-tab-pane>
      
      <!-- TAB 2: Image Gen -->
      <el-tab-pane label="Image Gen" name="image">
        <el-card>
          <el-input v-model="image.prompt" type="textarea" :rows="3" placeholder="Describe the image you want..." style="margin-bottom:10px"/>
          <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:10px">
            <el-select v-model="image.style" placeholder="Style" style="width:160px">
              <el-option v-for="s in imgStyles" :key="s" :label="s" :value="s"/>
            </el-select>
            <el-select v-model="image.size" placeholder="Size" style="width:140px">
              <el-option label="1024x1024" value="1024x1024"/>
              <el-option label="512x512" value="512x512"/>
              <el-option label="768x1344" value="768x1344"/>
            </el-select>
          </div>
          <el-button type="primary" @click="doGenImage" :loading="image.loading">Generate Image</el-button>
          <div v-if="image.result" class="mg-output" style="text-align:center">
            <img :src="image.result" style="max-width:100%;max-height:400px;border-radius:8px"/>
          </div>
        </el-card>
      </el-tab-pane>
      
      <!-- TAB 3: Digital Human -->
      <el-tab-pane label="Digital Human" name="avatar">
        <el-card>
          <el-input v-model="avatar.text" type="textarea" :rows="3" placeholder="What should the digital human say?" style="margin-bottom:10px"/>
          <el-select v-model="avatar.voice" placeholder="Voice" style="width:200px;margin-bottom:10px">
            <el-option v-for="v in voices" :key="v.id" :label="v.name" :value="v.id"/>
          </el-select>
          <div style="margin-bottom:10px">
            <span style="color:rgba(255,255,255,.5);font-size:12px">Upload avatar image (optional):</span>
            <input type="file" accept="image/*" @change="onAvatarFile" style="display:block;margin-top:4px"/>
          </div>
          <el-button type="primary" @click="doGenAvatar" :loading="avatar.loading">Generate Digital Human Video</el-button>
          <div v-if="avatar.result" class="mg-output" style="text-align:center">
            <video :src="avatar.result" controls style="max-width:100%;max-height:360px;border-radius:8px"/>
          </div>
        </el-card>
      </el-tab-pane>
      
      <!-- TAB 4: Video -->
      <el-tab-pane label="Video" name="video">
        <el-card>
          <el-input v-model="video.prompt" type="textarea" :rows="3" placeholder="Describe the video you want... (e.g. product showcase, ad)" style="margin-bottom:10px"/>
          <el-select v-model="video.template" placeholder="Template" style="width:200px;margin-bottom:10px">
            <el-option label="Product Showcase" value="product"/>
            <el-option label="Promo Ad" value="promo"/>
            <el-option label="Social Short" value="social"/>
            <el-option label="Tutorial" value="tutorial"/>
          </el-select>
          <el-button type="primary" @click="doGenVideo" :loading="video.loading">Generate Video</el-button>
          <div v-if="video.result" class="mg-output" style="text-align:center">
            <video :src="video.result" controls style="max-width:100%;max-height:360px;border-radius:8px"/>
          </div>
        </el-card>
      </el-tab-pane>
      
      <!-- TAB 5: Batch -->
      <el-tab-pane label="Batch" name="batch">
        <el-card>
          <div style="margin-bottom:10px">
            <span style="color:rgba(255,255,255,.5);font-size:12px">Upload a CSV with columns: product_name, category, features</span>
            <input type="file" accept=".csv" @change="onBatchFile" style="display:block;margin-top:4px"/>
          </div>
          <el-select v-model="batch.type" placeholder="Task type" style="width:200px;margin-bottom:10px">
            <el-option label="Generate Descriptions" value="descriptions"/>
            <el-option label="Generate Images" value="images"/>
            <el-option label="Generate Both" value="both"/>
          </el-select>
          <el-button type="primary" @click="doBatch" :loading="batch.loading" :disabled="!batch.file">Start Batch Processing</el-button>
          <div v-if="batch.result" class="mg-output">{{ batch.result }}</div>
        </el-card>
      </el-tab-pane>
      
      <!-- TAB 6: Gallery -->
      <el-tab-pane label="Gallery" name="gallery">
        <el-button @click="loadGallery" :loading="gallery.loading" style="margin-bottom:12px">Refresh Gallery</el-button>
        <el-row :gutter="12">
          <el-col :xs="12" :sm="8" :md="6" v-for="item in gallery.items" :key="item.filename" style="margin-bottom:12px">
            <el-card shadow="hover" :body-style="{padding:'8px'}">
              <img v-if="item.type==='image'" :src="item.url" style="width:100%;aspect-ratio:1;object-fit:cover;border-radius:6px"/>
              <video v-else-if="item.type==='video'" :src="item.url" controls style="width:100%;border-radius:6px"/>
              <div style="font-size:11px;color:rgba(255,255,255,.5);margin-top:4px;text-align:center;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ item.filename }}</div>
              <el-button size="small" @click="downloadItem(item)" style="width:100%;margin-top:4px">Download</el-button>
            </el-card>
          </el-col>
        </el-row>
        <div v-if="gallery.items.length===0 && !gallery.loading" style="text-align:center;color:rgba(255,255,255,.4);padding:40px">No generated content yet. Create something above!</div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"; import { ElMessage } from "element-plus"; import { agentApi } from "@/api"

const tab = ref("rewrite")

// Rewrite
const rewrite = ref({ text: '', style: 'professional', loading: false, result: '' })
const rewriteStyles = ['professional', 'casual', 'marketing', 'storytelling', 'bullet_points', 'seo_optimized']
async function doRewrite() {
  if (!rewrite.value.text) return ElMessage.warning('Enter text first')
  rewrite.value.loading = true
  try {
    const r = await agentApi.post("/agent/media/rewrite", { text: rewrite.value.text, style: rewrite.value.style })
    if (r?.data?.ok) rewrite.value.result = r.data.text || r.data.result
    else ElMessage.error(r?.data?.error || 'Rewrite failed')
  } catch (e) { ElMessage.error(e.message) }
  rewrite.value.loading = false
}

// Image Gen
const image = ref({ prompt: '', style: 'realistic', size: '1024x1024', loading: false, result: '' })
const imgStyles = ['realistic', 'cinematic', 'anime', 'oil-painting', 'watercolor', 'pixel-art', '3d-render', 'sketch', 'cyberpunk', 'minimalist']
onMounted(async () => {
  try { const r = await agentApi.get("/agent/media/styles"); if (r?.data?.ok) { /* use API styles */ } } catch {}
  try { const r2 = await agentApi.get("/agent/media/voices"); if (r2?.data?.ok) voices.value = r2.data.voices } catch {}
})
async function doGenImage() {
  if (!image.value.prompt) return ElMessage.warning('Enter a prompt first')
  image.value.loading = true
  try {
    const r = await agentApi.post("/agent/media/image", { prompt: image.value.prompt, style: image.value.style, size: image.value.size })
    if (r?.data?.ok) image.value.result = r.data.url || r.data.image_url
    else ElMessage.error(r?.data?.error || 'Generation failed')
  } catch (e) { ElMessage.error(e.message) }
  image.value.loading = false
}

// Digital Human
const avatar = ref({ text: '', voice: 'xiaoxiao', loading: false, result: '', imageB64: '' })
const voices = ref([
  { id: 'xiaoxiao', name: 'Xiaoxiao - Female Warm' },
  { id: 'yunxi', name: 'Yunxi - Male Professional' },
  { id: 'xiaoyi', name: 'Xiaoyi - Female Lively' },
  { id: 'yunyang', name: 'Yunyang - Male News Anchor' }
])
function onAvatarFile(e) {
  const file = e.target.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => { avatar.value.imageB64 = reader.result?.toString()?.split(',')[1] || '' }
  reader.readAsDataURL(file)
}
async function doGenAvatar() {
  if (!avatar.value.text) return ElMessage.warning('Enter text for the digital human')
  avatar.value.loading = true
  try {
    const r = await agentApi.post("/agent/media/avatar", { text: avatar.value.text, voice: avatar.value.voice, image_b64: avatar.value.imageB64 })
    if (r?.data?.ok) avatar.value.result = r.data.url || r.data.video_url
    else ElMessage.error(r?.data?.error || 'Avatar generation failed')
  } catch (e) { ElMessage.error(e.message) }
  avatar.value.loading = false
}

// Video
const video = ref({ prompt: '', template: 'product', loading: false, result: '' })
async function doGenVideo() {
  if (!video.value.prompt) return ElMessage.warning('Enter a video description')
  video.value.loading = true
  try {
    const r = await agentApi.post("/agent/media/video", { prompt: video.value.prompt, template: video.value.template })
    if (r?.data?.ok) video.value.result = r.data.url || r.data.video_url
    else ElMessage.error(r?.data?.error || 'Video generation failed')
  } catch (e) { ElMessage.error(e.message) }
  video.value.loading = false
}

// Batch
const batch = ref({ file: null, type: 'descriptions', loading: false, result: '' })
function onBatchFile(e) { batch.value.file = e.target.files?.[0] || null }
async function doBatch() {
  if (!batch.value.file) return ElMessage.warning('Upload a CSV file first')
  batch.value.loading = true
  try {
    const fd = new FormData(); fd.append('file', batch.value.file); fd.append('type', batch.value.type)
    const r = await agentApi.post("/agent/media/batch", fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    if (r?.data?.ok) batch.value.result = `Processed ${r.data.count||0} items. ${r.data.message||''}`
    else ElMessage.error(r?.data?.error || 'Batch failed')
  } catch (e) { ElMessage.error(e.message) }
  batch.value.loading = false
}

// Gallery
const gallery = ref({ items: [], loading: false })
async function loadGallery() {
  gallery.value.loading = true
  try {
    const r = await agentApi.get("/agent/media/gallery")
    if (r?.data?.ok) gallery.value.items = r.data.items || r.data.files || []
  } catch (e) { ElMessage.error(e.message) }
  gallery.value.loading = false
}
function downloadItem(item) {
  const a = document.createElement('a'); a.href = item.url; a.download = item.filename; a.click()
}
onMounted(() => { loadGallery() })
</script>

<style scoped>
.mg-shell { max-width: 1100px; margin: 0 auto; padding: 20px; }
.mg-header { margin-bottom: 16px; }
.mg-header h2 { font-size: 22px; color: #e0e0ff; margin: 0; }
.mg-header p { font-size: 13px; color: rgba(255,255,255,0.5); margin: 4px 0 0; }
.mg-output { margin-top: 12px; padding: 16px; background: rgba(102,126,234,0.08); border-radius: 10px; font-size: 14px; color: #e0e0e0; line-height: 1.7; white-space: pre-wrap; }
@media (max-width: 768px) { .mg-shell { padding: 10px; } }
</style>