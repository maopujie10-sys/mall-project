<template>
  <div class="page-container">
    <div class="page-header">
      <h2>瀹℃壒涓績</h2>
      <p>寰呭鎵逛换鍔?路 椋庨櫓鍒嗙骇 路 鍙樻洿棰勮 路 瀹℃壒鍘嗗彶</p>
    </div>

    <el-alert v-if="error" :title="error" type="error" show-icon closable @close="error=null" style="margin-bottom:16px" />

    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">寰呭鎵?/div>
          <div class="metric-value" style="color: var(--color-warning);">{{ loading ? '...' : pendingTasks.length }}</div>
          <div class="metric-sub">闇€瑕佷汉宸ョ‘璁?/div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">鍘嗗彶璁板綍</div>
          <div class="metric-value">{{ loading ? '...' : historyTasks.length }}</div>
          <div class="metric-sub">宸查€氳繃 {{ approvedCount }} 路 宸叉嫆缁?{{ rejectedCount }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">鎷掔粷鐜?/div>
          <div class="metric-value" style="color: var(--color-danger);">0</div>
          <div class="metric-sub">鏈€杩?30 澶?/div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">瀹℃壒鏁堢巼</div>
          <div class="metric-value">--</div>
          <div class="metric-sub">骞冲潎 24 灏忔椂鍐?/div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="24">
        <div v-if="pendingTasks.length === 0" style="padding: 60px 0;">
          <el-empty description="鏆傛棤寰呭鎵逛换鍔? />
        </div>
        <div v-for="task in pendingTasks" :key="task.id" class="approval-card" :class="'risk-' + task.risk.toLowerCase()">
          <div class="card-body">
            <div class="card-main">
              <div class="card-header">
                <div class="card-title-row">
                  <span class="risk-badge" :class="task.risk.toLowerCase()">{{ task.risk }}</span>
                  <h4>{{ task.name }}</h4>
                </div>
                <span class="card-time">{{ task.time }}</span>
              </div>
              <p class="card-desc">{{ task.description }}</p>
              <div class="card-preview" v-if="task.preview">
                <div class="preview-label">鍙樻洿棰勮</div>
                <div class="code-block" style="font-size: 11px; max-height: 100px;">{{ task.preview }}</div>
              </div>
              <div class="card-meta">
                <span>鍒涘缓鑰? {{ task.creator }}</span>
                <span>褰卞搷鑼冨洿: {{ task.scope }}</span>
                <span>棰勮鑰楁椂: {{ task.estimated }}</span>
              </div>
            </div>
            <div class="card-actions">
              <el-button type="success" @click="approveTask(task)" :loading="task.approving">
                <el-icon><Check /></el-icon> 鎵瑰噯
              </el-button>
              <el-button type="danger" @click="rejectTask(task)" :loading="task.rejecting">
                <el-icon><Close /></el-icon> 鎷掔粷
              </el-button>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-card shadow="never" style="margin-top: 20px;">
      <template #header><span style="font-weight: 600;">瀹℃壒鍘嗗彶</span></template>
      <el-table :data="historyTasks" style="width: 100%;" size="small" stripe>
        <el-table-column prop="name" label="浠诲姟鍚嶇О" min-width="160" />
        <el-table-column prop="risk" label="椋庨櫓绛夌骇" width="90">
          <template #default="{ row }"><span class="risk-badge" :class="row.risk.toLowerCase()">{{ row.risk }}</span></template>
        </el-table-column>
        <el-table-column prop="creator" label="鍒涘缓鑰? width="100" />
        <el-table-column prop="result" label="缁撴灉" width="90">
          <template #default="{ row }">
            <el-tag :type="row.result === '宸查€氳繃' ? 'success' : 'danger'" size="small" effect="plain">{{ row.result }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reviewer" label="瀹℃壒浜? width="90" />
        <el-table-column prop="time" label="鏃堕棿" width="100" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useSystemStore } from '@/stores/system'

const systemStore = useSystemStore()

const loading = ref(true)
const error = ref(null)

const pendingTasks = reactive([])
const historyTasks = reactive([])

const approvedCount = computed(() => historyTasks.filter((t) => t.result === '宸查€氳繃').length)
const rejectedCount = computed(() => historyTasks.filter((t) => t.result === '宸叉嫆缁?).length)

async function fetchApprovals() {
  try {
    const [pending, history] = await Promise.all([
      systemStore.fetchPendingApprovals(),
      systemStore.fetchApprovalHistory(),
    ])

    if (Array.isArray(pending)) {
      pendingTasks.splice(0, pendingTasks.length, ...pending.map((t) => ({
        id: t.id || t.taskId || Date.now(),
        risk: t.risk || 'L1',
        name: t.name || t.task || '鏈懡鍚嶄换鍔?,
        time: t.time || '-',
        description: t.description || '',
        preview: t.preview || '',
        creator: t.creator || 'AI Agent',
        scope: t.scope || '',
        estimated: t.estimated || '',
        approving: false,
        rejecting: false,
      })))
    }

    if (Array.isArray(history)) {
      historyTasks.splice(0, historyTasks.length, ...history.map((t) => ({
        name: t.name || t.task || '',
        risk: t.risk || 'L1',
        creator: t.creator || '-',
        result: t.result || t.decision || '-',
        reviewer: t.reviewer || 'Admin',
        time: t.time || '-',
      })))
    }

    error.value = null
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const approveTask = async (task) => {
  try {
    await ElMessageBox.confirm(`纭鎵瑰噯 "${task.name}"锛熸鎿嶄綔灏嗘墽琛屽搴斿彉鏇淬€俙, '瀹℃壒纭', {
      confirmButtonText: '纭鎵瑰噯', cancelButtonText: '鍙栨秷', type: 'warning',
    })
    task.approving = true
    const success = await systemStore.handleApproval(task.id, true)
    if (success) {
      const idx = pendingTasks.indexOf(task)
      if (idx > -1) {
        pendingTasks.splice(idx, 1)
        historyTasks.unshift({
          name: task.name, risk: task.risk, creator: task.creator,
          result: '宸查€氳繃', reviewer: 'Admin', time: new Date().toTimeString().slice(0, 5),
        })
      }
      ElMessage.success(`宸叉壒鍑?"${task.name}"`)
    } else {
      task.approving = false
    }
  } catch {}
}

const rejectTask = async (task) => {
  try {
    await ElMessageBox.confirm(`纭鎷掔粷 "${task.name}"锛焋, '鎷掔粷纭', {
      confirmButtonText: '纭鎷掔粷', cancelButtonText: '鍙栨秷', type: 'warning',
    })
    task.rejecting = true
    const success = await systemStore.handleApproval(task.id, false)
    if (success) {
      const idx = pendingTasks.indexOf(task)
      if (idx > -1) {
        pendingTasks.splice(idx, 1)
        historyTasks.unshift({
          name: task.name, risk: task.risk, creator: task.creator,
          result: '宸叉嫆缁?, reviewer: 'Admin', time: new Date().toTimeString().slice(0, 5),
        })
      }
      ElMessage.warning(`宸叉嫆缁?"${task.name}"`)
    } else {
      task.rejecting = false
    }
  } catch {}
}

onMounted(() => { fetchApprovals() })
</script>

<style scoped>
.approval-card { margin-bottom: 16px; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; border-left: 4px solid var(--border-color); overflow: hidden; transition: all 0.2s; }
.approval-card:hover { box-shadow: var(--shadow-elevated); }
.approval-card.risk-l3 { border-left-color: var(--color-warning); }
.approval-card.risk-l4 { border-left-color: var(--color-danger); }
.card-body { display: flex; padding: 20px 24px; gap: 24px; }
.card-main { flex: 1; min-width: 0; }
.card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }
.card-title-row { display: flex; align-items: center; gap: 10px; }
.card-title-row h4 { font-size: 15px; font-weight: 600; color: var(--text-primary); }
.card-time { font-size: 12px; color: var(--text-muted); flex-shrink: 0; margin-left: 12px; }
.card-desc { font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 12px; }
.card-preview { margin-bottom: 12px; }
.preview-label { font-size: 12px; color: var(--text-muted); margin-bottom: 4px; }
.card-meta { display: flex; gap: 24px; font-size: 12px; color: var(--text-muted); }
.card-actions { display: flex; flex-direction: column; gap: 8px; justify-content: center; flex-shrink: 0; min-width: 110px; }
</style>