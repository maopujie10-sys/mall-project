<template>
  <el-card shadow="never" header="KYC">
    <el-radio-group v-model="filter" size="small" style="margin-bottom:12px">
      <el-radio-button value=''></el-radio-button>
      <el-radio-button :value="0"></el-radio-button>
      <el-radio-button :value="1"></el-radio-button>
      <el-radio-button :value="2"></el-radio-button>
    </el-radio-group>
    <el-table :data="list" stripe size="small" v-loading="loading">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="user_id" label="ID" width="80" />
      <el-table-column prop="real_name" label='' width="120" />
      <el-table-column prop="id_number" label='' width="180" />
      <el-table-column prop="status" label='' width="80">
        <template #default="{row}"><el-tag :type="row.status===1?'success':row.status===2?'danger':'warning'' size="small">{{ row.status===1?'':row.status===2?'':'' }}</el-tag></template>
      </el-table-column>
      <el-table-column label='' width="160">
        <template #default="{row}">
          <el-button size="small" link type="success" @click="audit(row.id,true)">OK</el-button>
          <el-button size="small" link type="danger" @click="audit(row.id,false)">OK</el-button>
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
  try { await auditKyc(id, { approved, reason: approved ? '' : '' }); ElMessage.success('OK'); load() } catch { ElMessage.error('Error') }
}
watch(filter, load)
load()
</script>