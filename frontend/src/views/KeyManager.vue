<template>
  <div class="page-shell">
    <div class="page-header"><h2>🔑 API Key 管理</h2><p>后台增删改查+热切换 · 保存即生效</p></div>

    <!-- 添加Key -->
    <el-card style="margin-bottom:16px"><template #header>➕ 添加/更新 Key</template>
      <el-row :gutter="12">
        <el-col :span="6"><el-select v-model="newKey.env_key" placeholder="选择Key" filterable>
          <el-option v-for="o in keyOptions" :key="o.value" :label="o.label" :value="o.value"/>
        </el-select></el-col>
        <el-col :span="10"><el-input v-model="newKey.value" placeholder="粘贴Key值" type="password" show-password/></el-col>
        <el-col :span="4"><el-input v-model="newKey.name" placeholder="备注名"/></el-col>
        <el-col :span="4"><el-button type="primary" @click="saveKey">保存</el-button></el-col>
      </el-row>
    </el-card>

    <!-- Key列表 -->
    <el-card><template #header>📋 已配置的 Key ({{keys.length}})</template>
      <el-table :data="keys" stripe size="small">
        <el-table-column prop="name" label="名称" width="160"/>
        <el-table-column prop="env_key" label="环境变量" width="180"/>
        <el-table-column prop="provider" label="服务商" width="80"/>
        <el-table-column label="Key值" width="180"><template #default="{row}">
          <span :style="{color:row.has_value?'#4ade80':'#f87171'}">{{row.value_preview||'未配置'}}</span>
        </template></el-table-column>
        <el-table-column label="状态" width="80"><template #default="{row}">
          <el-switch v-model="row.active" @change="toggleKey(row)" size="small"/>
        </template></el-table-column>
        <el-table-column label="操作" width="80"><template #default="{row}">
          <el-button size="small" type="danger" @click="deleteKey(row)">删除</el-button>
        </template></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>
<script setup>
import {ref,reactive,onMounted} from 'vue';import {ElMessage,ElMessageBox} from 'element-plus';import {agentApi} from '@/api'
const keys=ref([])
const newKey=reactive({env_key:'',value:'',name:''})
const keyOptions=[
  {value:'OPENAI_API_KEY',label:'OpenAI API Key'},
  {value:'DEEPSEEK_API_KEY',label:'DeepSeek API Key'},
  {value:'CLAUDE_API_KEY',label:'Claude API Key'},
  {value:'TELEGRAM_BOT_TOKEN',label:'Telegram Bot Token'},
  {value:'WECHAT_TOKEN',label:'微信公众号Token'},
  {value:'WECOM_CORP_ID',label:'企业微信CorpID'},
  {value:'DINGTALK_APP_KEY',label:'钉钉AppKey'},
  {value:'GITHUB_TOKEN',label:'GitHub Token'},
  {value:'AI302_API_KEY',label:'302.AI API Key'},
  {value:'POE_API_KEY',label:'Poe API Key'},
]
async function fetchKeys(){try{const r=await agentApi.get('/agent/keys/list');if(r?.data?.ok)keys.value=r.data.keys}catch(e){}}
async function saveKey(){if(!newKey.env_key||!newKey.value){ElMessage.warning('请选择Key并填写值');return}
  try{await agentApi.post('/agent/keys/set',{...newKey});ElMessage.success('已保存');newKey.value='';fetchKeys()}catch(e){ElMessage.error(e.message)}}
async function toggleKey(row){try{await agentApi.post('/agent/keys/toggle/'+row.env_key);fetchKeys()}catch(e){}}
async function deleteKey(row){try{await ElMessageBox.confirm('删除 '+row.env_key+' ?');await agentApi.delete('/agent/keys/'+row.env_key);fetchKeys()}catch(e){}}
onMounted(fetchKeys)
</script>
<style scoped>
.page-shell{max-width:960px;margin:0 auto;padding:20px;}.page-header{margin-bottom:16px;}.page-header h2{font-size:20px;color:#e0e0ff;margin:0;}.page-header p{font-size:12px;color:rgba(255,255,255,0.5);margin:4px 0;}
@media(max-width:768px){.page-shell{padding:10px;}}
</style>
