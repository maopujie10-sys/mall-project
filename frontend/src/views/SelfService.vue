<template>
  <div class="self-service">
    <h2>鑷姪杩愮淮</h2>
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
            {{ runningId === rb.id ? '鎵ц涓?..' : '涓€閿墽琛' }}
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <!-- 瀹㈡湇璁㈠崟鏌ヨ -->
    <el-card shadow="never" style="margin-top:16px">
      <template #header>瀹㈡湇璁㈠崟鏌ヨ</template>
      <el-input v-model="queryUserId" placeholder="鐢ㄦ埛ID" style="width:200px;margin-right:8px" />
      <el-input v-model="queryOrderId" placeholder="璁㈠崟ID" style="width:200px;margin-right:8px" />
      <el-button type="primary" @click="runCustomerQuery" :loading="queryLoading">鏌ヨ</el-button>
    </el-card>

    <!-- 鎵ц缁撴灉 -->
    <el-card v-if="report" shadow="never" style="margin-top:16px">
      <template #header>
        <span>鎵ц鎶ュ憡</span>
        <el-tag :type="report.all_passed ? 'success' : 'danger'" size="small" style="margin-left:8px">
          {{ report.all_passed ? '鍏ㄩ儴閫氳繃' : `${report.failed} 椤瑰紓甯竊 }}
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
      <el-alert v-if="!report.all_passed" title="妫€娴嬪埌寮傚父" :description="report.summary" type="warning" show-icon style="margin-top:12px" />
      <el-alert v-else title="涓€鍒囨甯' :description="report.summary" type="success" show-icon style="margin-top:12px" />
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
  } catch { ElMessage.error('鑾峰彇鍦烘櫙鍒楄〃澶辫触') }
}

async function run(id) {
  runningId.value = id
  report.value = null
  try {
    report.value = await agentApi.post(`/self-service/run/${id}`)
    if (report.value.all_passed) {
      ElMessage.success('?) } else { ElMessage.warning(`${report.value.failed} ) } } catch { ElMessage.error('鎵ц澶辫触') }
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
  } catch { ElMessage.error('鏌ヨ澶辫触') }
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
