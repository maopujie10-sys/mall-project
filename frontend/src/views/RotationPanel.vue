<template>
  <div class="page-container">
    <div class="page-header">
      <h2>杞€肩鐞嗙郴缁</h2>
      <p style="color:var(--text-muted);font-size:13px">浼佷笟绾ц礋杞藉潎琛路 鏁呴殰鑷姩鍒囨崲 路 澶氱骇鍩熷悕杞€</p>
    </div>
    <el-alert v-if="error" :title="error" type="error" show-icon closable @close="error=null" style="margin-bottom:16px" />

    <!-- 缁熻 -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6"><div class="metric-card"><div class="metric-label">鎬诲煙鍚</div><div class="metric-value">{{ domains.length }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">鍦ㄧ嚎</div><div class="metric-value" style="color:#52c41a">{{ domains.filter(d=>d.active).length }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">鏁呴殰</div><div class="metric-value" style="color:#ff4d4f">{{ domains.filter(d=>!d.active&&d.status==='fail').length }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">骞冲潎鍝嶅簲</div><div class="metric-value">{{ avgLatency }}ms</div></div></el-col>
    </el-row>

    <!-- 鎿嶄綔鏍?-->
    <div style="display:flex;gap:10px;margin-bottom:16px">
      <el-button type="primary" @click="addDialogVisible=true">锛娣诲姞鍩熷悕</el-button>
      <el-button @click="refreshDomains" :loading="loading">鍒锋柊鐘舵€</el-button>
      <el-button @click="handleCheckAll" :loading="checkingAll">妫€娴嬪叏閮</el-button>
    </div>

    <!-- 鍩熷悕鍒楄〃 -->
    <el-card shadow="never">
      <el-table :data="domains" stripe size="small" style="width:100%">
        <el-table-column label="鍩熷悕" min-width="200">
          <template #default="{row}">
            <span style="display:flex;align-items:center;gap:8px">
              <span class="status-dot" :class="row.active?'online':'offline'"><span class="dot"></span></span>
              {{ row.domain }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="绫诲瀷" width="90">
          <template #default="{row}"><el-tag size="small">{{ row.type||'杞€' }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="ip" label="瑙ｆ瀽IP" width="140" />
        <el-table-column prop="latency" label="鍝嶅簲" width="80">
          <template #default="{row}"><span :style="{color:row.latency>800?'#ff4d4f':row.latency>300?'#faad14':'#52c41a'}">{{ row.latency }}ms</span></template>
        </el-table-column>
        <el-table-column prop="status" label="鍋ュ悍" width="90">
          <template #default="{row}">
            <el-tag :type="row.active?'success':row.status==='fail'?'danger':'info'" size="small">{{ row.active?'鍦ㄧ嚎':row.status==='fail'?'鏁呴殰':'鏆傚仠' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="鏉冮噸" width="100">
          <template #default="{row}">
            <el-input-number v-model="row.weight" :min="1" :max="10" size="small" controls-position="right" style="width:80px" @change="(v)=>updateWeight(row,v)" />
          </template>
        </el-table-column>
        <el-table-column label="鎿嶄綔" width="220">
          <template #default="{row}">
            <el-button text size="small" :type="row.active?'warning':'success'" @click="handleToggle(row)">{{ row.active?'鏆傚仠':'鎭㈠' }}</el-button>
            <el-button text size="small" type="primary" @click="handleCheckOne(row)">妫€娴</el-button>
            <el-button text size="small" type="danger" @click="handleRemove(row)">鍒犻櫎</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="domains.length===0&&!loading" description="暂无域名，点击上方「添加域名」开始配置" :image-size="80" style="padding:60px 0" />
    </el-card>

    <!-- ===== 浜岀骇杞€奸厤缃?===== -->
    <el-card shadow="never" style="margin-top:20px">
      <template #header><span style="font-weight:600">浜岀骇杞€奸厤缃紙主域名"+ 杞€肩粍 + 瀛愬煙鍚嶏級</span></template>
      <div v-if="!twoLevelConfig">鏆傛棤浜岀骇杞€奸厤缃</div>
      <div v-else>
        <div style="margin-bottom:16px">
          <strong>涓诲煙鍚嶏細</strong>{{ twoLevelConfig.primary?.main || '-' }}
          <span v-if="twoLevelConfig.primary?.children">锛坽{ twoLevelConfig.primary.children.length }} 涓瓙鍩熷悕锛</span>
        </div>
        <div v-for="g in (twoLevelConfig.rotation||[])" :key="g.id" style="padding:12px;background:rgba(102,126,234,0.05);border-radius:8px;margin-bottom:8px">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div><strong>{{ g.main }}</strong><el-tag size="small" style="margin-left:8px">鏉冮噸 {{ g.weight }}</el-tag></div>
            <div style="display:flex;gap:6px">
              <el-button text size="small" :type="g.enabled!==false?'success':'info'" @click="toggleRotationGroup(g.id)">{{ g.enabled!==false?'已启用':'已停用' }}</el-button>
              <el-button text size="small" type="primary" @click="showAddSubDomain(g)">锛瀛愬煙鍚</el-button>
            </div>
          </div>
          <div v-if="g.children?.length" style="margin-top:8px;padding-left:16px;font-size:13px;color:var(--text-muted)">
            <div v-for="c in g.children" :key="c.host" style="display:flex;justify-content:space-between;padding:4px 0">
              <span>{{ c.host }}锛堟潈閲?{{ c.weight }}锛</span>
              <el-button text size="small" type="danger" @click="removeSubDomain(g.id,c.host)">绉婚櫎</el-button>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 娣诲姞鍩熷悕寮圭獥 -->
    <el-dialog v-model="addDialogVisible" title="娣诲姞鍩熷悕" width="420px">
      <el-form label-position="top">
        <el-form-item label="鍩熷悕">
          <el-input v-model="newDomain.domain" placeholder="example.com" />
        </el-form-item>
        <el-form-item label="绫诲瀷">
          <el-select v-model="newDomain.type" style="width:100%">
            <el-option label="..." value="主域名" />
            <el-option label="..." value="轮值" />
            <el-option label="CDN鍥剧墖" value="CDN鍥剧墖" />
          </el-select>
        </el-form-item>
        <el-form-item label="权重（1-10）">
          <el-input-number v-model="newDomain.weight" :min="1" :max="10" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible=false">鍙栨秷</el-button>
        <el-button type="primary" @click="handleAdd" :loading="adding">娣诲姞</el-button>
      </template>
    </el-dialog>

    <!-- 娣诲姞瀛愬煙鍚嶅脊绐?-->
    <el-dialog v-model="subDialogVisible" :title="'为'+(subGroup?.main||'')+' 添加子域名'" width="400px">
      <el-form label-position="top">
        <el-form-item label="子域名">
          <el-input v-model="newSubDomain.host" placeholder="shop.example.com" />
        </el-form-item>
        <el-form-item label="鏉冮噸">
          <el-input-number v-model="newSubDomain.weight" :min="1" :max="10" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="subDialogVisible=false">鍙栨秷</el-button>
        <el-button type="primary" @click="handleAddSub" :loading="addingSub">娣诲姞</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import {
  getDomains, toggleDomain, checkDomain, addDomain, removeDomain, setDomainWeight,
  getTwoLevelConfig, toggleRotationGroup as apiToggleGroup, addSubdomain, removeSubdomain
} from "@/api/rotation"

const loading = ref(true)
const checkingAll = ref(false)
const error = ref(null)
let pollTimer = null
const domains = reactive([])
const twoLevelConfig = ref(null)

// 娣诲姞鍩熷悕
const addDialogVisible = ref(false)
const adding = ref(false)
const newDomain = reactive({ domain: "", type: "轮值", weight: 3 })

// 娣诲姞瀛愬煙鍚?
const subDialogVisible = ref(false)
const addingSub = ref(false)
const subGroup = ref(null)
const newSubDomain = reactive({ host: "", weight: 3 })

const avgLatency = computed(() => {
  const a = domains.filter(d => d.active && d.latency)
  return a.length ? Math.round(a.reduce((s, d) => s + d.latency, 0) / a.length) : "-"
})

async function fetchDomains() {
  try {
    const data = await getDomains()
    if (Array.isArray(data)) {
      domains.splice(0, domains.length, ...data.map(d => ({
        domain: d.domain || d.host || "",
        ip: d.ip || d.address || "",
        active: d.active ?? d.status === "ok",
        status: d.status || (d.active ? "ok" : "paused"),
        latency: d.latency ?? 0,
        type: d.type || "轮值",
        weight: d.weight ?? 3,
        sslExpiry: d.sslExpiry || "",
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
  if (!newDomain.domain) { ElMessage.warning("请输入域名"); return }
  adding.value = true
  try {
    await addDomain(newDomain.domain, newDomain.type)
    ElMessage.success(`已添加域名"${newDomain.domain}`)
    addDialogVisible.value = false
    newDomain.domain = ""
    await fetchDomains()
  } catch (e) { ElMessage.error(e.message) }
  finally { adding.value = false }
}

async function handleRemove(row) {
  try {
    await ElMessageBox.confirm(`确定删除域名 ${row.domain}？`, "确认删除", { type: "warning" })
    await removeDomain(row.domain)
    ElMessage.success(`已删除"${row.domain}`)
    await fetchDomains()
  } catch {}
}

async function handleToggle(row) {
  try {
    await toggleDomain(row.domain, !row.active)
    row.active = !row.active
    row.status = row.active ? "ok" : "paused"
    ElMessage.success(row.active ? "已恢复" : "已暂停")
  } catch { ElMessage.error("操作失败") }
}

async function handleCheckOne(row) {
  ElMessage.info(`姝ｅ湪妫€娴?${row.domain}...`)
  try {
    const r = await checkDomain(row.domain)
    if (r) { row.latency = r.latency ?? row.latency; row.active = r.online ?? row.active }
    ElMessage.success(`${row.domain} 检测完成"`)
  } catch { ElMessage.warning("检测请求已发送") }
}

async function handleCheckAll() {
  checkingAll.value = true
  try {
    await Promise.all(domains.map(d => checkDomain(d.domain).catch(()=>{})))
    await fetchDomains()
    ElMessage.success("全量检测完成")
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
    ElMessage.success("已切换")
  } catch { ElMessage.error("操作失败") }
}

function showAddSubDomain(g) {
  subGroup.value = g
  newSubDomain.host = ""
  newSubDomain.weight = 3
  subDialogVisible.value = true
}

async function handleAddSub() {
  if (!newSubDomain.host) { ElMessage.warning("请输入子域名"); return }
  addingSub.value = true
  try {
    await addSubdomain(subGroup.value.id, newSubDomain.host, newSubDomain.weight)
    ElMessage.success("子域名已添加")
    subDialogVisible.value = false
    await fetchTwoLevelConfig()
  } catch (e) { ElMessage.error(e.message) }
  finally { addingSub.value = false }
}

async function removeSubDomain(groupId, host) {
  try {
    await ElMessageBox.confirm(`确定移除子域名?${host}？`, "确认", { type: "warning" })
    await removeSubdomain(groupId, host)
    ElMessage.success("已移除")
    await fetchTwoLevelConfig()
  } catch {}
}

const refreshDomains = async () => {
  loading.value = true
  await fetchDomains()
  ElMessage.success("已刷新")
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
