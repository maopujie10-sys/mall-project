<template><div class="page-shell"><div class="page-header"><h2>🧩 技能市场</h2><p>社区上传+审核+一键安装AI技能</p></div>
<el-input v-model="searchSkill" placeholder="搜索技能..." style="margin-bottom:16px"/>
<div class="skill-grid"><div v-for="s in filteredSkills" :key="s.id" class="skill-card">
<div class="skill-icon">{{ s.icon }}</div><div class="skill-name">{{ s.name }}</div>
<div class="skill-desc">{{ s.desc }}</div><el-button size="small" type="primary" @click="installSkill(s)">安装</el-button>
</div></div></div></template>
<script setup>import {ref,computed} from "vue";import {ElMessage} from "element-plus";
const searchSkill=ref("");const skills=ref([{id:"auto_desc",icon:"📝",name:"自动描述生成",desc:"AI生成商品详情"},{id:"price_opt",icon:"💰",name:"智能定价",desc:"竞品比价自动调价"},{id:"social_post",icon:"📱",name:"社媒发布",desc:"自动发帖到多平台"},{id:"inv_mgr",icon:"📦",name:"库存预警",desc:"低库存自动提醒"},{id:"fraud_detect",icon:"🛡️",name:"反欺诈",desc:"异常订单检测"},{id:"email_camp",icon:"📧",name:"邮件营销",desc:"自动化邮件推广"}]);
const filteredSkills=computed(()=>skills.value.filter(s=>s.name.includes(searchSkill.value)||s.desc.includes(searchSkill.value)));
function installSkill(s){ElMessage.success("已安装: "+s.name)}</script>
<style scoped>.page-shell{max-width:900px;margin:0 auto;padding:20px;}.page-header{margin-bottom:16px;}.page-header h2{font-size:20px;color:#e0e0ff;margin:0;}.page-header p{font-size:12px;color:rgba(255,255,255,0.5);margin:4px 0;}.skill-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;}.skill-card{padding:16px;background:rgba(15,15,35,0.8);border:1px solid rgba(102,126,234,0.2);border-radius:12px;text-align:center;}.skill-icon{font-size:32px;margin-bottom:8px;}.skill-name{font-size:14px;font-weight:600;color:#e0e0ff;}.skill-desc{font-size:12px;color:rgba(255,255,255,0.5);margin:6px 0;}</style>
