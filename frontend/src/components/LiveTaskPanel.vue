<template>
  <div class="task-panel">
    <div class="tp-header">
      <span class="tp-title">Live Tasks</span>
      <span class="tp-count">{{ tasks.length }}</span>
    </div>
    <div class="tp-list">
      <TransitionGroup name="task-slide">
        <div v-for="task in tasks" :key="task.id" class="tp-item" :class="task.status">
          <div class="tp-icon">
            <span v-if="task.status === 'running'" class="spin-dot"></span>
            <span v-else-if="task.status === 'done'" class="done-dot">ok</span>
            <span v-else-if="task.status === 'failed'" class="fail-dot">!</span>
            <span v-else class="pending-dot"></span>
          </div>
          <div class="tp-body">
            <div class="tp-name">{{ task.name }}</div>
            <div class="tp-meta">{{ task.source }} · {{ task.time }}</div>
          </div>
        </div>
      </TransitionGroup>
      <div v-if="!tasks.length" class="tp-empty">no active tasks</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const tasks = ref([])
let timer = null

const demoEvents = [
  { name: 'SSH: check server health', source: 'DevOps', status: 'running' },
  { name: 'Docker: check containers', source: 'DevOps', status: 'running' },
  { name: 'Memory: save context', source: 'Memory', status: 'done' },
  { name: 'Trend: scan hot topics', source: 'Trend', status: 'running' },
  { name: 'Vision: analyze product image', source: 'Vision', status: 'pending' },
  { name: 'Nginx: check config', source: 'DevOps', status: 'done' },
  { name: 'DB: backup completed', source: 'Code', status: 'done' },
  { name: 'SelfHeal: patrol check', source: 'Heal', status: 'running' },
]

function addRandomTask() {
  const ev = demoEvents[Math.floor(Math.random() * demoEvents.length)]
  const now = new Date()
  tasks.value.unshift({
    id: Date.now(),
    name: ev.name,
    source: ev.source,
    status: ev.status,
    time: now.toLocaleTimeString('en-US', { hour12: false }),
  })
  if (tasks.value.length > 20) tasks.value.pop()
}

onMounted(() => {
  addRandomTask()
  timer = setInterval(addRandomTask, 4000)
})

onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.task-panel {
  width: 240px;
  min-width: 240px;
  background: #080b14;
  border-left: 1px solid rgba(102,126,234,.08);
  display: flex;
  flex-direction: column;
  height: 100%;
}
.tp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(102,126,234,.06);
}
.tp-title { font-size: 11px; font-weight: 600; color: rgba(255,255,255,.4); text-transform: uppercase; letter-spacing: 1px }
.tp-count { font-size: 10px; padding: 2px 8px; border-radius: 8px; background: rgba(102,126,234,.12); color: #667eea }
.tp-list { flex: 1; overflow-y: auto; padding: 8px }
.tp-empty { text-align: center; padding: 30px 10px; font-size: 11px; color: rgba(255,255,255,.15) }
.tp-item { display: flex; gap: 8px; padding: 8px 10px; border-radius: 8px; margin-bottom: 2px; align-items: flex-start }
.tp-item.running { background: rgba(102,126,234,.04) }
.tp-item.done { opacity: .5 }
.tp-icon { width: 14px; height: 14px; flex-shrink: 0; margin-top: 2px }
.spin-dot { display: block; width: 8px; height: 8px; border-radius: 50%; border: 2px solid #667eea; border-top-color: transparent; animation: spin .8s linear infinite }
.done-dot { display: block; font-size: 10px; color: #52c41a }
.fail-dot { display: block; font-size: 10px; color: #ff4d4f; font-weight: 700 }
.pending-dot { display: block; width: 6px; height: 6px; border-radius: 50%; background: rgba(255,255,255,.2) }
.tp-name { font-size: 11px; color: rgba(255,255,255,.7); line-height: 1.3 }
.tp-meta { font-size: 9px; color: rgba(255,255,255,.25); margin-top: 2px }
@keyframes spin { to { transform: rotate(360deg) } }
.task-slide-enter-active { transition: all .3s ease-out }
.task-slide-enter-from { opacity: 0; transform: translateX(20px) }
</style>