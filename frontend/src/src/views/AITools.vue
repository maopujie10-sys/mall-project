<template><div class="page-shell"><div class="page-header"><h2> AI</h2>-</div>
<el-tabs v-model="tab" type="border-card">

<el-tab-pane label=" " name="code">
<el-radio-group v-model="lang" size="small" style="margin-bottom:8px"><el-radio-button value="python">Python</el-radio-button><el-radio-button value="sql">SQL</el-radio-button></el-radio-group>
<el-input v-model="code" type="textarea" :rows="6" :placeholder="lang==='python'?'print(sum(range(1,101)))  # Python':'SELECT COUNT(*) FROM products  # SQL''/>

<div v-if="codeResult" class="result-box"><pre>{{codeResult}}</pre></div></el-tab-pane>

<el-tab-pane label=" " name="search">
<el-input v-model="searchQ" placeholder="..." @keydown.enter="runSearch"/><el-button type="primary" @click="runSearch" :loading="loading" style="margin-left:8px">OK</el-button>
<div v-if="searchResults.length" class="search-list"><div v-for="r in searchResults" :key="r.url" class="search-item"><a :href="r.url" target="_blank" class="search-title">{{r.title}}</a><div class="search-snippet">{{r.snippet}}</div></div></div></el-tab-pane>

<el-tab-pane label=" " name="image">
<el-input v-model="imgPrompt" placeholder="..." type="textarea" :rows="3"/><el-button type="primary" @click="genImage" :loading="loading" style="margin-top:8px"> DALL-E</el-button>
<div v-if="genImages.length" class="image-grid">-</el-tab-pane>

<el-tab-pane label=" " name="usage">
<el-button @click="loadUsage" :loading="loading">OK</el-button>
<div v-if="usage"><div class="stat-row"><span>Token:</span><b>{{usage.total_tokens_in?.toLocaleString()}}</b></div><div class="stat-row"><span>Token:</span><b>{{usage.total_tokens_out?.toLocaleString()}}</b></div><div class="stat-row"><span>:</span><b style="color:#fbbf24">${{usage.total_cost?.toFixed(4)}}</b></div>
<div v-if="usage.models?.length" style="margin-top:12px"><div v-for="m in usage.models" :key="m.model" class="stat-row"><span>{{m.model}}:</span><span>{{(m.tokens_in+m.tokens_out).toLocaleString()}} tokens / ${{m.cost.toFixed(4)}} ({{m.calls}})</span></div></div></div></el-tab-pane>

<el-tab-pane label=" " name="eval">
<el-input v-model="evalQ" placeholder=''/><el-input v-model="evalA" placeholder="AI" type="textarea" :rows="3" style="margin-top:8px"/><el-input v-model="evalE" placeholder="()" style="margin-top:8px"/>
<el-button type="primary" @click="runEval" :loading="loading" style="margin-top:8px">OK</el-button>
<div v-if="evalResult" class="result-box"><div class="eval-score">: {{evalResult.score}}/10</div><div>{{evalResult.feedback}}</div></div></el-tab-pane>

</el-tabs></div></template>
<script setup>
import {ref,onMounted} from "vue";import {ElMessage} from "element-plus";import {agentApi} from "@/api"
const tab=ref("code");const loading=ref(false)
const lang=ref("python");const code=ref('');const codeResult=ref('')
const searchQ=ref('');const searchResults=ref([])
const imgPrompt=ref('');const genImages=ref([])
const usage=ref(null)
const evalQ=ref('');const evalA=ref('');const evalE=ref('');const evalResult=ref(null)
const api=async(u,b)=>{loading.value=true;try{const r=await agentApi.post(u,b);loading.value=false;return r?.data}catch(e){loading.value=false;ElMessage.error(e.message)}}
async function runCode(){const d=await api("/agent/tools/code",{code:code.value,language:lang.value});codeResult.value=d?.ok?d.output||JSON.stringify(d.result,null,2):d?.error}
async function runSearch(){const d=await api("/agent/tools/search",{query:searchQ.value});searchResults.value=d?.ok?d.results||[]:[]}
async function genImage(){const d=await api("/agent/tools/image-gen",{prompt:imgPrompt.value});genImages.value=d?.ok?d.images||[]:[]}
async function loadUsage(){const r=await agentApi.get("/agent/tools/usage");usage.value=r?.data}
async function runEval(){const d=await api("/agent/tools/eval",{question:evalQ.value,answer:evalA.value,expected:evalE.value});evalResult.value=d}
onMounted(()=>loadUsage())
</script>
<style scoped>.page-shell{max-width:900px;margin:0 auto;padding:20px}.page-header{margin-bottom:16px}.page-header h2{font-size:20px;color:#e0e0ff;margin:0}.page-header p{font-size:12px;color:rgba(255,255,255,.5);margin:4px 0}.result-box{margin-top:12px;padding:14px;background: rgba(0,0,0,0.2);border:1px solid rgba(102,126,234,.2);border-radius:10px;max-height:400px;overflow:auto}.result-box pre{color:#a0c4ff;font-size:13px;white-space:pre-wrap;margin:0}.search-item{padding:10px;border-bottom:1px solid rgba(255,255,255,.05)}.search-title{color:#667eea;font-size:14px;text-decoration:none}.search-snippet{color:rgba(255,255,255,.5);font-size:12px;margin-top:4px}.image-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin-top:12px}.gen-img{width:100%;border-radius:10px;border:1px solid rgba(255,255,255,.1)}.stat-row{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid rgba(255,255,255,.05);font-size:13px;color:#e0e0e0}.eval-score{font-size:28px;font-weight:700;color:#fbbf24;margin-bottom:8px}@media(max-width:768px){.page-shell{padding:10px}}</style>