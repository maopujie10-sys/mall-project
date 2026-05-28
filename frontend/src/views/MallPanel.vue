锘?template>
  <div class="mall-admin-panel">
    <div class="page-header">
      <h2>鍟嗗煄鎬诲悗鍙扮鐞?/h2>
      <div class="header-actions">
        <el-button size="small" @click="scanAll" :loading="scanning">涓€閿壂鎻?/el-button>
        <el-button size="small" type="primary" @click="aiBrainScan" :loading="brainLoading">AI澶ц剳鍒嗘瀽</el-button>
      </div>
    </div>

    <!-- KPI 鎸囨爣鍗?-->
    <el-row :gutter="12" class="kpi-row">
      <el-col :span="4" v-for="k in kpis" :key="k.label">
        <div class="kpi-card" :style="{ background: k.bg }">
          <div class="kpi-num">{{ k.value }}</div>
          <div class="kpi-label">{{ k.label }}</div>
        </div>
      </el-col>
    </el-row>

    <!-- Tab 瀵艰埅 -->
    <el-tabs v-model="activeTab" type="border-card" class="mall-tabs">
      <el-tab-pane label="鎬昏" name="overview">
        <OverviewPanel :stats="stats" :endpoints="endpoints" :scanHistory="scanHistory" :aiSummary="aiSummary" @scan="scanAll" @brain="aiBrainScan" />
      </el-tab-pane>

      <el-tab-pane label="鍟嗗搧" name="products">
        <DataTablePanel title="鍟嗗搧绠＄悊" :columns="productColumns" :fetch="getProductList" :onDelete="deleteProduct" :onAudit="auditProduct" searchPlaceholder="鎼滅储鍟嗗搧鍚嶇О/ID" />
      </el-tab-pane>

      <el-tab-pane label="璁㈠崟" name="orders">
        <DataTablePanel title="璁㈠崟绠＄悊" :columns="orderColumns" :fetch="getOrderList" :onDetail="getOrderDetail" :onRefund="forceRefund" :onLogs="getOrderLogs" searchPlaceholder="鎼滅储璁㈠崟鍙?鐢ㄦ埛" />
      </el-tab-pane>

      <el-tab-pane label="鐢ㄦ埛" name="users">
        <DataTablePanel title="鐢ㄦ埛绠＄悊" :columns="userColumns" :fetch="getUserList" :onStatus="updateUserStatus" :onBalance="adjustUserBalance" searchPlaceholder="鎼滅储鐢ㄦ埛鍚?鎵嬫満鍙? />
      </el-tab-pane>

      <el-tab-pane label="鍒嗙被" name="categories">
        <CategoryPanel />
      </el-tab-pane>

      <el-tab-pane label="璐㈠姟" name="finance">
        <FinancePanel />
      </el-tab-pane>

      <el-tab-pane label="鐗╂祦" name="logistics">
        <DataTablePanel title="鐗╂祦绠＄悊" :columns="logisticsColumns" :fetch="fetchLogistics" :onTrace="getLogisticsTrace" searchPlaceholder="杈撳叆璁㈠崟ID鏌ヨ鐗╂祦" />
      </el-tab-pane>

      <el-tab-pane label="璁よ瘉" name="kyc">
        <KycPanel />
      </el-tab-pane>

      <el-tab-pane label="鍟嗗" name="merchants">
        <MerchantPanel />
      </el-tab-pane>

      <el-tab-pane label="鍐呭" name="content">
        <ContentPanel />
      </el-tab-pane>

      <el-tab-pane label="瀹㈡湇" name="service">
        <CustomerServicePanel />
      </el-tab-pane>

      <el-tab-pane label="椋庢帶" name="risk">
        <RiskPanel />
      </el-tab-pane>

      <el-tab-pane label="钀ラ攢" name="marketing">
        <MarketingPanel />
      </el-tab-pane>

      <el-tab-pane label="绯荤粺" name="system">
        <SystemPanel />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as mallApi from '@/api/mall'
import OverviewPanel from './mall/OverviewPanel.vue'
import DataTablePanel from './mall/DataTablePanel.vue'
import CategoryPanel from './mall/CategoryPanel.vue'
import FinancePanel from './mall/FinancePanel.vue'
import KycPanel from './mall/KycPanel.vue'
import MerchantPanel from './mall/MerchantPanel.vue'
import ContentPanel from './mall/ContentPanel.vue'
import CustomerServicePanel from './mall/CustomerServicePanel.vue'
import RiskPanel from './mall/RiskPanel.vue'
import MarketingPanel from './mall/MarketingPanel.vue'
import SystemPanel from './mall/SystemPanel.vue'

const activeTab = ref('overview')
const scanning = ref(false)
const brainLoading = ref(false)
const stats = ref({})
const endpoints = ref([])
const scanHistory = ref([])
const aiSummary = ref({})
const kpis = ref([
  { label: '鍟嗗搧鎬绘暟', value: 0, bg: 'linear-gradient(135deg,#409eff,#337ecc)' },
  { label: '璁㈠崟鎬绘暟', value: 0, bg: 'linear-gradient(135deg,#67c23a,#529b2e)' },
  { label: '鐢ㄦ埛鎬绘暟', value: 0, bg: 'linear-gradient(135deg,#e6a23c,#cf9236)' },
  { label: '鍟嗗鎬绘暟', value: 0, bg: 'linear-gradient(135deg,#f56c6c,#c45656)' },
  { label: '寰呭鏍?, value: 0, bg: 'linear-gradient(135deg,#909399,#73767a)' },
  { label: '浠婃棩璁㈠崟', value: 0, bg: 'linear-gradient(135deg,#8b5cf6,#7c3aed)' },
])

const productColumns = [
  { prop: 'id', label: 'ID', width: 80 },
  { prop: 'title', label: '鍟嗗搧鍚嶇О' },
  { prop: 'price', label: '浠锋牸', width: 100 },
  { prop: 'stock', label: '搴撳瓨', width: 80 },
  { prop: 'status', label: '鐘舵€?, width: 80 },
]
const orderColumns = [
  { prop: 'order_id', label: '璁㈠崟鍙?, width: 180 },
  { prop: 'user_name', label: '鐢ㄦ埛鍚?, width: 100 },
  { prop: 'total', label: '閲戦', width: 100 },
  { prop: 'status', label: '鐘舵€?, width: 80 },
  { prop: 'create_time', label: '鏃堕棿', width: 160 },
]
const userColumns = [
  { prop: 'id', label: 'ID', width: 80 },
  { prop: 'username', label: '鐢ㄦ埛鍚?, width: 120 },
  { prop: 'phone', label: '鎵嬫満鍙?, width: 130 },
  { prop: 'balance', label: '浣欓', width: 100 },
  { prop: 'status', label: '鐘舵€?, width: 80 },
]
const logisticsColumns = [
  { prop: 'order_id', label: '璁㈠崟ID', width: 180 },
  { prop: 'carrier', label: '蹇€掑叕鍙?, width: 120 },
  { prop: 'tracking_no', label: '杩愬崟鍙?, width: 150 },
  { prop: 'status', label: '鐘舵€?, width: 100 },
]

async function fetchLogistics(params) {
  const keyword = params?.keyword
  if (!keyword) return { list: [], total: 0 }
  try {
    const data = await mallApi.getLogisticsInfo(keyword)
    if (!data || data.error) return { list: [], total: 0 }
    return { list: [data], total: 1 }
  } catch { return { list: [], total: 0 } }
}

async function loadAll() {
  try {
    const [sRes, pRes, oRes, uRes] = await Promise.allSettled([
      mallApi.getMallStatus(),
      mallApi.getProductList({ page: 1, size: 1 }),
      mallApi.getOrderList({ page: 1, size: 1 }),
      mallApi.getUserList({ page: 1, size: 1 }),
    ])
    if (sRes.status === 'fulfilled') stats.value = sRes.value
    if (pRes.status === 'fulfilled') kpis.value[0].value = pRes.value?.total || 0
    if (oRes.status === 'fulfilled') kpis.value[1].value = oRes.value?.total || 0
    if (uRes.status === 'fulfilled') kpis.value[2].value = uRes.value?.total || 0
  } catch (e) { /* ignore */ }
}

async function scanAll() {
  scanning.value = true
  try {
    const r = await mallApi.scanStructure()
    endpoints.value = Object.entries(r.status || {}).map(([k, v]) => ({ name: k, ...v }))
    ElMessage.success(`鎵弿瀹屾垚: ${r.summary}`)
  } catch { ElMessage.error('鎵弿澶辫触') }
  scanning.value = false
}

async function aiBrainScan() {
  brainLoading.value = true
  try {
    const r = await mallApi.mallBrainScan()
    aiSummary.value = r
    ElMessage.success('AI鍒嗘瀽瀹屾垚')
  } catch { ElMessage.error('AI鍒嗘瀽澶辫触') }
  brainLoading.value = false
}

onMounted(() => { loadAll(); scanAll() })
</script>

<style scoped>
.mall-admin-panel { padding: 16px 20px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.page-header h2 { margin: 0; font-size: 18px; }
.header-actions { display: flex; gap: 8px; }
.kpi-row { margin-bottom: 12px; }
.kpi-card { padding: 12px 16px; border-radius: 8px; color: #fff; text-align: center; }
.kpi-num { font-size: 24px; font-weight: 700; }
.kpi-label { font-size: 12px; opacity: 0.9; margin-top: 2px; }
.mall-tabs { border-radius: 8px; overflow: hidden; }
:deep(.el-tabs__content) { padding: 16px; }
</style>
