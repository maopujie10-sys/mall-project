<template>
  <div class="page-shell">
    <div class="page-header">
      <h2>🔧 AI能力状态</h2>
      <p>API Key配置检测 — 配得越多AI越强</p>
      <div class="cap-score" :class="status.grade">
        总体: {{status.grade}}级 ({{status.score}}%) — {{status.available}}/{{status.total}} 可用
      </div>
    </div>

    <div class="cap-grid">
      <div v-for="(v,k) in status.capabilities" :key="k" class="cap-card" :class="{ok:v.ok}">
        <div class="cap-icon">{{v.ok?'✅':'❌'}}</div>
        <div class="cap-name">{{k}}</div>
        <div class="cap-label">{{v.label}}</div>
        <div v-if="v.models" class="cap-models">{{v.models.join(', ')}}</div>
        <div v-if="!v.ok" class="cap-action">
          {{k==='ollama'?'免费安装即可':'需配置环境变量'}}
        </div>
      </div>
    </div>

    <!-- 配置指南 -->
    <el-card style="margin-top:20px"><template #header>📖 快速配置指南</template>
      <div class="guide-grid">
        <div class="guide-item">
          <div class="guide-num">1</div>
          <div class="guide-text">
            <strong>Ollama(推荐)</strong> — 免费本地模型<br/>
            <code>curl -fsSL https://ollama.com/install.sh | sh</code><br/>
            <code>ollama pull qwen2.5:7b</code><br/>
            <span class="guide-gain">解锁：全部AI能力本地运行，零成本</span>
          </div>
        </div>
        <div class="guide-item">
          <div class="guide-num">2</div>
          <div class="guide-text">
            <strong>DeepSeek</strong> — 最便宜云端模型<br/>
            <code>export DEEPSEEK_API_KEY=sk-xxx</code><br/>
            <span class="guide-gain">解锁：Agent协作/RAG/预测/推荐/Text2SQL</span>
          </div>
        </div>
        <div class="guide-item">
          <div class="guide-num">3</div>
          <div class="guide-text">
            <strong>OpenAI</strong> — 语音+视觉<br/>
            <code>export OPENAI_API_KEY=sk-xxx</code><br/>
            <span class="guide-gain">解锁：语音对话STT/TTS + 视频分析 + 图片理解</span>
          </div>
        </div>
      </div>
      <div class="guide-note">
        ⚡ <strong>当前状态：</strong>
        <span v-if="status.available>=3">AI满血运行！</span>
        <span v-else-if="status.available>=1">AI基础可用，配更多Key提升能力</span>
        <span v-else>AI以本地模式运行（关键词+模板），配任意Key即可激活LLM智能</span>
      </div>
    </el-card>
  </div>
</template>
<script setup>
import {ref,onMounted} from 'vue';import {agentApi} from '@/api'
const status=ref({capabilities:{},score:0,grade:'C',available:0,total:0})
onMounted(async()=>{try{const r=await agentApi.get('/agent/capabilities/status');if(r?.data)status.value=r.data}catch(e){}})
</script>
<style scoped>
.page-shell{max-width:960px;margin:0 auto;padding:20px;}.page-header{margin-bottom:16px;}.page-header h2{font-size:20px;color:#e0e0ff;margin:0;}.page-header p{font-size:12px;color:rgba(255,255,255,0.5);margin:4px 0;}
.cap-score{font-size:16px;font-weight:600;margin-top:10px;padding:12px 18px;border-radius:10px;background:rgba(102,126,234,0.08);}
.cap-score.A{color:#4ade80;}.cap-score.B{color:#fbbf24;}.cap-score.C{color:#f87171;}.cap-score.D{color:#ef4444;}
.cap-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;margin-top:16px;}
.cap-card{padding:14px;background:rgba(15,15,35,0.8);border:1px solid rgba(255,255,255,0.06);border-radius:10px;text-align:center;opacity:0.45;transition:all 0.3s;}
.cap-card.ok{opacity:1;border-color:rgba(102,126,234,0.3);box-shadow:0 0 16px rgba(102,126,234,0.1);}
.cap-icon{font-size:22px;margin-bottom:4px;}.cap-name{font-size:12px;font-weight:600;color:#e0e0ff;text-transform:uppercase;}
.cap-label{font-size:10px;color:rgba(255,255,255,0.4);margin-top:2px;}.cap-models{font-size:9px;color:rgba(102,126,234,0.5);margin-top:2px;}
.cap-action{font-size:10px;color:#fbbf24;margin-top:4px;}
.guide-grid{display:flex;flex-direction:column;gap:12px;}
.guide-item{display:flex;gap:12px;align-items:flex-start;padding:12px;background:rgba(255,255,255,0.03);border-radius:10px;}
.guide-num{width:28px;height:28px;border-radius:50%;background:rgba(102,126,234,0.3);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;flex-shrink:0;}
.guide-text{font-size:13px;color:#e0e0e0;line-height:1.6;}
.guide-text code{background:rgba(0,0,0,0.5);padding:2px 6px;border-radius:4px;font-size:11px;color:#a0c4ff;}
.guide-gain{display:block;margin-top:4px;font-size:11px;color:#4ade80;}
.guide-note{margin-top:16px;padding:12px;background:rgba(102,126,234,0.06);border-radius:10px;font-size:13px;color:rgba(255,255,255,0.7);}
@media(max-width:768px){.page-shell{padding:10px;}.cap-grid{grid-template-columns:repeat(3,1fr);}}
</style>
