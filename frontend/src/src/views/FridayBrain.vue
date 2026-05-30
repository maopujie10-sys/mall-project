<template>
  <div class="lifeform-glass">
    <div class="glass-inner">
      <div class="glass-row">
        -
        <div class="glass-info">
          <span class="glass-name">Friday AI OS</span>
          <span class="glass-cycle"> {{ status.cycle }}  {{ status.status === 'active' ? '' : '' }}</span>
        </div>
        <div class="glass-mood" :style="{borderColor: status.mood?.color}">
          <span>{{ status.mood?.emoji }}</span>
          <span class="mood-text">{{ status.mood?.label }}</span>
        </div>
      </div>
      <div class="glass-stats">
        <span v-for="s in topStats" :key="s.key" class="glass-stat">
          <b>{{ s.icon }}</b> {{ s.label }} <em>{{ s.value }}%</em>
        </span>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted, onUnmounted } from "vue"
import { agentApi } from "@/api"

const status = ref({ traits:{}, insights:[], dreams:[], mood:{}, reflection:'' })
let timer = null

const topStats = computed(() => [
  {key:'health',icon:'',label:'',value:status.value.health||0},
  {key:'intelligence',icon:'',label:'',value:status.value.intelligence||0},
  {key:'energy',icon:'',label:'',value:status.value.energy||0},
  {key:'mood_score',icon:'',label:'',value:Math.round((status.value.mood?.score||0.75)*100)},
])
const stats = computed(() => [
  {key:"health",icon:"",label:'',value:status.value.health||0,color:"red",gradient:"linear-gradient(90deg,#ff4d4f,#ff7a45)"},
  {key:"intelligence",icon:"",label:'',value:status.value.intelligence||0,color:"blue",gradient:"linear-gradient(90deg,#1890ff,#667eea)"},
  {key:"energy",icon:"",label:'',value:status.value.energy||0,color:"green",gradient:"linear-gradient(90deg,#52c41a,#13c2c2)"},
  {key:"experience",icon:"",label:'',value:status.value.experience||0,color:"purple",gradient:"linear-gradient(90deg,#7c3aed,#8b5cf6)"},
  {key:"mood_score",icon:"",label:'',value:Math.round((status.value.mood?.score||0.75)*100),color:"orange",gradient:"linear-gradient(90deg,#faad14,#f59e0b)"},
  {key:"success_rate",icon:"",label:'',value:status.value.success_rate||0,color:"cyan",gradient:"linear-gradient(90deg,#06b6d4,#22d3ee)"},
  {key:"memory_count",icon:"",label:'',value:Math.min(100,(status.value.memory_count||0)),color:"pink",gradient:"linear-gradient(90deg,#ec4899,#f472b6)"},
])

function computed(fn) { return fn() }

async function refresh() {
  try { status.value = (await agentApi.get("/agent/lifeform/status")).data || {} } catch {}
}
onMounted(() => { refresh(); timer = setInterval(refresh, 10000) })
onUnmounted(() => { clearInterval(timer) })
</script>

<style scoped>
.lifeform-glass {
  position: fixed; top: 16px; left: 50%; transform: translateX(-50%);
  z-index: 100;
  max-width: 640px; width: calc(100% - 100px);
}
.glass-inner {
  background: rgba(13,16,37,0.55);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(102,126,234,0.2);
  border-radius: 16px;
  padding: 12px 20px;
}
.glass-row {
  display: flex; align-items: center; gap: 12px;
}
.glass-icon { font-size: 28px; }
.glass-info { flex: 1; display: flex; flex-direction: column; }
.glass-name { font-size: 16px; font-weight: 600; color: #e8eaf0; }
.glass-cycle { font-size: 11px; color: rgba(255,255,255,0.5); }
.glass-mood {
  display: flex; align-items: center; gap: 4px;
  padding: 4px 12px; border: 1px solid; border-radius: 20px;
  font-size: 13px;
}
.mood-text { font-size: 11px; color: rgba(255,255,255,0.6); }
.glass-stats {
  display: flex; gap: 16px; margin-top: 8px;
  padding-top: 8px; border-top: 1px solid rgba(102,126,234,0.1);
  flex-wrap: wrap;
}
.glass-stat {
  font-size: 11px; color: rgba(255,255,255,0.6);
  display: flex; align-items: center; gap: 3px;
}
.glass-stat b { font-size: 14px; }
.glass-stat em { font-style: normal; color: #667eea; font-weight: 500; }
@media (max-width: 768px) {
  .lifeform-glass { width: calc(100% - 80px); top: 76px; }
  .glass-inner { padding: 10px 14px; }
  .glass-stats { gap: 10px; }
}
</style>