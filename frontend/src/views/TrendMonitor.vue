<template>
  <div class="trend-page">
    <div class="page-header">
      <div>
        <h1>📡 热点监控</h1>
        <p>实时追踪抖音/B站/微博/X/YouTube热点 · AI自动分析趋势</p>
      </div>
      <div class="header-actions">
        <el-select v-model="activePlatform" placeholder="平台" size="small" style="width:130px">
          <el-option label="全部平台" value="all"/>
          <el-option label="微博" value="weibo"/>
          <el-option label="抖音" value="douyin"/>
          <el-option label="B站" value="bilibili"/>
          <el-option label="X/Twitter" value="twitter"/>
        </el-select>
        <el-button type="primary" size="small" @click="refreshTrends" :loading="loading">
          <el-icon><Refresh /></el-icon> 刷新
        </el-button>
      </div>
    </div>

    <!-- 平台热点卡片 -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="8" v-for="(pf, key) in filteredTrends" :key="key">
        <el-card shadow="never" class="trend-card" :style="{ borderTop: '2px solid ' + pf.color }">
          <template #header>
            <div class="trend-header">
              <span>{{ pf.icon }} {{ pf.name }}</span>
              <el-tag size="small">{{ pf.trends?.length || 0 }}条</el-tag>
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

    <!-- AI分析 -->
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header><span>🔮 AI趋势预测</span></template>
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
          <template #header><span>🛒 商城建议</span></template>
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
  weibo: { name:'微博热搜', icon:'📢', color:'#ff4d4f', trends:[] },
  douyin: { name:'抖音热点', icon:'🎵', color:'#010101', trends:[] },
  bilibili: { name:'B站热门', icon:'📺', color:'#fb7299', trends:[] },
})

const filteredTrends = computed(() => {
  if (activePlatform.value === 'all') return trends
  const filtered = {}
  if (trends[activePlatform.value]) filtered[activePlatform.value] = trends[activePlatform.value]
  return filtered
})

const predictions = ref([])
const suggestions = ref([])

function formatHeat(n) {
  if (!n) return ''
  if (n > 1000000) return (n/10000).toFixed(0) + '万'
  return (n/10000).toFixed(1) + '万'
}

async function refreshTrends() {
  loading.value = true
  try {
    const res = await agentApi.get('/agent/friday/trends')
    if (res?.data?.ok && res?.data?.trends) {
      Object.keys(trends).forEach(key => {
        if (res.data.trends[key]) {
          trends[key].trends = res.data.trends[key].map((t, i) => ({
            rank: i + 1,
            title: t.title || t.name || '',
            hot_score: t.hot_score || t.heat || 0,
          }))
        }
      })
    }
    // 获取预测数据
    const predRes = await agentApi.get('/agent/friday/trends/predict', { params: { category: '科技' } })
    if (predRes?.data?.ok && predRes?.data?.predictions) {
      predictions.value = [{ name:'AI预测', items: predRes.data.predictions.slice(0, 6) }]
    } else {
      predictions.value = []
    }
    ElMessage.success('热点已更新')
  } catch {
    ElMessage.error('获取热点数据失败')
  }
  loading.value = false
}

onMounted(refreshTrends)
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

