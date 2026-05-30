<template>
  <div class="agents-page">
    <div class="page-header">
      <div>
        <h1>🤖 Agent 控制面板</h1>
        <p>7大Agent协同工作 · 实时状态监控 · 任务调度</p>
      </div>
      <el-button type="primary" @click="refreshAgents" :loading="loading">刷新状态</el-button>
    </div>

    <div class="agent-grid">
      <div v-for="agent in agents" :key="agent.id" class="agent-card" :class="agent.status">
        <div class="agent-top">
          <span class="agent-icon">{{ agent.icon }}</span>
          <span class="agent-status-dot" :class="agent.status"></span>
        </div>
        <div class="agent-name">{{ agent.name }}</div>
        <div class="agent-role">{{ agent.descriptions[agent.id] }}</div>
        <div class="agent-stats">
          <div class="astat">
            <span class="astat-num">{{ agent.tasks }}</span>
            <span class="astat-label">任务</span>
          </div>
          <div class="astat">
            <span class="astat-num" style="color:#52c41a">{{ agent.successRate }}%</span>
            <span class="astat-label">成功率</span>
          </div>
        </div>
        <div class="agent-bar">
          <div class="agent-bar-fill" :style="{ width: agent.successRate + '%', background: agent.color }"></div>
        </div>
        <el-button size="small" :type="agent.status === 'active' ? 'success' : 'default'" style="width:100%;margin-top:12px" @click="toggleAgent(agent.id)" :loading="agent.toggling">
          {{ agent.status === 'active' ? '运行中' : '待机中' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { agentApi } from '@/api'

const loading = ref(false)
const agents = ref([
  { id:'master', name:'Master Agent', icon:'🧠', status:'idle', tasks:0, successRate:0, color:'#667eea', toggling:false },
  { id:'code', name:'Code Agent', icon:'💻', status:'idle', tasks:0, successRate:0, color:'#52c41a', toggling:false },
  { id:'devops', name:'DevOps Agent', icon:'⚙️', status:'idle', tasks:0, successRate:0, color:'#1890ff', toggling:false },
  { id:'vision', name:'Vision Agent', icon:'👁️', status:'idle', tasks:0, successRate:0, color:'#faad14', toggling:false },
  { id:'trend', name:'Trend Agent', icon:'📊', status:'idle', tasks:0, successRate:0, color:'#ff4d4f', toggling:false },
  { id:'memory', name:'Memory Agent', icon:'💾', status:'idle', tasks:0, successRate:0, color:'#764ba2', toggling:false },
  { id:'heal', name:'Self-Healing', icon:'🛡️', status:'idle', tasks:0, successRate:0, color:'#13c2c2', toggling:false },
])

const descriptions = {
  master: '总控调度 · 拆解任务 · 分配Agent',
  code: '代码编写 · Bug修复 · 接口生成',
  devops: '服务器管理 · Docker · Nginx · 部署',
  vision: '图片识别 · 视频分析 · OCR',
  trend: '热点监控 · 舆情分析 · 趋势预测',
  memory: '长期记忆 · 知识检索 · 经验学习',
  heal: '异常检测 · 自动修复 · 服务恢复',
}

async function refreshAgents() {
  loading.value = true
  try {
    const { data } = await agentApi.get('/agent/collab/agents')
    if (data && data.agents) {
      data.agents.forEach(a => {
        const local = agents.value.find(x => x.id === a.id)
        if (local) {
          local.status = a.status || 'idle'
          local.tasks = a.tasks || 0
          local.successRate = a.successRate || 0
        }
      })
    }
  } catch {
    // 降级: 从lifeform状态推断
    try {
      const { data } = await agentApi.get('/agent/lifeform/status')
      if (data) {
        agents.value.forEach(a => {
          a.status = data.running ? 'active' : 'idle'
          a.tasks = data.cycle_count || 0
          a.successRate = Math.round((data.mood_score || 0.75) * 100)
        })
      }
    } catch {}
  }
  loading.value = false
}

async function toggleAgent(id) {
  const agent = agents.value.find(a => a.id === id)
  if (!agent) return
  agent.toggling = true
  try {
    await agentApi.post('/agent/collab/toggle', { agent_id: id })
    agent.status = agent.status === 'active' ? 'idle' : 'active'
  } catch {
    // 降级: 本地切换
    agent.status = agent.status === 'active' ? 'idle' : 'active'
  }
  agent.toggling = false
}

onMounted(refreshAgents)
</script>
<style scoped>
.agents-page { padding: 24px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.page-header h1 { font-size: 20px; margin: 0 0 4px; color: var(--text-primary); }
.page-header p { font-size: 13px; color: var(--text-muted); margin: 0; }
.agent-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }
.agent-card {
  background: rgba(22,33,62,0.7); border: 1px solid var(--border-color);
  border-radius: 12px; padding: 20px; transition: all 0.2s;
}
.agent-card:hover { border-color: var(--border-glow); box-shadow: var(--shadow-glow); }
.agent-card.active { border-color: rgba(82,196,26,0.2); }
.agent-card.idle { opacity: 0.7; }
.agent-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.agent-icon { font-size: 28px; }
.agent-status-dot { width: 10px; height: 10px; border-radius: 50%; }
.agent-status-dot.active { background: #52c41a; box-shadow: 0 0 8px rgba(82,196,26,0.5); animation: glowPulse 2s infinite; }
.agent-status-dot.idle { background: #5a6080; }
.agent-name { font-size: 15px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }
.agent-role { font-size: 11px; color: var(--text-muted); margin-bottom: 16px; line-height: 1.4; }
.agent-stats { display: flex; gap: 24px; margin-bottom: 12px; }
.astat { display: flex; flex-direction: column; }
.astat-num { font-size: 20px; font-weight: 700; color: var(--text-primary); }
.astat-label { font-size: 10px; color: var(--text-muted); }
.agent-bar { height: 4px; background: var(--bg-hover); border-radius: 2px; overflow: hidden; }
.agent-bar-fill { height: 100%; border-radius: 2px; transition: width 0.6s; }
@keyframes glowPulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
@media (max-width: 768px) { .agents-page { padding: 12px; } .agent-grid { grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 10px; } .agent-card { padding: 14px; } }
</style>