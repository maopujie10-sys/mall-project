<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1>棣冾潵 AI 閸熷棗鐓勬径褑鍓?/h1>
        <p>閸忋劏鍤滈崝銊ュ瀻閺嬫劕鏅㈤崺搴′淮鎼村嘲瀹抽敍灞藉絺閻滄澘鎼х猾鑽ゅ繁閸欙綇绱濋弲楦垮厴閹恒劏宕樻潻鎰樊閺傝顢?/p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="runScan" :loading="scanning">
          <el-icon><Search /></el-icon> 閸忋劎鐝幍顐ｅ伎
        </el-button>
        <el-button type="success" @click="runAutoOps" :loading="autoRunning">
          <el-icon><Promotion /></el-icon> AI閼奉亜濮╂潻鎰樊
        </el-button>
      </div>
    </div>

    <!-- 閸嬨儱鎮嶅鍌濐潔 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6" v-for="item in summaryCards" :key="item.label">
        <el-card shadow="never" class="metric-card" :class="item.color">
          <div class="metric-num">{{ item.value }}</div>
          <div class="metric-label">{{ item.label }}</div>
          <div class="metric-sub">{{ item.sub }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 閸熷棗鎼ч崑銉ユ倣鎼达箒銆冮弽?-->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="16">
        <el-card shadow="never">
          <template #header>
            <div class="panel-header">
              <span>棣冩惓 閸熷棗鎼ч崑銉ユ倣鎼达箑鍨庨弸?/span>
              <el-select v-model="filterStatus" placeholder="缁涙盯鈧? size="small" style="width:120px">
                <el-option label="閸忋劑鍎? value="all"/>
                <el-option label="閻戭參鏀? value="hot"/>
                <el-option label="濮濓絽鐖? value="normal"/>
                <el-option label="閸愮兘妫? value="cold"/>
                <el-option label="濮濊鎼? value="dead"/>
              </el-select>
            </div>
          </template>
          <el-table :data="filteredProducts" style="width: 100%" size="small" max-height="400">
            <el-table-column prop="name" label="閸熷棗鎼ч崥宥囆? min-width="180">
              <template #default="{ row }">
                <div style="display:flex;align-items:center;gap:8px;">
                  <div :style="{ width:36,height:36,borderRadius:6,background:row.color+'22',display:'flex',alignItems:'center',justifyContent:'center',fontSize:18 }">{{ row.icon }}</div>
                  <span style="font-size:13px;">{{ row.name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="category" label="閸濅胶琚? width="100"/>
            <el-table-column prop="price" label="娴犻攱鐗? width="100"/>
            <el-table-column prop="sales" label="闁库偓闁? width="80" sortable/>
            <el-table-column prop="stock" label="鎼存挸鐡? width="80">
              <template #default="{ row }">
                <span :style="{ color: row.stock < 10 ? '#ff4d4f' : '#52c41a' }">{{ row.stock }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="閻樿埖鈧? width="90">
              <template #default="{ row }">
                <el-tag :type="row.statusType" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="閹垮秳缍? width="120">
              <template #default="{ row }">
                <el-button text size="small" type="primary" @click="handleReplace(row)">閺囨寧宕?/el-button>
                <el-button text size="small" type="danger" v-if="row.statusType==='info'" @click="handleRemove(row)">娑撳鐏?/el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 閸濅胶琚紓鍝勫經 -->
      <el-col :span="8">
        <el-card shadow="never">
          <template #header>
            <span>棣冩敵 閸濅胶琚紓鍝勫經閸掑棙鐎?/span>
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
                {{ gap.level === 'low' ? '娑撱儵鍣告稉宥堝喕' : gap.level === 'mid' ? '闂団偓鐞涖儱鍘? : '閸忓懓鍐? }}
              </el-tag>
            </div>
            <el-divider style="margin:16px 0"/>
            <div style="font-size:13px;color:var(--text-muted);margin-bottom:10px;">棣冾樆 AI瀵ら缚顔?/div>
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
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { agentApi } from '@/api/index'

const scanning = ref(false)
const autoRunning = ref(false)
const filterStatus = ref('all')

const summaryCards = reactive([
  { label: '鍟嗗搧鎬绘暟', value: 0, sub: '鍔犺浇涓?..', color: 'blue' },
  { label: '鐑攢鍟嗗搧', value: 0, sub: '鍔犺浇涓?..', color: 'red' },
  { label: '姝诲搧寰呮崲', value: 0, sub: '鍔犺浇涓?..', color: 'gray' },
  { label: '鍝佺被缂哄彛', value: 0, sub: '鍔犺浇涓?..', color: 'orange' },
])

const products = ref([])
const gaps = ref([])
const suggestions = ref([])

const filteredProducts = computed(() => {
  if (filterStatus.value === 'all') return products.value
  const map = { hot: 'hot', normal: 'warm', cold: 'cold', dead: 'dead' }
  const target = map[filterStatus.value] || filterStatus.value
  return products.value.filter(p => p.status === target)
})

function statusText(s) {
  return { hot: '鐑攢', warm: '姝ｅ父', cold: '鍐烽棬', dead: '姝诲搧' }[s] || s
}

function statusColor(s) {
  return { hot: '#ff4d4f', warm: '#52c41a', cold: '#faad14', dead: '#d9d9d9' }[s] || '#d9d9d9'
}

async function runScan() {
  scanning.value = true
  try {
    const { data } = await agentApi.post('/agent/mall-brain/scan')
    if (data.products) {
      products.value = data.products.map(function(p, i) {
        return {
          id: p.id || i + 1,
          icon: '馃摝',
          name: p.title || '鍟嗗搧',
          category: p.category || '鏈煡',
          price: '楼' + (p.price || 0),
          sales: p.sales || 0,
          stock: p.stock || 0,
          status: p.status || 'normal',
          color: statusColor(p.status),
          health_score: p.health_score || 0,
          recommendation: p.recommendation || ''
        }
      })
      const d = data.distribution || {}
      summaryCards[0].value = data.total || products.value.length
      summaryCards[1].value = d.hot || 0
      summaryCards[2].value = d.dead || 0
      summaryCards[3].value = 0
    }
    // 鑾峰彇鍝佺被缂哄彛
    try {
      const { data: gd } = await agentApi.get('/agent/mall-brain/gaps')
      gaps.value = (gd?.gaps || []).map(function(g) {
        return { name: g.category || g.name, current: g.current || 0, target: g.target || 10, percent: Math.round((g.current||0)/(g.target||1)*100), level: g.level || 'low' }
      })
      summaryCards[3].value = gaps.value.length
    } catch {}
    // 鑾峰彇AI寤鸿
    try {
      const { data: rd } = await agentApi.get('/agent/mall-brain/report')
      suggestions.value = rd?.suggestions || rd?.recommendations || []
    } catch {}
    ElMessage.success('鍏ㄧ珯鎵弿瀹屾垚锛?)
  } catch {
    ElMessage.error('鎵弿澶辫触锛岃妫€鏌ュ悗绔湇鍔?)
  } finally {
    scanning.value = false
  }
}

async function runAutoOps() {
  autoRunning.value = true
  try {
    const { data } = await agentApi.post('/agent/mall-brain/auto', { dry_run: false })
    ElMessage.success(data?.message || 'AI鑷姩杩愮淮瀹屾垚')
  } catch {
    ElMessage.error('鑷姩杩愮淮澶辫触')
  } finally {
    autoRunning.value = false
  }
}

function handleReplace(row) {
  ElMessageBox.confirm('纭瑕佷粠閲囬泦搴撲腑瀵绘壘 "' + row.name + '" 鐨勬浛浠ｅ搧鍚楋紵', '鏇挎崲鍟嗗搧', {
    confirmButtonText: '纭',
    cancelButtonText: '鍙栨秷',
  }).then(function() {
    ElMessage.success('宸插紑濮嬩负 "' + row.name + '" 瀵绘壘鏇夸唬鍝?)
  }).catch(function() {})
}

function handleRemove(row) {
  ElMessageBox.confirm('纭瑕佷笅鏋?"' + row.name + '" 鍚楋紵璇ユ搷浣滀細鑷姩澶囦唤銆?, '涓嬫灦鍟嗗搧', {
    confirmButtonText: '纭涓嬫灦',
    cancelButtonText: '鍙栨秷',
    type: 'warning',
  }).then(function() {
    ElMessage.success('"' + row.name + '" 宸蹭笅鏋?)
  }).catch(function() {})
}

onMounted(function() {
  runScan()
})
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
