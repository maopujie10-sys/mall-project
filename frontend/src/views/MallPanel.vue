<template>
  <div class="mall-panel">
    <h2>鍟嗗煄鐘舵€佺洃鎺?/h2>

    <!-- KPI -->
    <el-row :gutter="16" class="kpi-row">
      <el-col :span="6" v-for="k in kpis" :key="k.label">
        <div class="kpi-card" :class="k.color">
          <div class="kpi-num">{{ k.value }}</div>
          <div class="kpi-label">{{ k.label }}</div>
        </div>
      </el-col>
    </el-row>

    <!-- 绔偣鐘舵€?-->
    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <span>鎺ュ彛杩為€氭€?/span>
            <el-button size="small" @click="scanStructure" :loading="scanning" style="margin-left:12px">鎵弿</el-button>
          </template>
          <el-table :data="endpoints" stripe size="small" v-if="endpoints.length">
            <el-table-column prop="name" label="绔偣" width="100" />
            <el-table-column label="鐘舵€? width="80">
              <template #default="{row}">
                <el-tag :type="row.ok ? 'success' : 'danger'" size="small">{{ row.ok ? '姝ｅ父' : '寮傚父' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="code" label="鐘舵€佺爜" width="80" />
            <el-table-column prop="error" label="閿欒" show-overflow-tooltip />
          </el-table>
          <el-empty v-else description="鐐瑰嚮鎵弿妫€娴嬪晢鍩庣姸鎬? :image-size="60" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>鍟嗗搧 / 璁㈠崟姒傝</template>
          <el-button size="small" @click="checkProducts" :loading="prodLoading">妫€娴嬪晢鍝?/el-button>
          <el-button size="small" @click="checkOrders" :loading="ordLoading" style="margin-left:8px">妫€娴嬭鍗?/el-button>
          <div v-if="productInfo" style="margin-top:12px">
            <p>鍟嗗搧鎬绘暟: <strong>{{ productInfo.total || 'N/A' }}</strong></p>
            <p>鐘舵€? <el-tag :type="productInfo.ok ? 'success' : 'danger'" size="small">{{ productInfo.ok ? '姝ｅ父' : '寮傚父' }}</el-tag></p>
          </div>
          <div v-if="orderInfo" style="margin-top:8px">
            <p>璁㈠崟鎬绘暟: <strong>{{ orderInfo.total || 'N/A' }}</strong></p>
            <p>鐘舵€? <el-tag :type="orderInfo.ok ? 'success' : 'danger'" size="small">{{ orderInfo.ok ? '姝ｅ父' : '寮傚父' }}</el-tag></p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 鎵弿鍘嗗彶 -->
    <el-card shadow="never" style="margin-top:16px">
      <template #header>鎵弿鍘嗗彶</template>
      <el-timeline v-if="history.length">
        <el-timeline-item v-for="h in history" :key="h.time" :timestamp="h.time">
          {{ h.summary || `${h.total} 涓鐐癸紝${h.passed} 姝ｅ父` }}
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="鏆傛棤鎵弿璁板綍" :image-size="50" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { agentApi } from '@/api'
import { ElMessage } from 'element-plus'

const kpis = ref([
  { label: '鎺ュ彛鎬绘暟', value: 0, color: 'blue' },
  { label: '姝ｅ父', value: 0, color: 'green' },
  { label: '寮傚父', value: 0, color: 'red' },
  { label: '鍋ュ悍鐜?, value: '0%', color: 'blue' },
])
const endpoints = ref([])
const history = ref([])
const scanning = ref(false)
const prodLoading = ref(false)
const ordLoading = ref(false)
const productInfo = ref(null)
const orderInfo = ref(null)

async function scanStructure() {
  scanning.value = true
  try {
    const r = await agentApi.post('/mall/scan/structure')
    endpoints.value = Object.entries(r.status || {}).map(([k, v]) => ({ name: k, ...v }))
    const ok = endpoints.value.filter(e => e.ok).length
    const total = endpoints.value.length
    kpis.value = [
      { label: '鎺ュ彛鎬绘暟', value: total, color: 'blue' },
      { label: '姝ｅ父', value: ok, color: 'green' },
      { label: '寮傚父', value: total - ok, color: 'red' },
      { label: '鍋ュ悍鐜?, value: total ? `${Math.round(ok/total*100)}%` : '0%', color: 'blue' },
    ]
    ElMessage.success(`鎵弿瀹屾垚: ${ok}/${total} 姝ｅ父`)
  } catch { ElMessage.error('鎵弿澶辫触锛岃纭鍟嗗煄鏈嶅姟鏄惁杩愯') }
  scanning.value = false
}
async function checkProducts() {
  prodLoading.value = true
  try { productInfo.value = await agentApi.post('/mall/scan/products') } catch { ElMessage.error('妫€娴嬪け璐?) }
  prodLoading.value = false
}
async function checkOrders() {
  ordLoading.value = true
  try { orderInfo.value = await agentApi.post('/mall/scan/orders') } catch { ElMessage.error('妫€娴嬪け璐?) }
  ordLoading.value = false
}
onMounted(scanStructure)
</script>

<style scoped>
.mall-panel { padding: 24px; }
h2 { margin-bottom: 16px; font-size: 18px; }
.kpi-row { margin-bottom: 0; }
.kpi-card { padding: 16px; border-radius: 8px; color: #fff; text-align: center; }
.kpi-card.blue { background: linear-gradient(135deg, #409eff, #337ecc); }
.kpi-card.green { background: linear-gradient(135deg, #67c23a, #529b2e); }
.kpi-card.red { background: linear-gradient(135deg, #f56c6c, #c45656); }
.kpi-num { font-size: 28px; font-weight: 700; }
.kpi-label { font-size: 13px; opacity: 0.9; margin-top: 4px; }
</style>
