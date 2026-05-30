<template>
  <div class="log-viewer-panel">
    <div class="page-header">-<p>Docker  Nginx  Tomcat  </p></div>

    <!-- ?-->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6" v-for="s in sources" :key="s.id">
        <el-card shadow="never" :class="['src-card', { active: activeSource === s.id, unavailable: !s.available }]" @click="selectSource(s)">
          <div class="src-name">{{ s.name }}</div>
          <div class="src-info">{{ s.available ? s.size : '不可用' }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- ?-->
    <el-card shadow="never" style="margin-bottom:20px">
      <el-row :gutter="12" align="middle">
        <el-col :span="4">
          <el-select v-model="logLevel" :placeholder="$t('logs.search')" clearable style="width:100%">
            <el-option :label="$t('logs.title')" value=''/><el-option label="ERROR" value="ERROR"/>
            <el-option label="WARN" value="WARN"/><el-option label="INFO" value="INFO"/>
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-input v-model="filterText" placeholder="搜索日志..." clearable @keyup.enter="loadLogs"/>
        </el-col>
        <el-col :span="4">
          <el-select v-model="logLines" style="width:100%">
            <el-option :value="50" label="50" /><el-option :value="100" label="100" />
            <el-option :value="200" label="200" /><el-option :value="500" label="500" />
          </el-select>
        </el-col>
        <el-col :span="4">
          
          <el-button @click="loadSources">OK</el-button>
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

    
    <el-card shadow="never">
      <template #header>
        <span> {{ activeSourceName }} ?{{ logData.total_filtered || 0 }} / {{ logData.total_raw || 0 }} </span>
      </template>
      <div class="log-container" ref="logContainer">
        -
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
.src-card.active { border-color: #1677ff; background: rgba(240,245,255,0.15); }
.src-card.unavailable { opacity: .4; cursor: not-allowed; }
.src-name { font-size: 14px; font-weight: 600; }
.src-info { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
.log-container { background: rgba(30,30,30,0.85); color: #d4d4d4; font-family: 'Consolas','Courier New',monospace; font-size: 12px; padding: 12px; border-radius: 6px; max-height: 600px; overflow-y: auto; }
.log-empty { color: #888; text-align: center; padding: 40px; }
.log-line { display: flex; line-height: 1.6; white-space: pre-wrap; word-break: break-all; }
.log-num { color: #858585; min-width: 40px; user-select: none; flex-shrink: 0; }
.log-text { flex: 1; }
.level-error { background: rgba(244,67,54,.15); color: #f44336; }
.level-warn { background: rgba(255,152,0,.1); color: #ff9800; }
.level-info { color: #2196f3; }
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>
