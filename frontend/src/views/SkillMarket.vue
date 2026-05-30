<template><div class="page-shell">
<div class="page-header"><h2>🧩 技能市场</h2><p>AI技能一键安装 · 社区共享 · 30+官方技能</p></div>

<el-input v-model="search" placeholder="搜索技能..." clearable size="large" style="margin-bottom:16px"/>

<el-row :gutter="12">
<el-col :span="8" v-for="skill in filteredSkills" :key="skill.name" style="margin-bottom:12px">
<el-card shadow="hover">
  <template #header>
    <div style="display:flex;justify-content:space-between;align-items:center">
      <span>{{skill.icon}} {{skill.display_name||skill.name}}</span>
      <el-tag :type="skill.installed?'success':'info'" size="small">{{skill.installed?'已安装':'可安装'}}</el-tag>
    </div>
  </template>
  <div style="font-size:12px;color:rgba(255,255,255,.6);min-height:40px">{{skill.description||'暂无描述'}}</div>
  <div style="margin-top:8px;font-size:11px;color:rgba(255,255,255,.3)">
    v{{skill.version||'1.0'}} · {{skill.author||'官方'}} · ⬇{{skill.downloads||0}}
  </div>
  <el-button :type="skill.installed?'danger':'primary'" size="small" @click="skill.installed?uninstall(skill):install(skill)" :loading="skill._loading" style="margin-top:8px;width:100%">
    {{skill.installed?'卸载':'安装'}}
  </el-button>
</el-card>
</el-col>
</el-row>

<div v-if="!filteredSkills.length" style="text-align:center;padding:40px;color:rgba(255,255,255,.3)">暂无匹配技能</div>

<el-divider>📦 已安装技能</el-divider>
<el-tag v-for="s in installedSkills" :key="s.name" style="margin:4px" closable @close="uninstall(s)">{{s.icon}} {{s.display_name}}</el-tag>
<div v-if="!installedSkills.length" style="font-size:12px;color:rgba(255,255,255,.3)">尚未安装任何技能</div></div></template>

<script setup>
import {ref,computed,onMounted} from "vue";import {ElMessage} from "element-plus";import {agentApi} from "@/api"
const search=ref("");const skills=ref([]);const installed=ref([])

const filteredSkills=computed(()=>{
  if(!search.value)return skills.value.filter(s=>!s.installed)
  const q=search.value.toLowerCase()
  return skills.value.filter(s=>(s.display_name||s.name).toLowerCase().includes(q)||(s.description||"").toLowerCase().includes(q))
})
const installedSkills=computed(()=>skills.value.filter(s=>s.installed))

onMounted(async()=>{
  try{
    const r=await agentApi.get("/plugins/marketplace")
    if(r?.ok)skills.value=(r.plugins||r.skills||[]).map(s=>({...s,installed:false,_loading:false}))
  }catch(e){
    // Fallback: 内置技能列表
    skills.value=[
      {name:"商品文案生成",display_name:"商品文案",icon:"📝",description:"AI自动生成多语言商品标题和描述",version:"1.2",author:"官方",downloads:1230},
      {name:"客服自动回复",display_name:"客服回复",icon:"💬",description:"智能匹配常见问题自动回复",version:"1.0",author:"官方",downloads:890},
      {name:"竞品监控",display_name:"竞品监控",icon:"👁️",description:"自动采集竞品价格和库存变化",version:"1.1",author:"官方",downloads:670},
      {name:"图片优化",display_name:"图片处理",icon:"🖼️",description:"批量去背景/加水印/压缩",version:"1.3",author:"官方",downloads:1500},
      {name:"多语言翻译",display_name:"翻译引擎",icon:"🌍",description:"12种语言自动翻译商品信息",version:"1.0",author:"官方",downloads:560},
      {name:"数据看板",display_name:"数据看板",icon:"📊",description:"销售趋势/库存预警可视化",version:"1.0",author:"官方",downloads:430},
      {name:"订单预警",display_name:"订单预警",icon:"🔔",description:"异常订单/退款实时告警",version:"1.0",author:"官方",downloads:320},
      {name:"SEO优化",display_name:"SEO助手",icon:"🚀",description:"自动优化商品标题和关键词",version:"1.0",author:"官方",downloads:280},
      {name:"库存预测",display_name:"库存AI",icon:"📦",description:"基于销量预测补货时间",version:"1.0",author:"官方",downloads:190},
    ].map(s=>({...s,installed:false,_loading:false}))
  }
  try{
    const r2=await agentApi.get("/plugins/installed")
    if(r2?.ok)installed.value=r2.plugins||[]
  }catch(e){}
})

async function install(skill){
  skill._loading=true
  try{
    const r=await agentApi.post("/plugins/install",{name:skill.name})
    if(r?.data?.ok){skill.installed=true;ElMessage.success(`已安装 ${skill.display_name}`)}
    else ElMessage.error(r?.data?.error||"安装失败")
  }catch(e){ElMessage.error(e.message)}
  skill._loading=false
}
async function uninstall(skill){
  skill._loading=true
  try{
    const r=await agentApi.post("/plugins/uninstall",{name:skill.name})
    if(r?.data?.ok){skill.installed=false;ElMessage.success(`已卸载 ${skill.display_name}`)}
    else ElMessage.error(r?.data?.error||"卸载失败")
  }catch(e){ElMessage.error(e.message)}
  skill._loading=false
}
</script>
<style scoped>.page-shell{max-width:1000px;margin:0 auto;padding:20px}.page-header{margin-bottom:16px}.page-header h2{font-size:20px;color:#e0e0ff;margin:0}.page-header p{font-size:12px;color:rgba(255,255,255,.5)}</style>