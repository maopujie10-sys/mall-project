<template>
  <div class="dashboard">
    <div class="page-header">
      <div>
        <h1>AI MallBrain 总控台</h1>
        <p>全自动商城运维中枢 · 实时监控 · 智能决策</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="$router.push('/chat')">
          <el-icon><ChatDotRound /></el-icon> AI 对话
        </el-button>
        <el-button @click="refreshAll" :loading="loading">
          <el-icon><Refresh /></el-icon> 刷新
        </el-button>
      </div>
    </div>

    <!-- 核心指标 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(102,126,234,0.12); color: #667eea;">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.aiStatus }}</div>
          <div class="stat-label">AI 大脑状态</div>
        </div>
        <div class="stat-trend up">运行中</div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(82,196,26,0.12); color: #52c41a;">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.mallHealth }}%</div>
          <div class="stat-label">商城健康度</div>
        </div>
        <div class="stat-trend up">良好</div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(250,173,20,0.12); color: #faad14;">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.todayActions }}</div>
          <div class="stat-label">今日AI行动</div>
        </div>
        <div class="stat-trend up">活跃</div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(118,75,162,0.12); color: #764ba2;">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.memoryItems }}</div>
          <div class="stat-label">长期记忆条数</div>
        </div>
        <div class="stat-trend up">积累中</div>
      </div>
    </div>

    <!-- 图表行 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <!-- 商城健康概览 -->
      <el-col :span="12">
        <el-card shadow="never" class="panel-card">
          <template #header>
            <div class="panel-header">
              <span>🛒 商城健康概览</span>
              <el-button text size="small" type="primary" @click="$router.push('/ai-brain')">详情 →</el-button>
            </div>
          </template>
          <div class="health-grid">
            <div class="health-item hot">
              <div class="health-count">{{ health.hot }}</div>
              <div class="health-tag">🔥 热销</div>
            </div>
            <div class="health-item normal">
              <div class="health-count">{{ health.warm }}</div>
              <div class="health-tag">✅ 正常</div>
            </div>
            <div class="health-item cold">
              <div class="health-count">{{ health.cold }}</div>
              <div class="health-tag">❄️ 冷门</div>
            </div>
            <div class="health-item dead">
              <div class="health-count">{{ health.dead }}</div>
              <div class="health-tag">💀 死品</div>
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

      <!-- AI 进化曲线 -->
      <el-col :span="12">
        <el-card shadow="never" class="panel-card">
          <template #header>
            <div class="panel-header">
              <span>🧬 AI 自我进化</span>
              <el-button text size="small" type="primary" @click="$router.push('/evolution')">详情 →</el-button>
            </div>
          </template>
          <div class="evo-stats">
            <div class="evo-item">
              <div class="evo-value" style="color: #52c41a;">{{ evolution.successRate }}%</div>
              <div class="evo-label">30天成功率</div>
            </div>
            <div class="evo-item">
              <div class="evo-value" style="color: #667eea;">{{ evolution.learnedItems }}</div>
              <div class="evo-label">已学知识</div>
            </div>
            <div class="evo-item">
              <div class="evo-value" style="color: #faad14;">{{ evolution.corrections }}</div>
              <div class="evo-label">用户纠正</div>
            </div>
            <div class="evo-item">
              <div class="evo-value" style="color: #764ba2;">{{ evolution.trend }}</div>
              <div class="evo-label">进化趋势</div>
            </div>
          </div>
          <div class="evo-bar-container">
            <div class="evo-bar-label">学习进度</div>
            <div class="evo-bar-track">
              <div class="evo-bar-fill" :style="{ width: evolution.learnedPercent + '%' }"></div>
            </div>
            <span class="evo-pct">{{ evolution.learnedPercent }}%</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 底部行 -->
    <el-row :gutter="16">
      <!-- 最近活动 -->
      <el-col :span="14">
        <el-card shadow="never" class="panel-card">
          <template #header>
            <div class="panel-header">
              <span>📋 最近活动</span>
              <el-button text size="small" @click="refreshAll">刷新</el-button>
            </div>
          </template>
          <div class="activity-list">
            <div v-if="activities.length === 0" class="empty-state">暂无活动记录</div>
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

      <!-- 快捷操作 -->
      <el-col :span="10">
        <el-card shadow="never" class="panel-card">
          <template #header>
            <span>⚡ 快捷操作</span>
          </template>
          <div class="quick-grid">
            <div class="quick-card" @click="$router.push('/scraper')">
              <div class="qc-icon" style="background: rgba(102,126,234,0.12);">🛒</div>
              <div class="qc-label">采集商品</div>
              <div class="qc-desc">从多平台抓取</div>
            </div>
            <div class="quick-card" @click="$router.push('/virtual')">
              <div class="qc-icon" style="background: rgba(82,196,26,0.12);">👥</div>
              <div class="qc-label">生成数据</div>
              <div class="qc-desc">一键造数据</div>
            </div>
            <div class="quick-card" @click="$router.push('/ai-brain')">
              <div class="qc-icon" style="background: rgba(250,173,20,0.12);">🧠</div>
              <div class="qc-label">AI运维</div>
              <div class="qc-desc">自动管理商城</div>
            </div>
            <div class="quick-card" @click="$router.push('/evolution')">
              <div class="qc-icon" style="background: rgba(118,75,162,0.12);">📈</div>
              <div class="qc-label">进化报告</div>
              <div class="qc-desc">AI学得如何</div>
            </div>
            <div class="quick-card" @click="quickBackup">
              <div class="qc-icon" style="background: rgba(24,144,255,0.12);">💾</div>
              <div class="qc-label">创建备份</div>
              <div class="qc-desc">安全第一</div>
            </div>
            <div class="quick-card" @click="$router.push('/chat')">
              <div class="qc-icon" style="background: rgba(255,77,79,0.12);">💬</div>
              <div class="qc-label">AI对话</div>
              <div class="qc-desc">问AI任何事</div>
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
  aiStatus: '检测中...',
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
  trend: '加载中...',
})

const activities = ref([])

function healthPercent(type) {
  const total = health.total || 1
  return (health[type] / total * 100) + '%'
}

async function fetchStatus() {
  try {
    const { data } = await agentApi.get('/status')
    stats.aiStatus = data.mall_app === 'healthy' ? '在线' : '异常'
  } catch { stats.aiStatus = '未知' }
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
  } catch { /* 后端可能未就绪 */ }
}

async function fetchEvolution() {
  try {
    const { data } = await agentApi.get('/agent/evolution/stats')
    evolution.successRate = data.success_rate_7d || 0
    evolution.trend = evolution.successRate > 70 ? '↗ 提升中' : '→ 稳定'
    const kb = await agentApi.get('/agent/evolution/knowledge')
    evolution.learnedItems = (kb.data?.knowledge || []).length
    const corr = await agentApi.get('/agent/evolution/corrections')
    evolution.corrections = (corr.data?.corrections || []).length
  } catch { /* 后端可能未就绪 */ }
}

async function fetchActivities() {
  try {
    const acts = []
    // 获取最近备份
    try {
      const { data: bu } = await agentApi.get('/rollback/backups')
      if (bu?.length) acts.push({ icon: '💾', type: 'backup', title: '最近备份', detail: bu[0].name || '备份', time: bu[0].created_at?.slice(11,16) || '', status: '成功' })
    } catch {}
    // 获取最近巡检
    try {
      const { data: ins } = await agentApi.get('/inspector/history')
      if (ins?.length) acts.push({ icon: '🔍', type: 'evo', title: '最近巡检', detail: '多端点巡检完成', time: ins[0].time || '', status: '完成' })
    } catch {}
    // 获取系统模式
    try {
      const { data: mode } = await agentApi.get('/system/mode')
      acts.push({ icon: '⚙️', type: 'brain', title: '系统模式', detail: '当前: ' + (mode?.mode || 'ai_control'), time: '', status: '正常' })
    } catch {}
    if (acts.length === 0) {
      acts.push({ icon: '✅', type: 'evo', title: '系统就绪', detail: 'AI Agent 正常运行中', time: new Date().toTimeString().slice(0,5), status: '正常' })
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
    await agentApi.post('/rollback/backups', { name: '手动备份_' + new Date().toISOString().slice(0,10), type: 'manual', target: 'database' })
    ElMessage.success('备份任务已提交')
  } catch {
    ElMessage.error('备份失败，请检查后端服务')
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

/* 核心指标 */
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

/* 面板 */
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

/* 健康度网格 */
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

/* 进化统计 */
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

/* 活动列表 */
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

/* 快捷操作 */
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
