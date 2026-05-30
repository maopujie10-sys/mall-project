<template>
  <el-card shadow="never" header="收款方式管理">
    <el-table :data="list" stripe size="small" v-loading="loading">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="sellerId" label="商家ID" width="80" />
      <el-table-column prop="sellerName" label="商家名称" width="150" />
      <el-table-column prop="methodType" label="收款类型" width="120" />
      <el-table-column prop="bankName" label="银行/机构" width="180" />
      <el-table-column prop="accountNo" label="账号" width="200" />
      <el-table-column prop="accountName" label="户名" width="120" />
      <el-table-column prop="createTime" label="创建时间" width="160" />
    </el-table>
    <el-pagination style="margin-top:12px;text-align:right" v-model:current-page="page" :page-size="size" :total="total" layout="prev,pager,next,total" small @change="load" />
  </el-card>
</template>
<script setup>
import { ref } from 'vue'
import { agentApi } from '@/api/index'

const list = ref([]); const loading = ref(false); const page = ref(1); const size = ref(20); const total = ref(0)

async function load() {
  loading.value = true
  try {
    const r = await agentApi.get('/tools/mall/payment-methods', { params: { page: page.value, size: size.value } })
    const d = r?.data !== undefined ? r.data : r
    list.value = d.list || d.records || (Array.isArray(d) ? d : [])
    total.value = d.total || list.value.length
  } catch { }
  loading.value = false
}
load()
</script>
