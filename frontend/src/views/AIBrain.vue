<template>
  <div class="page-container">

    <div class="page-header">
      <div>
        <h1>🧠 AI 商城大脑</h1>
        <p>全自动分析商城健康度，发现品类缺口，智能推荐运维方案</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="runScan" :loading="scanning">
          <el-icon><Search /></el-icon> 全站扫描
        </el-button>
        <el-button type="success" @click="runAutoOps" :loading="autoRunning">
          <el-icon><Promotion /></el-icon> AI自动运维
        </el-button>
      </div>
    </div>

    <!-- 健康概览 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6" v-for="item in summaryCards" :key="item.label">
        <el-card shadow="never" class="metric-card" :class="item.color">
          <div class="metric-num">{{ item.value }}</div>
          <div class="metric-label">{{ item.label }}</div>
          <div class="metric-sub">{{ item.sub }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 商品健康度表格 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="16">
        <el-card shadow="never">
          <template #header>
            <div class="panel-header">
              <span>📊 商品健康度分析</span>
              <el-select v-model="filterStatus" placeholder="筛选" size="small" style="width:120px">
                <el-option label="全部" value="all"/>
                <el-option label="热销" value="hot"/>
                <el-option label="正常" value="normal"/>
                <el-option label="冷门" value="cold"/>
                <el-option label="死品" value="dead"/>
              </el-select>
            </div>
          </template>
          <el-table :data="filteredProducts" style="width: 100%" size="small" max-height="400">
            <el-table-column prop="name" label="商品名称" min-width="180">
              <template #default="{ row }">
                <div style="display:flex;align-items:center;gap:8px;">
                  <div :style="{ width:36,height:36,borderRadius:6,background:row.color+'22',display:'flex',alignItems:'center',justifyContent:'center',fontSize:18 }">{{ row.icon }}</div>
                  <span style="font-size:13px;">{{ row.name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="category" label="品类" width="100"/>
            <el-table-column prop="price" label="价格" width="100"/>
            <el-table-column prop="sales" label="销量" width="80" sortable/>
            <el-table-column prop="stock" label="库存" width="80">
              <template #default="{ row }">
                <span :style="{ color: row.stock < 10 ? '#ff4d4f' : '#52c41a' }">{{ row.stock }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="90">
              <template #default="{ row }">
                <el-tag :type="row.statusType" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button text size="small" type="primary" @click="handleReplace(row)">替换</el-button>
                <el-button text size="small" type="danger" v-if="row.statusType==='info'" @click="handleRemove(row)">下架</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 品类缺口 -->
      <el-col :span="8">
        <el-card shadow="never">
          <template #header>
            <span>🔍 品类缺口分析</span>
          </template>
          <div class="gap-list">
            <div v-for="gap in gaps" :key="gap.name" class="gap-item">
              <div class="gap-info">
                <div class="gap-name">{{ gap.name }}</div>
                <div class="gap-bar-wrap">
                  <div class="gap-bar">
                    <div class="gap-fill" :class="gap.level" :style="{ width: gap.percent + '%' }"></div>
                  </div>
                  <span class="gap-num">{{ gap.current }}/{{ gap.target }}</span>
                </div>
              </div>
              <el-tag :type="gap.level === 'low' ? 'danger' : gap.level === 'mid' ? 'warning' : 'success'" size="small">
                {{ gap.level === 'low' ? '严重不足' : gap.level === 'mid' ? '需补充' : '充足' }}
              </el-tag>
            </div>
            <el-divider style="margin:16px 0"/>
            <div style="font-size:13px;color:var(--text-muted);margin-bottom:10px;">🤖 AI建议</div>
            <div class="ai-suggestions">
              <div v-for="s in suggestions" :key="s" class="sug-item">
                <el-icon color="#667eea"><CircleCheckFilled /></el-icon>
                <span>{{ s }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const scanning = ref(false)
const autoRunning = ref(false)
const filterStatus = ref('all')

const summaryCards = [
  { label: '商品总数', value: 68, sub: '个在线商品', color: 'blue' },
  { label: '热销商品', value: 12, sub: '🔥 高活跃', color: 'red' },
  { label: '死品待换', value: 3, sub: '💀 需替换', color: 'gray' },
  { label: '品类缺口', value: 4, sub: '⚠ 需补充', color: 'orange' },
]

const products = reactive([
  { id:1, icon:'📱', name:'iPhone 15 Pro Max 256GB', category:'手机数码', price:'¥8,999', sales:234, stock:45, status:'热销', statusType:'danger', color:'#ff4d4f' },
  { id:2, icon:'🎧', name:'AirPods Pro 2代', category:'手机数码', price:'¥1,699', sales:189, stock:23, status:'热销', statusType:'danger', color:'#ff4d4f' },
  { id:3, icon:'💻', name:'MacBook Air M3 15寸', category:'电脑办公', price:'¥9,499', sales:156, stock:12, status:'正常', statusType:'success', color:'#52c41a' },
  { id:4, icon:'👟', name:'Nike Air Max 270', category:'运动鞋服', price:'¥899', sales:67, stock:88, status:'正常', statusType:'success', color:'#52c41a' },
  { id:5, icon:'⌚', name:'Apple Watch Ultra 2', category:'手机数码', price:'¥5,999', sales:45, stock:18, status:'正常', statusType:'success', color:'#52c41a' },
  { id:6, icon:'🎮', name:'PS5 Slim 数字版', category:'游戏设备', price:'¥2,999', sales:12, stock:55, status:'冷门', statusType:'warning', color:'#faad14' },
  { id:7, icon:'📷', name:'Canon EOS R6 Mark II', category:'摄影摄像', price:'¥15,999', sales:5, stock:8, status:'冷门', statusType:'warning', color:'#faad14' },
  { id:8, icon:'🧸', name:'Jellycat 毛绒兔 30cm', category:'母婴玩具', price:'¥259', sales:0, stock:120, status:'死品', statusType:'info', color:'#d9d9d9' },
])

const gaps = [
  { name:'母婴玩具', current:1, target:8, percent:12, level:'low' },
  { name:'美妆护肤', current:2, target:10, percent:20, level:'low' },
  { name:'食品饮料', current:3, target:10, percent:30, level:'mid' },
  { name:'家居生活', current:5, target:12, percent:42, level:'mid' },
  { name:'运动户外', current:8, target:12, percent:67, level:'ok' },
  { name:'手机数码', current:15, target:15, percent:100, level:'ok' },
]

const suggestions = [
  '母婴玩具仅1件商品，建议从 eBay 采集补充',
  '美妆护肤严重不足，建议采集韩国美妆品牌',
  '发现3件死品超过30天零销量，建议下架替换',
]

const filteredProducts = computed(() => {
  if (filterStatus.value === 'all') return products
  const map = { hot:'热销', normal:'正常', cold:'冷门', dead:'死品' }
  return products.filter(p => p.status === map[filterStatus.value])
})

async function runScan() {
  scanning.value = true
  await new Promise(r => setTimeout(r, 1500))
  scanning.value = false
  ElMessage.success('全站扫描完成！发现 3 件死品，4 个品类缺口')
}

async function runAutoOps() {
  autoRunning.value = true
  await new Promise(r => setTimeout(r, 2000))
  autoRunning.value = false
  ElMessage.success('AI自动运维完成：下架1件死品，采集8件新品，补充库存12件')
}

function handleReplace(row) {
  ElMessageBox.confirm(`确认要从采集库中寻找 "${row.name}" 的替代品吗？`, '替换商品', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
  }).then(() => {
    ElMessage.success(`已开始为 "${row.name}" 寻找替代品`)
  }).catch(() => {})
}

function handleRemove(row) {
  ElMessageBox.confirm(`确认要下架 "${row.name}" 吗？该操作会自动备份。`, '下架商品', {
    confirmButtonText: '确认下架',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    ElMessage.success(`"${row.name}" 已下架`)
  }).catch(() => {})
}
</script>

<style scoped>
.page-container { padding: 24px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.page-header h1 { font-size: 20px; margin: 0 0 4px; color: var(--text-primary); }
.page-header p { font-size: 13px; color: var(--text-muted); margin: 0; }
.header-actions { display: flex; gap: 8px; }

.metric-card { text-align: center; border-radius: 12px; border-top: 3px solid transparent; }
.metric-card.blue { border-top-color: #667eea; }
.metric-card.red { border-top-color: #ff4d4f; }
.metric-card.gray { border-top-color: #d9d9d9; }
.metric-card.orange { border-top-color: #faad14; }
.metric-num { font-size: 36px; font-weight: 700; color: var(--text-primary); }
.metric-label { font-size: 13px; color: var(--text-secondary); margin: 4px 0; }
.metric-sub { font-size: 11px; color: var(--text-muted); }

.panel-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; font-size: 14px; }

.gap-list { display: flex; flex-direction: column; gap: 12px; }
.gap-item { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.gap-info { flex: 1; min-width: 0; }
.gap-name { font-size: 13px; font-weight: 500; color: var(--text-primary); margin-bottom: 4px; }
.gap-bar-wrap { display: flex; align-items: center; gap: 8px; }
.gap-bar { flex: 1; height: 6px; background: var(--bg-page); border-radius: 3px; overflow: hidden; }
.gap-fill { height: 100%; border-radius: 3px; transition: width 0.4s; }
.gap-fill.low { background: #ff4d4f; }
.gap-fill.mid { background: #faad14; }
.gap-fill.ok { background: #52c41a; }
.gap-num { font-size: 11px; color: var(--text-muted); white-space: nowrap; }

.ai-suggestions { display: flex; flex-direction: column; gap: 8px; }
.sug-item { display: flex; align-items: flex-start; gap: 8px; font-size: 12px; color: var(--text-secondary); line-height: 1.5; }
</style>

