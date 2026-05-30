<template>
  <div class="page-container">
    <div class="page-header"><h1>微信平台管理</h1><p>微信公众号(服务号/订阅号) · 企业微信(WeCom) · 营业执照上传 · 自定义菜单</p></div>
    
    <el-tabs v-model="activeTab">
      <!-- 公众号配置 -->
      <el-tab-pane label="微信公众号" name="mp">
        <el-card>
          <template #header><span>微信公众号配置 (服务号/订阅号)</span><el-button size="small" @click="testMp" :loading="testingMp" style="float:right">测试连接</el-button></template>
          <el-form :model="mpForm" label-width="100px" size="default">
            <el-form-item label="公众号名称"><el-input v-model="mpForm.account_name" placeholder="如：Friday商城"/></el-form-item>
            <el-form-item label="账号类型"><el-select v-model="mpForm.account_type"><el-option label="服务号" value="service"/><el-option label="订阅号" value="subscription"/></el-select></el-form-item>
            <el-form-item label="AppID"><el-input v-model="mpForm.app_id" placeholder="wx..."/></el-form-item>
            <el-form-item label="AppSecret"><el-input v-model="mpForm.app_secret" type="password" placeholder="输入新的AppSecret" show-password/></el-form-item>
            <el-form-item label="Token"><el-input v-model="mpForm.token" placeholder="自定义Token"/></el-form-item>
            <el-form-item label="AES Key"><el-input v-model="mpForm.aes_key" type="password" placeholder="消息加密密钥" show-password/></el-form-item>
            <el-divider>自动回复设置</el-divider>
            <el-form-item label="开启自动回复"><el-switch v-model="mpForm.auto_reply_enabled"/></el-form-item>
            <el-form-item label="关注欢迎语"><el-input v-model="mpForm.welcome_message" type="textarea" :rows="2"/></el-form-item>
            <el-form-item label="默认回复"><el-input v-model="mpForm.default_reply" type="textarea" :rows="2"/></el-form-item>
            <el-form-item><el-button type="primary" @click="saveMp" :loading="savingMp">保存公众号配置</el-button></el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 企业微信 -->
      <el-tab-pane label="企业微信" name="wecom">
        <el-card>
          <template #header><span>企业微信配置</span><el-button size="small" @click="testWecom" :loading="testingWecom" style="float:right">测试连接</el-button></template>
          <el-form :model="wecomForm" label-width="100px">
            <el-form-item label="企业ID"><el-input v-model="wecomForm.corp_id" placeholder="ww..."/></el-form-item>
            <el-form-item label="应用AgentId"><el-input v-model="wecomForm.agent_id" placeholder="1000001"/></el-form-item>
            <el-form-item label="应用Secret"><el-input v-model="wecomForm.secret" type="password" show-password/></el-form-item>
            <el-form-item label="回调Token"><el-input v-model="wecomForm.token"/></el-form-item>
            <el-form-item label="AES Key"><el-input v-model="wecomForm.aes_key" type="password" show-password/></el-form-item>
            <el-form-item><el-button type="primary" @click="saveWecom" :loading="savingWecom">保存企业微信配置</el-button></el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 营业执照 -->
      <el-tab-pane label="营业执照" name="license">
        <el-card>
          <template #header><span>营业执照上传</span><el-tag v-if="licenseInfo.has_license" type="success" style="margin-left:10px">已上传</el-tag></template>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-upload class="license-upload" drag :auto-upload="false" :on-change="handleLicenseFile" accept="image/*" :limit="1">
                <el-icon :size="48"><svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/></svg></el-icon>
                <div class="el-upload__text">拖拽或<em>点击上传</em>营业执照</div>
              </el-upload>
              <div v-if="licenseFile" style="margin-top:10px;color:#52c41a">已选择: {{ licenseFile.name }}</div>
            </el-col>
            <el-col :span="12">
              <el-form :model="licenseForm" label-width="80px">
                <el-form-item label="公司名称"><el-input v-model="licenseForm.company_name"/></el-form-item>
                <el-form-item label="统一信用代码"><el-input v-model="licenseForm.license_number"/></el-form-item>
                <el-form-item label="法定代表人"><el-input v-model="licenseForm.legal_person"/></el-form-item>
                <el-form-item label="注册地址"><el-input v-model="licenseForm.address"/></el-form-item>
                <el-form-item><el-button type="primary" @click="uploadLicense" :loading="uploading" :disabled="!licenseFile">上传营业执照</el-button></el-form-item>
              </el-form>
            </el-col>
          </el-row>
        </el-card>
      </el-tab-pane>

      <!-- 自定义菜单 -->
      <el-tab-pane label="自定义菜单" name="menu">
        <el-card>
          <template #header><span>公众号菜单编辑</span><el-button size="small" @click="pushMenu" :loading="pushing" style="float:right">推送到微信</el-button></template>
          <el-alert title="微信公众号菜单最多3个一级菜单，每个最多5个子菜单" type="info" :closable="false" style="margin-bottom:16px"/>
          <div v-for="(btn, i) in menuButtons" :key="i" class="menu-item-card">
            <div class="menu-item-header">
              <span>一级菜单 #{{ i+1 }}</span>
              <el-button link type="danger" @click="menuButtons.splice(i,1)">删除</el-button>
            </div>
            <el-input v-model="btn.name" placeholder="菜单名称(最多8字)" style="margin-bottom:8px" maxlength="8"/>
            <el-select v-model="btn.type" v-if="!btn.sub_buttons.length" style="width:100%;margin-bottom:8px">
              <el-option label="点击事件" value="click"/><el-option label="跳转链接" value="view"/>
            </el-select>
            <el-input v-model="btn.key" v-if="btn.type==='click' && !btn.sub_buttons.length" placeholder="事件Key" style="margin-bottom:8px"/>
            <el-input v-model="btn.url" v-if="btn.type==='view' && !btn.sub_buttons.length" placeholder="跳转URL" style="margin-bottom:8px"/>
            <div v-if="btn.sub_buttons.length" style="margin-left:16px;margin-top:8px">
              <div v-for="(sub, j) in btn.sub_buttons" :key="j" style="display:flex;gap:8px;margin-bottom:6px;align-items:center">
                <el-input v-model="sub.name" placeholder="子菜单名" size="small" style="flex:1"/><el-select v-model="sub.type" size="small" style="width:90px"><el-option label="点击" value="click"/><el-option label="跳转" value="view"/></el-select><el-input v-model="sub.key" v-if="sub.type==='click'" size="small" placeholder="Key" style="width:100px"/><el-input v-model="sub.url" v-if="sub.type==='view'" size="small" placeholder="URL" style="width:120px"/><el-button link type="danger" size="small" @click="btn.sub_buttons.splice(j,1)">x</el-button>
              </div>
              <el-button size="small" @click="btn.sub_buttons.push({name:'',type:'click',key:'',url:''})" :disabled="btn.sub_buttons.length>=5">+添加子菜单</el-button>
            </div>
            <el-button size="small" @click="btn.sub_buttons=[]" v-if="!btn.sub_buttons.length && btn.type!=='view'" style="margin-top:4px">转为子菜单模式</el-button>
          </div>
          <el-button @click="menuButtons.push({name:'',type:'click',key:'',url:'',sub_buttons:[]})" :disabled="menuButtons.length>=3" style="margin-top:12px">+添加菜单</el-button>
        </el-card>
      </el-tab-pane>

      <!-- 消息统计 -->
      <el-tab-pane label="消息统计" name="stats">
        <el-card>
          <el-row :gutter="16">
            <el-col :span="6"><div class="stat-box"><div class="stat-num">{{ stats.total_messages }}</div><div class="stat-label">总消息数</div></div></el-col>
            <el-col :span="6"><div class="stat-box"><div class="stat-num">{{ stats.total_users }}</div><div class="stat-label">总用户数</div></div></el-col>
            <el-col :span="6"><div class="stat-box"><div class="stat-num">{{ stats.today_messages }}</div><div class="stat-label">今日消息</div></div></el-col>
            <el-col :span="6"><div class="stat-box"><div class="stat-num">{{ stats.today_users }}</div><div class="stat-label">今日新用户</div></div></el-col>
          </el-row>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'; import { ElMessage } from 'element-plus'; import { agentApi } from '@/api/index'
const activeTab = ref('mp')
const testingMp = ref(false); const savingMp = ref(false); const testingWecom = ref(false); const savingWecom = ref(false)
const uploading = ref(false); const pushing = ref(false); const licenseFile = ref(null)
const licenseInfo = ref({has_license:false})
const mpForm = reactive({account_name:'',account_type:'service',app_id:'',app_secret:'',token:'',aes_key:'',auto_reply_enabled:true,welcome_message:'欢迎关注！',default_reply:'已收到您的消息'})
const wecomForm = reactive({corp_id:'',agent_id:'',secret:'',token:'',aes_key:''})
const licenseForm = reactive({company_name:'',license_number:'',legal_person:'',address:''})
const menuButtons = reactive([{name:'',type:'click',key:'',url:'',sub_buttons:[]},{name:'',type:'click',key:'',url:'',sub_buttons:[]},{name:'',type:'click',key:'',url:'',sub_buttons:[]}])
const stats = reactive({total_messages:0,total_users:0,today_messages:0,today_users:0})

async function loadConfig() { try { const r=await agentApi.get('/agent/wechat/config'); if(r?.data?.ok) Object.assign(mpForm, r.data.config||{}) } catch(e){}; try { const w=await agentApi.get('/agent/wechat/wecom/config'); if(w?.data?.ok) Object.assign(wecomForm, w.data.config||{}) } catch(e){}; try { const l=await agentApi.get('/agent/wechat/license'); if(l?.data?.ok) licenseInfo.value = l.data } catch(e){}; try { const m=await agentApi.get('/agent/wechat/menu'); if(m?.data?.ok && m.data.menu?.length) { menuButtons.length=0; m.data.menu.forEach(b=>menuButtons.push({...b,sub_buttons:b.sub_buttons||[]})) } } catch(e){}; try { const s=await agentApi.get('/agent/wechat/stats'); if(s?.data?.ok) Object.assign(stats, s.data.stats||{}) } catch(e){} }
async function saveMp() { savingMp.value=true; try { await agentApi.post('/agent/wechat/config', mpForm); ElMessage.success('公众号配置已保存') } catch(e) { ElMessage.error(e.message) }; savingMp.value=false }
async function testMp() { testingMp.value=true; try { const r=await agentApi.post('/agent/wechat/test-connection'); ElMessage[r.data?.ok?'success':'error'](r.data?.message||r.data?.error) } catch(e) { ElMessage.error(e.message) }; testingMp.value=false }
async function saveWecom() { savingWecom.value=true; try { await agentApi.post('/agent/wechat/wecom/config', wecomForm); ElMessage.success('企业微信配置已保存') } catch(e) { ElMessage.error(e.message) }; savingWecom.value=false }
async function testWecom() { testingWecom.value=true; try { const r=await agentApi.post('/agent/wechat/wecom/test'); ElMessage[r.data?.ok?'success':'error'](r.data?.message||r.data?.error) } catch(e) { ElMessage.error(e.message) }; testingWecom.value=false }
function handleLicenseFile(file) { licenseFile.value = file }
async function uploadLicense() { if(!licenseFile.value) return; uploading.value=true; const fd=new FormData(); fd.append('file', licenseFile.value.raw); fd.append('company_name', licenseForm.company_name); fd.append('license_number', licenseForm.license_number); fd.append('legal_person', licenseForm.legal_person); fd.append('address', licenseForm.address); try { const r=await agentApi.post('/agent/wechat/license/upload', fd, {headers:{'Content-Type':'multipart/form-data'}}); if(r?.data?.ok) { ElMessage.success('营业执照已上传'); licenseInfo.value.has_license=true } } catch(e) { ElMessage.error(e.message) }; uploading.value=false }
async function pushMenu() { pushing.value=true; try { const r=await agentApi.post('/agent/wechat/menu', {buttons:[...menuButtons]}); ElMessage[r.data?.ok?'success':'warning'](r.data?.message||r.data?.error) } catch(e) { ElMessage.error(e.message) }; pushing.value=false }
onMounted(()=>loadConfig())
</script>
<style scoped>
.page-container { padding: 24px; } .page-header { margin-bottom: 24px; } .page-header h1 { font-size: 20px; margin: 0 0 4px; } .page-header p { font-size: 13px; color: var(--text-muted); margin: 0; }
.license-upload { width: 100%; }
.menu-item-card { background: rgba(0,0,0,0.2); border: 1px solid rgba(102,126,234,0.2); border-radius: 8px; padding: 12px; margin-bottom: 10px; }
.menu-item-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-size: 13px; color: #a0b4ff; }
.stat-box { text-align: center; padding: 20px; background: rgba(0,0,0,0.2); border-radius: 8px; } .stat-num { font-size: 28px; font-weight: 700; } .stat-label { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
@media (max-width: 768px) { .page-container { padding: 10px; } .el-col { margin-bottom: 10px; } }
</style>