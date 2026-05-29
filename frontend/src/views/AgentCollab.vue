<template>
  <div class="page-shell">
    <div class="page-header"><h2>🤖 Agent 协作中心</h2><p>多Agent协同 — 规划→分析→执行→审查→报告</p></div>
    <el-row :gutter="16">
      <el-col :span="14">
        <el-card><template #header>🎯 任务目标</template>
          <el-input v-model="goal" placeholder="描述你要完成的任务，如：分析今天订单异常并修复" type="textarea" :rows="3" />
          <el-button type="primary" style="margin-top:12px" @click="runCollab" :loading="running">🚀 启动协作</el-button>
        </el-card>
        <el-card v-if="task" style="margin-top:16px"><template #header>📋 执行计划</template>
          <el-timeline>
            <el-timeline-item v-for="s in task.steps" :key="s.id" :timestamp="s.role" :type="s.status === 'done' ? 'success' : s.status === 'running' ? 'warning' : 'info'">
              {{ s.action }}
              <el-tag v-if="s.status === 'running'" size="small" type="warning">执行中</el-tag>
              <el-tag v-if="s.status === 'done'" size="small" type="success">完成</el-tag>
            </el-timeline-item>
          </el-timeline>
          <div v-if="task.summary" class="collab-summary">{{ task.summary }}</div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card><template #header>📊 协作状态</template>
          <div class="stat-grid">
            <div class="stat-item"><span class="stat-val">{{ status.active_tasks }}</span><span class="stat-label">进行中</span></div>
            <div class="stat-item"><span class="stat-val">{{ status.completed_tasks }}</span><span class="stat-label">已完成</span></div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { agentApi } from '@/api'

const goal = ref('')
const running = ref(false)
const task = ref(null)
const status = ref({ active_tasks: 0, completed_tasks: 0 })

async function runCollab() {
  if (!goal.value) { ElMessage.warning('请输入任务目标'); return }
  running.value = true
  try {
    const res = await agentApi.post('/agent/collab/run', { goal: goal.value })
    if (res?.data?.ok) {
      task.value = res.data.task
      ElMessage.success(task.value.summary)
    } else {
      ElMessage.error('执行失败')
    }
  } catch (e) { ElMessage.error('请求失败: ' + e.message) }
  running.value = false
  fetchStatus()
}

async function fetchStatus() {
  try {
    const res = await agentApi.get('/agent/collab/status')
    if (res?.data) status.value = res.data
  } catch {}
}

onMounted(fetchStatus)
</script>

<style scoped>
.page-shell { max-width: 900px; margin: 0 auto; padding: 20px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { font-size: 20px; color: #e0e0ff; margin: 0; }
.page-header p { font-size: 12px; color: rgba(255,255,255,0.5); margin: 4px 0; }
.collab-summary { margin-top: 12px; padding: 10px; background: rgba(102,126,234,0.1); border-radius: 8px; font-size: 13px; color: #a0c4ff; }
.stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.stat-item { text-align: center; padding: 16px; background: rgba(255,255,255,0.03); border-radius: 10px; }
.stat-val { display: block; font-size: 28px; font-weight: 700; color: #667eea; }
.stat-label { font-size: 11px; color: rgba(255,255,255,0.5); }
@media (max-width: 768px) {
  .page-shell { padding: 10px; }
  .el-row { flex-direction: column; }
}
</style>
