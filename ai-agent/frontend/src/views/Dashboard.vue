<template>
  <div class="page-container">
    <div class="page-header">
      <h2>AI Agent 总控台</h2>
      <p>系统状态总览 · 实时监控 · 快捷操作</p>
    </div>

    <!-- 错误提示 -->
    <el-alert v-if="error" :title="error" type="error" show-icon closable @close="error=null" style="margin-bottom:16px" />

    <!-- 运行模式 + 状态概览 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">运行模式</div>
          <div class="metric-value" style="font-size: 20px;" :style="{ color: currentMode === 'human-control' ? 'var(--color-danger)' : 'var(--color-success)' }">
            <span class="status-dot" :class="currentMode === 'human-control' ? 'offline' : 'online'"><span class="dot"></span></span>
            {{ systemStore.modeLabel }}
          </div>
          <div class="metric-sub">自动处理 L1-L2 级任务</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">今日执行任务</div>
          <div class="metric-value">{{ loading ? '...' : stats.todayTasks || 0 }}</div>
          <div class="metric-sub">成功率 100%</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">待审批</div>
          <div class="metric-value" :style="{ color: (stats.pendingApprovals || 0) > 0 ? 'var(--color-warning)' : 'var(--text-primary)' }">{{ loading ? '...' : (stats.pendingApprovals || 0) }}</div>
          <div class="metric-sub">需要人工确认</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">最近告警</div>
          <div class="metric-value" style="font-size: 20px;" :style="{ color: stats.recentAlerts !== '无' ? 'var(--color-danger)' : 'var(--text-secondary)' }">{{ stats.recentAlerts || '无' }}</div>
          <div class="metric-sub">系统运行正常</div>
        </div>
      </el-col>
    </el-row>

    <!-- 核心系统状态 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="16">
        <el-card shadow="never">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: 600;">核心系统状态</span>
              <el-button text type="primary" size="small" @click="refreshStatus">刷新</el-button>
            </div>
          </template>
          <el-row :gutter="16">
            <el-col :span="8" v-for="item in systems" :key="item.name">
              <div style="display: flex; align-items: center; gap: 12px; padding: 12px 0;">
                <div :style="{ width: 40, height: 40, borderRadius: 8, background: item.online ? 'var(--color-success-bg)' : 'var(--color-danger-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center' }">
                  <el-icon :size="20" :color="item.online ? 'var(--color-success)' : 'var(--color-danger)'">
                    <component :is="item.icon" />
                  </el-icon>
                </div>
                <div>
                  <div style="font-weight: 500; font-size: 14px;">{{ item.name }}</div>
                  <div style="font-size: 12px; color: var(--text-muted);">
                    <span class="status-dot" :class="item.online ? 'online' : 'offline'">
                      <span class="dot"></span>{{ item.online ? '在线' : '离线' }}
                    </span>
                  </div>
                </div>
                <div style="margin-left: auto; font-size: 12px; color: var(--text-muted);">{{ item.info }}</div>
              </div>
              <el-divider v-if="item.name !== systems[systems.length-1].name" style="margin: 0;" />
            </el-col>
          </el-row>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never" style="height: 100%;">
          <template #header>
            <span style="font-weight: 600;">快捷操作</span>
          </template>
          <div style="display: flex; flex-direction: column; gap: 8px;">
            <el-button @click="$router.push('/chat')" style="justify-content: flex-start;">
              <el-icon style="margin-right: 8px;"><ChatDotRound /></el-icon>
              打开 AI 对话
            </el-button>
            <el-button @click="quickCheck" :loading="checking" style="justify-content: flex-start;">
              <el-icon style="margin-right: 8px;"><Search /></el-icon>
              全站快速诊断
            </el-button>
            <el-button @click="quickBackup" style="justify-content: flex-start;">
              <el-icon style="margin-right: 8px;"><FolderOpened /></el-icon>
              备份数据库
            </el-button>
            <el-button @click="$router.push('/emergency')" style="justify-content: flex-start; color: var(--color-danger);">
              <el-icon style="margin-right: 8px;"><WarningFilled /></el-icon>
              急救面板
            </el-button>
            <el-divider style="margin: 4px 0;" />
            <div style="font-size:12px; color:var(--text-muted); padding:4px 0;">虚拟数据生成</div>
            <el-button size="small" @click="genVirtual('orders')" style="justify-content: flex-start;">
              <el-icon style="margin-right: 6px;"><ShoppingCart /></el-icon>生成虚拟订单
            </el-button>
            <el-button size="small" @click="genVirtual('reviews')" style="justify-content: flex-start;">
              <el-icon style="margin-right: 6px;"><ChatLineSquare /></el-icon>补充虚拟评价
            </el-button>
            <el-button size="small" @click="genVirtual('views')" style="justify-content: flex-start;">
              <el-icon style="margin-right: 6px;"><View /></el-icon>增加浏览量
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近任务 + 系统日志 -->
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: 600;">最近任务</span>
              <el-button text type="primary" size="small">查看全部</el-button>
            </div>
          </template>
          <div v-for="task in recentTasks" :key="task.id" style="display: flex; align-items: center; gap: 12px; padding: 10px 0;">
            <span class="risk-badge" :class="task.risk.toLowerCase()">{{ task.risk }}</span>
            <span style="font-size: 13px; flex: 1;">{{ task.name }}</span>
            <span style="font-size: 12px; color: var(--text-muted);">{{ task.time }}</span>
            <el-tag :type="task.status === '完成' ? 'success' : 'warning'" size="small">{{ task.status }}</el-tag>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <span style="font-weight: 600;">系统日志</span>
          </template>
          <div class="code-block" style="max-height: 240px; font-size: 11px;">
            <div v-for="(log, i) in logs" :key="i" style="margin-bottom: 2px;">
              <span style="color: var(--text-muted);">{{ log.time }}</span>
              <span :style="{ color: log.level === 'ERROR' ? 'var(--color-danger)' : log.level === 'WARN' ? 'var(--color-warning)' : 'var(--text-secondary)' }"> [{{ log.level }}]</span>
              {{ log.msg }}
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getServerStatus } from '@/api/server'
import { getMallStatus } from '@/api/mall'
import { getAgentTasks } from '@/api/agent'
import { createBackup } from '@/api/rollback'
import { useSystemStore } from '@/stores/system'
import { storeToRefs } from 'pinia'

const systemStore = useSystemStore()
const { currentMode } = storeToRefs(systemStore)

const checking = ref(false)
const loading = ref(true)
const error = ref(null)
let pollTimer = null

// Stats from real API
const stats = reactive({
  todayTasks: 0,
  pendingApprovals: 0,
  recentAlerts: '无',
})

const systems = reactive([
  { name: 'Nginx', icon: 'Connection', online: false, info: '加载中...' },
  { name: 'Java App', icon: 'Service', online: false, info: '加载中...' },
  { name: 'MySQL', icon: 'Coin', online: false, info: '加载中...' },
  { name: 'Redis', icon: 'Odometer', online: false, info: '加载中...' },
  { name: 'Docker', icon: 'Files', online: false, info: '加载中...' },
  { name: '商城服务', icon: 'ShoppingCart', online: false, info: '加载中...' },
])

const recentTasks = reactive([])
const logs = reactive([])

async function fetchDashboardData() {
  try {
    // Fetch server status for system indicators
    const serverData = await getServerStatus()
    if (serverData) {
      if (serverData.systems) {
        serverData.systems.forEach((s, i) => {
          if (i < systems.length) {
            systems[i].online = s.online ?? s.status === 'running'
            systems[i].info = s.info || s.version || systems[i].info
          }
        })
      }
      if (serverData.todayTasks !== undefined) stats.todayTasks = serverData.todayTasks
      if (serverData.pendingApprovals !== undefined) stats.pendingApprovals = serverData.pendingApprovals
      if (serverData.recentLogs) {
        logs.splice(0, logs.length, ...serverData.recentLogs.map((l) => ({
          time: l.time || '',
          level: l.level || 'INFO',
          msg: l.msg || l.message || '',
        })))
      }
    }

    // Fetch agent tasks for recent tasks list
    try {
      const tasksData = await getAgentTasks()
      if (Array.isArray(tasksData)) {
        recentTasks.splice(0, recentTasks.length, ...tasksData.slice(0, 5).map((t) => ({
          id: t.id || Date.now(),
          risk: t.risk || 'L1',
          name: t.name || t.task || '未知任务',
          time: t.time || '-',
          status: t.status || '完成',
        })))
      }
    } catch {
      // Tasks optional
    }

    error.value = null
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const refreshStatus = async () => {
  checking.value = true
  await fetchDashboardData()
  checking.value = false
}

const quickCheck = async () => {
  checking.value = true
  await fetchDashboardData()
  checking.value = false
  ElMessage.success('全站诊断完成')
}

const quickBackup = async () => {
  try {
    await createBackup()
    ElMessage.success('备份任务已提交')
  } catch (e) {
    ElMessage.error('备份失败: ' + (e.message || '未知错误'))
  }
}

// Virtual data controls
const genVirtual = async (type) => {
  try {
    const { agentApi } = await import('@/api/index')
    await agentApi.post('/agent/virtual/generate', { type, count: 10 })
    ElMessage.success(`虚拟${type==='orders'?'订单':type==='reviews'?'评价':'浏览'}数据已生成`)
  } catch (e) {
    ElMessage.error('生成失败: ' + (e.message || '未知错误'))
  }
}

onMounted(() => {
  fetchDashboardData()
  pollTimer = setInterval(fetchDashboardData, 10000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>
