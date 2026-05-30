<template>
  <div class="page-container">

    <div class="page-header">
      <div>
        <h1>馃 AI 鍟嗗煄澶ц剳</h1>
        <p>鍏ㄨ嚜鍔ㄥ垎鏋愬晢鍩庡仴搴峰害锛屽彂鐜板搧绫荤己鍙ｏ紝鏅鸿兘鎺ㄨ崘杩愮淮鏂规</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="runScan" :loading="scanning">
          <el-icon><Search /></el-icon> 鍏ㄧ珯鎵弿
        </el-button>
        <el-button type="success" @click="runAutoOps" :loading="autoRunning">
          <el-icon><Promotion /></el-icon> AI鑷姩杩愮淮
        </el-button>
      </div>
    </div>

    <!-- 鍋ュ悍姒傝 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6" v-for="item in summaryCards" :key="item.label">
        <el-card shadow="never" class="metric-card" :class="item.color">
          <div class="metric-num">{{ item.value }}</div>
          <div class="metric-label">{{ item.label }}</div>
          <div class="metric-sub">{{ item.sub }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 鍟嗗搧鍋ュ悍搴﹁〃鏍?-->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="16">
        <el-card shadow="never">
          <template #header>
            <div class="panel-header">
              <span>馃搳 鍟嗗搧鍋ュ悍搴﹀垎鏋?/span>
              <el-select v-model="filterStatus" placeholder="绛涢€? size="small" style="width:120px">
                <el-option label="鍏ㄩ儴" value="all"/>
                <el-option label="鐑攢" value="hot"/>
                <el-option label="姝ｅ父" value="normal"/>
                <el-option label="鍐烽棬" value="cold"/>
                <el-option label="姝诲搧" value="dead"/>
              </el-select>
            </div>
          </template>
          <el-table :data="filteredProducts" style="width: 100%" size="small" max-height="400">
            <el-table-column prop="name" label="鍟嗗搧鍚嶇О" min-width="180">
              <template #default="{ row }">
                <div style="display:flex;align-items:center;gap:8px;">
                  <div :style="{ width:36,height:36,borderRadius:6,background:row.color+'22',display:'flex',alignItems:'center',justifyContent:'center',fontSize:18 }">{{ row.icon }}</div>
                  <span style="font-size:13px;">{{ row.name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="category" label="鍝佺被" width="100"/>
            <el-table-column prop="price" label="浠锋牸" width="100"/>
            <el-table-column prop="sales" label="閿€閲? width="80" sortable/>
            <el-table-column prop="stock" label="搴撳瓨" width="80">
              <template #default="{ row }">
                <span :style="{ color: row.stock < 10 ? '#ff4d4f' : '#52c41a' }">{{ row.stock }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="鐘舵€? width="90">
              <template #default="{ row }">
                <el-tag :type="row.statusType" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="鎿嶄綔" width="120">
              <template #default="{ row }">
                <el-button text size="small" type="primary" @click="handleReplace(row)">鏇挎崲</el-button>
                <el-button text size="small" type="danger" v-if="row.statusType==='info'" @click="handleRemove(row)">涓嬫灦</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 鍝佺被缂哄彛 -->
      <el-col :span="8">
        <el-card shadow="never">
          <template #header>
            <span>馃攳 鍝佺被缂哄彛鍒嗘瀽</span>
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
                {{ gap.level === 'low' ? '涓ラ噸涓嶈冻' : gap.level === 'mid' ? '闇€琛ュ厖' : '鍏呰冻' }}
              </el-tag>
            </div>
            <el-divider style="margin:16px 0"/>
            <div style="font-size:13px;color:var(--text-muted);margin-bottom:10px;">馃 AI寤鸿</div>
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
  { label: '鍟嗗搧鎬绘暟', value: 68, sub: '涓湪绾垮晢鍝?, color: 'blue' },
  { label: '鐑攢鍟嗗搧', value: 12, sub: '馃敟 楂樻椿璺?, color: 'red' },
  { label: '姝诲搧寰呮崲', value: 3, sub: '馃拃 闇€鏇挎崲', color: 'gray' },
  { label: '鍝佺被缂哄彛', value: 4, sub: '鈿?闇€琛ュ厖', color: 'orange' },
]

const products = reactive([
  { id:1, icon:'馃摫', name:'iPhone 15 Pro Max 256GB', category:'鎵嬫満鏁扮爜', price:'楼8,999', sales:234, stock:45, status:'鐑攢', statusType:'danger', color:'#ff4d4f' },
  { id:2, icon:'馃帶', name:'AirPods Pro 2浠?, category:'鎵嬫満鏁扮爜', price:'楼1,699', sales:189, stock:23, status:'鐑攢', statusType:'danger', color:'#ff4d4f' },
  { id:3, icon:'馃捇', name:'MacBook Air M3 15瀵?, category:'鐢佃剳鍔炲叕', price:'楼9,499', sales:156, stock:12, status:'姝ｅ父', statusType:'success', color:'#52c41a' },
  { id:4, icon:'馃憻', name:'Nike Air Max 270', category:'杩愬姩闉嬫湇', price:'楼899', sales:67, stock:88, status:'姝ｅ父', statusType:'success', color:'#52c41a' },
  { id:5, icon:'鈱?, name:'Apple Watch Ultra 2', category:'鎵嬫満鏁扮爜', price:'楼5,999', sales:45, stock:18, status:'姝ｅ父', statusType:'success', color:'#52c41a' },
  { id:6, icon:'馃幃', name:'PS5 Slim 鏁板瓧鐗?, category:'娓告垙璁惧', price:'楼2,999', sales:12, stock:55, status:'鍐烽棬', statusType:'warning', color:'#faad14' },
  { id:7, icon:'馃摲', name:'Canon EOS R6 Mark II', category:'鎽勫奖鎽勫儚', price:'楼15,999', sales:5, stock:8, status:'鍐烽棬', statusType:'warning', color:'#faad14' },
  { id:8, icon:'馃Ц', name:'Jellycat 姣涚粧鍏?30cm', category:'姣嶅┐鐜╁叿', price:'楼259', sales:0, stock:120, status:'姝诲搧', statusType:'info', color:'#d9d9d9' },
])

const gaps = [
  { name:'姣嶅┐鐜╁叿', current:1, target:8, percent:12, level:'low' },
  { name:'缇庡鎶よ偆', current:2, target:10, percent:20, level:'low' },
  { name:'椋熷搧楗枡', current:3, target:10, percent:30, level:'mid' },
  { name:'瀹跺眳鐢熸椿', current:5, target:12, percent:42, level:'mid' },
  { name:'杩愬姩鎴峰', current:8, target:12, percent:67, level:'ok' },
  { name:'鎵嬫満鏁扮爜', current:15, target:15, percent:100, level:'ok' },
]

const suggestions = [
  '姣嶅┐鐜╁叿浠?浠跺晢鍝侊紝寤鸿浠?eBay 閲囬泦琛ュ厖',
  '缇庡鎶よ偆涓ラ噸涓嶈冻锛屽缓璁噰闆嗛煩鍥界編濡嗗搧鐗?,
  '鍙戠幇3浠舵鍝佽秴杩?0澶╅浂閿€閲忥紝寤鸿涓嬫灦鏇挎崲',
]

const filteredProducts = computed(() => {
  if (filterStatus.value === 'all') return products
  const map = { hot:'鐑攢', normal:'姝ｅ父', cold:'鍐烽棬', dead:'姝诲搧' }
  return products.filter(p => p.status === map[filterStatus.value])
})

async function runScan() {
  scanning.value = true
  await new Promise(r => setTimeout(r, 1500))
  scanning.value = false
  ElMessage.success('鍏ㄧ珯鎵弿瀹屾垚锛佸彂鐜?3 浠舵鍝侊紝4 涓搧绫荤己鍙?)
}

async function runAutoOps() {
  autoRunning.value = true
  await new Promise(r => setTimeout(r, 2000))
  autoRunning.value = false
  ElMessage.success('AI鑷姩杩愮淮瀹屾垚锛氫笅鏋?浠舵鍝侊紝閲囬泦8浠舵柊鍝侊紝琛ュ厖搴撳瓨12浠?)
}

function handleReplace(row) {
  ElMessageBox.confirm(`纭瑕佷粠閲囬泦搴撲腑瀵绘壘 "${row.name}" 鐨勬浛浠ｅ搧鍚楋紵`, '鏇挎崲鍟嗗搧', {
    confirmButtonText: '纭',
    cancelButtonText: '鍙栨秷',
  }).then(() => {
    ElMessage.success(`宸插紑濮嬩负 "${row.name}" 瀵绘壘鏇夸唬鍝乣)
  }).catch(() => {})
}

function handleRemove(row) {
  ElMessageBox.confirm(`纭瑕佷笅鏋?"${row.name}" 鍚楋紵璇ユ搷浣滀細鑷姩澶囦唤銆俙, '涓嬫灦鍟嗗搧', {
    confirmButtonText: '纭涓嬫灦',
    cancelButtonText: '鍙栨秷',
    type: 'warning',
  }).then(() => {
    ElMessage.success(`"${row.name}" 宸蹭笅鏋禶)
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
.gap-bar { flex: 1; height: 6px; background: rgba(13,16,37,0.55); border-radius: 3px; overflow: hidden; }
.gap-fill { height: 100%; border-radius: 3px; transition: width 0.4s; }
.gap-fill.low { background: #ff4d4f; }
.gap-fill.mid { background: #faad14; }
.gap-fill.ok { background: #52c41a; }
.gap-num { font-size: 11px; color: var(--text-muted); white-space: nowrap; }

.ai-suggestions { display: flex; flex-direction: column; gap: 8px; }
.sug-item { display: flex; align-items: flex-start; gap: 8px; font-size: 12px; color: var(--text-secondary); line-height: 1.5; }
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>

