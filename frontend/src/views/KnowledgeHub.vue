<template><div class="page-shell">
<div class="page-header"><h2>  RAG</h2><p>  AI  </p></div>

<el-tabs v-model="tab">
<el-tab-pane label=" " name="upload">
  <el-upload drag :http-request="uploadDoc" :show-file-list="false" accept=".txt,.md,.pdf,.csv,.json,.py,.js,.html">
    <el-icon size="48"><UploadFilled/></el-icon>
    -
    <div style="font-size:11px;color:rgba(255,255,255,.4)"> TXT/MD/PDF/CSV/</div>
  </el-upload>
  <div v-if="uploadResult" class="result-box" style="margin-top:12px">{{uploadResult}}</div>
</el-tab-pane>

<el-tab-pane label=" " name="ask">
  <el-input v-model="question" placeholder="..." @keydown.enter="askRag" size="large"/>
  
  <div v-if="ragAnswer" class="result-box" style="margin-top:12px">
    -
    <div v-if="ragSources.length" style="margin-top:8px;font-size:11px;color:rgba(255,255,255,.4)">
       : {{ragSources.map(s=>s.source).join(', ')}}
    </div>
  </div>
</el-tab-pane>

<el-tab-pane label=" " name="stats">
  <el-button @click="loadStats" :loading="loading">OK</el-button>
  <div v-if="stats" class="result-box" style="margin-top:12px">
    <el-row :gutter="12">
      <el-col :span="8"><el-statistic title='' :value="stats.total_docs"/></el-col>
      <el-col :span="8"><el-statistic title='' :value="stats.unique_sources"/></el-col>
      <el-col :span="8"><el-statistic title='' :value="stats.index_size"/></el-col>
    </el-row>
    <div v-if="stats.last_doc" style="margin-top:8px;font-size:11px">: {{stats.last_doc}}</div>
  </div>
</el-tab-pane>

<el-tab-pane label=" " name="batch">
  <el-input v-model="batchText" type="textarea" :rows="6" placeholder="..."/>
  <el-input v-model="batchSource" placeholder="()" style="margin-top:8px"/>
  <el-button type="primary" @click="ingestText" :loading="loading" style="margin-top:8px">OK</el-button>
</el-tab-pane>
</el-tabs></div></template>

<script setup>
import {ref} from "vue";import {UploadFilled} from "@element-plus/icons-vue";import {ElMessage} from "element-plus";import {agentApi} from "@/api"
const tab=ref("upload");const loading=ref(false);const question=ref('');const ragAnswer=ref('');const ragSources=ref([])
const uploadResult=ref('');const stats=ref(null);const batchText=ref('');const batchSource=ref('')

async function uploadDoc(options) {
  loading.value=true;uploadResult.value=''
  try {
    const form=new FormData();form.append("file",options.file)
    const r=await agentApi.post("/rag/upload",form,{headers:{"Content-Type":"multipart/form-data"}})
    if(r?.data?.ok){uploadResult.value=` ${r.data.filename}  (${r.data.chunks||0})`;ElMessage.success('OK')}
    else uploadResult.value=` ${r?.data?.error||''}`
  }catch(e){uploadResult.value=" "+e.message}
  loading.value=false
}
async function askRag() {
  if(!question.value.trim())return
  loading.value=true;ragAnswer.value='';ragSources.value=[]
  try {
    const r=await agentApi.post("/rag/ask",{question:question.value,top_k:5})
    if(r?.data?.ok){ragAnswer.value=r.data.answer?.replace(/\n/g,"<br>");ragSources.value=r.data.sources||[]}
    else ragAnswer.value=r?.data?.error||''
  }catch(e){ragAnswer.value=": "+e.message}
  loading.value=false
}
async function loadStats() {
  loading.value=true
  try {const r=await agentApi.get("/rag/stats");if(r?.data?.ok)stats.value=r.data}catch(e){}
  loading.value=false
}
async function ingestText() {
  if(!batchText.value.trim())return
  loading.value=true
  try {
    const r=await agentApi.post("/rag/ingest",{text:batchText.value,source:batchSource.value||''})
    if(r?.data?.ok){ElMessage.success(`: ${r.data.doc_id}`);batchText.value=''}
  }catch(e){ElMessage.error(e.message)}
  loading.value=false
}
</script>
<style scoped>.page-shell{max-width:800px;margin:0 auto;padding:20px}.page-header{margin-bottom:16px}.page-header h2{font-size:20px;color:#e0e0ff;margin:0}.page-header p{font-size:12px;color:rgba(255,255,255,.5)}.result-box{margin-top:12px;padding:14px;background: rgba(0,0,0,0.2);border:1px solid rgba(102,126,234,.2);border-radius:10px;font-size:13px;color:#e0e0e0;line-height:1.7}</style>