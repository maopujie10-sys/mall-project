<template>
  <div class="skill-center">
    <div class="page-header">
      <h2>Control Panel</h2>
      <p>       AI</p>
      <div class="header-stats">
        <el-tag type="primary"> {{ totalSkills }} </el-tag>
        <el-tag type="success"> {{ installedCount }}</el-tag>
        <el-tag type="warning"> {{ communityCount }}</el-tag>
      </div>
    </div>

    <el-tabs v-model="activeTab">
      <!-- Tab 1: ?-->
      <el-tab-pane label='Status' name="market">
        <div class="toolbar">
          <el-input v-model="search" placeholder="..." clearable style="width:240px" size="small" />
          <el-select v-model="categoryFilter" :placeholder="\('plugin.search')" clearable style="width:140px" size="small">
            <el-option v-for="c in categories" :key="c.category" :label="(c.icon||'') + c.category + ' (' + c.count + ')' :value="c.category" />
          </el-select>
          <el-button @click="fetchMarket" size="small" :loading="loading">OK</el-button>
        </div>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12" :md="8" v-for="s in filteredSkills" :key="s.id" style="margin-bottom:16px">
            <el-card shadow="hover" class="skill-card" :class="{installed:s.installed}">
              <div class="skill-header">
                <span class="skill-icon">{{ s.icon || '' }}</span>
                <div class="skill-info">
                  <h3>{{ s.name }}</h3>
                  <el-tag size="small">{{ s.category }}</el-tag>
                </div>
              </div>
              <p class="skill-desc">{{ s.desc }}</p>
              <div class="skill-meta">
                <span>?{{ s.stars }}</span>
                <span> {{ s.downloads }}</span>
                <span>v{{ s.version }}</span>
                <span> {{ s.author }}</span>
              </div>
              <div class="skill-tags" v-if="s.tags">
                <el-tag v-for="t in s.tags.slice(0,3)" :key="t" size="small" effect="plain">{{ t }}</el-tag>
              </div>
              <el-button
                :type="s.installed ? 'success' : 'primary''
                size="small" style="width:100%;margin-top:10px"
                @click="s.installed ? null : installSkill(s)"
                :disabled="s.installed || installing === s.id"
                :loading="installing === s.id"
              >{{ s.installed ? '?? : '' }}</el-button>
            </el-card>
          </el-col>
        </el-row>
        <el-empty v-if="filteredSkills.length===0" description="? />
      </el-tab-pane>

      <!-- Tab 2:  -->
      <el-tab-pane label='Status' name="community">
        <div class="toolbar">
          <el-input v-model="communitySearch" placeholder="?.." clearable style="width:240px" size="small" />
          <el-select v-model="communityCategory" :placeholder="\('plugin.search')" clearable style="width:140px" size="small">
            <el-option v-for="c in communityCategories" :key="c" :label="c" :value="c" />
          </el-select>
          <el-button @click="fetchCommunity" size="small" :loading="communityLoading">OK</el-button>
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
                <span>?{{ s.stars }}</span>
                <span> {{ s.downloads }}</span>
                <span> {{ s.author }}</span>
                <span> {{ s.updated_at }}</span>
              </div>
              <div class="skill-tags" v-if="s.tags">
                <el-tag v-for="t in s.tags.slice(0,3)" :key="t" size="small" effect="plain">{{ t }}</el-tag>
              </div>
              <div style="font-size:11px;color:#999;margin-top:6px;padding:6px;background:#f5f5f5;border-radius:4px">
                 {{ s.readme }}
              </div>
              <el-button
                :type="isCommunityInstalled(s.id) ? 'success' : 'primary''
                size="small" style="width:100%;margin-top:10px"
                :disabled="isCommunityInstalled(s.id) || communityInstalling === s.id"
                :loading="communityInstalling === s.id"
                @click="installCommunity(s)"
              >{{ isCommunityInstalled(s.id) ? '?? : '' }}</el-button>
            </el-card>
          </el-col>
        </el-row>
        <el-empty v-if="filteredCommunity.length===0" description="? />
      </el-tab-pane>

      <!-- Tab 3: ?-->
      <el-tab-pane label=" ? name="installed">
        <el-table :data="allInstalledSkills" stripe size="small">
          <el-table-column label="? min-width="200">
            <template #default="{row}">
              <span style="font-size:18px;margin-right:6px">{{ row.icon || '' }}</span>
              <span style="font-weight:500">{{ row.name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="version" label='Status' width="80" />
          <el-table-column prop="category" label='Status' width="100">
            <template #default="{row}"><el-tag size="small">{{ row.category }}</el-tag></template>
          </el-table-column>
          <el-table-column :label="\('plugin.title')" width="80">
            <template #default="{row}">
              <el-tag v-if="row.id" size="small" :type="row._source==='package'?'warning':'default''>{{ row._source==='package'?'?:'' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="desc" label='Status' min-width="200" show-overflow-tooltip />
          <el-table-column label="? width="90">
            <template #default="{row}">
              <el-switch v-model="row.enabled" @change="toggleSkill(row)" size="small" :disabled="row._source==='package'' />
            </template>
          </el-table-column>
          <el-table-column label='Status' width="100" fixed="right">
            <template #default="{row}">
              <el-button v-if="row._source==='package'' text type="danger" size="small" @click="uninstallPackage(row)">OK</el-button>
              <el-button v-else text type="danger" size="small" @click="uninstallSkill(row)">OK</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="allInstalledSkills.length===0" description="? />
      </el-tab-pane>

      <!-- Tab 4: ?-->
      <el-tab-pane label=" ? name="publish">
        <el-card shadow="never">
          -
          <p style="color:#999;font-size:13px">?skill.json + main.py ?ZIP</p>
          <el-upload
            drag
            accept=".zip"
            :auto-upload="false"
            :on-change="handleFileChange"
            :file-list="publishFileList"
          >
            <el-icon style="font-size:48px;color:#667eea"><UploadFilled /></el-icon>
            <div style="font-size:14px;margin-top:8px"> ZIP ?-</div>
            <template #tip>
              <div style="font-size:12px;color:#999;margin-top:4px">
                 skill.json+ main.py
              </div>
            </template>
          </el-upload>
          <div style="margin-top:16px">
            <el-button type="primary" @click="publishSkill" :loading="publishing" :disabled="!publishFile">
               ?            </el-button>
          </div>
          <el-divider />
          <h4> ?URL </h4>
          <div style="display:flex;gap:8px">
            <el-input v-model="publishUrl" placeholder="https://example.com/my-skill.zip" style="flex:1" size="small" />
            <el-button @click="publishFromUrl" :loading="publishingUrl" size="small" :disabled="!publishUrl"></el-button>
          </div>
          <el-divider />
          -
          <pre style="font-size:12px;background:#f5f5f5;padding:12px;border-radius:4px">
my-skill.zip
 skill.json          # ??   id              
?   name            
?   version         # ??   desc            
?   author          # ??   category        
?   entry           # ?main.py??   dependencies    
 main.py             #  async def execute(params)? assets/             
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
const installing = ref('')
const search = ref('')
const categoryFilter = ref('')
const allSkills = ref([])
const categories = ref([])

const communitySearch = ref('')
const communityCategory = ref('')
const communityLoading = ref(false)
const communityInstalling = ref('')
const communitySkills = ref([])
const communityInstalledIds = ref([])

const publishFile = ref(null)
const publishFileList = ref([])
const publishing = ref(false)
const publishUrl = ref('')
const publishingUrl = ref(false)

const installedPackages = ref([])

// === ?===
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

// ===  ===
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
      ElMessage.success("?" + s.name + " ")
      s.installed = true
    }
  } catch (e) {
    ElMessage.error(": " + (e.response?.data?.detail || e.message))
  }
  installing.value = ''
}

async function uninstallSkill(s) {
  try {
    await ElMessageBox.confirm(" " + s.name + "?, "", { type: "warning" })
    const r = await agentApi.post("/agent/plugins/uninstall", { plugin_id: s.id })
    if (r.ok || r.uninstalled) {
      ElMessage.success(s.name + " ?)
      s.installed = false
    }
  } catch (e) {
    if (e !== "cancel") ElMessage.error('Error')
  }
}

async function toggleSkill(s) {
  try {
    await agentApi.post("/agent/plugins/toggle", { plugin_id: s.id, enabled: s.enabled })
    ElMessage.success(s.enabled ? s.name + " ? : s.name + " ?)
  } catch {
    s.enabled = !s.enabled
    ElMessage.error('Error')
  }
}

// ===  ===
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
      ElMessage.success("?" + s.name + " ")
      communityInstalledIds.value.push(s.id)
      fetchInstalledPackages()
    }
  } catch (e) {
    ElMessage.error(": " + (e.response?.data?.detail || e.message))
  }
  communityInstalling.value = ''
}

// === ?===
async function fetchInstalledPackages() {
  try {
    const r = await agentApi.get("/agent/plugins/installed/packages")
    if (r.skills) installedPackages.value = r.skills
  } catch { installedPackages.value = [] }
}

async function uninstallPackage(s) {
  try {
    await ElMessageBox.confirm(" " + s.name + "n?, "", { type: "warning" })
    const r = await agentApi.post("/agent/plugins/uninstall/" + s.id)
    if (r.ok || r.uninstalled) {
      ElMessage.success(s.name + " ?)
      installedPackages.value = installedPackages.value.filter(p => p.id !== s.id)
    }
  } catch (e) {
    if (e !== "cancel") ElMessage.error('Error')
  }
}

// === ?===
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
      ElMessage.success("?")
      publishFile.value = null
      publishFileList.value = []
      fetchInstalledPackages()
    } else {
      ElMessage.error(": " + (r.error || ""))
    }
  } catch (e) {
    ElMessage.error(": " + (e.response?.data?.detail || e.message))
  }
  publishing.value = false
}

async function publishFromUrl() {
  if (!publishUrl.value) return
  publishingUrl.value = true
  try {
    const r = await agentApi.post("/agent/plugins/publish", { download_url: publishUrl.value })
    if (r.ok) {
      ElMessage.success("?")
      publishUrl.value = ''
      fetchInstalledPackages()
    } else {
      ElMessage.error(": " + (r.error || ""))
    }
  } catch (e) {
    ElMessage.error(": " + (e.response?.data?.detail || e.message))
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
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>