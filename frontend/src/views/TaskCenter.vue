<template>
  <div class="page-container task-center">
    <div class="page-header"><h2>自动任务</h2><p>Cron定时 · 事件触发 · 失败重试 · 执行日志</p></div>

    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6"><div class="metric-card"><div class="metric-label">任务总数</div><div class="metric-value">{{ tasks.length }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">运行中</div><div class="metric-value" style="color:#52c41a">{{ runningCount }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">今日执行</div><div class="metric-value">{{ todayExecs }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">成功率</div><div class="metric-value" style="color:#667eea">{{ successRate }}%</div></div></el-col>
    </el-row>

    <div class="tab-toolbar">
      <el-select v-model="filterStatus" placeholder="状态筛选" style="width:140px" clearable>
        <el-option label="全部" value="" /><el-option label="启用" value="enabled" /><el-option label="禁用" value="disabled" /><el-option label="运行中" value="running" />
      </el-select>
      <el-button type="primary" @click="showAdd=true">创建任务</el-button>
    </div>

    <el-table :data="filteredTasks" stripe>
      <el-table-column type="index" width="50" />
      <el-table-column prop="name" label="任务名称" min-width="160" show-overflow-tooltip />
      <el-table-column prop="type" label="类型" width="100"><template #default="{row}"><el-tag size="small">{{ row.type }}</el-tag></template></el-table-column>
      <el-table-column prop="cron" label="Cron表达式" width="150" show-overflow-tooltip />
      <el-table-column label="下次执行" width="170"><template #default="{row}"><span class="mono">{{ row.nextRun || '-' }}</span></template></el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{row}">
          <el-switch v-if="row.status!=='running'" :model-value="enabledProxy(row)" @update:model-value="(val) => toggleTask(row)" size="small" @change="toggleTask(row)" />
          <el-tag v-else type="warning" size="small">运行中</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="lastResult" label="上次结果" width="100"><template #default="{row}"><el-tag :type="row.lastResult==='成功'?'success':row.lastResult==='失败'?'danger':'info'" size="small">{{ row.lastResult || '-' }}</el-tag></template></el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{row}">
          <el-button link type="primary" size="small" @click="runNow(row)">立即执行</el-button>
          <el-button link type="primary" size="small" @click="viewLogs(row)">日志</el-button>
          <el-button link type="primary" size="small" @click="editTask(row)">编辑</el-button>
          <el-button link type="danger" size="small" @click="removeTask(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showAdd" :title="editingId?'编辑任务':'创建任务'" width="560px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="任务名称"><el-input v-model="form.name" placeholder="如：每日数据库备份" /></el-form-item>
        <el-form-item label="任务类型"><el-select v-model="form.type" style="width:100%"><el-option v-for="t in taskTypes" :key="t" :label="t" :value="t" /></el-select></el-form-item>
        <el-form-item label="Cron表达式"><el-input v-model="form.cron" placeholder="0 3 * * * (每天凌晨3点)" /><div style="font-size:11px;color:var(--text-muted);margin-top:4px">分 时 日 月 周</div></el-form-item>
        <el-form-item label="执行命令"><el-input v-model="form.command" type="textarea" :rows="3" placeholder="要执行的命令或脚本" /></el-form-item>
        <el-form-item label="失败重试"><el-input-number v-model="form.retries" :min="0" :max="10" /> <span style="margin-left:4px">次</span></el-form-item>
        <el-form-item label="超时时间"><el-input-number v-model="form.timeout" :min="0" :max="3600" :step="60" /> <span style="margin-left:4px">秒</span></el-form-item>
      </el-form>
      <template #footer><el-button @click="showAdd=false">取消</el-button><el-button type="primary" @click="saveTask" :loading="saving">{{editingId?'保存':'创建'}}</el-button></template>
    </el-dialog>

    <el-dialog v-model="showLogs" title="执行日志" width="700px">
      <el-timeline v-if="currentLogs.length">
        <el-timeline-item v-for="log in currentLogs" :key="log.id" :timestamp="log.time" :type="log.ok?'success':'danger'" placement="top">
          <el-card shadow="hover"><p><strong>{{ log.taskName }}</strong></p><p>{{ log.output }}</p><small>耗时: {{ log.duration }}</small></el-card>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无执行日志" />
      <template #footer><el-button @click="showLogs=false">关闭</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { agentApi } from '@/api/index'
const tasks = ref([]); const loading = ref(false)
async function fetchTasks() { loading.value = true; try { const { data } = await agentApi.get('/tasks/queue'); tasks.value = data.tasks || [] } catch {} finally { loading.value = false } }
async function cancelTask(id) {
  try {
    await agentApi.post('/tasks/queue/' + id + '/cancel')
    ElMessage.success('任务已取消')
    fetchTasks()
  } catch { ElMessage.error('取消失败') }
}
onMounted(function() { fetchTasks() })
</script>

<style scoped>
.task-center { padding: 24px; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 18px; margin: 0 0 4px; }
.page-header p { color: var(--text-muted); font-size: 13px; margin: 0; }
.metric-card { background: var(--bg-card); border-radius: 8px; padding: 18px; border: 1px solid var(--border-color); }
.metric-label { font-size: 12px; color: var(--text-muted); margin-bottom: 6px; }
.metric-value { font-size: 28px; font-weight: 700; }
.tab-toolbar { display: flex; gap: 12px; margin-bottom: 16px; align-items: center; }
.mono { font-family: monospace; font-size: 12px; }
</style>
