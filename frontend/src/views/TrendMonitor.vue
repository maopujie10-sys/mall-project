<template>
  <div class="trend-page">
    <div class="page-header">
      <div><h1>馃摗 绔炲搧鐩戞帶</h1><p>浠锋牸鍙樺姩鍛婅 路 淇冮攢杩借釜 路 瓒嬪娍鍒嗘瀽 路 鏂板搧鍙戠幇</p></div>
      <el-button type="primary" @click="showAddDialog = true">+ 娣诲姞绔炲搧</el-button>
    </div>

    <!-- 缁熻姒傝 -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="4" v-for="c in summaryCards" :key="c.label">
        <el-card shadow="never" class="sm-card"><div class="sm-val">{{ c.value }}</div><div class="sm-lbl">{{ c.label }}</div></el-card>
      </el-col>
    </el-row>

    <!-- 绔炲搧鍒楄〃 -->
    <el-card shadow="never" style="margin-bottom:20px">
      <template #header>馃搵 鐩戞帶鍒楄〃 ({{ tracks.length }})</template>
      <el-table :data="tracks" size="small">
        <el-table-column prop="product" label="鍟嗗搧鍚? min-width="150"/>
        <el-table-column prop="platform" label="骞冲彴" width="100"/>
        <el-table-column label="..." width="120">
          <template #default="{row}">
            <span v-if="row.price_history && row.price_history.length">
              {{ row.price_history[row.price_history.length-1].price }} {{ row.price_history[row.price_history.length-1].currency || 'USD' }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="..." width="100"><template #default="{row}">{{ row.target_price || '-' }}</template></el-table-column>
        <el-table-column label="鍙樺姩" width="80">
          <template #default="{row}">
            <el-tag v-if="row.lastChange" :type="row.lastChange>0?'danger':'success'" size="small">{{ row.lastChange }}%</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="鍛婅" width="80"><template #default="{row}">{{ (row.alerts||[]).length }}</template></el-table-column>
        <el-table-column label="淇冮攢" width="80"><template #default="{row}">{{ (row.promotions||[]).length }}</template></el-table-column>
        <el-table-column label="鎿嶄綔" width="200">
          <template #default="{row}">
            <el-button size="small" link @click="showPriceDialog(row)">馃挵璁板綍浠锋牸</el-button>
            <el-button size="small" link @click="showPromoDialog(row)">馃帀璁板綍淇冮攢</el-button>
            <el-button size="small" link type="danger" @click="doRemove(row.id)">鍒犻櫎</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 浠锋牸瓒嬪娍 -->
    <el-card shadow="never" style="margin-bottom:20px" v-if="trends.length">
      <template #header>馃搱 浠锋牸瓒嬪娍</template>
      <el-table :data="trends" size="small">
        <el-table-column prop="product" label="鍟嗗搧"/>
        <el-table-column prop="platform" label="骞冲彴" width="100"/>
        <el-table-column prop="first_price" label="..." width="100"/>
        <el-table-column prop="last_price" label="鏈€鏂颁环" width="100"/>
        <el-table-column label="鍙樺姩" width="100">
          <template #default="{row}">
            <el-tag :type="row.trend==='up'?'danger':row.trend==='down'?'success':''" size="small">{{ row.change_pct }}%</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="瓒嬪娍" width="80">
          <template #default="{row}">{{ row.trend==='up'?'馃搱涓婃定':row.trend==='down'?'馃搲涓嬭穼':'鉃★笍骞崇ǔ' }}</template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 浠锋牸鍛婅 + 淇冮攢 -->
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>鈿狅笍 浠锋牸鍛婅 (杩澶?</template>
          <el-timeline v-if="alerts.length">
            <el-timeline-item v-for="a in alerts.slice(-10).reverse()" :key="a.time" :timestamp="a.time?.substr(0,16)" :type="a.severity==='P1'?'danger':'warning'">
              {{ a.product }}: {{ a.from }}鈫抺{ a.to }} ({{ a.change_pct }}%)
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="鏃犲憡璀?/>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>馃帀 娲昏穬淇冮攢</template>
          <el-timeline v-if="promos.length">
            <el-timeline-item v-for="p in promos.slice(-10).reverse()" :key="p.time" :timestamp="p.time?.substr(0,16)">
              {{ p.product }}: {{ p.title }} <el-tag v-if="p.discount" size="small">{{ p.discount }}</el-tag>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="鏃犱績閿€"/>
        </el-card>
      </el-col>
    </el-row>

    <!-- 娣诲姞绔炲搧瀵硅瘽妗?-->
    <el-dialog v-model="showAddDialog" title="娣诲姞绔炲搧鐩戞帶" width="450px">
      <el-form label-width="80px">
        <el-form-item label="鍟嗗搧鍚嶇О"><el-input v-model="addForm.product_name"/></el-form-item>
        <el-form-item label="骞冲彴"><el-select v-model="addForm.platform" style="width:100%">
          <el-option label="eBay" value="ebay"/><el-option label="Amazon" value="amazon"/>
          <el-option label="AliExpress" value="aliexpress"/><el-option label="Shopee" value="shopee"/>
          <el-option label="娣樺疂" value="taobao"/><el-option label="1688" value="alibaba1688"/>
        </el-select></el-form-item>
        <el-form-item label="鍟嗗搧閾炬帴"><el-input v-model="addForm.url"/></el-form-item>
        <el-form-item label="鐩爣浠锋牸"><el-input-number v-model="addForm.target_price" :min="0"/></el-form-item>
        <el-form-item label="鍒嗙被"><el-input v-model="addForm.category"/></el-form-item>
      </el-form>
      <template #footer><el-button @click="showAddDialog=false">鍙栨秷</el-button><el-button type="primary" @click="doAdd">娣诲姞</el-button></template>
    </el-dialog>

    <!-- 璁板綍浠锋牸瀵硅瘽妗?-->
    <el-dialog v-model="showPriceDlg" :title="'璁板綍浠锋牸: '+priceForm.product" width="350px">
      <el-form label-width="80px">
        <el-form-item label="浠锋牸"><el-input-number v-model="priceForm.price" :min="0" :precision="2"/></el-form-item>
        <el-form-item label="甯佺"><el-select v-model="priceForm.currency"><el-option label="USD" value="USD"/><el-option label="CNY" value="CNY"/></el-select></el-form-item>
      </el-form>
      <template #footer><el-button @click="showPriceDlg=false">鍙栨秷</el-button><el-button type="primary" @click="doRecordPrice">璁板綍</el-button></template>
    </el-dialog>

    <!-- 璁板綍淇冮攢瀵硅瘽妗?-->
    <el-dialog v-model="showPromoDlg" :title="'璁板綍淇冮攢: '+promoForm.product" width="400px">
      <el-form label-width="80px">
        <el-form-item label="鏍囬"><el-input v-model="promoForm.title"/></el-form-item>
        <el-form-item label="鎶樻墸"><el-input v-model="promoForm.discount" placeholder="濡? 30% OFF"/></el-form-item>
      </el-form>
      <template #footer><el-button @click="showPromoDlg=false">鍙栨秷</el-button><el-button type="primary" @click="doRecordPromo">璁板綍</el-button></template>
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
  { label:'鐩戞帶鎬绘暟', value: summary.value.total_tracks || 0 },
  { label:'娲昏穬', value: summary.value.active_tracks || 0 },
  { label:'浠锋牸鍙樺姩(7d)', value: summary.value.price_changes_7d || 0 },
  { label:'鎬诲憡璀?, value: summary.value.total_alerts || 0 },
  { label:'鎬讳績閿€', value: summary.value.total_promotions || 0 },
  { label:'骞冲彴鏁?, value: Object.keys(summary.value.by_platform||{}).length || 0 },
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
    ElMessage.success('宸叉坊鍔?)
    showAddDialog.value = false
    addForm.value = { product_name:'', platform:'ebay', url:'', target_price:0, category:'' }
    loadAll()
  } catch(e) { ElMessage.error('娣诲姞澶辫触') }
}

async function doRemove(id) {
  try { await removeTrack(id); ElMessage.success('宸插垹闄?); loadAll() } catch(e) { ElMessage.error('鍒犻櫎澶辫触') }
}

function showPriceDialog(row) { priceForm.value = { trackId: row.id, product: row.product, price: 0, currency: 'USD' }; showPriceDlg.value = true }
function showPromoDialog(row) { promoForm.value = { trackId: row.id, product: row.product, title: '', discount: '' }; showPromoDlg.value = true }

async function doRecordPrice() {
  try { await recordPrice(priceForm.value.trackId, priceForm.value.price, priceForm.value.currency); ElMessage.success('?); showPriceDlg.value = false; loadAll() } catch(e) { ElMessage.error('璁板綍澶辫触') }
}

async function doRecordPromo() {
  try { await recordPromotion(promoForm.value.trackId, promoForm.value.title, promoForm.value.discount); ElMessage.success('宸茶褰?); showPromoDlg.value = false; loadAll() } catch(e) { ElMessage.error('璁板綍澶辫触') }
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
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>
