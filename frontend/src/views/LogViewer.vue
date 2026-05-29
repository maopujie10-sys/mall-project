<template>
  <div class="log-viewer-panel">
    <div class="page-header"><h1>📋 日志中心</h1><p>Docker · Nginx · Tomcat · 应用日志统一查询</p></div>

    <!-- 日志源 -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6" v-for="s in sources" :key="s.id">
        <el-card shadow="never" :class="['src-card', { active: activeSource === s.id, unavailable: !s.available }]" @click="selectSource(s)">
          <div class="src-name">{{ s.name }}</div>
          <div class="src-info">{{ s.available ? s.size : '不可用' }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 工具栏 -->
    <el-card shadow="never" style="margin-bottom:20px">
      <el-row :gutter="12" align="middle">
        <el-col :span="4">
          <el-select v-model="logLevel" placeholder="级别过滤" clearable style="width:100%">
            <el-option label="全部" value=""/><el-option label="ERROR" value="ERROR"/>
            <el-option label="WARN" value="WARN"/><el-option label="INFO" value="INFO"/>
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-input v-model="filterText" placeholder="搜索关键词..." clearable @keyup.enter="loadLogs"/>
        </el-col>
        <el-col :span="4">
          <el-select v-model="logLines" style="width:100%">
            <el-option :value="50" label="50行"/><el-option :value="100" label="100行"/>
            <el-option :value="200" label="200行"/><el-option :value="500" label="500行"/>
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="loadLogs">🔍 查询</el-button>
          <el-button @click="loadSources">🔄 刷新</el-button>
        </el-col>
        <el-col :span="6">
          <el-space>
            <el-tag size="small" type="danger">ERROR: {{ stats.ERROR || 0 }}</el-tag>
            <el-tag size="small" type="warning">WARN: {{ stats.WARN || 0 }}</el-tag>
            <el-tag size="small" type="info">INFO: {{ stats.INFO || 0 }}</el-tag>
          </el-space>
        </el-col>
      </el-row>
    </el-card>

    <!-- 日志内容 -->
    <el-card shadow="never">
      <template #header>
        <span>📄 {{ activeSourceName }} — {{ logData.total_filtered || 0 }} / {{ logData.total_raw || 0 }} 行</span>
      </template>
      <div class="log-container" ref="logContainer">
        <div v-if="!logLines_data.length" class="log-empty">请选择日志源并点击查询</div>
        <div v-for="(line, i) in logLines_data" :key="i" :class="['log-line', getLineClass(line)]">
          <span class="log-num">{{ i + 1 }}</span>
          <span class="log-text">{{ line }}</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { listLogSources, viewLogs } from '@/api/log'

const sources = ref([])
const activeSource = ref('app')
const activeSourceName = ref('')
const filterText = ref('')
const logLevel = ref('')
const logLines = ref(100)
const logData = ref({})
const logLines_data = ref([])
const stats = ref({})

async function loadSources() {
  try {
    const { data } = await listLogSources()
    sources.value = data.sources || []
  } catch(e) {}
}

async function selectSource(s) {
  if (!s.available) return
  activeSource.value = s.id
  activeSourceName.value = s.name
  await loadLogs()
}

async function loadLogs() {
  try {
    const { data } = await viewLogs(activeSource.value, logLines.value, filterText.value, logLevel.value)
    logData.value = data
    logLines_data.value = data.lines || []
    stats.value = data.stats || {}
  } catch(e) {}
}

function getLineClass(line) {
  const u = (line||'').toUpperCase()
  if (u.includes('ERROR') || u.includes('FATAL') || u.includes('FAIL')) return 'level-error'
  if (u.includes('WARN')) return 'level-warn'
  if (u.includes('INFO')) return 'level-info'
  return ''
}

onMounted(async () => { await loadSources(); await loadLogs() })
</script>

<style scoped>
.log-viewer-panel { padding: 0; }
.page-header { margin-bottom: 20px; }
.page-header h1 { font-size: 22px; margin: 0 0 4px; }
.page-header p { color: var(--text-muted); font-size: 13px; margin: 0; }
.src-card { cursor: pointer; text-align: center; border: 2px solid transparent; transition: all .2s; }
.src-card.active { border-color: #1677ff; background: #f0f5ff; }
.src-card.unavailable { opacity: .4; cursor: not-allowed; }
.src-name { font-size: 14px; font-weight: 600; }
.src-info { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
.log-container { background: #1e1e1e; color: #d4d4d4; font-family: 'Consolas','Courier New',monospace; font-size: 12px; padding: 12px; border-radius: 6px; max-height: 600px; overflow-y: auto; }
.log-empty { color: #888; text-align: center; padding: 40px; }
.log-line { display: flex; line-height: 1.6; white-space: pre-wrap; word-break: break-all; }
.log-num { color: #858585; min-width: 40px; user-select: none; flex-shrink: 0; }
.log-text { flex: 1; }
.level-error { background: rgba(244,67,54,.15); color: #f44336; }
.level-warn { background: rgba(255,152,0,.1); color: #ff9800; }
.level-info { color: #2196f3; }
</style>
