<template>
  <div class="trend-page">
    <div class="page-header">
      <div>
        <h1>棣冩憲 閻戭厾鍋ｉ惄鎴炲付</h1>
        <p>鐎圭偞妞傛潻鍊熼嚋閹舵牠鐓?B缁?瀵邦喖宕?X/YouTube閻戭厾鍋?璺?AI閼奉亜濮╅崚鍡樼€界搾瀣◢</p>
      </div>
      <div class="header-actions">
        <el-select v-model="activePlatform" placeholder="楠炲啿褰? size="small" style="width:130px">
          <el-option label="閸忋劑鍎撮獮鍐插酱" value="all"/>
          <el-option label="瀵邦喖宕? value="weibo"/>
          <el-option label="閹舵牠鐓? value="douyin"/>
          <el-option label="B缁? value="bilibili"/>
          <el-option label="X/Twitter" value="twitter"/>
        </el-select>
        <el-button type="primary" size="small" @click="refreshTrends" :loading="loading">
          <el-icon><Refresh /></el-icon> 閸掗攱鏌?        </el-button>
      </div>
    </div>

    <!-- 楠炲啿褰撮悜顓犲仯閸楋紕澧?-->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="8" v-for="(pf, key) in filteredTrends" :key="key">
        <el-card shadow="never" class="trend-card" :style="{ borderTop: '2px solid ' + pf.color }">
          <template #header>
            <div class="trend-header">
              <span>{{ pf.icon }} {{ pf.name }}</span>
              <el-tag size="small">{{ pf.trends?.length || 0 }}閺?/el-tag>
            </div>
          </template>
          <div class="trend-list">
            <div v-for="t in (pf.trends || []).slice(0, 8)" :key="t.rank" class="trend-item">
              <span class="trend-rank" :class="{ top3: t.rank <= 3 }">{{ t.rank }}</span>
              <span class="trend-title">{{ t.title }}</span>
              <span class="trend-heat">{{ formatHeat(t.hot_score) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- AI閸掑棙鐎?-->
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header><span>棣冩暛 AI鐡掑濞嶆０鍕ゴ</span></template>
          <div class="predict-grid">
            <div v-for="cat in predictions" :key="cat.name" class="predict-card">
              <div class="predict-name">{{ cat.name }}</div>
              <div class="predict-items">
                <el-tag v-for="item in cat.items" :key="item" size="small" class="predict-tag">{{ item }}</el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header><span>棣冩磪 閸熷棗鐓勫楦款唴</span></template>
          <div class="suggest-list">
            <div v-for="s in suggestions" :key="s" class="suggest-item">
              <el-icon color="#667eea"><CircleCheckFilled /></el-icon>
              <span>{{ s }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { agentApi } from '@/api/index'

const loading = ref(false)
const activePlatform = ref('all')

const trends = reactive({
  douyin: { name:'鎶栭煶鐑偣', icon:'馃幍', color:'#010101', trends:[] },
  bilibili: { name:'B绔欑儹闂?, icon:'馃摵', color:'#fb7299', trends:[] },
  weibo: { name:'寰崥鐑悳', icon:'馃摍', color:'#ff4d4f', trends:[] },
})

const filteredTrends = computed(function() {
  if (activePlatform.value === 'all') {
    return Object.values(trends).flatMap(function(t) { return t.trends })
  }
  return trends[activePlatform.value]?.trends || []
})

async function fetchTrends() {
  loading.value = true
  try {
    const { data } = await agentApi.get('/agent/friday/trends')
    if (data.trends) {
      Object.keys(trends).forEach(function(key) {
        if (data.trends[key]) {
          trends[key].trends = (data.trends[key] || []).slice(0, 15).map(function(t, i) {
            return { rank: i+1, title: t.title || t.name || '', hot: t.hot || t.heat || 0, url: t.url || '' }
          })
        }
      })
    }
  } catch {
    ElMessage.error('鑾峰彇鐑偣鏁版嵁澶辫触')
  } finally {
    loading.value = false
  }
}

function setPlatform(platform) { activePlatform.value = platform }
function refreshTrends() { fetchTrends() }

onMounted(function() { fetchTrends() })
</script>

<style scoped>
.trend-page { padding: 24px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.page-header h1 { font-size: 20px; margin: 0 0 4px; color: var(--text-primary); }
.page-header p { font-size: 13px; color: var(--text-muted); margin: 0; }
.header-actions { display: flex; gap: 8px; }

.trend-card { border-radius: 12px; }
.trend-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; font-size: 14px; }

.trend-list { display: flex; flex-direction: column; gap: 2px; }
.trend-item { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid var(--border-color); font-size: 13px; }
.trend-item:last-child { border-bottom: none; }
.trend-rank { width: 22px; text-align: center; font-weight: 700; color: var(--text-muted); font-size: 12px; flex-shrink: 0; }
.trend-rank.top3 { color: #ff4d4f; }
.trend-title { flex: 1; color: var(--text-secondary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.trend-heat { font-size: 11px; color: var(--text-muted); white-space: nowrap; }

.predict-grid { display: flex; flex-direction: column; gap: 16px; }
.predict-card { }
.predict-name { font-size: 13px; font-weight: 600; color: var(--text-primary); margin-bottom: 8px; }
.predict-items { display: flex; gap: 6px; flex-wrap: wrap; }
.predict-tag { cursor: default; }

.suggest-list { display: flex; flex-direction: column; gap: 10px; }
.suggest-item { display: flex; align-items: flex-start; gap: 8px; font-size: 13px; color: var(--text-secondary); line-height: 1.5; }
</style>
