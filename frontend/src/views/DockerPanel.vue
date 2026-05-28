<template>
  <div class="docker-panel">
    <div class="page-header">
      <h1>棣冩儞 Docker 缁狅紕鎮?/h1>
      <div class="header-actions">
        <el-button type="primary" @click="fetchAll" :loading="loading" size="small">
          <el-icon><Refresh /></el-icon> 閸掗攱鏌?        </el-button>
      </div>
    </div>

    <el-row :gutter="16" class="stat-cards">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-value">{{ stats.running ?? "-" }}</div>
          <div class="stat-label">鏉╂劘顢戞稉?/div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-value">{{ stats.total ?? "-" }}</div>
          <div class="stat-label">閹顔愰崳銊︽殶</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-value">{{ containers.length }}</div>
          <div class="stat-label">鐎圭懓娅掗崚妤勩€?/div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-value">{{ images.length }}</div>
          <div class="stat-label">闂€婊冨剼閺?/div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="section-card">
      <template #header>
        <span>鐎圭懓娅掗崚妤勩€?/span>
      </template>
      <el-table :data="containers" stripe v-loading="loading" max-height="400">
        <el-table-column prop="name" label="閸氬秶袨" min-width="160" />
        <el-table-column prop="image" label="闂€婊冨剼" min-width="200" />
        <el-table-column prop="status" label="閻樿埖鈧? min-width="180">
          <template #default="{ row }">
            <el-tag :type="row.status?.includes('Up') ? 'success' : 'danger'" size="small">
              {{ row.status?.substring(0, 30) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ports" label="缁旑垰褰? min-width="120" />
        <el-table-column label="閹垮秳缍? width="100" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="warning" @click="restartContainer(row.name)" :loading="restarting === row.name">
              闁插秴鎯?            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-card class="section-card">
          <template #header><span>闂€婊冨剼閸掓銆?/span></template>
          <el-table :data="images" stripe v-loading="loading" max-height="300">
            <el-table-column prop="repo" label="娴犳挸绨? min-width="200" />
            <el-table-column prop="tag" label="閺嶅洨顒? width="100" />
            <el-table-column prop="size" label="婢堆冪毈" width="100" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="section-card">
          <template #header><span>缂冩垹绮堕崚妤勩€?/span></template>
          <el-table :data="networks" stripe v-loading="loading" max-height="300">
            <el-table-column prop="name" label="閸氬秶袨" min-width="160" />
            <el-table-column prop="driver" label="妞瑰崬濮? width="100" />
            <el-table-column prop="scope" label="閼煎啫娲? width="80" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="section-card">
      <template #header><span>鐎圭懓娅掗弮銉ョ箶</span></template>
      <div style="display: flex; gap: 8px; margin-bottom: 12px;">
        <el-input v-model="logContainer" placeholder="鏉堟挸鍙嗙€圭懓娅掗崥宥囆為幋鏈揇" style="width: 300px;" size="small" />
        <el-button @click="fetchLogs" type="primary" size="small">閺屻儳婀呴弮銉ョ箶</el-button>
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
    ElMessage.error("閼惧嘲褰嘍ocker娣団剝浼呮径杈Е")
  }
  loading.value = false
}

async function fetchLogs() {
  if (!logContainer.value) return ElMessage.warning("鐠囩柉绶崗銉ヮ啇閸ｃ劌鎮曠粔?)
  try {
    const r = await agentApi.get("/docker/logs", { params: { container: logContainer.value, lines: 100 } })
    logs.value = r.content || "閺冪姵妫╄箛?
  } catch (e) {
    logs.value = "閼惧嘲褰囬弮銉ョ箶婢惰精瑙? " + (e.response?.data?.detail || e.message)
  }
}

async function restartContainer(name) {
  restarting.value = name
  try {
    const r = await agentApi.post("/docker/restart", { container_id: name, action: "restart" })
    ElMessage.success(r.ok ? `鐎圭懓娅?${name} 瀹告煡鍣搁崥鐥?: (r.error || "瀹稿弶褰佹禍銈咁吀閹?))
  } catch (e) {
    ElMessage.error("闁插秴鎯庢径杈Е: " + (e.response?.data?.detail || e.message))
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
</style>
