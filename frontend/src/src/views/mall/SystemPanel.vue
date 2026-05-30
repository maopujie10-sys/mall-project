<template>
  <div>
    <el-tabs type="card">
      <el-tab-pane label=''>
        <el-table :data="sysparas" stripe size="small" v-loading="sp">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="key" label='' width="180" />
          <el-table-column prop="value" label='' show-overflow-tooltip />
          <el-table-column label='' width="160">
            <template #default="{row}">
              <el-button size="small" link type="primary" @click="editSyspara(row)">OK</el-button>
              <el-button size="small" link type="danger" @click="delSyspara(row.id)">OK</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label=''>
        <el-table :data="countries" stripe size="small" v-loading="al">
          <el-table-column prop="name" label="/" />
          <el-table-column prop="code" label='' width="80" />
          <el-table-column prop="prefix" label='' width="80" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label=''>
        <el-table :data="levels" stripe size="small" v-loading="mll">
          <el-table-column prop="uuid" label="UUID" width="200" />
          <el-table-column prop="name" label='' width="120" />
          <el-table-column prop="threshold" label='' width="100" />
          <el-table-column prop="benefits" label='' />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label=''>
        <el-table :data="combos" stripe size="small" v-loading="cbl">
          <el-table-column prop="uuid" label="UUID" width="200" />
          <el-table-column prop="name" label='' width="150" />
          <el-table-column prop="price" label='' width="100" />
          <el-table-column prop="description" label='' />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label=''>
        <el-table :data="idcodes" stripe size="small" v-loading="idl">
          <el-table-column prop="uuid" label="UUID" width="200" />
          <el-table-column prop="user_id" label="ID" width="80" />
          <el-table-column prop="real_name" label='' width="100" />
          <el-table-column prop="status" label='' width="80" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label=''>
        <el-table :data="admins" stripe size="small" v-loading="adml">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="username" label='' width="120" />
          <el-table-column prop="role" label='' width="100" />
          <el-table-column prop="status" label='' width="80" />
        </el-table>
      </el-tab-pane>
    </el-tabs>
    <el-dialog title='' v-model="sysparaDialog" width="400px">
      <el-form :model="sysparaForm" label-width="60px">
        <el-form-item label=''><el-input v-model="sysparaForm.key" /></el-form-item>
        <el-form-item label=''><el-input v-model="sysparaForm.value" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="sysparaDialog=false">OK</el-button><el-button type="primary" @click="saveSyspara">OK</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { getSysparaList, saveSyspara, updateSyspara, deleteSyspara, getAreaCountries, getMallLevelList, getComboList, getIdcodeList, getAdminList } from '@/api/mall'
import { ElMessage } from 'element-plus'

const sysparas = ref([]); const sp = ref(false)
const countries = ref([]); const al = ref(false)
const levels = ref([]); const mll = ref(false)
const combos = ref([]); const cbl = ref(false)
const idcodes = ref([]); const idl = ref(false)
const admins = ref([]); const adml = ref(false)
const sysparaDialog = ref(false)
const sysparaForm = ref({ id: null, key: '', value: '' })

async function loadAll() {
  sp.value = al.value = mll.value = cbl.value = idl.value = adml.value = true
  try { const r = await getSysparaList(); sysparas.value = r.list || r.records || r || [] } catch { }
  try { const r = await getAreaCountries('zh'); countries.value = r || [] } catch { }
  try { const r = await getMallLevelList(); levels.value = r.list || r.records || [] } catch { }
  try { const r = await getComboList(); combos.value = r.list || r.records || [] } catch { }
  try { const r = await getIdcodeList(); idcodes.value = r.list || r.records || [] } catch { }
  try { const r = await getAdminList(); admins.value = r.list || r.records || [] } catch { }
  sp.value = al.value = mll.value = cbl.value = idl.value = adml.value = false
}
function editSyspara(row) { sysparaForm.value = { ...row }; sysparaDialog.value = true }
async function saveSyspara() {
  try {
    if (sysparaForm.value.id) await updateSyspara(sysparaForm.value.id, sysparaForm.value)
    else await saveSyspara(sysparaForm.value)
    ElMessage.success('OK'); sysparaDialog.value = false; loadAll()
  } catch { ElMessage.error('Error') }
}
async function delSyspara(id) { try { await deleteSyspara(id); ElMessage.success('OK'); loadAll() } catch { ElMessage.error('Error') } }
onMounted(loadAll)
</script>