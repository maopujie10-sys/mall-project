<template>
  <div class="agents-page">
    <div class="page-header">
      <div>
        <h1>馃 Agent 鎺у埗闈㈡澘</h1>
        <p>7澶gent鍗忓悓宸ヤ綔 路 瀹炴椂鐘舵€佺洃鎺?路 浠诲姟璋冨害</p>
      </div>
    </div>

    <!-- Agent缃戞牸 -->
    <div class="agent-grid">
      <div v-for="agent in agents" :key="agent.id" class="agent-card" :class="agent.status">
        <div class="agent-top">
          <span class="agent-icon">{{ agent.icon }}</span>
          <span class="agent-status-dot" :class="agent.status"></span>
        </div>
        <div class="agent-name">{{ agent.name }}</div>
        <div class="agent-role">{{ agentDescriptions[agent.id] }}</div>
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
        <el-button size="small" :type="agent.status === 'active' ? 'success' : 'default'" style="width:100%;margin-top:12px" @click="toggleAgent(agent.id)">
          {{ agent.status === 'active' ? '运行中' : '待机中' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const agentDescriptions = {
  master: '总控调度 · 拆解任务 · 分配Agent',
  code: '代码编写 · Bug修复 · 接口生成',
  devops: '服务器管理 · Docker · Nginx · 部署',
  vision: '图片识别 · 视频分析 · OCR',
  trend: '热点监控 · 舆情分析 · 趋势预测',
  memory: '长期记忆 · 知识检索 · 经验学习',
  heal: '异常检测 · 自动修复 · 服务恢复',
}

const agents = ref([
  { id:'master', name:'Master Agent', icon:'🧠', status:'active', tasks:156, successRate:98.2, color:'#667eea' },
  { id:'code', name:'Code Agent', icon:'💻', status:'active', tasks:89, successRate:94.5, color:'#52c41a' },
  { id:'devops', name:'DevOps Agent', icon:'⚙️', status:'active', tasks:234, successRate:99.1, color:'#1890ff' },
  { id:'vision', name:'Vision Agent', icon:'👁️', status:'idle', tasks:45, successRate:91.3, color:'#faad14' },
  { id:'trend', name:'Trend Agent', icon:'📊', status:'active', tasks:312, successRate:96.7, color:'#ff4d4f' },
  { id:'memory', name:'Memory Agent', icon:'💾', status:'active', tasks:567, successRate:99.8, color:'#764ba2' },
  { id:'heal', name:'Self-Healing', icon:'🛡️', status:'idle', tasks:23, successRate:100, color:'#13c2c2' },
])

function toggleAgent(id) {
  const a = agents.value.find(x => x.id === id)
  if (a) a.status = a.status === 'active' ? 'idle' : 'active'
}
</script>

<style scoped>
.agents-page { padding: 24px; }
.page-header { margin-bottom: 24px; }
.page-header h1 { font-size: 20px; margin: 0 0 4px; color: var(--text-primary); }
.page-header p { font-size: 13px; color: var(--text-muted); margin: 0; }

.agent-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }

.agent-card {
  background: rgba(22,33,62,0.7);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.2s;
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

@keyframes glowPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>
