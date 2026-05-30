<template>
  <div class="page-shell">
    <div class="page-header">-<p> / Telegram / Web AI</p></div>

    <el-row :gutter="16">
      <el-col :span="8" v-for="p in platforms" :key="p.id">
        <el-card :class="{ 'connected': p.connected, 'disconnected': !p.connected }">
          <template #header>
            <span class="platform-header">{{ p.icon }} {{ p.name }}</span>
            <el-tag :type="p.connected ? 'success' : 'info' size="small" style="float:right">{{ p.connected ? '' : '' }}</el-tag>
          </template>
          <div class="platform-status">{{ p.status }}</div>
          <div class="platform-memory" v-if="p.memoryCount !== null">
            : <strong>{{ p.memoryCount }}</strong> 
          </div>
          
          <el-button v-else size="small" @click="goToKeys"> Key</el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top:16px">
      <template #header> </template>
      <el-timeline v-if="logs.length">
        <el-timeline-item v-for="l in logs" :key="l.time" :timestamp="l.time" :type="l.ok ? 'success' : 'danger''>
          {{ l.platform }}: {{ l.message }}
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description='' />
    </el-card>

    <el-card style="margin-top:16px">
      <template #header> </template>
      <el-input v-model="pushMsg" placeholder="..." style="margin-bottom:12px">
        <template #append><el-button @click="pushMemory" :loading="pushing">OK</el-button></template>
      </el-input>
      <el-table :data="memories" size="small" stripe max-height="300" v-if="memories.length">
        <el-table-column prop="platform" label='Status' width="100" />
        <el-table-column prop="content" label='Status' min-width="300" show-overflow-tooltip />
        <el-table-column prop="time" label='Status' width="160" />
      </el-table>
      <el-empty v-else description='' />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { agentApi } from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const pushing = ref(false)
const pushMsg = ref('')
const logs = ref([])
const memories = ref([])

const platforms = ref([
  { id: 'telegram', icon: '', name: 'Telegram', connected: false, status: '', memoryCount: null, syncing: false },
  { id: 'wechat', icon: '', name: '', connected: false, status: 'WECHAT_TOKEN', memoryCount: null, syncing: false },
  { id: 'web', icon: '', name: 'Web', connected: true, status: 'tiktook.eu.cc/ai/', memoryCount: 0, syncing: false }
])

async function loadStatus() {
  try {
    const r = await agentApi.get('/agent/keys/status')
    if (r?.data?.ok) {
      const caps = r.data.capabilities || {}
      if (caps.TELEGRAM_BOT_TOKEN?.ok) {
        platforms.value[0].connected = true
        platforms.value[0].status = 'Bot'
      }
      if (caps.WECHAT_TOKEN?.ok) {
        platforms.value[1].connected = true
        platforms.value[1].status = ''
      }
    }
  } catch {}
  try {
    const r = await agentApi.get('/agent/memory/stats')
    if (r?.data?.ok) {
      platforms.value[0].memoryCount = r.data.telegram || 0
      platforms.value[1].memoryCount = r.data.wechat || 0
      platforms.value[2].memoryCount = r.data.local || 0
    }
  } catch {}
}

async function syncNow(platformId) {
  const p = platforms.value.find(x => x.id === platformId)
  if (!p) return
  p.syncing = true
  try {
    const r = await agentApi.post('/agent/memory/sync/' + platformId)
    if (r?.data?.ok) {
      logs.value.unshift({ time: new Date().toLocaleString(), platform: p.name, ok: true, message: '' })
      ElMessage.success('OK')
    }
  } catch (e) {
    logs.value.unshift({ time: new Date().toLocaleString(), platform: p.name, ok: false, message: e.message })
  }
  p.syncing = false
}

async function pushMemory() {
  if (!pushMsg.value.trim()) return
  pushing.value = true
  try {
    await agentApi.post('/agent/memory/push', { message: pushMsg.value })
    ElMessage.success('OK')
    logs.value.unshift({ time: new Date().toLocaleString(), platform: '', ok: true, message: pushMsg.value.slice(0, 50) })
    pushMsg.value = ''
    loadStatus()
  } catch (e) {
    ElMessage.error(e.message)
  }
  pushing.value = false
}

function goToKeys() { router.push('/key-manager') }

onMounted(loadStatus)
</script>

<style scoped>
.page-shell { max-width: 960px; margin: 0 auto; padding: 20px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { font-size: 20px; color: #e0e0ff; margin: 0; }
.page-header p { font-size: 12px; color: rgba(255,255,255,0.5); margin: 4px 0; }
.platform-header { font-weight: 600; }
.platform-status { font-size: 12px; color: rgba(255,255,255,0.5); margin: 8px 0; }
.platform-memory { font-size: 13px; margin: 8px 0; }
.connected { border-left: 3px solid #4ade80; }
.disconnected { border-left: 3px solid #f87171; }
@media (max-width: 768px) { .page-shell { padding: 10px; } }
</style>