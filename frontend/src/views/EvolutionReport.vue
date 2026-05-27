<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1>🧬 AI 进化报告</h1>
        <p>AI 自我评估 · 成功率趋势 · 知识积累 · 持续进化</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="refreshReport" :loading="loading">
          <el-icon><Refresh /></el-icon> 生成报告
        </el-button>
      </div>
    </div>

    <!-- 进化指标 -->
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

    <!-- 趋势 + 知识库 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header><span>📈 成功率趋势</span></template>
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
          <template #header><span>📚 知识库</span></template>
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

    <!-- 行动历史 + 纠正 -->
    <el-row :gutter="16">
      <el-col :span="14">
        <el-card shadow="never">
          <template #header><span>📋 行动历史</span></template>
          <el-table :data="actionHistory" size="small" max-height="320">
            <el-table-column prop="type" label="类型" width="90">
              <template #default="{ row }">
                <el-tag size="small" :type="row.typeTag">{{ row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="行动" min-width="150"/>
            <el-table-column prop="result" label="结果" width="80">
              <template #default="{ row }">
                <span :style="{ color: row.ok ? '#52c41a' : '#ff4d4f' }">{{ row.ok ? '✓ 成功' : '✗ 失败' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="time" label="时间" width="140"/>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="never">
          <template #header><span>💡 进化建议</span></template>
          <div class="evo-suggestions">
            <div v-for="(s, i) in suggestions" :key="i" class="sug-card" :class="s.level">
              <div class="sug-icon">{{ s.icon }}</div>
              <div class="sug-text">{{ s.text }}</div>
              <el-button v-if="s.action" text size="small" type="primary" @click="handleSuggestion(s)">{{ s.action }}</el-button>
            </div>
            <div v-if="suggestions.length === 0" class="empty-hint">暂无进化建议，AI表现良好！</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)

const evoCards = [
  { icon:'🎯', label:'30天成功率', value:'87.5%', color:'#52c41a', bg:'rgba(82,196,26,0.1)' },
  { icon:'📚', label:'已学知识', value:'156条', color:'#667eea', bg:'rgba(102,126,234,0.1)' },
  { icon:'✏️', label:'用户纠正', value:'23次', color:'#faad14', bg:'rgba(250,173,20,0.1)' },
  { icon:'📈', label:'进化趋势', value:'↗ 上升', color:'#764ba2', bg:'rgba(118,75,162,0.1)' },
]

const trends = [
  { label:'商品采集', rate:92, color:'#52c41a', trend:'↗ +3%', trendType:'success' },
  { label:'健康扫描', rate:100, color:'#667eea', trend:'→ 持平', trendType:'info' },
  { label:'商品替换', rate:78, color:'#faad14', trend:'↗ +5%', trendType:'success' },
  { label:'自动运维', rate:85, color:'#764ba2', trend:'↗ +2%', trendType:'success' },
  { label:'价格优化', rate:70, color:'#ff4d4f', trend:'↘ -3%', trendType:'danger' },
]

const knowledge = [
  { category:'采集源', key:'eBay > 电子产品', score:0.92, catType:'success' },
  { category:'采集源', key:'AliExpress > 服装', score:0.85, catType:'success' },
  { category:'品类偏好', key:'手机数码 > 热门', score:0.88, catType:'' },
  { category:'品类偏好', key:'运动鞋服 > 增长中', score:0.76, catType:'' },
  { category:'用户偏好', key:'价格区间 ¥500-2000', score:0.82, catType:'warning' },
  { category:'纠正学习', key:'采集时保留原始规格', score:0.95, catType:'danger' },
  { category:'纠正学习', key:'图片上传COS前压缩', score:0.90, catType:'danger' },
]

const actionHistory = [
  { type:'采集', typeTag:'', name:'采集:eBay:iPhone配件', ok:true, time:'2024-05-28 14:32' },
  { type:'健康', typeTag:'success', name:'商品健康度扫描', ok:true, time:'2024-05-28 14:15' },
  { type:'替换', typeTag:'warning', name:'替换商品:旧数据线', ok:true, time:'2024-05-28 13:08' },
  { type:'采集', typeTag:'', name:'采集:AliExpress:夏季T恤', ok:false, time:'2024-05-28 12:45' },
  { type:'运维', typeTag:'danger', name:'AI自动运维执行', ok:true, time:'2024-05-28 11:20' },
  { type:'采集', typeTag:'', name:'采集:eBay:数码相机', ok:true, time:'2024-05-28 10:05' },
  { type:'健康', typeTag:'success', name:'每日健康扫描', ok:true, time:'2024-05-28 08:00' },
]

const suggestions = [
  { icon:'⚠️', level:'warn', text:'价格优化成功率仅70%，建议学习更多定价策略', action:'开始学习' },
  { icon:'💡', level:'tip', text:'采集源 AliExpress 时装类成功率下降，建议降低优先级', action:'调整' },
  { icon:'✅', level:'good', text:'eBay电子产品采集表现优异，建议保持当前策略' },
  { icon:'📝', level:'tip', text:'还有2条用户纠正未学习，说"AI学习纠正"来消化' },
]

function refreshReport() {
  loading.value = true
  setTimeout(() => { loading.value = false; ElMessage.success('进化报告已更新') }, 1200)
}

function handleSuggestion(sug) {
  if (sug.action === '开始学习') {
    ElMessage.success('已开始学习定价策略，下次会更准确')
  } else if (sug.action === '调整') {
    ElMessage.success('已降低 AliExpress 时装类优先级')
  }
}
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
