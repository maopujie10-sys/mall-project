<template>
  <el-card shadow="never">
    <template #header>
      <div class="dt-header"><span>分类管理</span><el-button size="small" type="primary" @click="showForm(null)">新增分类</el-button></div>
    </template>
    <el-table :data="list" stripe size="small" v-loading="loading">
      <el-table-column prop="uuid" label="UUID" width="200" />
      <el-table-column prop="name" label="名称" width="150" />
      <el-table-column prop="status" label="状态" width="80">
        <template #default="{row}"><el-tag :type="row.status===1?'success':'info'" size="small">{{ row.status===1?'启用':'禁用' }}</el-tag></template>
      </el-table-column>
      <el-table-column label="操作" width="240">
        <template #default="{row}">
          <el-button size="small" link type="primary" @click="showForm(row)">编辑</el-button>
          <el-button size="small" link type="warning" @click="toggleStatus(row)">{{ row.status===1?'禁用':'启用' }}</el-button>
          <el-button size="small" link type="danger" @click="del(row.uuid)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog :title="editing?.uuid?'编辑分类':'新增分类'" v-model="dialogVisible" width="400px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort" :min="0" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
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
    ElMessage.success('保存成功')
    dialogVisible.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
async function toggleStatus(row) {
  try {
    await updateCategoryStatus(row.uuid, { status: row.status === 1 ? 0 : 1 })
    ElMessage.success('更新成功')
    load()
  } catch { ElMessage.error('更新失败') }
}
async function del(uuid) {
  await ElMessageBox.confirm('确认删除?', '提示', { type: 'warning' })
  try { await deleteCategory(uuid); ElMessage.success('删除成功'); load() } catch { ElMessage.error('删除失败') }
}
load()
</script>
<style scoped>.dt-header{display:flex;align-items:center;justify-content:space-between;}</style>