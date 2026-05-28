<template>
  <div class="page-container plugin-center">
    <div class="page-header"><h2>鎻掍欢绯荤粺</h2><p>鎻掍欢瀹夎 路 鍚敤 路 閰嶇疆 路 甯傚満娴忚</p></div>

    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6"><div class="metric-card"><div class="metric-label">宸插畨瑁?/div><div class="metric-value" style="color:#52c41a">{{ installedCount }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">宸插惎鐢?/div><div class="metric-value" style="color:#667eea">{{ enabledCount }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">鍙敤</div><div class="metric-value">{{ availableCount }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">闇€瑕佹洿鏂?/div><div class="metric-value" style="color:#faad14">{{ updateCount }}</div></div></el-col>
    </el-row>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="宸插畨瑁? name="installed">
        <div class="tab-toolbar">
          <el-input v-model="search" placeholder="鎼滅储鎻掍欢..." prefix-icon="Search" style="width:280px" clearable />
          <el-button type="primary" @click="activeTab='market'">娴忚甯傚満</el-button>
        </div>
        <el-table :data="filteredInstalled" stripe v-loading="loading">
          <el-table-column prop="name" label="鎻掍欢" min-width="180"><template #default="{row}"><span class="plug-name">{{ row.icon || '馃攲' }} {{ row.name }}</span><el-tag v-if="row.updateAvailable" type="warning" size="small" style="margin-left:8px">鏇存柊</el-tag></template></el-table-column>
          <el-table-column prop="version" label="鐗堟湰" width="90" />
          <el-table-column prop="desc" label="鎻忚堪" min-width="240" show-overflow-tooltip />
          <el-table-column prop="author" label="浣滆€? width="120" />
          <el-table-column label="鐘舵€? width="100"><template #default="{row}"><el-switch v-model="row.enabled" @change="toggle(row)" size="small" /></template></el-table-column>
          <el-table-column label="鎿嶄綔" width="180" fixed="right">
            <template #default="{row}">
              <el-button link type="primary" size="small" @click="configPlugin(row)">閰嶇疆</el-button>
              <el-button v-if="row.updateAvailable" link type="warning" size="small" @click="updatePlugin(row)">鏇存柊</el-button>
              <el-button link type="danger" size="small" @click="removePlugin(row)">鍗歌浇</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!loading && !filteredInstalled.length" description="鏆傛棤宸插畨瑁呮彃浠讹紝鍘诲競鍦虹湅鐪嬪惂" />
      </el-tab-pane>

      <el-tab-pane label="鎻掍欢甯傚満" name="market">
        <div class="tab-toolbar"><el-input v-model="marketSearch" placeholder="鎼滅储甯傚満..." prefix-icon="Search" style="width:280px" clearable /><el-select v-model="marketCategory" placeholder="鍒嗙被" style="width:140px" clearable><el-option v-for="c in marketCats" :key="c" :label="c" :value="c" /></el-select></div>
        <el-row :gutter="16">
          <el-col :span="8" v-for="p in filteredMarket" :key="p.id">
            <el-card shadow="hover" class="market-card">
              <div class="market-icon">{{ p.icon || '馃摝' }}</div>
              <h3>{{ p.name }}</h3>
              <el-tag size="small">{{ p.category || '宸ュ叿' }}</el-tag>
              <p>{{ p.desc }}</p>
              <div class="market-meta"><span>猸?{{ p.stars || 0 }}</span><span>馃摜 {{ p.downloads || 0 }}</span><span>{{ p.version }}</span></div>
              <el-button :type="p.installed?'success':'primary'" size="small" style="width:100%;margin-top:12px" @click="p.installed?null:installMarket(p)" :disabled="p.installed || installing===p.id" :loading="installing===p.id">{{ p.installed?'宸插畨瑁?:'瀹夎' }}</el-button>
            </el-card>
          </el-col>
        </el-row>
        <el-empty v-if="!filteredMarket.length" description="鏆傛棤鍙敤鎻掍欢" />
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="showConfig" title="鎻掍欢閰嶇疆" width="520px">
      <el-form v-if="configPluginData" label-width="100px">
        <el-form-item v-for="(v,k) in configPluginData.config" :key="k" :label="k">
          <el-input v-if="typeof v==='string'" v-model="configPluginData.config[k]" />
          <el-switch v-else-if="typeof v==='boolean'" v-model="configPluginData.config[k]" />
        </el-form-item>
      </el-form>
      <template #footer><el-button @click="showConfig=false">鍙栨秷</el-button><el-button type="primary" @click="saveConfig" :loading="saving">淇濆瓨閰嶇疆</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listPlugins, togglePlugin, installPlugin, uninstallPlugin, getPluginConfig, updatePluginConfig } from '@/api/plugin'

const activeTab = ref('installed')
const search = ref('')
const marketSearch = ref('')
const marketCategory = ref('')
const installing = ref('')
const loading = ref(false)
const saving = ref(false)
const showConfig = ref(false)
const configPluginData = ref(null)

const plugins = ref([])
const marketplace = ref([])
const marketCats = ['閲囬泦', '鐩戞帶', 'AI', '瀹夊叏', '杩愮淮', '鏁版嵁']

const installedCount = computed(() => plugins.value.length)
const enabledCount = computed(() => plugins.value.filter(p => p.enabled).length)
const availableCount = computed(() => marketplace.value.length)
const updateCount = computed(() => plugins.value.filter(p => p.updateAvailable).length)

const filteredInstalled = computed(() => {
  if (!search.value) return plugins.value
  const q = search.value.toLowerCase()
  return plugins.value.filter(p => p.name.toLowerCase().includes(q) || (p.desc||'').toLowerCase().includes(q))
})

const filteredMarket = computed(() => {
  let list = marketplace.value
  if (marketSearch.value) {
    const q = marketSearch.value.toLowerCase()
    list = list.filter(p => p.name.toLowerCase().includes(q) || (p.desc||'').toLowerCase().includes(q))
  }
  if (marketCategory.value) list = list.filter(p => p.category === marketCategory.value)
  return list
})

async function fetchPlugins() {
  loading.value = true
  try {
    const resp = await listPlugins()
    if (resp?.plugins) plugins.value = resp.plugins
    if (resp?.marketplace) marketplace.value = resp.marketplace
  } catch {}
  loading.value = false
}

async function toggle(row) {
  try {
    await togglePlugin(row.id, row.enabled)
    ElMessage.success(row.enabled ? `${row.name} 宸插惎鐢╜ : `${row.name} 宸茬鐢╜)
  } catch { ElMessage.error('鎿嶄綔澶辫触') }
}

async function installMarket(p) {
  installing.value = p.id
  try {
    await installPlugin(p.id)
    p.installed = true
    plugins.value.push({ ...p, enabled: true })
    ElMessage.success(`${p.name} 瀹夎鎴愬姛`)
  } catch { ElMessage.error('瀹夎澶辫触') }
  installing.value = ''
}

async function removePlugin(p) {
  try {
    await ElMessageBox.confirm(`纭畾鍗歌浇 "${p.name}"锛焋, '纭鍗歌浇', { type: 'warning' })
    await uninstallPlugin(p.id)
    plugins.value = plugins.value.filter(x => x.id !== p.id)
    ElMessage.success('宸插嵏杞?)
  } catch {}
}

async function configPlugin(p) {
  try {
    const resp = await getPluginConfig(p.id)
    configPluginData.value = { id: p.id, name: p.name, config: resp?.config || {} }
    showConfig.value = true
  } catch { ElMessage.error('鑾峰彇閰嶇疆澶辫触') }
}

async function saveConfig() {
  if (!configPluginData.value) return
  saving.value = true
  try {
    await updatePluginConfig(configPluginData.value.id, configPluginData.value.config)
    showConfig.value = false
    ElMessage.success('閰嶇疆宸蹭繚瀛?)
  } catch { ElMessage.error('淇濆瓨澶辫触') }
  saving.value = false
}

function updatePlugin(p) {
  ElMessage.info('鏇存柊鍔熻兘寮€鍙戜腑')
}

onMounted(fetchPlugins)
</script>

<style scoped>
.plugin-center { padding: 24px; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 18px; margin: 0 0 4px; }
.page-header p { color: var(--text-muted); font-size: 13px; margin: 0; }
.metric-card { background: var(--bg-card); border-radius: 8px; padding: 18px; border: 1px solid var(--border-color); }
.metric-label { font-size: 12px; color: var(--text-muted); margin-bottom: 6px; }
.metric-value { font-size: 28px; font-weight: 700; }
.tab-toolbar { display: flex; gap: 12px; margin-bottom: 16px; align-items: center; }
.plug-name { font-weight: 500; }
.market-card { text-align: center; transition: all 0.2s; }
.market-card:hover { transform: translateY(-4px); }
.market-icon { font-size: 40px; margin-bottom: 8px; }
.market-card h3 { margin: 0 0 8px; font-size: 15px; }
.market-card p { color: var(--text-muted); font-size: 12px; margin: 8px 0; }
.market-meta { display: flex; justify-content: center; gap: 12px; font-size: 11px; color: var(--text-muted); }
</style>