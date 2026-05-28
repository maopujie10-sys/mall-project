<template>
  <div class="skill-center">
    <div class="page-header">
      <h2>🧩 技能市场</h2>
      <p>浏览 · 安装 · 管理 · 发布 AI 技能</p>
      <div class="header-stats">
        <el-tag type="primary">内置 {{ totalSkills }} 个</el-tag>
        <el-tag type="success">已装 {{ installedCount }}</el-tag>
        <el-tag type="warning">社区 {{ communityCount }}</el-tag>
      </div>
    </div>

    <el-tabs v-model="activeTab">
      <!-- Tab 1: 内置技能市场 -->
      <el-tab-pane label="🛒 内置市场" name="market">
        <div class="toolbar">
          <el-input v-model="search" placeholder="搜索..." clearable style="width:240px" size="small" />
          <el-select v-model="categoryFilter" placeholder="全部分类" clearable style="width:140px" size="small">
            <el-option v-for="c in categories" :key="c.category" :label="(c.icon||'📦') + ' ' + c.category + ' (' + c.count + ')'" :value="c.category" />
          </el-select>
          <el-button @click="fetchMarket" size="small" :loading="loading">刷新</el-button>
        </div>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12" :md="8" v-for="s in filteredSkills" :key="s.id" style="margin-bottom:16px">
            <el-card shadow="hover" class="skill-card" :class="{installed:s.installed}">
              <div class="skill-header">
                <span class="skill-icon">{{ s.icon || "📦" }}</span>
                <div class="skill-info">
                  <h3>{{ s.name }}</h3>
                  <el-tag size="small">{{ s.category }}</el-tag>
                </div>
              </div>
              <p class="skill-desc">{{ s.desc }}</p>
              <div class="skill-meta">
                <span>⭐ {{ s.stars }}</span>
                <span>📥 {{ s.downloads }}</span>
                <span>v{{ s.version }}</span>
                <span>✍️ {{ s.author }}</span>
              </div>
              <div class="skill-tags" v-if="s.tags">
                <el-tag v-for="t in s.tags.slice(0,3)" :key="t" size="small" effect="plain">{{ t }}</el-tag>
              </div>
              <el-button
                :type="s.installed ? 'success' : 'primary'"
                size="small" style="width:100%;margin-top:10px"
                @click="s.installed ? null : installSkill(s)"
                :disabled="s.installed || installing === s.id"
                :loading="installing === s.id"
              >{{ s.installed ? '✅ 已安装' : '📥 安装' }}</el-button>
            </el-card>
          </el-col>
        </el-row>
        <el-empty v-if="filteredSkills.length===0" description="没有匹配的技能" />
      </el-tab-pane>

      <!-- Tab 2: 社区市场 -->
      <el-tab-pane label="🌍 社区市场" name="community">
        <div class="toolbar">
          <el-input v-model="communitySearch" placeholder="搜索社区技能..." clearable style="width:240px" size="small" />
          <el-select v-model="communityCategory" placeholder="全部分类" clearable style="width:140px" size="small">
            <el-option v-for="c in communityCategories" :key="c" :label="c" :value="c" />
          </el-select>
          <el-button @click="fetchCommunity" size="small" :loading="communityLoading">刷新</el-button>
        </div>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12" :md="8" v-for="s in filteredCommunity" :key="s.id" style="margin-bottom:16px">
            <el-card shadow="hover" class="skill-card" :class="{installed:s.installed || communityInstalledIds.includes(s.id)}">
              <div class="skill-header">
                <span class="skill-icon">{{ s.name.slice(0,2) }}</span>
                <div class="skill-info">
                  <h3>{{ s.name }}</h3>
                  <el-tag size="small">{{ s.category }}</el-tag>
                  <el-tag v-if="s.version" size="small" type="info">v{{ s.version }}</el-tag>
                </div>
              </div>
              <p class="skill-desc">{{ s.desc }}</p>
              <div class="skill-meta">
                <span>⭐ {{ s.stars }}</span>
                <span>📥 {{ s.downloads }}</span>
                <span>✍️ {{ s.author }}</span>
                <span>🕐 {{ s.updated_at }}</span>
              </div>
              <div class="skill-tags" v-if="s.tags">
                <el-tag v-for="t in s.tags.slice(0,3)" :key="t" size="small" effect="plain">{{ t }}</el-tag>
              </div>
              <div style="font-size:11px;color:#999;margin-top:6px;padding:6px;background:#f5f5f5;border-radius:4px">
                📖 {{ s.readme }}
              </div>
              <el-button
                :type="isCommunityInstalled(s.id) ? 'success' : 'primary'"
                size="small" style="width:100%;margin-top:10px"
                :disabled="isCommunityInstalled(s.id) || communityInstalling === s.id"
                :loading="communityInstalling === s.id"
                @click="installCommunity(s)"
              >{{ isCommunityInstalled(s.id) ? '✅ 已安装' : '📥 安装' }}</el-button>
            </el-card>
          </el-col>
        </el-row>
        <el-empty v-if="filteredCommunity.length===0" description="暂无社区技能" />
      </el-tab-pane>

      <!-- Tab 3: 已安装 -->
      <el-tab-pane label="📦 已安装" name="installed">
        <el-table :data="allInstalledSkills" stripe size="small">
          <el-table-column label="技能" min-width="200">
            <template #default="{row}">
              <span style="font-size:18px;margin-right:6px">{{ row.icon || "📦" }}</span>
              <span style="font-weight:500">{{ row.name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="version" label="版本" width="80" />
          <el-table-column prop="category" label="分类" width="100">
            <template #default="{row}"><el-tag size="small">{{ row.category }}</el-tag></template>
          </el-table-column>
          <el-table-column label="来源" width="80">
            <template #default="{row}">
              <el-tag v-if="row.id" size="small" :type="row._source==='package'?'warning':'default'">{{ row._source==='package'?'包':'内置' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="desc" label="描述" min-width="200" show-overflow-tooltip />
          <el-table-column label="状态" width="90">
            <template #default="{row}">
              <el-switch v-model="row.enabled" @change="toggleSkill(row)" size="small" :disabled="row._source==='package'" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{row}">
              <el-button v-if="row._source==='package'" text type="danger" size="small" @click="uninstallPackage(row)">卸载</el-button>
              <el-button v-else text type="danger" size="small" @click="uninstallSkill(row)">卸载</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="allInstalledSkills.length===0" description="暂无已安装技能" />
      </el-tab-pane>

      <!-- Tab 4: 发布技能 -->
      <el-tab-pane label="📤 发布技能" name="publish">
        <el-card shadow="never">
          <h3 style="margin-top:0">📤 发布技能包</h3>
          <p style="color:#999;font-size:13px">将你的 skill.json + main.py 打包成 ZIP 上传，即可在系统中安装使用</p>
          <el-upload
            drag
            accept=".zip"
            :auto-upload="false"
            :on-change="handleFileChange"
            :file-list="publishFileList"
          >
            <el-icon style="font-size:48px;color:#667eea"><UploadFilled /></el-icon>
            <div style="font-size:14px;margin-top:8px">拖拽 ZIP 文件到此处，或 <em>点击上传</em></div>
            <template #tip>
              <div style="font-size:12px;color:#999;margin-top:4px">
                需包含 skill.json（清单）+ main.py（入口代码）
              </div>
            </template>
          </el-upload>
          <div style="margin-top:16px">
            <el-button type="primary" @click="publishSkill" :loading="publishing" :disabled="!publishFile">
              📤 发布并安装
            </el-button>
          </div>
          <el-divider />
          <h4>🔗 从 URL 安装</h4>
          <div style="display:flex;gap:8px">
            <el-input v-model="publishUrl" placeholder="https://example.com/my-skill.zip" style="flex:1" size="small" />
            <el-button @click="publishFromUrl" :loading="publishingUrl" size="small" :disabled="!publishUrl">安装</el-button>
          </div>
          <el-divider />
          <h4>📦 技能包格式要求</h4>
          <pre style="font-size:12px;background:#f5f5f5;padding:12px;border-radius:4px">
my-skill.zip
├── skill.json          # 必填：技能清单
│   ├── id              # 唯一标识
│   ├── name            # 显示名称
│   ├── version         # 版本号
│   ├── desc            # 描述
│   ├── author          # 作者
│   ├── category        # 分类
│   ├── entry           # 入口文件（默认 main.py）
│   └── dependencies    # 依赖列表
├── main.py             # 入口代码（需实现 async def execute(params)）
└── assets/             # 资源文件（可选）
          </pre>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import { agentApi } from "@/api"

const activeTab = ref("market")
const loading = ref(false)
const installing = ref("")
const search = ref("")
const categoryFilter = ref("")
const allSkills = ref([])
const categories = ref([])

// 社区
const communitySearch = ref("")
const communityCategory = ref("")
const communityLoading = ref(false)
const communityInstalling = ref("")
const communitySkills = ref([])
const communityInstalledIds = ref([])

// 发布
const publishFile = ref(null)
const publishFileList = ref([])
const publishing = ref(false)
const publishUrl = ref("")
const publishingUrl = ref(false)

// 已安装包
const installedPackages = ref([])

// === 计算属性 ===
const totalSkills = computed(() => allSkills.value.length)
const communityCount = computed(() => communitySkills.value.length)
const installedCount = computed(() => allSkills.value.filter(s => s.installed).length + installedPackages.value.length)

const installedSkills = computed(() => allSkills.value.filter(s => s.installed))

const allInstalledSkills = computed(() => {
  const builtin = installedSkills.value.map(s => ({ ...s, _source: "builtin" }))
  const pkgs = installedPackages.value.map(s => ({ ...s, _source: "package", enabled: true }))
  return [...builtin, ...pkgs]
})

const filteredSkills = computed(() => {
  let list = allSkills.value
  if (categoryFilter.value) list = list.filter(s => s.category === categoryFilter.value)
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(s => s.name.toLowerCase().includes(q) || s.desc.toLowerCase().includes(q))
  }
  return list
})

const communityCategories = computed(() => {
  const set = new Set(communitySkills.value.map(s => s.category))
  return [...set]
})

const filteredCommunity = computed(() => {
  let list = communitySkills.value
  if (communityCategory.value) list = list.filter(s => s.category === communityCategory.value)
  if (communitySearch.value) {
    const q = communitySearch.value.toLowerCase()
    list = list.filter(s => s.name.toLowerCase().includes(q) || s.desc.toLowerCase().includes(q))
  }
  return list
})

function isCommunityInstalled(id) {
  return communityInstalledIds.value.includes(id)
}

// === 内置市场 ===
async function fetchMarket() {
  loading.value = true
  try {
    const r = await agentApi.get("/agent/plugins")
    if (r.plugins) allSkills.value = r.plugins
  } catch { allSkills.value = [] }
  try {
    const r = await agentApi.get("/agent/plugins/categories")
    if (r.categories) categories.value = r.categories
  } catch { categories.value = [] }
  loading.value = false
}

async function installSkill(s) {
  installing.value = s.id
  try {
    const r = await agentApi.post("/agent/plugins/install", { plugin_id: s.id })
    if (r.ok || r.status === "installed" || r.status === "already_installed") {
      ElMessage.success("✅ " + s.name + " 安装成功")
      s.installed = true
    }
  } catch (e) {
    ElMessage.error("安装失败: " + (e.response?.data?.detail || e.message))
  }
  installing.value = ""
}

async function uninstallSkill(s) {
  try {
    await ElMessageBox.confirm("确定卸载 " + s.name + "？", "确认", { type: "warning" })
    const r = await agentApi.post("/agent/plugins/uninstall", { plugin_id: s.id })
    if (r.ok || r.uninstalled) {
      ElMessage.success(s.name + " 已卸载")
      s.installed = false
    }
  } catch (e) {
    if (e !== "cancel") ElMessage.error("卸载失败")
  }
}

async function toggleSkill(s) {
  try {
    await agentApi.post("/agent/plugins/toggle", { plugin_id: s.id, enabled: s.enabled })
    ElMessage.success(s.enabled ? s.name + " 已启用" : s.name + " 已禁用")
  } catch {
    s.enabled = !s.enabled
    ElMessage.error("操作失败")
  }
}

// === 社区市场 ===
async function fetchCommunity() {
  communityLoading.value = true
  try {
    const r = await agentApi.get("/agent/plugins/community")
    if (r.skills) {
      communitySkills.value = r.skills
      communityInstalledIds.value = r.installed_ids || []
    }
  } catch { communitySkills.value = [] }
  communityLoading.value = false
}

async function installCommunity(s) {
  communityInstalling.value = s.id
  try {
    const r = await agentApi.post("/agent/plugins/community/install", { skill_id: s.id })
    if (r.ok || r.status === "installed") {
      ElMessage.success("✅ " + s.name + " 安装成功")
      communityInstalledIds.value.push(s.id)
      fetchInstalledPackages()
    }
  } catch (e) {
    ElMessage.error("安装失败: " + (e.response?.data?.detail || e.message))
  }
  communityInstalling.value = ""
}

// === 安装包管理 ===
async function fetchInstalledPackages() {
  try {
    const r = await agentApi.get("/agent/plugins/installed/packages")
    if (r.skills) installedPackages.value = r.skills
  } catch { installedPackages.value = [] }
}

async function uninstallPackage(s) {
  try {
    await ElMessageBox.confirm("确定卸载技能包 " + s.name + "？\n文件将被删除。", "确认", { type: "warning" })
    const r = await agentApi.post("/agent/plugins/uninstall/" + s.id)
    if (r.ok || r.uninstalled) {
      ElMessage.success(s.name + " 已卸载")
      installedPackages.value = installedPackages.value.filter(p => p.id !== s.id)
    }
  } catch (e) {
    if (e !== "cancel") ElMessage.error("卸载失败")
  }
}

// === 发布技能 ===
function handleFileChange(file) {
  publishFile.value = file.raw
  return false
}

async function publishSkill() {
  if (!publishFile.value) return
  publishing.value = true
  try {
    const form = new FormData()
    form.append("file", publishFile.value)
    const r = await agentApi.post("/agent/plugins/publish", form, {
      headers: { "Content-Type": "multipart/form-data" }
    })
    if (r.ok) {
      ElMessage.success("✅ 技能发布并安装成功")
      publishFile.value = null
      publishFileList.value = []
      fetchInstalledPackages()
    } else {
      ElMessage.error("发布失败: " + (r.error || "未知错误"))
    }
  } catch (e) {
    ElMessage.error("发布失败: " + (e.response?.data?.detail || e.message))
  }
  publishing.value = false
}

async function publishFromUrl() {
  if (!publishUrl.value) return
  publishingUrl.value = true
  try {
    const r = await agentApi.post("/agent/plugins/publish", { download_url: publishUrl.value })
    if (r.ok) {
      ElMessage.success("✅ 安装成功")
      publishUrl.value = ""
      fetchInstalledPackages()
    } else {
      ElMessage.error("安装失败: " + (r.error || "未知错误"))
    }
  } catch (e) {
    ElMessage.error("安装失败: " + (e.response?.data?.detail || e.message))
  }
  publishingUrl.value = false
}

onMounted(() => {
  fetchMarket()
  fetchCommunity()
  fetchInstalledPackages()
})
</script>

<style scoped>
.skill-center { padding: 20px; }
.page-header { margin-bottom: 20px; }
.page-header h2 { margin: 0 0 4px; font-size: 20px; }
.page-header p { margin: 0 0 8px; color: #999; font-size: 13px; }
.header-stats { display: flex; gap: 8px; }
.toolbar { display: flex; gap: 12px; margin-bottom: 16px; align-items: center; }
.skill-card { transition: all 0.2s; position: relative; }
.skill-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.1); }
.skill-card.installed { border-left: 3px solid #52c41a; }
.skill-header { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.skill-icon { font-size: 36px; }
.skill-info h3 { margin: 0; font-size: 15px; font-weight: 600; }
.skill-info { flex: 1; }
.skill-desc { font-size: 12px; color: #666; margin: 8px 0; line-height: 1.5; }
.skill-meta { display: flex; gap: 12px; font-size: 11px; color: #999; margin-bottom: 8px; }
.skill-tags { display: flex; gap: 4px; flex-wrap: wrap; }
</style>