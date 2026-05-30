<template>
  <div class="page-container memory-center">
    <div class="page-header">
      <h2>璁板繂涓績</h2>
      <p>闀挎湡璁板繂 路 HANDOFF浜ゆ帴 路 鎿嶄綔鏃ュ織 路 浠ｇ爜鍙樻洿鍘嗗彶</p>
    </div>

    <!-- 缁熻 -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6"><div class="metric-card"><div class="metric-label">璁板繂鎬绘暟</div><div class="metric-value">{{ memories.length }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">鐭ヨ瘑鍥捐氨</div><div class="metric-value" style="color:#667eea">{{ graphNodes }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">浜ゆ帴鏂囨。</div><div class="metric-value" style="color:#52c41a">{{ handoffCount }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">鎿嶄綔鏃ュ織</div><div class="metric-value" style="color:#faad14">{{ operationLogs.length }}</div></div></el-col>
    </el-row>

    <el-tabs v-model="activeTab" @tab-change="onTabChange">
      <!-- 鍏ㄩ儴璁板繂 -->
      <el-tab-pane label="鍏ㄩ儴璁板繂" name="all">
        <div class="tab-toolbar">
          <el-input v-model="searchQuery" placeholder="鎼滅储璁板繂..." prefix-icon="Search" style="width:280px" clearable @clear="loadMemories" @keyup.enter="searchMem" />
          <el-select v-model="filterCategory" placeholder="鍒嗙被绛涢€? style="width:140px" clearable @change="loadMemories">
            <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
          </el-select>
          <el-button type="primary" @click="showAdd = true">鏂板璁板繂</el-button>
        </div>
        <el-table :data="filteredMemories" stripe max-height="calc(100vh - 380px)">
          <el-table-column type="index" width="50" />
          <el-table-column prop="title" label="鏍囬" min-width="180" show-overflow-tooltip />
          <el-table-column prop="category" label="鍒嗙被" width="110">
            <template #default="{row}"><el-tag :type="catType(row.category)" size="small">{{ row.category }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="content" label="鍐呭" min-width="280" show-overflow-tooltip />
          <el-table-column prop="tags" label="鏍囩" width="160"><template #default="{row}"><el-tag v-for="t in row.tags" :key="t" size="small" style="margin-right:4px">{{ t }}</el-tag></template></el-table-column>
          <el-table-column prop="created_at" label="鏃堕棿" width="170" sortable />
          <el-table-column label="鎿嶄綔" width="160" fixed="right">
            <template #default="{row}">
              <el-button link type="primary" size="small" @click="viewMemory(row)">鏌ョ湅</el-button>
              <el-button link type="warning" size="small" @click="editMemory(row)">缂栬緫</el-button>
              <el-button link type="danger" size="small" @click="removeMemory(row.id)">鍒犻櫎</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- HANDOFF 浜ゆ帴鏂囨。 -->
      <el-tab-pane label="浜ゆ帴鏂囨。" name="handoff">
        <div class="tab-toolbar"><el-button type="primary" @click="showHandoffEdit=!showHandoffEdit">{{showHandoffEdit?'棰勮':'缂栬緫'}}</el-button></div>
        <div v-if="!showHandoffEdit && handoffData" class="doc-viewer">
          <el-alert title="HANDOFF.md 鈥?褰撳墠鐘舵€佷氦鎺? type="info" :closable="false" style="margin-bottom:16px" />
          <div class="markdown-body" v-html="renderedHandoff"></div>
        </div>
        <el-input v-if="showHandoffEdit" v-model="handoffRaw" type="textarea" :rows="20" placeholder="缂栧啓HANDOFF.md..." />
        <el-button v-if="showHandoffEdit" type="primary" @click="saveHandoff" :loading="saving" style="margin-top:12px">淇濆瓨浜ゆ帴鏂囨。</el-button>
        <el-empty v-if="!handoffData && !showHandoffEdit" description="鏆傛棤浜ゆ帴鏂囨。" />
      </el-tab-pane>

      <!-- 鎿嶄綔鏃ュ織 -->
      <el-tab-pane label="鎿嶄綔鏃ュ織" name="oplog">
        <el-timeline v-if="operationLogs.length">
          <el-timeline-item v-for="log in operationLogs" :key="log.id" :timestamp="log.time" :type="log.level==='error'?'danger':log.level==='warn'?'warning':'primary'" placement="top">
            <el-card shadow="hover"><div class="log-header"><el-tag :type="log.level==='error'?'danger':log.level==='warn'?'warning':'success'" size="small">{{ log.level }}</el-tag><span>{{ log.action }}</span></div><p>{{ log.detail }}</p><small v-if="log.file">馃搧 {{ log.file }}</small></el-card>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="鏆傛棤鎿嶄綔鏃ュ織" />
      </el-tab-pane>

      <!-- 浠ｇ爜鍙樻洿 -->
      <el-tab-pane label="浠ｇ爜鍙樻洿" name="changes">
        <el-table :data="codeChanges" stripe max-height="calc(100vh - 300px)" v-if="codeChanges.length">
          <el-table-column type="index" width="50" />
          <el-table-column prop="file" label="鏂囦欢" min-width="220" show-overflow-tooltip />
          <el-table-column prop="change" label="鍙樻洿鍐呭" min-width="250" show-overflow-tooltip />
          <el-table-column prop="reason" label="鍘熷洜" min-width="200" show-overflow-tooltip />
          <el-table-column prop="time" label="鏃堕棿" width="170" sortable />
        </el-table>
        <el-empty v-else description="鏆傛棤浠ｇ爜鍙樻洿璁板綍" />
      </el-tab-pane>
    </el-tabs>

    <!-- 鏂板/缂栬緫瀵硅瘽妗?-->
    <el-dialog v-model="showAdd" :title="editingId?'缂栬緫璁板繂':'鏂板璁板繂'" width="560px">
      <el-form :model="form" label-width="70px">
        <el-form-item label="鏍囬"><el-input v-model="form.title" placeholder="璁板繂鏍囬" /></el-form-item>
        <el-form-item label="鍒嗙被"><el-select v-model="form.category" style="width:100%"><el-option v-for="c in categories" :key="c" :label="c" :value="c" /></el-select></el-form-item>
        <el-form-item label="鏍囩"><el-select-v2 v-model="form.tags" :options="tagOptions" multiple filterable allow-create placeholder="閫夋嫨鎴栬緭鍏ユ爣绛? style="width:100%" /></el-form-item>
        <el-form-item label="鍐呭"><el-input v-model="form.content" type="textarea" :rows="8" placeholder="璁板繂鍐呭..." /></el-form-item>
      </el-form>
      <template #footer><el-button @click="showAdd=false">鍙栨秷</el-button><el-button type="primary" @click="saveMem" :loading="saving">{{editingId?'淇濆瓨':'娣诲姞'}}</el-button></template>
    </el-dialog>

    <!-- 鏌ョ湅璇︽儏 -->
    <el-dialog v-model="showView" title="璁板繂璇︽儏" width="560px">
      <div v-if="viewing">
        <p><strong>鏍囬:</strong> {{ viewing.title }}</p>
        <p><strong>鍒嗙被:</strong> <el-tag :type="catType(viewing.category)" size="small">{{ viewing.category }}</el-tag></p>
        <p><strong>鏍囩:</strong> <el-tag v-for="t in viewing.tags" :key="t" size="small" style="margin-right:4px">{{ t }}</el-tag></p>
        <p><strong>鍐呭:</strong></p><pre class="doc-content">{{ viewing.content }}</pre>
        <p><strong>鏃堕棿:</strong> {{ viewing.created_at }}</p>
      </div>
      <template #footer><el-button @click="showView=false">鍏抽棴</el-button></template>
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
      m.journals.forEach(function(j) { memories.value.push({ type:'鏃ヨ', title:j.date||'', content:j.summary||'', time:j.date||'' }) })
    }
    if (h?.key_context) {
      h.key_context.forEach(function(k) { memories.value.push({ type:'涓婁笅鏂?, title:k.category||'', content:k.value||'', time:'' }) })
    }
  } catch {
    memories.value = [{ type:'绯荤粺', title:'璁板繂涓績', content:'杩炴帴鍚庣鑾峰彇璁板繂鏁版嵁...', time:new Date().toISOString().slice(0,10) }]
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
.metric-card { background: rgba(22,33,62,0.7); border-radius: 8px; padding: 18px; border: 1px solid var(--border-color); }
.metric-label { font-size: 12px; color: var(--text-muted); margin-bottom: 6px; }
.metric-value { font-size: 28px; font-weight: 700; }
.tab-toolbar { display: flex; gap: 12px; margin-bottom: 16px; align-items: center; }
.doc-viewer { background: rgba(22,33,62,0.7); border-radius: 8px; padding: 20px; }
.doc-content { white-space: pre-wrap; font-size: 13px; color: var(--text-secondary); line-height: 1.8; max-height: 50vh; overflow-y: auto; background: rgba(0,0,0,0.2); padding: 16px; border-radius: 6px; }
.log-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.markdown-body { line-height: 1.8; }
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>
