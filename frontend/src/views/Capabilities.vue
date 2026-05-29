<template>
  <div class="page-shell">
    <div class="page-header"><h2>🔧 AI能力状态</h2><p>检测所有API Key配置 + 模型可用性</p>
      <div class="cap-score" :class="status.grade">总体评分: {{status.grade}} ({{status.score}}%) — {{status.available}}/{{status.total}} 可用</div>
    </div>
    <div class="cap-grid">
      <div v-for="(v,k) in status.capabilities" :key="k" class="cap-card" :class="{ok:v.ok}">
        <div class="cap-icon">{{v.ok?'✅':'❌'}}</div>
        <div class="cap-name">{{k}}</div>
        <div class="cap-label">{{v.label}}</div>
        <div v-if="v.models" class="cap-models">{{v.models.join(', ')}}</div>
      </div>
    </div>
    <div class="cap-tip">{{status.tip}}</div>
  </div>
</template>
<script setup>
import {ref,onMounted} from 'vue';import {agentApi} from '@/api'
const status=ref({capabilities:{},score:0,grade:'C',available:0,total:0,tip:''})
onMounted(async()=>{try{const r=await agentApi.get('/agent/capabilities/status');if(r?.data)status.value=r.data}catch(e){}})
</script>
<style scoped>
.page-shell{max-width:900px;margin:0 auto;padding:20px;}.page-header{margin-bottom:16px;}.page-header h2{font-size:20px;color:#e0e0ff;margin:0;}.page-header p{font-size:12px;color:rgba(255,255,255,0.5);margin:4px 0;}
.cap-score{font-size:16px;font-weight:600;margin-top:10px;padding:10px 16px;border-radius:10px;background:rgba(102,126,234,0.08);}
.cap-score.A{color:#4ade80;}.cap-score.B{color:#fbbf24;}.cap-score.C{color:#f87171;}.cap-score.D{color:#ef4444;}
.cap-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px;margin-top:16px;}
.cap-card{padding:14px;background:rgba(15,15,35,0.8);border:1px solid rgba(255,255,255,0.06);border-radius:10px;text-align:center;opacity:0.5;}
.cap-card.ok{opacity:1;border-color:rgba(102,126,234,0.3);}
.cap-icon{font-size:24px;margin-bottom:6px;}.cap-name{font-size:13px;font-weight:600;color:#e0e0ff;text-transform:uppercase;}
.cap-label{font-size:11px;color:rgba(255,255,255,0.5);margin-top:4px;}.cap-models{font-size:10px;color:rgba(102,126,234,0.7);margin-top:4px;}
.cap-tip{margin-top:16px;text-align:center;font-size:13px;color:rgba(255,255,255,0.5);}
@media(max-width:768px){.page-shell{padding:10px;}}
</style>
