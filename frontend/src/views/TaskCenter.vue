<template>
  <div class="page-container task-center">
    <div class="page-header"><h2>鑷姩浠诲姟</h2><p>Cron瀹氭椂 路 浜嬩欢瑙﹀彂 路 澶辫触閲嶈瘯 路 鎵ц鏃ュ織</p></div>

    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6"><div class="metric-card"><div class="metric-label">浠诲姟鎬绘暟</div><div class="metric-value">{{ tasks.length }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">杩愯涓?/div><div class="metric-value" style="color:#52c41a">{{ runningCount }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">浠婃棩鎵ц</div><div class="metric-value">{{ todayExecs }}</div></div></el-col>
      <el-col :span="6"><div class="metric-card"><div class="metric-label">鎴愬姛鐜?/div><div class="metric-value" style="color:#667eea">{{ successRate }}%</div></div></el-col>
    </el-row>

    <div class="tab-toolbar">
      <el-select v-model="filterStatus" placeholder="鐘舵€佺瓫閫? style="width:140px" clearable>
        <el-option label="鍏ㄩ儴" value="" /><el-option label="鍚敤" value="enabled" /><el-option label="绂佺敤" value="disabled" /><el-option label="杩愯涓? value="running" />
      </el-select>
      <el-button type="primary" @click="showAdd=true">鍒涘缓浠诲姟</el-button>
    </div>

    <el-table :data="filteredTasks" stripe>
      <el-table-column type="index" width="50" />
      <el-table-column prop="name" label="浠诲姟鍚嶇О" min-width="160" show-overflow-tooltip />
      <el-table-column prop="type" label="绫诲瀷" width="100"><template #default="{row}"><el-tag size="small">{{ row.type }}</el-tag></template></el-table-column>
      <el-table-column prop="cron" label="Cron琛ㄨ揪寮? width="150" show-overflow-tooltip />
      <el-table-column label="涓嬫鎵ц" width="170"><template #default="{row}"><span class="mono">{{ row.nextRun || '-' }}</span></template></el-table-column>
      <el-table-column label="鐘舵€? width="100">
        <template #default="{row}">
          <el-switch v-if="row.status!=='running'" v-model="enabledProxy(row)" size="small" @change="toggleTask(row)" />
          <el-tag v-else type="warning" size="small">杩愯涓?/el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="lastResult" label="涓婃缁撴灉" width="100"><template #default="{row}"><el-tag :type="row.lastResult==='鎴愬姛'?'success':row.lastResult==='澶辫触'?'danger':'info'" size="small">{{ row.lastResult || '-' }}</el-tag></template></el-table-column>
      <el-table-column label="鎿嶄綔" width="220" fixed="right">
        <template #default="{row}">
          <el-button link type="primary" size="small" @click="runNow(row)">绔嬪嵆鎵ц</el-button>
          <el-button link type="primary" size="small" @click="viewLogs(row)">鏃ュ織</el-button>
          <el-button link type="primary" size="small" @click="editTask(row)">缂栬緫</el-button>
          <el-button link type="danger" size="small" @click="removeTask(row)">鍒犻櫎</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showAdd" :title="editingId?'缂栬緫浠诲姟':'鍒涘缓浠诲姟'" width="560px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="浠诲姟鍚嶇О"><el-input v-model="form.name" placeholder="濡傦細姣忔棩鏁版嵁搴撳浠? /></el-form-item>
        <el-form-item label="浠诲姟绫诲瀷"><el-select v-model="form.type" style="width:100%"><el-option v-for="t in taskTypes" :key="t" :label="t" :value="t" /></el-select></el-form-item>
        <el-form-item label="Cron琛ㄨ揪寮?><el-input v-model="form.cron" placeholder="0 3 * * * (姣忓ぉ鍑屾櫒3鐐?" /><div style="font-size:11px;color:var(--text-muted);margin-top:4px">鍒?鏃?鏃?鏈?鍛?/div></el-form-item>
        <el-form-item label="鎵ц鍛戒护"><el-input v-model="form.command" type="textarea" :rows="3" placeholder="瑕佹墽琛岀殑鍛戒护鎴栬剼鏈? /></el-form-item>
        <el-form-item label="澶辫触閲嶈瘯"><el-input-number v-model="form.retries" :min="0" :max="10" /> <span style="margin-left:4px">娆?/span></el-form-item>
        <el-form-item label="瓒呮椂鏃堕棿"><el-input-number v-model="form.timeout" :min="0" :max="3600" :step="60" /> <span style="margin-left:4px">绉?/span></el-form-item>
      </el-form>
      <template #footer><el-button @click="showAdd=false">鍙栨秷</el-button><el-button type="primary" @click="saveTask" :loading="saving">{{editingId?'淇濆瓨':'鍒涘缓'}}</el-button></template>
    </el-dialog>

    <el-dialog v-model="showLogs" title="鎵ц鏃ュ織" width="700px">
      <el-timeline v-if="currentLogs.length">
        <el-timeline-item v-for="log in currentLogs" :key="log.id" :timestamp="log.time" :type="log.ok?'success':'danger'" placement="top">
          <el-card shadow="hover"><p><strong>{{ log.taskName }}</strong></p><p>{{ log.output }}</p><small>鑰楁椂: {{ log.duration }}</small></el-card>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="鏆傛棤鎵ц鏃ュ織" />
      <template #footer><el-button @click="showLogs=false">鍏抽棴</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { agentApi } from '@/api/index'
const tasks = ref([]); const loading = ref(false)
async function fetchTasks() { loading.value = true; try { const { data } = await agentApi.get('/tasks/queue'); tasks.value = data.tasks || [] } catch {} finally { loading.value = false } }
function cancelTask(id) { ElMessage.success('浠诲姟宸插彇娑?) }
onMounted(function() { fetchTasks() })
</script>

<style scoped>
.task-center { padding: 24px; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 18px; margin: 0 0 4px; }
.page-header p { color: var(--text-muted); font-size: 13px; margin: 0; }
.metric-card { background: var(--bg-card); border-radius: 8px; padding: 18px; border: 1px solid var(--border-color); }
.metric-label { font-size: 12px; color: var(--text-muted); margin-bottom: 6px; }
.metric-value { font-size: 28px; font-weight: 700; }
.tab-toolbar { display: flex; gap: 12px; margin-bottom: 16px; align-items: center; }
.mono { font-family: monospace; font-size: 12px; }
</style>