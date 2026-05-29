<template><div class="page-shell"><div class="page-header"><h2>🚀 高级AI</h2><p>实时语音 · 视频理解 · 深度研究 · 数据分析 · 网页抓取 · 浏览器自动化</p></div>
<el-tabs v-model="tab" type="border-card">

<el-tab-pane label="🎙️ 实时语音" name="voice">
<div class="voice-area"><div class="voice-status" :class="{active:voiceConnected}">{{voiceConnected?'🟢 已连接':'🔴 未连接'}}</div>
<div class="voice-transcript" ref="voiceLog"><div v-for="(m,i) in voiceMsgs" :key="i" :class="'vm-'+m.role">{{m.content}}</div></div>
<div class="voice-controls"><button class="vc-btn" :class="{recording:isRecording}" @click="toggleVoice" :disabled="!voiceConnected">{{isRecording?'⏹️ 停止':'🎤 开始说话'}}</button></div></div></el-tab-pane>

<el-tab-pane label="🔬 深度研究" name="research">
<el-input v-model="researchTopic" placeholder="研究主题，如：2024跨境电商趋势"/>
<el-button type="primary" @click="runResearch" :loading="loading" style="margin-top:8px">🔬 开始研究</el-button>
<div v-if="researchReport" class="report-box"><div class="report-title">📄 研究报告: {{researchTopic}}</div>
<div v-if="researchFindings" class="findings"><div v-for="f in researchFindings" :key="f.question" class="finding-item"><b>{{f.question}}</b><br>{{f.finding}}</div></div>
<div class="report-body" v-html="md(researchReport)"></div></div></el-tab-pane>

<el-tab-pane label="📊 数据分析" name="data">
<el-input v-model="csvData" type="textarea" :rows="4" placeholder="粘贴CSV数据..."/>
<el-input v-model="dataQuestion" placeholder="你想了解什么？（如：哪个品类销量最高）"/>
<el-button type="primary" @click="analyzeData" :loading="loading" style="margin-top:8px">📊 分析</el-button>
<div v-if="dataInsight" class="result-box"><div v-html="md(dataInsight)"></div></div></el-tab-pane>

<el-tab-pane label="🌐 网页抓取" name="scrape">
<el-input v-model="scrapeUrl" placeholder="https://..." @keydown.enter="runScrape"/>
<el-button type="primary" @click="runScrape" :loading="loading" style="margin-left:8px">抓取+总结</el-button>
<div v-if="scrapeResult" class="result-box"><b>{{scrapeResult.title}}</b><div v-html="md(scrapeResult.summary||scrapeResult.error)"></div></div></el-tab-pane>

<el-tab-pane label="📁 导出" name="export">
<el-input v-model="exportContent" type="textarea" :rows="6" placeholder="要导出的内容..."/>
<el-select v-model="exportFormat"><el-option label="Markdown" value="md"/><el-option label="HTML" value="html"/><el-option label="纯文本" value="txt"/></el-select>
<el-button type="primary" @click="runExport" :loading="loading" style="margin-left:8px">导出</el-button>
<div v-if="exportUrl" class="result-box">✅ <a :href="exportUrl" target="_blank">下载文件</a></div></el-tab-pane>

<el-tab-pane label="🧠 记忆压缩" name="memory">
<el-input v-model="compressCid" placeholder="对话ID（可从AI对话中获取）"/>
<el-button type="primary" @click="compressMem" :loading="loading">压缩长对话</el-button>
<div v-if="memorySummary" class="result-box"><b>原始消息:</b> {{memoryCount}}条<br><b>摘要:</b><div v-html="md(memorySummary)"></div></div></el-tab-pane>

</el-tabs></div></template>
<script setup>
import {ref,nextTick,onUnmounted} from "vue";import {ElMessage} from "element-plus";import {agentApi} from "@/api"
const tab=ref("voice");const loading=ref(false)
const voiceConnected=ref(false);const isRecording=ref(false);const voiceMsgs=ref([]);const voiceLog=ref(null)
const researchTopic=ref("");const researchReport=ref("");const researchFindings=ref(null)
const csvData=ref("");const dataQuestion=ref("分析数据");const dataInsight=ref("")
const scrapeUrl=ref("");const scrapeResult=ref(null)
const exportContent=ref("");const exportFormat=ref("md");const exportUrl=ref("")
const compressCid=ref("");const memorySummary=ref("");const memoryCount=ref(0)
let ws=null;let recognition=null

function connectVoice(){
  const proto=location.protocol==='https:'?'wss:':'ws:'
  ws=new WebSocket(`${proto}//${location.host}/agent/advanced/voice/live`)
  ws.onopen=()=>{voiceConnected.value=true;ElMessage.success('语音已连接')}
  ws.onclose=()=>{voiceConnected.value=false;setTimeout(connectVoice,3000)}
  ws.onmessage=(e)=>{const d=JSON.parse(e.data)
    if(d.type==='token'){const last=voiceMsgs.value[voiceMsgs.value.length-1];if(last&&last.role==='assistant')last.content+=d.text;else voiceMsgs.value.push({role:'assistant',content:d.text})}
    else if(d.type==='done'){/* done */}
    else if(d.type==='interrupted'){ElMessage.info('已打断')}
    scrollVoice()}
  ws.onerror=()=>{voiceConnected.value=false}
}
function toggleVoice(){
  if(isRecording.value){if(recognition){recognition.stop();recognition=null};isRecording.value=false;return}
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition
  if(!SR){ElMessage.error('浏览器不支持语音识别');return}
  recognition=new SR();recognition.lang='zh-CN';recognition.continuous=true;recognition.interimResults=false
  recognition.onresult=(e)=>{const text=Array.from(e.results).map(r=>r[0].transcript).join('');if(text){voiceMsgs.value.push({role:'user',content:text});if(ws&&ws.readyState===WebSocket.OPEN)ws.send(JSON.stringify({type:'speech',text}))}}
  recognition.onerror=()=>{isRecording.value=false}
  recognition.onend=()=>{isRecording.value=false}
  recognition.start();isRecording.value=true
}
function scrollVoice(){nextTick(()=>{if(voiceLog.value)voiceLog.value.scrollTop=voiceLog.value.scrollHeight})}
onUnmounted(()=>{if(ws)ws.close();if(recognition)recognition.stop()})
connectVoice()

const api=async(u,b)=>{loading.value=true;try{const r=await agentApi.post(u,b);loading.value=false;return r?.data}catch(e){loading.value=false;ElMessage.error(e.message)}}
async function runResearch(){const d=await api("/agent/advanced/research",{topic:researchTopic.value});researchReport.value=d?.report;researchFindings.value=d?.findings}
async function analyzeData(){const d=await api("/agent/advanced/data/analyze",{csv_data:csvData.value,question:dataQuestion.value});dataInsight.value=d?.insight}
async function runScrape(){const d=await api("/agent/advanced/scrape",{url:scrapeUrl.value});scrapeResult.value=d}
async function runExport(){const d=await api("/agent/advanced/export",{content:exportContent.value,format:exportFormat.value,filename:'report'});if(d?.ok)exportUrl.value="/agent/advanced/download/"+d.filename}
async function compressMem(){const d=await api("/agent/advanced/memory/compress",{conversation_id:compressCid.value});if(d?.ok){memorySummary.value=d.summary;memoryCount.value=d.original_messages}}
function md(t){return(t||'').replace(/\n/g,"<br>").replace(/\*\*(.*?)\*\*/g,"<b>$1</b>")}
</script>
<style scoped>.page-shell{max-width:900px;margin:0 auto;padding:20px}.page-header{margin-bottom:16px}.page-header h2{font-size:20px;color:#e0e0ff;margin:0}.page-header p{font-size:12px;color:rgba(255,255,255,.5);margin:4px 0}.voice-area{text-align:center}.voice-status{font-size:14px;margin-bottom:12px;color:rgba(255,255,255,.5)}.voice-status.active{color:#4ade80}.voice-transcript{max-height:300px;overflow-y:auto;text-align:left;padding:12px;background:rgba(0,0,0,.3);border-radius:10px;margin-bottom:12px}.vm-user{color:#667eea;margin-bottom:8px}.vm-assistant{color:#e0e0e0;margin-bottom:8px}.vc-btn{width:80px;height:80px;border-radius:50%;border:3px solid rgba(102,126,234,.4);background:rgba(15,15,35,.9);color:#e0e0ff;font-size:16px;cursor:pointer}.vc-btn.recording{border-color:#ef4444;animation:pulse 1.5s infinite}@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,.5)}50%{box-shadow:0 0 0 20px rgba(239,68,68,0)}}.report-box{margin-top:12px;padding:16px;background:rgba(15,15,35,.8);border:1px solid rgba(102,126,234,.2);border-radius:12px}.report-title{font-size:16px;font-weight:600;color:#e0e0ff;margin-bottom:12px}.findings{margin-bottom:12px}.finding-item{padding:8px;background:rgba(102,126,234,.08);border-radius:8px;margin-bottom:6px;font-size:13px;color:rgba(255,255,255,.7)}.result-box{margin-top:12px;padding:14px;background:rgba(0,0,0,.5);border:1px solid rgba(102,126,234,.2);border-radius:10px;font-size:13px;color:#e0e0e0;line-height:1.7;max-height:400px;overflow:auto}@media(max-width:768px){.page-shell{padding:10px}}</style>