<template>
  <div class="mall-admin-panel">
    <div class="page-header">
      <h2>商城总后台管理</h2>
      <div class="header-actions">
        <el-button size="small" @click="scanAll" :loading="scanning">一键扫描</el-button>
        <el-button size="small" type="primary" @click="aiBrainScan" :loading="brainLoading">AI大脑分析</el-button>
      </div>
    </div>

    <!-- KPI 指标卡 -->
    <el-row :gutter="12" class="kpi-row">
      <el-col :span="4" v-for="k in kpis" :key="k.label">
        <div class="kpi-card" :style="{ background: k.bg }">
          <div class="kpi-num">{{ k.value }}</div>
          <div class="kpi-label">{{ k.label }}</div>
        </div>
      </el-col>
    </el-row>

    <!-- Tab 导航 -->
    <el-tabs v-model="activeTab" type="border-card" class="mall-tabs">
      <el-tab-pane label="总览" name="overview">
        <OverviewPanel :stats="stats" :endpoints="endpoints" :scanHistory="scanHistory" :aiSummary="aiSummary" @scan="scanAll" @brain="aiBrainScan" />
      </el-tab-pane>

      <el-tab-pane label="商品" name="products">
        <DataTablePanel title="商品管理" :columns="productColumns" :fetch="getProductList" :onDelete="deleteProduct" :onAudit="auditProduct" searchPlaceholder="搜索商品名称/ID" />
      </el-tab-pane>

      <el-tab-pane label="订单" name="orders">
        <DataTablePanel title="订单管理" :columns="orderColumns" :fetch="getOrderList" :onDetail="getOrderDetail" :onRefund="forceRefund" :onLogs="getOrderLogs" searchPlaceholder="搜索订单号/用户" />
      </el-tab-pane>

      <el-tab-pane label="用户" name="users">
        <DataTablePanel title="用户管理" :columns="userColumns" :fetch="getUserList" :onStatus="updateUserStatus" :onBalance="adjustUserBalance" searchPlaceholder="搜索用户名/手机号" />
      </el-tab-pane>

      <el-tab-pane label="分类" name="categories">
        <CategoryPanel />
      </el-tab-pane>

      <el-tab-pane label="财务" name="finance">
        <FinancePanel />
      </el-tab-pane>

      <el-tab-pane label="物流" name="logistics">
        <DataTablePanel title="物流管理" :columns="logisticsColumns" :fetch="fetchLogistics" :onTrace="getLogisticsTrace" searchPlaceholder="输入订单ID查询物流" />
      </el-tab-pane>

      <el-tab-pane label="认证" name="kyc">
        <KycPanel />
      </el-tab-pane>

      <el-tab-pane label="商家" name="merchants">
        <MerchantPanel />
      </el-tab-pane>

      <el-tab-pane label="内容" name="content">
        <ContentPanel />
      </el-tab-pane>

      <el-tab-pane label="客服" name="service">
        <CustomerServicePanel />
      </el-tab-pane>

      <el-tab-pane label="风控" name="risk">
        <RiskPanel />
      </el-tab-pane>

      <el-tab-pane label="营销" name="marketing">
        <MarketingPanel />
      </el-tab-pane>

      <el-tab-pane label="系统" name="system">
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
  { label: '商品总数', value: 0, bg: 'linear-gradient(135deg,#409eff,#337ecc)' },
  { label: '订单总数', value: 0, bg: 'linear-gradient(135deg,#67c23a,#529b2e)' },
  { label: '用户总数', value: 0, bg: 'linear-gradient(135deg,#e6a23c,#cf9236)' },
  { label: '商家总数', value: 0, bg: 'linear-gradient(135deg,#f56c6c,#c45656)' },
  { label: '待审核', value: 0, bg: 'linear-gradient(135deg,#909399,#73767a)' },
  { label: '今日订单', value: 0, bg: 'linear-gradient(135deg,#8b5cf6,#7c3aed)' },
])

const productColumns = [
  { prop: 'id', label: 'ID', width: 80 },
  { prop: 'title', label: '商品名称' },
  { prop: 'price', label: '价格', width: 100 },
  { prop: 'stock', label: '库存', width: 80 },
  { prop: 'status', label: '状态', width: 80 },
]
const orderColumns = [
  { prop: 'order_id', label: '订单号', width: 180 },
  { prop: 'user_name', label: '用户名', width: 100 },
  { prop: 'total', label: '金额', width: 100 },
  { prop: 'status', label: '状态', width: 80 },
  { prop: 'create_time', label: '时间', width: 160 },
]
const userColumns = [
  { prop: 'id', label: 'ID', width: 80 },
  { prop: 'username', label: '用户名', width: 120 },
  { prop: 'phone', label: '手机号', width: 130 },
  { prop: 'balance', label: '余额', width: 100 },
  { prop: 'status', label: '状态', width: 80 },
]
const logisticsColumns = [
  { prop: 'order_id', label: '订单ID', width: 180 },
  { prop: 'carrier', label: '快递公司', width: 120 },
  { prop: 'tracking_no', label: '运单号', width: 150 },
  { prop: 'status', label: '状态', width: 100 },
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
    ElMessage.success(`扫描完成: ${r.summary}`)
  } catch { ElMessage.error('扫描失败') }
  scanning.value = false
}

async function aiBrainScan() {
  brainLoading.value = true
  try {
    const r = await mallApi.mallBrainScan()
    aiSummary.value = r
    ElMessage.success('AI分析完成')
  } catch { ElMessage.error('AI分析失败') }
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
