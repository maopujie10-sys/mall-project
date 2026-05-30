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
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)

const evoCards = [
  { icon:'馃幆', label:'30澶╂垚鍔熺巼', value:'87.5%', color:'#52c41a', bg:'rgba(82,196,26,0.1)' },
  { icon:'馃摎', label:'宸插鐭ヨ瘑', value:'156鏉?, color:'#667eea', bg:'rgba(102,126,234,0.1)' },
  { icon:'鉁忥笍', label:'鐢ㄦ埛绾犳', value:'23娆?, color:'#faad14', bg:'rgba(250,173,20,0.1)' },
  { icon:'馃搱', label:'杩涘寲瓒嬪娍', value:'鈫?涓婂崌', color:'#764ba2', bg:'rgba(118,75,162,0.1)' },
]

const trends = [
  { label:'鍟嗗搧閲囬泦', rate:92, color:'#52c41a', trend:'鈫?+3%', trendType:'success' },
  { label:'鍋ュ悍鎵弿', rate:100, color:'#667eea', trend:'鈫?鎸佸钩', trendType:'info' },
  { label:'鍟嗗搧鏇挎崲', rate:78, color:'#faad14', trend:'鈫?+5%', trendType:'success' },
  { label:'鑷姩杩愮淮', rate:85, color:'#764ba2', trend:'鈫?+2%', trendType:'success' },
  { label:'浠锋牸浼樺寲', rate:70, color:'#ff4d4f', trend:'鈫?-3%', trendType:'danger' },
]

const knowledge = [
  { category:'閲囬泦婧?, key:'eBay > 鐢靛瓙浜у搧', score:0.92, catType:'success' },
  { category:'閲囬泦婧?, key:'AliExpress > 鏈嶈', score:0.85, catType:'success' },
  { category:'鍝佺被鍋忓ソ', key:'鎵嬫満鏁扮爜 > 鐑棬', score:0.88, catType:'' },
  { category:'鍝佺被鍋忓ソ', key:'杩愬姩闉嬫湇 > 澧為暱涓?, score:0.76, catType:'' },
  { category:'鐢ㄦ埛鍋忓ソ', key:'浠锋牸鍖洪棿 楼500-2000', score:0.82, catType:'warning' },
  { category:'绾犳瀛︿範', key:'閲囬泦鏃朵繚鐣欏師濮嬭鏍?, score:0.95, catType:'danger' },
  { category:'绾犳瀛︿範', key:'鍥剧墖涓婁紶COS鍓嶅帇缂?, score:0.90, catType:'danger' },
]

const actionHistory = [
  { type:'閲囬泦', typeTag:'', name:'閲囬泦:eBay:iPhone閰嶄欢', ok:true, time:'2024-05-28 14:32' },
  { type:'鍋ュ悍', typeTag:'success', name:'鍟嗗搧鍋ュ悍搴︽壂鎻?, ok:true, time:'2024-05-28 14:15' },
  { type:'鏇挎崲', typeTag:'warning', name:'鏇挎崲鍟嗗搧:鏃ф暟鎹嚎', ok:true, time:'2024-05-28 13:08' },
  { type:'閲囬泦', typeTag:'', name:'閲囬泦:AliExpress:澶忓T鎭?, ok:false, time:'2024-05-28 12:45' },
  { type:'杩愮淮', typeTag:'danger', name:'AI鑷姩杩愮淮鎵ц', ok:true, time:'2024-05-28 11:20' },
  { type:'閲囬泦', typeTag:'', name:'閲囬泦:eBay:鏁扮爜鐩告満', ok:true, time:'2024-05-28 10:05' },
  { type:'鍋ュ悍', typeTag:'success', name:'姣忔棩鍋ュ悍鎵弿', ok:true, time:'2024-05-28 08:00' },
]

const suggestions = [
  { icon:'鈿狅笍', level:'warn', text:'浠锋牸浼樺寲鎴愬姛鐜囦粎70%锛屽缓璁涔犳洿澶氬畾浠风瓥鐣?, action:'寮€濮嬪涔? },
  { icon:'馃挕', level:'tip', text:'閲囬泦婧?AliExpress 鏃惰绫绘垚鍔熺巼涓嬮檷锛屽缓璁檷浣庝紭鍏堢骇', action:'璋冩暣' },
  { icon:'鉁?, level:'good', text:'eBay鐢靛瓙浜у搧閲囬泦琛ㄧ幇浼樺紓锛屽缓璁繚鎸佸綋鍓嶇瓥鐣? },
  { icon:'馃摑', level:'tip', text:'杩樻湁2鏉＄敤鎴风籂姝ｆ湭瀛︿範锛岃"AI瀛︿範绾犳"鏉ユ秷鍖? },
]

function refreshReport() {
  loading.value = true
  setTimeout(() => { loading.value = false; ElMessage.success('杩涘寲鎶ュ憡宸叉洿鏂?) }, 1200)
}

function handleSuggestion(sug) {
  if (sug.action === '寮€濮嬪涔?) {
    ElMessage.success('宸插紑濮嬪涔犲畾浠风瓥鐣ワ紝涓嬫浼氭洿鍑嗙‘')
  } else if (sug.action === '璋冩暣') {
    ElMessage.success('宸查檷浣?AliExpress 鏃惰绫讳紭鍏堢骇')
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
.trend-bar-wrap { flex: 1; height: 8px; background: rgba(13,16,37,0.55); border-radius: 4px; overflow: hidden; }
.trend-bar { height: 100%; border-radius: 4px; transition: width 0.6s; }
.trend-val { width: 40px; font-size: 12px; font-weight: 600; color: var(--text-primary); text-align: right; }

.knowledge-list { display: flex; flex-direction: column; gap: 10px; }
.kn-item { display: flex; align-items: center; gap: 10px; }
.kn-cat { width: 70px; flex-shrink: 0; }
.kn-key { flex: 1; font-size: 13px; color: var(--text-primary); }
.kn-score { display: flex; align-items: center; gap: 6px; width: 120px; }
.kn-score-bar { flex: 1; height: 4px; background: rgba(13,16,37,0.55); border-radius: 2px; overflow: hidden; }
.kn-score-fill { height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 2px; }
.kn-score-num { font-size: 11px; color: var(--text-muted); width: 32px; }

.evo-suggestions { display: flex; flex-direction: column; gap: 10px; }
.sug-card { display: flex; align-items: center; gap: 10px; padding: 12px; border-radius: 8px; background: rgba(13,16,37,0.55); }
.sug-card.warn { border-left: 3px solid #faad14; }
.sug-card.tip { border-left: 3px solid #667eea; }
.sug-card.good { border-left: 3px solid #52c41a; }
.sug-icon { font-size: 18px; flex-shrink: 0; }
.sug-text { flex: 1; font-size: 12px; color: var(--text-secondary); line-height: 1.5; }
.empty-hint { text-align: center; padding: 30px; color: var(--text-muted); font-size: 13px; }
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>

