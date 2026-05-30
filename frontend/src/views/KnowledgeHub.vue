<template><div class="page-shell">
<div class="page-header"><h2>📚 知识库 RAG</h2><p>上传文档 · AI基于你的数据回答 · 语义搜索</p></div>

<el-tabs v-model="tab">
<el-tab-pane label="📤 上传文档" name="upload">
  <el-upload drag :http-request="uploadDoc" :show-file-list="false" accept=".txt,.md,.pdf,.csv,.json,.py,.js,.html">
    <el-icon size="48"><UploadFilled/></el-icon>
    <div style="margin-top:12px">拖拽或点击上传文档</div>
    <div style="font-size:11px;color:rgba(255,255,255,.4)">支持 TXT/MD/PDF/CSV/代码文件</div>
  </el-upload>
  <div v-if="uploadResult" class="result-box" style="margin-top:12px">{{uploadResult}}</div>
</el-tab-pane>

<el-tab-pane label="🔍 智能问答" name="ask">
  <el-input v-model="question" placeholder="基于知识库提问..." @keydown.enter="askRag" size="large"/>
  <el-button type="primary" @click="askRag" :loading="loading" style="margin-top:8px">🔍 搜索知识库</el-button>
  <div v-if="ragAnswer" class="result-box" style="margin-top:12px">
    <div v-html="ragAnswer"></div>
    <div v-if="ragSources.length" style="margin-top:8px;font-size:11px;color:rgba(255,255,255,.4)">
      📖 参考: {{ragSources.map(s=>s.source).join(', ')}}
    </div>
  </div>
</el-tab-pane>

<el-tab-pane label="📊 知识库统计" name="stats">
  <el-button @click="loadStats" :loading="loading">刷新统计</el-button>
  <div v-if="stats" class="result-box" style="margin-top:12px">
    <el-row :gutter="12">
      <el-col :span="8"><el-statistic title="文档数" :value="stats.total_docs"/></el-col>
      <el-col :span="8"><el-statistic title="来源数" :value="stats.unique_sources"/></el-col>
      <el-col :span="8"><el-statistic title="索引词" :value="stats.index_size"/></el-col>
    </el-row>
    <div v-if="stats.last_doc" style="margin-top:8px;font-size:11px">最新: {{stats.last_doc}}</div>
  </div>
</el-tab-pane>

<el-tab-pane label="💬 批量导入" name="batch">
  <el-input v-model="batchText" type="textarea" :rows="6" placeholder="粘贴文本内容，自动分段导入..."/>
  <el-input v-model="batchSource" placeholder="来源名称(可选)" style="margin-top:8px"/>
  <el-button type="primary" @click="ingestText" :loading="loading" style="margin-top:8px">摄入知识库</el-button>
</el-tab-pane>
</el-tabs></div></template>

<script setup>
import {ref} from "vue";import {UploadFilled} from "@element-plus/icons-vue";import {ElMessage} from "element-plus";import {agentApi} from "@/api"
const tab=ref("upload");const loading=ref(false);const question=ref("");const ragAnswer=ref("");const ragSources=ref([])
const uploadResult=ref("");const stats=ref(null);const batchText=ref("");const batchSource=ref("")

async function uploadDoc(options) {
  loading.value=true;uploadResult.value=""
  try {
    const form=new FormData();form.append("file",options.file)
    const r=await agentApi.post("/rag/upload",form,{headers:{"Content-Type":"multipart/form-data"}})
    if(r?.ok){uploadResult.value=`✅ ${r.filename} 摄入成功 (${r.chunks||0}段)`;ElMessage.success("上传成功")}
    else uploadResult.value=`❌ ${r?.error||"失败"}`
  }catch(e){uploadResult.value="❌ "+e.message}
  loading.value=false
}
async function askRag() {
  if(!question.value.trim())return
  loading.value=true;ragAnswer.value="";ragSources.value=[]
  try {
    const r=await agentApi.post("/rag/ask",{question:question.value,top_k:5})
    if(r?.ok){ragAnswer.value=r.answer?.replace(/\n/g,"<br>");ragSources.value=r.sources||[]}
    else ragAnswer.value=r?.error||"无结果"
  }catch(e){ragAnswer.value="搜索失败: "+e.message}
  loading.value=false
}
async function loadStats() {
  loading.value=true
  try {const r=await agentApi.get("/rag/stats");if(r?.ok)stats.value=r}catch(e){}
  loading.value=false
}
async function ingestText() {
  if(!batchText.value.trim())return
  loading.value=true
  try {
    const r=await agentApi.post("/rag/ingest",{text:batchText.value,source:batchSource.value||"手动导入"})
    if(r?.ok){ElMessage.success(`摄入成功: ${r.doc_id}`);batchText.value=""}
  }catch(e){ElMessage.error(e.message)}
  loading.value=false
}
</script>
<style scoped>.page-shell{max-width:800px;margin:0 auto;padding:20px}.page-header{margin-bottom:16px}.page-header h2{font-size:20px;color:#e0e0ff;margin:0}.page-header p{font-size:12px;color:rgba(255,255,255,.5)}.result-box{margin-top:12px;padding:14px;background: rgba(0,0,0,0.2);border:1px solid rgba(102,126,234,.2);border-radius:10px;font-size:13px;color:#e0e0e0;line-height:1.7}</style>