<template>
  <div class="page-container plugin-center">
    <div class="page-header"><h2>插件系统</h2><p>插件安装 · 启用 · 配置 · 市场浏览</p></div>

    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6"><div class="metric-card"><div class="metric-label">已安装</div><div class="metric-value" style="color:#52c41a">{{ installedCount }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">已启用</div><div class="metric-value" style="color:#667eea">{{ enabledCount }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">可用</div><div class="metric-value">{{ availableCount }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">需要更新</div><div class="metric-value" style="color:#faad14">{{ updateCount }}</div></div></el-col>
    </el-row>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="已安装" name="installed">
        <div class="tab-toolbar">
          <el-input v-model="search" placeholder="搜索插件..." prefix-icon="Search" style="width:280px" clearable />
          <el-button type="primary" @click="activeTab='market'">浏览市场</el-button>
        </div>
        <el-table :data="filteredInstalled" stripe>
          <el-table-column prop="name" label="插件" min-width="180"><template #default="{row}"><span class="plug-name">{{ row.icon }} {{ row.name }}</span><el-tag v-if="row.updateAvailable" type="warning" size="small" style="margin-left:8px">更新</el-tag></template></el-table-column>
          <el-table-column prop="version" label="版本" width="90" />
          <el-table-column prop="desc" label="描述" min-width="240" show-overflow-tooltip />
          <el-table-column prop="author" label="作者" width="120" />
          <el-table-column label="状态" width="100"><template #default="{row}"><el-switch v-model="row.enabled" @change="toggle(row)" size="small" /></template></el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{row}">
              <el-button link type="primary" size="small" @click="configPlugin(row)">配置</el-button>
              <el-button v-if="row.updateAvailable" link type="warning" size="small" @click="updatePlugin(row)">更新</el-button>
              <el-button link type="danger" size="small" @click="removePlugin(row)">卸载</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!filteredInstalled.length" description="暂无已安装插件" />
      </el-tab-pane>

      <el-tab-pane label="插件市场" name="market">
        <div class="tab-toolbar"><el-input v-model="marketSearch" placeholder="搜索市场..." prefix-icon="Search" style="width:280px" clearable /><el-select v-model="marketCategory" placeholder="分类" style="width:140px" clearable><el-option v-for="c in marketCats" :key="c" :label="c" :value="c" /></el-select></div>
        <el-row :gutter="16">
          <el-col :span="8" v-for="p in filteredMarket" :key="p.id">
            <el-card shadow="hover" class="market-card">
              <div class="market-icon">{{ p.icon }}</div>
              <h3>{{ p.name }}</h3>
              <el-tag size="small">{{ p.category }}</el-tag>
              <p>{{ p.desc }}</p>
              <div class="market-meta"><span>⭐ {{ p.stars }}</span><span>📥 {{ p.downloads }}</span><span>{{ p.version }}</span></div>
              <el-button :type="p.installed?'success':'primary'" size="small" style="width:100%;margin-top:12px" @click="p.installed?null:installMarket(p)" :disabled="p.installed || installing===p.id" :loading="installing===p.id">{{ p.installed?'已安装':'安装' }}</el-button>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>
    </el-tabs>

    <!-- 配置对话框 -->
    <el-dialog v-model="showConfig" title="插件配置" width="520px">
      <el-form v-if="configPluginData" label-width="100px">
        <el-form-item v-for="(v,k) in configPluginData.config" :key="k" :label="k">
          <el-input v-if="typeof v==='string'" v-model="configPluginData.config[k]" />
          <el-switch v-else-if="typeof v==='boolean'" v-model="configPluginData.config[k]" />
        </el-form-item>
      </el-form>
      <template #footer><el-button @click="showConfig=false">取消</el-button><el-button type="primary" @click="saveConfig" :loading="saving">保存配置</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
const plugins = ref([{name:'趋势监控',version:'1.0',status:'active'},{name:'商品采集',version:'1.2',status:'active'},{name:'自动备份',version:'0.9',status:'active'},{name:'AI作图',version:'0.5',status:'idle'}])
function togglePlugin(p) { p.status = p.status === 'active' ? 'idle' : 'active'; ElMessage.success(p.name + ' 已' + (p.status==='active'?'启用':'停用')) }
onMounted(function() {})
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