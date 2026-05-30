<template>
  <el-card shadow="never">
    <template #header>
      <div class="dt-header">
        <span>{{ title }}</span>
        <el-input v-model="search" :placeholder="searchPlaceholder" size="small" clearable style="width:220px" @change="load" />
      </div>
    </template>
    <el-table :data="tableData" stripe size="small" v-loading="loading">
      <el-table-column v-for="col in columns" :key="col.prop" v-bind="col" />
      <el-table-column label='' width="180" v-if="actions.length">
        <template #default="{row}">
          <el-button v-for="act in actions" :key="act.label" :type="act.type" size="small" link @click="act.handler(row)">
            {{ act.label }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="dt-footer">
      <el-pagination v-model:current-page="page" :page-size="size" :total="total" layout="prev,pager,next,total" small @change="load" />
    </div>
  </el-card>
</template>
<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  title: String,
  columns: Array,
  fetch: Function,
  onDelete: Function,
  onAudit: Function,
  onDetail: Function,
  onRefund: Function,
  onLogs: Function,
  onStatus: Function,
  onBalance: Function,
  onTrace: Function,
  searchPlaceholder: { type: String, default: '...' },
})

const search = ref('')
const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const page = ref(1)
const size = ref(20)

const actions = computed(() => {
  const acts = []
  if (props.onDetail) acts.push({ label: '', type: 'primary', handler: (r) => props.onDetail(r.id || r.order_id) })
  if (props.onAudit) acts.push({ label: '', type: 'warning', handler: (r) => props.onAudit(r) })
  if (props.onStatus) acts.push({ label: '', type: 'info', handler: (r) => props.onStatus(r) })
  if (props.onBalance) acts.push({ label: '', type: 'warning', handler: (r) => props.onBalance(r) })
  if (props.onRefund) acts.push({ label: '', type: 'danger', handler: (r) => props.onRefund(r.order_id) })
  if (props.onLogs) acts.push({ label: '', type: 'info', handler: (r) => props.onLogs(r.order_id || r.id) })
  if (props.onTrace) acts.push({ label: '', type: 'primary', handler: (r) => props.onTrace(r.order_id || r.id) })
  if (props.onDelete) acts.push({ label: '', type: 'danger', handler: (r) => props.onDelete(r.id || r.uuid) })
  return acts
})

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, size: size.value }
    if (search.value) params.keyword = search.value
    const r = await props.fetch(params)
    tableData.value = r.list || r.records || r.data || []
    total.value = r.total || 0
  } catch (e) { /* ignore */ }
  loading.value = false
}
load()
</script>
<style scoped>
.dt-header { display: flex; align-items: center; justify-content: space-between; }
.dt-footer { margin-top: 12px; display: flex; justify-content: flex-end; }
</style>