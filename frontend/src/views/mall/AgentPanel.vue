<template>
  <div>
    <el-tabs type="card">
      <!-- 代理列表 -->
      <el-tab-pane label='代理列表'>
        <div class="tb-bar">
          <el-input v-model="agentKw" placeholder="搜索代理..." style="width:220px" clearable @clear="loadAll" @keyup.enter="loadAll" />
          <el-button type="primary" @click="loadAll">搜索</el-button>
        </div>
        <el-table :data="agents" stripe size="small" v-loading="agtl">
          <el-table-column prop="sellerId" label="ID" width="80" />
          <el-table-column prop="name" label="名称" width="120" />
          <el-table-column prop="phone" label="电话" width="130" />
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{row}"><el-tag :type="row.status===1?'success':'danger'" size="small">{{ row.status===1?'启用':'禁用' }}</el-tag></template>
          </el-table-column>
          <el-table-column label="操作" width="260">
            <template #default="{row}">
              <el-button size="small" link type="primary" @click="showAgentDetail(row)">详情</el-button>
              <el-button size="small" link type="primary" @click="showAgentTeam(row)">团队</el-button>
              <el-button size="small" link :type="row.status===1?'warning':'success'" @click="toggleAgentStatus(row)">{{ row.status===1?'禁用':'启用' }}</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination style="margin-top:12px" background layout="prev,next" :total="agentTotal" :page-size="10" v-model:current-page="agentPg" @current-change="loadAll" small />
      </el-tab-pane>
      <!-- 代理等级 -->
      <el-tab-pane label='代理等级'>
        <div style="margin-bottom:12px"><el-button size="small" type="primary" @click="showLevelForm()">添加等级</el-button></div>
        <el-table :data="levels" stripe size="small" v-loading="lvl">
          <el-table-column prop="uuid" label="UUID" width="200" />
          <el-table-column prop="name" label="名称" width="120" />
          <el-table-column prop="threshold" label="门槛" width="100" />
          <el-table-column prop="description" label="描述" />
          <el-table-column label="操作" width="160">
            <template #default="{row}">
              <el-button size="small" link type="primary" @click="showLevelForm(row)">编辑</el-button>
              <el-button size="small" link type="danger" @click="delLevel(row.uuid)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <!-- 返利统计 -->
      <el-tab-pane label='返利记录'>
        <el-row :gutter="12" style="margin-bottom:12px">
          <el-col :span="8"><div class="metric-card"><div class="metric-label">总返利金额</div><div class="metric-value">{{ rebateStats?.totalAmount||0 }}</div></div></el-col>
          <el-col :span="8"><div class="metric-card c2"><div class="metric-label">总返利笔数</div><div class="metric-value">{{ rebateStats?.totalCount||0 }}</div></div></el-col>
        </el-row>
        <el-table :data="rebates" stripe size="small" v-loading="rbl">
          <el-table-column prop="uuid" label="UUID" width="200" />
          <el-table-column prop="agentId" label="代理ID" width="100" />
          <el-table-column prop="amount" label="金额" width="100" />
          <el-table-column prop="createTime" label="时间" width="160" />
        </el-table>
        <el-pagination style="margin-top:12px" background layout="prev,next" :total="rebateTotal" :page-size="20" v-model:current-page="rebatePg" @current-change="loadRebates" small />
      </el-tab-pane>
    </el-tabs>
    <!-- 代理详情弹窗 -->
    <el-dialog v-model="agentDetail.show" title="代理详情" width="500px">
      <el-descriptions :column="2" border size="small" v-if="agentDetail.data">
        <el-descriptions-item label="ID">{{ agentDetail.data.sellerId }}</el-descriptions-item>
        <el-descriptions-item label="名称">{{ agentDetail.data.name }}</el-descriptions-item>
        <el-descriptions-item label="电话">{{ agentDetail.data.phone }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ agentDetail.data.email }}</el-descriptions-item>
        <el-descriptions-item label="等级">{{ agentDetail.data.level }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ agentDetail.data.status===1?'启用':'禁用' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间" :span="2">{{ agentDetail.data.createTime }}</el-descriptions-item>
      </el-descriptions>
      <template #footer><el-button @click="agentDetail.show=false">关闭</el-button></template>
    </el-dialog>
    <!-- 团队弹窗 -->
    <el-dialog v-model="agentTeam.show" title="下级团队" width="600px">
      <el-table :data="agentTeam.members" stripe size="small" v-loading="agentTeam.loading">
        <el-table-column prop="sellerId" label="ID" width="80" />
        <el-table-column prop="name" label="名称" width="120" />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="level" label="等级" width="100" />
        <el-table-column prop="status" label="状态" width="80" />
      </el-table>
      <template #footer><el-button @click="agentTeam.show=false">关闭</el-button></template>
    </el-dialog>
    <!-- 等级弹窗 -->
    <el-dialog :title="editingLevel?.uuid?'编辑等级':'添加等级'" v-model="levelDialog" width="400px">
      <el-form :model="levelForm" label-width="80px">
        <el-form-item label='名称'><el-input v-model="levelForm.name" /></el-form-item>
        <el-form-item label='门槛'><el-input v-model="levelForm.threshold" /></el-form-item>
        <el-form-item label='描述'><el-input v-model="levelForm.description" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="levelDialog=false">取消</el-button><el-button type="primary" @click="saveLevel">保存</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getAgentList, getAgentDetail, updateAgentStatus, getAgentTeam,
  getAgentLevelList, saveAgentLevel, updateAgentLevel, deleteAgentLevel,
  getAgentRebateList, getAgentRebateStats
} from '@/api/mall'

const agents = ref([]); const agtl = ref(false); const agentKw = ref(''); const agentPg = ref(1); const agentTotal = ref(0)
const levels = ref([]); const lvl = ref(false)
const rebates = ref([]); const rbl = ref(false); const rebatePg = ref(1); const rebateTotal = ref(0)
const rebateStats = ref({})
const agentDetail = reactive({ show:false, data:null })
const agentTeam = reactive({ show:false, members:[], loading:false })
const levelDialog = ref(false); const editingLevel = ref(null)
const levelForm = ref({ name: '', threshold: '', description: '' })

async function loadAll() {
  agtl.value = true; lvl.value = true
  try { const r = await getAgentList({ page: agentPg.value, size: 10, keyword: agentKw.value }); agents.value = r.list||r.records||[]; agentTotal.value = r.total||0 } catch { }
  try { const r = await getAgentLevelList(); levels.value = r.list||r.records||[] } catch { }
  agtl.value = false; lvl.value = false
}
async function loadRebates() {
  rbl.value = true
  try { const r = await getAgentRebateList({ page: rebatePg.value, size: 20 }); rebates.value = r.list||r.records||[]; rebateTotal.value = r.total||0 } catch { }
  try { rebateStats.value = await getAgentRebateStats() } catch { }
  rbl.value = false
}
async function showAgentDetail(row) {
  try { agentDetail.data = await getAgentDetail(row.sellerId||row.id) } catch { agentDetail.data = row }
  agentDetail.show = true
}
async function showAgentTeam(row) {
  agentTeam.show = true; agentTeam.loading = true
  try { const r = await getAgentTeam(row.sellerId||row.id); agentTeam.members = r.list||r.records||[] } catch { agentTeam.members = [] }
  agentTeam.loading = false
}
async function toggleAgentStatus(row) {
  try { await updateAgentStatus({ sellerId: row.sellerId||row.id, status: row.status===1?0:1 }); ElMessage.success('OK'); loadAll() } catch { ElMessage.error('Error') }
}
function showLevelForm(row) { editingLevel.value = row; levelForm.value = row ? { name:row.name||'', threshold:row.threshold||'', description:row.description||'' } : { name:'', threshold:'', description:'' }; levelDialog.value = true }
async function saveLevel() {
  try {
    if (editingLevel.value?.uuid) await updateAgentLevel(editingLevel.value.uuid, levelForm.value)
    else await saveAgentLevel(levelForm.value)
    ElMessage.success('OK'); levelDialog.value = false; loadAll()
  } catch { ElMessage.error('Error') }
}
async function delLevel(uuid) { await ElMessageBox.confirm('确认删除?'); try { await deleteAgentLevel(uuid); ElMessage.success('OK'); loadAll() } catch { ElMessage.error('Error') } }
onMounted(() => { loadAll(); loadRebates() })
</script>
<style scoped>
.tb-bar { display:flex; gap:8px; margin-bottom:12px; }
.metric-card { padding:12px; border-radius:8px; text-align:center; background:linear-gradient(135deg,#667eea,#764ba2); color:#fff; }
.metric-card.c2 { background:linear-gradient(135deg,#f093fb,#f5576c); }
.metric-label { font-size:12px; opacity:.9; }
.metric-value { font-size:24px; font-weight:700; }
</style>
