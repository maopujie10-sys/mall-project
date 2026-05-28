<template>
  <div class="nginx-panel">
    <div class="page-header"><h1>🔧 Nginx 管理</h1><p>进程监控 · 配置管理 · 站点管理 · 日志分析 · SSL</p></div>
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6"><el-card shadow="never"><template #header>进程状态</template>
        <el-tag :type="status?.running ? 'success' : 'danger'" size="large">{{ status?.running ? "运行中" : "已停止" }}</el-tag>
        <div style="margin-top:8px;font-size:12px;color:var(--text-muted)">HTTP连接: {{ conn?.http_connections || "?" }} | HTTPS: {{ conn?.https_connections || "?" }}</div>
      </el-card></el-col>
      <el-col :span="6"><el-card shadow="never"><template #header>配置语法</template>
        <el-button @click="testConfig" :loading="cfgLoading" size="small">测试 nginx -t</el-button>
        <div v-if="cfgResult" :style="{color:cfgResult.ok?'#52c41a':'#ff4d4f',fontSize:'12px',marginTop:'8px'}">{{ cfgResult.ok ? "配置正确" : "配置有误" }}</div>
      </el-card></el-col>
      <el-col :span="6"><el-card shadow="never"><template #header>站点数</template>
        <div style="font-size:28px;font-weight:700;color:var(--color-primary)">{{ sites.length }}</div>
        <div style="font-size:12px;color:var(--text-muted)">已启用站点</div>
      </el-card></el-col>
      <el-col :span="6"><el-card shadow="never"><template #header>操作</template>
        <el-button type="warning" @click="doReload" :loading="rlLoading" size="small">重载 Nginx</el-button>
        <el-button @click="fetchAll" :loading="loading" size="small" style="margin-left:8px">刷新</el-button>
      </el-card></el-col>
    </el-row>
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card shadow="never"><template #header><span>📄 配置文件</span><el-select v-model="configPath" size="small" style="width:200px;margin-left:12px">
          <el-option label="nginx.conf 主配置" value="/etc/nginx/nginx.conf" />
          <el-option label="default 站点" value="/etc/nginx/sites-enabled/default" />
        </el-select><el-button size="small" @click="fetchConfig" style="margin-left:8px">加载</el-button></template>
        <pre class="code-box">{{ configContent || "点击加载配置" }}</pre>
      </el-card>
      <el-col :span="12">
        <el-card shadow="never"><template #header>📊 错误统计</template>
          <div v-if="errors?.total" style="margin-bottom:12px">共 {{ errors.total }} 条最近错误</div>
          <div v-for="(cnt,type) in errors?.by_type" :key="type" style="display:flex;align-items:center;gap:8px;margin-bottom:6px;font-size:13px">
            <span style="width:60px">{{ type }}</span><el-progress :percentage="Math.round(cnt/errors.total*100)" :stroke-width="12" :color="type==='error'?'#ff4d4f':type==='warn'?'#faad14':'#1890ff'" />
          </div>
          <el-empty v-if="!errors?.total" description="无错误日志" />
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="8">
        <el-card shadow="never"><template #header>🌐 站点列表</template>
          <el-table :data="sites" stripe size="small" max-height="300">
            <el-table-column prop="name" label="站点名" min-width="140" />
            <el-table-column prop="type" label="类型" width="80"><template #default="{row}"><el-tag size="small">{{ row.type }}</el-tag></template></el-table-column>
            <el-table-column prop="date" label="修改时间" width="100" />
          </el-table>
          <el-empty v-if="!sites.length" description="暂无站点" />
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card shadow="never"><template #header>
          <span>📋 日志查看</span>
          <el-select v-model="logType" size="small" style="width:120px;margin-left:12px">
            <el-option label="错误日志" value="error" /><el-option label="访问日志" value="access" />
          </el-select>
          <el-input v-model="logKeyword" placeholder="搜索关键词" size="small" style="width:150px;margin-left:8px" clearable />
          <el-button size="small" @click="fetchLogs" style="margin-left:8px">搜索</el-button>
        </template>
        <pre class="code-box" style="max-height:350px">{{ logs || "点击搜索查看日志" }}</pre>
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
const configPath=ref("/etc/nginx/nginx.conf"), configContent=ref("")
const logType=ref("error"), logKeyword=ref(""), logs=ref("")
async function fetchAll(){loading.value=true;try{status.value=await getNginxStatus();conn.value=await getNginxConnections();sites.value=(await getNginxSites()).sites||[];errors.value=await getNginxErrors()}catch(e){ElMessage.error("获取失败")}loading.value=false}
async function testConfig(){cfgLoading.value=true;try{cfgResult.value=await testNginxConfig()}catch{}cfgLoading.value=false}
async function doReload(){rlLoading.value=true;try{await reloadNginx();ElMessage.success("重载成功")}catch{ElMessage.error("重载失败")}rlLoading.value=false}
async function fetchConfig(){try{const r=await getNginxConfig(configPath.value);configContent.value=r.content}catch{ElMessage.error("加载失败")}}
async function fetchLogs(){try{const r=await searchNginxLogs({keyword:logKeyword.value,type:logType.value,lines:100});logs.value=r.content}catch{ElMessage.error("获取日志失败")}}
onMounted(fetchAll)
</script>
<style scoped>
.nginx-panel{padding:24px}.page-header{margin-bottom:20px}.page-header h1{font-size:20px;margin:0 0 4px}.page-header p{font-size:13px;color:var(--text-muted);margin:0}
.code-box{background:#1e1e1e;color:#d4d4d4;padding:12px;border-radius:6px;font-size:11px;margin-top:8px;max-height:350px;overflow:auto;white-space:pre-wrap;word-break:break-all}
</style>
