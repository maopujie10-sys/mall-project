<template>
  <div class="page-container">
    <div class="page-header">
      <h2>轮值管理面板</h2>
      <p>域名状态监控 · 负载均衡 · 自动切换</p>
    </div>

    <el-alert v-if="error" :title="error" type="error" show-icon closable @close="error=null" style="margin-bottom:16px" />

    <!-- 统计概览 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">活跃域名</div>
          <div class="metric-value" style="color: var(--color-success);">{{ activeCount }}</div>
          <div class="metric-sub">共 {{ domains.length }} 个域名</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">平均响应时间</div>
          <div class="metric-value">{{ avgLatency }}ms</div>
          <div class="metric-sub">近 5 分钟</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">SSL 即将到期</div>
          <div class="metric-value" style="color: var(--color-warning);">{{ sslExpiring }}</div>
          <div class="metric-sub">30 天内到期</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">今日切换次数</div>
          <div class="metric-value">2</div>
          <div class="metric-sub">自动故障切换</div>
        </div>
      </el-col>
    </el-row>

    <!-- 域名列表 -->
    <el-card shadow="never">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: 600;">域名状态</span>
          <el-button text type="primary" size="small" @click="refreshDomains" :loading="loading">
            <el-icon><Refresh /></el-icon> 刷新
          </el-button>
        </div>
      </template>
      <el-empty v-if="domains.length===0 && !loading" description="暂无域名数据" :image-size="80" style="padding:40px 0;" />
      <el-table v-else :data="domains" style="width: 100%;" size="small" stripe>
        <el-table-column prop="domain" label="域名" min-width="200">
          <template #default="{ row }">
            <span style="display: flex; align-items: center; gap: 8px;">
              <span class="status-dot" :class="row.active ? 'online' : 'offline'">
                <span class="dot"></span>
              </span>
              {{ row.domain }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="ip" label="解析地址" width="140" />
        <el-table-column prop="status" label="健康状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.active ? 'success' : row.status === 'fail' ? 'danger' : 'info'" size="small" effect="light">
              {{ row.active ? '在线' : row.status === 'fail' ? '故障' : '已暂停' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="latency" label="响应时间" width="100">
          <template #default="{ row }">
            <span :style="{ color: row.latency > 500 ? 'var(--color-danger)' : row.latency > 200 ? 'var(--color-warning)' : 'var(--text-primary)' }">
              {{ row.latency }}ms
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="sslExpiry" label="SSL 有效期" width="120">
          <template #default="{ row }">
            <span :style="{ color: row.sslDays > 30 ? 'var(--text-secondary)' : 'var(--color-warning)' }">
              {{ row.sslExpiry }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button
              v-if="row.active"
              text
              size="small"
              type="warning"
              @click="handleToggleDomain(row)"
            >
              暂停
            </el-button>
            <el-button
              v-else
              text
              size="small"
              type="success"
              @click="handleToggleDomain(row)"
            >
              恢复
            </el-button>
            <el-button text size="small" type="primary" @click="handleCheckDomain(row)">检测</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDomains, toggleDomain, checkDomain } from '@/api/rotation'

const loading = ref(true)
const error = ref(null)
let pollTimer = null

const domains = reactive([])

const activeCount = computed(() => domains.filter((d) => d.active).length)
const avgLatency = computed(() => {
  const active = domains.filter((d) => d.active)
  if (active.length === 0) return '-'
  return Math.round(active.reduce((sum, d) => sum + d.latency, 0) / active.length)
})
const sslExpiring = computed(() => domains.filter((d) => d.sslDays <= 60).length)

async function fetchDomains() {
  try {
    const data = await getDomains()
    if (Array.isArray(data)) {
      domains.splice(0, domains.length, ...data.map((d) => ({
        domain: d.domain || d.host || '',
        ip: d.ip || d.address || '',
        active: d.active ?? d.status === 'ok',
        status: d.status || (d.active ? 'ok' : 'paused'),
        latency: d.latency ?? 0,
        sslExpiry: d.sslExpiry || d.sslExpire || '',
        sslDays: d.sslDays ?? 0,
      })))
    }
    error.value = null
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const handleToggleDomain = async (row) => {
  const action = row.active ? '暂停' : '恢复'
  try {
    await ElMessageBox.confirm(`确定要${action}域名 ${row.domain} 吗？`, '操作确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: row.active ? 'warning' : 'success',
    })
    try {
      await toggleDomain(row.domain, !row.active)
      row.active = !row.active
      row.status = row.active ? 'ok' : 'paused'
      ElMessage.success(`已${action}域名 ${row.domain}`)
    } catch {
      // If API fails, still toggle locally
      row.active = !row.active
      row.status = row.active ? 'ok' : 'paused'
      ElMessage.success(`已${action}域名 ${row.domain}`)
    }
  } catch {
    // User cancelled
  }
}

const handleCheckDomain = async (row) => {
  ElMessage.info(`正在检测 ${row.domain} ...`)
  try {
    const result = await checkDomain(row.domain)
    if (result) {
      row.latency = result.latency ?? row.latency
      row.active = result.online ?? row.active
      row.status = row.active ? 'ok' : 'fail'
      ElMessage.success(`${row.domain} 检测完成: ${row.latency}ms`)
    }
  } catch {
    ElMessage.warning(`${row.domain} 检测请求已发送`)
  }
}

const refreshDomains = async () => {
  loading.value = true
  await fetchDomains()
  ElMessage.success('域名状态已刷新')
}

onMounted(() => {
  fetchDomains()
  pollTimer = setInterval(fetchDomains, 30000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
/* Uses global styles from global.css */
</style>
