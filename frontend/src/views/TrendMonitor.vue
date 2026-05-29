<template>
  <div class="trend-page">
    <div class="page-header">
      <div><h1>📡 竞品监控</h1><p>价格变动告警 · 促销追踪 · 趋势分析 · 新品发现</p></div>
      <el-button type="primary" @click="showAddDialog = true">+ 添加竞品</el-button>
    </div>

    <!-- 统计概要 -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="4" v-for="c in summaryCards" :key="c.label">
        <el-card shadow="never" class="sm-card"><div class="sm-val">{{ c.value }}</div><div class="sm-lbl">{{ c.label }}</div></el-card>
      </el-col>
    </el-row>

    <!-- 竞品列表 -->
    <el-card shadow="never" style="margin-bottom:20px">
      <template #header>📋 监控列表 ({{ tracks.length }})</template>
      <el-table :data="tracks" size="small">
        <el-table-column prop="product" label="商品名" min-width="150"/>
        <el-table-column prop="platform" label="平台" width="100"/>
        <el-table-column label="当前价" width="120">
          <template #default="{row}">
            <span v-if="row.price_history && row.price_history.length">
              {{ row.price_history[row.price_history.length-1].price }} {{ row.price_history[row.price_history.length-1].currency || 'USD' }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="目标价" width="100"><template #default="{row}">{{ row.target_price || '-' }}</template></el-table-column>
        <el-table-column label="变动" width="80">
          <template #default="{row}">
            <el-tag v-if="row.lastChange" :type="row.lastChange>0?'danger':'success'" size="small">{{ row.lastChange }}%</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="告警" width="80"><template #default="{row}">{{ (row.alerts||[]).length }}</template></el-table-column>
        <el-table-column label="促销" width="80"><template #default="{row}">{{ (row.promotions||[]).length }}</template></el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{row}">
            <el-button size="small" link @click="showPriceDialog(row)">💰记录价格</el-button>
            <el-button size="small" link @click="showPromoDialog(row)">🎉记录促销</el-button>
            <el-button size="small" link type="danger" @click="doRemove(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 价格趋势 -->
    <el-card shadow="never" style="margin-bottom:20px" v-if="trends.length">
      <template #header>📈 价格趋势</template>
      <el-table :data="trends" size="small">
        <el-table-column prop="product" label="商品"/>
        <el-table-column prop="platform" label="平台" width="100"/>
        <el-table-column prop="first_price" label="初始价" width="100"/>
        <el-table-column prop="last_price" label="最新价" width="100"/>
        <el-table-column label="变动" width="100">
          <template #default="{row}">
            <el-tag :type="row.trend==='up'?'danger':row.trend==='down'?'success':''" size="small">{{ row.change_pct }}%</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="趋势" width="80">
          <template #default="{row}">{{ row.trend==='up'?'📈上涨':row.trend==='down'?'📉下跌':'➡️平稳' }}</template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 价格告警 + 促销 -->
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>⚠️ 价格告警 (近7天)</template>
          <el-timeline v-if="alerts.length">
            <el-timeline-item v-for="a in alerts.slice(-10).reverse()" :key="a.time" :timestamp="a.time?.substr(0,16)" :type="a.severity==='P1'?'danger':'warning'">
              {{ a.product }}: {{ a.from }}→{{ a.to }} ({{ a.change_pct }}%)
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="无告警"/>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>🎉 活跃促销</template>
          <el-timeline v-if="promos.length">
            <el-timeline-item v-for="p in promos.slice(-10).reverse()" :key="p.time" :timestamp="p.time?.substr(0,16)">
              {{ p.product }}: {{ p.title }} <el-tag v-if="p.discount" size="small">{{ p.discount }}</el-tag>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="无促销"/>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加竞品对话框 -->
    <el-dialog v-model="showAddDialog" title="添加竞品监控" width="450px">
      <el-form label-width="80px">
        <el-form-item label="商品名称"><el-input v-model="addForm.product_name"/></el-form-item>
        <el-form-item label="平台"><el-select v-model="addForm.platform" style="width:100%">
          <el-option label="eBay" value="ebay"/><el-option label="Amazon" value="amazon"/>
          <el-option label="AliExpress" value="aliexpress"/><el-option label="Shopee" value="shopee"/>
          <el-option label="淘宝" value="taobao"/><el-option label="1688" value="alibaba1688"/>
        </el-select></el-form-item>
        <el-form-item label="商品链接"><el-input v-model="addForm.url"/></el-form-item>
        <el-form-item label="目标价格"><el-input-number v-model="addForm.target_price" :min="0"/></el-form-item>
        <el-form-item label="分类"><el-input v-model="addForm.category"/></el-form-item>
      </el-form>
      <template #footer><el-button @click="showAddDialog=false">取消</el-button><el-button type="primary" @click="doAdd">添加</el-button></template>
    </el-dialog>

    <!-- 记录价格对话框 -->
    <el-dialog v-model="showPriceDlg" :title="'记录价格: '+priceForm.product" width="350px">
      <el-form label-width="80px">
        <el-form-item label="价格"><el-input-number v-model="priceForm.price" :min="0" :precision="2"/></el-form-item>
        <el-form-item label="币种"><el-select v-model="priceForm.currency"><el-option label="USD" value="USD"/><el-option label="CNY" value="CNY"/></el-select></el-form-item>
      </el-form>
      <template #footer><el-button @click="showPriceDlg=false">取消</el-button><el-button type="primary" @click="doRecordPrice">记录</el-button></template>
    </el-dialog>

    <!-- 记录促销对话框 -->
    <el-dialog v-model="showPromoDlg" :title="'记录促销: '+promoForm.product" width="400px">
      <el-form label-width="80px">
        <el-form-item label="标题"><el-input v-model="promoForm.title"/></el-form-item>
        <el-form-item label="折扣"><el-input v-model="promoForm.discount" placeholder="如: 30% OFF"/></el-form-item>
      </el-form>
      <template #footer><el-button @click="showPromoDlg=false">取消</el-button><el-button type="primary" @click="doRecordPromo">记录</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { addTrack, listTracks, removeTrack, recordPrice, recordPromotion, getPriceAlerts, getPriceTrends, getActivePromotions, getCompetitorSummary } from '@/api/competitor'

const tracks = ref([])
const alerts = ref([])
const trends = ref([])
const promos = ref([])
const summary = ref({})
const showAddDialog = ref(false)
const showPriceDlg = ref(false)
const showPromoDlg = ref(false)

const addForm = ref({ product_name:'', platform:'ebay', url:'', target_price:0, category:'' })
const priceForm = ref({ trackId:'', product:'', price:0, currency:'USD' })
const promoForm = ref({ trackId:'', product:'', title:'', discount:'' })

const summaryCards = computed(() => [
  { label:'监控总数', value: summary.value.total_tracks || 0 },
  { label:'活跃', value: summary.value.active_tracks || 0 },
  { label:'价格变动(7d)', value: summary.value.price_changes_7d || 0 },
  { label:'总告警', value: summary.value.total_alerts || 0 },
  { label:'总促销', value: summary.value.total_promotions || 0 },
  { label:'平台数', value: Object.keys(summary.value.by_platform||{}).length || 0 },
])

async function loadAll() {
  try {
    const [t, a, tr, p, s] = await Promise.all([
      listTracks(), getPriceAlerts(7), getPriceTrends(), getActivePromotions(), getCompetitorSummary()
    ])
    tracks.value = (t.data.tracks || []).map(trk => {
      const h = trk.price_history || []
      const last = h.length >= 2 ? h[h.length-1] : null
      const prev = h.length >= 2 ? h[h.length-2] : null
      return { ...trk, lastChange: last && prev && prev.price ? ((last.price - prev.price) / prev.price * 100).toFixed(1) : null }
    })
    alerts.value = a.data.alerts || []
    trends.value = tr.data.trends || []
    promos.value = p.data.promotions || []
    summary.value = s.data || {}
  } catch(e) {}
}

async function doAdd() {
  try {
    await addTrack(addForm.value.product_name, addForm.value.platform, addForm.value.url, addForm.value.target_price, addForm.value.category)
    ElMessage.success('已添加')
    showAddDialog.value = false
    addForm.value = { product_name:'', platform:'ebay', url:'', target_price:0, category:'' }
    loadAll()
  } catch(e) { ElMessage.error('添加失败') }
}

async function doRemove(id) {
  try { await removeTrack(id); ElMessage.success('已删除'); loadAll() } catch(e) { ElMessage.error('删除失败') }
}

function showPriceDialog(row) { priceForm.value = { trackId: row.id, product: row.product, price: 0, currency: 'USD' }; showPriceDlg.value = true }
function showPromoDialog(row) { promoForm.value = { trackId: row.id, product: row.product, title: '', discount: '' }; showPromoDlg.value = true }

async function doRecordPrice() {
  try { await recordPrice(priceForm.value.trackId, priceForm.value.price, priceForm.value.currency); ElMessage.success('已记录'); showPriceDlg.value = false; loadAll() } catch(e) { ElMessage.error('记录失败') }
}

async function doRecordPromo() {
  try { await recordPromotion(promoForm.value.trackId, promoForm.value.title, promoForm.value.discount); ElMessage.success('已记录'); showPromoDlg.value = false; loadAll() } catch(e) { ElMessage.error('记录失败') }
}

onMounted(() => loadAll())
</script>

<style scoped>
.trend-page { padding: 0; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-header h1 { font-size: 22px; margin: 0 0 4px; }
.page-header p { color: var(--text-muted); font-size: 13px; margin: 0; }
.sm-card { text-align: center; }
.sm-card .sm-val { font-size: 24px; font-weight: 700; color: #1677ff; }
.sm-card .sm-lbl { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
</style>
