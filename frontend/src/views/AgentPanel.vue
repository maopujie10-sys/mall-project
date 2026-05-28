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
            <span class="astat-label">浠诲姟</span>
          </div>
          <div class="astat">
            <span class="astat-num" style="color:#52c41a">{{ agent.successRate }}%</span>
            <span class="astat-label">鎴愬姛鐜?/span>
          </div>
        </div>
        <div class="agent-bar">
          <div class="agent-bar-fill" :style="{ width: agent.successRate + '%', background: agent.color }"></div>
        </div>
        <el-button size="small" :type="agent.status === 'active' ? 'success' : 'default'" style="width:100%;margin-top:12px" @click="toggleAgent(agent.id)">
          {{ agent.status === 'active' ? '杩愯涓? : '寰呮満涓? }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { agentApi } from '@/api/index'
import { ElMessage } from 'element-plus'

const agentDescriptions = {
  master: '鎬绘帶璋冨害 路 鎷嗚В浠诲姟 路 鍒嗛厤Agent',
  code: '浠ｇ爜缂栧啓 路 Bug淇 路 鎺ュ彛鐢熸垚',
  devops: '鏈嶅姟鍣ㄧ鐞?路 Docker 路 Nginx 路 閮ㄧ讲',
  vision: '鍥剧墖璇嗗埆 路 瑙嗛鍒嗘瀽 路 OCR',
  trend: '鐑偣鐩戞帶 路 鑸嗘儏鍒嗘瀽 路 瓒嬪娍棰勬祴',
  memory: '闀挎湡璁板繂 路 鐭ヨ瘑妫€绱?路 缁忛獙瀛︿範',
  heal: '寮傚父妫€娴?路 鑷姩淇 路 鏈嶅姟鎭㈠',
}

const agentColors = {
  master: '#667eea', code: '#52c41a', devops: '#1890ff',
  vision: '#faad14', trend: '#ff4d4f', memory: '#764ba2', heal: '#13c2c2'
}

const agents = ref([])

async function fetchAgents() {
  try {
    const { data } = await agentApi.get('/agent/friday/agents')
    if (Array.isArray(data.agents)) {
      agents.value = data.agents.map(function(a) {
        return {
          id: a.id || a.name,
          name: a.display_name || a.name || '',
          icon: '馃',
          status: a.status || 'active',
          tasks: a.tasks || 0,
          successRate: a.success_rate || 0,
          color: agentColors[a.id] || '#667eea'
        }
      })
    }
  } catch {
    agents.value = Object.keys(agentDescriptions).map(function(id) {
      return { id, name: id.charAt(0).toUpperCase()+id.slice(1)+' Agent', icon:'馃', status:'active', tasks:0, successRate:0, color:agentColors[id]||'#667eea' }
    })
  }
}

function toggleAgent(id) {
  const a = agents.value.find(function(x) { return x.id === id })
  if (a) a.status = a.status === 'active' ? 'idle' : 'active'
}

onMounted(function() { fetchAgents() })
</script>

<style scoped>
.agents-page { padding: 24px; }
.page-header { margin-bottom: 24px; }
.page-header h1 { font-size: 20px; margin: 0 0 4px; color: var(--text-primary); }
.page-header p { font-size: 13px; color: var(--text-muted); margin: 0; }

.agent-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }

.agent-card {
  background: var(--bg-card);
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
</style>