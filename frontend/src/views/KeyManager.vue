<template>
  <div class="page-shell">
    <div class="page-header"><h2>馃攽 API Key 绠＄悊</h2><p>鍚庡彴澧炲垹鏀规煡+鐑垏鎹?鈥?淇濆瓨鍗崇敓鏁?/p></div>

    <!-- 娣诲姞Key -->
    <el-card style="margin-bottom:16px"><template #header>鉃?娣诲姞/鏇存柊 Key</template>
      <el-row :gutter="12">
        <el-col :span="6"><el-select v-model="newKey.env_key" placeholder="閫夋嫨Key" filterable>
          <el-option v-for="o in keyOptions" :key="o.value" :label="o.label" :value="o.value"/>
        </el-select></el-col>
        <el-col :span="10"><el-input v-model="newKey.value" placeholder="绮樿创Key鍊? type="password" show-password/></el-col>
        <el-col :span="4"><el-input v-model="newKey.name" placeholder="澶囨敞鍚?/></el-col>
        <el-col :span="4"><el-button type="primary" @click="saveKey">淇濆瓨</el-button></el-col>
      </el-row>
    </el-card>

    <!-- Key鍒楄〃 -->
    <el-card><template #header>馃搵 宸查厤缃殑 Key ({{keys.length}})</template>
      <el-table :data="keys" stripe size="small">
        <el-table-column prop="name" label="鍚嶇О" width="160"/>
        <el-table-column prop="env_key" label="鐜鍙橀噺" width="180"/>
        <el-table-column prop="provider" label="鏈嶅姟鍟? width="80"/>
        <el-table-column label="Key鍊? width="180"><template #default="{row}">
          <span :style="{color:row.has_value?'#4ade80':'#f87171'}">{{row.value_preview||'鏈厤缃?}}</span>
        </template></el-table-column>
        <el-table-column label="鐘舵€? width="80"><template #default="{row}">
          <el-switch v-model="row.active" @change="toggleKey(row)" size="small"/>
        </template></el-table-column>
        <el-table-column label="鎿嶄綔" width="80"><template #default="{row}">
          <el-button size="small" type="danger" @click="deleteKey(row)">鍒犻櫎</el-button>
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
  {value:'WECHAT_TOKEN',label:'寰俊鍏紬鍙稵oken'},
  {value:'WECOM_CORP_ID',label:'浼佷笟寰俊CorpID'},
  {value:'DINGTALK_APP_KEY',label:'閽夐拤AppKey'},
  {value:'GITHUB_TOKEN',label:'GitHub Token'},
  {value:'AI302_API_KEY',label:'302.AI API Key'},
  {value:'POE_API_KEY',label:'Poe API Key'},
]
async function fetchKeys(){try{const r=await agentApi.get('/agent/keys/list');if(r?.data?.ok)keys.value=r.data.keys}catch(e){}}
async function saveKey(){if(!newKey.env_key||!newKey.value){ElMessage.warning('璇烽€夋嫨Key骞跺～鍐欏€?);return}
  try{await agentApi.post('/agent/keys/set',{...newKey});ElMessage.success('宸蹭繚瀛?);newKey.value='';fetchKeys()}catch(e){ElMessage.error(e.message)}}
async function toggleKey(row){try{await agentApi.post('/agent/keys/toggle/'+row.env_key);fetchKeys()}catch(e){}}
async function deleteKey(row){try{await ElMessageBox.confirm('鍒犻櫎 '+row.env_key+' ?');await agentApi.delete('/agent/keys/'+row.env_key);fetchKeys()}catch(e){}}
onMounted(fetchKeys)
</script>
<style scoped>
.page-shell{max-width:960px;margin:0 auto;padding:20px;}.page-header{margin-bottom:16px;}.page-header h2{font-size:20px;color:#e0e0ff;margin:0;}.page-header p{font-size:12px;color:rgba(255,255,255,0.5);margin:4px 0;}
@media(max-width:768px){.page-shell{padding:10px;}}
</style>
