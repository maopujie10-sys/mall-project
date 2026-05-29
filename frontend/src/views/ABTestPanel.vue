<template><div class="page-shell"><div class="page-header"><h2>🧪 A/B测试引擎</h2><p>自动分流+数据对比+AI决策</p></div>
<el-row :gutter="16"><el-col :span="12"><el-card><template #header>🆕 创建实验</template>
<el-input v-model="expName" placeholder="实验名称"/><el-input v-model="variantA" placeholder="变体A" style="margin-top:8px"/>
<el-input v-model="variantB" placeholder="变体B" style="margin-top:8px"/>
<el-button type="primary" style="margin-top:8px" @click="createExp">创建</el-button></el-card></el-col>
<el-col :span="12"><el-card><template #header>📊 实验列表</template>
<el-empty v-if="!exps.length" description="暂无实验"/>
<div v-for="e in exps" :key="e.exp_id" class="exp-item"><span>{{ e.name }}</span><el-tag size="small">{{ e.status }}</el-tag></div>
</el-card></el-col></el-row></div></template>
<script setup>import {ref} from "vue";import {ElMessage} from "element-plus";import {agentApi} from "@/api";
const expName=ref("");const variantA=ref("对照组");const variantB=ref("实验组");const exps=ref([]);
async function createExp(){if(!expName.value)return;
try{const r=await agentApi.post("/agent/abtest/create",{name:expName.value,variants:[variantA.value,variantB.value]});
if(r?.data?.ok){ElMessage.success("实验创建: "+r.data.exp_id);exps.value.push({exp_id:r.data.exp_id,name:expName.value,status:"running"});expName.value=""}}catch(e){ElMessage.error(e.message)}}</script>
<style scoped>.page-shell{max-width:900px;margin:0 auto;padding:20px;}.page-header{margin-bottom:16px;}.page-header h2{font-size:20px;color:#e0e0ff;margin:0;}.page-header p{font-size:12px;color:rgba(255,255,255,0.5);margin:4px 0;}.exp-item{display:flex;justify-content:space-between;padding:10px;background:rgba(102,126,234,0.06);border-radius:8px;margin-bottom:6px;font-size:13px;color:#e0e0e0;}@media(max-width:768px){.page-shell{padding:10px;}}</style>
