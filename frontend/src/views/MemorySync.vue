<template><div class="page-shell"><div class="page-header"><h2>🔄 跨平台记忆同步</h2><p>微信/Telegram/Web 统一记忆</p></div>
<el-row :gutter="16"><el-col :span="8" v-for="p in platforms" :key="p.id"><el-card>
<template #header>{{p.icon}} {{p.name}}</template>
<el-tag :type="p.connected?'success':'info'">{{p.connected?'已连接':'待配置'}}</el-tag>
<div style="margin-top:8px;font-size:12px;color:rgba(255,255,255,0.5)">{{p.status}}</div>
</el-card></el-col></el-row><el-card style="margin-top:16px"><template #header>🧠 共享记忆</template>
<el-empty description="连接平台后将自动同步对话记忆"/></el-card></div></template>
<script setup>import {ref} from "vue";
const platforms=ref([{id:"telegram",icon:"✈️",name:"Telegram",connected:true,status:"@mytianyou_bot"},
{id:"wechat",icon:"💬",name:"微信",connected:false,status:"需配置WECHAT_TOKEN"},
{id:"web",icon:"🌐",name:"Web",connected:true,status:"tiktook.eu.cc/ai/"}])</script>
<style scoped>.page-shell{max-width:900px;margin:0 auto;padding:20px;}.page-header{margin-bottom:16px;}.page-header h2{font-size:20px;color:#e0e0ff;margin:0;}.page-header p{font-size:12px;color:rgba(255,255,255,0.5);margin:4px 0;}</style>
