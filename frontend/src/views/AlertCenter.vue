<template>
  <div class="alert-center">
    <h2>告警中心</h2>
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6" v-for="s in levelStats" :key="s.level">
        <div class="stat-card" :class="s.level">
          <div class="stat-label">{{ s.name }}</div>
          <div class="stat-num">{{ s.count }}</div>
          <div class="stat-sub">未解决: {{ s.unresolved }}</div>
        </div>
      </el-col>
    </el-row>
    <el-card shadow="never" style="margin-top:16px">
      <template #header>
        <span>告警列表</span>
        <el-select v-model="filterLevel" size="small" clearable placeholder="筛选等级" style="width:120px;margin-left:12px">
          <el-option v-for="(n, k) in levelMap" :key="k" :label="`${k} - ${n}`" :value="k" />
        </el-select>
        <el-button size="small" @click="fetchAlerts" style="margin-left:8px">刷新</el-button>
      </template>
      <el-table :data="alerts" stripe size="small" empty-text="暂无告警">
        <el-table-column label="等级" width="80">
          <template #default="{row}">
            <el-tag :type="tagType(row.level)" size="small">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="time" label="时间" width="80" />
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="detail" label="详情" min-width="200" show-overflow-tooltip />
        <el-table-column prop="source" label="来源" width="80" />
        <el-table-column label="状态" width="80">
          <template #default="{row}">
            <el-tag :type="row.resolved ? 'info' : 'danger'" size="small">{{ row.resolved ? '已解决' : '未解决' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{row}">
            <el-button v-if="!row.resolved" size="small" type="primary" link @click="doResolve(row.id)">解决</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getAlertList, getAlertStats, resolveAlert } from '@/api/alert'
import { ElMessage } from 'element-plus'

const levelMap = { P1: '紧急', P2: '严重', P3: '一般', P4: '观察' }
const alerts = ref([])
const stats = ref({})
const filterLevel = ref('')

const levelStats = computed(() => {
  return Object.entries(levelMap).map(([k, v]) => ({
    level: k, name: v,
    count: stats.value[k]?.count || 0,
    unresolved: stats.value[k]?.unresolved || 0,
  }))
})

function tagType(level) {
  return { P1: 'danger', P2: 'warning', P3: 'primary', P4: 'info' }[level] || 'info'
}

async function fetchAlerts() {
  try {
    const params = filterLevel.value ? { level: filterLevel.value } : {}
    const r = await getAlertList(params)
    alerts.value = r.alerts || []
  } catch { ElMessage.error('获取告警失败') }
}
async function fetchStats() {
  try { const r = await getAlertStats(); stats.value = r.stats || {} } catch {}
}
async function doResolve(id) {
  try { await resolveAlert(id); ElMessage.success('已标记解决'); fetchAlerts(); fetchStats() } catch { ElMessage.error('操作失败') }
}
onMounted(() => { fetchAlerts(); fetchStats() })
</script>

<style scoped>
.alert-center { padding: 24px; }
h2 { margin-bottom: 16px; font-size: 18px; }
.stats-row { margin-bottom: 0; }
.stat-card { padding: 16px; border-radius: 8px; color: #fff; text-align: center; }
.stat-card.P1 { background: #f56c6c; }
.stat-card.P2 { background: #e6a23c; }
.stat-card.P3 { background: #409eff; }
.stat-card.P4 { background: #909399; }
.stat-label { font-size: 13px; opacity: 0.9; }
.stat-num { font-size: 28px; font-weight: 700; margin: 4px 0; }
.stat-sub { font-size: 12px; opacity: 0.8; }
</style>
