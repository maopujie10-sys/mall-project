<template><div class="page-shell">
<div class="page-header"><h2>Skill Market</h2><p>30+ AI Skills — one-click install</p></div>

<el-input v-model="search" placeholder="Search skills..." clearable size="large" style="margin-bottom:16px"/>

<el-row :gutter="12">
<el-col :span="8" v-for="skill in filteredSkills" :key="skill.name" style="margin-bottom:12px">
<el-card shadow="hover">
  <template #header>
    <div style="display:flex;justify-content:space-between;align-items:center">
      <span>{{skill.icon}} {{skill.display_name||skill.name}}</span>
      <el-tag :type="skill.installed?'success':'info'" size="small">{{skill.installed?'Installed':'Available'}}</el-tag>
    </div>
  </template>
  <div style="font-size:12px;color:rgba(255,255,255,.6);min-height:40px">{{skill.description||skill.desc||''}}</div>
  <div style="margin-top:8px;font-size:11px;color:rgba(255,255,255,.3)">
    v{{skill.version||'1.0'}} by {{skill.author||'Friday'}} | {{skill.downloads||0}} downloads
  </div>
  <el-button :type="skill.installed?'danger':'primary'" size="small" @click="skill.installed?uninstall(skill):install(skill)" :loading="skill._loading" style="margin-top:8px;width:100%">
    {{skill.installed?'Uninstall':'Install'}}
  </el-button>
</el-card>
</el-col>
</el-row>

<el-divider>Installed Skills</el-divider>
<div v-if="installedSkills.length===0" style="color:rgba(255,255,255,.4);text-align:center;padding:20px">No skills installed yet. Browse above and click Install.</div>
<el-tag v-for="s in installedSkills" :key="s.name" style="margin:4px" closable @close="uninstall(s)">{{s.icon}} {{s.display_name}}</el-tag>
</div></template>

<script setup>
import {ref,computed,onMounted} from "vue";import {ElMessage} from "element-plus";import {agentApi} from "@/api"
const search=ref('');const skills=ref([]);const installed=ref([])

const filteredSkills=computed(()=>{
  if(!search.value)return skills.value.filter(s=>!s.installed)
  const q=search.value.toLowerCase()
  return skills.value.filter(s=>(s.display_name||s.name).toLowerCase().includes(q)||(s.description||s.desc||'').toLowerCase().includes(q))
})
const installedSkills=computed(()=>skills.value.filter(s=>s.installed))

onMounted(async()=>{
  try{
    const r=await agentApi.get("/agent/plugins/marketplace")
    if(r?.data?.ok)skills.value=(r.data.plugins||r.data.skills||[]).map(s=>({...s,installed:false,_loading:false}))
  }catch(e){
    skills.value=[
      {id:"server-monitor",name:"Server Monitor",display_name:"Server Monitor",icon:"🖥️",description:"Real-time CPU/RAM/Disk monitoring dashboard",version:"2.0",author:"Friday",downloads:1280},
      {id:"docker-manager",name:"Docker Manager",display_name:"Docker Manager",icon:"🐳",description:"Container start/stop/logs/image management",version:"1.5",author:"Friday",downloads:960},
      {id:"auto-backup",name:"Auto Backup",display_name:"Auto Backup",icon:"📁",description:"Scheduled database and file backups",version:"1.0",author:"Friday",downloads:1100},
      {id:"scraper-engine",name:"Scraper Engine",display_name:"Scraper Engine",icon:"🔍",description:"7-platform product scraping engine",version:"2.1",author:"Friday",downloads:890},
      {id:"ai-chat",name:"AI Chat",display_name:"AI Chat",icon:"🤖",description:"Multi-model AI chat assistant",version:"2.0",author:"Friday",downloads:3200},
      {id:"security-center",name:"Security Center",display_name:"Security Center",icon:"🛡️",description:"IP blacklist and firewall rules",version:"2.0",author:"Friday",downloads:1050},
      {id:"mall-manager",name:"Mall Manager",display_name:"Mall Manager",icon:"🏪",description:"Full e-commerce management suite",version:"3.0",author:"Friday",downloads:2100},
      {id:"rotation-system",name:"Rotation System",display_name:"Rotation System",icon:"🔄",description:"Domain rotation and health checks",version:"2.0",author:"Friday",downloads:1150},
      {id:"emergency-kill",name:"Emergency Kill",display_name:"Emergency Kill",icon:"⚠️",description:"One-click emergency shutdown",version:"1.0",author:"Friday",downloads:1350},
    ].map(s=>({...s,installed:false,_loading:false}))
  }
  try{
    const r2=await agentApi.get("/agent/plugins/installed/packages")
    if(r2?.data?.ok){
      const ids=new Set((r2.data.plugins||[]).map(p=>p.id||p.name))
      skills.value.forEach(s=>{if(ids.has(s.id||s.name))s.installed=true})
    }
  }catch(e){}
})
async function install(skill){
  skill._loading=true
  try{
    const r=await agentApi.post("/agent/plugins/install",{plugin_id:skill.id})
    if(r?.data?.ok){skill.installed=true;ElMessage.success("Installed "+skill.display_name)}
    else ElMessage.error(r?.data?.error||"Install failed")
  }catch(e){ElMessage.error(e.message)}
  skill._loading=false
}
async function uninstall(skill){
  skill._loading=true
  try{
    const r=await agentApi.post("/agent/plugins/uninstall",{plugin_id:skill.id})
    if(r?.data?.ok){skill.installed=false;ElMessage.success("Removed "+skill.display_name)}
    else ElMessage.error(r?.data?.error||"Uninstall failed")
  }catch(e){ElMessage.error(e.message)}
  skill._loading=false
}
</script>
<style scoped>.page-shell{max-width:1000px;margin:0 auto;padding:20px}.page-header{margin-bottom:16px}.page-header h2{font-size:20px;color:#e0e0ff;margin:0}.page-header p{font-size:12px;color:rgba(255,255,255,.5)}</style>