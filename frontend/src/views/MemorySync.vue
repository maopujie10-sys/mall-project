<template>
  <div class="page-shell">
    <div class="page-header"><h2>🔄 跨平台记忆同步</h2><p>微信 / Telegram / Web 统一记忆，AI跨平台无缝衔接</p></div>

    <el-row :gutter="16">
      <el-col :span="8" v-for="p in platforms" :key="p.id">
        <el-card :class="{ 'connected': p.connected, 'disconnected': !p.connected }">
          <template #header>
            <span class="platform-header">{{ p.icon }} {{ p.name }}</span>
            <el-tag :type="p.connected ? 'success' : 'info'" size="small" style="float:right">{{ p.connected ? '已连接' : '待配置' }}</el-tag>
          </template>
          <div class="platform-status">{{ p.status }}</div>
          <div class="platform-memory" v-if="p.memoryCount !== null">
            同步记忆: <strong>{{ p.memoryCount }}</strong> 条
          </div>
          <el-button v-if="p.connected" size="small" type="primary" @click="syncNow(p.id)" :loading="p.syncing">
            🔄 立即同步
          </el-button>
          <el-button v-else size="small" @click="goToKeys">🔑 配置Key</el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top:16px">
      <template #header>📋 同步日志</template>
      <el-timeline v-if="logs.length">
        <el-timeline-item v-for="l in logs" :key="l.time" :timestamp="l.time" :type="l.ok ? 'success' : 'danger'">
          {{ l.platform }}: {{ l.message }}
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无同步记录" />
    </el-card>

    <el-card style="margin-top:16px">
      <template #header>🧠 共享记忆内容</template>
      <el-input v-model="pushMsg" placeholder="输入要同步到所有平台的记忆..." style="margin-bottom:12px">
        <template #append><el-button @click="pushMemory" :loading="pushing">推送</el-button></template>
      </el-input>
      <el-table :data="memories" size="small" stripe max-height="300" v-if="memories.length">
        <el-table-column prop="platform" label="平台" width="100" />
        <el-table-column prop="content" label="内容" min-width="300" show-overflow-tooltip />
        <el-table-column prop="time" label="时间" width="160" />
      </el-table>
      <el-empty v-else description="暂无共享记忆" />
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
  { id: 'telegram', icon: '✈️', name: 'Telegram', connected: false, status: '等待配置', memoryCount: null, syncing: false },
  { id: 'wechat', icon: '💬', name: '微信', connected: false, status: '需要WECHAT_TOKEN', memoryCount: null, syncing: false },
  { id: 'web', icon: '🌐', name: 'Web', connected: true, status: 'tiktook.eu.cc/ai/', memoryCount: 0, syncing: false }
])

async function loadStatus() {
  try {
    const r = await agentApi.get('/agent/keys/status')
    if (r?.ok) {
      const caps = r.capabilities || {}
      if (caps.TELEGRAM_BOT_TOKEN?.ok) {
        platforms.value[0].connected = true
        platforms.value[0].status = 'Bot已连接'
      }
      if (caps.WECHAT_TOKEN?.ok) {
        platforms.value[1].connected = true
        platforms.value[1].status = '公众号已连接'
      }
    }
  } catch {}
  try {
    const r = await agentApi.get('/agent/memory/stats')
    if (r?.ok) {
      platforms.value[0].memoryCount = r.telegram || 0
      platforms.value[1].memoryCount = r.wechat || 0
      platforms.value[2].memoryCount = r.local || 0
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
      logs.value.unshift({ time: new Date().toLocaleString(), platform: p.name, ok: true, message: '同步成功' })
      ElMessage.success('同步完成')
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
    ElMessage.success('已推送到所有平台')
    logs.value.unshift({ time: new Date().toLocaleString(), platform: '全平台', ok: true, message: pushMsg.value.slice(0, 50) })
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