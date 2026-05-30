<template>
  <div class="docker-panel">
    <div class="page-header">
      <h1> Docker </h1>
      <div class="header-actions">
        <el-button type="primary" @click="fetchAll" :loading="loading" size="small">
          <el-icon><Refresh /></el-icon> 
        </el-button>
      </div>
    </div>

    <el-row :gutter="16" class="stat-cards">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-value">{{ stats.running ?? "-" }}</div>
          <div class="stat-label"></div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-value">{{ stats.total ?? "-" }}</div>
          -
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-value">{{ containers.length }}</div>
          <div class="stat-label">{{ $t('docker.title') }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-value">{{ images.length }}</div>
          <div class="stat-label"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="section-card">
      <template #header>
        <span>{{ $t('docker.title') }}</span>
      </template>
      <el-table :data="containers" stripe v-loading="loading" max-height="400">
        <el-table-column prop="name" :label="$t('docker.title')" min-width="160" />
        <el-table-column prop="image" label='Status' min-width="200" />
        <el-table-column prop="status" label="状态" min-width="180">
          <template #default="{ row }">
            <el-tag :type="row.status?.includes('Up') ? 'success' : 'danger'" size="small">
              {{ row.status?.substring(0, 30) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ports" :label="$t('docker.title')" min-width="120" />
        <el-table-column label='Status' width="100" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="warning" @click="restartContainer(row.name)" :loading="restarting === row.name">OK</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-card class="section-card">
          <template #header><span>{{ $t('docker.title') }}</span></template>
          <el-table :data="images" stripe v-loading="loading" max-height="300">
            <el-table-column prop="repo" label='Status' min-width="200" />
            <el-table-column prop="tag" :label="$t('docker.title')" width="100" />
            <el-table-column prop="size" :label="$t('docker.title')" width="100" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="section-card">
          <template #header><span>{{ $t('docker.title') }}</span></template>
          <el-table :data="networks" stripe v-loading="loading" max-height="300">
            <el-table-column prop="name" :label="$t('docker.title')" min-width="160" />
            <el-table-column prop="driver" label='Status' width="100" />
            <el-table-column prop="scope" label='Status' width="80" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="section-card">
      <template #header>-</template>
      <div style="display: flex; gap: 8px; margin-bottom: 12px;">
        <el-input v-model="logContainer" placeholder="D" style="width: 300px;" size="small" />
        <el-button @click="fetchLogs" type="primary" size="small"></el-button>
      </div>
      <el-input type="textarea" :rows="8" :value="logs" readonly style="font-family: monospace; font-size: 12px;" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { agentApi } from "@/api"
import { ElMessage } from "element-plus"

const loading = ref(false)
const restarting = ref('')
const containers = ref([])
const images = ref([])
const networks = ref([])
const stats = ref({})
const logs = ref('')
const logContainer = ref('')

async function fetchAll() {
  loading.value = true
  try {
    const [ps, st, imgs, nets] = await Promise.all([
      agentApi.get("/docker/ps"),
      agentApi.get("/docker/status"),
      agentApi.get("/docker/images"),
      agentApi.get("/docker/network"),
    ])
    containers.value = ps.containers || []
    stats.value = st
    images.value = imgs.images || []
    networks.value = nets.networks || []
  } catch (e) {
    ElMessage.error("Docker")
  }
  loading.value = false
}

async function fetchLogs() {
  if (!logContainer.value) return ElMessage.warning("请选择容器")
  try {
    const r = await agentApi.get("/docker/logs", { params: { container: logContainer.value, lines: 100 } })
    logs.value = r.content || ""
  } catch (e) {
    logs.value = ": " + (e.response?.data?.detail || e.message)
  }
}

async function restartContainer(name) {
  restarting.value = name
  try {
    const r = await agentApi.post("/docker/restart", { container_id: name, action: "restart" })
    ElMessage.success(r.ok ? `已重启 ${name}` : (r.error || ""))
  } catch (e) {
    ElMessage.error(": " + (e.response?.data?.detail || e.message))
  }
  restarting.value = ''
}

onMounted(fetchAll)
</script>

<style scoped>
.docker-panel { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h1 { margin: 0; font-size: 20px; }
.stat-cards { margin-bottom: 16px; }
.stat-value { font-size: 28px; font-weight: 700; color: var(--color-primary); }
.stat-label { font-size: 13px; color: #666; margin-top: 4px; }
.section-card { margin-bottom: 16px; }
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>
