<template>
  <div class="page-container">
    <div class="page-header">
      <h2>服务器监控面板</h2>
      <p>系统资源 · 进程管理 · 端口监听</p>
    </div>

    <el-alert v-if="error" :title="error" type="error" show-icon closable @close="error=null" style="margin-bottom:16px" />

    <!-- 指标卡片 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">CPU 使用率</div>
          <div class="metric-value">{{ systemMetrics.cpu }}%</div>
          <el-progress :percentage="systemMetrics.cpu" :color="cpuColor" :show-text="false" style="margin-top: 12px;" />
          <div class="metric-sub">4 核心 · {{ systemMetrics.cpuCores }} 线程</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">内存使用</div>
          <div class="metric-value">{{ systemMetrics.memory }}%</div>
          <el-progress :percentage="systemMetrics.memory" :color="memColor" :show-text="false" style="margin-top: 12px;" />
          <div class="metric-sub">已用 {{ systemMetrics.memUsed }} / 总计 {{ systemMetrics.memTotal }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">磁盘使用</div>
          <div class="metric-value">{{ systemMetrics.disk }}%</div>
          <el-progress :percentage="systemMetrics.disk" :color="diskColor" :show-text="false" style="margin-top: 12px;" />
          <div class="metric-sub">已用 {{ systemMetrics.diskUsed }} / 总计 {{ systemMetrics.diskTotal }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">系统负载</div>
          <div class="metric-value">{{ systemMetrics.loadAvg }}</div>
          <div class="metric-sub">1min / 5min / 15min</div>
          <div style="margin-top: 8px; display: flex; gap: 8px;">
            <span class="status-dot online"><span class="dot"></span>运行正常</span>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 进程列表 + 端口监听 -->
    <el-row :gutter="16">
      <el-col :span="14">
        <el-card shadow="never">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: 600;">进程列表</span>
              <el-button text type="primary" size="small" @click="refreshAll" :loading="loading">
                <el-icon><Refresh /></el-icon> 刷新
              </el-button>
            </div>
          </template>
          <el-table :data="processes" style="width: 100%;" size="small" stripe>
            <template #empty>
              <el-empty description="暂无进程数据" :image-size="60" />
            </template>
            <el-table-column prop="name" label="进程名称" min-width="140">
              <template #default="{ row }">
                <span style="display: flex; align-items: center; gap: 6px;">
                  <span class="status-dot" :class="row.status === 'running' ? 'online' : 'offline'">
                    <span class="dot"></span>
                  </span>
                  {{ row.name }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="pid" label="PID" width="80" />
            <el-table-column prop="cpu" label="CPU %" width="80">
              <template #default="{ row }">
                <span :style="{ color: row.cpu > 50 ? 'var(--color-danger)' : row.cpu > 20 ? 'var(--color-warning)' : 'var(--text-primary)' }">
                  {{ row.cpu }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="mem" label="内存 %" width="90">
              <template #default="{ row }">
                <span :style="{ color: row.mem > 70 ? 'var(--color-danger)' : row.mem > 40 ? 'var(--color-warning)' : 'var(--text-primary)' }">
                  {{ row.mem }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="uptime" label="运行时间" width="120" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'running' ? 'success' : 'danger'" size="small" effect="light">
                  {{ row.status === 'running' ? '运行中' : '已停止' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="never">
          <template #header>
            <span style="font-weight: 600;">端口监听</span>
          </template>
          <div class="port-list">
            <el-empty v-if="ports.length===0" description="暂无端口数据" :image-size="60" style="padding:20px 0;" />
            <template v-else>
            <div v-for="port in ports" :key="port.port" class="port-item">
              <div class="port-info">
                <span class="status-dot" :class="port.listening ? 'online' : 'offline'">
                  <span class="dot"></span>
                </span>
                <div>
                  <div class="port-name">{{ port.service }}</div>
                  <div class="port-detail">{{ port.port }} · {{ port.protocol }}</div>
                </div>
              </div>
              <el-tag size="small" :type="port.listening ? 'success' : 'danger'" effect="light">
                {{ port.listening ? '监听中' : '未监听' }}
              </el-tag>
            </div>
            </template>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useServerStore } from '@/stores/server'
import { storeToRefs } from 'pinia'

const serverStore = useServerStore()
const { systemMetrics, processes, ports, loading, cpuColor, memColor, diskColor, error } = storeToRefs(serverStore)

let pollTimer = null

const refreshAll = async () => {
  await serverStore.fetchAll()
  if (!error.value) {
    ElMessage.success('数据已刷新')
  }
}

onMounted(async () => {
  await serverStore.fetchAll()
  pollTimer = setInterval(() => serverStore.fetchAll(), 10000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.port-list { display: flex; flex-direction: column; }
.port-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-color);
}
.port-item:last-child { border-bottom: none; }
.port-info { display: flex; align-items: center; gap: 10px; }
.port-name { font-size: 13px; font-weight: 500; color: var(--text-primary); }
.port-detail { font-size: 12px; color: var(--text-muted); }
</style>
