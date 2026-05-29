<template>
  <div class="lifeform-dashboard">
    <!-- 椤堕儴鐘舵€?-->
    <div class="lf-header">
      <div class="lf-title"><span class="lf-icon">🧠</span><div><h1>Friday AI OS 数字生命体</h1><p class="lf-subtitle">自主运行 {{ status.cycle }} 周期 · {{ status.status === "active" ? "运行中" : "休眠" }}</p></div></div>
      <div class="lf-mood" :style="{borderColor: status.mood?.color}">
        <span class="mood-emoji">{{ status.mood?.emoji }}</span>
        <div><div class="mood-label">{{ status.mood?.label }}</div><div class="mood-desc">{{ status.mood?.desc }}</div></div>
      </div>
    </div>

    <!-- 涓冪淮鑳藉姏 -->
    <el-row :gutter="12" class="stats-row">
      <el-col :span="3" v-for="s in stats" :key="s.key">
        <div class="stat-card" :class="s.color">
          <div class="stat-icon">{{ s.icon }}</div>
          <div class="stat-value">{{ s.value }}<span class="stat-unit">%</span></div>
          <div class="stat-label">{{ s.label }}</div>
          <div class="stat-bar"><div class="stat-fill" :style="{width:s.value+'%',background:s.gradient}"></div></div>
        </div>
      </el-col>
    </el-row>

    <!-- 浜烘牸鐗硅川 -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="12">
        <el-card shadow="never"><template #header>🧠 浜烘牸鐗硅川</template>
          <div class="traits-grid">
            <div v-for="(v,k) in status.traits" :key="k" class="trait-item">
              <span class="trait-name">{{ {curiosity:"好奇心",precision:"精确性",creativity:"创造力",empathy:"同理心",efficiency:"效率"}[k]||k }}</span>
              <el-progress :percentage="Math.round(v*100)" :stroke-width="10" :color="v>0.7?'#52c41a':v>0.4?'#faad14':'#ff4d4f'" />
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never"><template #header>馃挱 褰撳墠鍙嶆€</template>
          <div class="reflection-box">{{ status.reflection || "姝ｅ湪绉疮缁忛獙..." }}</div>
          <div style="margin-top:12px;display:flex;gap:8px">
            <el-tag size="small">璁板繂: {{ status.memory_count }}娈</el-tag>
            <el-tag size="small" type="success">鎴愬姛鐜? {{ status.success_rate }}%</el-tag>
            <el-tag size="small" :type="status.health>60?'success':'warning'">鍋ュ悍搴? {{ status.health }}%</el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 娲炲療 + 姊﹀ -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="14">
        <el-card shadow="never"><template #header>馃攳 鏅鸿兘娲炲療 <el-button text size="small" @click="refresh" style="margin-left:auto">鍒锋柊</el-button></template>
          <div v-if="status.insights?.length" class="insight-list">
            <div v-for="ins in status.insights" :key="ins.title" class="insight-item" :class="ins.type">
              <span class="insight-icon">{{ ins.icon }}</span>
              <div class="insight-body"><div class="insight-title">{{ ins.title }}</div><div class="insight-detail">{{ ins.detail }}</div></div>
              <el-tag :type="ins.priority<=2?'danger':ins.priority<=3?'warning':'info'" size="small">P{{ ins.priority }}</el-tag>
            </div>
          </div>
          <el-empty v-else description="鏆傛棤娲炲療锛岀郴缁熻繍琛屽钩绋" />
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="never"><template #header>馃寵 姊﹀鏃ュ織</template>
          <div v-if="status.dreams?.length" class="dream-list">
            <div v-for="d in status.dreams" :key="d.time" class="dream-item">
              <div class="dream-cycle">周期 #{{ d.cycle }}</div>
              <div class="dream-assoc">馃挱 {{ d.association }}</div>
              <div class="dream-meta">{{ d.memory_count }}娈佃蹇</div>
            </div>
          </div>
          <el-empty v-else description="姝ｅ湪杩涘叆娣卞害鐫＄湢..." />
        </el-card>
      </el-col>
    </el-row>

    <!-- 3D鏁板瓧浣?-->
    <el-card shadow="never" style="overflow:hidden;border-radius:12px;flex:1;display:flex;flex-direction:column" body-style="flex:1;padding:0;overflow:hidden">
      <template #header><span>🧠 绁炵粡缃戠粶娲诲姩 <span style="font-size:12px;color:var(--text-muted);font-weight:400">鎷栨嫿鏃嬭浆 · 婊氳疆缂╂斁</span></span></template>
      <NeuralNetwork3D />
    </el-card>
  </div>
</template>
<script setup>
import { ref, onMounted, onUnmounted } from "vue"
import { agentApi } from "@/api"
import NeuralNetwork3D from "@/components/NeuralNetwork3D.vue"

const status = ref({ traits:{}, insights:[], dreams:[], mood:{}, reflection:"" })
let timer = null

const stats = computed(() => [
  {key:"health",icon:"鉂わ笍",label:"鐢熷懡鍊",value:status.value.health||0,color:"red",gradient:"linear-gradient(90deg,#ff4d4f,#ff7a45)"},
  {key:"intelligence",icon:"馃",label:"鏅哄姏",value:status.value.intelligence||0,color:"blue",gradient:"linear-gradient(90deg,#1890ff,#667eea)"},
  {key:"energy",icon:"鈿",label:"鑳介噺",value:status.value.energy||0,color:"green",gradient:"linear-gradient(90deg,#52c41a,#13c2c2)"},
  {key:"experience",icon:"馃搱",label:"缁忛獙",value:status.value.experience||0,color:"purple",gradient:"linear-gradient(90deg,#7c3aed,#8b5cf6)"},
  {key:"mood_score",icon:"馃槉",label:"鎯呯华",value:Math.round((status.value.mood?.score||0.75)*100),color:"orange",gradient:"linear-gradient(90deg,#faad14,#f59e0b)"},
  {key:"success_rate",icon:"馃幆",label:"鎴愬姛鐜",value:status.value.success_rate||0,color:"cyan",gradient:"linear-gradient(90deg,#06b6d4,#22d3ee)"},
  {key:"memory_count",icon:"馃捑",label:"璁板繂",value:Math.min(100,(status.value.memory_count||0)),color:"pink",gradient:"linear-gradient(90deg,#ec4899,#f472b6)"},
])

function computed(fn) { return fn() }

async function refresh() {
  try { status.value = (await agentApi.get("/agent/lifeform/status")).data || {} } catch {}
}
onMounted(() => { refresh(); timer = setInterval(refresh, 10000) })
onUnmounted(() => { clearInterval(timer) })
</script>
<style scoped>
.lifeform-dashboard{display:flex;flex-direction:column;height:calc(100vh - 80px);padding:20px;overflow-y:auto}
.lf-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}
.lf-title{display:flex;align-items:center;gap:12px}
.lf-icon{font-size:36px}
.lf-title h1{font-size:20px;margin:0}
.lf-subtitle{font-size:12px;color:var(--text-muted);margin:2px 0 0}
.lf-mood{display:flex;align-items:center;gap:10px;padding:8px 16px;border:1px solid;border-radius:12px;background:rgba(102,126,234,0.05)}
.mood-emoji{font-size:28px}
.mood-label{font-size:14px;font-weight:600}
.mood-desc{font-size:11px;color:var(--text-muted)}
.stats-row{margin-bottom:20px}
.stat-card{text-align:center;padding:12px 4px;border-radius:10px;background:var(--bg-card);border:1px solid var(--border-color);transition:all .2s}
.stat-card:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,0.1)}
.stat-icon{font-size:22px;margin-bottom:4px}
.stat-value{font-size:22px;font-weight:700}
.stat-unit{font-size:12px;font-weight:400;color:var(--text-muted)}
.stat-label{font-size:10px;color:var(--text-muted);margin:2px 0}
.stat-bar{height:3px;background:#f0f0f0;border-radius:2px;overflow:hidden;margin-top:4px}
.stat-fill{height:100%;border-radius:2px;transition:width .6s}
.traits-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.trait-item{display:flex;flex-direction:column;gap:4px}
.trait-name{font-size:12px;color:var(--text-muted)}
.reflection-box{font-size:13px;line-height:1.6;color:var(--text-primary);padding:8px;background:rgba(102,126,234,0.05);border-radius:8px}
.insight-list{display:flex;flex-direction:column;gap:8px}
.insight-item{display:flex;align-items:flex-start;gap:10px;padding:10px;border-radius:8px;background:var(--bg-page)}
.insight-item.warning{border-left:3px solid #faad14}
.insight-item.error{border-left:3px solid #ff4d4f}
.insight-item.success{border-left:3px solid #52c41a}
.insight-icon{font-size:18px;flex-shrink:0;margin-top:2px}
.insight-body{flex:1}
.insight-title{font-size:13px;font-weight:500}
.insight-detail{font-size:11px;color:var(--text-muted);margin-top:2px}
.dream-list{display:flex;flex-direction:column;gap:8px}
.dream-item{padding:10px;border-radius:8px;background:rgba(102,126,234,0.05);font-size:12px}
.dream-cycle{font-size:10px;color:var(--text-muted)}
.dream-assoc{margin:4px 0;line-height:1.5}
.dream-meta{font-size:10px;color:var(--text-muted)}
</style>
