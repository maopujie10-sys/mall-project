<template>
  <div class="task-center-panel">
    <div class="page-header">
      <h1>⏱️ 定时任务中心</h1>
      <p>9个定时任务 · 自动巡检/备份/轮值/报告 · 支持手动触发和暂停</p>
    </div>

    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6">
        <el-card shadow="never" class="stat-simple">
          <div class="stat-num" style="color:#1677ff">{{ tasks.length }}</div>
          <div class="stat-text">总任务数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-simple">
          <div class="stat-num" style="color:#52c41a">{{ runningCount }}</div>
          <div class="stat-text">运行中</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-simple">
          <div class="stat-num" style="color:#faad14">{{ pausedCount }}</div>
          <div class="stat-text">已暂停</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-simple">
          <div class="stat-num" style="color:#722ed1">{{ pendingCount }}</div>
          <div class="stat-text">等待执行</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never">
      <template #header>
        <el-space><span>📋 任务清单</span><el-button size="small" @click="loadTasks">🔄 刷新</el-button></el-space>
      </template>
      <el-table :data="tasks" size="small" v-loading="loading">
        <el-table-column prop="id" label="ID" width="120"/>
        <el-table-column prop="name" label="任务名称" width="140"/>
        <el-table-column prop="desc" label="描述" min-width="200"/>
        <el-table-column prop="trigger" label="触发规则" width="130"/>
        <el-table-column prop="next_run" label="下次执行" width="170">
          <template #default="{row}">{{ formatTime(row.next_run) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{row}">
            <el-tag :type="row.status==='running'?'success':'warning'" size="small">
              {{ row.status==='running'?'运行中':'已暂停' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{row}">
            <el-button size="small" type="primary" link @click="doTrigger(row.id)">▶ 立即执行</el-button>
            <el-button v-if="row.status==='running'" size="small" type="warning" link @click="doPause(row.id)">⏸ 暂停</el-button>
            <el-button v-else size="small" type="success" link @click="doResume(row.id)">▶ 恢复</el-button>
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
    ElMessage.error('加载失败')
  } finally { loading.value = false }
}

async function doTrigger(id) {
  try {
    await triggerTask(id)
    ElMessage.success('任务已触发')
    loadTasks()
  } catch (e) { ElMessage.error('触发失败') }
}

async function doPause(id) {
  try {
    await pauseTask(id)
    ElMessage.success('已暂停')
    loadTasks()
  } catch (e) { ElMessage.error('暂停失败') }
}

async function doResume(id) {
  try {
    await resumeTask(id)
    ElMessage.success('已恢复')
    loadTasks()
  } catch (e) { ElMessage.error('恢复失败') }
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
</style>
