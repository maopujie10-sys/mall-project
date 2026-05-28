<template>
  <div class="file-manager">
    <div class="page-header">
      <h2>📁 文件管理器</h2>
      <p>浏览 · 上传 · 下载 · 删除</p>
    </div>

    <div class="toolbar">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item v-for="(seg, i) in pathParts" :key="i" @click="navigateTo(seg.path)">
          <a href="javascript:void 0" style="color:var(--color-primary)">{{ seg.name || "📁 /" }}</a>
        </el-breadcrumb-item>
      </el-breadcrumb>
      <div style="display:flex;gap:8px;margin-left:auto">
        <el-input v-model="currentPath" placeholder="路径" size="small" style="width:300px" @keyup.enter="loadFiles" />
        <el-button @click="loadFiles" type="primary" size="small" :loading="loading">📂 浏览</el-button>
        <el-upload :http-request="handleUpload" :show-file-list="false" style="display:inline-block">
          <el-button type="success" size="small">📤 上传</el-button>
        </el-upload>
      </div>
    </div>

    <el-table :data="entries" stripe size="small" v-loading="loading">
      <el-table-column label="名称" min-width="300">
        <template #default="{row}">
          <span @click="row.is_dir ? navigateDir(row.name) : null"
                style="cursor:pointer;display:flex;align-items:center;gap:6px">
            <span>{{ row.is_dir ? "📁" : "📄" }}</span>
            <span :style="{color: row.is_dir ? 'var(--color-primary)' : 'inherit', fontWeight: row.is_dir ? 500 : 'normal'}">
              {{ row.name }}
            </span>
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="size" label="大小" width="120">
        <template #default="{row}">{{ row.is_dir ? "-" : formatSize(row.size) }}</template>
      </el-table-column>
      <el-table-column prop="modified" label="修改时间" width="160" />
      <el-table-column prop="permissions" label="权限" width="80" />
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{row}">
          <el-button v-if="!row.is_dir" text type="primary" size="small" @click="downloadFile(row.name)">下载</el-button>
          <el-button text type="danger" size="small" @click="deleteFile(row.name)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-empty v-if="!loading && entries.length===0" description="空目录" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import { agentApi } from "@/api"

const currentPath = ref("/")
const entries = ref([])
const loading = ref(false)

const pathParts = computed(() => {
  const parts = currentPath.value.replace(/\\/g, "/").split("/").filter(Boolean)
  const result = [{ name: "根目录 /", path: "/" }]
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
    ElMessage.error("浏览失败: " + (e.response?.data?.detail || e.message))
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
      ElMessage.success("上传成功")
      loadFiles()
    }
  } catch (e) {
    ElMessage.error("上传失败")
  }
}

async function deleteFile(name) {
  const fp = currentPath.value.replace(/\/+$/, "") + "/" + name
  try {
    await ElMessageBox.confirm(`确定删除 ${name}？`, "确认", { type: "warning" })
    const r = await agentApi.delete("/server/files", { params: { path: fp } })
    if (r.ok || r.deleted) {
      ElMessage.success("已删除")
      loadFiles()
    }
  } catch (e) {
    if (e !== "cancel") ElMessage.error("删除失败")
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
</style>
