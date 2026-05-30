<template>
  <div class="self-service">
    -
    <el-row :gutter="16">
      <el-col :span="8" v-for="rb in runbooks" :key="rb.id">
        <el-card shadow="never" class="rb-card" :class="{ running: runningId === rb.id }">
          <template #header>
            <div class="rb-header">
              <span>{{ rb.name }}</span>
              <el-tag :type="rb.risk === 'L1' ? 'success' : 'warning'" size="small">{{ rb.risk }}</el-tag>
            </div>
          </template>
          <el-button type="primary" @click="run(rb.id)" :loading="runningId === rb.id" :disabled="runningId">
            {{ runningId === rb.id ? '执行中...' : '开始诊断' }}
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    
    <el-card shadow="never" style="margin-top:16px">
      <template #header></template>
      <el-input v-model="queryUserId" placeholder="ID" style="width:200px;margin-right:8px" />
      <el-input v-model="queryOrderId" placeholder="ID" style="width:200px;margin-right:8px" />
      <el-button type="primary" @click="runCustomerQuery" :loading="queryLoading"></el-button>
    </el-card>

    
    <el-card v-if="report" shadow="never" style="margin-top:16px">
      <template #header>
        -
        <el-tag :type="report.all_passed ? 'success' : 'danger'" size="small" style="margin-left:8px">
          {{ report.all_passed ? '' : `${report.failed} 个失败`}}
        </el-tag>
      </template>
      <el-timeline>
        <el-timeline-item v-for="s in report.steps" :key="s.name"
          :timestamp="s.time"
          :type="s.ok ? 'success' : 'danger'"
          :color="s.ok ? '#67c23a' : '#f56c6c'">
          <p><strong>{{ s.name }}</strong></p>
          <p>{{ s.detail }}</p>
          <p v-if="s.evidence" style="font-size:12px;color:#999">{{ s.evidence }}</p>
        </el-timeline-item>
      </el-timeline>
      <el-alert v-if="!report.all_passed" :title="$t('selfService.title')" :description="report.summary" type="warning" show-icon style="margin-top:12px" />
      <el-alert v-else title="状态" :description="report.summary" type="success" show-icon style="margin-top:12px" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { agentApi } from '@/api'
import { ElMessage } from 'element-plus'

const runbooks = ref([])
const runningId = ref('')
const queryUserId = ref('')
const queryOrderId = ref('')
const queryLoading = ref(false)
const report = ref(null)

async function fetchRunbooks() {
  try {
    const r = await agentApi.get('/self-service/runbooks')
    runbooks.value = r.runbooks || []
  } catch { ElMessage.error('Error') }
}

async function run(id) {
  runningId.value = id
  report.value = null
  try {
    report.value = await agentApi.post(`/self-service/run/${id}`)
    if (report.value.all_passed) {
      ElMessage.success('所有检查通过')
    } else {
      ElMessage.warning(`${report.value.failed} 个失败`)
    }
  } catch { ElMessage.error('Error') }
  runningId.value = ''
}

async function runCustomerQuery() {
  queryLoading.value = true
  report.value = null
  try {
    const params = {}
    if (queryUserId.value) params.user_id = queryUserId.value
    if (queryOrderId.value) params.order_id = queryOrderId.value
    report.value = await agentApi.post('/self-service/run/customer_order', params)
  } catch { ElMessage.error('Error') }
  queryLoading.value = false
}

onMounted(fetchRunbooks)
</script>

<style scoped>
.self-service { padding: 24px; }
h2 { margin-bottom: 16px; font-size: 18px; }
.rb-card { margin-bottom: 16px; cursor: pointer; transition: all 0.2s; }
.rb-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.rb-card.running { opacity: 0.7; }
.rb-header { display: flex; justify-content: space-between; align-items: center; }
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>
