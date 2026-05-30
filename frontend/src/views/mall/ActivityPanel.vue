<template>
  <div>
    <el-tabs type="card">
      <!-- 活动列表 -->
      <el-tab-pane label='活动管理'>
        <div style="margin-bottom:12px"><el-button size="small" type="primary" @click="showActivityForm()">创建活动</el-button></div>
        <el-table :data="activities" stripe size="small" v-loading="al" @row-click="showActivityDetail">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="startTime" label="开始时间" width="160" />
          <el-table-column prop="endTime" label="结束时间" width="160" />
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{row}"><el-tag :type="row.status===1?'success':'info'" size="small">{{ row.status===1?'进行中':'已结束' }}</el-tag></template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{row}">
              <el-button size="small" link type="primary" @click.stop="showActivityForm(row)">编辑</el-button>
              <el-button size="small" link type="primary" @click.stop="showPrizes(row)">奖品</el-button>
              <el-button size="small" link type="danger" @click.stop="delActivity(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination style="margin-top:12px" background layout="prev,next" :total="actTotal" :page-size="10" v-model:current-page="actPg" @current-change="loadActivities" small />
      </el-tab-pane>
      <!-- 中奖记录 -->
      <el-tab-pane label='中奖记录'>
        <div class="tb-bar">
          <el-select v-model="recordActFilter" placeholder="筛选活动" style="width:220px" clearable @change="loadRecords">
            <el-option v-for="a in activities" :key="a.id" :label="a.title" :value="a.id" />
          </el-select>
          <el-button type="primary" @click="loadRecords">查询</el-button>
        </div>
        <el-table :data="records" stripe size="small" v-loading="rcl">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="activityId" label="活动ID" width="80" />
          <el-table-column prop="userId" label="用户ID" width="80" />
          <el-table-column prop="prizeName" label="奖品" width="120" />
          <el-table-column prop="prizeLevel" label="级别" width="80" />
          <el-table-column prop="createTime" label="时间" width="160" />
        </el-table>
        <el-pagination style="margin-top:12px" background layout="prev,next" :total="recTotal" :page-size="20" v-model:current-page="recPg" @current-change="loadRecords" small />
      </el-tab-pane>
    </el-tabs>
    <!-- 活动弹窗 -->
    <el-dialog :title="editingActivity?.id?'编辑活动':'创建活动'" v-model="activityDialog" width="500px">
      <el-form :model="activityForm" label-width="80px">
        <el-form-item label='标题'><el-input v-model="activityForm.title" /></el-form-item>
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label='开始时间'><el-input v-model="activityForm.startTime" placeholder="2026-01-01 00:00" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label='结束时间'><el-input v-model="activityForm.endTime" placeholder="2026-12-31 23:59" /></el-form-item></el-col>
        </el-row>
        <el-form-item label='描述'><el-input v-model="activityForm.description" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="activityDialog=false">取消</el-button><el-button type="primary" @click="saveActivity">保存</el-button></template>
    </el-dialog>
    <!-- 奖品管理弹窗 -->
    <el-dialog title="奖品管理" v-model="prizeDialog" width="600px">
      <div style="margin-bottom:12px"><el-button size="small" type="primary" @click="showPrizeForm()">添加奖品</el-button></div>
      <el-table :data="prizes" stripe size="small" v-loading="pzl">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" width="120" />
        <el-table-column prop="level" label="级别" width="80" />
        <el-table-column prop="totalCount" label="总量" width="80" />
        <el-table-column prop="remainCount" label="剩余" width="80" />
        <el-table-column prop="probability" label="概率(%)" width="80" />
        <el-table-column label="操作" width="160">
          <template #default="{row}">
            <el-button size="small" link type="primary" @click="showPrizeForm(row)">编辑</el-button>
            <el-button size="small" link type="danger" @click="delPrize(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer><el-button @click="prizeDialog=false">关闭</el-button></template>
    </el-dialog>
    <!-- 奖品弹窗 -->
    <el-dialog :title="editingPrize?.id?'编辑奖品':'添加奖品'" v-model="prizeFormDialog" width="400px">
      <el-form :model="prizeForm" label-width="80px">
        <el-form-item label='名称'><el-input v-model="prizeForm.name" /></el-form-item>
        <el-form-item label='级别'><el-input v-model="prizeForm.level" placeholder="一等奖/二等奖/参与奖" /></el-form-item>
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label='总量'><el-input v-model="prizeForm.totalCount" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label='概率(%)'><el-input v-model="prizeForm.probability" /></el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer><el-button @click="prizeFormDialog=false">取消</el-button><el-button type="primary" @click="savePrize">保存</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getActivityList as fetchActivityList, getActivityDetail, saveActivity as saveAct, updateActivity as updateAct, deleteActivity as deleteAct, getActivityPrizes, saveActivityPrize, updateActivityPrize, deleteActivityPrize, getActivityRecords } from '@/api/mall'

const activities = ref([]); const al = ref(false); const actPg = ref(1); const actTotal = ref(0)
const records = ref([]); const rcl = ref(false); const recPg = ref(1); const recTotal = ref(0); const recordActFilter = ref('')
const activityDialog = ref(false); const editingActivity = ref(null)
const activityForm = ref({ title: '', startTime: '', endTime: '', description: '' })
const prizeDialog = ref(false); const prizeFormDialog = ref(false)
const prizes = ref([]); const pzl = ref(false); const currentActivityId = ref('')
const editingPrize = ref(null)
const prizeForm = ref({ name: '', level: '', totalCount: '', probability: '' })

async function loadActivities() {
  al.value = true
  try { const r = await fetchActivityList({ page: actPg.value, size: 10 }); activities.value = r.list||r.records||[]; actTotal.value = r.total||0 } catch { }
  al.value = false
}
async function loadRecords() {
  rcl.value = true
  try { const r = await getActivityRecords({ page: recPg.value, size: 20, activity_id: recordActFilter.value||undefined }); records.value = r.list||r.records||[]; recTotal.value = r.total||0 } catch { }
  rcl.value = false
}
async function showActivityDetail(row) {
  try {
    const r = await getActivityDetail(row.id)
    editingActivity.value = r?.data||r
    activityForm.value = {
      title: row.title||'', startTime: row.startTime||'',
      endTime: row.endTime||'', description: row.description||''
    }
    activityDialog.value = true
  } catch { }
}
function showActivityForm(row) {
  editingActivity.value = row
  activityForm.value = row ? { title: row.title||'', startTime: row.startTime||'', endTime: row.endTime||'', description: row.description||'' } : { title:'', startTime:'', endTime:'', description:'' }
  activityDialog.value = true
}
async function saveActivity() {
  try {
    if (editingActivity.value?.id) await updateAct(editingActivity.value.id, activityForm.value)
    else await saveAct(activityForm.value)
    ElMessage.success('OK'); activityDialog.value = false; loadActivities()
  } catch { ElMessage.error('Error') }
}
async function delActivity(id) { await ElMessageBox.confirm('确认删除?'); try { await deleteAct(id); ElMessage.success('OK'); loadActivities() } catch { ElMessage.error('Error') } }
async function showPrizes(row) {
  currentActivityId.value = row.id
  prizeDialog.value = true; pzl.value = true
  try { const r = await getActivityPrizes(row.id); prizes.value = r.list||r.records||[] } catch { }
  pzl.value = false
}
function showPrizeForm(row) { editingPrize.value = row; prizeForm.value = row ? { name:row.name||'', level:row.level||'', totalCount:row.totalCount||'', probability:row.probability||'' } : { name:'', level:'', totalCount:'', probability:'' }; prizeFormDialog.value = true }
async function savePrize() {
  try {
    const data = { ...prizeForm.value, activityId: currentActivityId.value }
    if (editingPrize.value?.id) await updateActivityPrize(editingPrize.value.id, data)
    else await saveActivityPrize(data)
    ElMessage.success('OK'); prizeFormDialog.value = false; showPrizes({ id: currentActivityId.value })
  } catch { ElMessage.error('Error') }
}
async function delPrize(id) { await ElMessageBox.confirm('确认删除?'); try { await deleteActivityPrize(id); ElMessage.success('OK'); showPrizes({ id: currentActivityId.value }) } catch { ElMessage.error('Error') } }
onMounted(() => { loadActivities() })
</script>
<style scoped>
.tb-bar { display:flex; gap:8px; margin-bottom:12px; }
</style>
