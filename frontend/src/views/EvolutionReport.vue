<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1>馃К AI 杩涘寲鎶ュ憡</h1>
        <p>AI 鑷垜璇勪及 路 鎴愬姛鐜囪秼鍔?路 鐭ヨ瘑绉疮 路 鎸佺画杩涘寲</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="refreshReport" :loading="loading">
          <el-icon><Refresh /></el-icon> 鐢熸垚鎶ュ憡
        </el-button>
      </div>
    </div>

    <!-- 杩涘寲鎸囨爣 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6" v-for="card in evoCards" :key="card.label">
        <el-card shadow="never" class="evo-card">
          <div class="evo-icon-wrap" :style="{ background: card.bg }">
            <span class="evo-emoji">{{ card.icon }}</span>
          </div>
          <div class="evo-card-info">
            <div class="evo-card-value" :style="{ color: card.color }">{{ card.value }}</div>
            <div class="evo-card-label">{{ card.label }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 瓒嬪娍 + 鐭ヨ瘑搴?-->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header><span>馃搱 鎴愬姛鐜囪秼鍔?/span></template>
          <div class="trend-chart">
            <div class="trend-row" v-for="item in trends" :key="item.label">
              <div class="trend-label">{{ item.label }}</div>
              <div class="trend-bar-wrap">
                <div class="trend-bar" :style="{ width: item.rate + '%', background: item.color }"></div>
              </div>
              <div class="trend-val">{{ item.rate }}%</div>
              <el-tag :type="item.trendType" size="small">{{ item.trend }}</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header><span>馃摎 鐭ヨ瘑搴?/span></template>
          <div class="knowledge-list">
            <div v-for="k in knowledge" :key="k.key" class="kn-item">
              <div class="kn-cat">
                <el-tag size="small" :type="k.catType">{{ k.category }}</el-tag>
              </div>
              <div class="kn-key">{{ k.key }}</div>
              <div class="kn-score">
                <div class="kn-score-bar">
                  <div class="kn-score-fill" :style="{ width: (k.score * 100) + '%' }"></div>
                </div>
                <span class="kn-score-num">{{ Math.round(k.score * 100) }}%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 琛屽姩鍘嗗彶 + 绾犳 -->
    <el-row :gutter="16">
      <el-col :span="14">
        <el-card shadow="never">
          <template #header><span>馃搵 琛屽姩鍘嗗彶</span></template>
          <el-table :data="actionHistory" size="small" max-height="320">
            <el-table-column prop="type" label="绫诲瀷" width="90">
              <template #default="{ row }">
                <el-tag size="small" :type="row.typeTag">{{ row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="琛屽姩" min-width="150"/>
            <el-table-column prop="result" label="缁撴灉" width="80">
              <template #default="{ row }">
                <span :style="{ color: row.ok ? '#52c41a' : '#ff4d4f' }">{{ row.ok ? '鉁?鎴愬姛' : '鉁?澶辫触' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="time" label="鏃堕棿" width="140"/>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="never">
          <template #header><span>馃挕 杩涘寲寤鸿</span></template>
          <div class="evo-suggestions">
            <div v-for="(s, i) in suggestions" :key="i" class="sug-card" :class="s.level">
              <div class="sug-icon">{{ s.icon }}</div>
              <div class="sug-text">{{ s.text }}</div>
              <el-button v-if="s.action" text size="small" type="primary" @click="handleSuggestion(s)">{{ s.action }}</el-button>
            </div>
            <div v-if="suggestions.length === 0" class="empty-hint">鏆傛棤杩涘寲寤鸿锛孉I琛ㄧ幇鑹ソ锛?/div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { agentApi } from '@/api/index'

const loading = ref(false)

const evoCards = reactive([
  { icon:'🧬', label:'30天成功率', value:'0%', color:'#52c41a', bg:'rgba(82,196,26,0.1)' },
  { icon:'📎', label:'已学知识', value:'0', color:'#667eea', bg:'rgba(102,126,234,0.1)' },
  { icon:'✏️', label:'用户纠正', value:'0', color:'#faad14', bg:'rgba(250,173,20,0.1)' },
  { icon:'📱', label:'进化趋势', value:'加载中...', color:'#764ba2', bg:'rgba(118,75,162,0.1)' },
])

const trends = ref([])
const knowledge = ref([])
const actionHistory = ref([])
const suggestions = ref([])

async function fetchReport() {
  loading.value = true
  try {
    // 获取进化统计
    const { data: st } = await agentApi.get('/agent/evolution/stats')
    evoCards[0].value = (st.success_rate_7d || 0) + '%'
    evoCards[3].value = (st.success_rate_7d || 0) > 70 ? '↗ 上升' : '→ 稳定'
    if (st.motto) evoCards[3].value = st.motto

    // 获取知识库
    const { data: kb } = await agentApi.get('/agent/evolution/knowledge')
    if (Array.isArray(kb.knowledge)) {
      knowledge.value = kb.knowledge.map(function(k) { return { category:k.category||'知识', key:k.key||k.value||'', score:k.score||k.avg_score||0, catType:k.score>0.8?'success':k.score>0.5?'':'warning' } })
      evoCards[1].value = kb.knowledge.length + ''
    }

    // 获取纠正
    const { data: corr } = await agentApi.get('/agent/evolution/corrections')
    if (Array.isArray(corr.corrections)) {
      evoCards[2].value = corr.corrections.length + ''
    }

    // 获取行动历史
    const { data: mem } = await agentApi.get('/agent/evolution/memory', { params: { limit: 20 } })
    if (Array.isArray(mem.actions)) {
      actionHistory.value = mem.actions.map(function(a) {
        return { type:a.action_type||'行动', typeTag:'', name:a.description||a.action||'', ok:a.success!==false, time:a.created_at||'' }
      })
    }

    // 获取进化报告
    const { data: report } = await agentApi.get('/agent/evolution/report')
    if (Array.isArray(report.report?.suggestions)) {
      suggestions.value = report.report.suggestions.map(function(s) {
        return { icon:'💡', level:'tip', text:s, action:'' }
      })
    }

    // 获取趋势
    if (Array.isArray(report.report?.success_trends)) {
      trends.value = report.report.success_trends.map(function(t) {
        return { label:t.name||t.category, rate:t.rate||t.value||0, color:t.rate>80?'#52c41a':t.rate>60?'#faad14':'#ff4d4f', trend:t.trend||'', trendType:t.rate>80?'success':t.rate>60?'':'danger' }
      })
    }

    ElMessage.success('进化报告已更新')
  } catch {
    ElMessage.error('获取进化数据失败')
  } finally {
    loading.value = false
  }
}

function refreshReport() { fetchReport() }

function handleSuggestion(sug) {
  if (sug.action) {
    ElMessage.success('已执行: ' + sug.text.slice(0,30))
  }
}

onMounted(function() { fetchReport() })
</script>

<style scoped>
.page-container { padding: 24px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.page-header h1 { font-size: 20px; margin: 0 0 4px; color: var(--text-primary); }
.page-header p { font-size: 13px; color: var(--text-muted); margin: 0; }
.header-actions { display: flex; gap: 8px; }

.evo-card { text-align: center; border-radius: 12px; }
.evo-icon-wrap { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; }
.evo-emoji { font-size: 24px; }
.evo-card-value { font-size: 28px; font-weight: 700; }
.evo-card-label { font-size: 12px; color: var(--text-muted); margin-top: 4px; }

.trend-chart { display: flex; flex-direction: column; gap: 16px; }
.trend-row { display: flex; align-items: center; gap: 12px; }
.trend-label { width: 80px; font-size: 13px; color: var(--text-secondary); text-align: right; flex-shrink: 0; }
.trend-bar-wrap { flex: 1; height: 8px; background: var(--bg-page); border-radius: 4px; overflow: hidden; }
.trend-bar { height: 100%; border-radius: 4px; transition: width 0.6s; }
.trend-val { width: 40px; font-size: 12px; font-weight: 600; color: var(--text-primary); text-align: right; }

.knowledge-list { display: flex; flex-direction: column; gap: 10px; }
.kn-item { display: flex; align-items: center; gap: 10px; }
.kn-cat { width: 70px; flex-shrink: 0; }
.kn-key { flex: 1; font-size: 13px; color: var(--text-primary); }
.kn-score { display: flex; align-items: center; gap: 6px; width: 120px; }
.kn-score-bar { flex: 1; height: 4px; background: var(--bg-page); border-radius: 2px; overflow: hidden; }
.kn-score-fill { height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 2px; }
.kn-score-num { font-size: 11px; color: var(--text-muted); width: 32px; }

.evo-suggestions { display: flex; flex-direction: column; gap: 10px; }
.sug-card { display: flex; align-items: center; gap: 10px; padding: 12px; border-radius: 8px; background: var(--bg-page); }
.sug-card.warn { border-left: 3px solid #faad14; }
.sug-card.tip { border-left: 3px solid #667eea; }
.sug-card.good { border-left: 3px solid #52c41a; }
.sug-icon { font-size: 18px; flex-shrink: 0; }
.sug-text { flex: 1; font-size: 12px; color: var(--text-secondary); line-height: 1.5; }
.empty-hint { text-align: center; padding: 30px; color: var(--text-muted); font-size: 13px; }
</style>
