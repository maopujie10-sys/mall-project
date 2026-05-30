<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  getDashboard, getUserList, updateUserStatus, adjustUserBalance,
  getProductList, auditProduct, getOrderList, forceRefund,
  getRechargePending, auditRecharge, getWithdrawPending, auditWithdraw,
  getMerchantList, updateMerchantStatus, getMerchantApplyList, auditMerchantApply,
  getDashboardHead, getDashboardLine, getDashboardGoods,
  getBannerList, saveBanner, updateBanner, deleteBanner,
  getCategoryList, saveCategory, updateCategory, updateCategoryStatus, deleteCategory,
  getEvaluationList, updateEvaluationStatus, deleteEvaluation,
  getAttrCategoryList, saveAttrCategory, updateAttrCategory, deleteAttrCategory,
  getAttrList, saveAttr, updateAttr, deleteAttr,
} from '@/api/mall'

const activeTab = ref('dashboard')
const chartRef = ref(null)
const chartR = ref(0)
let chart = null, timer = null

// ===== 浠〃鐩樻暟鎹?=====
const kpis = reactive([
  { label:'总用户', value:0, color:'c1', key:'total_users' },
  { label:'今日订单', value:0, color:'c2', key:'today_orders' },
  { label:'今日交易额', value:0, color:'c3', key:'today_amount' },
  { label:'待处理', value:0, color:'c4', key:'pending_recharge' },
])
const orderStats = reactive([
  { l:'总订单', v:0 },{ l:'待付款', v:0 },{ l:'已完成', v:0 },{ l:'已取消', v:0 },
])
const topGoods = ref([])
const chartData = reactive({ comm:[], s:[] })

// ===== 鍚勬ā鍧楁暟鎹?=====
const users = ref([]), userKw = ref(''), userPg = ref(1), userTotal = ref(0)
const merchants = ref([]), merKw = ref(''), merPg = ref(1), merTotal = ref(0)
const products = ref([]), prodKw = ref(''), prodPg = ref(1), prodTotal = ref(0)
const orders = ref([]), orderKw = ref(''), orderPg = ref(1), orderTotal = ref(0)
const recharges = ref([]), recPending = ref(0)
const withdraws = ref([]), witPending = ref(0)
const applies = ref([])
const balDlg = reactive({ show:false, user:'', userId:null, amount:'', remark:''})
const applyDlg = reactive({ show:false })

// ===== 轮播图 =====
const banners = ref([]), bannerType = ref(''), bannerPg = ref(1), bannerTotal = ref(0)
const bannerDlg = reactive({ show:false, uuid:'', title:'', type:'home', imgUrl:'', sort:0, linkUrl:'' })

// ===== 鍒嗙被 =====
const categories = ref([]), catLevel = ref(null), catPg = ref(1), catTotal = ref(0)
const catDlg = reactive({ show:false, uuid:'', name:'', sort:0, level:1, parentId:'0', type:1, iconImg:'', status:1 })

// ===== 璇勪环 =====
const evaluations = ref([]), evalKw = ref(''), evalStatus = ref(null), evalPg = ref(1), evalTotal = ref(0)

// ===== 灞炴€у垎绫?+ 灞炴€?=====
const attrCats = ref([]), attrCatKw = ref(''), attrCatPg = ref(1), attrCatTotal = ref(0)
const attrCatDlg = reactive({ show:false, uuid:'', name:'', sort:0 })
const attrs = ref([]), attrCatFilter = ref(''), attrPg = ref(1), attrTotal = ref(0)
const attrDlg = reactive({ show:false, uuid:'', categoryId:'', sort:0 })

// ===== 閫氱敤 =====
function fmt(v) {
  if (v == null) return '0'
  const n = Number(v)
  return Number.isNaN(n) ? String(v) : n.toLocaleString('en-US',{maximumFractionDigits:2})
}
function statTxt(s) { return s===1?'上架':s===0?'待审':'下架'}

// ===== 仪表盘 =====
async function loadDashboard() {
  try {
    const d = await getDashboard()
    if (d) {
      kpis[0].value = d.total_users ?? d.totalUsers ?? 0
      kpis[1].value = d.today_orders ?? d.todayOrders ?? 0
      kpis[2].value = d.today_amount ?? d.todayAmount ?? 0
      kpis[3].value = (d.pending_recharge||0) + (d.pending_withdraw||0) + (d.pending_merchant||0)
      orderStats[0].v = d.total_orders ?? 0
    }
  } catch(_){}
  try {
    const g = await getDashboardGoods()
    if (g?.goods) topGoods.value = g.goods.slice(0,10)
  } catch(_){}
  try {
    const l = await getDashboardLine({type:chartR.value})
    if (l?.line) {
      chartData.comm = l.line.map(x=>x.dayString||'')
      chartData.s = l.line.map(x=>x.countSales||0)
    }
  } catch(_){}
  nextTick(()=>initChart())
}

function initChart() {
  if (!chartRef.value) return
  if (chart) chart.dispose()
  chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip:{trigger:'axis'}, legend:{data:['销量'],left:'left',top:0},
    grid:{left:10,right:20,bottom:20,top:40,containLabel:true},
    xAxis:{type:'category',data:chartData.comm,boundaryGap:false},
    yAxis:{type:'value',minInterval:1},
    series:[{name:'销量',type:'line',smooth:false,data:chartData.s,
      lineStyle:{color:'#FF005A',width:2},itemStyle:{color:'#FF005A'}}],
  })
}
function switchChart(i) { chartR.value=i; loadDashboard() }

// ===== 鐢ㄦ埛 =====
async function fetchUsers() {
  try {
    const d = await getUserList({keyword:userKw.value,page:userPg.value,size:10})
    if (d?.records) { users.value = d.records; userTotal.value = d.total||0 }
    else if (Array.isArray(d)) { users.value = d; userTotal.value = d.length }
  } catch(_){}
}
async function toggleUser(row) {
  try {
    await updateUserStatus({userId:row.id,status:row.status===1?0:1})
    ElMessage.success('已更新'); fetchUsers()
  } catch(e) { ElMessage.error(e.message) }
}
function showBalDlg(row) { balDlg.user=row.username||row.phone; balDlg.userId=row.id; balDlg.amount=''; balDlg.remark=''; balDlg.show=true }
async function doAdjust() {
  try {
    await adjustUserBalance({userId:balDlg.userId,amount:balDlg.amount,remark:balDlg.remark})
    ElMessage.success('已调整')
    balDlg.show=false
    fetchUsers()
  } catch(e) { ElMessage.error(e.message) }
}

// ===== 商家 =====
async function fetchMerchants() {
  try {
    const d = await getMerchantList({keyword:merKw.value,page:merPg.value,size:10})
    if (d?.records) { merchants.value = d.records; merTotal.value = d.total||0 }
    else if (Array.isArray(d)) { merchants.value = d; merTotal.value = d.length }
  } catch(_){}
}

async function toggleMer(row) {
  try {
    await updateMerchantStatus({merchantId:row.id,status:row.status===1?0:1})
    ElMessage.success('已更新')
    fetchMerchants()
  } catch(e) { ElMessage.error(e.message) }
}
async function fetchMerApplies() {
  try {
    const d = await getMerchantApplyList({page:1,size:50})
    applies.value = d?.records || (Array.isArray(d)?d:[])
    applyDlg.show = true
  } catch(_){}
}
async function auditApply(row, approved) {
  try {
    await auditMerchantApply({applyId:row.id,approved})
    ElMessage.success(approved?'已通过':'已拒绝')
    applies.value = applies.value.filter(x=>x.id!==row.id)
  } catch(e) { ElMessage.error(e.message) }
}

// ===== 鍟嗗搧 =====
async function fetchProducts() {
  try {
    const d = await getProductList({keyword:prodKw.value,page:prodPg.value,size:10})
    if (d?.records) { products.value = d.records; prodTotal.value = d.total||0 }
    else if (Array.isArray(d)) { products.value = d; prodTotal.value = d.length }
  } catch(_){}
}
async function auditProd(row, status) {
  try {
    await auditProduct({productId:row.id,status})
    ElMessage.success(status===1?'已上架':'已下架')
    fetchProducts()
  } catch(e) { ElMessage.error(e.message) }
}

// ===== 订单 =====
async function fetchOrders() {
  try {
    const d = await getOrderList({keyword:orderKw.value,page:orderPg.value,size:10})
    if (d?.records) { orders.value = d.records; orderTotal.value = d.total||0 }
    else if (Array.isArray(d)) { orders.value = d; orderTotal.value = d.length }
  } catch(_){}
}

async function doRefund(row) {
  try {
    await ElMessageBox.confirm(`确认对订单 ${row.orderNo||row.id} 进行退款？`, '退款确认', {type:'warning'})
    await forceRefund(row.id)
    ElMessage.success('已退款')
    fetchOrders()
  } catch(_){}
}

// ===== 鍏呭€?=====
async function fetchRecharges() {
  try {
    const d = await getRechargePending({page:1,size:100})
    recharges.value = d?.records || (Array.isArray(d)?d:[])
    recPending.value = recharges.value.length
  } catch(_){}
}
async function auditRec(row, approved) {
  try {
    await auditRecharge({id:row.id,approved,reason:''})
    ElMessage.success(approved?'已通过':'已拒绝'); fetchRecharges()
  } catch(e) { ElMessage.error(e.message) }
}

// ===== 鎻愮幇 =====
async function fetchWithdraws() {
  try {
    const d = await getWithdrawPending({page:1,size:100})
    withdraws.value = d?.records || (Array.isArray(d)?d:[])
    witPending.value = withdraws.value.length
  } catch(_){}
}
async function auditWit(row, approved) {
  try {
    await auditWithdraw({id:row.id,approved,txHash:'',reason:''})
    ElMessage.success(approved?'已通过':'已拒绝')
    fetchWithdraws()
  } catch(e) { ElMessage.error(e.message) }
}

// ===== 轮播图 =====
async function fetchBanners() {
  try {
    const params = { page: bannerPg.value, size: 20 }
    if (bannerType.value) params.type = bannerType.value
    const d = await getBannerList(params)
    if (d?.records) { banners.value = d.records; bannerTotal.value = d.total || 0 }
    else if (Array.isArray(d)) { banners.value = d; bannerTotal.value = d.length }
  } catch(_){}
}

function showBannerDlg(row) {
  if (row) {
    bannerDlg.uuid = row.uuid; bannerDlg.title = row.title||''; bannerDlg.type = row.type||'home'
    bannerDlg.imgUrl = row.imgUrl||''; bannerDlg.sort = row.sort||0; bannerDlg.linkUrl = row.linkUrl||''
  } else {
    bannerDlg.uuid = ''; bannerDlg.title = ''; bannerDlg.type = 'home'
    bannerDlg.imgUrl = ''; bannerDlg.sort = 0; bannerDlg.linkUrl = ''
  }
  bannerDlg.show = true
}
async function saveBannerDlg() {
  try {
    const body = { title:bannerDlg.title, type:bannerDlg.type, imgUrl:bannerDlg.imgUrl, sort:bannerDlg.sort, linkUrl:bannerDlg.linkUrl }
    if (bannerDlg.uuid) await updateBanner(bannerDlg.uuid, body)
    else await saveBanner(body)
    ElMessage.success('已保存'); bannerDlg.show = false; fetchBanners()
  } catch(e) { ElMessage.error(e.message) }
}
async function delBanner(row) {
  try {
    await ElMessageBox.confirm('TODO','TODO',{type:'warning'})
    await deleteBanner(row.uuid); ElMessage.success('已删除'); fetchBanners()
  } catch(_){}
}

// ===== 鍒嗙被绠＄悊 =====
async function fetchCategories() {
  try {
    const params = { page: catPg.value, size: 20 }
    if (catLevel.value) params.level = catLevel.value
    const d = await getCategoryList(params)
    if (d?.records) { categories.value = d.records; catTotal.value = d.total || 0 }
    else if (Array.isArray(d)) { categories.value = d; catTotal.value = d.length }
  } catch(_){}
}
function showCatDlg(row) {
  if (row) {
    catDlg.uuid = row.uuid; catDlg.name = row.name||''; catDlg.sort = row.sort||0
    catDlg.level = row.level||1; catDlg.parentId = row.parentId||'0'
    catDlg.type = row.type||1; catDlg.iconImg = row.iconImg||''; catDlg.status = row.status||1
  } else {
    catDlg.uuid = ''; catDlg.name = ''; catDlg.sort = 0
    catDlg.level = 1; catDlg.parentId = '0'; catDlg.type = 1; catDlg.iconImg = ''; catDlg.status = 1
  }
  catDlg.show = true
}
async function saveCatDlg() {
  try {
    const body = { name:catDlg.name, sort:catDlg.sort, level:catDlg.level, parentId:catDlg.parentId, type:catDlg.type, iconImg:catDlg.iconImg, status:catDlg.status }
    if (catDlg.uuid) await updateCategory(catDlg.uuid, body)
    else await saveCategory(body)
    ElMessage.success('已保存'); catDlg.show = false; fetchCategories()
  } catch(e) { ElMessage.error(e.message) }
}
async function toggleCatStatus(row) {
  try {
    await updateCategoryStatus(row.uuid, {status: row.status===1?0:1})
    ElMessage.success('已更新'); fetchCategories()
  } catch(e) { ElMessage.error(e.message) }
}
async function delCat(row) {
  try {
    await ElMessageBox.confirm('纭鍒犻櫎璇ュ垎绫伙紵','鍒犻櫎纭',{type:'warning'})
    await deleteCategory(row.uuid); ElMessage.success('已删除'); fetchCategories()
  } catch(_){}
}

// ===== 璇勪环绠＄悊 =====
async function fetchEvaluations() {
  try {
    const params = { page: evalPg.value, size: 20 }
    if (evalKw.value) params.keyword = evalKw.value
    if (evalStatus.value !== null && evalStatus.value !== '') params.status = evalStatus.value
    const d = await getEvaluationList(params)
    if (d?.records) { evaluations.value = d.records; evalTotal.value = d.total || 0 }
    else if (Array.isArray(d)) { evaluations.value = d; evalTotal.value = d.length }
  } catch(_){}
}
async function toggleEval(row) {
  try {
    await updateEvaluationStatus(row.uuid, {status: row.status===1?0:1})
    ElMessage.success('已更新'); fetchEvaluations()
  } catch(e) { ElMessage.error(e.message) }
}
async function delEval(row) {
  try {
    await ElMessageBox.confirm('纭鍒犻櫎璇ヨ瘎浠凤紵','鍒犻櫎纭',{type:'warning'})
    await deleteEvaluation(row.uuid); ElMessage.success('已删除'); fetchEvaluations()
  } catch(_){}
}

// ===== 灞炴€у垎绫荤鐞?=====
async function fetchAttrCats() {
  try {
    const params = { page: attrCatPg.value, size: 20 }
    if (attrCatKw.value) params.keyword = attrCatKw.value
    const d = await getAttrCategoryList(params)
    if (d?.records) { attrCats.value = d.records; attrCatTotal.value = d.total || 0 }
    else if (Array.isArray(d)) { attrCats.value = d; attrCatTotal.value = d.length }
  } catch(_){}
}
function showAttrCatDlg(row) {
  if (row) { attrCatDlg.uuid = row.uuid || row.id; attrCatDlg.name = row.name||''; attrCatDlg.sort = row.sort||0 }
  else { attrCatDlg.uuid = ''; attrCatDlg.name = ''; attrCatDlg.sort = 0 }
  attrCatDlg.show = true
}
async function saveAttrCatDlg() {
  try {
    const body = { name: attrCatDlg.name, sort: attrCatDlg.sort }
    if (attrCatDlg.uuid) await updateAttrCategory(attrCatDlg.uuid, body)
    else await saveAttrCategory(body)
    ElMessage.success('已保存'); attrCatDlg.show = false; fetchAttrCats()
  } catch(e) { ElMessage.error(e.message) }
}
async function delAttrCat(row) {
  try {
    await ElMessageBox.confirm('纭鍒犻櫎璇ュ睘鎬у垎绫伙紵','鍒犻櫎纭',{type:'warning'})
    await deleteAttrCategory(row.uuid || row.id); ElMessage.success('已删除'); fetchAttrCats()
  } catch(_){}
}

// ===== 灞炴€х鐞?=====
async function fetchAttrs() {
  try {
    const params = { page: attrPg.value, size: 20 }
    if (attrCatFilter.value) params.categoryId = attrCatFilter.value
    const d = await getAttrList(params)
    if (d?.records) { attrs.value = d.records; attrTotal.value = d.total || 0 }
    else if (Array.isArray(d)) { attrs.value = d; attrTotal.value = d.length }
  } catch(_){}
}
function showAttrDlg(row) {
  if (row) { attrDlg.uuid = row.uuid || row.id; attrDlg.categoryId = row.categoryId||''; attrDlg.sort = row.sort||0 }
  else { attrDlg.uuid = ''; attrDlg.categoryId = ''; attrDlg.sort = 0 }
  attrDlg.show = true
}
async function saveAttrDlg() {
  try {
    const body = { categoryId: attrDlg.categoryId, sort: attrDlg.sort }
    if (attrDlg.uuid) await updateAttr(attrDlg.uuid, body)
    else await saveAttr(body)
    ElMessage.success('已保存'); attrDlg.show = false; fetchAttrs()
  } catch(e) { ElMessage.error(e.message) }
}
async function delAttr(row) {
  try {
    await ElMessageBox.confirm('纭鍒犻櫎璇ュ睘鎬э紵','鍒犻櫎纭',{type:'warning'})
    await deleteAttr(row.uuid || row.id); ElMessage.success('已删除'); fetchAttrs()
  } catch(_){}
}

// ===== 鐢熷懡鍛ㄦ湡 =====
onMounted(() => {
  loadDashboard()
  timer = setInterval(loadDashboard, 30000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  if (chart) chart.dispose()
})
</script>

<style scoped>
.mall-panel { padding: 0; }
.mall-tabs { border-radius: 8px; overflow: hidden; }

/* KPI */
.kpi-row { margin-bottom: 16px; }
.kpi-card { border-radius: 8px; padding: 22px 16px; color: #fff; text-align: center; min-height: 96px; display: flex; flex-direction: column; justify-content: center; margin-bottom: 12px; }
.kpi-card.c1 { background: rgba(255,131,153,0.12); }
.kpi-card.c2 { background: linear-gradient(135deg,#71C3FF,#54a0ff); }
.kpi-card.c3 { background: linear-gradient(135deg,#7190FF,#5f6fff); }
.kpi-card.c4 { background: linear-gradient(135deg,#5AD7CF,#2ed573); }
.kpi-num { font-size: 28px; font-weight: 700; }
.kpi-label { font-size: 13px; opacity: .9; margin-top: 4px; }

/* Card */
.card-hd { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.card-tt { font-size: 15px; font-weight: 600; color: #333; margin-bottom: 12px; }

/* Chart tabs */
.ctab { padding: 3px 10px; border:1px solid #ddd; border-radius:4px; font-size:12px; cursor:pointer; color:#999; margin-left:4px; user-select:none; }
.ctab.on { border-color:#1552F0; color:#1552F0; }

/* Chart */
.chart-box { width:100%; height:360px; }

/* Order stats */
.order-card { height: 444px; }
.order-grid { display:flex; flex-wrap:wrap; }
.oi { width:50%; text-align:center; padding:24px 0; }
.oi-num { font-size:22px; font-weight:700; color:#e99d42; }
.oi-lbl { font-size:13px; color:#999; margin-top:4px; }

/* Toolbar */
.tb-bar { display:flex; gap:8px; margin-bottom:12px; }
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>
