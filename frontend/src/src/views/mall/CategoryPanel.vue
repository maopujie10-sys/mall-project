<template>
  <el-card shadow="never">
    <template #header>
      <div class="dt-header"><span>{{ \('mallSub.title') }}</span><el-button size="small" type="primary" @click="showForm(null)">OK</el-button></div>
    </template>
    <el-table :data="list" stripe size="small" v-loading="loading">
      <el-table-column prop="uuid" label="UUID" width="200" />
      <el-table-column prop="name" label='' width="150" />
      <el-table-column prop="status" label='' width="80">
        <template #default="{row}"><el-tag :type="row.status===1?'success':'info'' size="small">{{ row.status===1?'':'' }}</el-tag></template>
      </el-table-column>
      <el-table-column label='' width="240">
        <template #default="{row}">
          <el-button size="small" link type="primary" @click="showForm(row)">OK</el-button>
          <el-button size="small" link type="warning" @click="toggleStatus(row)">{{ row.status===1?'':'' }}</el-button>
          <el-button size="small" link type="danger" @click="del(row.uuid)">OK</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog :title="editing?.uuid?'':''" v-model="dialogVisible" width="400px">
      <el-form :model="form" label-width="80px">
        <el-form-item label=''><el-input v-model="form.name" /></el-form-item>
        <el-form-item label=''><el-input-number v-model="form.sort" :min="0" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">OK</el-button><el-button type="primary" @click="save">OK</el-button></template>
    </el-dialog>
  </el-card>
</template>
<script setup>
import { ref } from 'vue'
import { getCategoryList, saveCategory, updateCategory, updateCategoryStatus, deleteCategory } from '@/api/mall'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const editing = ref(null)
const form = ref({ name: '', sort: 0 })

async function load() {
  loading.value = true
  try { const r = await getCategoryList(); list.value = r.list || r.records || [] } catch(e) { }
  loading.value = false
}
function showForm(row) {
  editing.value = row
  form.value = row ? { name: row.name, sort: row.sort || 0 } : { name: '', sort: 0 }
  dialogVisible.value = true
}
async function save() {
  try {
    if (editing.value) await updateCategory(editing.value.uuid, form.value)
    else await saveCategory(form.value)
    ElMessage.success('OK')
    dialogVisible.value = false
    load()
  } catch { ElMessage.error('Error') }
}
async function toggleStatus(row) {
  try {
    await updateCategoryStatus(row.uuid, { status: row.status === 1 ? 0 : 1 })
    ElMessage.success('OK')
    load()
  } catch { ElMessage.error('Error') }
}
async function del(uuid) {
  await ElMessageBox.confirm('?', '', { type: 'warning' })
  try { await deleteCategory(uuid); ElMessage.success('OK'); load() } catch { ElMessage.error('Error') }
}
load()
</script>
<style scoped>.dt-header{display:flex;align-items:center;justify-content:space-between;}</style>