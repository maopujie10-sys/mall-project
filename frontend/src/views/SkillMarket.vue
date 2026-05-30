<template><div class="page-shell">
<div class="page-header">-<p>AI    30+</p></div>

<el-input v-model="search" placeholder="..." clearable size="large" style="margin-bottom:16px"/>

<el-row :gutter="12">
<el-col :span="8" v-for="skill in filteredSkills" :key="skill.name" style="margin-bottom:12px">
<el-card shadow="hover">
  <template #header>
    <div style="display:flex;justify-content:space-between;align-items:center">
      <span>{{skill.icon}} {{skill.display_name||skill.name}}</span>
      <el-tag :type="skill.installed?'success':'info'' size="small">{{skill.installed?'':''}}</el-tag>
    </div>
  </template>
  <div style="font-size:12px;color:rgba(255,255,255,.6);min-height:40px">{{skill.description||''}}</div>
  <div style="margin-top:8px;font-size:11px;color:rgba(255,255,255,.3)">
    v{{skill.version||'1.0'}}  {{skill.author||''}}  {{skill.downloads||0}}
  </div>
  <el-button :type="skill.installed?'danger':'primary'' size="small" @click="skill.installed?uninstall(skill):install(skill)" :loading="skill._loading" style="margin-top:8px;width:100%">
    {{skill.installed?'':''}}
  </el-button>
</el-card>
</el-col>
</el-row>

-

<el-divider> </el-divider>
<el-tag v-for="s in installedSkills" :key="s.name" style="margin:4px" closable @close="uninstall(s)">{{s.icon}} {{s.display_name}}</el-tag>
-</div></template>

<script setup>
import {ref,computed,onMounted} from "vue";import {ElMessage} from "element-plus";import {agentApi} from "@/api"
const search=ref('');const skills=ref([]);const installed=ref([])

const filteredSkills=computed(()=>{
  if(!search.value)return skills.value.filter(s=>!s.installed)
  const q=search.value.toLowerCase()
  return skills.value.filter(s=>(s.display_name||s.name).toLowerCase().includes(q)||(s.description||'').toLowerCase().includes(q))
})
const installedSkills=computed(()=>skills.value.filter(s=>s.installed))

onMounted(async()=>{
  try{
    const r=await agentApi.get("/agent/plugins/marketplace")
    if(r?.data?.ok)skills.value=(r.data.plugins||r.data.skills||[]).map(s=>({...s,installed:false,_loading:false}))
  }catch(e){
    // Fallback: 
    skills.value=[
      {name:'',display_name:'',icon:"",description:"AI",version:"1.2",author:'',downloads:1230},
      {name:'',display_name:'',icon:"",description:'',version:"1.0",author:'',downloads:890},
      {name:'',display_name:'',icon:"",description:'',version:"1.1",author:'',downloads:670},
      {name:'',display_name:'',icon:"",description:"//",version:"1.3",author:'',downloads:1500},
      {name:'',display_name:'',icon:"",description:"12",version:"1.0",author:'',downloads:560},
      {name:'',display_name:'',icon:"",description:"/",version:"1.0",author:'',downloads:430},
      {name:'',display_name:'',icon:"",description:"/",version:"1.0",author:'',downloads:320},
      {name:"SEO",display_name:"SEO",icon:"",description:'',version:"1.0",author:'',downloads:280},
      {name:'',display_name:"AI",icon:"",description:'',version:"1.0",author:'',downloads:190},
    ].map(s=>({...s,installed:false,_loading:false}))
  }
  try{
    const r2=await agentApi.get("/agent/plugins/installed/packages")
    if(r2?.data?.ok)installed.value=r2.data.plugins||[]
  }catch(e){}
})

async function install(skill){
  skill._loading=true
  try{
    const r=await agentApi.post("/agent/plugins/install",{plugin_id:skill.id})
    if(r?.data?.ok){skill.installed=true;ElMessage.success(` ${skill.display_name}`)}
    else ElMessage.error(r?.data?.error||'')
  }catch(e){ElMessage.error(e.message)}
  skill._loading=false
}
async function uninstall(skill){
  skill._loading=true
  try{
    const r=await agentApi.post("/agent/plugins/uninstall",{plugin_id:skill.id})
    if(r?.data?.ok){skill.installed=false;ElMessage.success(` ${skill.display_name}`)}
    else ElMessage.error(r?.data?.error||'')
  }catch(e){ElMessage.error(e.message)}
  skill._loading=false
}
</script>
<style scoped>.page-shell{max-width:1000px;margin:0 auto;padding:20px}.page-header{margin-bottom:16px}.page-header h2{font-size:20px;color:#e0e0ff;margin:0}.page-header p{font-size:12px;color:rgba(255,255,255,.5)}</style>