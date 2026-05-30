<template>
  <div class="page-container memory-center">
    <div class="page-header"><h2>记忆中心</h2><p>长期记忆 · HANDOFF交接 · 操作日志 · 代码变更历史</p></div>
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6"><div class="metric-card"><div class="metric-label">记忆总数</div><div class="metric-value">{{ memories.length }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">知识图谱</div><div class="metric-value" style="color:#667eea">{{ graphNodes }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">交接文档</div><div class="metric-value" style="color:#52c41a">{{ handoffCount }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">操作日志</div><div class="metric-value" style="color:#faad14">{{ operationLogs.length }}</div></div></el-col>
    </el-row>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="全部记忆" name="all">
        <div class="tab-toolbar">
          <el-input v-model="searchQuery" placeholder="搜索记忆..." style="width:280px" clearable @clear="refreshMemories" @keyup.enter="searchMem" />
          <el-select v-model="filterCategory" placeholder="分类筛选" style="width:140px" clearable @change="refreshMemories">
            <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
          </el-select>
          <el-button type="primary" @click="showAdd = true">新增记忆</el-button>
        </div>
        <el-table :data="filteredMemories" stripe max-height="calc(100vh - 380px)">
          <el-table-column type="index" width="50" />
          <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
          <el-table-column prop="category" label="分类" width="110">
            <template #default="{row}"><el-tag :type="catType(row.category)" size="small">{{ row.category }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="content" label="内容" min-width="280" show-overflow-tooltip />
          <el-table-column prop="created_at" label="时间" width="170" sortable />
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{row}">
              <el-button link type="primary" size="small" @click="viewMemory(row)">查看</el-button>
              <el-button link type="warning" size="small" @click="editMemory(row)">编辑</el-button>
              <el-button link type="danger" size="small" @click="removeMemory(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="HANDOFF交接" name="handoff">
        <el-button type="primary" @click="showHandoffEdit=!showHandoffEdit" style="margin-bottom:12px">{{showHandoffEdit?'预览':'编辑'}}</el-button>
        <div v-if="!showHandoffEdit && handoffContent" class="doc-viewer"><pre class="doc-content">{{ handoffContent }}</pre></div>
        <el-input v-if="showHandoffEdit" v-model="handoffContent" type="textarea" :rows="20" placeholder="编辑HANDOFF交接文档..." />
        <el-button v-if="showHandoffEdit" type="primary" @click="saveHandoff" :loading="saving" style="margin-top:12px">保存交接文档</el-button>
        <el-empty v-if="!handoffContent && !showHandoffEdit" description="暂无交接文档" />
      </el-tab-pane>
      <el-tab-pane label="操作日志" name="oplog">
        <el-timeline v-if="operationLogs.length">
          <el-timeline-item v-for="log in operationLogs" :key="log.id" :timestamp="log.time" :type="log.level==='error'?'danger':log.level==='warn'?'warning':'primary'" placement="top">
            <el-card shadow="hover"><p>{{ log.action }} - {{ log.detail }}</p><small v-if="log.file">{{ log.file }}</small></el-card>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="暂无操作日志" />
      </el-tab-pane>
    </el-tabs>
    <el-dialog v-model="showAdd" :title="editingId?'编辑记忆':'新增记忆'" width="560px">
      <el-form :model="form" label-width="70px">
        <el-form-item label="标题"><el-input v-model="form.title" placeholder="记忆标题" /></el-form-item>
        <el-form-item label="分类"><el-select v-model="form.category" style="width:100%"><el-option v-for="c in categories" :key="c" :label="c" :value="c" /></el-select></el-form-item>
        <el-form-item label="内容"><el-input v-model="form.content" type="textarea" :rows="8" placeholder="记忆内容..." /></el-form-item>
      </el-form>
      <template #footer><el-button @click="showAdd=false">取消</el-button><el-button type="primary" @click="saveMem" :loading="saving">{{editingId?'保存':'添加'}}</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'; import { ElMessage } from 'element-plus'; import { agentApi } from '@/api/index'
const memories = ref([]); const loading = ref(false); const saving = ref(false); const searchQuery = ref('')
const filterCategory = ref(''); const activeTab = ref('all'); const showAdd = ref(false); const editingId = ref(null)
const showHandoffEdit = ref(false); const handoffContent = ref(''); const operationLogs = ref([])
const form = ref({ title: '', category: 'general', content: '', tags: [] })
const categories = ref(['general','代码','部署','运维','采集','商城','配置','告警','日记'])
const graphNodes = ref(0); const handoffCount = ref(0)

const filteredMemories = computed(() => {
  let list = memories.value
  if(searchQuery.value) { const q = searchQuery.value.toLowerCase(); list = list.filter(m => (m.title||'').toLowerCase().includes(q) || (m.content||'').toLowerCase().includes(q)) }
  if(filterCategory.value) { list = list.filter(m => m.category === filterCategory.value) }
  return list
})
function catType(c) { const map = { '代码':'', '部署':'warning', '运维':'info', '采集':'success', '商城':'', '配置':'info', '告警':'danger', '日记':'' }; return map[c] || '' }

async function fetchMemories() {
  loading.value = true
  try { const r = await agentApi.get('/agent/memory/list'); if(r?.data?.ok) { memories.value = r.data.memories || []; graphNodes.value = r.data.total || 0 } }
  catch(e) { console.error(e) }
  try { const h = await agentApi.get('/agent/memory/handoff'); if(h?.data?.ok) { handoffContent.value = h.data.content || ''; handoffCount.value = h.data.content ? 1 : 0 } } catch(e) {}
  try { const l = await agentApi.get('/agent/memory/logs'); if(l?.data?.ok) { operationLogs.value = l.data.logs || [] } } catch(e) {}
  loading.value = false
}
function refreshMemories() { fetchMemories() }
function searchMem() { refreshMemories() }
function viewMemory(row) { form.value = {...row}; showAdd.value = true; editingId.value = row.id }
function editMemory(row) { viewMemory(row) }
async function removeMemory(id) { try { await agentApi.delete('/agent/memory/'+id); ElMessage.success('已删除'); fetchMemories() } catch(e) { ElMessage.error('删除失败') } }
async function saveMem() {
  saving.value = true
  try {
    if(editingId.value) { await agentApi.put('/agent/memory/'+editingId.value, form.value) }
    else { await agentApi.post('/agent/memory/add', form.value) }
    ElMessage.success(editingId.value?'已更新':'已添加'); showAdd.value = false; editingId.value = null
    form.value = { title: '', category: 'general', content: '', tags: [] }; fetchMemories()
  } catch(e) { ElMessage.error('保存失败') }
  saving.value = false
}
async function saveHandoff() {
  saving.value = true
  try { await agentApi.post('/agent/memory/handoff', { content: handoffContent.value }); ElMessage.success('已保存'); showHandoffEdit.value = false } catch(e) { ElMessage.error('保存失败') }
  saving.value = false
}
onMounted(() => fetchMemories())
</script>
<style scoped>
.memory-center { padding: 24px; }
.page-header { margin-bottom: 16px; } .page-header h2 { font-size: 18px; margin: 0 0 4px; } .page-header p { color: var(--text-muted); font-size: 13px; margin: 0; }
.metric-card { background: rgba(0,0,0,0.25); border: 1px solid rgba(102,126,234,0.15); border-radius: 10px; padding: 16px; text-align: center; }
.metric-label { font-size: 12px; color: var(--text-muted); margin-bottom: 6px; } .metric-value { font-size: 28px; font-weight: 700; }
.tab-toolbar { display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }
.doc-content { white-space: pre-wrap; font-size: 13px; line-height: 1.7; background: rgba(0,0,0,0.2); padding: 16px; border-radius: 8px; max-height: 350px; overflow-y: auto; }
.doc-viewer { max-height: 500px; overflow-y: auto; }
@media (max-width: 768px) { .memory-center { padding: 10px; } .tab-toolbar { flex-direction: column; } .metric-card { padding: 10px; } .metric-value { font-size: 22px; } }
</style>