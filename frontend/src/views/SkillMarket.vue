<template><div class="page-shell"><div class="page-header"><h2>🧩 技能市场</h2><p>30+ AI技能 · 一键安装 · 社区共享</p></div>
<el-row :gutter="12"><el-col :span="6"><el-input v-model="search" placeholder="搜索技能..." clearable/></el-col>
<el-col :span="18"><el-radio-group v-model="cat" size="small"><el-radio-button value="">全部({{total}})</el-radio-button>
<el-radio-button v-for="c in categories" :key="c.category" :value="c.category">{{c.icon}} {{c.category}}({{c.count}})</el-radio-button></el-radio-group></el-col></el-row>
<div class="skill-grid" style="margin-top:16px"><div v-for="s in filtered" :key="s.id" class="skill-card" :class="{installed:s.installed}">
<div class="skill-top"><span class="skill-icon">{{s.icon}}</span><span class="skill-version">v{{s.version}}</span></div>
<div class="skill-name">{{s.name}}</div><div class="skill-desc">{{s.desc}}</div>
<div class="skill-meta"><span>⭐{{s.stars}}</span><span>⬇{{s.downloads}}</span><span>@{{s.author}}</span></div>
<el-button size="small" :type="s.installed?'':'primary'" @click="toggleInstall(s)" :loading="s._loading">
{{s.installed ? '已安装' : '安装'}}</el-button></div></div>
<el-empty v-if="!filtered.length" description="没有匹配的技能"/></div></template>
<script setup>
import {ref,computed,onMounted} from "vue";import {ElMessage} from "element-plus";import {agentApi} from "@/api"
const search=ref("");const cat=ref("");const plugins=ref([]);const categories=ref([]);const total=ref(0)
onMounted(async()=>{try{const r=await agentApi.get("/agent/plugins/marketplace");if(r?.data?.ok){plugins.value=r.data.plugins||[];categories.value=r.data.categories||[];total.value=r.data.count||0}}catch(e){}})
const filtered=computed(()=>{let list=plugins.value;if(cat.value)list=list.filter(p=>p.category===cat.value);if(search.value)list=list.filter(p=>p.name.includes(search.value)||p.desc.includes(search.value)||(p.tags||[]).some(t=>t.includes(search.value)));return list})
async function toggleInstall(s){s._loading=true
try{if(s.installed){const r=await agentApi.delete("/agent/plugins/"+s.id);if(r?.data?.ok){s.installed=false;ElMessage.success("已卸载")}}
else{const r=await agentApi.post("/agent/plugins/install",{plugin_id:s.id});if(r?.data?.ok){s.installed=true;ElMessage.success("已安装: "+s.name)}}}
catch(e){ElMessage.error(e.message)}s._loading=false}
</script>
<style scoped>.page-shell{max-width:1100px;margin:0 auto;padding:20px}.page-header{margin-bottom:16px}.page-header h2{font-size:20px;color:#e0e0ff;margin:0}.page-header p{font-size:12px;color:rgba(255,255,255,.5);margin:4px 0}.skill-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px}.skill-card{padding:16px;background:rgba(15,15,35,.8);border:1px solid rgba(102,126,234,.2);border-radius:12px;transition:all .2s}.skill-card:hover{border-color:rgba(102,126,234,.5);transform:translateY(-2px)}.skill-card.installed{border-color:rgba(74,222,128,.3)}.skill-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}.skill-icon{font-size:28px}.skill-version{font-size:10px;color:rgba(255,255,255,.3)}.skill-name{font-size:14px;font-weight:600;color:#e0e0ff;margin-bottom:4px}.skill-desc{font-size:12px;color:rgba(255,255,255,.5);margin-bottom:8px;line-height:1.4}.skill-meta{display:flex;gap:12px;font-size:11px;color:rgba(255,255,255,.35);margin-bottom:10px}@media(max-width:768px){.page-shell{padding:10px}.skill-grid{grid-template-columns:repeat(auto-fill,minmax(150px,1fr))}}</style>