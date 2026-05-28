<template>
  <div class="page-container memory-center">
    <div class="page-header">
      <h2>记忆中心</h2>
      <p>长期记忆 · HANDOFF交接 · 操作日志 · 代码变更历史</p>
    </div>

    <!-- 统计 -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6"><div class="metric-card"><div class="metric-label">记忆总数</div><div class="metric-value">{{ memories.length }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">知识图谱</div><div class="metric-value" style="color:#667eea">{{ graphNodes }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">交接文档</div><div class="metric-value" style="color:#52c41a">{{ handoffCount }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">操作日志</div><div class="metric-value" style="color:#faad14">{{ operationLogs.length }}</div></div></el-col>
    </el-row>

    <el-tabs v-model="activeTab" @tab-change="onTabChange">
      <!-- 全部记忆 -->
      <el-tab-pane label="全部记忆" name="all">
        <div class="tab-toolbar">
          <el-input v-model="searchQuery" placeholder="搜索记忆..." prefix-icon="Search" style="width:280px" clearable @clear="loadMemories" @keyup.enter="searchMem" />
          <el-select v-model="filterCategory" placeholder="分类筛选" style="width:140px" clearable @change="loadMemories">
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
          <el-table-column prop="tags" label="标签" width="160"><template #default="{row}"><el-tag v-for="t in row.tags" :key="t" size="small" style="margin-right:4px">{{ t }}</el-tag></template></el-table-column>
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

      <!-- HANDOFF 交接文档 -->
      <el-tab-pane label="交接文档" name="handoff">
        <div class="tab-toolbar"><el-button type="primary" @click="showHandoffEdit=!showHandoffEdit">{{showHandoffEdit?'预览':'编辑'}}</el-button></div>
        <div v-if="!showHandoffEdit && handoffData" class="doc-viewer">
          <el-alert title="HANDOFF.md — 当前状态交接" type="info" :closable="false" style="margin-bottom:16px" />
          <div class="markdown-body" v-html="renderedHandoff"></div>
        </div>
        <el-input v-if="showHandoffEdit" v-model="handoffRaw" type="textarea" :rows="20" placeholder="编写HANDOFF.md..." />
        <el-button v-if="showHandoffEdit" type="primary" @click="saveHandoff" :loading="saving" style="margin-top:12px">保存交接文档</el-button>
        <el-empty v-if="!handoffData && !showHandoffEdit" description="暂无交接文档" />
      </el-tab-pane>

      <!-- 操作日志 -->
      <el-tab-pane label="操作日志" name="oplog">
        <el-timeline v-if="operationLogs.length">
          <el-timeline-item v-for="log in operationLogs" :key="log.id" :timestamp="log.time" :type="log.level==='error'?'danger':log.level==='warn'?'warning':'primary'" placement="top">
            <el-card shadow="hover"><div class="log-header"><el-tag :type="log.level==='error'?'danger':log.level==='warn'?'warning':'success'" size="small">{{ log.level }}</el-tag><span>{{ log.action }}</span></div><p>{{ log.detail }}</p><small v-if="log.file">📁 {{ log.file }}</small></el-card>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="暂无操作日志" />
      </el-tab-pane>

      <!-- 代码变更 -->
      <el-tab-pane label="代码变更" name="changes">
        <el-table :data="codeChanges" stripe max-height="calc(100vh - 300px)" v-if="codeChanges.length">
          <el-table-column type="index" width="50" />
          <el-table-column prop="file" label="文件" min-width="220" show-overflow-tooltip />
          <el-table-column prop="change" label="变更内容" min-width="250" show-overflow-tooltip />
          <el-table-column prop="reason" label="原因" min-width="200" show-overflow-tooltip />
          <el-table-column prop="time" label="时间" width="170" sortable />
        </el-table>
        <el-empty v-else description="暂无代码变更记录" />
      </el-tab-pane>
    </el-tabs>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="showAdd" :title="editingId?'编辑记忆':'新增记忆'" width="560px">
      <el-form :model="form" label-width="70px">
        <el-form-item label="标题"><el-input v-model="form.title" placeholder="记忆标题" /></el-form-item>
        <el-form-item label="分类"><el-select v-model="form.category" style="width:100%"><el-option v-for="c in categories" :key="c" :label="c" :value="c" /></el-select></el-form-item>
        <el-form-item label="标签"><el-select-v2 v-model="form.tags" :options="tagOptions" multiple filterable allow-create placeholder="选择或输入标签" style="width:100%" /></el-form-item>
        <el-form-item label="内容"><el-input v-model="form.content" type="textarea" :rows="8" placeholder="记忆内容..." /></el-form-item>
      </el-form>
      <template #footer><el-button @click="showAdd=false">取消</el-button><el-button type="primary" @click="saveMem" :loading="saving">{{editingId?'保存':'添加'}}</el-button></template>
    </el-dialog>

    <!-- 查看详情 -->
    <el-dialog v-model="showView" title="记忆详情" width="560px">
      <div v-if="viewing">
        <p><strong>标题:</strong> {{ viewing.title }}</p>
        <p><strong>分类:</strong> <el-tag :type="catType(viewing.category)" size="small">{{ viewing.category }}</el-tag></p>
        <p><strong>标签:</strong> <el-tag v-for="t in viewing.tags" :key="t" size="small" style="margin-right:4px">{{ t }}</el-tag></p>
        <p><strong>内容:</strong></p><pre class="doc-content">{{ viewing.content }}</pre>
        <p><strong>时间:</strong> {{ viewing.created_at }}</p>
      </div>
      <template #footer><el-button @click="showView=false">关闭</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { agentApi } from '@/api/index'

const memories = ref([])
const loading = ref(false)

async function fetchMemories() {
  loading.value = true
  try {
    const { data: m } = await agentApi.get('/agent/friday/journal')
    const { data: h } = await agentApi.get('/agent/friday/handoff')
    memories.value = []
    if (Array.isArray(m?.journals)) {
      m.journals.forEach(function(j) { memories.value.push({ type:'日记', title:j.date||'', content:j.summary||'', time:j.date||'' }) })
    }
    if (h?.key_context) {
      h.key_context.forEach(function(k) { memories.value.push({ type:'上下文', title:k.category||'', content:k.value||'', time:'' }) })
    }
  } catch {
    memories.value = [{ type:'系统', title:'记忆中心', content:'连接后端获取记忆数据...', time:new Date().toISOString().slice(0,10) }]
  } finally { loading.value = false }
}

function refreshMemories() { fetchMemories() }
onMounted(function() { fetchMemories() })
</script>

<style scoped>
.memory-center { padding: 24px; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 18px; margin: 0 0 4px; }
.page-header p { color: var(--text-muted); font-size: 13px; margin: 0; }
.metric-card { background: var(--bg-card); border-radius: 8px; padding: 18px; border: 1px solid var(--border-color); }
.metric-label { font-size: 12px; color: var(--text-muted); margin-bottom: 6px; }
.metric-value { font-size: 28px; font-weight: 700; }
.tab-toolbar { display: flex; gap: 12px; margin-bottom: 16px; align-items: center; }
.doc-viewer { background: var(--bg-card); border-radius: 8px; padding: 20px; }
.doc-content { white-space: pre-wrap; font-size: 13px; color: var(--text-secondary); line-height: 1.8; max-height: 50vh; overflow-y: auto; background: rgba(0,0,0,0.2); padding: 16px; border-radius: 6px; }
.log-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.markdown-body { line-height: 1.8; }
</style>
