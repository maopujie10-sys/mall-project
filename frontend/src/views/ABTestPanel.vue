<template><div class="page-shell"><div class="page-header"><h2> A/B</h2><p>++AI</p></div>
<el-row :gutter="16"><el-col :span="12"><el-card><template #header> </template>
<el-input v-model="expName" placeholder=''/><el-input v-model="variantA" placeholder="A" style="margin-top:8px"/>
<el-input v-model="variantB" placeholder="B" style="margin-top:8px"/>
<el-button type="primary" style="margin-top:8px" @click="createExp">OK</el-button></el-card></el-col>
<el-col :span="12"><el-card><template #header> </template>
<el-empty v-if="!exps.length" description=''/>
<div v-for="e in exps" :key="e.exp_id" class="exp-item"><span>{{ e.name }}</span><el-tag size="small">{{ e.status }}</el-tag></div>
</el-card></el-col></el-row></div></template>
<script setup>import {ref} from "vue";import {ElMessage} from "element-plus";import {agentApi} from "@/api";
const expName=ref('');const variantA=ref('');const variantB=ref('');const exps=ref([]);
async function createExp(){if(!expName.value)return;
try{const r=await agentApi.post("/agent/abtest/create",{name:expName.value,variants:[variantA.value,variantB.value]});
if(r?.data?.ok){ElMessage.success(": "+r.data.exp_id);exps.value.push({exp_id:r.data.exp_id,name:expName.value,status:"running"});expName.value=''}}catch(e){ElMessage.error(e.message)}}</script>
<style scoped>.page-shell{max-width:900px;margin:0 auto;padding:20px;}.page-header{margin-bottom:16px;}.page-header h2{font-size:20px;color:#e0e0ff;margin:0;}.page-header p{font-size:12px;color:rgba(255,255,255,0.5);margin:4px 0;}.exp-item{display:flex;justify-content:space-between;padding:10px;background:rgba(102,126,234,0.06);border-radius:8px;margin-bottom:6px;font-size:13px;color:#e0e0e0;}@media(max-width:768px){.page-shell{padding:10px;}}</style>
