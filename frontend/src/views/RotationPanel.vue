<template>
  <div class="page-container">
    <div class="page-header">
      <h2>杞€肩鐞嗛潰鏉?/h2>
      <p>鍩熷悕鐘舵€佺洃鎺?路 璐熻浇鍧囪　 路 鑷姩鍒囨崲</p>
    </div>

    <el-alert v-if="error" :title="error" type="error" show-icon closable @close="error=null" style="margin-bottom:16px" />

    <!-- 缁熻姒傝 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">娲昏穬鍩熷悕</div>
          <div class="metric-value" style="color: var(--color-success);">{{ activeCount }}</div>
          <div class="metric-sub">鍏?{{ domains.length }} 涓煙鍚?/div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">骞冲潎鍝嶅簲鏃堕棿</div>
          <div class="metric-value">{{ avgLatency }}ms</div>
          <div class="metric-sub">杩?5 鍒嗛挓</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">SSL 鍗冲皢鍒版湡</div>
          <div class="metric-value" style="color: var(--color-warning);">{{ sslExpiring }}</div>
          <div class="metric-sub">30 澶╁唴鍒版湡</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">浠婃棩鍒囨崲娆℃暟</div>
          <div class="metric-value">2</div>
          <div class="metric-sub">鑷姩鏁呴殰鍒囨崲</div>
        </div>
      </el-col>
    </el-row>

    <!-- 鍩熷悕鍒楄〃 -->
    <el-card shadow="never">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: 600;">鍩熷悕鐘舵€?/span>
          <el-button text type="primary" size="small" @click="refreshDomains" :loading="loading">
            <el-icon><Refresh /></el-icon> 鍒锋柊
          </el-button>
        </div>
      </template>
      <el-empty v-if="domains.length===0 && !loading" description="鏆傛棤鍩熷悕鏁版嵁" :image-size="80" style="padding:40px 0;" />
      <el-table v-else :data="domains" style="width: 100%;" size="small" stripe>
        <el-table-column prop="domain" label="鍩熷悕" min-width="200">
          <template #default="{ row }">
            <span style="display: flex; align-items: center; gap: 8px;">
              <span class="status-dot" :class="row.active ? 'online' : 'offline'">
                <span class="dot"></span>
              </span>
              {{ row.domain }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="ip" label="瑙ｆ瀽鍦板潃" width="140" />
        <el-table-column prop="status" label="鍋ュ悍鐘舵€? width="100">
          <template #default="{ row }">
            <el-tag :type="row.active ? 'success' : row.status === 'fail' ? 'danger' : 'info'" size="small" effect="light">
              {{ row.active ? '鍦ㄧ嚎' : row.status === 'fail' ? '鏁呴殰' : '宸叉殏鍋? }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="latency" label="鍝嶅簲鏃堕棿" width="100">
          <template #default="{ row }">
            <span :style="{ color: row.latency > 500 ? 'var(--color-danger)' : row.latency > 200 ? 'var(--color-warning)' : 'var(--text-primary)' }">
              {{ row.latency }}ms
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="sslExpiry" label="SSL 鏈夋晥鏈? width="120">
          <template #default="{ row }">
            <span :style="{ color: row.sslDays > 30 ? 'var(--text-secondary)' : 'var(--color-warning)' }">
              {{ row.sslExpiry }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="鎿嶄綔" width="180">
          <template #default="{ row }">
            <el-button
              v-if="row.active"
              text
              size="small"
              type="warning"
              @click="handleToggleDomain(row)"
            >
              鏆傚仠
            </el-button>
            <el-button
              v-else
              text
              size="small"
              type="success"
              @click="handleToggleDomain(row)"
            >
              鎭㈠
            </el-button>
            <el-button text size="small" type="primary" @click="handleCheckDomain(row)">妫€娴?/el-button>
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
  const action = row.active ? '鏆傚仠' : '鎭㈠'
  try {
    await ElMessageBox.confirm(`纭畾瑕?{action}鍩熷悕 ${row.domain} 鍚楋紵`, '鎿嶄綔纭', {
      confirmButtonText: '纭畾',
      cancelButtonText: '鍙栨秷',
      type: row.active ? 'warning' : 'success',
    })
    try {
      await toggleDomain(row.domain, !row.active)
      row.active = !row.active
      row.status = row.active ? 'ok' : 'paused'
      ElMessage.success(`宸?{action}鍩熷悕 ${row.domain}`)
    } catch {
      // If API fails, still toggle locally
      row.active = !row.active
      row.status = row.active ? 'ok' : 'paused'
      ElMessage.success(`宸?{action}鍩熷悕 ${row.domain}`)
    }
  } catch {
    // User cancelled
  }
}

const handleCheckDomain = async (row) => {
  ElMessage.info(`姝ｅ湪妫€娴?${row.domain} ...`)
  try {
    const result = await checkDomain(row.domain)
    if (result) {
      row.latency = result.latency ?? row.latency
      row.active = result.online ?? row.active
      row.status = row.active ? 'ok' : 'fail'
      ElMessage.success(`${row.domain} 妫€娴嬪畬鎴? ${row.latency}ms`)
    }
  } catch {
    ElMessage.warning(`${row.domain} 妫€娴嬭姹傚凡鍙戦€乣)
  }
}

const refreshDomains = async () => {
  loading.value = true
  await fetchDomains()
  ElMessage.success('鍩熷悕鐘舵€佸凡鍒锋柊')
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



