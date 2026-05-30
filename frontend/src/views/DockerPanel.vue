<template>
  <div class="docker-panel">
    <div class="page-header">
      <h1>馃惓 Docker 绠＄悊</h1>
      <div class="header-actions">
        <el-button type="primary" @click="fetchAll" :loading="loading" size="small">
          <el-icon><Refresh /></el-icon> 鍒锋柊
        </el-button>
      </div>
    </div>

    <el-row :gutter="16" class="stat-cards">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-value">{{ stats.running ?? "-" }}</div>
          <div class="stat-label">杩愯涓</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-value">{{ stats.total ?? "-" }}</div>
          <div class="stat-label">鎬诲鍣ㄦ暟</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-value">{{ containers.length }}</div>
          <div class="stat-label">瀹瑰櫒鍒楄〃</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-value">{{ images.length }}</div>
          <div class="stat-label">闀滃儚鏁</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="section-card">
      <template #header>
        <span>瀹瑰櫒鍒楄〃</span>
      </template>
      <el-table :data="containers" stripe v-loading="loading" max-height="400">
        <el-table-column prop="name" label="鍚嶇О" min-width="160" />
        <el-table-column prop="image" label="闀滃儚" min-width="200" />
        <el-table-column prop="status" label="..." min-width="180">
          <template #default="{ row }">
            <el-tag :type="row.status?.includes('Up') ? 'success' : 'danger'" size="small">
              {{ row.status?.substring(0, 30) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ports" label="绔彛" min-width="120" />
        <el-table-column label="鎿嶄綔" width="100" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="warning" @click="restartContainer(row.name)" :loading="restarting === row.name">
              閲嶅惎
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-card class="section-card">
          <template #header><span>闀滃儚鍒楄〃</span></template>
          <el-table :data="images" stripe v-loading="loading" max-height="300">
            <el-table-column prop="repo" label="浠撳簱" min-width="200" />
            <el-table-column prop="tag" label="鏍囩" width="100" />
            <el-table-column prop="size" label="澶у皬" width="100" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="section-card">
          <template #header><span>缃戠粶鍒楄〃</span></template>
          <el-table :data="networks" stripe v-loading="loading" max-height="300">
            <el-table-column prop="name" label="鍚嶇О" min-width="160" />
            <el-table-column prop="driver" label="椹卞姩" width="100" />
            <el-table-column prop="scope" label="鑼冨洿" width="80" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="section-card">
      <template #header><span>瀹瑰櫒鏃ュ織</span></template>
      <div style="display: flex; gap: 8px; margin-bottom: 12px;">
        <el-input v-model="logContainer" placeholder="杈撳叆瀹瑰櫒鍚嶇О鎴朓D" style="width: 300px;" size="small" />
        <el-button @click="fetchLogs" type="primary" size="small">鏌ョ湅鏃ュ織</el-button>
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
const restarting = ref("")
const containers = ref([])
const images = ref([])
const networks = ref([])
const stats = ref({})
const logs = ref("")
const logContainer = ref("")

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
    ElMessage.error("鑾峰彇Docker淇℃伅澶辫触")
  }
  loading.value = false
}

async function fetchLogs() {
  if (!logContainer.value) return ElMessage.warning("璇疯緭鍏ュ鍣ㄥ悕绉?)
  try {
    const r = await agentApi.get("/docker/logs", { params: { container: logContainer.value, lines: 100 } })
    logs.value = r.content || "鏃犳棩蹇?
  } catch (e) {
    logs.value = "鑾峰彇鏃ュ織澶辫触: " + (e.response?.data?.detail || e.message)
  }
}

async function restartContainer(name) {
  restarting.value = name
  try {
    const r = await agentApi.post("/docker/restart", { container_id: name, action: "restart" })
    ElMessage.success(r.ok ? `瀹瑰櫒 ${name} 宸查噸鍚痐 : (r.error || "宸叉彁浜ゅ鎵?))
  } catch (e) {
    ElMessage.error("閲嶅惎澶辫触: " + (e.response?.data?.detail || e.message))
  }
  restarting.value = ""
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
