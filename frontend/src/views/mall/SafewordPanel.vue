<template>
  <el-card shadow="never" header="安全重置审核 (资金密码/登录密码)">
    <el-table :data="list" stripe size="small" v-loading="loading">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="userId" label="用户ID" width="80" />
      <el-table-column prop="userName" label="用户名" width="120" />
      <el-table-column prop="type" label="类型" width="120" />
      <el-table-column prop="reason" label="原因" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="80">
        <template #default="{row}"><el-tag :type="row.status===0?'warning':row.status===1?'success':'danger'" size="small">{{ row.status===0?'待审核':row.status===1?'已通过':'已拒绝' }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="createTime" label="申请时间" width="160" />
      <el-table-column label="操作" width="160">
        <template #default="{row}">
          <el-button v-if="row.status===0" size="small" type="success" @click="approve(row.id)">通过</el-button>
          <el-button v-if="row.status===0" size="small" type="danger" @click="reject(row.id)">拒绝</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination style="margin-top:12px;text-align:right" v-model:current-page="page" :page-size="size" :total="total" layout="prev,pager,next,total" small @change="load" />
  </el-card>
</template>
<script setup>
import { ref } from 'vue'
import { getSafewordList, approveSafeword, rejectSafeword } from '@/api/mall'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([]); const loading = ref(false); const page = ref(1); const size = ref(20); const total = ref(0)

async function load() {
  loading.value = true
  try { const r = await getSafewordList({ page: page.value, size: size.value }); list.value = r.list||r.records||[]; total.value = r.total||0 } catch { }
  loading.value = false
}
async function approve(id) {
  await ElMessageBox.confirm('确认批准该安全重置申请?', '审批', { type:'warning' })
  try { await approveSafeword(id); ElMessage.success('已批准'); load() } catch { ElMessage.error('Error') }
}
async function reject(id) {
  await ElMessageBox.confirm('确认拒绝该申请?', '审批', { type:'warning' })
  try { await rejectSafeword(id); ElMessage.success('已拒绝'); load() } catch { ElMessage.error('Error') }
}
load()
</script>
