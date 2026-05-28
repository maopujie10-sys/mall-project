<template>
  <el-card shadow="never" header="KYC认证管理">
    <el-radio-group v-model="filter" size="small" style="margin-bottom:12px">
      <el-radio-button value="">全部</el-radio-button>
      <el-radio-button :value="0">待审核</el-radio-button>
      <el-radio-button :value="1">已通过</el-radio-button>
      <el-radio-button :value="2">已拒绝</el-radio-button>
    </el-radio-group>
    <el-table :data="list" stripe size="small" v-loading="loading">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="user_id" label="用户ID" width="80" />
      <el-table-column prop="real_name" label="真实姓名" width="120" />
      <el-table-column prop="id_number" label="身份证号" width="180" />
      <el-table-column prop="status" label="状态" width="80">
        <template #default="{row}"><el-tag :type="row.status===1?'success':row.status===2?'danger':'warning'" size="small">{{ row.status===1?'已通过':row.status===2?'已拒绝':'待审核' }}</el-tag></template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{row}">
          <el-button size="small" link type="success" @click="audit(row.id,true)">通过</el-button>
          <el-button size="small" link type="danger" @click="audit(row.id,false)">拒绝</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div style="margin-top:12px;text-align:right">
      <el-pagination v-model:current-page="page" :page-size="size" :total="total" layout="prev,pager,next,total" small @change="load" />
    </div>
  </el-card>
</template>
<script setup>
import { ref, watch } from 'vue'
import { getKycList, auditKyc } from '@/api/mall'
import { ElMessage } from 'element-plus'
const list = ref([]); const loading = ref(false); const filter = ref(0); const page = ref(1); const size = ref(20); const total = ref(0)
async function load() {
  loading.value = true
  try {
    const params = { page, size }
    if (filter.value !== '') params.status = filter.value
    const r = await getKycList(params)
    list.value = r.list || r.records || []
    total.value = r.total || 0
  } catch { }
  loading.value = false
}
async function audit(id, approved) {
  try { await auditKyc(id, { approved, reason: approved ? '审核通过' : '审核拒绝' }); ElMessage.success('操作成功'); load() } catch { ElMessage.error('操作失败') }
}
watch(filter, load)
load()
</script>