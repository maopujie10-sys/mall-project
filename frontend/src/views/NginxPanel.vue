<template>
  <div class="nginx-panel">
    <div class="page-header"><h1> Nginx </h1><p>        SSL</p></div>
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6"><el-card shadow="never"><template #header>?/template>
        <el-tag :type="status?.running ? 'success' : 'danger'' size="large">{{ status?.running ? "? : "? }}</el-tag>
        <div style="margin-top:8px;font-size:12px;color:var(--text-muted)">HTTP: {{ conn?.http_connections || "?" }} | HTTPS: {{ conn?.https_connections || "?" }}</div>
      </el-card></el-col>
      <el-col :span="6"><el-card shadow="never"><template #header></template>
        <el-button @click="testConfig" :loading="cfgLoading" size="small"> nginx -t</el-button>
        <div v-if="cfgResult" :style="{color:cfgResult.ok?'#52c41a':'#ff4d4f',fontSize:'12px',marginTop:'8px'}">{{ cfgResult.ok ? "" : "" }}</div>
      </el-card></el-col>
      <el-col :span="6"><el-card shadow="never"><template #header>?/template>
        <div style="font-size:28px;font-weight:700;color:var(--color-primary)">{{ sites.length }}</div>
        <div style="font-size:12px;color:var(--text-muted)">?/div>
      </el-card></el-col>
      <el-col :span="6"><el-card shadow="never"><template #header></template>
        <el-button type="warning" @click="doReload" :loading="rlLoading" size="small"> Nginx</el-button>
        <el-button @click="fetchAll" :loading="loading" size="small" style="margin-left:8px">OK</el-button>
      </el-card></el-col>
    </el-row>
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card shadow="never"><template #header><span>{{ \('nginx.title') }}</span><el-select v-model="configPath" size="small" style="width:200px;margin-left:12px">
          <el-option label="nginx.conf ? value="/etc/nginx/nginx.conf" />
          <el-option label="default " value="/etc/nginx/sites-enabled/default" />
        </el-select><el-button size="small" @click="fetchConfig" style="margin-left:8px">OK</el-button></template>
        <pre class="code-box">{{ configContent || '' }}</pre>
      </el-card></el-col>
      <el-col :span="12">
        <el-card shadow="never"><template #header> </template>
          <div v-if="errors?.total" style="margin-bottom:12px">?{{ errors.total }} ?/div>
          <div v-for="(cnt,type) in errors?.by_type" :key="type" style="display:flex;align-items:center;gap:8px;margin-bottom:6px;font-size:13px">
            <span style="width:60px">{{ type }}</span><el-progress :percentage="Math.round(cnt/errors.total*100)" :stroke-width="12" :color="type==='error'?'#ff4d4f':type==='warn'?'#faad14':'#1890ff'' />
          </div>
          <el-empty v-if="!errors?.total" description="? />
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="8">
        <el-card shadow="never"><template #header> </template>
          <el-table :data="sites" stripe size="small" max-height="300">
            <el-table-column prop="name" label="? min-width="140" />
            <el-table-column prop="type" label='Status' width="80"><template #default="{row}"><el-tag size="small">{{ row.type }}</el-tag></template></el-table-column>
            <el-table-column prop="date" :label="\('nginx.title')" width="100" />
          </el-table>
          <el-empty v-if="!sites.length" description='' />
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card shadow="never"><template #header>
          -
          <el-select v-model="logType" size="small" style="width:120px;margin-left:12px">
            <el-option :label="\('nginx.title')" value="error" /><el-option :label="\('nginx.title')" value="access" />
          </el-select>
          <el-input v-model="logKeyword" placeholder="? size="small" style="width:150px;margin-left:8px" clearable />
          <el-button size="small" @click="fetchLogs" style="margin-left:8px">OK</el-button>
        </template>
        <pre class="code-box" style="max-height:350px">{{ logs || "" }}</pre>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"
import { getNginxStatus, testNginxConfig, getNginxSites, getNginxErrors, getNginxConnections, getNginxConfig, searchNginxLogs, reloadNginx } from "@/api/nginx"
import { ElMessage } from "element-plus"
const loading=ref(false), status=ref(null), conn=ref(null), sites=ref([]), errors=ref(null)
const cfgResult=ref(null), cfgLoading=ref(false), rlLoading=ref(false)
const configPath=ref("/etc/nginx/nginx.conf"), configContent=ref('')
const logType=ref("error"), logKeyword=ref(''), logs=ref('')
async function fetchAll(){loading.value=true;try{status.value=await getNginxStatus();conn.value=await getNginxConnections();sites.value=(await getNginxSites()).sites||[];errors.value=await getNginxErrors()}catch(e){ElMessage.error('Error')}loading.value=false}
async function testConfig(){cfgLoading.value=true;try{cfgResult.value=await testNginxConfig()}catch{}cfgLoading.value=false}
async function doReload(){rlLoading.value=true;try{await reloadNginx();ElMessage.success('OK')}catch{ElMessage.error('Error')}rlLoading.value=false}
async function fetchConfig(){try{const r=await getNginxConfig(configPath.value);configContent.value=r.content}catch{ElMessage.error('Error')}}
async function fetchLogs(){try{const r=await searchNginxLogs({keyword:logKeyword.value,type:logType.value,lines:100});logs.value=r.content}catch{ElMessage.error("")}}
onMounted(fetchAll)
</script>
<style scoped>
.nginx-panel{padding:24px}.page-header{margin-bottom:20px}.page-header h1{font-size:20px;margin:0 0 4px}.page-header p{font-size:13px;color:var(--text-muted);margin:0}
.code-box{background: rgba(30,30,30,0.85);color:#d4d4d4;padding:12px;border-radius:6px;font-size:11px;margin-top:8px;max-height:350px;overflow:auto;white-space:pre-wrap;word-break:break-all}
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>
