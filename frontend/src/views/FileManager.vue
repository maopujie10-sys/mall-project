<template>
  <div class="file-manager">
    <div class="page-header">
      <h2>馃搧 鏂囦欢绠＄悊鍣?/h2>
      <p>娴忚 路 涓婁紶 路 涓嬭浇 路 鍒犻櫎</p>
    </div>

    <div class="toolbar">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item v-for="(seg, i) in pathParts" :key="i" @click="navigateTo(seg.path)">
          <a href="javascript:void 0" style="color:var(--color-primary)">{{ seg.name || "馃搧 /" }}</a>
        </el-breadcrumb-item>
      </el-breadcrumb>
      <div style="display:flex;gap:8px;margin-left:auto">
        <el-input v-model="currentPath" placeholder="璺緞" size="small" style="width:300px" @keyup.enter="loadFiles" />
        <el-button @click="loadFiles" type="primary" size="small" :loading="loading">馃搨 娴忚</el-button>
        <el-upload :http-request="handleUpload" :show-file-list="false" style="display:inline-block">
          <el-button type="success" size="small">馃摛 涓婁紶</el-button>
        </el-upload>
      </div>
    </div>

    <el-table :data="entries" stripe size="small" v-loading="loading">
      <el-table-column label="鍚嶇О" min-width="300">
        <template #default="{row}">
          <span @click="row.is_dir ? navigateDir(row.name) : null"
                style="cursor:pointer;display:flex;align-items:center;gap:6px">
            <span>{{ row.is_dir ? "馃搧" : "馃搫" }}</span>
            <span :style="{color: row.is_dir ? 'var(--color-primary)' : 'inherit', fontWeight: row.is_dir ? 500 : 'normal'}">
              {{ row.name }}
            </span>
          </span>
        

    <!-- 褰掓。绠＄悊 -->
    <el-divider/>
    <div class="section-header"><h3>馃摝 褰掓。绠＄悊</h3><el-button size="small" type="primary" @click="showArchiveDialog=true">+ 鏂板缓褰掓。</el-button></div>
    
    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="6" v-for="s in archiveStorage" :key="s.label">
        <el-card shadow="never" class="stat-tiny"><div class="stat-tiny-val">{{ s.value }}</div><div class="stat-tiny-lbl">{{ s.label }}</div></el-card>
      </el-col>
    </el-row>

    <el-table :data="archives" size="small" v-if="archives.length">
      <el-table-column prop="id" label="ID" width="140"/>
      <el-table-column prop="name" label="鏂囦欢鍚? min-width="200"/>
      <el-table-column prop="size_mb" label="澶у皬(MB)" width="100"/>
      <el-table-column prop="created_at" label="鏃堕棿" width="170"/>
      <el-table-column label="鐘舵€? width="80"><template #default="{row}"><el-tag :type="row.file_exists?'success':'danger'" size="small">{{ row.file_exists?'瀛樺湪':'宸插垹闄? }}</el-tag></template></el-table-column>
      <el-table-column label="鎿嶄綔" width="100"><template #default="{row}"><el-button size="small" link type="danger" @click="doDeleteArchive(row.id)">鍒犻櫎</el-button></template></el-table-column>
    </el-table>

    <!-- 鏂板缓褰掓。瀵硅瘽妗?-->
    <el-dialog v-model="showArchiveDialog" title="鏂板缓褰掓。" width="500px">
      <el-form label-width="80px">
        <el-form-item label="鐩爣"><el-checkbox-group v-model="archiveTargets">
          <el-checkbox v-for="t in archiveTargetList" :key="t.id" :value="t.id" :disabled="!t.exists">{{ t.name }} <small style="color:var(--text-muted)">({{ t.size }})</small></el-checkbox>
        </el-checkbox-group></el-form-item>
        <el-form-item label="澶囨敞"><el-input v-model="archiveNote" placeholder="鍙€夛細褰掓。璇存槑"/></el-form-item>
        <el-form-item label="鎺ㄩ€丟itHub"><el-switch v-model="archivePushGithub"/></el-form-item>
      </el-form>
      <template #footer><el-button @click="showArchiveDialog=false">鍙栨秷</el-button><el-button type="primary" :loading="archiveLoading" @click="doCreateArchive">鍒涘缓褰掓。</el-button></template>
    </el-dialog>
</template>
      </el-table-column>
      <el-table-column prop="size" label="澶у皬" width="120">
        <template #default="{row}">{{ row.is_dir ? "-" : formatSize(row.size) }}</template>
      </el-table-column>
      <el-table-column prop="modified" label="淇敼鏃堕棿" width="160" />
      <el-table-column prop="permissions" label="鏉冮檺" width="80" />
      <el-table-column label="鎿嶄綔" width="100" fixed="right">
        <template #default="{row}">
          <el-button v-if="!row.is_dir" text type="primary" size="small" @click="downloadFile(row.name)">涓嬭浇</el-button>
          <el-button text type="danger" size="small" @click="deleteFile(row.name)">鍒犻櫎</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-empty v-if="!loading && entries.length===0" description="绌虹洰褰? />
  </div>
</template>

<script setup>
import { createArchive, listArchives, deleteArchive, getArchiveStorage, listArchiveTargets } from '@/api/archive'
import { ref, computed, onMounted } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import { agentApi } from "@/api"

const currentPath = ref("/")
const entries = ref([])
const loading = ref(false)
// 褰掓。
const archives = ref([])
const archiveTargetList = ref([])
const archiveTargets = ref(['memory'])
const archiveNote = ref('')
const archivePushGithub = ref(false)
const showArchiveDialog = ref(false)
const archiveLoading = ref(false)
const archiveStorage = ref([])

const pathParts = computed(() => {
  const parts = currentPath.value.replace(/\\/g, "/").split("/").filter(Boolean)
  const result = [{ name: "鏍圭洰褰?/", path: "/" }]
  let cum = ""
  for (const p of parts) {
    cum += "/" + p
    result.push({ name: p, path: cum })
  }
  return result
})

async function loadFiles() {
  loading.value = true
  try {
    const r = await agentApi.get("/server/files", { params: { path: currentPath.value } })
    entries.value = r.entries || []
    if (r.path) currentPath.value = r.path
  } catch (e) {
    ElMessage.error("娴忚澶辫触: " + (e.response?.data?.detail || e.message))
  }
  loading.value = false
}

function navigateTo(path) {
  currentPath.value = path
  loadFiles()
}

function navigateDir(name) {
  const sep = currentPath.value.endsWith("/") ? "" : "/"
  currentPath.value += sep + name
  loadFiles()
}

async function handleUpload(options) {
  try {
    const form = new FormData()
    form.append("file", options.file)
    const r = await agentApi.post("/server/files/upload", form, {
      params: { path: currentPath.value },
      headers: { "Content-Type": "multipart/form-data" },
    })
    if (r.ok || r.path) {
      ElMessage.success("涓婁紶鎴愬姛")
      loadFiles()
    }
  } catch (e) {
    ElMessage.error("涓婁紶澶辫触")
  }
}

async function deleteFile(name) {
  const fp = currentPath.value.replace(/\/+$/, "") + "/" + name
  try {
    await ElMessageBox.confirm(`纭畾鍒犻櫎 ${name}锛焋, "纭", { type: "warning" })
    const r = await agentApi.delete("/server/files", { params: { path: fp } })
    if (r.ok || r.deleted) {
      ElMessage.success("宸插垹闄?)
      loadFiles()
    }
  } catch (e) {
    if (e !== "cancel") ElMessage.error("鍒犻櫎澶辫触")
  }
}

function downloadFile(name) {
  const fp = currentPath.value.replace(/\/+$/, "") + "/" + name
  window.open(`/ai/api/server/files/download?path=${encodeURIComponent(fp)}`, "_blank")
}

function formatSize(bytes) {
  if (!bytes) return "0B"
  const units = ["B", "KB", "MB", "GB"]
  let i = 0
  let size = bytes
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
  return size.toFixed(1) + units[i]
}

onMounted(loadFiles)
</script>

<style scoped>
.file-manager { padding: 20px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px; font-size: 18px; }
.page-header p { margin: 0; color: #999; font-size: 13px; }
.toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>
