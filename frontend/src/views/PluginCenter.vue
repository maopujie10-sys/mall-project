<template>
  <div class="skill-center">
    <div class="page-header">
      <h2>🧩 技能市场</h2>
      <p>浏览 · 安装 · 管理 AI 技能</p>
      <div class="header-stats">
        <el-tag>总计 {{ totalSkills }} 个技能</el-tag>
        <el-tag type="success">已安装 {{ installedCount }}</el-tag>
        <el-tag type="warning">分类 {{ categoryCount }} 类</el-tag>
      </div>
    </div>

    <el-tabs v-model="activeTab">
      <!-- 技能市场 -->
      <el-tab-pane label="🛒 技能市场" name="market">
        <div class="toolbar">
          <el-input v-model="search" placeholder="搜索技能..." clearable style="width:280px" size="small" />
          <el-select v-model="categoryFilter" placeholder="全部分类" clearable style="width:140px" size="small">
            <el-option v-for="c in categories" :key="c.category" :label="c.icon + ' ' + c.category + ' (' + c.count + ')'" :value="c.category" />
          </el-select>
          <el-button @click="fetchMarket" size="small" :loading="loading">刷新</el-button>
        </div>
        <el-row :gutter="16">
          <el-col :span="8" v-for="s in filteredSkills" :key="s.id" style="margin-bottom:16px">
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

      <!-- 已安装 -->
      <el-tab-pane label="📦 已安装" name="installed">
        <el-table :data="installedSkills" stripe size="small">
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
          <el-table-column prop="desc" label="描述" min-width="200" show-overflow-tooltip />
          <el-table-column label="状态" width="90">
            <template #default="{row}">
              <el-switch v-model="row.enabled" @change="toggleSkill(row)" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{row}">
              <el-button text type="danger" size="small" @click="uninstallSkill(row)">卸载</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="installedSkills.length===0" description="暂无已安装技能" />
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

const totalSkills = computed(() => allSkills.value.length)
const installedCount = computed(() => allSkills.value.filter(s => s.installed).length)
const categoryCount = computed(() => categories.value.length)

const installedSkills = computed(() => allSkills.value.filter(s => s.installed))

const filteredSkills = computed(() => {
  let list = allSkills.value.filter(s => !s.installed)
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(s => s.name.toLowerCase().includes(q) || s.desc.toLowerCase().includes(q))
  }
  if (categoryFilter.value) {
    list = list.filter(s => s.category === categoryFilter.value)
  }
  return list
})

async function fetchMarket() {
  loading.value = true
  try {
    const r = await agentApi.get("/agent/plugins")
    if (r.plugins) {
      allSkills.value = r.plugins
    }
  } catch {
    allSkills.value = []
  }
  try {
    const r = await agentApi.get("/agent/plugins/categories")
    if (r.categories) categories.value = r.categories
  } catch { categories.value = [] }
  loading.value = false
}

async function installSkill(s) {
  installing.value = s.id
  try {
    const r = await agentApi.post("/agent/plugins/install", null, { params: { plugin_id: s.id } })
    if (r.ok || r.status === "installed" || r.status === "already_installed") {
      ElMessage.success(`✅ ${s.name} 安装成功`)
      s.installed = true
    }
  } catch (e) {
    ElMessage.error("安装失败: " + (e.response?.data?.detail || e.message))
  }
  installing.value = ""
}

async function uninstallSkill(s) {
  try {
    await ElMessageBox.confirm(`确定卸载 ${s.name}？`, "确认", { type: "warning" })
    const r = await agentApi.post("/agent/plugins/uninstall", null, { params: { plugin_id: s.id } })
    if (r.ok || r.uninstalled) {
      ElMessage.success(`${s.name} 已卸载`)
      s.installed = false
    }
  } catch (e) {
    if (e !== "cancel") ElMessage.error("卸载失败")
  }
}

async function toggleSkill(s) {
  try {
    await agentApi.post("/agent/plugins/toggle", { plugin_id: s.id, enabled: s.enabled })
    ElMessage.success(s.enabled ? `${s.name} 已启用` : `${s.name} 已禁用`)
  } catch {
    s.enabled = !s.enabled
    ElMessage.error("操作失败")
  }
}

onMounted(fetchMarket)
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
