<template>
  <div class="page-container">
    <div class="page-header">
      <h2>?/h2>
      <p style="color:var(--text-muted);font-size:13px">?   ?/p>
    </div>
    <el-alert v-if="error" :title="error" type="error" show-icon closable @close="error=null" style="margin-bottom:16px" />

    
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6"><div class="metric-card"><div class="metric-label">?/div><div class="metric-value">{{ domains.length }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card">-<div class="metric-value" style="color:#52c41a">{{ domains.filter(d=>d.active).length }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">{{ \('rotation.title') }}</div><div class="metric-value" style="color:#ff4d4f">{{ domains.filter(d=>!d.active&&d.status==='fail').length }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">{{ \('rotation.title') }}</div><div class="metric-value">{{ avgLatency }}ms</div></div></el-col>
    </el-row>

    <!-- ?-->
    <div style="display:flex;gap:10px;margin-bottom:16px">
      <el-button type="primary" @click="addDialogVisible=true">?</el-button>
      <el-button @click="refreshDomains" :loading="loading">?/el-button>
      <el-button @click="handleCheckAll" :loading="checkingAll">?/el-button>
    </div>

    
    <el-card shadow="never">
      <el-table :data="domains" stripe size="small" style="width:100%">
        <el-table-column label='' min-width="200">
          <template #default="{row}">
            <span style="display:flex;align-items:center;gap:8px">
              <span class="status-dot" :class="row.active?'online':'offline''><span class="dot">{{ \('rotation.title') }}</span></span>
              {{ row.domain }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="type" label='' width="90">
          <template #default="{row}"><el-tag size="small">{{ row.type||'? }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="ip" label="IP" width="140" />
        <el-table-column prop="latency" label='' width="80">
          <template #default="{row}"><span :style="{color:row.latency>800?'#ff4d4f':row.latency>300?'#faad14':'#52c41a'}">{{ row.latency }}ms</span></template>
        </el-table-column>
        <el-table-column prop="status" :label="\('rotation.title')" width="90">
          <template #default="{row}">
            <el-tag :type="row.active?'success':row.status==='fail'?'danger':'info'' size="small">{{ row.active?'':row.status==='fail'?'':'' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label='' width="100">
          <template #default="{row}">
            <el-input-number v-model="row.weight" :min="1" :max="10" size="small" controls-position="right" style="width:80px" @change="(v)=>updateWeight(row,v)" />
          </template>
        </el-table-column>
        <el-table-column label='' width="220">
          <template #default="{row}">
            <el-button text size="small" :type="row.active?'warning':'success'' @click="handleToggle(row)">{{ row.active?'':'' }}</el-button>
            <el-button text size="small" type="primary" @click="handleCheckOne(row)">?/el-button>
            <el-button text size="small" type="danger" @click="handleRemove(row)">OK</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="domains.length===0&&!loading" description="? :image-size="80" style="padding:60px 0" />
    </el-card>

    <!-- ===== ?===== -->
    <el-card shadow="never" style="margin-top:20px">
      <template #header><span style="font-weight:600">?+  + </span></template>
      <div v-if="!twoLevelConfig">?/div>
      <div v-else>
        <div style="margin-bottom:16px">
          -{{ twoLevelConfig.primary?.main || '-' }}
          <span v-if="twoLevelConfig.primary?.children">{ twoLevelConfig.primary.children.length }} ?/span>
        </div>
        <div v-for="g in (twoLevelConfig.rotation||[])" :key="g.id" style="padding:12px;background:rgba(102,126,234,0.05);border-radius:8px;margin-bottom:8px">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div><strong>{{ g.main }}</strong><el-tag size="small" style="margin-left:8px"> {{ g.weight }}</el-tag></div>
            <div style="display:flex;gap:6px">
              <el-button text size="small" :type="g.enabled!==false?'success':'info'' @click="toggleRotationGroup(g.id)">{{ g.enabled!==false?'?:'? }}</el-button>
              <el-button text size="small" type="primary" @click="showAddSubDomain(g)">??/el-button>
            </div>
          </div>
          <div v-if="g.children?.length" style="margin-top:8px;padding-left:16px;font-size:13px;color:var(--text-muted)">
            <div v-for="c in g.children" :key="c.host" style="display:flex;justify-content:space-between;padding:4px 0">
              <span>{{ c.host }}?{{ c.weight }}?/span>
              <el-button text size="small" type="danger" @click="removeSubDomain(g.id,c.host)">OK</el-button>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    
    <el-dialog v-model="addDialogVisible" title='' width="420px">
      <el-form label-position="top">
        <el-form-item label=''>
          <el-input v-model="newDomain.domain" placeholder="example.com" />
        </el-form-item>
        <el-form-item label=''>
          <el-select v-model="newDomain.type" style="width:100%">
            <el-option label="? value="? />
            <el-option label="? value="? />
            <el-option label="CDN" value="CDN" />
          </el-select>
        </el-form-item>
        <el-form-item label="?-10?>
          <el-input-number v-model="newDomain.weight" :min="1" :max="10" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible=false">OK</el-button>
        <el-button type="primary" @click="handleAdd" :loading="adding">OK</el-button>
      </template>
    </el-dialog>

    <!-- ?-->
    <el-dialog v-model="subDialogVisible" :title=''?'+(subGroup?.main||'')+' ?" width="400px">
      <el-form label-position="top">
        <el-form-item label="?>
          <el-input v-model="newSubDomain.host" placeholder="shop.example.com" />
        </el-form-item>
        <el-form-item label=''>
          <el-input-number v-model="newSubDomain.weight" :min="1" :max="10" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="subDialogVisible=false">OK</el-button>
        <el-button type="primary" @click="handleAddSub" :loading="addingSub">OK</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import {
  getDomains, toggleDomain, checkDomain, addDomain, removeDomain, setDomainWeight,
  getTwoLevelConfig, toggleRotationGroup as apiToggleGroup, addSubdomain, removeSubdomain, getRotationHistory
} from "@/api/rotation"

const loading = ref(true)
const checkingAll = ref(false)
const error = ref(null)
let pollTimer = null
const domains = reactive([])
const twoLevelConfig = ref(null)


const addDialogVisible = ref(false)
const adding = ref(false)
const newDomain = reactive({ domain: '', type: "?, weight: 3 })

// ?
const subDialogVisible = ref(false)
const addingSub = ref(false)
const subGroup = ref(null)
const newSubDomain = reactive({ host: '', weight: 3 })

const avgLatency = computed(() => {
  const a = domains.filter(d => d.active && d.latency)
  return a.length ? Math.round(a.reduce((s, d) => s + d.latency, 0) / a.length) : "-"
})

async function fetchDomains() {
  try {
    const data = await getDomains()
    if (Array.isArray(data)) {
      domains.splice(0, domains.length, ...data.map(d => ({
        domain: d.domain || d.host || '',
        ip: d.ip || d.address || '',
        active: d.active ?? d.status === "ok",
        status: d.status || (d.active ? "ok" : "paused"),
        latency: d.latency ?? 0,
        type: d.type || "?,
        weight: d.weight ?? 3,
        sslExpiry: d.sslExpiry || '',
        sslDays: d.sslDays ?? 0,
      })))
    }
  } catch (e) { error.value = e.message }
  finally { loading.value = false }
}

async function fetchTwoLevelConfig() {
  try {
    const res = await getTwoLevelConfig()
    if (res?.config) twoLevelConfig.value = res.config
  } catch {}
}

async function handleAdd() {
  if (!newDomain.domain) { ElMessage.warning("?); return }
  adding.value = true
  try {
    await addDomain(newDomain.domain, newDomain.type)
    ElMessage.success(`?${newDomain.domain}`)
    addDialogVisible.value = false
    newDomain.domain = ''
    await fetchDomains()
  } catch (e) { ElMessage.error(e.message) }
  finally { adding.value = false }
}

async function handleRemove(row) {
  try {
    await ElMessageBox.confirm(` ${row.domain}, "", { type: "warning" })
    await removeDomain(row.domain)
    ElMessage.success(`?${row.domain}`)
    await fetchDomains()
  } catch {}
}

async function handleToggle(row) {
  try {
    await toggleDomain(row.domain, !row.active)
    row.active = !row.active
    row.status = row.active ? "ok" : "paused"
    ElMessage.success(row.active ? "? : "?)
  } catch { ElMessage.error('Error') }
}

async function handleCheckOne(row) {
  ElMessage.info(`?${row.domain}...`)
  try {
    const r = await checkDomain(row.domain)
    if (r) { row.latency = r.latency ?? row.latency; row.active = r.online ?? row.active }
    ElMessage.success(`${row.domain} )
  } catch { ElMessage.warning("?) }
}

async function handleCheckAll() {
  checkingAll.value = true
  try {
    await Promise.all(domains.map(d => checkDomain(d.domain).catch(()=>{})))
    await fetchDomains()
    ElMessage.success("?)
  } catch {}
  finally { checkingAll.value = false }
}

async function updateWeight(row, val) {
  try { await setDomainWeight(row.domain, val) } catch {}
}

async function toggleRotationGroup(id) {
  try {
    await apiToggleGroup(id)
    await fetchTwoLevelConfig()
    ElMessage.success("?)
  } catch { ElMessage.error('Error') }
}

function showAddSubDomain(g) {
  subGroup.value = g
  newSubDomain.host = ''
  newSubDomain.weight = 3
  subDialogVisible.value = true
}

async function handleAddSub() {
  if (!newSubDomain.host) { ElMessage.warning(""); return }
  addingSub.value = true
  try {
    await addSubdomain(subGroup.value.id, newSubDomain.host, newSubDomain.weight)
    ElMessage.success('OK')
    subDialogVisible.value = false
    await fetchTwoLevelConfig()
  } catch (e) { ElMessage.error(e.message) }
  finally { addingSub.value = false }
}

async function removeSubDomain(groupId, host) {
  try {
    await ElMessageBox.confirm(`?${host}, "", { type: "warning" })
    await removeSubdomain(groupId, host)
    ElMessage.success("?)
    await fetchTwoLevelConfig()
  } catch {}
}

const refreshDomains = async () => {
  loading.value = true
  await fetchDomains()
  ElMessage.success("?)
}

onMounted(() => {
  fetchDomains()
  fetchTwoLevelConfig()
  pollTimer = setInterval(fetchDomains, 30000)
})
onUnmounted(() => { if (pollTimer) clearInterval(pollTimer) })
</script>
<style scoped>
.metric-card { background: rgba(22,33,62,0.7);border:1px solid var(--border-color);border-radius:10px;padding:16px;text-align:center}
.metric-label { font-size:12px;color:var(--text-muted);margin-bottom:4px }
.metric-value { font-size:28px;font-weight:700 }
.status-dot { display:flex;align-items:center }
.dot { width:8px;height:8px;border-radius:50%;display:inline-block }
.online .dot { background:#52c41a;box-shadow:0 0 6px rgba(82,196,26,.5) }
.offline .dot { background:#ff4d4f;box-shadow:0 0 6px rgba(255,77,79,.4) }
:deep(.el-input-number--small) { width:80px }
:deep(.el-input-number--small .el-input-number__decrease),:deep(.el-input-number--small .el-input-number__increase) { width:20px }
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>
