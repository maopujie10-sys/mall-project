<template>
  <div class="audit-page">
    <div class="page-header">
      -
      -
      <div class="header-stats">
        <el-tag> {{ stats.total || 0 }} </el-tag>
        <el-tag type="success"> {{ stats.today || 0 }} </el-tag>
      </div>
    </div>

    <div class="filters">
      <el-input v-model="filters.action" placeholder="..." clearable size="small" style="width:200px" />
      <el-select v-model="filters.risk" placeholder='Enter...' clearable size="small" style="width:120px">
        <el-option label="L1 ? value="L1" />
        <el-option label="L2 ? value="L2" />
        <el-option label="L3 ? value="L3" />
        <el-option label="L4 " value="L4" />
      </el-select>
      
      <el-button @click="fetchLogs" size="small">OK</el-button>
    </div>

    <el-table :data="logs" stripe size="small" v-loading="loading" max-height="600">
      <el-table-column label='Status' width="170">
        <template #default="{row}">{{ formatTime(row.time) }}</template>
      </el-table-column>
      <el-table-column label='Status' width="160">
        <template #default="{row}"><el-tag size="small">{{ row.action }}</el-tag></template>
      </el-table-column>
      <el-table-column :label="\('audit.title')" width="200" show-overflow-tooltip>
        <template #default="{row}">{{ row.target }}</template>
      </el-table-column>
      <el-table-column :label="\('audit.title')" min-width="250" show-overflow-tooltip>
        <template #default="{row}">{{ row.detail }}</template>
      </el-table-column>
      <el-table-column label='Status' width="80">
        <template #default="{row}">
          <el-tag :type="riskType(row.risk)" size="small">{{ row.risk }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="? width="80">
        <template #default="{row}">{{ row.user }}</template>
      </el-table-column>
    </el-table>

    <div v-if="pages > 1" style="display:flex;justify-content:center;margin-top:16px">
      <el-pagination background layout="prev,pager,next" :total="total" :page-size="50" @current-change="changePage" />
    </div>
    <el-empty v-if="!loading && logs.length===0" description="" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { agentApi } from "@/api"

const logs = ref([])
const loading = ref(false)
const total = ref(0)
const pages = ref(0)
const page = ref(1)
const stats = ref({})
const filters = ref({ action: '', risk: '' })

function riskType(r) {
  return { L1: "success", L2: "warning", L3: "danger", L4: "danger" }[r] || "info"
}

function formatTime(t) {
  if (!t) return "-"
  return t.replace("T", '').substring(0, 19)
}

async function fetchLogs() {
  loading.value = true
  try {
    const params = { page: page.value, size: 50 }
    if (filters.value.action) params.action = filters.value.action
    if (filters.value.risk) params.risk = filters.value.risk
    const r = await agentApi.get("/audit", { params })
    logs.value = r.logs || []
    total.value = r.total || 0
    pages.value = r.pages || 0
  } catch { logs.value = [] }
  loading.value = false
}

async function fetchStats() {
  try {
    const r = await agentApi.get("/audit/stats")
    stats.value = r || {}
  } catch { stats.value = {} }
}

function changePage(p) {
  page.value = p
  fetchLogs()
}

onMounted(() => { fetchLogs(); fetchStats() })
</script>

<style scoped>
.audit-page { padding: 20px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px; font-size: 18px; }
.page-header p { margin: 0 0 8px; color: #999; font-size: 13px; }
.header-stats { display: flex; gap: 8px; }
.filters { display: flex; gap: 12px; margin-bottom: 16px; align-items: center; }
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>
