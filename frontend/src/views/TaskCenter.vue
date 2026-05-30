<template>
  <div class="task-center-panel">
    <div class="page-header">
      <h1>鈴憋笍 瀹氭椂浠诲姟涓績</h1>
      <p>9涓畾鏃朵换鍔路 鑷姩宸℃/澶囦唤/杞€?鎶ュ憡 路 鏀寔鎵嬪姩瑙﹀彂鍜屾殏鍋</p>
    </div>

    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6">
        <el-card shadow="never" class="stat-simple">
          <div class="stat-num" style="color:#1677ff">{{ tasks.length }}</div>
          <div class="stat-text">鎬讳换鍔℃暟</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-simple">
          <div class="stat-num" style="color:#52c41a">{{ runningCount }}</div>
          <div class="stat-text">杩愯涓</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-simple">
          <div class="stat-num" style="color:#faad14">{{ pausedCount }}</div>
          <div class="stat-text">宸叉殏鍋</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-simple">
          <div class="stat-num" style="color:#722ed1">{{ pendingCount }}</div>
          <div class="stat-text">绛夊緟鎵ц</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never">
      <template #header>
        <el-space><span>馃搵 浠诲姟娓呭崟</span><el-button size="small" @click="loadTasks">馃攧 鍒锋柊</el-button></el-space>
      </template>
      <el-table :data="tasks" size="small" v-loading="loading">
        <el-table-column prop="id" label="ID" width="120"/>
        <el-table-column prop="name" label="浠诲姟鍚嶇О" width="140"/>
        <el-table-column prop="desc" label="鎻忚堪" min-width="200"/>
        <el-table-column prop="trigger" label="瑙﹀彂瑙勫垯" width="130"/>
        <el-table-column prop="next_run" label="涓嬫鎵ц" width="170">
          <template #default="{row}">{{ formatTime(row.next_run) }}</template>
        </el-table-column>
        <el-table-column label="..." width="90">
          <template #default="{row}">
            <el-tag :type="row.status==='running'?'success':'warning'" size="small">
              {{ row.status==='running'''杩愯涓':'宸叉殏鍋' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="鎿嶄綔" width="180">
          <template #default="{row}">
            <el-button size="small" type="primary" link @click="doTrigger(row.id)">鈻绔嬪嵆鎵ц</el-button>
            <el-button v-if="row.status==='running'" size="small" type="warning" link @click="doPause(row.id)">鈴鏆傚仠</el-button>
            <el-button v-else size="small" type="success" link @click="doResume(row.id)">鈻鎭㈠</el-button>
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
    ElMessage.error('鍔犺浇澶辫触')
  } finally { loading.value = false }
}

async function doTrigger(id) {
  try {
    await triggerTask(id)
    ElMessage.success('浠诲姟宸茶Е鍙?)
    loadTasks()
  } catch (e) { ElMessage.error('瑙﹀彂澶辫触') }
}

async function doPause(id) {
  try {
    await pauseTask(id)
    ElMessage.success('宸叉殏鍋?)
    loadTasks()
  } catch (e) { ElMessage.error('鏆傚仠澶辫触') }
}

async function doResume(id) {
  try {
    await resumeTask(id)
    ElMessage.success('宸叉仮澶?)
    loadTasks()
  } catch (e) { ElMessage.error('鎭㈠澶辫触') }
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
