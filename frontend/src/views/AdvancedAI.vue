<template><div class="page-shell"><div class="page-header"><h2> AI</h2>-</div>
<el-tabs v-model="tab" type="border-card">

<el-tab-pane label=" " name="voice">
<div class="voice-area"><div class="voice-status" :class="{active:voiceConnected}">{{voiceConnected?'':''}}</div>
<div class="voice-transcript" ref="voiceLog"><div v-for="(m,i) in voiceMsgs" :key="i" :class=''vm-'+m.role">{{m.content}}</div></div>
<div class="voice-controls"><button class="vc-btn" :class="{recording:isRecording}" @click="toggleVoice" :disabled="!voiceConnected">{{isRecording?'':''}}</button></div></div></el-tab-pane>

<el-tab-pane label=" " name="research">
<el-input v-model="researchTopic" placeholder="2024"/>

<div v-if="researchReport" class="report-box"><div class="report-title"> : {{researchTopic}}</div>
<div v-if="researchFindings" class="findings"><div v-for="f in researchFindings" :key="f.question" class="finding-item"><b>{{f.question}}</b><br>{{f.finding}}</div></div>
-</div></el-tab-pane>

<el-tab-pane label=" " name="data">
<el-input v-model="csvData" type="textarea" :rows="4" placeholder="CSV..."/>
<el-input v-model="dataQuestion" placeholder='Search...'/>

<div v-if="dataInsight" class="result-box">-</div></el-tab-pane>

<el-tab-pane label=" " name="scrape">
<el-input v-model="scrapeUrl" placeholder="https://..." @keydown.enter="runScrape"/>
<el-button type="primary" @click="runScrape" :loading="loading" style="margin-left:8px">+</el-button>
<div v-if="scrapeResult" class="result-box"><b>{{scrapeResult.title}}</b>-</div></el-tab-pane>

<el-tab-pane label=" " name="export">
<el-input v-model="exportContent" type="textarea" :rows="6" placeholder="..."/>
<el-select v-model="exportFormat"><el-option label="Markdown" value="md"/><el-option label="HTML" value="html"/><el-option label='Status' value="txt"/></el-select>
<el-button type="primary" @click="runExport" :loading="loading" style="margin-left:8px">OK</el-button>
<div v-if="exportUrl" class="result-box"> -</div></el-tab-pane>

<el-tab-pane label=" " name="memory">
<el-input v-model="compressCid" placeholder="IDAI"/>
<el-button type="primary" @click="compressMem" :loading="loading">OK</el-button>
<div v-if="memorySummary" class="result-box"><b>:</b> {{memoryCount}}<br><b>:</b>-</div></el-tab-pane>


<el-tab-pane label=" Agent" name="browser">
<el-input v-model="browserCmd" placeholder="10" type="textarea" :rows="3"/>
<el-button type="primary" @click="runBrowser" :loading="loading" style="margin-top:8px"> AI</el-button>
<el-row :gutter="8" style="margin-top:8px"><el-col :span="8"></el-col>
<el-col :span="8"></el-col>
<el-col :span="8"></el-col></el-row>
<div v-if="browserPlan" class="result-box" style="margin-top:12px"><div class="plan-title"> AI({{browserPlan.length}}):</div>
<div v-for="(s,i) in browserPlan" :key="i" class="plan-step">{{i+1}}. {{s.action}}  {{s.target}} <span style="color:rgba(255,255,255,.4)">({{s.reason}})</span></div></div>
<div v-if="browserSummary" class="result-box"><b> :</b>-</div>
<div v-if="browserScreenshot" style="margin-top:12px">-</el-tab-pane>

<el-tab-pane label=" Agent" name="human">
<el-input v-model="humanCmd" placeholder='Enter...' type="textarea" :rows="3"/>
<el-select v-model="humanTarget" style="margin-top:8px"><el-option label=" " value="server"/><el-option v-for="c in remoteClients" :key="c" :label='Status' '+c" :value="c"/></el-select>

<div v-if="humanLog.length" class="human-log"><div v-for="l in humanLog" :key="l.cycle" class="hl-item">
<div class="hl-cycle"> {{l.cycle}}</div>
<div class="hl-obs"> {{l.observation}}</div>
<div class="hl-thought"> {{l.thought}}</div>
<div class="hl-action"> {{l.action}}: {{JSON.stringify(l.params)}}</div>
</div></div>
<div v-if="humanResult" class="result-box"><b> :</b> {{humanResult}}</div>
<div v-if="humanScreenshot" class="result-box">-</el-tab-pane>

<el-tab-pane label=" " name="remote">
<div style="display:flex;gap:8px;margin-bottom:12px"><el-tag v-for="c in remoteClients" :key="c" type="success"> {{c}} </el-tag>-</div>
<el-button @click="loadRemoteClients" size="small">OK</el-button>
<el-select v-model="remoteClient" placeholder=''><el-option v-for="c in remoteClients" :key="c" :label="c" :value="c"/></el-select>
<el-select v-model="remoteAction" placeholder='Enter...' style="margin-left:8px"><el-option label=" " value="screenshot"/><el-option label=" " value="open_url"/><el-option label=" " value="click"/><el-option label=" " value="type_text"/><el-option label=" " value="press_key"/><el-option label=" " value="run_command"/><el-option label=" " value="get_info"/><el-option label=" " value="open_app"/></el-select>
<el-input v-model="remoteParams" placeholder="(JSON)" style="margin-top:8px"/>
<el-button type="primary" @click="runRemote" :loading="loading" style="margin-top:8px">OK</el-button>
<div v-if="remoteScreenshot" class="result-box">-
<div v-if="remoteResult" class="result-box"><pre>{{remoteResult}}</pre></div>

<el-divider> Agent</el-divider>
<el-button @click="downloadAgent">  friday_agent.py</el-button>
<div style="font-size:12px;color:rgba(255,255,255,.5);margin-top:4px">Windows/Mac: pip install websockets pyautogui pillow psutil && python friday_agent.py</div></el-tab-pane>
</el-tabs></div></template>
<script setup>
import {ref,nextTick,onUnmounted} from "vue";import {ElMessage} from "element-plus";import {agentApi} from "@/api"
const tab=ref("voice");const loading=ref(false)
const voiceConnected=ref(false);const isRecording=ref(false);const voiceMsgs=ref([]);const voiceLog=ref(null)
const researchTopic=ref('');const researchReport=ref('');const researchFindings=ref(null)
const csvData=ref('');const dataQuestion=ref('');const dataInsight=ref('')
const scrapeUrl=ref('');const scrapeResult=ref(null)
const exportContent=ref('');const exportFormat=ref("md");const exportUrl=ref('')
const compressCid=ref('');const memorySummary=ref('');const memoryCount=ref(0)
let ws=null;let recognition=null

function connectVoice(){
  const proto=location.protocol==='https:'?'wss:':'ws:'
  ws=new WebSocket(`${proto}//${location.host}/agent/advanced/voice/live`)
  ws.onopen=()=>{voiceConnected.value=true;ElMessage.success('OK')}
  ws.onclose=()=>{voiceConnected.value=false;setTimeout(connectVoice,3000)}
  ws.onmessage=(e)=>{const d=JSON.parse(e.data)
    if(d.type==='token'){const last=voiceMsgs.value[voiceMsgs.value.length-1];if(last&&last.role==='assistant')last.content+=d.text;else voiceMsgs.value.push({role:'assistant',content:d.text})}
    else if(d.type==='done'){/* done */}
    else if(d.type==='interrupted'){ElMessage.info('Info')}
    scrollVoice()}
  ws.onerror=()=>{voiceConnected.value=false}
}
function toggleVoice(){
  if(isRecording.value){if(recognition){recognition.stop();recognition=null};isRecording.value=false;return}
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition
  if(!SR){ElMessage.error('Error');return}
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

// === Agent ===
const browserCmd=ref('');const browserPlan=ref(null);const browserSummary=ref('');const browserScreenshot=ref(null)
// === Agent ===
const humanCmd=ref('');const humanTarget=ref("server");const humanLog=ref([]);const humanResult=ref('');const humanScreenshot=ref(null)
// ===  ===
const remoteClients=ref([]);const remoteClient=ref('');const remoteAction=ref("screenshot");const remoteParams=ref('');const remoteScreenshot=ref(null);const remoteResult=ref('')
async function runBrowser(){const d=await api("/agent/advanced/browser/agent",{command:browserCmd.value});if(d?.ok){browserPlan.value=d.plan;browserSummary.value=d.summary;browserScreenshot.value=d.final_screenshot}}
async function quickBrowser(type){const d=await api("/agent/advanced/browser/quick",{type,url:browserCmd.value||"https://www.google.com"});if(d?.ok){browserPlan.value=d.plan;browserSummary.value=d.summary;browserScreenshot.value=d.final_screenshot}}

async function runHumanAgent(){if(!humanCmd.value){ElMessage.warning('Warning');return}
humanLog.value=[];humanResult.value='';humanScreenshot.value=null;loading.value=true
try{const d=(await agentApi.post("/agent/advanced/agent/human",{command:humanCmd.value,target:humanTarget.value})).data
loading.value=false
if(d&&d.ok){humanLog.value=d.log||[];humanResult.value=d.final_result;humanScreenshot.value=d.screenshot;return}
humanLog.value=(d&&d.log)||[];humanResult.value=(d&&d.partial_result)||(d&&d.error)||'';humanScreenshot.value=d&&d.screenshot}catch(e){loading.value=false;ElMessage.error(e.message)}}
async function loadRemoteClients(){try{const d=(await agentApi.get("/agent/advanced/remote/clients")).data;if(d&&d.ok)remoteClients.value=d.clients||[]}catch(e){}}
async function runRemote(){if(!remoteClient.value){ElMessage.warning('Warning');return}
let params={};if(remoteParams.value){try{params=JSON.parse(remoteParams.value)}catch(e){ElMessage.error("JSON");return}}
loading.value=true
try{const d=(await agentApi.post("/agent/advanced/agent/quick",{client_id:remoteClient.value,action:remoteAction.value,params})).data
loading.value=false
if(d&&d.ok){remoteResult.value=JSON.stringify(d,null,2);remoteScreenshot.value=d.screenshot}else{remoteResult.value=JSON.stringify(d,null,2);remoteScreenshot.value=null}}catch(e){loading.value=false;ElMessage.error(e.message)}}
async function downloadAgent(){try{const r=await agentApi.get("/agent/advanced/remote/agent-script",{responseType:"text"});const blob=new Blob([r.data],{type:"text/plain"});const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="friday_agent.py";a.click();URL.revokeObjectURL(a.href);ElMessage.success(" friday_agent.py")}catch(e){ElMessage.error(": "+e.message)}}
</script>
<style scoped>.page-shell{max-width:900px;margin:0 auto;padding:20px}.page-header{margin-bottom:16px}.page-header h2{font-size:20px;color:#e0e0ff;margin:0}.page-header p{font-size:12px;color:rgba(255,255,255,.5);margin:4px 0}.voice-area{text-align:center}.voice-status{font-size:14px;margin-bottom:12px;color:rgba(255,255,255,.5)}.voice-status.active{color:#4ade80}.voice-transcript{max-height:300px;overflow-y:auto;text-align:left;padding:12px;background: rgba(0,0,0,0.15);border-radius:10px;margin-bottom:12px}.vm-user{color:#667eea;margin-bottom:8px}.vm-assistant{color:#e0e0e0;margin-bottom:8px}.vc-btn{width:80px;height:80px;border-radius:50%;border:3px solid rgba(102,126,234,.4);background:rgba(15,15,35,.9);color:#e0e0ff;font-size:16px;cursor:pointer}.vc-btn.recording{border-color:#ef4444;animation:pulse 1.5s infinite}@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,.5)}50%{box-shadow:0 0 0 20px rgba(239,68,68,0)}}.report-box{margin-top:12px;padding:16px;background: rgba(15,15,35,0.4);border:1px solid rgba(102,126,234,.2);border-radius:12px}.report-title{font-size:16px;font-weight:600;color:#e0e0ff;margin-bottom:12px}.findings{margin-bottom:12px}.finding-item{padding:8px;background:rgba(102,126,234,.08);border-radius:8px;margin-bottom:6px;font-size:13px;color:rgba(255,255,255,.7)}.result-box{margin-top:12px;padding:14px;background: rgba(0,0,0,0.2);border:1px solid rgba(102,126,234,.2);border-radius:10px;font-size:13px;color:#e0e0e0;line-height:1.7;max-height:400px;overflow:auto}@media(max-width:768px){.page-shell{padding:10px}}.plan-title{font-weight:600;color:#e0e0ff;margin-bottom:8px}.plan-step{padding:4px 0;font-size:12px;color:rgba(255,255,255,.7);border-bottom:1px solid rgba(255,255,255,.03)}
.human-log{margin-top:12px;max-height:400px;overflow-y:auto}.hl-item{padding:10px 12px;margin-bottom:8px;background: rgba(15,15,35,0.4);border:1px solid rgba(102,126,234,.15);border-radius:10px}.hl-cycle{font-size:13px;font-weight:600;color:#667eea;margin-bottom:6px}.hl-obs{font-size:12px;color:rgba(255,255,255,.6);margin-bottom:4px;line-height:1.5}.hl-thought{font-size:12px;color:#c084fc;margin-bottom:4px;font-style:italic;line-height:1.5}.hl-action{font-size:12px;color:#4ade80;font-family:monospace;line-height:1.5}</style>