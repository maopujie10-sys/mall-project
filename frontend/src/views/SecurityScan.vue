<template><div class="page-shell"><div class="page-header"><h2>🛡️ 安全扫描</h2><p>AI定期扫描漏洞+自动修复+安全报告</p></div>
<el-button type="primary" size="large" @click="runScan" :loading="scanning">🔍 开始全量扫描</el-button>
<div v-if="result" class="scan-result"><div class="scan-grade" :class="result.grade">安全等级: {{result.grade}} ({{result.score}}分)</div>
<div class="scan-stats"><el-tag type="danger">严重: {{result.critical}}</el-tag><el-tag type="warning">高: {{result.high}}</el-tag>
<el-tag type="info">中: {{result.medium}}</el-tag><el-tag>低: {{result.low}}</el-tag></div>
<div class="scan-checks"><div v-for="c in result.checks" :key="c.name" class="check-item">
<span :class="c.pass?'pass':'fail'">{{c.pass?'✅':'❌'}} {{c.name}}</span><span class="check-detail">{{c.detail}}</span></div></div></div></div></template>
<script setup>import {ref} from "vue";import {ElMessage} from "element-plus";import {agentApi} from "@/api";
const scanning=ref(false);const result=ref(null);
async function runScan(){scanning.value=true;result.value=null;
try{const r=await agentApi.post("/agent/security-scan/full");if(r?.data?.ok)result.value=r.data;else ElMessage.error("扫描失败")}
catch(e){ElMessage.error(e.message)}scanning.value=false}</script>
<style scoped>.page-shell{max-width:900px;margin:0 auto;padding:20px;}.page-header{margin-bottom:16px;}.page-header h2{font-size:20px;color:#e0e0ff;margin:0;}.page-header p{font-size:12px;color:rgba(255,255,255,0.5);margin:4px 0;}.scan-result{margin-top:20px;padding:20px;background:rgba(15,15,35,0.8);border:1px solid rgba(102,126,234,0.2);border-radius:12px;}.scan-grade{font-size:24px;font-weight:700;margin-bottom:12px;}.scan-grade.A{color:#4ade80;}.scan-grade.B{color:#fbbf24;}.scan-grade.C{color:#f87171;}.scan-grade.D{color:#ef4444;}.scan-stats{display:flex;gap:8px;margin-bottom:16px;}.check-item{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);font-size:13px;}.check-item .pass{color:#4ade80;}.check-item .fail{color:#f87171;}.check-detail{color:rgba(255,255,255,0.4);font-size:12px;max-width:50%;text-align:right;}@media(max-width:768px){.page-shell{padding:10px;}}</style>
