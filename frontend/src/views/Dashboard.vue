<template>
  <div class="dashboard">
    <div class="page-header">
      <div>
        <h1>AI MallBrain 鎬绘帶鍙?/h1>
        <p>鍏ㄨ嚜鍔ㄥ晢鍩庤繍缁翠腑鏋?路 瀹炴椂鐩戞帶 路 鏅鸿兘鍐崇瓥</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="$router.push('/chat')">
          <el-icon><ChatDotRound /></el-icon> AI 瀵硅瘽
        </el-button>
        <el-button @click="refreshAll" :loading="loading">
          <el-icon><Refresh /></el-icon> 鍒锋柊
        </el-button>
      </div>
    </div>

    <!-- 鏍稿績鎸囨爣 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(102,126,234,0.12); color: #667eea;">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.aiStatus }}</div>
          <div class="stat-label">AI 澶ц剳鐘舵€?/div>
        </div>
        <div class="stat-trend up">杩愯涓?/div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(82,196,26,0.12); color: #52c41a;">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.mallHealth }}%</div>
          <div class="stat-label">鍟嗗煄鍋ュ悍搴?/div>
        </div>
        <div class="stat-trend up">鑹ソ</div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(250,173,20,0.12); color: #faad14;">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.todayActions }}</div>
          <div class="stat-label">浠婃棩AI琛屽姩</div>
        </div>
        <div class="stat-trend up">娲昏穬</div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(118,75,162,0.12); color: #764ba2;">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.memoryItems }}</div>
          <div class="stat-label">闀挎湡璁板繂鏉℃暟</div>
        </div>
        <div class="stat-trend up">绉疮涓?/div>
      </div>
    </div>

    <!-- 鍥捐〃琛?-->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <!-- 鍟嗗煄鍋ュ悍姒傝 -->
      <el-col :span="12">
        <el-card shadow="never" class="panel-card">
          <template #header>
            <div class="panel-header">
              <span>馃洅 鍟嗗煄鍋ュ悍姒傝</span>
              <el-button text size="small" type="primary" @click="$router.push('/ai-brain')">璇︽儏 鈫?/el-button>
            </div>
          </template>
          <div class="health-grid">
            <div class="health-item hot">
              <div class="health-count">{{ health.hot }}</div>
              <div class="health-tag">馃敟 鐑攢</div>
            </div>
            <div class="health-item normal">
              <div class="health-count">{{ health.warm }}</div>
              <div class="health-tag">鉁?姝ｅ父</div>
            </div>
            <div class="health-item cold">
              <div class="health-count">{{ health.cold }}</div>
              <div class="health-tag">鉂勶笍 鍐烽棬</div>
            </div>
            <div class="health-item dead">
              <div class="health-count">{{ health.dead }}</div>
              <div class="health-tag">馃拃 姝诲搧</div>
            </div>
          </div>
          <div class="health-bar">
            <div class="bar-seg hot" :style="{ width: healthPercent('hot') }"></div>
            <div class="bar-seg normal" :style="{ width: healthPercent('warm') }"></div>
            <div class="bar-seg cold" :style="{ width: healthPercent('cold') }"></div>
            <div class="bar-seg dead" :style="{ width: healthPercent('dead') }"></div>
          </div>
        </el-card>
      </el-col>

      <!-- AI 杩涘寲鏇茬嚎 -->
      <el-col :span="12">
        <el-card shadow="never" class="panel-card">
          <template #header>
            <div class="panel-header">
              <span>馃К AI 鑷垜杩涘寲</span>
              <el-button text size="small" type="primary" @click="$router.push('/evolution')">璇︽儏 鈫?/el-button>
            </div>
          </template>
          <div class="evo-stats">
            <div class="evo-item">
              <div class="evo-value" style="color: #52c41a;">{{ evolution.successRate }}%</div>
              <div class="evo-label">30澶╂垚鍔熺巼</div>
            </div>
            <div class="evo-item">
              <div class="evo-value" style="color: #667eea;">{{ evolution.learnedItems }}</div>
              <div class="evo-label">宸插鐭ヨ瘑</div>
            </div>
            <div class="evo-item">
              <div class="evo-value" style="color: #faad14;">{{ evolution.corrections }}</div>
              <div class="evo-label">鐢ㄦ埛绾犳</div>
            </div>
            <div class="evo-item">
              <div class="evo-value" style="color: #764ba2;">{{ evolution.trend }}</div>
              <div class="evo-label">杩涘寲瓒嬪娍</div>
            </div>
          </div>
          <div class="evo-bar-container">
            <div class="evo-bar-label">瀛︿範杩涘害</div>
            <div class="evo-bar-track">
              <div class="evo-bar-fill" :style="{ width: evolution.learnedPercent + '%' }"></div>
            </div>
            <span class="evo-pct">{{ evolution.learnedPercent }}%</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 搴曢儴琛?-->
    <el-row :gutter="16">
      <!-- 鏈€杩戞椿鍔?-->
      <el-col :span="14">
        <el-card shadow="never" class="panel-card">
          <template #header>
            <div class="panel-header">
              <span>馃搵 鏈€杩戞椿鍔?/span>
              <el-button text size="small" @click="refreshAll">鍒锋柊</el-button>
            </div>
          </template>
          <div class="activity-list">
            <div v-if="activities.length === 0" class="empty-state">鏆傛棤娲诲姩璁板綍</div>
            <div v-for="act in activities" :key="act.id" class="activity-item">
              <div class="act-icon" :class="act.type">
                <span>{{ act.icon }}</span>
              </div>
              <div class="act-content">
                <div class="act-title">{{ act.title }}</div>
                <div class="act-detail">{{ act.detail }}</div>
              </div>
              <div class="act-time">{{ act.time }}</div>
              <el-tag :type="act.statusType" size="small">{{ act.status }}</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 蹇嵎鎿嶄綔 -->
      <el-col :span="10">
        <el-card shadow="never" class="panel-card">
          <template #header>
            <span>鈿?蹇嵎鎿嶄綔</span>
          </template>
          <div class="quick-grid">
            <div class="quick-card" @click="$router.push('/scraper')">
              <div class="qc-icon" style="background: rgba(102,126,234,0.12);">馃洅</div>
              <div class="qc-label">閲囬泦鍟嗗搧</div>
              <div class="qc-desc">浠庡骞冲彴鎶撳彇</div>
            </div>
            <div class="quick-card" @click="$router.push('/virtual')">
              <div class="qc-icon" style="background: rgba(82,196,26,0.12);">馃懃</div>
              <div class="qc-label">鐢熸垚鏁版嵁</div>
              <div class="qc-desc">涓€閿€犳暟鎹?/div>
            </div>
            <div class="quick-card" @click="$router.push('/ai-brain')">
              <div class="qc-icon" style="background: rgba(250,173,20,0.12);">馃</div>
              <div class="qc-label">AI杩愮淮</div>
              <div class="qc-desc">鑷姩绠＄悊鍟嗗煄</div>
            </div>
            <div class="quick-card" @click="$router.push('/evolution')">
              <div class="qc-icon" style="background: rgba(118,75,162,0.12);">馃搱</div>
              <div class="qc-label">杩涘寲鎶ュ憡</div>
              <div class="qc-desc">AI瀛﹀緱濡備綍</div>
            </div>
            <div class="quick-card" @click="quickBackup">
              <div class="qc-icon" style="background: rgba(24,144,255,0.12);">馃捑</div>
              <div class="qc-label">鍒涘缓澶囦唤</div>
              <div class="qc-desc">瀹夊叏绗竴</div>
            </div>
            <div class="quick-card" @click="$router.push('/chat')">
              <div class="qc-icon" style="background: rgba(255,77,79,0.12);">馃挰</div>
              <div class="qc-label">AI瀵硅瘽</div>
              <div class="qc-desc">闂瓵I浠讳綍浜?/div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { agentApi } from '@/api/index'

const loading = ref(false)
let pollTimer = null

const stats = reactive({
  aiStatus: '妫€娴嬩腑...',
  mallHealth: 0,
  todayActions: 0,
  memoryItems: 0,
})

const health = reactive({
  hot: 0,
  warm: 0,
  cold: 0,
  dead: 0,
  total: 0,
})

const evolution = reactive({
  successRate: 0,
  learnedItems: 0,
  corrections: 0,
  trend: '鍔犺浇涓?..',
})

const activities = ref([])

function healthPercent(type) {
  const total = health.total || 1
  return (health[type] / total * 100) + '%'
}

async function fetchStatus() {
  try {
    const { data } = await agentApi.get('/status')
    stats.aiStatus = data.mall_app === 'healthy' ? '鍦ㄧ嚎' : '寮傚父'
  } catch { stats.aiStatus = '鏈煡' }
}

async function fetchMallHealth() {
  try {
    const { data } = await agentApi.post('/agent/mall-brain/scan')
    const d = data.distribution || {}
    health.hot = d.hot || 0
    health.warm = d.warm || 0
    health.cold = d.cold || 0
    health.dead = d.dead || 0
    health.total = data.total || (health.hot + health.warm + health.cold + health.dead)
    const ok = health.hot + health.warm
    stats.mallHealth = health.total ? Math.round(ok / health.total * 100) : 0
  } catch { /* 鍚庣鍙兘鏈氨缁?*/ }
}

async function fetchEvolution() {
  try {
    const { data } = await agentApi.get('/agent/evolution/stats')
    evolution.successRate = data.success_rate_7d || 0
    evolution.trend = evolution.successRate > 70 ? '鈫?鎻愬崌涓? : '鈫?绋冲畾'
    const kb = await agentApi.get('/agent/evolution/knowledge')
    evolution.learnedItems = (kb.data?.knowledge || []).length
    const corr = await agentApi.get('/agent/evolution/corrections')
    evolution.corrections = (corr.data?.corrections || []).length
  } catch { /* 鍚庣鍙兘鏈氨缁?*/ }
}

async function fetchActivities() {
  try {
    const acts = []
    // 鑾峰彇鏈€杩戝浠?    try {
      const { data: bu } = await agentApi.get('/rollback/backups')
      if (bu?.length) acts.push({ icon: '馃捑', type: 'backup', title: '鏈€杩戝浠?, detail: bu[0].name || '澶囦唤', time: bu[0].created_at?.slice(11,16) || '', status: '鎴愬姛' })
    } catch {}
    // 鑾峰彇鏈€杩戝贰妫€
    try {
      const { data: ins } = await agentApi.get('/inspector/history')
      if (ins?.length) acts.push({ icon: '馃攳', type: 'evo', title: '鏈€杩戝贰妫€', detail: '澶氱鐐瑰贰妫€瀹屾垚', time: ins[0].time || '', status: '瀹屾垚' })
    } catch {}
    // 鑾峰彇绯荤粺妯″紡
    try {
      const { data: mode } = await agentApi.get('/system/mode')
      acts.push({ icon: '鈿欙笍', type: 'brain', title: '绯荤粺妯″紡', detail: '褰撳墠: ' + (mode?.mode || 'ai_control'), time: '', status: '姝ｅ父' })
    } catch {}
    if (acts.length === 0) {
      acts.push({ icon: '鉁?, type: 'evo', title: '绯荤粺灏辩华', detail: 'AI Agent 姝ｅ父杩愯涓?, time: new Date().toTimeString().slice(0,5), status: '姝ｅ父' })
    }
    activities.value = acts
  } catch {}
}

async function refreshAll() {
  if (loading.value) return
  loading.value = true
  try {
    await Promise.all([fetchStatus(), fetchMallHealth(), fetchEvolution(), fetchActivities()])
    stats.todayActions += 1
  } finally {
    loading.value = false
  }
}

async function quickBackup() {
  try {
    await agentApi.post('/rollback/backups', { name: '鎵嬪姩澶囦唤_' + new Date().toISOString().slice(0,10), type: 'manual', target: 'database' })
    ElMessage.success('澶囦唤浠诲姟宸叉彁浜?)
  } catch {
    ElMessage.error('澶囦唤澶辫触锛岃妫€鏌ュ悗绔湇鍔?)
  }
}

onMounted(() => {
  refreshAll()
  pollTimer = setInterval(refreshAll, 60000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.dashboard { padding: 24px; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}
.page-header h1 { font-size: 22px; font-weight: 700; color: var(--text-primary); margin: 0 0 4px; }
.page-header p { font-size: 13px; color: var(--text-muted); margin: 0; }
.header-actions { display: flex; gap: 8px; }

/* 鏍稿績鎸囨爣 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}
.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: box-shadow 0.2s;
}
.stat-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
.stat-icon {
  width: 48px; height: 48px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.stat-info { flex: 1; min-width: 0; }
.stat-value { font-size: 28px; font-weight: 700; color: var(--text-primary); line-height: 1.2; }
.stat-label { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
.stat-trend { font-size: 11px; padding: 2px 8px; border-radius: 8px; font-weight: 500; }
.stat-trend.up { background: rgba(82,196,26,0.1); color: #52c41a; }

/* 闈㈡澘 */
.panel-card {
  border-radius: 12px;
  border: 1px solid var(--border-color);
  height: 100%;
}
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 14px;
}

/* 鍋ュ悍搴︾綉鏍?*/
.health-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}
.health-item {
  text-align: center;
  padding: 16px 8px;
  border-radius: 8px;
  background: var(--bg-page);
}
.health-item.hot { border-bottom: 3px solid #ff4d4f; }
.health-item.normal { border-bottom: 3px solid #52c41a; }
.health-item.cold { border-bottom: 3px solid #1890ff; }
.health-item.dead { border-bottom: 3px solid #d9d9d9; }
.health-count { font-size: 32px; font-weight: 700; color: var(--text-primary); }
.health-tag { font-size: 11px; color: var(--text-muted); margin-top: 4px; }

.health-bar {
  display: flex;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
  background: var(--bg-page);
}
.bar-seg.hot { background: #ff4d4f; }
.bar-seg.normal { background: #52c41a; }
.bar-seg.cold { background: #1890ff; }
.bar-seg.dead { background: #d9d9d9; }

/* 杩涘寲缁熻 */
.evo-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}
.evo-item { text-align: center; }
.evo-value { font-size: 28px; font-weight: 700; }
.evo-label { font-size: 11px; color: var(--text-muted); margin-top: 4px; }

.evo-bar-container {
  display: flex;
  align-items: center;
  gap: 10px;
}
.evo-bar-label { font-size: 11px; color: var(--text-muted); white-space: nowrap; }
.evo-bar-track {
  flex: 1;
  height: 6px;
  background: var(--bg-page);
  border-radius: 3px;
  overflow: hidden;
}
.evo-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 3px;
  transition: width 0.6s ease;
}
.evo-pct { font-size: 12px; font-weight: 600; color: var(--text-primary); }

/* 娲诲姩鍒楄〃 */
.activity-list { display: flex; flex-direction: column; }
.empty-state { text-align: center; padding: 40px; color: var(--text-muted); font-size: 13px; }
.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
}
.activity-item:last-child { border-bottom: none; }
.act-icon {
  width: 36px; height: 36px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; flex-shrink: 0;
}
.act-icon.scraper { background: rgba(102,126,234,0.1); }
.act-icon.brain { background: rgba(250,173,20,0.1); }
.act-icon.virtual { background: rgba(82,196,26,0.1); }
.act-icon.evo { background: rgba(118,75,162,0.1); }
.act-icon.backup { background: rgba(24,144,255,0.1); }
.act-content { flex: 1; min-width: 0; }
.act-title { font-size: 13px; font-weight: 500; color: var(--text-primary); }
.act-detail { font-size: 12px; color: var(--text-muted); margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.act-time { font-size: 11px; color: var(--text-muted); white-space: nowrap; }

/* 蹇嵎鎿嶄綔 */
.quick-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.quick-card {
  padding: 16px 12px;
  border-radius: 10px;
  background: var(--bg-page);
  cursor: pointer;
  text-align: center;
  transition: all 0.15s;
  border: 1px solid transparent;
}
.quick-card:hover {
  background: var(--bg-card);
  border-color: var(--color-primary-light);
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.qc-icon {
  width: 40px; height: 40px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px;
  margin: 0 auto 8px;
}
.qc-label { font-size: 13px; font-weight: 500; color: var(--text-primary); }
.qc-desc { font-size: 11px; color: var(--text-muted); margin-top: 2px; }

@media (max-width: 1200px) {
  .stats-row { grid-template-columns: repeat(2, 1fr); }
  .health-grid { grid-template-columns: repeat(2, 1fr); }
  .evo-stats { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 768px) {
  .stats-row { grid-template-columns: 1fr; }
  .quick-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
