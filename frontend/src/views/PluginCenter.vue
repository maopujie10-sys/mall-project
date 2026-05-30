<template>
  <div class="skill-center">
    <div class="page-header">
      <h2>馃З 鎶€鑳藉競鍦?/h2>
      <p>娴忚 路 瀹夎 路 绠＄悊 路 鍙戝竷 AI 鎶€鑳?/p>
      <div class="header-stats">
        <el-tag type="primary">鍐呯疆 {{ totalSkills }} 涓?/el-tag>
        <el-tag type="success">宸茶 {{ installedCount }}</el-tag>
        <el-tag type="warning">绀惧尯 {{ communityCount }}</el-tag>
      </div>
    </div>

    <el-tabs v-model="activeTab">
      <!-- Tab 1: 鍐呯疆鎶€鑳藉競鍦?-->
      <el-tab-pane label="馃洅 鍐呯疆甯傚満" name="market">
        <div class="toolbar">
          <el-input v-model="search" placeholder="鎼滅储..." clearable style="width:240px" size="small" />
          <el-select v-model="categoryFilter" placeholder="鍏ㄩ儴鍒嗙被" clearable style="width:140px" size="small">
            <el-option v-for="c in categories" :key="c.category" :label="(c.icon||'馃摝') + ' ' + c.category + ' (' + c.count + ')'" :value="c.category" />
          </el-select>
          <el-button @click="fetchMarket" size="small" :loading="loading">鍒锋柊</el-button>
        </div>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12" :md="8" v-for="s in filteredSkills" :key="s.id" style="margin-bottom:16px">
            <el-card shadow="hover" class="skill-card" :class="{installed:s.installed}">
              <div class="skill-header">
                <span class="skill-icon">{{ s.icon || "馃摝" }}</span>
                <div class="skill-info">
                  <h3>{{ s.name }}</h3>
                  <el-tag size="small">{{ s.category }}</el-tag>
                </div>
              </div>
              <p class="skill-desc">{{ s.desc }}</p>
              <div class="skill-meta">
                <span>猸?{{ s.stars }}</span>
                <span>馃摜 {{ s.downloads }}</span>
                <span>v{{ s.version }}</span>
                <span>鉁嶏笍 {{ s.author }}</span>
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
              >{{ s.installed ? '鉁?宸插畨瑁? : '馃摜 瀹夎' }}</el-button>
            </el-card>
          </el-col>
        </el-row>
        <el-empty v-if="filteredSkills.length===0" description="娌℃湁鍖归厤鐨勬妧鑳? />
      </el-tab-pane>

      <!-- Tab 2: 绀惧尯甯傚満 -->
      <el-tab-pane label="馃實 绀惧尯甯傚満" name="community">
        <div class="toolbar">
          <el-input v-model="communitySearch" placeholder="鎼滅储绀惧尯鎶€鑳?.." clearable style="width:240px" size="small" />
          <el-select v-model="communityCategory" placeholder="鍏ㄩ儴鍒嗙被" clearable style="width:140px" size="small">
            <el-option v-for="c in communityCategories" :key="c" :label="c" :value="c" />
          </el-select>
          <el-button @click="fetchCommunity" size="small" :loading="communityLoading">鍒锋柊</el-button>
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
                <span>猸?{{ s.stars }}</span>
                <span>馃摜 {{ s.downloads }}</span>
                <span>鉁嶏笍 {{ s.author }}</span>
                <span>馃晲 {{ s.updated_at }}</span>
              </div>
              <div class="skill-tags" v-if="s.tags">
                <el-tag v-for="t in s.tags.slice(0,3)" :key="t" size="small" effect="plain">{{ t }}</el-tag>
              </div>
              <div style="font-size:11px;color:#999;margin-top:6px;padding:6px;background:#f5f5f5;border-radius:4px">
                馃摉 {{ s.readme }}
              </div>
              <el-button
                :type="isCommunityInstalled(s.id) ? 'success' : 'primary'"
                size="small" style="width:100%;margin-top:10px"
                :disabled="isCommunityInstalled(s.id) || communityInstalling === s.id"
                :loading="communityInstalling === s.id"
                @click="installCommunity(s)"
              >{{ isCommunityInstalled(s.id) ? '鉁?宸插畨瑁? : '馃摜 瀹夎' }}</el-button>
            </el-card>
          </el-col>
        </el-row>
        <el-empty v-if="filteredCommunity.length===0" description="鏆傛棤绀惧尯鎶€鑳? />
      </el-tab-pane>

      <!-- Tab 3: 宸插畨瑁?-->
      <el-tab-pane label="馃摝 宸插畨瑁? name="installed">
        <el-table :data="allInstalledSkills" stripe size="small">
          <el-table-column label="鎶€鑳? min-width="200">
            <template #default="{row}">
              <span style="font-size:18px;margin-right:6px">{{ row.icon || "馃摝" }}</span>
              <span style="font-weight:500">{{ row.name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="version" label="鐗堟湰" width="80" />
          <el-table-column prop="category" label="鍒嗙被" width="100">
            <template #default="{row}"><el-tag size="small">{{ row.category }}</el-tag></template>
          </el-table-column>
          <el-table-column label="鏉ユ簮" width="80">
            <template #default="{row}">
              <el-tag v-if="row.id" size="small" :type="row._source==='package'?'warning':'default'">{{ row._source==='package'?'鍖?:'鍐呯疆' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="desc" label="鎻忚堪" min-width="200" show-overflow-tooltip />
          <el-table-column label="鐘舵€? width="90">
            <template #default="{row}">
              <el-switch v-model="row.enabled" @change="toggleSkill(row)" size="small" :disabled="row._source==='package'" />
            </template>
          </el-table-column>
          <el-table-column label="鎿嶄綔" width="100" fixed="right">
            <template #default="{row}">
              <el-button v-if="row._source==='package'" text type="danger" size="small" @click="uninstallPackage(row)">鍗歌浇</el-button>
              <el-button v-else text type="danger" size="small" @click="uninstallSkill(row)">鍗歌浇</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="allInstalledSkills.length===0" description="鏆傛棤宸插畨瑁呮妧鑳? />
      </el-tab-pane>

      <!-- Tab 4: 鍙戝竷鎶€鑳?-->
      <el-tab-pane label="馃摛 鍙戝竷鎶€鑳? name="publish">
        <el-card shadow="never">
          <h3 style="margin-top:0">馃摛 鍙戝竷鎶€鑳藉寘</h3>
          <p style="color:#999;font-size:13px">灏嗕綘鐨?skill.json + main.py 鎵撳寘鎴?ZIP 涓婁紶锛屽嵆鍙湪绯荤粺涓畨瑁呬娇鐢?/p>
          <el-upload
            drag
            accept=".zip"
            :auto-upload="false"
            :on-change="handleFileChange"
            :file-list="publishFileList"
          >
            <el-icon style="font-size:48px;color:#667eea"><UploadFilled /></el-icon>
            <div style="font-size:14px;margin-top:8px">鎷栨嫿 ZIP 鏂囦欢鍒版澶勶紝鎴?<em>鐐瑰嚮涓婁紶</em></div>
            <template #tip>
              <div style="font-size:12px;color:#999;margin-top:4px">
                闇€鍖呭惈 skill.json锛堟竻鍗曪級+ main.py锛堝叆鍙ｄ唬鐮侊級
              </div>
            </template>
          </el-upload>
          <div style="margin-top:16px">
            <el-button type="primary" @click="publishSkill" :loading="publishing" :disabled="!publishFile">
              馃摛 鍙戝竷骞跺畨瑁?            </el-button>
          </div>
          <el-divider />
          <h4>馃敆 浠?URL 瀹夎</h4>
          <div style="display:flex;gap:8px">
            <el-input v-model="publishUrl" placeholder="https://example.com/my-skill.zip" style="flex:1" size="small" />
            <el-button @click="publishFromUrl" :loading="publishingUrl" size="small" :disabled="!publishUrl">瀹夎</el-button>
          </div>
          <el-divider />
          <h4>馃摝 鎶€鑳藉寘鏍煎紡瑕佹眰</h4>
          <pre style="font-size:12px;background:#f5f5f5;padding:12px;border-radius:4px">
my-skill.zip
鈹溾攢鈹€ skill.json          # 蹇呭～锛氭妧鑳芥竻鍗?鈹?  鈹溾攢鈹€ id              # 鍞竴鏍囪瘑
鈹?  鈹溾攢鈹€ name            # 鏄剧ず鍚嶇О
鈹?  鈹溾攢鈹€ version         # 鐗堟湰鍙?鈹?  鈹溾攢鈹€ desc            # 鎻忚堪
鈹?  鈹溾攢鈹€ author          # 浣滆€?鈹?  鈹溾攢鈹€ category        # 鍒嗙被
鈹?  鈹溾攢鈹€ entry           # 鍏ュ彛鏂囦欢锛堥粯璁?main.py锛?鈹?  鈹斺攢鈹€ dependencies    # 渚濊禆鍒楄〃
鈹溾攢鈹€ main.py             # 鍏ュ彛浠ｇ爜锛堥渶瀹炵幇 async def execute(params)锛?鈹斺攢鈹€ assets/             # 璧勬簮鏂囦欢锛堝彲閫夛級
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

// 绀惧尯
const communitySearch = ref("")
const communityCategory = ref("")
const communityLoading = ref(false)
const communityInstalling = ref("")
const communitySkills = ref([])
const communityInstalledIds = ref([])

// 鍙戝竷
const publishFile = ref(null)
const publishFileList = ref([])
const publishing = ref(false)
const publishUrl = ref("")
const publishingUrl = ref(false)

// 宸插畨瑁呭寘
const installedPackages = ref([])

// === 璁＄畻灞炴€?===
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

// === 鍐呯疆甯傚満 ===
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
      ElMessage.success("鉁?" + s.name + " 瀹夎鎴愬姛")
      s.installed = true
    }
  } catch (e) {
    ElMessage.error("瀹夎澶辫触: " + (e.response?.data?.detail || e.message))
  }
  installing.value = ""
}

async function uninstallSkill(s) {
  try {
    await ElMessageBox.confirm("纭畾鍗歌浇 " + s.name + "锛?, "纭", { type: "warning" })
    const r = await agentApi.post("/agent/plugins/uninstall", { plugin_id: s.id })
    if (r.ok || r.uninstalled) {
      ElMessage.success(s.name + " 宸插嵏杞?)
      s.installed = false
    }
  } catch (e) {
    if (e !== "cancel") ElMessage.error("鍗歌浇澶辫触")
  }
}

async function toggleSkill(s) {
  try {
    await agentApi.post("/agent/plugins/toggle", { plugin_id: s.id, enabled: s.enabled })
    ElMessage.success(s.enabled ? s.name + " 宸插惎鐢? : s.name + " 宸茬鐢?)
  } catch {
    s.enabled = !s.enabled
    ElMessage.error("鎿嶄綔澶辫触")
  }
}

// === 绀惧尯甯傚満 ===
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
      ElMessage.success("鉁?" + s.name + " 瀹夎鎴愬姛")
      communityInstalledIds.value.push(s.id)
      fetchInstalledPackages()
    }
  } catch (e) {
    ElMessage.error("瀹夎澶辫触: " + (e.response?.data?.detail || e.message))
  }
  communityInstalling.value = ""
}

// === 瀹夎鍖呯鐞?===
async function fetchInstalledPackages() {
  try {
    const r = await agentApi.get("/agent/plugins/installed/packages")
    if (r.skills) installedPackages.value = r.skills
  } catch { installedPackages.value = [] }
}

async function uninstallPackage(s) {
  try {
    await ElMessageBox.confirm("纭畾鍗歌浇鎶€鑳藉寘 " + s.name + "锛焅n鏂囦欢灏嗚鍒犻櫎銆?, "纭", { type: "warning" })
    const r = await agentApi.post("/agent/plugins/uninstall/" + s.id)
    if (r.ok || r.uninstalled) {
      ElMessage.success(s.name + " 宸插嵏杞?)
      installedPackages.value = installedPackages.value.filter(p => p.id !== s.id)
    }
  } catch (e) {
    if (e !== "cancel") ElMessage.error("鍗歌浇澶辫触")
  }
}

// === 鍙戝竷鎶€鑳?===
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
      ElMessage.success("鉁?鎶€鑳藉彂甯冨苟瀹夎鎴愬姛")
      publishFile.value = null
      publishFileList.value = []
      fetchInstalledPackages()
    } else {
      ElMessage.error("鍙戝竷澶辫触: " + (r.error || "鏈煡閿欒"))
    }
  } catch (e) {
    ElMessage.error("鍙戝竷澶辫触: " + (e.response?.data?.detail || e.message))
  }
  publishing.value = false
}

async function publishFromUrl() {
  if (!publishUrl.value) return
  publishingUrl.value = true
  try {
    const r = await agentApi.post("/agent/plugins/publish", { download_url: publishUrl.value })
    if (r.ok) {
      ElMessage.success("鉁?瀹夎鎴愬姛")
      publishUrl.value = ""
      fetchInstalledPackages()
    } else {
      ElMessage.error("瀹夎澶辫触: " + (r.error || "鏈煡閿欒"))
    }
  } catch (e) {
    ElMessage.error("瀹夎澶辫触: " + (e.response?.data?.detail || e.message))
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