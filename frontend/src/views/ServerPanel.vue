<template>
  <div class="server-panel">
    <div class="page-header"><h1>??/h1><p>AI      </p></div>
    <!-- ?-->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6">
        <el-card shadow="never"><template #header> CPU</template>
          <div class="metric-ring"><svg viewBox="0 0 100 100" width="80" height="80"><circle cx="50" cy="50" r="40" fill="none" stroke="#f0f0f0" stroke-width="8"/><circle cx="50" cy="50" r="40" fill="none" :stroke="cpu>80?'#ff4d4f':cpu>60?'#faad14':'#52c41a'' stroke-width="8" stroke-dasharray="251.2" :stroke-dashoffset="251.2-251.2*cpu/100" transform="rotate(-90,50,50)"/><text x="50" y="55" text-anchor="middle" font-size="18" fill="currentColor">{{ cpu }}%</text></svg></div>
          <div style="font-size:12px;color:var(--text-muted);text-align:center">{{ status?.cpu_count }}? {{ status?.load?.["1min"] }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never"><template #header>  <el-tag size="small" :type="memHealth" v-if="memPct">{{ memPct }}%</el-tag></template>
          <div class="metric-ring"><svg viewBox="0 0 100 100" width="80" height="80"><circle cx="50" cy="50" r="40" fill="none" stroke="#f0f0f0" stroke-width="8"/><circle cx="50" cy="50" r="40" fill="none" :stroke="memPct>85?'#ff4d4f':memPct>70?'#faad14':'#52c41a'' stroke-width="8" stroke-dasharray="251.2" :stroke-dashoffset="251.2-251.2*memPct/100" transform="rotate(-90,50,50)"/><text x="50" y="55" text-anchor="middle" font-size="18" fill="currentColor">{{ memPct }}%</text></svg></div>
          <div style="font-size:12px;color:var(--text-muted);text-align:center">? {{ cache?.reclaimable_gb }}GB</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never"><template #header> </template>
          <div class="metric-ring"><svg viewBox="0 0 100 100" width="80" height="80"><circle cx="50" cy="50" r="40" fill="none" stroke="#f0f0f0" stroke-width="8"/><circle cx="50" cy="50" r="40" fill="none" :stroke="diskPct>85?'#ff4d4f':diskPct>70?'#faad14':'#52c41a'' stroke-width="8" stroke-dasharray="251.2" :stroke-dashoffset="251.2-251.2*diskPct/100" transform="rotate(-90,50,50)"/><text x="50" y="55" text-anchor="middle" font-size="18" fill="currentColor">{{ diskPct }}%</text></svg></div>
          <div style="font-size:12px;color:var(--text-muted);text-align:center">{{ status?.disk?.used_gb }}/{{ status?.disk?.total_gb }} GB</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never"><template #header> Swap</template>
          <div style="font-size:28px;font-weight:700;color:var(--color-primary);text-align:center">{{ swapPct }}%</div>
          <div style="font-size:12px;color:var(--text-muted);text-align:center">{{ status?.swap?.used_gb }}/{{ status?.swap?.total_gb }} GB</div>
        </el-card>
      </el-col>
    </el-row>
    <!--  +  -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="8">
        <el-card shadow="never"><template #header>? <el-tag size="small" :type="memPct>80?'danger':'success''>{{ memPct>80?"":'' }}</el-tag></template>
          <div style="display:flex;flex-direction:column;gap:8px">
            <el-button type="primary" @click="doRelease('safe')" :loading="rlSafe" size="small"> (?</el-button>
            <el-button type="warning" @click="doRelease('aggressive')" :loading="rlAgg" size="small"> (?)</el-button>
            <el-button type="danger" @click="doRelease('max')" :loading="rlMax" size="small"> ??+Nginx+Docker)</el-button>
            <div v-if="releaseResult" style="font-size:12px;margin-top:4px">
              <div>? {{ releaseResult.before_percent }}% ?? {{ releaseResult.after_percent }}%</div>
              <div>: {{ releaseResult.freed_mb }}MB</div>
              <div v-for="a in releaseResult.actions" :key="a" style="color:var(--text-muted)">{{ a }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never"><template #header> (24h) <el-tag size="small" :type="trend?.trend_per_hour>0?'danger':'success''>: {{ trend?.trend_per_hour }}/h</el-tag></template>
          <div v-if="trend?.points?.length" style="height:160px;overflow:hidden">
            <svg viewBox="0 0 720 160" width="100%" height="160">
              <polyline :points="trendPoints" fill="none" stroke="#667eea" stroke-width="2"/>
              <polyline :points="trendFillPoints" fill="url(#memGrad)" opacity="0.3"/>
              <defs><linearGradient id="memGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#667eea"/><stop offset="100%" stop-color="#667eea" stop-opacity="0"/></linearGradient></defs>
            </svg>
          </div>
          <div v-if="trend?.prediction_12h" style="font-size:12px;color:var(--text-muted);margin-top:4px">12h? {{ trend.prediction_12h }}% <span :style="{color:trend.prediction_12h>85?'#ff4d4f':'#52c41a'}">{{ trend.prediction_12h>85?'':'?' }}</span></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never"><template #header> ?/template>
          <el-button @click="checkLeaks" :loading="leakLoading" size="small">?/el-button>
          <div v-if="leaks?.length" style="margin-top:8px;font-size:12px">
            <div v-for="l in leaks" :key="l.pid" style="padding:4px 0;border-bottom:1px solid #f0f0f0">
              <el-tag size="small" type="danger">{{ l.name }}</el-tag> PID={{ l.pid }} {{ l.growth_pct }}% ({{ l.old_mb }}{ l.new_mb }}MB)
            </div>
          </div>
          <div v-else-if="leakChecked" style="margin-top:8px;font-size:12px;color:#52c41a">?</div>
        </el-card>
      </el-col>
    </el-row>
    <!-- TOP -->
    <el-card shadow="never" style="margin-bottom:20px">
      <template #header> TOP</template>
      <el-table :data="topMem" stripe size="small" max-height="300">
        <el-table-column prop="name" label="? min-width="160"/>
        <el-table-column prop="pid" label="PID" width="80"/>
        <el-table-column prop="memory_mb" label='Status' width="100" sortable><template #default="{row}">{{ row.memory_mb }}MB</template></el-table-column>
        <el-table-column prop="memory_percent" label='Status' width="80"><template #default="{row}">{{ row.memory_percent?.toFixed(1) }}%</template></el-table-column>
        <el-table-column prop="cpu_percent" label="CPU" width="60"><template #default="{row}">{{ row.cpu_percent }}%</template></el-table-column>
        <el-table-column prop="uptime_hours" label="(h)" width="80"/>
        <el-table-column label='Status' width="80"><template #default="{row}"><el-button text size="small" type="danger" @click="killPid(row.pid)"></el-button></template></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from "vue"
import { getServerStatus, getMemoryTop, getMemoryTrend, getMemoryLeaks, releaseMemory, killServerProcess, cleanTemp } from "@/api/server"
import { ElMessage } from "element-plus"

const status = ref({}), topMem = ref([]), trend = ref(null), leaks = ref([])
const rlSafe=ref(false), rlAgg=ref(false), rlMax=ref(false), releaseResult=ref(null)
const leakLoading=ref(false), leakChecked=ref(false)

const cpu = computed(() => status.value?.cpu ?? 0)
const memPct = computed(() => status.value?.memory?.percent ?? 0)
const diskPct = computed(() => status.value?.disk?.percent ?? 0)
const swapPct = computed(() => status.value?.swap?.percent ?? 0)
const cache = computed(() => status.value?.cache ?? {})
const memHealth = computed(() => memPct.value > 85 ? "danger" : memPct.value > 70 ? "warning" : "success")

const trendPoints = computed(() => (trend.value?.points||[]).map((p,i)=>{const w=720,h=160,mx=trend.value.points.length-1||1;return `${i/mx*w},${h-p.memory/100*h}`}).join(''))
const trendFillPoints = computed(() => {const pts=trendPoints.value;if(!pts)return'';return pts+` ${trend.value.points.length-1},160 0,160`})

async function fetchAll() {
  try { status.value = await getServerStatus() } catch {}
  try { topMem.value = (await getMemoryTop(20)).processes || [] } catch {}
  try { trend.value = await getMemoryTrend(24) } catch {}
}
async function doRelease(mode) {
  const loader = {safe:rlSafe,aggressive:rlAgg,max:rlMax}[mode]
  loader.value = true
  try { releaseResult.value = await releaseMemory(mode); ElMessage.success(`${releaseResult.value.freed_mb}MB`) } catch { ElMessage.error('Error') }
  loader.value = false
  fetchAll()
}
async function checkLeaks() {
  leakLoading.value = true
  try { leaks.value = (await getMemoryLeaks()).leaks || []; leakChecked.value = true } catch { ElMessage.error("?) }
  leakLoading.value = false
}
async function killPid(pid) {
  try { await killServerProcess(pid); ElMessage.success(`?PID=${pid}`); fetchAll() } catch { ElMessage.error("") }
}
onMounted(fetchAll)
</script>
<style scoped>
.server-panel{padding:20px}
.page-header{margin-bottom:20px}.page-header h1{font-size:20px;margin:0 0 4px}.page-header p{font-size:13px;color:var(--text-muted);margin:0}
.metric-ring{text-align:center;margin-bottom:4px}
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>
