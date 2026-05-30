<template><div class="page-shell"><div class="page-header">-<p>  RBAC</p></div>
<el-row :gutter="16"><el-col :span="12"><el-card><template #header> </template>
<el-input v-model="newUser" placeholder='Enter...' style="margin-bottom:8px"/>
<el-input v-model="newPass" placeholder='Enter...' type="password" style="margin-bottom:8px"/>
<el-select v-model="newRole" placeholder=''><el-option label='Status' value="admin"/><el-option label='Status' value="operator"/><el-option label='Status' value="viewer"/></el-select>
<el-button type="primary" style="margin-top:8px;width:100%" @click="createUser" :loading="creating">OK</el-button>
</el-card></el-col>
<el-col :span="12"><el-card><template #header>  ({{users.length}})</template>
<div v-if="!users.length" style="text-align:center;padding:20px;color:rgba(255,255,255,0.4)">...</div>
<div v-for="u in users" :key="u.username" class="user-row"><div><div class="user-name">{{u.username}}</div><div class="user-meta">{{u.role}}  {{u.created_at?.slice(0,10)}}</div></div>
<el-dropdown @command="(cmd)=>roleAction(u.username,cmd)"><el-tag :type="u.role==='admin'?'danger':u.role==='operator'?'warning':'info' style="cursor:pointer">{{u.role}}</el-tag>
<template #dropdown><el-dropdown-menu><el-dropdown-item command="admin">admin</el-dropdown-item><el-dropdown-item command="operator">operator</el-dropdown-item><el-dropdown-item command="viewer">viewer</el-dropdown-item><el-dropdown-item divided command="delete">-</el-dropdown-item></el-dropdown-menu></template>
</el-dropdown></div></el-card></el-col></el-row></div></template>
<script setup>
import {ref,onMounted} from "vue";import {ElMessage,ElMessageBox} from "element-plus";import {agentApi} from "@/api"
const users=ref([]);const newUser=ref('');const newPass=ref('');const newRole=ref("viewer");const creating=ref(false)
onMounted(async()=>{try{const r=await agentApi.get("/agent/auth/users");if(r?.data?.ok)users.value=r.data.users}catch(e){}})
async function createUser(){if(!newUser.value||!newPass.value)return ElMessage.warning('Warning');creating.value=true
try{const r=await agentApi.post("/agent/auth/users",{username:newUser.value,password:newPass.value,role:newRole.value})
if(r?.data?.ok){ElMessage.success('OK');users.value.push({username:newUser.value,role:newRole.value,created_at:new Date().toISOString()});newUser.value='';newPass.value=''}}catch(e){ElMessage.error(e.message)}creating.value=false}
async function roleAction(uname,cmd){if(cmd==="delete"){try{await ElMessageBox.confirm(''+uname+"?",'',{type:"warning"})}catch{return}}
try{const isDel=cmd==="delete";const r=isDel?await agentApi.delete("/agent/auth/users/"+uname):await agentApi.patch("/agent/auth/users/"+uname+"/role",{role:cmd})
if(r?.data?.ok){ElMessage.success(isDel?'':'');if(isDel)users.value=users.value.filter(u=>u.username!==uname);else{const u=users.value.find(u=>u.username===uname);if(u)u.role=cmd}}}catch(e){ElMessage.error(e.message)}}
</script>
<style scoped>.page-shell{max-width:900px;margin:0 auto;padding:20px}.page-header{margin-bottom:16px}.page-header h2{font-size:20px;color:#e0e0ff;margin:0}.page-header p{font-size:12px;color:rgba(255,255,255,.5);margin:4px 0}.user-row{display:flex;justify-content:space-between;align-items:center;padding:10px;background:rgba(102,126,234,.06);border-radius:8px;margin-bottom:6px}.user-name{color:#e0e0e0;font-size:14px;font-weight:600}.user-meta{font-size:11px;color:rgba(255,255,255,.4);margin-top:2px}@media(max-width:768px){.page-shell{padding:10px}}</style>