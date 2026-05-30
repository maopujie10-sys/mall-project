<template>
  <div class="page-container">
    <div class="page-header">
      <div><h1>采集中心</h1><p>多平台智能采集 · 商品数据完整保留 · 自动上传腾讯云COS</p></div>
      <div class="header-actions"><el-button type="primary" @click="showCreateDialog = true"><el-icon><Plus /></el-icon> 新建采集任务</el-button></div>
    </div>
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6" v-for="p in platforms" :key="p.name">
        <el-card shadow="never" class="platform-card" @click="startQuickScrape(p)">
          <div class="pf-icon">{{ p.icon }}</div><div class="pf-name">{{ p.name }}</div><div class="pf-count">{{ p.count }} 件商品</div><div class="pf-rate" :style="{ color: p.rate > 80 ? '#52c41a' : '#faad14' }">成功率 {{ p.rate }}%</div>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="16">
        <el-card shadow="never">
          <template #header><div class="panel-header"><span>采集任务</span><el-button text size="small" @click="refreshJobs">刷新</el-button></div></template>
          <el-table :data="jobs" size="small" max-height="350">
            <el-table-column prop="keyword" label="关键词" min-width="120"/><el-table-column prop="platform" label="平台" width="110"><template #default="{ row }"><el-tag size="small">{{ row.platform }}</el-tag></template></el-table-column>
            <el-table-column prop="collected" label="已采集" width="80"/><el-table-column prop="imported" label="已导入" width="80"/>
            <el-table-column prop="status" label="状态" width="100"><template #default="{ row }"><el-tag :type="row.statusType" size="small">{{ row.status }}</el-tag></template></el-table-column>
            <el-table-column label="操作" width="180"><template #default="{ row }"><el-button link type="primary" size="small" @click="previewProducts(row)">预览</el-button><el-button link type="success" size="small" @click="importToMall(row)">导入商城</el-button><el-button link type="danger" size="small" @click="removeJob(row.id)">删除</el-button></template></el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never"><template #header><span>COS存储</span></template><div class="cos-info">已用: {{ cosInfo.used }}MB / {{ cosInfo.total }}MB<el-progress :percentage="Math.round(cosInfo.used/cosInfo.total*100)" style="margin-top:8px"/></div></el-card>
      </el-col>
    </el-row>
    <el-dialog v-model="showCreateDialog" title="新建采集任务" width="500px">
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="平台"><el-select v-model="createForm.platform" style="width:100%"><el-option v-for="p in platforms" :key="p.name" :label="p.name" :value="p.name" /></el-select></el-form-item>
        <el-form-item label="关键词"><el-input v-model="createForm.keyword" placeholder="输入搜索关键词"/></el-form-item>
      </el-form>
      <template #footer><el-button @click="showCreateDialog=false">取消</el-button><el-button type="primary" @click="createJob" :loading="loading">开始采集</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'; import { ElMessage } from 'element-plus'; import { agentApi } from '@/api/index'
const loading = ref(false); const showCreateDialog = ref(false); const cosInfo = ref({ used: 0, total: 1024 })
const platforms = ref([{name:'eBay',icon:'',count:4520,rate:92},{name:'Amazon',icon:'',count:3210,rate:88},{name:'AliExpress',icon:'',count:6150,rate:85},{name:'Shopee',icon:'',count:2340,rate:91}])
const jobs = ref([]); const createForm = ref({ platform: 'eBay', keyword: '' })

async function fetchJobs() { try { const r = await agentApi.get('/agent/scraper/jobs'); if(r?.data?.ok) jobs.value = (r.data.jobs||[]).map(j=>({...j,statusType:j.status==='running'?'warning':j.status==='done'?'success':'info'})) } catch(e) {} }
async function fetchCOS() { try { const r = await agentApi.get('/agent/scraper/cos'); if(r?.data?.ok) cosInfo.value = { used: r.data.used||0, total: r.data.total||1024 } } catch(e) {} }
function refreshJobs() { fetchJobs() }
async function createJob() { if(!createForm.value.keyword) { ElMessage.warning('请输入关键词'); return }; loading.value=true; try { await agentApi.post('/agent/scraper/start', createForm.value); ElMessage.success('采集任务已创建'); showCreateDialog.value=false; fetchJobs() } catch(e) { ElMessage.error(e.message) }; loading.value=false }
function startQuickScrape(p) { createForm.value.platform = p.name; showCreateDialog.value = true }
async function importToMall(row) { try { await agentApi.post('/agent/scraper/import', { job_id: row.id }); ElMessage.success('已导入商城') } catch(e) { ElMessage.error('导入失败') } }
function previewProducts(row) { ElMessage.info('预览功能: ' + (row.collected||0) + ' 件商品') }
async function removeJob(id) { try { await agentApi.delete('/agent/scraper/jobs/'+id); ElMessage.success('已删除'); fetchJobs() } catch(e) { ElMessage.error(e.message) } }
onMounted(() => { fetchJobs(); fetchCOS() })
</script>
<style scoped>
.page-container { padding: 24px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; } .page-header h1 { font-size: 20px; margin: 0 0 4px; } .page-header p { color: var(--text-muted); font-size: 13px; margin: 0; }
.platform-card { cursor: pointer; text-align: center; transition: transform .2s; } .platform-card:hover { transform: translateY(-2px); } .pf-icon { font-size: 32px; } .pf-name { font-size: 15px; font-weight: 600; margin: 8px 0 4px; } .pf-count { font-size: 12px; color: var(--text-muted); } .pf-rate { font-size: 12px; }
.panel-header { display: flex; justify-content: space-between; align-items: center; }
.cos-info { text-align: center; font-size: 13px; color: var(--text-muted); }
@media (max-width: 768px) { .page-container { padding: 10px; } .page-header { flex-direction: column; gap: 10px; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } }
</style>