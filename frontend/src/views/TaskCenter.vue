<template>
  <div class="task-center-panel">
    <div class="page-header">
      -
      <p>9? //? </p>
    </div>

    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6">
        <el-card shadow="never" class="stat-simple">
          <div class="stat-num" style="color:#1677ff">{{ tasks.length }}</div>
          -
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-simple">
          <div class="stat-num" style="color:#52c41a">{{ runningCount }}</div>
          <div class="stat-text">?/div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-simple">
          <div class="stat-num" style="color:#faad14">{{ pausedCount }}</div>
          <div class="stat-text">?/div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-simple">
          <div class="stat-num" style="color:#722ed1">{{ pendingCount }}</div>
          -
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never">
      <template #header>
        <el-space><span>{{ ('tasks.title') }}</span><el-button size="small" @click="loadTasks">OK</el-button></el-space>
      </template>
      <el-table :data="tasks" size="small" v-loading="loading">
        <el-table-column prop="id" label="ID" width="120"/>
        <el-table-column prop="name" :label="\('tasks.title')" width="140"/>
        <el-table-column prop="desc" label='Status' min-width="200"/>
        <el-table-column prop="trigger" :label="\('tasks.title')" width="130"/>
        <el-table-column prop="next_run" :label="\('tasks.title')" width="170">
          <template #default="{row}">{{ formatTime(row.next_run) }}</template>
        </el-table-column>
        <el-table-column label="? width="90">
          <template #default="{row}">
            <el-tag :type="row.status==='running'?'success':'warning'' size="small">
              {{ row.status==='running'?'?:'? }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label='Status' width="180">
          <template #default="{row}">
            <el-button size="small" type="primary" link @click="doTrigger(row.id)">?</el-button>
            <el-button v-if="row.status==='running'' size="small" type="warning" link @click="doPause(row.id)">?</el-button>
            <el-button v-else size="small" type="success" link @click="doResume(row.id)">?</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { listSchedulerTasks, triggerTask, pauseTask, resumeTask } from '@/api/scheduler'

const tasks = ref([])
const loading = ref(false)

const runningCount = computed(() => tasks.value.filter(t => t.status === 'running').length)
const pausedCount = computed(() => tasks.value.filter(t => t.status === 'paused').length)
const pendingCount = computed(() => tasks.value.filter(t => t.pending).length)

function formatTime(t) {
  if (!t) return '-'
  const d = new Date(t)
  return d.toLocaleString('zh-CN', { hour12: false })
}

async function loadTasks() {
  loading.value = true
  try {
    const { data } = await listSchedulerTasks()
    tasks.value = data.tasks || []
  } catch (e) {
    ElMessage.error('OK')
  } finally { loading.value = false }
}

async function doTrigger(id) {
  try {
    await triggerTask(id)
    ElMessage.success('?)
    loadTasks()
  } catch (e) { ElMessage.error('OK') }
}

async function doPause(id) {
  try {
    await pauseTask(id)
    ElMessage.success('?)
    loadTasks()
  } catch (e) { ElMessage.error('OK') }
}

async function doResume(id) {
  try {
    await resumeTask(id)
    ElMessage.success('?)
    loadTasks()
  } catch (e) { ElMessage.error('Error') }
}

onMounted(() => loadTasks())
</script>

<style scoped>
.task-center-panel { padding: 0; }
.page-header { margin-bottom: 20px; }
.page-header h1 { font-size: 22px; margin: 0 0 4px; }
.page-header p { color: var(--text-muted); font-size: 13px; margin: 0; }
.stat-simple { text-align: center; }
.stat-simple .stat-num { font-size: 32px; font-weight: 700; }
.stat-simple .stat-text { font-size: 13px; color: var(--text-muted); margin-top: 4px; }
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>
