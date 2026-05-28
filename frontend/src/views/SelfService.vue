<template>
  <div class="self-service">
    <h2>閼奉亜濮潻鎰樊</h2>
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
            {{ runningId === rb.id ? '閹笛嗩攽娑?..' : '娑撯偓闁款喗澧界悰? }}
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <!-- 鐎广垺婀囩拋銏犲礋閺屻儴顕?-->
    <el-card shadow="never" style="margin-top:16px">
      <template #header>鐎广垺婀囩拋銏犲礋閺屻儴顕?/template>
      <el-input v-model="queryUserId" placeholder="閻劍鍩汭D" style="width:200px;margin-right:8px" />
      <el-input v-model="queryOrderId" placeholder="鐠併垹宕烮D" style="width:200px;margin-right:8px" />
      <el-button type="primary" @click="runCustomerQuery" :loading="queryLoading">閺屻儴顕?/el-button>
    </el-card>

    <!-- 閹笛嗩攽缂佹挻鐏?-->
    <el-card v-if="report" shadow="never" style="margin-top:16px">
      <template #header>
        <span>閹笛嗩攽閹躲儱鎲?/span>
        <el-tag :type="report.all_passed ? 'success' : 'danger'" size="small" style="margin-left:8px">
          {{ report.all_passed ? '閸忋劑鍎撮柅姘崇箖' : `${report.failed} 妞ょ懓绱撶敮绔?}}
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
      <el-alert v-if="!report.all_passed" title="濡偓濞村鍩屽鍌氱埗" :description="report.summary" type="warning" show-icon style="margin-top:12px" />
      <el-alert v-else title="娑撯偓閸掑洦顒滅敮? :description="report.summary" type="success" show-icon style="margin-top:12px" />
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
  } catch { ElMessage.error('閼惧嘲褰囬崷鐑樻珯閸掓銆冩径杈Е') }
}

async function run(id) {
  runningId.value = id
  report.value = null
  try {
    report.value = await agentApi.post(`/self-service/run/${id}`)
    if (report.value.all_passed) {
      ElMessage.success('閹碘偓閺堝顥呴弻銉┾偓姘崇箖 閴?)
    } else {
      ElMessage.warning(`${report.value.failed} 妞ょ懓绱撶敮闈╃礉鐠囬攱鐓￠惇瀣Г閸涘グ)
    }
  } catch { ElMessage.error('閹笛嗩攽婢惰精瑙?) }
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
  } catch { ElMessage.error('閺屻儴顕楁径杈Е') }
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
</style>
